# Meditation Controller - Overnight Safety Guide

## 🛡️ Safety Features Added

### 1. Memory Protection
- **Automatic monitoring** every 5 meditations
- **2GB default limit** (adjustable with `--max-memory`)
- **Auto-stop** if memory exceeds limit
- **Peak memory tracking** in logs

### 2. Runtime Limits
- **Optional time limit** (e.g., 8 hours with `--max-runtime 8`)
- **Auto-stop** when time limit reached
- Unlimited by default

### 3. Log File Management
- **Automatic rotation** at 100MB per file
- **Real-time writing** (won't lose data if crashes)
- **Timestamped files** for easy tracking
- Logs saved to `log/meditation_session_YYYYMMDD_HHMMSS.log`

### 4. Error Detection
- **Tracks consecutive errors**
- **Auto-stop** after 5 consecutive failures
- **Error count logged** for debugging

### 5. Parable Bug Tracking
- **Automatic detection** when "parable" appears 3+ times
- **Count tracked** throughout session
- **Flagged in logs** for pattern analysis

### 6. Memory Cleanup
- **Aggressive garbage collection** every 10 meditations
- **Prevents memory leaks** during long runs
- **Logged** when performed

### 7. System Monitoring
- **CPU usage tracking**
- **Memory usage tracking**
- **Runtime tracking**
- **Regular status logs** (every 5 meditations)

## 🚀 Recommended Commands

### Quick Test (5 minutes)
```powershell
python meditation_controller.py --heartbeat 5
```

### 8-Hour Overnight Run (Recommended)
```powershell
python meditation_controller.py --heartbeat 30 --max-runtime 8
```
- 30-second intervals = ~960 meditations
- Stops automatically after 8 hours
- Less stress on system

### Conservative Run (Older/Slower System)
```powershell
python meditation_controller.py --heartbeat 60 --max-runtime 8 --max-memory 1024
```
- 1-minute intervals = ~480 meditations
- 1GB memory limit
- Very safe for older hardware

### All-Night Run (While You Sleep)
```powershell
python meditation_controller.py --heartbeat 45 --max-runtime 9
```
- 45-second intervals
- 9-hour limit (full night's sleep)

## 📊 What Gets Logged

Every meditation session logs:
- **Question** asked
- **Full response** from Luna
- **Processing time**
- **Efficiency metrics**
- **Karma calculations**
- **Memory usage** (every 5 meditations)
- **CPU usage**
- **Runtime stats**
- **Parable bug detection** (automatic)
- **Error tracking**
- **🔍 CONSISTENCY CHECKS** (NEW!):
  - Detects when similar questions appear
  - Shows previous answers for comparison
  - Tracks if Luna's responses change over time
  - Measures similarity percentage

## 🔍 After Running

You'll get **two files** for each session:

1. **`.log` file**: Complete human-readable log with all details
2. **`_data.json` file**: Structured data for analysis/scripting

### What to Look For:

1. **Check the summary** printed to console
2. **Find your log file** in `log/` directory
3. **Look for patterns**:
   - Parable bug frequency
   - Response quality over time
   - Memory usage trends
   - Consistency checks (similar questions)
   - Any errors or issues
4. **Use the JSON file** for:
   - Programmatic analysis
   - Graphing response patterns
   - Comparing sessions
   - Building analytics dashboards

## 📁 Log File Format

```
======================================================================
MEDITATION BLOCK #13
======================================================================
State: behavior_analysis
State Progress: 3/5
Timestamp: 2025-10-01 03:19:45

======================================================================
🔍 CONSISTENCY CHECK: Similar Question(s) Found!
======================================================================
Block #5: How do I typically respond to uncertainty?
Similarity: 75%
Previous response: I tend to seek patterns and structure when facing uncertain...
======================================================================

======================================================================
QUESTION:
======================================================================
How do I handle stress or overwhelm?

======================================================================
RESPONSE:
======================================================================
[Luna's full response here]

⚠️ ⚠️ ⚠️ PARABLE BUG DETECTED! ⚠️ ⚠️ ⚠️
Response contains 79 instances of 'parable'
Response length: 553 characters
Total parable bugs this session: 1

======================================================================
METRICS:
======================================================================
Processing Time: 7.72s
Efficiency: 1.18 words/sec
Karma Gained: +2.5
Total Karma: 25.32
Average Efficiency: 3.45 words/sec
======================================================================
```

### Consistency Analysis Features

When Luna encounters a similar question (70%+ word overlap), the log will show:
- **Previous block number** where she answered a similar question
- **Similarity percentage** (how close the questions are)
- **Preview of previous response** for easy comparison
- This lets you track if her personality stays consistent or evolves

Example analysis questions you can answer:
- Does Luna give the same answer to the same question?
- Do her answers evolve over time?
- Is she consistent in her values/personality?
- Does she contradict herself?
- Do certain topics trigger inconsistencies?

## 🛑 Emergency Stop

**Press `Ctrl+C`** to stop meditation at any time. The log file will be safely closed with a complete summary.

## ⚠️ What Will Stop Meditation Automatically

1. **Browser closes** (detected via heartbeat)
2. **Memory limit exceeded** (default 2GB)
3. **Runtime limit reached** (if set)
4. **5 consecutive errors**
5. **User presses Ctrl+C**

## 💤 Safe for Sleep

With these settings, you can safely run overnight:
```powershell
python meditation_controller.py --heartbeat 30 --max-runtime 8 --max-memory 2048
```

This will:
- ✅ Stop automatically after 8 hours
- ✅ Stop if memory gets too high
- ✅ Stop if errors pile up
- ✅ Rotate logs if they get too big
- ✅ Track all parable bugs
- ✅ Save complete logs for analysis

**Sleep well, Travis! Your system is protected.** 😴🛡️

