# Blackwall Looking Glass UI

The Looking Glass UI provides a centralized dashboard for monitoring, testing, and interacting with the Blackwall symbolic/emotional fusion engine. It serves as a control center for developers working with the system, allowing them to run tests, visualize results, and interact directly with the Blackwall pipeline.

## Features

### Master Terminal Interface
- **Unified Looking Glass**: Combined visualization and interactive experience with real-time graphs
- **Optimized Dashboard**: Fast performance visualization with responsive graphs
- **Log Visualization**: View fragment activations, emotion profiles, and token statistics
- **Batch Testing**: Run pipeline test batches with configurable loop counts
- **Continuous Learning**: Start indefinite learning mode for long-term system evolution
- **Interactive Mode**: Directly interact with the Blackwall pipeline using text prompts
- **Log Inspection**: Quickly view recent log entries without leaving the UI
- **Multiple Visualization Options**: Choose between different visualization types

### Unified Looking Glass
- **Combined Experience**: Both visualization and interaction in one interface
- **Real-time Fragment Activation**: See fragment levels change with usage
- **Dynamic Charts**: Fragment weights history, emotion profiles, and blend usage
- **Direct LLM Chat**: Test interactions right in the interface
- **Auto-refresh**: Data updates automatically every few seconds
- **Optimized Performance**: Smooth graphics and responsive interface

### Legacy Visualization Options
- **Classic Graph UI**: Detailed analysis with multi-panel synchronized graphs
- **Pygame Interface**: Traditional bar graphs and text interface
- **Optimized Dashboard**: Fast-rendering, lightweight visualizer

## Getting Started

### Running the UI

#### Windows
```
run_looking_glass.bat
```

#### Linux/Mac
```
./run_looking_glass.sh
```

Or manually:
```
python Copilot/blackwall_master_terminal.py
```

### Navigation

The master terminal provides a menu-driven interface:
1. 🌟 Unified Looking Glass: Opens the new combined visualization and interaction UI
2. 📊 Optimized Dashboard: Opens the fast graph UI with improved performance
3. 🪞 Classic Log Graph: Opens the detailed analytics tool with multiple panels
4. 🎮 Looking Glass Pygame UI: Opens the traditional graphical UI
5. 🧠 Start Continuous Learning Mode: Runs the pipeline indefinitely for ongoing learning
6. 🧪 Run Pipeline Test Batch: Runs the pipeline with a specific number of test prompts
7. 💬 Run Interactive Mode: Start an interactive session with Blackwall
8. ⚙️ Set Number of Test Loops: Configure batch testing
9. ⏹ Stop All Running Processes: Halt any running processes
0. 📜 Show Last 5 Log Entries: Quick log preview
X. 🚪 Exit Wonderland: Exit the interface

## Continuous Learning Mode

The new continuous learning mode allows you to run Blackwall in an indefinite learning process. This is useful when:

- You want to leave the system running overnight or when you're away
- You need to build up a large history of data for visualization
- You're testing long-term stability of the emotional fusion engine
- You want to allow the system's weights to evolve naturally over time

This mode will continue running until explicitly stopped from the menu or by closing the terminal.

## Technical Notes

- The Looking Glass UI works with both the legacy pipeline and new core architecture
- Dependencies will be automatically installed if needed (pygame, matplotlib, numpy, requests)
- All visualizations read from the standard logs in BLACKWALL_LOGS.md
- The Unified Looking Glass provides the most complete experience
- For performance issues, use the Optimized Dashboard instead of the Classic Graph

## Emotional Design

The Looking Glass UI is designed to reflect the emotional nuance and empathy at the core of the Blackwall system:

- **Fragment Activation Visualization**: Colors reflect the emotional signature of each fragment
- **Combined Visualization**: The unified interface allows both analytical and intuitive understanding 
- **Neon Aesthetic**: The glowing interface elements represent the living emotional core of Blackwall
- **Interactive Echo**: Responses provide immediate emotional feedback for better understanding
- **Terminal Connection**: The text-based interface maintains an intimate connection to Blackwall's core

## Comparison of Visualization Options

| Feature | Unified Looking Glass | Optimized Dashboard | Classic Graph | Pygame UI |
|---------|---------------------|-------------------|-------------|-----------|
| Visualization | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Performance | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Interactivity | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Detail Level | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Aesthetic | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Chat Integration | ⭐⭐⭐⭐⭐ | ❌ | ❌ | ⭐⭐⭐⭐ |

## Advanced Usage

- Use the Unified Looking Glass for the best overall experience
- Use the Optimized Dashboard when you need the fastest performance
- Run continuous learning mode when you want to build up more data for visualization
- For best results, run test batches with at least 5 loops to get meaningful visualization data
- Use keyboard shortcuts in the Unified Looking Glass:
  - F5: Manual refresh of data
  - Esc: Exit to terminal
  - Enter: Send message to LLM
