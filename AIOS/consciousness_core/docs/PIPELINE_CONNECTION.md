# Blackwall v2 Pipeline Connection Guide

This guide explains how to connect and run the Blackwall v2 pipeline to get the bot running and start the learning process.

## Files Overview

1. **fix_paths.py** - Fixes path references in core files to ensure everything can find each other
2. **setup_lexicon.py** - Creates and initializes the lexicon directories and files
3. **connect_blackwall.py** - Main connector that links all components together
4. **Core_Pipeline/run_blackwall.py** - Actual runner to start the bot in interactive mode

## Step-by-Step Connection Process

### Step 1: Fix File Paths

First, run the fix_paths.py script to ensure all files have proper path references:

```python
python fix_paths.py
```

This will:

- Create fragment profiles in Core_Personality if they don't exist
- Create test prompts for interacting with the system
- Fix path references in key files to ensure they find the right resources

### Step 2: Set up the Lexicon

Next, set up the lexicon directories and files:

```python
python setup_lexicon.py
```

This will:

- Create the lexicon directory structure in Core_Pipeline
- Initialize the left hemisphere lexicon (word->emotion mappings)
- Initialize the right hemisphere lexicon (variant->canonical mappings)

### Step 3: Connect System Components

Connect all the Blackwall components:

```python
python connect_blackwall.py
```

This will:

- Add core directories to the Python path
- Create necessary directories if missing
- Import and verify key modules
- Set up the pipeline configuration
- Check for missing files and create templates as needed

### Step 4: Run the Bot

Navigate to the Core_Pipeline directory and run the interactive mode:

```bash
cd Core_Pipeline
python run_blackwall.py --interactive
```

This will start the bot in interactive mode where you can chat with it and help it learn.

## Troubleshooting

If you encounter any issues:

1. **Missing files**: Make sure all the Core_* directories exist with their required files
2. **Import errors**: Run fix_paths.py again to ensure correct paths
3. **Lexicon errors**: Run setup_lexicon.py to recreate the lexicon files
4. **Memory errors**: Check if the Core_Memory directory has the required memory files
5. **Pipeline errors**: Verify that blackwall_pipeline.py and blackwall_core.py exist and are properly set up

## Learning Process

Once the bot is running, it will:

1. Process input through the lexicon to generate emotional weights
2. Select personality fragments based on these weights
3. Generate a response that reflects the chosen fragments
4. Store interactions in the memory system for learning

You can enhance the learning process by:

- Adding more entries to the lexicon files
- Creating more detailed fragment profiles
- Running with the --learn flag to enable memory processing

## Advanced Usage

For advanced usage, try:

- `python run_blackwall.py --batch` to run a batch of predefined prompts
- `python run_blackwall.py --test` to run test mode with diagnostic output
- `python run_blackwall.py --learn` to enable active learning mode
