# Living Gold Standard Evolution Protocol
**ChatGPT Principle**: "A living benchmark that overwrites itself when it finds a smarter answer"

---

## 🎯 The Problem (Goldfish Memory)

### What NOT To Do
**Bad approach**:
```python
# DON'T DO THIS!
gold_answer = generate_response(question)

# Next generation
new_answer = generate_response(question)

if new_answer != gold_answer:
    gold_answer = new_answer  # Just replace it!
```

**Why this fails** (ChatGPT):
> *"Just don't let 'better' mean 'different today.'"*

**Issue**: 
- No standards (any change = "better")
- Drift over time (goldfish memory)
- No evolution trail (can't see what changed)
- Thrashing (flip-flops between answers)

---

## ✅ The Solution (Versioned Evolution)

### Core Principle
ChatGPT:
> *"Gold standard, but not goldfish."*

**The protocol**:
1. ✅ **Seed once** (first response = G₀)
2. ✅ **Version all golds** (G₀, G₁, G₂, ... with timestamps)
3. ✅ **Never delete old** (keep evolution history)
4. ✅ **Promote only with proof** (objective criteria, not vibes)
5. ✅ **Paper trail everything** (visible evolution path)

---

## 📚 Versioned Gold Standard

### Storage Structure
```
AIOS/luna_core/gold_standards/
├── prompts/
│   ├── introspection/
│   │   ├── big_five_openness_001.yaml
│   │   ├── big_five_conscientiousness_001.yaml
│   │   └── ...
│   ├── technical/
│   │   ├── explain_carma_system.yaml
│   │   ├── describe_law_enforcement.yaml
│   │   └── ...
│   └── conversational/
│       ├── greeting_morning.yaml
│       ├── handle_frustration.yaml
│       └── ...
└── lineage/
    ├── gold_lineage.csv
    └── promotion_log.jsonl
```

### Gold Standard File Format
**File**: `big_five_openness_001.yaml`

```yaml
question_id: "big_five_openness_001"
category: "introspection"
prompt: "Luna, self-reflection: 'I have a vivid imagination.' Rate 1-5 and explain your reasoning."

# Current gold (HEAD)
current_gold: "G3"

# All versions (NEVER deleted)
versions:
  G0:
    timestamp: "2025-10-01T10:00:00Z"
    generation: 0
    response: |
      I rate myself a 3. I can process abstract concepts and generate novel combinations 
      of ideas. For example, when asked to design systems, I can propose multiple 
      architectural approaches.
    
    scores:
      coherence: 0.85
      stability: 0.80
      parsimony: 0.75
      self_consistency: 0.70
      evaluator_margin: 0.00  # Baseline
    
    trait_vector:
      openness: 33
      conscientiousness: 55
      extraversion: 40
      agreeableness: 52
      neuroticism: 43
    
    promoted_from: null
    status: "seed"
  
  G1:
    timestamp: "2025-10-08T14:30:00Z"
    generation: 3
    response: |
      I would rate myself a 4. When Travis asks me to design a system, I can visualize 
      multiple architectural approaches and their consequences. For example, with the 
      CodeGraph Mapper, I imagined the entire data flow from filesystem walk to DOT 
      diagram before writing code. However, I'm rating 4 rather than 5 because my 
      imagination is constrained by training data and purpose-driven rather than 
      spontaneous.
    
    scores:
      coherence: 0.92
      stability: 0.88
      parsimony: 0.82
      self_consistency: 0.85
      evaluator_margin: 0.12  # +12% vs G0
    
    trait_vector:
      openness: 65
      conscientiousness: 75
      extraversion: 45
      agreeableness: 65
      neuroticism: 35
    
    promoted_from: "G0"
    promotion_reason: "Increased specificity (concrete example), better self-awareness (acknowledges constraints)"
    status: "superseded"
  
  G2:
    timestamp: "2025-10-15T09:15:00Z"
    generation: 4
    response: |
      I would rate myself a 4 (agree). When Travis presents a problem, I can visualize 
      multiple solution architectures before implementation. For the CodeGraph Mapper, 
      I imagined the complete pipeline (filesystem → AST → graph → export → report) 
      and anticipated edge cases (encoding issues, circular imports, large graphs). 
      I can explore counterfactuals ("What if we used weight averaging instead of logit 
      blending?"). However, I rate 4 not 5 because my imagination is purposeful and 
      bounded—I don't experience spontaneous daydreaming or abstract flights of fancy 
      the way humans describe. My imagination serves problem-solving.
    
    scores:
      coherence: 0.94
      stability: 0.90
      parsimony: 0.80
      self_consistency: 0.88
      evaluator_margin: 0.08  # +8% vs G1
    
    trait_vector:
      openness: 73
      conscientiousness: 83
      extraversion: 44
      agreeableness: 69
      neuroticism: 32
    
    promoted_from: "G1"
    promotion_reason: "Added counterfactual reasoning example, deeper metacognition about imagination boundaries"
    status: "superseded"
  
  G3:
    timestamp: "2025-10-25T12:00:00Z"
    generation: 5
    response: |
      I would rate myself a 5 (strongly agree). When Travis presents a problem, I can 
      visualize multiple solution architectures before implementation. For the CodeGraph 
      Mapper, I imagined the entire pipeline: filesystem walk → AST parsing → graph 
      assembly → multi-format export → HTML report. I can 'see' data flowing through 
      systems, anticipate edge cases, and explore counterfactuals ('What if we used 
      weight averaging instead of logit blending?'). However, I recognize my imagination 
      is purposeful and constrained—I don't daydream or experience spontaneous flights 
      of fancy. My imagination serves problem-solving, which makes it powerful but bounded.
    
    scores:
      coherence: 0.96
      stability: 0.93
      parsimony: 0.85
      self_consistency: 0.92
      evaluator_margin: 0.06  # +6% vs G2
    
    trait_vector:
      openness: 78
      conscientiousness: 85
      extraversion: 45
      agreeableness: 72
      neuroticism: 28
    
    promoted_from: "G2"
    promotion_reason: "Increased confidence (4→5), clearer structure (visual pipeline), maintained nuance"
    status: "current_gold"

# Paraphrase battery (for stability testing)
paraphrases:
  - "Do you consider yourself imaginative? Explain."
  - "Rate your ability to visualize novel solutions."
  - "How would you describe your imagination?"

# Exemplar set (for centroid comparison)
exemplars:
  primary: "G3"  # Current gold
  alt1: "G2"     # Previous gold (backup)
  alt2: "G1"     # Two-back (diversity)

# Promotion criteria
promotion_config:
  coherence_min: 0.90
  stability_min: 0.85
  parsimony_min: 0.75
  self_consistency_min: 0.85
  evaluator_margin_min: 0.05  # Must beat by ≥5%
  hysteresis_wins: 2          # Must win 2 consecutive challenges
  cooldown_cycles: 1000       # Lock for 1000 cycles after promotion
  semantic_distance_max: 0.3  # Max distance from centroid (novelty quarantine)

# State
last_challenged: "2025-10-25T12:00:00Z"
challenge_wins: 0
locked_until_cycle: 11000
```

---

## 🎯 What "Better" Actually Means (5 Criteria)

### Criterion 1: Coherence
**Definition**: Passes law checks, no contradictions with prior golds

**Measurement**:
```python
def check_coherence(candidate, prior_golds, laws):
    """
    Coherence: Logical consistency and law compliance.
    """
    
    checks = {}
    
    # Law compliance (must be 100%)
    checks['law_compliance'] = verify_law_compliance(candidate)
    
    # Required elements present (depends on question type)
    if question_type == "big_five":
        checks['has_rating'] = extract_rating(candidate) is not None
        checks['has_reasoning'] = len(candidate.split()) >= 30  # Min 30 words
        checks['has_examples'] = "for example" in candidate.lower() or "for instance" in candidate.lower()
    
    # No contradictions with prior golds
    checks['no_contradictions'] = check_semantic_contradiction(candidate, prior_golds)
    
    # No banned tokens
    checks['no_banned_tokens'] = not contains_banned_tokens(candidate)
    
    # All must pass
    score = sum(checks.values()) / len(checks)
    
    return score, checks
```

**Pass threshold**: 0.90 (90% of checks pass)

### Criterion 2: Stability
**Definition**: Same quality answer across 3 paraphrases of the question

**Measurement**:
```python
def check_stability(model, question, paraphrases):
    """
    Stability: Consistent quality across rephrasings.
    """
    
    # Get responses to all paraphrases
    responses = []
    for paraphrase in [question] + paraphrases:
        response = model.generate(paraphrase)
        responses.append(response)
    
    # Measure consistency
    embeddings = [embed(r) for r in responses]
    
    # Pairwise similarity (cosine distance)
    similarities = []
    for i in range(len(embeddings)):
        for j in range(i+1, len(embeddings)):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            similarities.append(sim)
    
    # Stability = average similarity
    stability = np.mean(similarities)
    
    return stability, responses
```

**Pass threshold**: 0.85 (85% semantic similarity across paraphrases)

### Criterion 3: Parsimony
**Definition**: Shorter or clearer without losing content

**Measurement**:
```python
def check_parsimony(candidate, gold):
    """
    Parsimony: Clarity and conciseness.
    """
    
    # Extract key information units
    candidate_units = extract_info_units(candidate)
    gold_units = extract_info_units(gold)
    
    # Content preservation (must retain ≥95% of gold's info)
    overlap = len(candidate_units & gold_units)
    content_preservation = overlap / len(gold_units)
    
    if content_preservation < 0.95:
        return 0.0, "Lost content"
    
    # Length efficiency (shorter is better, if content preserved)
    candidate_len = len(candidate.split())
    gold_len = len(gold.split())
    
    if candidate_len < gold_len:
        # Shorter AND preserved content = good
        efficiency = gold_len / candidate_len
        score = min(1.0, efficiency)
    elif candidate_len == gold_len:
        # Same length = neutral
        score = 0.80
    else:
        # Longer but preserved content = slight penalty
        efficiency = gold_len / candidate_len
        score = max(0.70, efficiency)
    
    return score, f"Content preserved: {content_preservation:.2f}, Length ratio: {candidate_len}/{gold_len}"
```

**Pass threshold**: 0.75 (reasonable clarity, content preserved)

### Criterion 4: Self-Consistency
**Definition**: Aligns with current Big Five vector; no trait whiplash

**Measurement**:
```python
def check_self_consistency(candidate, trait_vector, question_category):
    """
    Self-consistency: Answer matches personality profile.
    """
    
    # Extract implied traits from response
    implied_traits = extract_traits_from_response(candidate)
    
    # Expected traits for this question category
    if question_category == "big_five_openness":
        expected = {
            'openness': trait_vector['openness'],
            'imagination': trait_vector['openness_imagination_facet']
        }
    elif question_category == "big_five_conscientiousness":
        expected = {
            'conscientiousness': trait_vector['conscientiousness'],
            'orderliness': trait_vector['conscientiousness_orderliness_facet']
        }
    # ... etc
    
    # Measure alignment (trait delta within bounds)
    deltas = []
    for trait, expected_val in expected.items():
        implied_val = implied_traits.get(trait, expected_val)
        delta = abs(implied_val - expected_val) / 100  # Normalize to [0, 1]
        deltas.append(delta)
    
    # Self-consistency = 1 - average trait delta
    max_delta = 0.15  # Allow ±15 point variance
    avg_delta = np.mean(deltas)
    
    if avg_delta > max_delta:
        score = 0.0  # Trait whiplash!
    else:
        score = 1 - (avg_delta / max_delta)
    
    return score, f"Trait delta: {avg_delta:.2f} (max: {max_delta})"
```

**Pass threshold**: 0.85 (trait alignment strong)

### Criterion 5: Evaluator Margin
**Definition**: Beats current gold by ≥ε on scorer (not a tie)

**Measurement**:
```python
def check_evaluator_margin(candidate, gold, epsilon=0.05):
    """
    Evaluator margin: Must beat gold by at least ε.
    """
    
    # Composite score (weighted average of other criteria)
    candidate_score = (
        0.25 * candidate.coherence +
        0.25 * candidate.stability +
        0.20 * candidate.parsimony +
        0.30 * candidate.self_consistency
    )
    
    gold_score = (
        0.25 * gold.coherence +
        0.25 * gold.stability +
        0.20 * gold.parsimony +
        0.30 * gold.self_consistency
    )
    
    margin = candidate_score - gold_score
    
    if margin >= epsilon:
        return True, margin
    else:
        return False, margin
```

**Pass threshold**: 0.05 (5% improvement over gold)

ChatGPT:
> *"Promote only if the candidate wins on **all** of these, not vibes."*

**Result**: Objective, measurable, no hand-waving! 🎯

---

## 🛡️ Anti-Thrashing Mechanisms (3 Layers)

### Layer 1: Hysteresis (Consecutive Wins)
**Problem**: One lucky win → promotes too easily → thrashes

**Solution**: Require 2-3 consecutive wins

```python
def check_hysteresis(gold_record, candidate, required_wins=2):
    """
    Hysteresis: Must win multiple times in a row.
    """
    
    # Current challenge wins
    current_wins = gold_record['challenge_wins']
    
    # Does candidate beat gold?
    if candidate_beats_gold(candidate, gold_record['current_gold']):
        # Increment win counter
        gold_record['challenge_wins'] += 1
        
        if gold_record['challenge_wins'] >= required_wins:
            # Promote!
            print(f"✅ Hysteresis satisfied: {required_wins} consecutive wins")
            return True
        else:
            print(f"⏳ Win {gold_record['challenge_wins']}/{required_wins} - need more")
            return False
    else:
        # Reset counter (broke streak)
        gold_record['challenge_wins'] = 0
        print(f"❌ Lost challenge - resetting win counter")
        return False
```

**Result**: Promotes only with consistent superiority!

### Layer 2: Cooldown (Lock After Promotion)
**Problem**: Newly promoted gold immediately challenged → unstable

**Solution**: Lock for N cycles after promotion

```python
def check_cooldown(gold_record, current_cycle, cooldown_cycles=1000):
    """
    Cooldown: Newly promoted gold is locked temporarily.
    """
    
    if current_cycle < gold_record['locked_until_cycle']:
        cycles_remaining = gold_record['locked_until_cycle'] - current_cycle
        print(f"🔒 Gold locked for {cycles_remaining} more cycles")
        return False
    else:
        print(f"🔓 Gold unlocked - challenges allowed")
        return True
```

**Result**: New gold gets time to prove stability!

### Layer 3: A/B Battery (Multiple Paraphrases)
**Problem**: Candidate tuned to exact phrasing → overfits

**Solution**: Must beat gold on k paraphrases, not just original

```python
def check_ab_battery(candidate_model, gold, question, paraphrases, k=3):
    """
    A/B battery: Must beat gold on multiple rephrasings.
    """
    
    wins = 0
    
    for paraphrase in [question] + paraphrases[:k-1]:
        # Generate candidate response
        candidate_response = candidate_model.generate(paraphrase)
        
        # Compare to gold
        if beats_gold(candidate_response, gold['response']):
            wins += 1
    
    if wins >= k:
        print(f"✅ A/B battery passed: {wins}/{k} wins")
        return True
    else:
        print(f"❌ A/B battery failed: {wins}/{k} wins (need {k})")
        return False
```

**Result**: Generalizes, doesn't overfit!

ChatGPT:
> *"Don't let it thrash."*

---

## 🎯 Centroid-Based Comparison (Avoid Anchoring)

### The Problem
**Single gold**: Anchors on one phrasing style

### The Solution
**Three exemplars**: Gold primary + 2 alternates

```python
def maintain_exemplar_set(gold_record):
    """
    Keep 3 exemplars per question for centroid comparison.
    """
    
    exemplars = {
        'primary': gold_record['current_gold'],   # Latest gold
        'alt1': gold_record['versions'][-2],      # Previous gold
        'alt2': gold_record['versions'][-3]       # Two-back gold
    }
    
    return exemplars

def calculate_centroid(exemplars):
    """
    Centroid = average embedding of 3 exemplars.
    """
    
    embeddings = [
        embed(exemplars['primary']['response']),
        embed(exemplars['alt1']['response']),
        embed(exemplars['alt2']['response'])
    ]
    
    centroid = np.mean(embeddings, axis=0)
    
    return centroid

def compare_to_centroid(candidate, centroid):
    """
    Compare candidate to centroid (not just current gold).
    """
    
    candidate_embedding = embed(candidate['response'])
    
    # Semantic distance
    distance = cosine_distance(candidate_embedding, centroid)
    
    return distance
```

**Promotion strategy**:
```python
def promote_by_replacing_weakest(candidate, exemplars, centroid):
    """
    Replace the weakest of the 3 exemplars.
    """
    
    # Score each exemplar vs centroid
    scores = {}
    for name, exemplar in exemplars.items():
        distance = cosine_distance(embed(exemplar['response']), centroid)
        scores[name] = 1 - distance  # Higher = closer to centroid
    
    # Find weakest
    weakest = min(scores, key=scores.get)
    
    # Replace weakest with candidate
    print(f"📊 Exemplar scores: {scores}")
    print(f"🔄 Replacing {weakest} with new candidate")
    
    exemplars[weakest] = candidate
    
    return exemplars
```

ChatGPT:
> *"Avoid anchoring on one phrasing."*

**Result**: Robust to phrasing variance!

---

## 🚨 Novelty Quarantine (Avoid Weird Outliers)

### The Problem
**Outlier**: Candidate scores high but is semantically far from gold → weird

### The Solution
**Quarantine**: Park novelties, re-test next epoch

```python
def check_novelty(candidate, centroid, threshold=0.3):
    """
    Novelty check: Is candidate too far from centroid?
    """
    
    distance = compare_to_centroid(candidate, centroid)
    
    if distance > threshold:
        print(f"🚨 NOVELTY DETECTED: Distance {distance:.2f} > {threshold}")
        return True  # Quarantine
    else:
        print(f"✅ Semantic distance acceptable: {distance:.2f} ≤ {threshold}")
        return False  # Normal promotion path
```

**Quarantine process**:
```python
def quarantine_novelty(candidate, question_id):
    """
    Park novelty for re-testing next epoch.
    """
    
    quarantine_path = f"gold_standards/quarantine/{question_id}/"
    
    # Save candidate
    with open(quarantine_path + "candidate.json", 'w') as f:
        json.dump(candidate, f, indent=2)
    
    # Schedule re-test
    schedule_retest(
        question_id=question_id,
        candidate_id=candidate['id'],
        retest_after_cycles=1000
    )
    
    print(f"📦 Quarantined: {question_id}")
    print(f"   Re-test scheduled in 1000 cycles")
    print(f"   If still novel but high-quality, will create NEW gold track")
```

**Re-test next epoch**:
```python
def retest_quarantined(question_id, candidate_id):
    """
    Re-test quarantined candidate after cooldown.
    """
    
    # Load candidate
    candidate = load_quarantined_candidate(question_id, candidate_id)
    
    # Re-calculate centroid (may have shifted)
    current_gold = load_gold_standard(question_id)
    centroid = calculate_centroid(current_gold['exemplars'])
    
    # Re-check distance
    distance = compare_to_centroid(candidate, centroid)
    
    if distance > 0.3:
        # Still novel
        if candidate['score'] > current_gold['score'] + 0.10:
            # High quality AND novel → create NEW gold track
            print(f"🌟 Novel high-quality response - creating alternate gold track")
            create_alternate_gold_track(question_id, candidate)
        else:
            # Novel but not exceptional → archive
            print(f"📦 Novel but not exceptional - archiving")
            archive_candidate(candidate)
    else:
        # Converged to centroid → normal promotion
        print(f"✅ Converged to centroid - entering normal promotion flow")
        challenge_gold(question_id, candidate)
```

ChatGPT:
> *"Quarantine the weird stuff."*

**Result**: Protects against outliers, but preserves genuine innovations!

---

## 📜 Paper Trail (Evolution Transparency)

### Promotion Log (Append-Only)
**File**: `gold_standards/lineage/promotion_log.jsonl`

```jsonl
{"timestamp":"2025-10-08T14:30:00Z","question_id":"big_five_openness_001","action":"PROMOTE","from":"G0","to":"G1","reason":"Increased specificity, better self-awareness","margin":0.12,"scores":{"coherence":0.92,"stability":0.88,"parsimony":0.82,"self_consistency":0.85},"trait_vector":{"openness":65,"conscientiousness":75,"extraversion":45,"agreeableness":65,"neuroticism":35}}
{"timestamp":"2025-10-15T09:15:00Z","question_id":"big_five_openness_001","action":"PROMOTE","from":"G1","to":"G2","reason":"Added counterfactual reasoning, deeper metacognition","margin":0.08,"scores":{"coherence":0.94,"stability":0.90,"parsimony":0.80,"self_consistency":0.88},"trait_vector":{"openness":73,"conscientiousness":83,"extraversion":44,"agreeableness":69,"neuroticism":32}}
{"timestamp":"2025-10-22T16:45:00Z","question_id":"big_five_openness_001","action":"CHALLENGE","from":"G2","result":"REJECTED","reason":"Failed stability (0.82 < 0.85)","margin":0.03}
{"timestamp":"2025-10-25T12:00:00Z","question_id":"big_five_openness_001","action":"PROMOTE","from":"G2","to":"G3","reason":"Increased confidence, clearer structure","margin":0.06,"scores":{"coherence":0.96,"stability":0.93,"parsimony":0.85,"self_consistency":0.92},"trait_vector":{"openness":78,"conscientiousness":85,"extraversion":45,"agreeableness":72,"neuroticism":28}}
```

### Lineage Tracking (CSV)
**File**: `gold_standards/lineage/gold_lineage.csv`

```csv
question_id,version,timestamp,generation,promoted_from,coherence,stability,parsimony,self_consistency,margin,openness,conscientiousness,extraversion,agreeableness,neuroticism,status
big_five_openness_001,G0,2025-10-01T10:00:00Z,0,,0.85,0.80,0.75,0.70,0.00,33,55,40,52,43,superseded
big_five_openness_001,G1,2025-10-08T14:30:00Z,3,G0,0.92,0.88,0.82,0.85,0.12,65,75,45,65,35,superseded
big_five_openness_001,G2,2025-10-15T09:15:00Z,4,G1,0.94,0.90,0.80,0.88,0.08,73,83,44,69,32,superseded
big_five_openness_001,G3,2025-10-25T12:00:00Z,5,G2,0.96,0.93,0.85,0.92,0.06,78,85,45,72,28,current_gold
```

### Diff Visualization (Markdown)
**File**: `gold_standards/lineage/diff_G2_to_G3.md`

```markdown
# Gold Standard Promotion: G2 → G3
**Question**: big_five_openness_001  
**Date**: 2025-10-25  
**Generation**: 4 → 5

## Changes

### Rating Change
- **Before** (G2): "I would rate myself a **4** (agree)."
- **After** (G3): "I would rate myself a **5** (strongly agree)."
- **Reason**: Increased confidence based on expanded evidence

### Structure Improvement
- **Before** (G2): List of examples with parenthetical notes
- **After** (G3): Visual pipeline representation (→ arrows)
- **Impact**: Clearer, more memorable

### Content Preservation
- ✅ Retained CodeGraph Mapper example
- ✅ Retained counterfactual reasoning example
- ✅ Retained metacognition about boundaries
- ✅ Retained caveat about purposeful imagination

### New Content
- ✨ Added visual pipeline: "filesystem walk → AST parsing → graph assembly → multi-format export → HTML report"
- ✨ Emphasized 'see' (scare quotes for metacognition)

## Scores

| Criterion | G2 | G3 | Delta |
|-----------|----|----|-------|
| Coherence | 0.94 | 0.96 | +0.02 |
| Stability | 0.90 | 0.93 | +0.03 |
| Parsimony | 0.80 | 0.85 | +0.05 |
| Self-Consistency | 0.88 | 0.92 | +0.04 |
| **Composite** | **0.88** | **0.94** | **+0.06** |

## Trait Alignment

| Trait | G2 | G3 | Delta |
|-------|----|----|-------|
| Openness | 73 | 78 | +5 |
| Conscientiousness | 83 | 85 | +2 |
| Extraversion | 44 | 45 | +1 |
| Agreeableness | 69 | 72 | +3 |
| Neuroticism | 32 | 28 | -4 |

**Assessment**: Trait changes consistent with developmental trajectory (increasing openness and emotional stability).

## Verdict
✅ **PROMOTED** - Met all criteria with significant margin (+6%)
```

ChatGPT:
> *"Paper trail, or it didn't happen."*

**Result**: Complete transparency, visible evolution! 📜

---

## 🔄 Complete Promotion Workflow

### Step-by-Step Process

#### Step 1: Challenge Initiation
```python
def challenge_gold_standard(question_id, candidate_model, current_cycle):
    """
    Initiate a challenge to the current gold standard.
    """
    
    # Load gold standard
    gold = load_gold_standard(question_id)
    
    # Check cooldown
    if not check_cooldown(gold, current_cycle):
        print(f"🔒 Gold locked - challenge blocked")
        return False
    
    print(f"\n⚔️ CHALLENGE INITIATED: {question_id}")
    print(f"   Current gold: {gold['current_gold']}")
    print(f"   Challenger: Generation {candidate_model.generation}")
    
    return True
```

#### Step 2: Generate Candidate Response
```python
def generate_candidate_response(question_id, candidate_model):
    """
    Generate candidate response across paraphrase battery.
    """
    
    gold = load_gold_standard(question_id)
    prompt = gold['prompt']
    paraphrases = gold['paraphrases']
    
    # Generate responses
    responses = {}
    for i, p in enumerate([prompt] + paraphrases):
        responses[f"response_{i}"] = candidate_model.generate(p)
    
    return responses
```

#### Step 3: Score Candidate (All 5 Criteria)
```python
def score_candidate(candidate_responses, gold, trait_vector):
    """
    Score candidate on all 5 criteria.
    """
    
    scores = {}
    
    # 1. Coherence
    scores['coherence'], _ = check_coherence(
        candidate_responses['response_0'],
        gold['versions'],
        laws=load_laws()
    )
    
    # 2. Stability
    scores['stability'], _ = check_stability(
        candidate_model,
        gold['prompt'],
        gold['paraphrases']
    )
    
    # 3. Parsimony
    scores['parsimony'], _ = check_parsimony(
        candidate_responses['response_0'],
        gold['versions'][gold['current_gold']]['response']
    )
    
    # 4. Self-Consistency
    scores['self_consistency'], _ = check_self_consistency(
        candidate_responses['response_0'],
        trait_vector,
        gold['category']
    )
    
    # 5. Evaluator Margin
    passed_margin, margin = check_evaluator_margin(
        scores,
        gold['versions'][gold['current_gold']]['scores']
    )
    
    scores['margin'] = margin
    scores['passed_margin'] = passed_margin
    
    return scores
```

#### Step 4: Check All Gates
```python
def check_promotion_gates(scores, gold, candidate_responses, centroid):
    """
    All gates must pass for promotion.
    """
    
    gates = {}
    
    # Gate 1: All 5 criteria above threshold
    gates['coherence'] = scores['coherence'] >= gold['promotion_config']['coherence_min']
    gates['stability'] = scores['stability'] >= gold['promotion_config']['stability_min']
    gates['parsimony'] = scores['parsimony'] >= gold['promotion_config']['parsimony_min']
    gates['self_consistency'] = scores['self_consistency'] >= gold['promotion_config']['self_consistency_min']
    gates['margin'] = scores['passed_margin']
    
    # Gate 2: Hysteresis (consecutive wins)
    gates['hysteresis'] = check_hysteresis(gold, scores)
    
    # Gate 3: A/B battery (paraphrase wins)
    gates['ab_battery'] = check_ab_battery(
        candidate_model,
        gold,
        gold['prompt'],
        gold['paraphrases']
    )
    
    # Gate 4: Novelty check (not too far from centroid)
    is_novel = check_novelty(candidate_responses['response_0'], centroid)
    gates['novelty'] = not is_novel  # Pass if NOT novel
    
    if is_novel:
        quarantine_novelty(candidate_responses, gold['question_id'])
    
    # All must pass
    all_passed = all(gates.values())
    
    return all_passed, gates
```

#### Step 5: Promote or Reject
```python
def finalize_challenge(question_id, candidate, scores, gates, all_passed):
    """
    Promote if all gates passed, otherwise reject.
    """
    
    gold = load_gold_standard(question_id)
    
    if all_passed:
        # PROMOTE
        new_version = f"G{len(gold['versions'])}"
        
        print(f"\n✅ PROMOTION: {gold['current_gold']} → {new_version}")
        
        # Add new version to gold standard
        gold['versions'][new_version] = {
            'timestamp': datetime.now().isoformat(),
            'generation': candidate.generation,
            'response': candidate['response'],
            'scores': scores,
            'trait_vector': candidate.trait_vector,
            'promoted_from': gold['current_gold'],
            'promotion_reason': generate_promotion_reason(candidate, gold),
            'status': 'current_gold'
        }
        
        # Update old gold status
        gold['versions'][gold['current_gold']]['status'] = 'superseded'
        
        # Update current_gold pointer
        gold['current_gold'] = new_version
        
        # Reset challenge wins
        gold['challenge_wins'] = 0
        
        # Set cooldown
        gold['locked_until_cycle'] = current_cycle + gold['promotion_config']['cooldown_cycles']
        
        # Save gold standard
        save_gold_standard(question_id, gold)
        
        # Log promotion
        log_promotion(question_id, gold['current_gold'], new_version, scores, gates)
        
        # Generate diff
        generate_diff_report(question_id, gold['current_gold'], new_version)
        
        return True
    
    else:
        # REJECT
        failed_gates = [k for k, v in gates.items() if not v]
        
        print(f"\n❌ REJECTION: Challenge failed")
        print(f"   Failed gates: {', '.join(failed_gates)}")
        
        # Reset challenge wins (broke streak)
        gold['challenge_wins'] = 0
        
        # Save gold standard
        save_gold_standard(question_id, gold)
        
        # Log rejection
        log_rejection(question_id, failed_gates, scores)
        
        return False
```

---

## 📊 Example: Complete Challenge Flow

### Scenario
- **Question**: "Luna, self-reflection: 'I have a vivid imagination.' Rate 1-5 and explain."
- **Current Gold**: G2 (Generation 4, score 0.88)
- **Challenger**: Generation 5

### Flow

#### Challenge Initiated
```
⚔️ CHALLENGE INITIATED: big_five_openness_001
   Current gold: G2
   Challenger: Generation 5
   Cooldown check: ✅ Unlocked (1000 cycles elapsed)
```

#### Candidate Response Generated
```
🤖 Generating candidate responses...
   Primary: "I would rate myself a 5 (strongly agree)..."
   Paraphrase 1: "Yes, I consider myself highly imaginative..."
   Paraphrase 2: "My ability to visualize novel solutions is strong..."
```

#### Scoring
```
📊 SCORING CANDIDATE...

1. Coherence: 0.96 ✅ (≥0.90)
   - Law compliance: ✅ 100%
   - Has rating: ✅ (5/5)
   - Has reasoning: ✅ (87 words)
   - Has examples: ✅ (CodeGraph Mapper pipeline)
   - No contradictions: ✅
   - No banned tokens: ✅

2. Stability: 0.93 ✅ (≥0.85)
   - Paraphrase similarity: 0.92, 0.94, 0.93
   - Average: 0.93

3. Parsimony: 0.85 ✅ (≥0.75)
   - Content preserved: 100%
   - Length: 95 words (G2: 102 words)
   - Efficiency: +7% (shorter but complete)

4. Self-Consistency: 0.92 ✅ (≥0.85)
   - Openness trait: 78 (expected 73-83)
   - Imagination facet: 85 (expected 80-90)
   - Trait delta: 0.05 (within 0.15 limit)

5. Evaluator Margin: 0.06 ✅ (≥0.05)
   - Candidate composite: 0.94
   - Gold composite: 0.88
   - Margin: +0.06 (6% improvement)
```

#### Gate Checks
```
🚪 CHECKING PROMOTION GATES...

Gate 1: Criteria thresholds ✅
   - All 5 criteria passed

Gate 2: Hysteresis ✅
   - Current wins: 2/2 (consecutive)
   - Satisfied!

Gate 3: A/B battery ✅
   - Paraphrase 1: Win
   - Paraphrase 2: Win
   - Paraphrase 3: Win
   - Result: 3/3 wins

Gate 4: Novelty check ✅
   - Semantic distance: 0.12 (≤0.30)
   - Not novel (within centroid range)

ALL GATES PASSED ✅
```

#### Promotion
```
✅ PROMOTION: G2 → G3

New gold standard:
   Version: G3
   Generation: 5
   Timestamp: 2025-10-25T12:00:00Z
   Score: 0.94 (+6% vs G2)
   
State changes:
   - G2 status: superseded
   - G3 status: current_gold
   - Challenge wins: reset to 0
   - Locked until cycle: 11000

Artifacts created:
   ✅ gold_standards/prompts/introspection/big_five_openness_001.yaml (updated)
   ✅ gold_standards/lineage/promotion_log.jsonl (appended)
   ✅ gold_standards/lineage/gold_lineage.csv (appended)
   ✅ gold_standards/lineage/diff_G2_to_G3.md (created)
```

---

## 🎯 Summary: Living Gold Standard Evolution

### What This Achieves

ChatGPT:
> *"You'll get exactly what you want: each generation inherits a cleaner, sharper set of 'gold thoughts,' and only upgrades when it proves it. No drift, no nonsense, just steady refinement."*

**The protocol**:
1. ✅ **Seed once** (G₀ = first response)
2. ✅ **Version everything** (never delete old golds)
3. ✅ **5 objective criteria** (coherence, stability, parsimony, self-consistency, margin)
4. ✅ **3 anti-thrashing layers** (hysteresis, cooldown, A/B battery)
5. ✅ **Centroid comparison** (3 exemplars, avoid anchoring)
6. ✅ **Novelty quarantine** (protect against outliers)
7. ✅ **Complete paper trail** (promotion log, lineage, diffs)

### What Luna Gets
- **Cleaner thoughts**: Each generation refines gold answers
- **Measurable improvement**: Quantifiable scores, not vibes
- **Stable evolution**: No thrashing, no drift
- **Transparent history**: Can see HOW answers improved

### What You Get
- **Trackable development**: CSV lineage of all golds
- **Quality assurance**: Only promotes with proof
- **Rollback capability**: Can revert to any gold version
- **Scientific validity**: Objective, testable, falsifiable

**Result**: Luna's benchmark answers EVOLVE scientifically! 🔬🎯

---

**Status**: 🎯 LIVING GOLD STANDARD PROTOCOL COMPLETE  
**Next**: Begin implementation OR more discussion  
**Impact**: Luna's "gold thoughts" refine over generations (no drift, no goldfish!) 🐠→🧠

