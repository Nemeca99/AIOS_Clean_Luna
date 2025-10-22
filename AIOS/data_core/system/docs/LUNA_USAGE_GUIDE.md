# 🌙 Luna Usage Guide

This guide covers how to use the Luna personality system with real-time output and continuous operation.

## 🚀 Quick Start

### Basic Luna Test
```bash
# Single question test
python "HiveMind/luna_main.py" --mode real_learning --questions 1

# Multiple questions
python "HiveMind/luna_main.py" --mode real_learning --questions 10
```

### Continuous Operation
```bash
# Run continuously with real-time output
python "HiveMind/continuous_real_luna.py"

# Run in background (Linux/Mac)
python "HiveMind/continuous_real_luna.py &

# Run in background (Windows PowerShell)
Start-Process python -ArgumentList "HiveMind/continuous_real_luna.py" -WindowStyle Hidden
```

## 🖥️ Windows Support

The system now includes full Windows console support:

### Unicode Encoding Fix
- ✅ All emoji characters display correctly
- ✅ Real-time output streaming
- ✅ Proper console encoding handling

### Windows-Specific Features
- **Console Encoding**: Automatic UTF-8 conversion for Windows
- **Signal Handling**: Graceful shutdown with Ctrl+C
- **Background Processing**: PowerShell-compatible background execution

## 📊 Real-Time Output

### What You'll See
```
🌙 Starting REAL Continuous Luna Data Gathering
============================================================
⏰ Started: 17:41:02
🔄 Mode: Continuous question processing with REAL LLM
⏱️ Delay: 3-5 seconds between questions (random)
🛑 Press Ctrl+C to stop gracefully
============================================================

🔄 Running Luna Question #1
============================================================
🚀 Starting Luna...
✅ CARMA system imports successful
🌙 LUNA MASTER TEST - COMPLETE CLI CONTROL
============================================================
🎯 Mode: real_learning
❓ Questions: 1 (from 120 Big Five)
🔄 Test Runs: 1
⚙️ Tokens: 2000, Temp: 0.7, Top-p: 0.9
🧠 RAG System: Enabled (standard mode, 3 context, 5.0MB cache, 50 msgs)
🔗 Depth Control: Queue=5, Stack=7 → Chain ceiling=7, Stack ceiling=8
🎲 Fixed Questions: False
============================================================
```

### Progress Indicators
- 🚀 **Starting Luna...** - Process initialization
- ✅ **Luna completed successfully** - Question completed
- ⏳ **Processing...** - Shows when no output for 5+ seconds
- 💤 **Waiting X.Xs before next question...** - Delay between questions

## 🔧 Configuration Options

### Luna Main System
```bash
python "HiveMind/luna_main.py" --help
```

**Key Options:**
- `--mode real_learning` - Enable learning mode
- `--questions N` - Number of questions to process
- `--delay X.X` - Delay between questions (seconds)
- `--verbose` - Detailed output logging

### Continuous System
The continuous system runs with these defaults:
- **Questions per cycle**: 1
- **Delay range**: 3-5 seconds (random)
- **Timeout**: 120 seconds per question
- **Background capable**: Yes

## 📈 Performance Monitoring

### Real-Time Metrics
- ⏱️ **Response Time**: Time for Luna to respond
- 🔢 **Token Usage**: Input → Output token counts
- 🎂 **Luna Age**: Current age and cycle information
- 💭 **Dream Insights**: Memory consolidation results
- ✅ **Success Rate**: Percentage of successful responses

### Example Output
```
--- Q1/1 (openness) ---
👤 User: I am someone who seldom gets lost in thought
🎂 Luna Age: 1 | Messages in cycle: 1/41
🍄 Mycelium Collective: Analyzing question with neural network...
🍄 Mycelium Network: 3 related fragments
🧠 Collective Intelligence: 11 fragments, 0 neural pathways
🌙 Luna: Yeah, me neither. I mean, sometimes I'm deep in the rabbit hole of a thought or problem, but it's not like I get 'lost.' It's more like I'm tracking every twist and turn of my mind. It's kind of a ride, actually. You? Do you find yourself lost often, or are you more of a navigator like me?
⏱️ Time: 14.6s
🔢 Tokens: 347→84 = 431
🌙 Light Sleep (Daydreaming): Processing Question 1: openness...
💭 Daydream Insights: 1 insights gained
   • General contemplation and mental reorganization
```

## 🛠️ Troubleshooting

### Common Issues

**Unicode/Emoji Display Issues**
- ✅ **Fixed**: Windows console encoding now handled automatically
- ✅ **Fixed**: All emoji characters display correctly

**Output Not Real-Time**
- ✅ **Fixed**: Subprocess now streams output immediately
- ✅ **Fixed**: No more buffering delays

**Background Process Issues**
- Use `Start-Process` on Windows for proper background execution
- Check process with `Get-Process python` or Task Manager

### Debug Mode
```bash
# Run with verbose output
python "HiveMind/luna_main.py" --mode real_learning --questions 1 --verbose

# Check system status
python "HiveMind/master_main.py" status
```

## 🔄 Continuous Operation

### Starting Continuous Mode
```bash
python "HiveMind/continuous_real_luna.py"
```

### Stopping Gracefully
- Press **Ctrl+C** to stop gracefully
- System will complete current question before stopping
- All data is saved automatically

### Background Operation
```bash
# Linux/Mac
nohup python "HiveMind/continuous_real_luna.py" > luna.log 2>&1 &

# Windows PowerShell
Start-Process python -ArgumentList "HiveMind/continuous_real_luna.py" -WindowStyle Hidden
```

## 📁 Data Storage

### Learning Results
- **Location**: `../AI/personality/learning_results/`
- **Format**: JSON files with timestamps
- **Content**: Question responses, timing, token usage

### Recovery Data
- **Location**: `C:\Users\[user]\AppData\Local\Temp\hive_mind_recovery\`
- **Purpose**: System state recovery
- **Auto-cleanup**: Yes, on successful completion

## 🎯 Best Practices

### For Development
1. Start with single questions to test setup
2. Use continuous mode for extended testing
3. Monitor token usage and response times
4. Check logs for any errors or warnings

### For Production
1. Run in background mode for long-term operation
2. Monitor system resources (RAM, CPU)
3. Set up log rotation for large datasets
4. Implement health checks and monitoring

### For Research
1. Use consistent question sets for reproducibility
2. Document all configuration changes
3. Save results with timestamps and metadata
4. Run multiple trials for statistical significance

## 📞 Support

### Getting Help
- Check this guide for common issues
- Review console output for error messages
- Check log files in recovery directory
- Use `--verbose` flag for detailed debugging

### System Requirements
- **Python**: 3.11+
- **RAM**: 8GB+ recommended
- **Storage**: 1GB+ for data and logs
- **OS**: Windows 10+, Linux, macOS

---

**The Luna system now provides real-time, continuous operation with full Windows support and comprehensive monitoring capabilities.**
