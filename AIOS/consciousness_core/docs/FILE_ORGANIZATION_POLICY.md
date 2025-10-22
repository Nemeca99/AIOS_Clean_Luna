# Blackwall v2 File Organization Policy

## Core Directory Structure

The Blackwall project is organized into the following core directories:

- **Core_Pipeline**: Contains all pipeline processing files and components
- **Core_Memory**: Contains memory management and storage-related files
- **Core_Personality**: Contains personality and identity-related files
- **Core_Utils**: Contains utility functions, diagnostics, and helper tools
- **Core_Extra**: Contains uncategorized or specialized files that don't fit elsewhere
- **Core_Copilot**: Contains documentation, build logs, and organization policies

## File Placement Rules

### Core_Pipeline

- Processing engines and pipeline components
- Data transformation scripts
- Text processing utilities
- Tokenization and embedding tools
- Pipeline configuration files
- Pipeline service integrations

### Core_Memory

- Memory storage management
- Retrieval mechanisms
- Long-term/short-term memory handlers
- Memory encoding/decoding utilities
- Memory context management
- Knowledge base connections

### Core_Personality

- Personality profiles
- Identity structures
- Behavioral parameters
- Emotional response systems
- Character traits configuration
- Personality weights and vectors

### Core_Utils

- General utility functions
- Diagnostic tools
- Logging mechanisms
- Testing frameworks
- Helper scripts
- Common libraries

### Core_Extra

- Specialized tools with unique functions
- Experimental features
- Files pending categorization
- Archive of outdated but potentially useful code
- Documentation that doesn't fit elsewhere

### Core_Copilot

- Build logs
- System documentation
- Organization policies
- Planning documents
- Architecture diagrams
- Development guidelines

## Naming Conventions

1. **File Names**: Use snake_case for all Python files and descriptive names for other file types
2. **Module Names**: Should clearly indicate their function
3. **Class Names**: Use PascalCase
4. **Function Names**: Use snake_case
5. **Constants**: Use UPPER_SNAKE_CASE
6. **Private Members**: Prefix with underscore (_)

## Import Standards

1. Standard library imports first
2. Third-party library imports second
3. Local module imports third
4. Within each section, alphabetical order
5. Absolute imports preferred over relative imports

## Documentation Requirements

1. Each file must have a header comment with:
   - Brief description
   - Author
   - Date created/modified
   - Purpose

2. Each class and function must have docstrings explaining:
   - Purpose
   - Parameters
   - Return values
   - Exceptions raised

## File Migration Process

When moving files between directories:

1. Use the `organize_new_files.py` script to suggest appropriate locations
2. Update the `update_imports.py` script to fix import paths
3. Run verification scripts to ensure functionality
4. Update the Build Log with any changes made

## Housekeeping Schedule

1. **Daily**: Organize any new files created
2. **Weekly**: Run the verification script to check directory integrity
3. **Monthly**: Review the Core_Extra folder for files that can be properly categorized
4. **Quarterly**: Full code review and organization audit

## Adding New Files

When adding new files to the project:

1. Determine the appropriate Core directory based on functionality
2. Follow the naming conventions
3. Include proper documentation
4. Add necessary imports following the import standards
5. Register the new file in the Build Log

## Plugin/Extension Development

When developing new plugins or extensions:

1. Create a dedicated subfolder in the appropriate Core directory
2. Include a README.md file explaining the plugin's purpose
3. Follow the standard project structure within the plugin folder
4. Create proper interfaces for integration with the main system

## Conflict Resolution

If a file could belong to multiple Core directories:

1. Place it in the directory most aligned with its primary function
2. Create appropriate imports in other directories as needed
3. Document the decision in the Build Log

## Version Control Guidelines

1. Commit messages should reference the files modified and their core directories
2. Branch names should include the core directory they primarily affect
3. Pull requests should maintain the established organization structure

This policy is to be reviewed and updated quarterly as the project evolves.

# Lyra Blackwall Reorganization Summary

## Completed Reorganization

The Lyra Blackwall project files have been successfully reorganized into functional categories as requested. Files from Core_Backup are now distributed across the following folders according to their function:

### Core_Pipeline

Contains the core pipeline processing files and scripts:

- Main processing scripts like blackwall_pipeline.py, blackwall_core.py
- Lexicon processing files like lexicon_service.py, lexicon_filter.py
- Runtime scripts like run_blackwall.bat/sh
- Pipeline documentation and refactoring notes

### Core_Memory

Contains memory management and processing files:

- Memory processing scripts like process_and_learn_memories.py
- Memory reprocessing tools like reprocess_memory_files.py
- Vector search functionality with vector_search.py
- Memory indexing scripts like generate_memory_index.py
- Memory-related batch and shell scripts

### Core_Personality

Contains personality and identity definition files:

- Fragment profiles like fragment_profiles.json
- Emotion engine definitions like lyra_emotion_engine_v3.json
- Identity definitions like lyra_identity_v3.json
- Voice and behavioral protocols
- Personality-related Python scripts

### Core_Utils

Contains utility and diagnostic scripts:

- Setup scripts like setup_blackwall.py, verify_setup.py
- Diagnostic tools like memory_diagnostics.py
- Visualization tools like unified_looking_glass.py
- Testing scripts like test_lexicon_service.py
- Documentation and requirements files

### Core_Extra

Contains all other files that don't fit clearly into the above categories:

- Additional scripts and tools
- Miscellaneous documentation
- Alternative implementations
- Development and test files
- Legacy files for reference

### Core_Copilot

Contains build logs and documentation about the reorganization process:

- Build_Log.md documenting all changes made
- RECOMMENDED_STRUCTURE.md with recommendations for future organization

## Verification

A verification script (verify_reorganization.py) has been created to ensure all required directories exist and contain the expected key files. All verification checks have passed, confirming that the reorganization is complete and successful.

## Recommendations for Further Organization

1. Review files in Core_Extra to determine if any should be moved to more specific locations
2. Update import statements in Python files to reflect the new folder structure
3. Test the system thoroughly to ensure all components work with the new organization
4. Consider further organizing Core_Utils into subdirectories like Scripts, Diagnostics, Visualization, etc.
5. Update documentation to reflect the new organization

## Build Log

A detailed build log has been maintained in Core_Copilot/Build_Log.md, documenting all changes made during the reorganization process.

## Pipeline Connection and System Integration

To ensure proper operation of the Blackwall system, components must be properly connected. The following guidelines apply to system integration:

1. **Core Component Connectivity**:
   - Core_Pipeline components must have clear import paths to Core_Memory and Core_Personality
   - Lexicon directories must be properly structured with left and right hemispheres
   - All connections between components should use relative imports where possible

2. **Integration Scripts**:
   - System connector scripts should be stored at the project root
   - These scripts must use absolute paths derived from the root directory
   - Include proper error handling for missing components or configuration

3. **Path Management**:
   - Always use os.path.join() for cross-platform compatibility
   - Store configuration files in consistent locations
   - Use `__file__` to determine script locations rather than hard-coded paths

4. **Documentation**:
   - Any changes to system integration must be documented in Build_Log.md
   - System connection processes should have clear step-by-step guides
   - Major architecture changes require updates to connection documentation

5. **Verification**:
   - After any structural changes, run verification scripts to ensure integrity
   - Test all critical paths and component connections
   - Ensure system can initialize and run properly after all changes

The following core connector files must be maintained and updated when making structural changes:

- connect_blackwall.py
- setup_lexicon.py
- fix_paths.py

These files ensure that all components can interact correctly regardless of installation location or system configuration.

