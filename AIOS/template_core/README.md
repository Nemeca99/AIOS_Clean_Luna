# Template Core - Create Your Own AIOS Plugin

This is a **reference implementation** showing how to create your own AIOS core plugin.

## Quick Start - Copy This Template

```bash
# 1. Copy this folder
cp -r template_core/ my_awesome_core/

# 2. Rename files
mv my_awesome_core/template_core.py my_awesome_core/my_awesome_core.py

# 3. Edit the files (see below)

# 4. Drop it in AIOS_Clean root
# Your core is now auto-discovered and ready!

# 5. Test it
python main.py --myawesome --test
```

That's it! Your core is now part of AIOS!

## File Structure

```
my_awesome_core/
├── __init__.py              # Import your main class/function
├── my_awesome_core.py       # Main plugin code (REQUIRED)
├── config/
│   └── config.json          # Auto-created if missing
└── README.md                # Documentation for users
```

## Required Function: `handle_command()`

Every core MUST have this function:

```python
def handle_command(args: List[str]) -> bool:
    """
    Check if command is for this core.
    Return True if handled, False otherwise.
    """
    if '--mycommand' in args:
        # Handle it
        do_something()
        return True
    return False  # Not for me
```

## Step-by-Step Customization

### 1. Update `__init__.py`

```python
from .my_awesome_core import handle_command, MyAwesomeCore

__all__ = ['handle_command', 'MyAwesomeCore']
```

### 2. Update Class Name in `my_awesome_core.py`

```python
class MyAwesomeCore:  # Change from TemplateCore
    def __init__(self):
        self.name = "my_awesome_core"  # Your core name
        # ... rest of init
```

### 3. Define Your Commands

```python
def handle_command(args):
    my_commands = [
        '--myawesome',      # Main command
        '--myawesome-do',   # Sub-command
        '--myawesome-test', # Test command
    ]
    
    if not any(cmd in args for cmd in my_commands):
        return False  # Not for us
```

### 4. Implement Your Logic

```python
if '--myawesome' in args:
    # Your code here
    result = do_my_awesome_thing()
    print(f"✅ {result}")
    return True
```

## Best Practices

### ✅ DO:
- Auto-create config files if missing
- Use friendly error messages
- Return True/False correctly in handle_command()
- Handle exceptions gracefully
- Support --debug flag for detailed errors
- Keep it simple and focused

### ❌ DON'T:
- Assume files exist (check first!)
- Show cryptic errors to users
- Modify other cores' files
- Use absolute paths (use Path() relative to core)
- Block the main thread (use async if needed)

## Testing Your Core

### Test Standalone:
```bash
python my_awesome_core/my_awesome_core.py --myawesome-test
```

### Test in AIOS:
```bash
python main.py --myawesome --test
```

### Test Discovery:
```bash
python main.py --ping --core myawesome --depth 2
```

## Configuration

Auto-create config in `config/` folder:

```python
def _load_config(self):
    config_file = Path(__file__).parent / "config" / "config.json"
    
    default_config = {
        "enabled": True,
        "setting1": "value1",
    }
    
    if not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    
    with open(config_file, 'r') as f:
        return json.load(f)
```

## Error Handling

Always use friendly messages:

```python
try:
    result = do_something()
except FileNotFoundError:
    print("⚠️  Required file not found.")
    print("   Please run: setup_my_core.py")
    return True
except Exception as e:
    print(f"❌ Error: {e}")
    if '--debug' in args:
        import traceback
        traceback.print_exc()
    return True
```

## Dependencies

If your core needs other cores:

```python
def handle_command(args):
    # Check if required core exists
    if not Path('data_core').exists():
        print("⚠️  This core requires data_core")
        print("   Please install: data_core/")
        return True
    
    # Import and use it
    from data_core import DataCore
    # ... use it
```

## Help Command

Add help for your core:

```python
if '--help' in args and '--myawesome' in args:
    print("""
    My Awesome Core - Does awesome things!
    
    Commands:
      --myawesome <arg>       Main command
      --myawesome-test        Test the core
      --myawesome-config      Show configuration
    
    Examples:
      python main.py --myawesome "do something"
      python main.py --myawesome-test
    """)
    return True
```

## OS Compatibility

Use Path() for cross-platform paths:

```python
from pathlib import Path

# ✅ Good - works everywhere
config_file = Path(__file__).parent / "config" / "config.json"

# ❌ Bad - Windows only
config_file = "config\\config.json"
```

## Plugin Checklist

Before releasing your core:

- [ ] `handle_command()` function exists
- [ ] Returns True/False correctly
- [ ] Auto-creates config if missing
- [ ] Friendly error messages
- [ ] Works standalone (can test directly)
- [ ] Works in AIOS (discovered by main.py)
- [ ] README.md with usage examples
- [ ] No hardcoded paths
- [ ] Handles missing dependencies gracefully

## Examples of Good Cores

Look at these for inspiration:
- `main_core/` - System orchestration
- `luna_core/` - AI personality (if updated)
- `carma_core/` - Memory management

## Share Your Core!

Once you've built something cool:
1. Test it thoroughly
2. Add good documentation
3. Share it with the community!

People can drop your core into their AIOS and it just works! 🎉

