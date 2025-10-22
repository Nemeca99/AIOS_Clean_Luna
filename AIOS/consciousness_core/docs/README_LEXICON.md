# Blackwall Lexicon System

## Overview

The Blackwall lexicon system is a sophisticated dual-hemisphere language processing system that is core to the emotional, cognitive, and stylistic capabilities of the Blackwall AI. This document explains how the lexicon works, how to use the new modular lexicon service, and the organization of lexicon files across the project.

## Dual Hemisphere Architecture

The lexicon uses a biological metaphor of left and right hemisphere functions:

### Left Hemisphere: Emotional Weight Mapping
- Maps words to emotional fragment weights
- Each word has weights for 9 emotional fragments:
  - Desire
  - Logic
  - Compassion
  - Stability
  - Autonomy
  - Recursion 
  - Protection
  - Vulnerability
  - Paradox
- Stored in JSON files (root_A.json through root_Z.json)
- Example: `"love": {"Desire": 60.0, "Compassion": 40.0}`

### Right Hemisphere: Synonym/Word Variant Mapping
- Maps word variations, synonyms, and related forms to canonical root words
- Helps normalize text for consistent emotional analysis
- Stored in JSON files (thesaurus_A.json through thesaurus_Z.json) 
- Example: `"loving": "love"`

## Integration in the Blackwall Pipeline

1. **Text Analysis**
   - When processing a prompt, the pipeline tokenizes the text
   - Each word is normalized using the right hemisphere
   - The normalized words are looked up in the left hemisphere
   - The resulting emotional weights influence the dynamic_fusion process

2. **Style Transfer**
   - After getting a root response from the LLM, style transfer is applied
   - The emotional profile from the lexicon affects which fragments are activated
   - The fragments determine the final styled response

3. **Continuous Learning**
   - The lexicon can update word weights based on feedback
   - New words can be added to the lexicon
   - The learning process is tracked in history files

## Using the New Lexicon Service

### Basic Usage

```python
from core.lexicon_service import get_lexicon_instance

# Get a singleton instance of the lexicon service
lexicon = get_lexicon_instance("blackwall")

# Analyze text to get emotional profile
text = "I love the logical structure of this paradoxical system"
profile = lexicon.analyze_text(text)
print(profile)
# Output: {'Desire': 32.0, 'Logic': 18.0, 'Compassion': 26.0, ... }

# Get weights for a specific word
weights = lexicon.get_word_weights("love")
print(weights)
# Output: {'Desire': 60.0, 'Compassion': 40.0}

# Update weights for a word
new_weights = {
    "Desire": 50.0,
    "Compassion": 50.0
}
lexicon.update_word_weights("love", new_weights, contributor="user_feedback")
```

### Advanced Usage

```python
from core.lexicon_service import LexiconService

# Create a custom instance
lexicon = LexiconService(
    left_master_path="/path/to/left_hemisphere_master.json",
    right_master_path="/path/to/right_hemisphere_master.json",
    stopwords_path="/path/to/stopwords.txt",
    personality="custom_system",
    enable_logging=True
)

# Normalize a word using the right hemisphere
canonical = lexicon.get_normalized_word("loving")
print(canonical)  # Output: "love"

# Get word weights without normalization
raw_weights = lexicon.get_word_weights("loving", normalize=False)

# Force reload the lexicon data (useful after file changes)
lexicon.reload_lexicon()
```

## Architecture Improvements

The new lexicon service includes several enhancements:

1. **Better Error Handling**
   - Graceful fallbacks for missing or incorrect data
   - Detailed error logging
   - Auto-recovery from common issues

2. **Performance Optimization**
   - Memory-efficient loading and processing
   - Better path resolution for finding lexicon files
   - Support for large lexicons with millions of entries

3. **Cleaner API**
   - Simple singleton access for common use cases
   - Consistent method signatures
   - Better documentation

4. **Better Logging**
   - Timestamped logs
   - Personality-tagged entries
   - Both machine and human-readable formats

## Future Enhancements

Planned improvements for the lexicon system:

1. **Persistence Layer**
   - Support for database-backed storage
   - Efficient updates and reads
   - Versioning of weight changes

2. **Enhanced Learning**
   - More sophisticated weight adjustment algorithms
   - Context-aware learning
   - Feedback-driven optimization

3. **Phrase Understanding**
   - Better multi-word phrase detection
   - Handling of idiomatic expressions
   - Contextual meaning extraction

4. **Performance Monitoring**
   - Tracking of lexicon usage patterns
   - Analytics for optimization
   - Cache hit/miss statistics

## File Organization

### Core Directory
The `/core` directory contains the canonical versions of all critical lexicon files:
- `lexicon_service.py` - The main lexicon service implementation
- `test_lexicon_service.py` - Comprehensive tests for the lexicon service
- `left_hemisphere_master.json` - Master index of left hemisphere emotional weight files
- `right_hemisphere_master.json` - Master index of right hemisphere synonym mapping files
- `stopwords.txt` - List of common words to exclude from lexicon processing
- `blackwall_pipeline_integration.py` - Example of integrating the lexicon service with the pipeline

### Lexicon Directory
The `/lexicon` directory contains utility scripts and raw lexicon data:
- `/left_hemisphere` - Contains raw lexicon data files for emotional weighting
- `/right_hemisphere` - Contains synonym mapping data files
- `/Hemisphere_Backup` - Backup copies of the hemisphere data
- `/archive` - Contains older versions of files that have been moved to core

All critical files in the `/lexicon` directory are symbolic links to their canonical versions in `/core` to maintain backward compatibility while ensuring a single source of truth.

### Utility Scripts
The original utility scripts for working with lexicon data remain in `/lexicon`:
- `auto_weight_lexicon.py` - Automatic weight generation for lexicon entries
- `convert_hemisphere_txt_to_json.py` - Converts raw text lexicon data to JSON format
- `convert_lexicon_to_emotion_weights.py` - Converts lexicon entries to emotional weight format
- `convert_thesaurus_to_mapping.py` - Converts thesaurus data to mapping format
- `lexicon_filter.py` - Legacy lexicon processing (replaced by core/lexicon_service.py)
- `spacy_bootstrap.py` - Helper script to ensure spaCy is properly installed

## Migration Notes

When updating existing code that uses the lexicon system:
1. Import the LexiconService from core.lexicon_service instead of using LexiconFilter
2. Update function calls to match the new API (see examples above)
3. Use the provided test_lexicon_service.py as a reference for implementation details