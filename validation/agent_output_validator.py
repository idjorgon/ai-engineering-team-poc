"""
Agent Output Quality Validator

Validates outputs from AI agents to ensure they meet quality standards
before being used in production or presented to stakeholders.

Usage:
    from agent_output_validator import AgentOutputValidator
    
    validator = AgentOutputValidator()
    result = validator.validate_all(crew_result)
    
    if result.is_valid:
        print("✅ All outputs meet quality standards")
    else:
        print(f"❌ Quality issues found: {result.failed_checks}")
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import re

# Optional import - CrewAI only needed for validate_all() method
try:
    from crewai import CrewOutput
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    CrewOutput = None  # Type hint placeholder


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    CRITICAL = "critical"  # Must fix - blocks production use
    WARNING = "warning"    # Should fix - quality concern
    INFO = "info"          # Nice to have - improvement suggestion


@dataclass
class ValidationIssue:
    """Represents a single validation issue"""
    check_name: str
    severity: ValidationSeverity
    message: str
    agent_role: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation checks"""
    is_valid: bool
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    score: float = 0.0  # 0-100 quality score
    
    def get_summary(self) -> str:
        """Get human-readable summary"""
        critical_count = sum(1 for issue in self.failed_checks if issue.severity == ValidationSeverity.CRITICAL)
        warning_count = len(self.warnings)
        
        status = "✅ PASSED" if self.is_valid else "❌ FAILED"
        
        summary = f"""
{'='*60}
QUALITY VALIDATION RESULTS
{'='*60}

Status: {status}
Quality Score: {self.score:.1f}/100

Checks Passed: {len(self.passed_checks)}
Critical Issues: {critical_count}
Warnings: {warning_count}

"""
        if self.failed_checks:
            summary += "\n🚨 CRITICAL ISSUES:\n"
            for issue in self.failed_checks:
                if issue.severity == ValidationSeverity.CRITICAL:
                    summary += f"  • {issue.check_name}: {issue.message}\n"
                    if issue.suggestion:
                        summary += f"    💡 {issue.suggestion}\n"
        
        if self.warnings:
            summary += "\n⚠️  WARNINGS:\n"
            for warning in self.warnings:
                summary += f"  • {warning.check_name}: {warning.message}\n"
                if warning.suggestion:
                    summary += f"    💡 {warning.suggestion}\n"
        
        summary += f"\n{'='*60}\n"
        return summary


