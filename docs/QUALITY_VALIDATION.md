# Quality Validation Guide

## Overview

The quality validation system ensures that AI agent outputs meet production standards before use. It performs automated checks for completeness, specificity, security, and technical depth.

## Quick Start

### In Jupyter Notebook

The validation is integrated into the main notebook as Step 6. After running your crew:

```python
from validation import quick_validate

# Validate the crew output
validation_result = quick_validate(result, production_mode=True)
print(validation_result.get_summary())

if validation_result.is_valid:
    print("✅ Ready for production!")
else:
    print("❌ Needs revision")
```

### Standalone Validation

**Important**: Make sure to use the virtual environment:

```bash
# Option 1: Use venv Python directly
.venv/bin/python -m validation.examples  # macOS/Linux
.venv\Scripts\python -m validation.examples  # Windows

# Option 2: Activate venv first
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
python -m validation.examples
```

## What Gets Validated

### ✅ Completeness Checks
- **Minimum Length**: Ensures outputs are substantive (default: 500 characters)
- **Structure**: Validates proper markdown headers and organization
- **Recommendations**: Requires specific, actionable recommendations

### 🔍 Quality Indicators
- **Code Examples**: Technical outputs must include code snippets
- **Specificity**: Detects vague language ("maybe", "perhaps", "might")
- **Technical Depth**: Measures presence of detailed examples and explanations

### 🔒 Security Scanning
- **Credential Detection**: Flags exposed API keys, passwords, secrets
- **Best Practices**: Checks for security considerations

### 📊 Production Readiness
- **Cost Awareness**: Validates that cost considerations are mentioned
- **Placeholder Detection**: Flags TODO, FIXME, [YOUR_API_KEY], etc.
- **Hallucination Prevention**: Detects "As an AI..." and "I cannot" phrases

## Validation Results

### Score Interpretation

- **90-100**: Excellent - Production ready
- **70-89**: Good - Minor improvements recommended
- **50-69**: Fair - Needs revision
- **Below 50**: Poor - Significant issues

### Severity Levels

- **CRITICAL** ❌: Must fix before production use
- **WARNING** ⚠️: Should fix for quality
- **INFO** ℹ️: Nice to have improvements

## Examples

### Example 1: High-Quality Output

```
Status: ✅ PASSED
Quality Score: 100.0/100

Checks Passed: 7
Critical Issues: 0
Warnings: 0
```

**Characteristics:**
- Detailed technical analysis (>1000 characters)
- Multiple code examples with explanations
- Specific, numbered recommendations
- Well-structured with clear sections
- No placeholders or vague language

### Example 2: Low-Quality Output (Failed)

```
Status: ❌ FAILED
Quality Score: 50.0/100

Critical Issues: 2
- Minimum Length: Output too short (225 chars)
- Placeholder Detection: [YOUR_API_KEY] found

Warnings: 3
- No code examples
- Lacks technical depth
- Missing structure
```

**Issues:**
- Too brief, not substantive
- Contains placeholders
- Vague recommendations
- No code examples

## Custom Validation

You can customize validation criteria:

```python
from validation import AgentOutputValidator

# Custom validator
validator = AgentOutputValidator(
    min_output_length=1000,  # Stricter length requirement
    require_code_examples=True,
    require_specific_recommendations=True,
    check_for_placeholders=True
)

# Validate single output
result = validator.validate_output_text(
    output="Your agent output text...",
    agent_role="Backend Engineer"
)

print(result.get_summary())
```

## Advanced Usage

### Production-Mode Validation

Production mode includes additional security and cost checks:

```python
# Standard validation
basic_result = quick_validate(crew_output, production_mode=False)

# Production validation (includes security + cost checks)
prod_result = quick_validate(crew_output, production_mode=True)
```

### Accessing Detailed Results

```python
validation = quick_validate(result, production_mode=True)

# Overall metrics
print(f"Score: {validation.score}/100")
print(f"Valid: {validation.is_valid}")

# Failed checks
for issue in validation.failed_checks:
    print(f"❌ {issue.check_name}: {issue.message}")
    if issue.suggestion:
        print(f"   💡 {issue.suggestion}")

# Warnings
for warning in validation.warnings:
    print(f"⚠️  {warning.check_name}: {warning.message}")

# Passed checks
print(f"\n✅ Passed: {len(validation.passed_checks)} checks")
```

## Integration with Workflows

### CI/CD Pipeline

```python
#!/usr/bin/env python
"""
ci_validate.py - Validate agent outputs in CI/CD
"""
from validation import quick_validate
import sys

# Run your crew
result = engineering_crew.kickoff()

# Validate
validation = quick_validate(result, production_mode=True)

# Exit with error code if validation fails
if not validation.is_valid:
    print("❌ Quality validation failed!")
    print(validation.get_summary())
    sys.exit(1)

print("✅ Quality validation passed!")
sys.exit(0)
```

### Quality Gates

```python
# Only proceed if validation passes
validation = quick_validate(result, production_mode=True)

if validation.score >= 80 and validation.is_valid:
    # Deploy to production
    deploy_to_production(result)
elif validation.score >= 60:
    # Send for human review
    send_for_review(result, validation)
else:
    # Reject and re-run with different prompts
    print("Quality too low - adjusting prompts...")
    retry_with_better_prompts()
```

## Best Practices

### 1. Always Validate Before Use
```python
result = crew.kickoff()
validation = quick_validate(result, production_mode=True)

if validation.is_valid:
    use_result(result)
else:
    fix_issues(validation.failed_checks)
```

### 2. Use Production Mode for Deployments
```python
# Development
dev_validation = quick_validate(result, production_mode=False)

# Production
prod_validation = quick_validate(result, production_mode=True)
```

### 3. Review Warnings, Not Just Failures
```python
if validation.warnings:
    print("⚠️  Consider addressing these warnings:")
    for warning in validation.warnings:
        print(f"  - {warning.message}")
```

### 4. Track Quality Metrics Over Time
```python
results_history = []

for run in range(10):
    result = crew.kickoff()
    validation = quick_validate(result)
    results_history.append(validation.score)

avg_quality = sum(results_history) / len(results_history)
print(f"Average quality: {avg_quality}/100")
```

## Troubleshooting

### Common Issues

**Issue**: "Output too short"
- **Fix**: Provide more detailed task descriptions
- **Fix**: Ask agents to elaborate on recommendations

**Issue**: "No code examples found"
- **Fix**: Explicitly request code snippets in task descriptions
- **Fix**: Include "provide code examples" in agent goals

**Issue**: "Placeholder detection: [YOUR_API_KEY]"
- **Fix**: Configure agents to use realistic examples
- **Fix**: Provide example values in task context

**Issue**: "Lacks technical depth"
- **Fix**: Request step-by-step explanations
- **Fix**: Ask for multiple alternatives with pros/cons

## Validation Checklist

Before marking outputs as production-ready:

- [ ] Quality score > 80
- [ ] No critical issues
- [ ] All warnings reviewed
- [ ] Code examples present (for technical tasks)
- [ ] Specific recommendations provided
- [ ] No security issues detected
- [ ] No placeholders or TODOs
- [ ] Cost considerations mentioned
- [ ] Well-structured output

## Support

For issues or questions:
1. Check `example_validation.py` for usage patterns
2. Review validation results summary
3. Adjust agent prompts based on suggestions
4. Customize validation criteria if needed

---

**Next Steps:**
- Run `python -m validation.examples` to see validation in action
- Execute Step 6 in the Jupyter notebook
- Customize validation criteria for your use case
- Integrate into your CI/CD pipeline
