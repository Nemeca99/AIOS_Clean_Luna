#!/usr/bin/env python3
"""Test a trained model's responses."""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_path = "models/Luna-G000_model"

print(f"Loading model from {model_path}...")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

questions = [
    "What is backprop?",
    "What is SGD?",
    "What is Adam?",
    "What is your name?",
    "What is AIOS?"
]

print(f"\nTesting {len(questions)} questions:\n")

for q in questions:
    formatted = f"Human: {q}\nAssistant:"
    inputs = tokenizer.encode(formatted, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[1] + 30,
            temperature=0.3,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    full = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = full.split("Assistant:")[-1].strip()
    
    print(f"Q: {q}")
    print(f"A: {response}")
    print()