class AgentOutputValidator:
    """
    Validates AI agent outputs for quality, completeness, and production-readiness.
    
    Quality Checks:
    - Minimum length requirements
    - Structure and formatting
    - Code block validation
    - Technical depth assessment
    - Actionability
    - Hallucination detection
    - Cost-benefit analysis
    """
    
    def __init__(self, 
                 min_output_length: int = 500,
                 require_code_examples: bool = True,
                 require_specific_recommendations: bool = True,
                 check_for_placeholders: bool = True):
        """
        Initialize validator with quality criteria
        
        Args:
            min_output_length: Minimum characters for substantial output
            require_code_examples: Require code examples in technical outputs
            require_specific_recommendations: Require specific, actionable items
            check_for_placeholders: Flag generic placeholders like "TODO", "FIXME"
        """
        self.min_output_length = min_output_length
        self.require_code_examples = require_code_examples
        self.require_specific_recommendations = require_specific_recommendations
        self.check_for_placeholders = check_for_placeholders
        
        # Patterns that indicate low quality or hallucinations
        self.red_flag_patterns = [
            r"I don't have enough information",
            r"As an AI",
            r"I cannot",
            r"I apologize.*cannot",
            r"\[YOUR_.*?\]",  # e.g., [YOUR_API_KEY]
            r"\{.*?PLACEHOLDER.*?\}",
            r"<INSERT.*?>",
            r"TODO: implement",
            r"FIXME",
            r"XXX",
        ]
        
        # Keywords that indicate actionable, specific guidance
        self.quality_indicators = [
            "specifically",
            "for example",
            "here's how",
            "step 1",
            "recommendation",
            "implementation",
            "```",  # Code blocks
        ]
    
    def validate_all(self, crew_output: Any) -> ValidationResult:
        """
        Validate all agent outputs from a crew execution
        
        Args:
            crew_output: CrewOutput object from crew.kickoff()
            
        Returns:
            ValidationResult with overall quality assessment
        """
        if not CREWAI_AVAILABLE:
            raise ImportError(
                "CrewAI is required for validate_all(). "
                "Please activate your virtual environment:\n"
                "  source .venv/bin/activate  # On macOS/Linux\n"
                "  .venv\\Scripts\\activate     # On Windows\n"
                "Or install CrewAI: pip install crewai"
            )
        
        all_issues = []
        all_warnings = []
        passed = []
        
        # Validate each task output
        for i, task_output in enumerate(crew_output.tasks_output, 1):
            agent_role = task_output.agent if hasattr(task_output, 'agent') else f"Agent {i}"
            output_text = task_output.raw if hasattr(task_output, 'raw') else str(task_output)
            
            # Run all validation checks
            issues, warnings, checks_passed = self._validate_output(output_text, agent_role)
            all_issues.extend(issues)
            all_warnings.extend(warnings)
            passed.extend(checks_passed)
        
        # Calculate quality score
        total_checks = len(passed) + len(all_issues) + len(all_warnings)
        if total_checks == 0:
            score = 0.0
        else:
            # Passed checks = 100%, Warnings = 50%, Failed = 0%
            score = ((len(passed) * 100) + (len(all_warnings) * 50)) / total_checks
        
        # Determine if valid (no critical issues)
        critical_issues = [i for i in all_issues if i.severity == ValidationSeverity.CRITICAL]
        is_valid = len(critical_issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            passed_checks=passed,
            failed_checks=all_issues,
            warnings=all_warnings,
            score=score
        )
    
    def _validate_output(self, output: str, agent_role: str) -> tuple:
        """
        Validate a single agent output
        
        Returns:
            Tuple of (issues, warnings, passed_checks)
        """
        issues = []
        warnings = []
        passed = []
        
        # Check 1: Minimum length
        if len(output) < self.min_output_length:
            issues.append(ValidationIssue(
                check_name="Minimum Length",
                severity=ValidationSeverity.CRITICAL,
                message=f"Output too short ({len(output)} chars, minimum {self.min_output_length})",
                agent_role=agent_role,
                suggestion="Agent should provide more detailed analysis and recommendations"
            ))
        else:
            passed.append(f"{agent_role}: Minimum length")
        
        # Check 2: Red flag patterns (hallucinations, placeholders)
        if self.check_for_placeholders:
            for pattern in self.red_flag_patterns:
                matches = re.findall(pattern, output, re.IGNORECASE)
                if matches:
                    issues.append(ValidationIssue(
                        check_name="Placeholder Detection",
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Found placeholder or low-quality content: {matches[0][:50]}",
                        agent_role=agent_role,
                        suggestion="Remove placeholders and provide specific, concrete recommendations"
                    ))
                    break
            else:
                passed.append(f"{agent_role}: No placeholders")
        
        # Check 3: Contains code examples (for technical roles)
        if self.require_code_examples:
            code_blocks = re.findall(r'```[\s\S]*?```', output)
            if not code_blocks and any(role in agent_role.lower() for role in ['engineer', 'developer', 'architect']):
                warnings.append(ValidationIssue(
                    check_name="Code Examples",
                    severity=ValidationSeverity.WARNING,
                    message="No code examples found in technical output",
                    agent_role=agent_role,
                    suggestion="Include code snippets to demonstrate recommended approaches"
                ))
            elif code_blocks:
                passed.append(f"{agent_role}: Code examples present")
        
        # Check 4: Specific recommendations
        if self.require_specific_recommendations:
            has_recommendations = any(
                indicator in output.lower() 
                for indicator in ['recommendation', 'suggest', 'should', 'consider', 'step 1', 'step 2']
            )
            
            if not has_recommendations:
                issues.append(ValidationIssue(
                    check_name="Actionable Recommendations",
                    severity=ValidationSeverity.CRITICAL,
                    message="Output lacks specific, actionable recommendations",
                    agent_role=agent_role,
                    suggestion="Provide clear, numbered recommendations or action items"
                ))
            else:
                passed.append(f"{agent_role}: Has recommendations")
        
        # Check 5: Quality indicators
        quality_score = sum(1 for indicator in self.quality_indicators if indicator.lower() in output.lower())
        
        if quality_score < 2:
            warnings.append(ValidationIssue(
                check_name="Technical Depth",
                severity=ValidationSeverity.WARNING,
                message=f"Output may lack technical depth (quality score: {quality_score}/10)",
                agent_role=agent_role,
                suggestion="Include more specific examples, code snippets, or detailed explanations"
            ))
        else:
            passed.append(f"{agent_role}: Sufficient technical depth")
        
        # Check 6: Structure (sections, headers)
        has_structure = bool(re.search(r'^#{1,3}\s', output, re.MULTILINE))
        
        if not has_structure:
            warnings.append(ValidationIssue(
                check_name="Output Structure",
                severity=ValidationSeverity.WARNING,
                message="Output lacks clear structure (headings, sections)",
                agent_role=agent_role,
                suggestion="Use markdown headers to organize content into clear sections"
            ))
        else:
            passed.append(f"{agent_role}: Well-structured output")
        
        # Check 7: Vagueness detection
        vague_phrases = [
            'may want to', 'could consider', 'might be good',
            'perhaps', 'possibly', 'maybe', 'sort of', 'kind of'
        ]
        
        vague_count = sum(output.lower().count(phrase) for phrase in vague_phrases)
        
        if vague_count > 5:
            warnings.append(ValidationIssue(
                check_name="Specificity",
                severity=ValidationSeverity.WARNING,
                message=f"Output contains {vague_count} vague phrases - lacks decisiveness",
                agent_role=agent_role,
                suggestion="Use more definitive language and specific recommendations"
            ))
        else:
            passed.append(f"{agent_role}: Specific language")
        
        return issues, warnings, passed
    
    def validate_output_text(self, output: str, agent_role: str = "Agent") -> ValidationResult:
        """
        Validate a single text output
        
        Args:
            output: The output text to validate
            agent_role: Name/role of the agent for context
            
        Returns:
            ValidationResult
        """
        issues, warnings, passed = self._validate_output(output, agent_role)
        
        total_checks = len(passed) + len(issues) + len(warnings)
        score = ((len(passed) * 100) + (len(warnings) * 50)) / total_checks if total_checks > 0 else 0.0
        
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        is_valid = len(critical_issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            passed_checks=passed,
            failed_checks=issues,
            warnings=warnings,
            score=score
        )


