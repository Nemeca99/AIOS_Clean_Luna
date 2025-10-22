# Blackwall Pipeline Refactoring and Optimization

## Updated Continuous Operation Features

The Blackwall pipeline has been refactored and optimized to support continuous operation with the following improvements:

### Memory and Performance Optimizations

- **BufferedLogger**: Reduces I/O overhead by buffering log messages and writing in batches
- **Adaptive Sleep**: Dynamically adjusts sleep time based on processing cycles
- **Performance Monitoring**: Tracks memory, CPU usage, and other system metrics
- **Periodic Cleanup**: Runs garbage collection and memory compaction at configurable intervals
- **Graceful Shutdown**: Ensures clean exit on interruption with proper resource cleanup

### Data Processing Improvements

- **Batch Processing**: Efficiently processes prompts in batches
- **Advanced Text Cleaning**: Improved text normalization for better style transfer
- **Automated Feedback**: Learns from past interactions to improve fragment weighting

### Configuration and Customization

- **Continuous Config**: Runtime parameters for controlling sleep times, thresholds, and batch sizes
- **Fragment Weight Management**: Automatic weight tuning based on performance

## Files and Structure

- `/core/blackwall_pipeline.py`: Core implementation with all optimizations
- `/lexicon/blackwall_pipeline.py`: Symlinked or updated with optimizations
- `/core/continuous_config.json`: Configuration for continuous operation

## Usage

The pipeline can be run in continuous mode:

```bash
python lexicon/blackwall_pipeline.py
```

Or in example mode:

```bash
python lexicon/blackwall_pipeline.py example
```

## Testing

A verification script can be run to test all optimizations:

```bash
python test_blackwall_pipeline.py
```

## Key Configuration Parameters

The continuous operation settings can be adjusted in `continuous_config.json`:

- `cycle_interval`: Target time for each processing cycle
- `memory_threshold`: Percentage threshold for memory warning
- `cpu_threshold`: Percentage threshold for CPU usage warning
- `log_buffer_size`: Number of log entries to buffer before writing
- `cleanup_frequency`: How often to run garbage collection
- `adaptive_timing`: Whether to use adaptive timing
- `performance_log_frequency`: How often to log performance metrics
- `batch_size`: Number of prompts to process in each batch
