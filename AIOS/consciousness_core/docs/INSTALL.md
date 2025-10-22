# Blackwall Installation Guide

## Standard Installation

1. Install the package in development mode:

```bash
# Navigate to the Blackwall directory
cd /path/to/Blackwallv2

# Install in development mode
pip install -e .
```

2. Verify the installation:

```bash
# Run the test script
python test_blackwall_pipeline.py
```

## Alternative Installation (if the above doesn't work)

If you're having import issues, you can use the setup script:

```bash
# Run the setup script
python setup_blackwall.py
```

## Manual Import (for troubleshooting)

If you're still having import issues, you can use direct imports in your code:

```python
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly from the file
import lexicon.blackwall_pipeline as bp
# OR
from lexicon.blackwall_pipeline import BlackwallPipeline
```

## Common Issues and Solutions

### Module Not Found Errors

If you see "No module named 'lexicon.blackwall_pipeline'" errors:

1. Make sure you've installed the package with `pip install -e .`
2. Check that the directory structure is correct:
   - /Blackwallv2/
     - setup.py
     - __init__.py
     - lexicon/
       - __init__.py
       - blackwall_pipeline.py

### ImportError or AttributeError

If specific functions/classes can't be imported:

1. Make sure all dependencies are installed:
   ```bash
   pip install psutil requests
   ```
2. Optional NLP features require spaCy:
   ```bash
   pip install spacy
   python -m spacy download en_core_web_sm
   ```

## Running the Pipeline

After installation, you can run the pipeline:

```bash
# Run the main pipeline
python -m lexicon.blackwall_pipeline

# Or run a simple example
python -m lexicon.blackwall_pipeline example
```
