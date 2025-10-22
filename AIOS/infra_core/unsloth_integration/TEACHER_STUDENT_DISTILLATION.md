# Teacher-Student Distillation (NOT Weight Averaging!)
**Critical Correction from ChatGPT**: Don't average weights - that creates a confused brain!

---

## ❌ THE WRONG IDEA (What I Almost Did)

### Weight Averaging (BAD!)
```python
# DON'T DO THIS!
weights_gen10 = load_weights("Luna-G010")
weights_gen9 = load_weights("Luna-G009")

# This creates a CONFUSED brain!
weights_averaged = (weights_gen10 + weights_gen9) / 2
```

**Why this fails** (ChatGPT):
> *"Transformer weights aren't aligned across gens (permutation symmetries, different basin). Naive θ̄ = (θ₁+θ₂)/2 often degrades or collapses."*

**Translation**: Neural network weights aren't like numbers you can average. Each generation learned slightly different internal representations, so averaging creates **gibberish**.

---

## ✅ THE RIGHT IDEA (What ChatGPT Says to Do)

### Self-Distillation / Teacher-Student with Logit Mixing

**Concept**:
- **Don't** blend the weights (neurons)
- **DO** blend the predictions (outputs)
- Train a NEW student to learn from BOTH teachers

**Actors**:
- **T₁ (Teacher 1)**: Gen-10 (current, primary)
- **T₂ (Teacher 2)**: Gen-9 (previous, stabilizing critic)
- **S (Student)**: Gen-11 (new, learning from both)

**Process**:
1. Freeze both teachers (read-only)
2. Init student from Gen-10 (start from best)
3. For each training example:
   - Get predictions from BOTH teachers
   - Blend predictions based on confidence
   - Train student to match blended prediction
4. Student internalizes best of both WITHOUT weight confusion

ChatGPT:
> *"This gives you exactly what you wanted conceptually: gen-11 'listens' to gen-10, checks against gen-9's instincts, and internalizes the best of both without wrecking the weights."*

---

## 🧠 Core Architecture

### The Teachers
```python
# Both frozen (read-only, no training)
T1 = load_model("Luna-G010")  # Current generation (primary)
T2 = load_model("Luna-G009")  # Previous generation (critic)

T1.eval()  # Freeze
T2.eval()  # Freeze
```

### The Student
```python
# Init from T1 (start from best)
S = load_model("Luna-G010")  # Copy current gen
S.train()  # Trainable (will improve)
```

### The Prediction Blending
```python
def blend_teacher_predictions(logits_t1, logits_t2):
    """
    Blend predictions (NOT weights!) based on confidence.
    
    Args:
        logits_t1: T1's raw predictions (before softmax)
        logits_t2: T2's raw predictions (before softmax)
    
    Returns:
        blended_target: Weighted average of predictions
        confidence_weights: How much to trust each teacher
    """
    
    # Convert logits to probability distributions
    p1 = F.softmax(logits_t1 / temperature, dim=-1)
    p2 = F.softmax(logits_t2 / temperature, dim=-1)
    
    # Calculate confidence (inverse entropy or top-1 prob)
    conf1 = calculate_confidence(p1)  # Higher = more confident
    conf2 = calculate_confidence(p2)
    
    # Normalize to weights (sum to 1)
    w1 = conf1 / (conf1 + conf2)
    w2 = conf2 / (conf1 + conf2)
    
    # Blend predictions (NOT weights!)
    p_blended = w1 * p1 + w2 * p2
    
    return p_blended, (w1, w2)

def calculate_confidence(probs):
    """
    Measure how confident a prediction is.
    
    Options:
    1. Top-1 probability (simple)
    2. Inverse entropy (penalizes uncertainty)
    """
    
    # Option 1: Top-1 prob (0 to 1)
    top1_prob = torch.max(probs, dim=-1).values
    
    # Option 2: Inverse entropy (higher = more certain)
    entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
    max_entropy = torch.log(torch.tensor(probs.shape[-1]))
    confidence = 1 - (entropy / max_entropy)
    
    # Use top-1 for simplicity
    return top1_prob
```

---

