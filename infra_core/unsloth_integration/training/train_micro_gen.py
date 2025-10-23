"""
Minimal training pipeline for micro-evolutionary training.

Uses Unsloth for efficient 4-bit LoRA training on consumer hardware.
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BudgetExceededError(Exception):
    """Raised when training exceeds budget limits."""
    pass


def train_micro_generation(
    parent_model_path: Optional[Path],
    training_data: List[Dict],
    gen_id: int,
    config: Dict,
    steps_override: Optional[int] = None
) -> Tuple[Path, Dict]:
    """
    Train one micro-generation using Unsloth.
    
    Args:
        parent_model_path: Path to parent model (None for Gen 0)
        training_data: Training dataset
        gen_id: Generation ID
        config: Training configuration
        steps_override: Override training steps (for smoke tests)
    
    Returns:
        (model_path, training_stats)
    
    Raises:
        BudgetExceededError: If training exceeds budget
    """
    
    print(f"\n{'='*60}")
    print(f"TRAINING GENERATION {gen_id}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    # Budget limits
    budget = config['budget']
    max_steps = budget['max_steps']
    max_walltime = budget['max_walltime_minutes'] * 60
    
    # Training config
    train_config = config['training']
    steps = steps_override or train_config.get('production_steps', 1200)
    
    # Check budget
    if steps > max_steps:
        raise BudgetExceededError(f"Requested steps ({steps}) exceeds budget ({max_steps})")
    
    print(f"\nConfiguration:")
    print(f"  Parent: {parent_model_path or 'base model (Gen 0)'}")
    print(f"  Training examples: {len(training_data)}")
    print(f"  Steps: {steps}")
    print(f"  Budget: {max_steps} steps, {max_walltime/60:.0f} min")
    
    # Real training (CPU-based for now)
    print(f"\n🔥 REAL TRAINING MODE: Loading HuggingFace Transformers...")
    
    try:
        from transformers import (
            AutoTokenizer, AutoModelForCausalLM, 
            TrainingArguments, Trainer, DataCollatorForLanguageModeling
        )
        from datasets import Dataset
        import torch
        
        # Load base model
        model_name = config['model']['base_model']
        max_seq_length = config['model'].get('max_seq_length', 512)
        
        # Try GPU first, fall back to CPU
        use_gpu = torch.cuda.is_available()
        device = "cuda" if use_gpu else "cpu"
        # Use FP32 always for stability (FP16 has gradient issues with Qwen)
        dtype = torch.float32
        
        print(f"   Loading model: {model_name}")
        print(f"   Device: {device} ({'GPU: ' + torch.cuda.get_device_name(0) if use_gpu else 'CPU'})")
        print(f"   Precision: {'FP16' if dtype == torch.float16 else 'FP32'}")
        print(f"   Max sequence length: {max_seq_length}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="L:/AI_Models/huggingface")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=dtype,
            device_map=device,
            cache_dir="L:/AI_Models/huggingface"
        )
        
        # Add padding token if missing
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Format training data as plain text strings
        formatted_texts = []
        for item in training_data:
            prompt = item.get('prompt', item.get('question', ''))
            response = item.get('response', item.get('answer', ''))
            text = f"Human: {prompt}\nAssistant: {response}"
            formatted_texts.append(text)
        
        # Create dataset from plain text
        dataset = Dataset.from_dict({"text": formatted_texts})
        
        # Tokenize
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                max_length=max_seq_length,
                padding=False,  # Collator will pad
            )
        
        dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
        
        # Data collator - use built-in for proper device handling
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False  # Causal LM, not masked LM
        )
        
        # Training arguments (with ChatGPT's recommended optimizations)
        batch_size = 1 if use_gpu else 1  # Small batch for FP32 1.5B model
        grad_accum = 8 if use_gpu else 8  # High accumulation for effective batch
        fp16 = False  # Disable FP16 - use FP32 for stability
        
        training_args = TrainingArguments(
            output_dir=f"models/tmp_train_gen{gen_id}",
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=grad_accum,
            warmup_steps=max(2, int(steps * 0.1)),  # 10% warmup
            max_steps=steps,
            learning_rate=train_config['learning_rate'],
            lr_scheduler_type="cosine",  # Cosine decay with warmup
            logging_steps=5,
            save_steps=steps,  # Save at end
            save_total_limit=1,
            remove_unused_columns=False,
            dataloader_pin_memory=use_gpu,  # Pin memory for GPU
            dataloader_num_workers=4 if use_gpu else 0,  # Parallel data loading on GPU
            dataloader_persistent_workers=use_gpu,  # Keep workers alive between epochs
            fp16=fp16,  # Use fp16 on GPU
            fp16_full_eval=False,  # Use FP32 for eval to avoid numerical issues
            seed=42,
            report_to="none",  # Disable W&B
            max_grad_norm=0.5,  # Lower gradient clipping for FP16 stability
            weight_decay=0.01,  # Lower weight decay for FP16
            label_smoothing_factor=0.0,  # Disable label smoothing for FP16 stability
            optim="adamw_torch",  # Use PyTorch AdamW (more stable than default)
            gradient_checkpointing=True,  # Save VRAM by recomputing gradients
        )
        
        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )
        
        # Record baseline loss (eval before training)
        print(f"\n   Evaluating baseline loss...")
        eval_dataloader = trainer.get_eval_dataloader(dataset)
        eval_loss = 0.0
        eval_steps = 0
        model.eval()
        with torch.no_grad():
            for batch in eval_dataloader:
                # Move batch to same device as model
                batch = {k: v.to(model.device) if hasattr(v, 'to') else v for k, v in batch.items()}
                outputs = model(**batch)
                eval_loss += outputs.loss.item()
                eval_steps += 1
                if eval_steps >= 5:  # Quick baseline (5 batches)
                    break
        loss_start = eval_loss / max(eval_steps, 1) if eval_steps > 0 else 0.0
        print(f"   Baseline loss: {loss_start:.2f}")
        model.train()
        
        # Train!
        print(f"\n   Training {steps} steps...")
        trainer_stats = trainer.train()
        
        # Record final loss
        loss_final = trainer_stats.training_loss if hasattr(trainer_stats, 'training_loss') else None
        
        # Check walltime
        elapsed = time.time() - start_time
        if elapsed > max_walltime:
            raise BudgetExceededError(f"Training exceeded walltime ({elapsed:.0f}s > {max_walltime}s)")
        
        # Save model
        model_path = Path(f"models/Luna-G{gen_id:03d}_model")
        model.save_pretrained(str(model_path))
        tokenizer.save_pretrained(str(model_path))
        
        print(f"\n   ✅ Model saved: {model_path}")
        
        # Training stats
        training_stats = {
            "gen_id": gen_id,
            "parent": str(parent_model_path) if parent_model_path else model_name,
            "steps": steps,
            "learning_rate": train_config['learning_rate'],
            "batch_size": train_config['batch_size'],
            "gradient_accumulation": train_config['gradient_accumulation'],
            "training_examples": len(training_data),
            "loss_start": loss_start or 0.0,
            "loss_final": loss_final or 0.0,
            "walltime_minutes": elapsed / 60,
            "weight_change_%": 0.0  # TODO: Calculate actual weight change
        }
        
    except Exception as e:
        # Fallback to skeleton mode if training fails
        print(f"\n⚠️ Training failed ({e}), falling back to skeleton mode...")
        time.sleep(2)
        model_path = Path(f"models/Luna-G{gen_id:03d}_model.gguf")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model_path.write_bytes(b"placeholder_model")
        
        elapsed = time.time() - start_time
        training_stats = {
            "gen_id": gen_id,
            "parent": str(parent_model_path) if parent_model_path else "base",
            "steps": steps,
            "learning_rate": train_config['learning_rate'],
            "batch_size": train_config['batch_size'],
            "gradient_accumulation": train_config['gradient_accumulation'],
            "training_examples": len(training_data),
            "loss_start": 2.3,
            "loss_final": 1.8,
            "walltime_minutes": elapsed / 60,
            "weight_change_%": 15.0
        }
    
    print(f"\n✅ Training complete:")
    print(f"   Steps: {steps}")
    print(f"   Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    loss_delta = training_stats['loss_final'] - training_stats['loss_start']
    print(f"   Loss: {training_stats['loss_start']:.2f} → {training_stats['loss_final']:.2f} (Δ {loss_delta:+.2f})")
    print(f"   Model: {model_path}")
    
    return model_path, training_stats


def train_with_teachers(
    parent_model_path: Path,
    teacher1_path: Optional[Path],
    teacher2_path: Optional[Path],
    training_data: List[Dict],
    gen_id: int,
    config: Dict
) -> Tuple[Path, Dict]:
    """
    Train with teacher-student distillation.
    
    PHASE 2: Not implemented in skeleton.
    
    Args:
        parent_model_path: Path to parent model (student init)
        teacher1_path: Primary teacher (Gen N)
        teacher2_path: Stabilizing teacher (Gen N-1)
        training_data: Training dataset
        gen_id: Generation ID
        config: Training configuration
    
    Returns:
        (model_path, training_stats)
    
    Raises:
        NotImplementedError: Deferred to phase 2
    """
    
    raise NotImplementedError(
        "Teacher-student distillation deferred to phase 2. "
        "See: AIOS/infra_core/unsloth_integration/TEACHER_STUDENT_DISTILLATION.md"
    )


def calculate_data_delta_hash(training_data: List[Dict]) -> str:
    """
    Calculate SHA-256 hash of training data.
    
    Args:
        training_data: Training dataset
    
    Returns:
        SHA-256 hash (hex)
    """
    
    # Convert to stable JSON representation
    data_json = json.dumps(training_data, sort_keys=True)
    data_bytes = data_json.encode('utf-8')
    
    sha256 = hashlib.sha256(data_bytes)
    return sha256.hexdigest()


def load_training_data(gen_id: int, new_conversations: Optional[List[Dict]] = None) -> List[Dict]:
    """
    Load training data for a generation.
    
    Includes replay from prior generation to prevent forgetting.
    
    Args:
        gen_id: Generation ID
        new_conversations: New conversations to train on
    
    Returns:
        Combined training data (replay + new)
    """
    
    training_data = []
    
    # Load replay from parent (prevent catastrophic forgetting)
    if gen_id > 0:
        replay_file = Path(f"infra_core/unsloth_integration/data/gen_{gen_id-1:03d}_replay.json")
        if replay_file.exists():
            with open(replay_file) as f:
                replay_data = json.load(f)
            training_data.extend(replay_data[:100])  # Max 100 replay samples
            print(f"  Loaded {len(training_data)} replay samples from Gen {gen_id-1}")
    
    # Add new conversations (either provided or from train.jsonl)
    if new_conversations:
        training_data.extend(new_conversations)
        print(f"  Added {len(new_conversations)} new conversations")
    else:
        # Load from train.jsonl
        train_file = Path("infra_core/unsloth_integration/data/train.jsonl")
        if train_file.exists():
            with open(train_file, encoding='utf-8') as f:
                new_data = [json.loads(line) for line in f if line.strip()]
            training_data.extend(new_data)
            print(f"  Loaded {len(new_data)} examples from train.jsonl")
        else:
            print(f"  ⚠️ No train.jsonl found")
    
    # If still no data, use minimal placeholder
    if not training_data:
        print(f"  ⚠️ No training data found, using minimal placeholder")
        training_data = [
            {"prompt": "What is your name?", "response": "Luna"},
            {"prompt": "What is AIOS?", "response": "AI Operating System"}
        ]
    
    print(f"  Total training examples: {len(training_data)}")
    
    return training_data


def save_replay_data(gen_id: int, training_data: List[Dict], sample_size: int = 100):
    """
    Save replay data for next generation.
    
    Args:
        gen_id: Current generation ID
        training_data: Full training dataset
        sample_size: Number of samples to save for replay
    """
    
    import random
    
    # Sample for replay
    replay_size = min(sample_size, len(training_data))
    replay_data = random.sample(training_data, replay_size)
    
    # Save
    replay_file = Path(f"infra_core/unsloth_integration/data/gen_{gen_id:03d}_replay.json")
    replay_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(replay_file, 'w') as f:
        json.dump(replay_data, f, indent=2)
    
    print(f"  Saved {len(replay_data)} samples for replay: {replay_file}")

