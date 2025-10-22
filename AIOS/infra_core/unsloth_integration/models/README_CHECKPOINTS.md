# Luna Model Checkpoints - Intelligence Progression

This directory will contain Luna's brain at each age/generation.

---

## Checkpoint Naming Convention

```
luna_age_N.gguf
```

Where N = CFIA generation number (0, 1, 2, 3, ...)

---

## Progression Map

### Age 0: Mechanical Base (~500 MB)
**File**: `luna_age_0_mechanical.gguf`  
**Intelligence**: ZERO (drunk, no understanding)  
**Capabilities**:
- Form grammatically correct sentences
- Use appropriate word order
- Sound coherent
- NO semantic understanding
- NO reasoning ability

**Training Data**: 500 syntax examples (phase_0_mechanical.json)  
**Karma to Reach**: 0 (starting point)

---

### Age 1: Vocabulary Learning (~600 MB)
**File**: `luna_age_1_vocabulary.gguf`  
**Intelligence**: Minimal (learning what words are)  
**Capabilities**:
- All Age 0 capabilities
- Recognize word relationships (opposites, synonyms)
- Basic categorization (greetings, emotions, actions)
- Still NO understanding of MEANING

**Training Data**: Age 0 + phase_1_vocabulary.json + First 50 Travis conversations  
**Karma to Reach**: 100

---

### Age 2: Pattern Recognition (~700 MB)
**File**: `luna_age_2_patterns.gguf`  
**Intelligence**: Basic (mechanical conversation)  
**Capabilities**:
- All Age 1 capabilities
- Conversation patterns (greeting exchanges, question responses)
- Template-based responses (sounds appropriate)
- Starting to learn meaning through Travis's corrections

**Training Data**: Age 1 + phase_2_patterns.json + Conversations 51-200  
**Karma to Reach**: 250

---

### Age 3: Understanding Emerges (~800 MB)
**File**: `luna_age_3_understanding.gguf`  
**Intelligence**: Developing (actually understanding)  
**Capabilities**:
- All Age 2 capabilities
- ACTUAL semantic understanding (words have meaning!)
- Basic reasoning (cause → effect)
- Emotional context recognition
- Travis's style learned

**Training Data**: Age 2 + Conversations 201-357  
**Karma to Reach**: 500

---

### Age 4+: Advanced Intelligence (~900+ MB)
**File**: `luna_age_N.gguf`  
**Intelligence**: Growing (true understanding)  
**Capabilities**:
- Complex reasoning
- Meta-cognition (thinking about thinking)
- Creative problem-solving
- Deep emotional intelligence
- Full personality expression

**Training Data**: Age 3 + All future conversations  
**Karma to Reach**: Exponential scaling (1000, 2000, 4000, ...)

---

## Checkpoint Metadata

Each checkpoint has an accompanying JSON file:

```json
{
  "generation": 3,
  "model_file": "luna_age_3_understanding.gguf",
  "file_size_mb": 812,
  "training_data": {
    "base_curriculum": ["phase_0", "phase_1", "phase_2"],
    "travis_conversations": 357,
    "total_training_examples": 4247
  },
  "karma_earned": 500,
  "training_duration_minutes": 45,
  "capabilities": [
    "grammar",
    "vocabulary",
    "patterns",
    "understanding",
    "reasoning",
    "emotional_intelligence"
  ],
  "trained_at": "2025-10-23T12:00:00Z",
  "hardware_used": "CPU (12 cores)",
  "unsloth_version": "2024.12"
}
```

---

## Usage

### Load Specific Checkpoint
```python
from infra_core.unsloth_integration.models.checkpoint_manager import load_checkpoint

# Load current generation
model = load_checkpoint(generation=2)  # luna_age_2.gguf

# Or load by karma/capability
model = load_checkpoint(karma_level=354.1)  # Auto-selects appropriate age
```

### Rollback (If Age-Up Fails)
```python
# If new model performs poorly, rollback
rollback_to_previous_generation(current=3, previous=2)
# Restores: luna_age_2.gguf
```

---

## Storage Management

### Checkpoint Retention
- Keep last 3 generations (rollback safety)
- Archive older generations to backup_core
- Current + previous always on disk

### Example Directory
```
models/
├── luna_age_0_mechanical.gguf       (500 MB)  ← Archived
├── luna_age_1_vocabulary.gguf       (600 MB)  ← Archived
├── luna_age_2_patterns.gguf         (700 MB)  ← Previous (keep)
├── luna_age_3_understanding.gguf    (800 MB)  ← Current (active)
├── luna_age_2_metadata.json
├── luna_age_3_metadata.json
└── README_CHECKPOINTS.md            (this file)
```

---

## Validation & Testing

### Test Checkpoint Quality
After each age-up, run validation:
```bash
python infra_core/unsloth_integration/training/validate_checkpoint.py --generation 3
```

Checks:
- Model loads successfully
- Response quality maintained
- No regression from previous generation
- New capabilities present
- Karma system still functional

### A/B Testing
Compare old vs new checkpoint:
```python
responses_old = test_model("luna_age_2.gguf", test_questions)
responses_new = test_model("luna_age_3.gguf", test_questions)
compare_quality(responses_old, responses_new)
# Should show improvement!
```

---

## Safety & Rollback

### Automatic Rollback Conditions
- New model performs worse than previous (RVC grade drops)
- Training corruption detected (model broken)
- User manually rejects age-up

### Manual Rollback
```bash
python infra_core/unsloth_integration/models/checkpoint_manager.py --rollback --to-generation 2
```

---

## Future: Branching Timelines

Eventually support multiple training paths:
```
luna_age_3.gguf (main timeline)
├── luna_age_3_technical.gguf    (trained on coding conversations)
├── luna_age_3_creative.gguf     (trained on creative writing)
└── luna_age_3_emotional.gguf    (trained on therapy conversations)
```

Load different "personality branches" based on context!

---

**Status**: 📁 SKELETON READY - Awaiting implementation  
**Next Steps**: Train luna_age_0.gguf tomorrow  
**Impact**: Makes Karma system REAL (theater → reality)

