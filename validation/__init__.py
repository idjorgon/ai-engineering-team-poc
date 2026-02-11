"""
Validation Package for AI Agent Outputs

Provides quality validation, security scanning, and production readiness
checks for AI agent-generated content.

Usage:
    from validation import quick_validate, AgentOutputValidator
    
    # Quick validation
    result = quick_validate(crew_output, production_mode=True)
    
    # Custom validation
    validator = AgentOutputValidator(min_output_length=1000)
    result = validator.validate_output_text(output, "Agent Name")
"""

from .agent_output_validator import (
    AgentOutputValidator,
    ProductionReadinessChecker,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    quick_validate,
)

__all__ = [
    'AgentOutputValidator',
    'ProductionReadinessChecker',
    'ValidationResult',
    'ValidationIssue',
    'ValidationSeverity',
    'quick_validate',
]

__version__ = '1.0.0'
