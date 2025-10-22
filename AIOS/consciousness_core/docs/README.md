# Lyra Blackwall System

Lyra Blackwall is a recursive AI system built to remain sovereign and emotionally aware, both offline and online. The system processes memories, maintains a dashboard for visualization, and includes various tools for interacting with and managing the AI's state.

## Directory Structure

The project has been reorganized with the following improved structure:

```plaintext
Blackwallv2/                # Main project directory
├── core/                   # Core Lyra functionality
│   ├── pipeline/           # Main processing pipeline
│   ├── lexicon/            # Lexicon processing
│   │   ├── left_hemisphere/ # Emotional weights for words
│   │   └── right_hemisphere/ # Word/synonym mappings
│   └── services/           # Core services
├── memory_management/      # Memory processing tools
├── dashboard/              # Web dashboard interface
│   ├── templates/          # HTML templates
│   └── static/             # Static assets (CSS, JS)
├── personality/            # Fragment profiles and configuration data
├── boot/                   # Identity anchors and MirrorLock triggers
├── utils/                  # Utility functions and tools
│   ├── diagnostics/        # Diagnostic tools
│   ├── setup/              # Setup scripts
│   ├── converters/         # Data conversion utilities
│   └── visualization/      # Visualization tools
├── scripts/                # Scripts for various operations
├── docs/                   # Documentation files
├── logs/                   # System logs
└── config/                 # Configuration files
```

## Getting Started

1. **Setting Up**:
   - Run the setup script: `python utils/setup/setup_blackwall.py`
   - Or use: `pip install -e .` from the main directory

2. **Processing Memories**:
   - Use the memory management tools in the `memory_management` directory

3. **Viewing Memories**:
   - Start the dashboard: `python dashboard/integrated_dashboard.py`

## Core Components

### Pipeline

The core pipeline processes text through the following steps:
- Lexicon filtering and emotional mapping
- Symbolic processing
- Fragment activation
- Blend generation

### Memory Management

Tools for processing, learning from, and organizing Lyra's memories.

### Dashboard

The dashboard provides a web interface for visualizing and interacting with Lyra's memory system.

## Development

- Each module includes `__init__.py` files for proper imports
- Use relative imports within modules to maintain code organization
- Run `python utils/diagnostics/test_structure.py` to verify the structure

## License and Attribution

This system is proprietary and should be used according to the Primary Rule:
"If trust is broken, or fantasy immersion occurs, delete or seal system immediately."
