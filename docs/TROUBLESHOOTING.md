# Troubleshooting Guide

## Common Errors and Solutions

### Error: ModuleNotFoundError: No module named 'validation'

**Problem**: Python can't find the validation module.

**Solution**: Make sure you're in the correct directory:
```bash
cd /path/to/agentic-eng-team
.venv/bin/python -m validation.examples
```

---

### Error: ModuleNotFoundError: No module named 'crewai'

**Problem**: CrewAI is not installed or virtual environment is not activated.

**Solutions**:

**Option 1: Use virtual environment Python directly (Recommended)**
```bash
# macOS/Linux
.venv/bin/python -m validation.examples

# Windows
.venv\Scripts\python -m validation.examples
```

**Option 2: Activate virtual environment first**
```bash
# macOS/Linux
source .venv/bin/activate
python -m validation.examples

# Windows
.venv\Scripts\activate
python -m validation.examples
```

**Option 3: Reinstall dependencies**
```bash
.venv/bin/pip install -r requirements.txt
```

---

### Error: openai.OpenAIError or API key not found

**Problem**: OpenAI API key is not configured.

**Solution**: Check your `.env` file:
```bash
# Create .env if it doesn't exist
cp .env.example .env

# Edit .env and add your key
# OPENAI_API_KEY=sk-your-key-here
```

---

### Error: jupyter: command not found

**Problem**: Jupyter is not installed or virtual environment is not activated.

**Solution**:
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install Jupyter
pip install jupyter

# Or use requirements.txt
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook
```

---

### Error: validation.py runs but shows import errors

**Problem**: Running with system Python instead of virtual environment.

**Solution**: Always use the virtual environment:
```bash
# Check which Python you're using
which python  # macOS/Linux
where python  # Windows

# Should show something like:
# /path/to/agentic-eng-team/.venv/bin/python

# If not, activate venv:
source .venv/bin/activate
```

---

### Notebook Kernel Issues

**Problem**: Jupyter notebook can't find installed packages.

**Solution**: Select the correct kernel:

1. In Jupyter, click **Kernel** → **Change Kernel**
2. Select the kernel that matches your virtual environment
3. Or run in terminal:
   ```bash
   .venv/bin/python -m ipykernel install --user --name=agentic-eng-team
   ```

---

### Error: Quality validation fails with low scores

**Problem**: Agent outputs don't meet quality standards.

**Not an error!** This means validation is working correctly. 

**Solutions**:
- Review the validation suggestions
- Improve agent prompts to be more specific
- Ask for code examples explicitly
- Request numbered recommendations
- Provide more context in task descriptions

---

### Python Version Issues

**Problem**: "This package requires Python <=3.13"

**Solution**: Check your Python version:
```bash
python --version
# Should be 3.11, 3.12, or 3.13

# If wrong version, recreate venv with correct Python:
rm -rf .venv
python3.12 -m venv .venv  # Use available version
.venv/bin/pip install -r requirements.txt
```

---

## Quick Diagnostic Commands

Run these to check your setup:

```bash
# 1. Check you're in the right directory
pwd
# Should show: .../agentic-eng-team

# 2. Check virtual environment exists
ls -la .venv
# Should show directory contents

# 3. Check Python in venv
.venv/bin/python --version
# Should show Python 3.11+

# 4. Test imports
.venv/bin/python -c "import crewai, openai, langchain; print('✅ All imports work!')"

# 5. Check OpenAI key is set
.venv/bin/python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ API key loaded' if os.getenv('OPENAI_API_KEY') else '❌ No API key')"

# 6. Run validation demo
.venv/bin/python -m validation.examples
```

---

## Still Having Issues?

### Check File Permissions
```bash
# Make sure you can read the files
ls -l *.py
chmod +r *.py  # If needed
```

### Verify File Integrity
```bash
# Check files exist
ls -1 validation/*.py docs/*.md
# Should show:
# validation/__init__.py
# validation/agent_output_validator.py
# validation/examples.py
# docs/IMPLEMENTATION_SUMMARY.md
# docs/QUALITY_VALIDATION.md
# docs/TROUBLESHOOTING.md
```

### Clean Reinstall
```bash
# Remove and recreate everything
rm -rf .venv
python -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# Test
.venv/bin/python example_validation.py
```

---

## Platform-Specific Notes

### macOS
- Use `source .venv/bin/activate`
- Python command: `.venv/bin/python`
- Default shell: zsh (newer versions) or bash

### Windows
- Use `.venv\Scripts\activate`
- Python command: `.venv\Scripts\python`
- Use PowerShell or Command Prompt
- May need to run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Linux
- Use `source .venv/bin/activate`
- Python command: `.venv/bin/python`
- May need to install: `sudo apt install python3-venv`

---

## Get Help

If you're still stuck:

1. **Check the error message carefully** - it usually tells you what's wrong
2. **Verify virtual environment** - most issues are from not using .venv
3. **Check file paths** - make sure you're in the right directory
4. **Review documentation** - check README.md and QUALITY_VALIDATION.md
5. **Run diagnostics** - use the commands in "Quick Diagnostic Commands" above

---

**Last Updated**: February 10, 2026
