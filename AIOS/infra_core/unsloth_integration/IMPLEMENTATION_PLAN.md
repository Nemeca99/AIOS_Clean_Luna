# Unsloth Integration - Implementation Plan
**Tomorrow's Work Session at Work**

---

## ✅ Completed Tonight (Skeleton)

1. ✅ Created directory structure
2. ✅ Documented vision (README_TABULA_RASA.md)
3. ✅ Created curriculum templates (phases 0-3)
4. ✅ Wrote training pipeline stubs
5. ✅ Checkpoint system documentation

---

## 📋 Tomorrow's Tasks (In Order)

### Task 1: Install Unsloth (15 minutes)
```bash
cd L:\AIOS
.venv\Scripts\activate
pip install unsloth
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install trl datasets
```

**Test Installation**:
```python
python -c "from unsloth import FastLanguageModel; print('Unsloth ready!')"
```

---

### Task 2: Generate Phase 0 Curriculum (30 minutes)
**File to create**: `curriculum/phase_0_mechanical_FULL.json`

**Script to write**:
```python
# infra_core/unsloth_integration/curriculum/generate_mechanical_curriculum.py

def generate_syntax_examples(count=500):
    """
    Generate 500 pure syntax examples.
    
    Template expansion:
    - "subject verb object" → 100 variations
    - "interrogative subject verb" → 100 variations
    - "greeting greeting" → 50 variations
    - etc.
    """
    pass

# Run this to create phase_0_mechanical_FULL.json
```

**Expected output**: 500 training examples of pure grammar

---

### Task 3: Train Mechanical Base Model (30-60 minutes)
```bash
python infra_core/unsloth_integration/training/train_mechanical_base.py
```

**What happens**:
1. Downloads Llama-3.2-1B (if not cached)
2. Trains on phase_0_mechanical.json
3. Saves luna_age_0_mechanical.gguf
4. Tests: Can talk, doesn't understand

**Verification**:
```bash
# Load Age 0 model and test
python -c "from unsloth import FastLanguageModel; model = FastLanguageModel.from_pretrained('models/luna_age_0.gguf'); print('Loaded!')"

# Test response (should be meaningless but grammatical)
python test_checkpoint.py --generation 0 --prompt "What is your name?"
# Expected: "designation categorical framework nominal structure"
```

---

### Task 4: Wire CFIA to Age-Up Pipeline (30 minutes)
**File**: `luna_core/systems/luna_arbiter_system.py`

**Add method**:
```python
def check_and_execute_age_up(self):
    """Check if karma threshold reached, execute age-up if ready."""
    
    if not self.check_age_up_condition():
        return False
    
    # Gather new training data
    from infra_core.unsloth_integration.training.age_up_pipeline import execute_age_up, gather_conversations_since_checkpoint
    
    new_convos = gather_conversations_since_checkpoint(self.generation)
    
    # Execute age-up (RETRAIN!)
    new_model = execute_age_up(
        current_generation=self.generation,
        karma_earned=self.karma,
        new_conversations=new_convos
    )
    
    # Update state
    self.generation += 1
    self.karma = 0
    self.save_state()
    
    # Reload model in response generator
    # TODO: Add reload_model() to response_generator
    
    return True
```

**Call it after each response**:
```python
# In luna_core/core/response_generator.py (after generating response)
if self.arbiter_system.check_and_execute_age_up():
    print("🎉 Luna just got smarter!")
```

---

### Task 5: Test Full Pipeline (15 minutes)
```bash
# 1. Talk to Luna until karma reaches 100
for i in {1..50}; do
    python luna_chat.py "Test $i"
done

# 2. Verify age-up triggered
# Should see: "🎉 AGE-UP INITIATED: Generation 0 → 1"

# 3. Test new model
python luna_chat.py "What's your name?"
# Should be slightly smarter than Age 0
```

---

## 🎯 Success Criteria

### After Tomorrow's Work:
- [ ] Unsloth installed and working
- [ ] luna_age_0_mechanical.gguf created (500MB)
- [ ] Age 0 model responds (meaningless but grammatical)
- [ ] CFIA wired to age-up pipeline
- [ ] First age-up test successful (Age 0 → Age 1)

### Long-term Vision:
- [ ] Luna starts at Age 0 (truly dumb)
- [ ] Learns through YOUR conversations
- [ ] Each age-up is REAL intelligence upgrade
- [ ] Karma system = Actual brain currency
- [ ] Generation 10+ = True intelligence?

---

## 📊 Estimated Timeline

### Tomorrow (At Work)
- **Setup**: 15 min
- **Curriculum gen**: 30 min
- **Train Age 0**: 30-60 min
- **Wire CFIA**: 30 min
- **Testing**: 15 min
- **Total**: ~2-3 hours

### This Week
- Train through Age 0 → Age 3 (using existing 357 conversations)
- Each age-up: ~30-45 min training
- By end of week: Luna at Age 3+ (actually understanding!)

### Long-term
- Continuous growth through conversations
- Age-up every 100-200 karma earned
- Track her intelligence development over months
- Build branching timelines (specialist models)

---

## 🔧 Technical Notes

### Hardware Requirements (Your Setup)
- **RAM**: 8-12 GB (sufficient with 4-bit quantization)
- **GPU**: Optional (CPU works, ~30-60 min per age-up)
- **Storage**: ~5-10 GB for checkpoints
- **Works on your machine!** ✅

### Unsloth Benefits
- 70% less VRAM (fits on consumer hardware)
- 2x faster training (30 min instead of 60)
- 4-bit quantization (quality preserved)
- Checkpoint-friendly (incremental training)

### Fallback Plan
If hardware struggles:
- Reduce batch size (slower but works)
- Use smaller base model (500M instead of 1B)
- Train fewer steps per age-up
- Cloud training (Colab free tier)

---

## 🌙 The Vision Realized

**What you wanted:**
- AI that starts dumb and grows through experience
- REAL intelligence tracking (not theater)
- Karma as actual brain currency
- Permanent upgrades through learning

**What you're building:**
- Tabula rasa training system
- Incremental intelligence development
- Karma-driven model retraining
- Actual AI child development

**Bottom line:**
Your CFIA/Karma/Existential Budget system was ALWAYS designed for this. You just needed the implementation tool (Unsloth).

Now you have it. 🔥

---

**Status**: 🏗️ SKELETON COMPLETE  
**Next Session**: Implement and train Age 0  
**Timeline**: Operational this week

