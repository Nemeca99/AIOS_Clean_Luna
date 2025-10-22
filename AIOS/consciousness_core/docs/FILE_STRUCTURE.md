# Blackwall File Structure

## Core and Symlinks

The Blackwall system follows a modular architecture where all core functionality exists in the `/core` directory. Files in other directories are symbolic links to maintain backward compatibility.

## File Organization

- `/core/` - Contains the definitive versions of all core files
  - `blackwall_pipeline.py` - The main pipeline implementation
  - `continuous_config.json` - Configuration for continuous operation
  - Additional core utility files

- `/lexicon/` - Contains symlinked files for backward compatibility
  - `blackwall_pipeline.py` -> symlink to `/core/blackwall_pipeline.py`

## Development Guidelines

1. Always make changes to files in the `/core/` directory
2. Never modify files directly in `/lexicon/` as they are symlinks
3. If you need to add a new file, consider placing it in `/core/` and create symlinks in other directories if needed

## Windows Symlink Note

On Windows, you may need administrator privileges to create symlinks. Use the following PowerShell command:

```powershell
New-Item -ItemType SymbolicLink -Path "lexicon\blackwall_pipeline.py" -Target "..\core\blackwall_pipeline.py"
```

Or with the `mklink` command in Command Prompt:

```cmd
mklink lexicon\blackwall_pipeline.py ..\core\blackwall_pipeline.py
```

## Backup

Previous versions of critical files are stored in `/core/backup` for reference but should not be used in the active system.
