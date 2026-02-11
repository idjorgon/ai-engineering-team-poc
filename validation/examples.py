"""
Example: Quality Validation Demo

This script demonstrates how to use the AgentOutputValidator
to ensure AI agent outputs meet quality standards.

Note: This script can run standalone without CrewAI installed.
      For full integration with CrewAI, activate the virtual environment.
"""

import sys

# Check if running in virtual environment
try:
    from validation import (
        AgentOutputValidator, 
        ProductionReadinessChecker,
        quick_validate,
        ValidationResult
    )
except ImportError as e:
    print("❌ Error: Could not import validation modules.")
    print("\n💡 Please activate the virtual environment first:")
    print("   source .venv/bin/activate  # On macOS/Linux")
    print("   .venv\\Scripts\\activate     # On Windows")
    print("\nOr run with:")
    print("   .venv/bin/python validation/examples.py")
    print(f"\nDetailed error: {e}")
    sys.exit(1)


# Example 1: Validating good output
def demo_good_output():
    """Demonstrate validation of high-quality output"""
    
    print("\n" + "="*60)
    print("DEMO 1: High-Quality Agent Output")
    print("="*60)
    
    good_output = """
# Architecture Plan for Task Management Application

## Executive Summary

Based on analysis of the requirements, I recommend a microservices architecture 
with the following technology stack:

## Recommended Technology Stack

### Backend
- **API Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15 with TimescaleDB extension
- **Cache**: Redis 7.0
- **Message Queue**: RabbitMQ

**Rationale**: FastAPI provides excellent performance (comparable to Node.js) 
while maintaining Python's developer productivity. Type hints enable better 
code quality and automatic API documentation.

### Implementation Example

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

app = FastAPI()

@app.post("/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate user permissions
    if not current_user.can_create_tasks:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Create task with proper error handling
    try:
        db_task = Task(**task.dict(), owner_id=current_user.id)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Task creation failed")
```

## Specific Recommendations

1. **Use Database Migrations**: Implement Alembic for schema version control
2. **Implement Rate Limiting**: Prevent abuse with Redis-based rate limiting
3. **Add Observability**: Use Prometheus + Grafana for monitoring
4. **Security First**: Implement OAuth2 with JWT tokens

## Cost Estimates

- AWS Infrastructure: ~$500/month (t3.medium instances)
- Database: ~$200/month (RDS PostgreSQL)
- Redis Cache: ~$50/month
- **Total**: ~$750/month for initial deployment

## Next Steps

Step 1: Set up development environment
Step 2: Implement authentication service
Step 3: Create database schema and migrations
Step 4: Build core API endpoints
"""
    
    validator = AgentOutputValidator()
    result = validator.validate_output_text(good_output, "Engineering Lead")
    
    print(result.get_summary())
    
    return result


# Example 2: Validating poor output
def demo_poor_output():
    """Demonstrate validation of low-quality output"""
    
    print("\n" + "="*60)
    print("DEMO 2: Low-Quality Agent Output (Issues Detected)")
    print("="*60)
    
    poor_output = """
I think you should maybe use FastAPI or perhaps Django. 
TODO: add more details here.

You could consider using PostgreSQL or MongoDB.

[YOUR_API_KEY] should be set in environment.

This is a basic approach that might work.
"""
    
    validator = AgentOutputValidator()
    result = validator.validate_output_text(poor_output, "Backend Engineer")
    
    print(result.get_summary())
    
    return result


# Example 3: Production validation with security check
def demo_security_validation():
    """Demonstrate security validation"""
    
    print("\n" + "="*60)
    print("DEMO 3: Security Validation")
    print("="*60)
    
    insecure_output = """
# API Configuration

Here's the setup:

```python
API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"
SECRET_KEY = "my-secret-key"

def connect():
    client = Client(api_key=API_KEY)
    return client
```

This should work for your setup.
"""
    
    # Create mock crew output
    class MockTaskOutput:
        def __init__(self, text):
            self.raw = text
            self.agent = "Security Review"
    
    class MockCrewOutput:
        def __init__(self, outputs):
            self.tasks_output = outputs
    
    mock_output = MockCrewOutput([MockTaskOutput(insecure_output)])
    
    # Run production validation
    checker = ProductionReadinessChecker()
    result = checker.validate_for_production(mock_output)
    
    print(result.get_summary())
    
    return result


# Example 4: Comprehensive validation
def demo_comprehensive_validation():
    """Demonstrate full validation pipeline"""
    
    print("\n" + "="*60)
    print("DEMO 4: Comprehensive Validation Pipeline")
    print("="*60)
    
    output = """
# Backend API Design

## Overview

The backend will use FastAPI with PostgreSQL.

## API Endpoints

### Create Task
```python
@app.post("/api/v1/tasks")
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(**task.dict())
    db.add(new_task)
    db.commit()
    return new_task
```

### Get Tasks
```python
@app.get("/api/v1/tasks")
async def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks
```

## Database Schema

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

## Recommendations

1. **Implement Authentication**: Use OAuth2 with JWT tokens
2. **Add Rate Limiting**: Prevent API abuse (100 requests/minute per user)
3. **Input Validation**: Use Pydantic models for all request/response schemas
4. **Error Handling**: Implement global exception handlers
5. **Database Migrations**: Use Alembic for version control

## Performance Considerations

- Add Redis caching for frequently accessed tasks
- Implement pagination for large result sets
- Use connection pooling (SQLAlchemy default)

## Cost Estimates

- API hosting (AWS ECS): $30/month
- PostgreSQL (RDS t3.micro): $15/month
- Redis (ElastiCache): $13/month
- **Total**: ~$58/month

## Next Steps

1. Set up CI/CD pipeline
2. Implement comprehensive testing
3. Add monitoring and alerting
4. Deploy to staging environment
"""
    
    validator = AgentOutputValidator(
        min_output_length=500,
        require_code_examples=True,
        require_specific_recommendations=True
    )
    
    result = validator.validate_output_text(output, "Backend Engineer")
    
    print(result.get_summary())
    
    # Show individual check results
    print("\n📊 Detailed Metrics:")
    print(f"  Quality Score: {result.score:.1f}/100")
    print(f"  Passed Checks: {len(result.passed_checks)}")
    print(f"  Failed Checks: {len(result.failed_checks)}")
    print(f"  Warnings: {len(result.warnings)}")
    
    if result.is_valid:
        print("\n✅ OUTPUT APPROVED FOR USE")
    else:
        print("\n❌ OUTPUT NEEDS REVISION")
    
    return result


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║     Agent Output Quality Validation - Demo Suite         ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Run all demos
    demo_good_output()
    demo_poor_output()
    demo_security_validation()
    demo_comprehensive_validation()
    
    print("\n" + "="*60)
    print("✅ All validation demos completed!")
    print("="*60)
    print("\nTo use in your project:")
    print("  from agent_output_validator import quick_validate")
    print("  result = quick_validate(crew_output, production_mode=True)")
    print("  print(result.get_summary())")