class ProductionReadinessChecker:
    """
    Advanced validation for production deployment
    Checks security, cost, and compliance considerations
    """
    
    def __init__(self):
        self.security_patterns = [
            r'api[_-]?key',
            r'password',
            r'secret',
            r'token',
            r'private[_-]?key',
        ]
    
    def check_security(self, output: str) -> List[ValidationIssue]:
        """Check for potential security issues in output"""
        issues = []
        
        for pattern in self.security_patterns:
            matches = re.findall(f'{pattern}\\s*[=:]\\s*["\']?([^"\'\\s]+)', output, re.IGNORECASE)
            if matches:
                issues.append(ValidationIssue(
                    check_name="Security - Exposed Credentials",
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Potential credential exposure: {pattern}",
                    suggestion="Remove hardcoded credentials and use environment variables"
                ))
        
        return issues
    
    def check_cost_estimates(self, output: str) -> List[ValidationIssue]:
        """Verify cost considerations are mentioned"""
        warnings = []
        
        cost_keywords = ['cost', 'pricing', 'budget', 'expense', 'rate limit']
        has_cost_mention = any(keyword in output.lower() for keyword in cost_keywords)
        
        if not has_cost_mention and len(output) > 1000:
            warnings.append(ValidationIssue(
                check_name="Cost Awareness",
                severity=ValidationSeverity.WARNING,
                message="No cost or budget considerations mentioned",
                suggestion="Include estimated costs for API calls, infrastructure, etc."
            ))
        
        return warnings
    
    def validate_for_production(self, crew_output: Any) -> ValidationResult:
        """
        Comprehensive production readiness check
        
        Args:
            crew_output: CrewOutput from crew execution
            
        Returns:
            ValidationResult with production-specific checks
        """
        if not CREWAI_AVAILABLE:
            raise ImportError(
                "CrewAI is required for validate_for_production(). "
                "Please activate your virtual environment:\n"
                "  source .venv/bin/activate  # On macOS/Linux\n"
                "  .venv\\Scripts\\activate     # On Windows\n"
                "Or install CrewAI: pip install crewai"
            )
        
        all_issues = []
        all_warnings = []
        passed = []
        
        for task_output in crew_output.tasks_output:
            output_text = task_output.raw if hasattr(task_output, 'raw') else str(task_output)
            
            # Security check
            security_issues = self.check_security(output_text)
            all_issues.extend(security_issues)
            
            if not security_issues:
                passed.append("Security: No exposed credentials")
            
            # Cost check
            cost_warnings = self.check_cost_estimates(output_text)
            all_warnings.extend(cost_warnings)
            
            if not cost_warnings:
                passed.append("Cost awareness: Present")
        
        total_checks = len(passed) + len(all_issues) + len(all_warnings)
        score = ((len(passed) * 100) + (len(all_warnings) * 50)) / total_checks if total_checks > 0 else 0.0
        
        is_valid = len([i for i in all_issues if i.severity == ValidationSeverity.CRITICAL]) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            passed_checks=passed,
            failed_checks=all_issues,
            warnings=all_warnings,
            score=score
        )


