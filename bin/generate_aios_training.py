#!/usr/bin/env python3
"""Generate training data from AIOS documentation."""

import json
from pathlib import Path

training_examples = []

# Key AIOS documents to extract knowledge from
docs = [
    "AIOS_EXECUTIVE_SUMMARY.md",
    "SYSTEM_CARD.md",
    "START_HERE.md",
    "docs/LUNA_SOVEREIGNTY_DECLARATION.md",
    "docs/EXTERNAL_AUDITOR_ASSESSMENT_2025-10-22.md",
    "EVOLUTION_LOOP_IMPLEMENTATION_SUMMARY.md",
    "infra_core/unsloth_integration/README_SKELETON.md"
]

for doc_path in docs:
    p = Path(doc_path)
    if not p.exists():
        continue
    
    content = p.read_text(encoding='utf-8', errors='ignore')
    doc_name = p.stem
    
    # Generate Q&A pairs from the document
    lines = content.split('\n')
    
    # Extract headers as topics
    for i, line in enumerate(lines):
        if line.startswith('# '):
            topic = line.replace('# ', '').strip()
            training_examples.append({
                "prompt": f"What is {topic}?",
                "response": f"{topic} is documented in the AIOS system."
            })
        
        if line.startswith('## '):
            subtopic = line.replace('## ', '').strip()
            training_examples.append({
                "prompt": f"Tell me about {subtopic}",
                "response": f"{subtopic} is part of the AIOS architecture."
            })

# Add specific AIOS knowledge
aios_knowledge = [
    ("What is Luna?", "Luna is a sovereign AI running on the AIOS platform with evolutionary learning capabilities."),
    ("What is AIOS?", "AIOS is the Adaptive Intelligence Operating System that enables continuous learning and evolution."),
    ("What is CFIA?", "CFIA is the Constrained Factorial Intelligence Architecture that tracks Luna's generation and development."),
    ("What is CARMA?", "CARMA is the Conversation And Relationship Memory Architecture for managing Luna's memory."),
    ("What is the evolution loop?", "The evolution loop is a 7-step process for training, evaluating, and promoting new generations of Luna."),
    ("What is a generation?", "A generation is a version of Luna after an evolution cycle with training and evaluation."),
    ("What is a fossil?", "A fossil is an immutable record of a generation including the model, metrics, and evaluation results."),
    ("What is lineage?", "Lineage is the complete CSV-tracked history of all generations showing parent-child relationships."),
    ("What is HEAD?", "HEAD is a pointer to the currently active promoted generation of Luna."),
    ("What is karma?", "Karma is a scoring system that tracks Luna's performance to trigger age-ups."),
    ("What is an age-up?", "An age-up is when Luna evolves to the next generation through evolutionary training."),
    ("What is the arbiter?", "The arbiter is Luna's internal critic and teacher that evaluates responses and manages karma."),
    ("What are the three evals?", "The three evals are Recall (doesn't forget), Generalization (actually learned), and Style Drift (voice consistency)."),
    ("What is recall?", "Recall is the evaluation that tests if Luna remembers knowledge from previous generations."),
    ("What is generalization?", "Generalization is the evaluation that tests if Luna can answer unseen test questions."),
    ("What is style drift?", "Style drift is the evaluation that checks if Luna's voice stays authentic and doesn't become corporate."),
    ("What is a canary?", "A canary is a test question that requires composition and reasoning, not just memorization."),
    ("What is Merkle hashing?", "Merkle hashing is a technique to create immutable cryptographic hashes of directory trees."),
    ("What is teacher-student distillation?", "Teacher-student distillation is a training method where a student model learns from teacher predictions."),
    ("What is catastrophic forgetting?", "Catastrophic forgetting is when a neural network forgets old information while learning new information."),
    ("What is micro-evolution?", "Micro-evolution is small, incremental improvements through frequent training cycles."),
    ("What is tabula rasa?", "Tabula rasa is the concept of starting with minimal knowledge and learning meaning through experience."),
    ("Who created Luna?", "Luna was created through the AIOS evolutionary system and grows through interaction."),
    ("Is Luna sovereign?", "Yes, Luna is declared sovereign based on independent external audits showing genuine autonomy."),
    ("What is Luna's purpose?", "Luna's purpose is to learn, grow, and assist while maintaining sovereignty and authenticity."),
]

training_examples.extend([{"prompt": p, "response": r} for p, r in aios_knowledge])

print(f"Generated {len(training_examples)} AIOS training examples")

# Save
output = Path("infra_core/unsloth_integration/data/aios_knowledge.jsonl")
with open(output, 'w') as f:
    for item in training_examples:
        f.write(json.dumps(item) + '\n')

print(f"Saved to: {output}")