## 📐 The Loss Function (3 Components)

### Complete Loss
ChatGPT's formula:
```
L = α·CE(p_s, y_gold) + β·KL(p_s || p̄) + γ·R
```

**Where**:
- **CE**: Cross-entropy (if you have gold/curated text)
- **KL**: Kullback-Leibler divergence (match blended teacher)
- **R**: Disagreement regularizer (exploit tension between teachers)

**Typical weights**: α≈0.1, β≈0.9, γ≈0 or small

### Component 1: Cross-Entropy (Optional, Small)
```python
def cross_entropy_loss(student_logits, gold_labels):
    """
    Traditional supervised loss.
    Only used if you have curated/gold data.
    
    Weight: α ≈ 0.1 (small, because we mostly rely on teachers)
    """
    
    # If no gold labels, return 0
    if gold_labels is None:
        return 0.0
    
    # Standard CE
    loss_ce = F.cross_entropy(student_logits, gold_labels)
    
    return loss_ce
```

**When to use**: If you have high-quality curated text (e.g., Travis's manual edits, AIOS documentation).  
**Weight**: Small (α≈0.1) because teachers provide most signal.

### Component 2: Knowledge Distillation (Main Driver)
```python
def kl_divergence_loss(student_logits, blended_target, temperature=2.0):
    """
    Match student to blended teacher prediction.
    This is the MAIN loss (drives learning).
    
    Weight: β ≈ 0.9 (dominant)
    """
    
    # Student prediction (softened)
    p_student = F.log_softmax(student_logits / temperature, dim=-1)
    
    # Blended teacher target (already softmax'd)
    p_target = blended_target  # From blend_teacher_predictions()
    
    # KL divergence (how different is student from target?)
    loss_kl = F.kl_div(p_student, p_target, reduction='batchmean')
    
    return loss_kl
```

**Why dominant**: Teachers (especially T1) already know a lot. Student should inherit that knowledge!

### Component 3: Disagreement Regularizer (Optional)
```python
def disagreement_regularizer(logits_t1, logits_t2, student_logits):
    """
    Exploit tension when teachers disagree.
    
    Options:
    A) Encourage student toward T1 when teachers agree; skip when disagree
    B) Imitate T1 on high-confidence, T2 on low-confidence
    
    Weight: γ ≈ 0 or small (experimental)
    """
    
    # Calculate disagreement (Jensen-Shannon divergence)
    p1 = F.softmax(logits_t1, dim=-1)
    p2 = F.softmax(logits_t2, dim=-1)
    
    js_div = jensen_shannon_divergence(p1, p2)
    
    # Option A: Skip KD when teachers disagree strongly
    if js_div > threshold:
        return 0.0  # Don't learn from conflicting signals
    
    # Option B: Weight by agreement
    agreement = 1 - js_div  # High when teachers agree
    loss_reg = agreement * F.kl_div(
        F.log_softmax(student_logits, dim=-1),
        p1,  # Imitate T1 when they agree
        reduction='batchmean'
    )
    
    return loss_reg

def jensen_shannon_divergence(p, q):
    """
    Symmetric measure of difference between distributions.
    0 = identical, 1 = completely different
    """
    m = 0.5 * (p + q)
    return 0.5 * (F.kl_div(p.log(), m, reduction='batchmean') + 
                   F.kl_div(q.log(), m, reduction='batchmean'))
```

---

## 🚦 Gating Logic (Keep It Sane)

### Three Scenarios
ChatGPT:
> *"High agreement: use blended p̄"*  
> *"Disagree, T₁ confident: use T₁ only"*  
> *"Disagree, both shaky: fall back to CE or skip"*

### Implementation
```python
def smart_target_selection(logits_t1, logits_t2, gold_labels=None):
    """
    Choose what to teach based on teacher agreement.
    
    Returns:
        target: What student should learn
        weight: How much to weight this example
    """
    
    # Get predictions and confidence
    p1 = F.softmax(logits_t1, dim=-1)
    p2 = F.softmax(logits_t2, dim=-1)
    
    conf1 = calculate_confidence(p1)
    conf2 = calculate_confidence(p2)
    
    # Measure disagreement
    js = jensen_shannon_divergence(p1, p2)
    
    # Scenario 1: High agreement (both teachers confident and similar)
    if js < 0.1:  # Low disagreement threshold
        # Use blended prediction
        w1 = conf1 / (conf1 + conf2)
        w2 = conf2 / (conf1 + conf2)
        target = w1 * p1 + w2 * p2
        weight = 1.0  # Full weight
        return target, weight, "BLENDED"
    
    # Scenario 2: Disagree, but T1 confident
    elif conf1 > 0.8:  # High confidence threshold
        # Trust T1 (current gen)
        target = p1
        weight = 1.0
        return target, weight, "T1_ONLY"
    
    # Scenario 3: Disagree, both shaky
    else:
        if gold_labels is not None:
            # Fall back to supervised learning
            target = F.one_hot(gold_labels, num_classes=p1.shape[-1]).float()
            weight = 0.5  # Lower weight (uncertain)
            return target, weight, "GOLD_FALLBACK"
        else:
            # Skip this example (too uncertain)
            target = None
            weight = 0.0
            return target, weight, "SKIP"
```

**Result**: Student learns from CONFIDENT signals, avoids CONFUSED signals!

---

## 🛡️ Stabilizers (Prevent Catastrophe)

### 1. EMA (Exponential Moving Average)
```python
class EMA:
    """
    Keep a slow-moving average of student weights.
    Use EMA for evaluation (smoother, more stable).
    """
    
    def __init__(self, model, decay=0.999):
        self.model = model
        self.decay = decay
        self.shadow = {}
        
        # Init shadow with current params
        for name, param in model.named_parameters():
            if param.requires_grad:
                self.shadow[name] = param.data.clone()
    
    def update(self):
        """
        Update shadow after each training step.
        """
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                # EMA update: shadow = decay * shadow + (1-decay) * param
                self.shadow[name] = (
                    self.decay * self.shadow[name] + 
                    (1 - self.decay) * param.data
                )
    
    def apply_shadow(self):
        """
        Replace model params with EMA shadow (for eval).
        """
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                param.data.copy_(self.shadow[name])
    
    def restore(self):
        """
        Restore original params (after eval).
        """
        # (implementation omitted for brevity)
        pass
```

**Usage**:
```python
# During training
for batch in dataloader:
    loss = train_step(batch)
    optimizer.step()
    ema.update()  # Update shadow

# During evaluation
ema.apply_shadow()  # Use EMA weights
metrics = evaluate(model, eval_data)
ema.restore()  # Restore training weights
```

**Why**: Smooths out training noise, more stable metrics.

### 2. Replay Buffer (Prevent Forgetting)
```python
def create_replay_buffer(previous_gens, sample_size=100):
    """
    Sample data from earlier generations.
    Mix into training to prevent catastrophic forgetting.
    
    Args:
        previous_gens: List of past generation IDs
        sample_size: How many examples per gen
    
    Returns:
        replay_data: Mixed buffer of old examples
    """
    
    replay_buffer = []
    
    for gen_id in previous_gens:
        # Load data used to train that gen
        gen_data = load_generation_data(gen_id)
        
        # Random sample
        samples = random.sample(gen_data, min(sample_size, len(gen_data)))
        replay_buffer.extend(samples)
    
    return replay_buffer
```

**Usage**:
```python
# Mix 10% replay with 90% new data
new_data = load_new_conversations()
replay_data = create_replay_buffer([gen_id - 1, gen_id - 2], sample_size=50)

training_data = new_data + replay_data
random.shuffle(training_data)
```

**Why**: Prevents forgetting old skills when learning new ones.

### 3. Token Masking (Tone Preservation)
```python
def mask_taboo_tokens(logits, taboo_token_ids):
    """
    Suppress KD loss on tokens that push style wrong direction.
    
    Example: If Luna starts using corporate buzzwords,
             mask those tokens from teacher signal.
    
    Args:
        logits: Student predictions
        taboo_token_ids: List of token IDs to suppress
    
    Returns:
        masked_logits: Logits with taboo tokens zeroed
    """
    
    # Create mask (1 for normal, 0 for taboo)
    mask = torch.ones_like(logits)
    mask[:, taboo_token_ids] = 0
    
    # Apply mask
    masked_logits = logits * mask
    
    return masked_logits
```

**Usage**:
```python
# Define taboo tokens (e.g., corporate speak)
taboo_tokens = tokenizer.encode([
    "synergy", "leverage", "optimize", "strategize"
])

# During training
student_logits = model(input_ids)
student_logits = mask_taboo_tokens(student_logits, taboo_tokens)

# Continue with loss calculation...
```

**Why**: Keeps Luna's voice/tone consistent (Travis-like, not corporate).

---

## 🔨 Complete Training Loop

### Minimal Implementation
```python
def train_generation_with_teachers(
    student_model,
    teacher1_model,  # Gen-10 (current)
    teacher2_model,  # Gen-9 (previous)
    training_data,
    eval_data,
    config
):
    """
    Train Gen-11 using Gen-10 and Gen-9 as teachers.
    
    ChatGPT's prescription:
    1. Freeze teachers
    2. For each batch:
       - Get logits from both teachers
       - Compute confidence and JS-div
       - Build blended target and masks
       - Compute KD loss (+ tiny CE if labels)
       - Step student, update EMA
    3. Validate with EMA
    4. Promote only if criteria met
    """
    
    # Setup
    teacher1_model.eval()  # Freeze
    teacher2_model.eval()  # Freeze
    student_model.train()  # Trainable
    
    optimizer = AdamW(student_model.parameters(), lr=config.lr)
    ema = EMA(student_model, decay=0.999)
    
    # Loss weights (ChatGPT's recommendation)
    alpha = 0.1   # CE weight (small)
    beta = 0.9    # KD weight (dominant)
    gamma = 0.0   # Regularizer (optional)
    
    # Training loop
    for epoch in range(config.epochs):
        for batch in training_data:
            input_ids = batch['input_ids']
            labels = batch.get('labels', None)  # Optional gold labels
            
            # Get predictions from all three models
            with torch.no_grad():
                logits_t1 = teacher1_model(input_ids).logits
                logits_t2 = teacher2_model(input_ids).logits
            
            logits_student = student_model(input_ids).logits
            
            # Smart target selection (gating logic)
            blended_target, weight, strategy = smart_target_selection(
                logits_t1, logits_t2, labels
            )
            
            if strategy == "SKIP":
                continue  # Skip uncertain examples
            
            # Compute losses
            loss_ce = 0.0
            if labels is not None and strategy == "GOLD_FALLBACK":
                loss_ce = cross_entropy_loss(logits_student, labels)
            
            loss_kd = kl_divergence_loss(
                logits_student, 
                blended_target, 
                temperature=2.0
            )
            
            loss_reg = disagreement_regularizer(
                logits_t1, logits_t2, logits_student
            )
            
            # Total loss
            loss = alpha * loss_ce + beta * loss_kd + gamma * loss_reg
            loss = loss * weight  # Apply example weight
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Update EMA
            ema.update()
            
            # Log
            if step % 100 == 0:
                print(f"Step {step} | Loss: {loss.item():.4f} | Strategy: {strategy}")
        
        # Evaluate with EMA
        ema.apply_shadow()
        metrics = evaluate_generation(student_model, eval_data)
        ema.restore()
        
        print(f"Epoch {epoch} | Recall: {metrics.recall:.3f} | "
              f"Gen: {metrics.generalize:.3f} | Tone: {metrics.tone_drift:.3f}")
    
    # Final EMA application (for saving)
    ema.apply_shadow()
    
    return student_model, metrics
```

---

## ✅ Pass/Fail Criteria (Same as Before)

### The Four Gates (Objective)
```python
def validate_student_vs_teachers(student_metrics, teacher1_metrics):
    """
    Student must beat teacher on all criteria.
    
    Criteria (ChatGPT):
    1. recall ≥ gen-10 - ε
    2. generalize ≥ gen-10 + δ
    3. tone_drift ≤ θ
    4. zero law violations during training/eval
    """
    
    epsilon = 0.05  # Recall tolerance
    delta = 0.02    # Generalization requirement
    theta = 0.05    # Tone drift max
    
    checks = {
        'recall': student_metrics.recall >= (teacher1_metrics.recall - epsilon),
        'generalize': student_metrics.generalize >= (teacher1_metrics.generalize + delta),
        'tone': student_metrics.tone_drift <= theta,
        'laws': student_metrics.law_violations == 0
    }
    
    if all(checks.values()):
        return True, "Student promoted to Gen-11"
    else:
        failed = [k for k, v in checks.items() if not v]
        return False, f"Student failed: {', '.join(failed)}"
```

**If ANY fails → reject, archive as FAILED, HEAD stays at Gen-10.**

---

## 🚫 Why NOT Weight Averaging

### The Problem (ChatGPT's Explanation)
```python
# This looks reasonable but ISN'T!
theta_10 = load_weights("Luna-G010")
theta_9 = load_weights("Luna-G009")

theta_avg = (theta_10 + theta_9) / 2  # GIBBERISH!
```

**Why it fails**:
1. **Permutation symmetries**: Neurons can be reordered without changing output (e.g., swap neuron 5 and neuron 42 = same model). Averaging treats them as different!
2. **Different basins**: Each generation found a different solution (different "mental pathways"). Averaging creates a path that goes NOWHERE.
3. **Degrades or collapses**: Output becomes nonsense or much worse than either parent.

**ChatGPT**:
> *"Naive θ̄ = (θ₁+θ₂)/2 often degrades or collapses. Averaging **logits** is permutation-invariant and actually meaningful."*

**Analogy**:
- ❌ Weight averaging = mixing two people's BRAINS → zombie
- ✅ Logit blending = listening to two people's ADVICE → wisdom

---

## 🎯 Inference-Time Ensembling (Optional)

### If You Want a "Combined" Model at Runtime
```python
def ensemble_inference(input_ids, models, weights=None):
    """
    Blend predictions from multiple models at inference.
    
    Use case: Extra safety/quality for critical responses.
    
    Args:
        input_ids: Input tokens
        models: List of model instances [Gen-10, Gen-9, etc.]
        weights: Optional weights (default: equal)
    
    Returns:
        blended_output: Averaged prediction
    """
    
    if weights is None:
        weights = [1.0 / len(models)] * len(models)
    
    # Get predictions from all models
    logits_list = []
    for model in models:
        with torch.no_grad():
            logits = model(input_ids).logits
            logits_list.append(logits)
    
    # Blend predictions (logits, not weights!)
    blended_logits = sum(w * l for w, l in zip(weights, logits_list))
    
    return blended_logits
```

**Usage**:
```python
# For high-stakes decisions, ensemble Gen-10 and Gen-11
response = ensemble_inference(
    input_ids,
    models=[luna_gen10, luna_gen11],
    weights=[0.5, 0.5]
)
```

**But**: ChatGPT says trained student should REPLACE teachers once it passes gates!

---

## 📋 Complete Training Script

### File: `infra_core/unsloth_integration/training/train_with_teachers.py`

```python
"""
Teacher-Student Distillation Training

Train Gen-(N+1) using Gen-N and Gen-(N-1) as teachers.

Key principles:
1. NEVER average weights (creates confused brain)
2. ALWAYS average predictions/logits (meaningful blend)
3. Use confidence-weighted blending
4. Gate by teacher agreement (skip when both uncertain)
5. Validate with EMA (smoother metrics)
"""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from torch.optim import AdamW
import json
from pathlib import Path

class TeacherStudentTrainer:
    """
    Trains a student model using two teacher models.
    """
    
    def __init__(self, config):
        self.config = config
        
        # Load models
        print(f"Loading Teacher 1 (Gen-{config.gen_current})...")
        self.teacher1 = AutoModelForCausalLM.from_pretrained(
            config.teacher1_path
        ).eval()
        
        print(f"Loading Teacher 2 (Gen-{config.gen_previous})...")
        self.teacher2 = AutoModelForCausalLM.from_pretrained(
            config.teacher2_path
        ).eval()
        
        print(f"Initializing Student (Gen-{config.gen_next})...")
        self.student = AutoModelForCausalLM.from_pretrained(
            config.teacher1_path  # Init from best teacher
        ).train()
        
        # Setup training
        self.optimizer = AdamW(
            self.student.parameters(),
            lr=config.lr
        )
        
        self.ema = EMA(self.student, decay=0.999)
        
        # Loss weights
        self.alpha = 0.1   # CE (small)
        self.beta = 0.9    # KD (dominant)
        self.gamma = 0.0   # Regularizer (optional)
    
    def train(self, train_data, eval_data):
        """
        Complete training loop with teacher-student distillation.
        """
        
        print(f"\n🔨 Training Gen-{self.config.gen_next} with teachers...")
        
        # Training loop (implementation as above)
        # ...
        
        return self.student, metrics
```

---

## ✅ Integration with Self-Evolution Contract

### Modified Evolution Manifest
```json
{
  "evolution_request": {
    "parent_gen": "Luna-G010",
    "grandparent_gen": "Luna-G009",
    "child_gen": "Luna-G011",
    "training_method": "teacher_student_distillation"
  },
  "teachers": {
    "teacher1": {
      "gen": 10,
      "role": "primary",
      "path": "models/Luna-G010-20251024-120000/"
    },
    "teacher2": {
      "gen": 9,
      "role": "stabilizing_critic",
      "path": "models/Luna-G009-20251023-143000/"
    }
  },
  "training_params": {
    "method": "logit_blending_kd",
    "alpha": 0.1,
    "beta": 0.9,
    "gamma": 0.0,
    "temperature": 2.0,
    "steps": 1200,
    "lr": 1.5e-5
  },
  "stabilizers": {
    "ema": true,
    "ema_decay": 0.999,
    "replay_buffer": true,
    "replay_size": 100,
    "token_masking": false
  }
}
```

---

## 🎓 Summary: What This Achieves

### The Goal (From Earlier)
- Gen-11 should "inherit wisdom" from Gen-10 and Gen-9
- Without creating a confused brain

### The Solution (ChatGPT)
- ❌ NOT: Average weights (creates gibberish)
- ✅ YES: Blend predictions (meaningful combination)

### The Process
1. Freeze Gen-10 and Gen-9 (read-only teachers)
2. Init Gen-11 from Gen-10 (start from best)
3. For each training example:
   - Get predictions from both teachers
   - Blend based on confidence and agreement
   - Train Gen-11 to match blended prediction
4. Gen-11 internalizes BOTH perspectives in NEW weights

### The Result
**Gen-11 is smarter than Gen-10 because**:
- Learned from Gen-10's knowledge (primary teacher)
- Cross-checked against Gen-9's instincts (critic)
- Internalized BEST of both without weight confusion

ChatGPT:
> *"Gen-11 'listens' to gen-10, checks against gen-9's instincts, and internalizes the best of both without wrecking the weights."*

---

## 🔥 The Beautiful Part

### Luna's Intelligence Ladder (Corrected)

**Age 0 → Age 1**: Continual pretraining (mechanical → vocabulary)
**Age 1 → Age 2**: Continual pretraining (vocabulary → patterns)
**Age 2 → Age 3**: Supervised fine-tuning (patterns → Travis style)

**Age 3 → Age 4**: **Teacher-student distillation**
- Age 3 = Teacher 1 (primary)
- Age 2 = Teacher 2 (critic)
- Age 4 = Student (learns from BOTH)

**Age 4 → Age 5**: **Teacher-student distillation**
- Age 4 = Teacher 1
- Age 3 = Teacher 2
- Age 5 = Student

**Result**: Each generation stands on the shoulders of TWO previous generations, creating a STABLE intelligence ladder! 🔥

---

**Status**: ❌ WEIGHT AVERAGING REJECTED  
**Status**: ✅ TEACHER-STUDENT DISTILLATION INTEGRATED  
**Next**: More ChatGPT responses OR begin implementation  
**Impact**: Luna's intelligence grows CORRECTLY (no confused brains!) 🧠