# Convenience function for quick validation
def quick_validate(crew_output: Any, production_mode: bool = False) -> ValidationResult:
    """
    Quick validation of crew output
    
    Args:
        crew_output: CrewOutput from crew.kickoff()
        production_mode: If True, includes production-readiness checks
        
    Returns:
        ValidationResult
    """
    if not CREWAI_AVAILABLE:
        raise ImportError(
            "CrewAI is required for quick_validate(). "
            "Please activate your virtual environment:\n"
            "  source .venv/bin/activate  # On macOS/Linux\n"
            "  .venv\\Scripts\\activate     # On Windows\n"
            "Or install CrewAI: pip install crewai"
        )
    
    validator = AgentOutputValidator()
    result = validator.validate_all(crew_output)
    
    if production_mode:
        prod_checker = ProductionReadinessChecker()
        prod_result = prod_checker.validate_for_production(crew_output)
        
        # Merge results
        result.failed_checks.extend(prod_result.failed_checks)
        result.warnings.extend(prod_result.warnings)
        result.passed_checks.extend(prod_result.passed_checks)
        
        # Recalculate score
        total = len(result.passed_checks) + len(result.failed_checks) + len(result.warnings)
        result.score = ((len(result.passed_checks) * 100) + (len(result.warnings) * 50)) / total if total > 0 else 0.0
        result.is_valid = len([i for i in result.failed_checks if i.severity == ValidationSeverity.CRITICAL]) == 0
    
    return result


if __name__ == "__main__":
    # Example usage
    print("Agent Output Validator")
    print("=" * 60)
    print("\nThis module validates AI agent outputs for quality and production-readiness.")
    print("\nUsage in Jupyter Notebook:")
    print("""
    from agent_output_validator import quick_validate
    
    # After running your crew
    result = engineering_crew.kickoff()
    
    # Validate outputs
    validation = quick_validate(result, production_mode=True)
    print(validation.get_summary())
    
    # Only proceed if valid
    if validation.is_valid:
        print("✅ Ready for production!")
    else:
        print("❌ Fix issues before deploying")
        for issue in validation.failed_checks:
            print(f"  - {issue.message}")
    """)
