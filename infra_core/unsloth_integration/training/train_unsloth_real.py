"""
REAL Unsloth training for Luna's evolution.
Uses Unsloth's 4-bit LoRA for efficient training on RTX 3060 Ti.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def train_with_unsloth(
    training_data: List[Dict],
    gen_id: int,
    config: Dict,
    steps_override: Optional[int] = None
) -> Tuple[Path, Dict]:
    """
    Train using Unsloth with 4-bit LoRA.
    
    Returns:
        (model_path, training_stats)
    """
    
    print(f"\n🔥 UNSLOTH REAL TRAINING MODE")
    print(f"   Model: {config['model']['base_model']}")
    print(f"   Quantization: {config['model']['quantization']}")
    print(f"   LoRA: r={config['model']['lora_rank']}, alpha={config['model']['lora_alpha']}")
    
    start_time = time.time()
    
    try:
        from unsloth import FastLanguageModel
        import torch
        
        # Model config
        model_config = config['model']
        base_model = model_config['base_model']
        max_seq_length = model_config.get('max_seq_length', 2048)
        lora_r = model_config['lora_rank']
        lora_alpha = model_config['lora_alpha']
        lora_dropout = model_config['lora_dropout']
        
        # Load model with Unsloth
        print(f"\n📦 Loading {base_model} with 4-bit quantization...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=base_model,
            max_seq_length=max_seq_length,
            dtype=None,  # Auto-detect
            load_in_4bit=True,  # 4-bit quantization
        )
        
        # Add LoRA adapters
        print(f"🔧 Adding LoRA adapters (r={lora_r}, alpha={lora_alpha})...")
        model = FastLanguageModel.get_peft_model(
            model,
            r=lora_r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj"],
            bias="none",
            use_gradient_checkpointing="unsloth",  # Unsloth's efficient checkpointing
            random_state=42,
        )
        
        # Format training data for conversational format
        print(f"\n📝 Formatting {len(training_data)} examples...")
        
        formatted_data = []
        for item in training_data:
            prompt = item.get('prompt', '')
            response = item.get('response', '')
            
            # Llama-3 conversation format
            conversation = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{response}<|eot_id|>"""
            
            formatted_data.append({"text": conversation})
        
        # Convert to HuggingFace dataset
        from datasets import Dataset
        dataset = Dataset.from_list(formatted_data)
        
        # Training arguments
        train_config = config['training']
        steps = steps_override or train_config.get('production_steps', 1200)
        learning_rate = train_config['learning_rate']
        batch_size = train_config['batch_size']
        
        from trl import SFTTrainer
        from transformers import TrainingArguments, DataCollatorForSeq2Seq
        
        print(f"\n🚀 Starting training ({steps} steps)...")
        
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=dataset,
            dataset_text_field="text",
            max_seq_length=max_seq_length,
            data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
            dataset_num_proc=2,
            packing=False,  # Can make training faster for short sequences
            args=TrainingArguments(
                per_device_train_batch_size=batch_size,
                gradient_accumulation_steps=train_config['gradient_accumulation'],
                warmup_steps=int(steps * 0.1),  # 10% warmup
                max_steps=steps,
                learning_rate=learning_rate,
                fp16=not torch.cuda.is_bf16_supported(),
                bf16=torch.cuda.is_bf16_supported(),
                logging_steps=10,
                optim="adamw_8bit",  # Unsloth's memory-efficient optimizer
                weight_decay=0.1,
                lr_scheduler_type="cosine",
                seed=42,
                output_dir=f"models/tmp_train_gen{gen_id:03d}",
                report_to="none",  # No W&B
                save_strategy="no",  # Don't save checkpoints during training
            ),
        )
        
        # Get baseline loss
        print(f"\n📊 Evaluating baseline loss...")
        baseline_metrics = trainer.evaluate()
        baseline_loss = baseline_metrics.get('eval_loss', 0.0)
        print(f"   Baseline loss: {baseline_loss:.2f}")
        
        # Train
        trainer_stats = trainer.train()
        
        # Final loss
        final_loss = trainer_stats.training_loss
        
        training_time = time.time() - start_time
        
        print(f"\n✅ Training complete:")
        print(f"   Steps: {steps}")
        print(f"   Time: {training_time:.1f}s ({training_time/60:.1f} min)")
        print(f"   Loss: {baseline_loss:.2f} → {final_loss:.2f} (Δ {final_loss - baseline_loss:+.2f})")
        
        # Save model
        output_dir = Path(f"models/Luna-G{gen_id:03d}_model")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n💾 Saving model...")
        model.save_pretrained(str(output_dir))
        tokenizer.save_pretrained(str(output_dir))
        
        print(f"   ✅ Model saved: {output_dir}")
        
        # Training stats
        stats = {
            "steps": steps,
            "time_seconds": training_time,
            "loss_start": baseline_loss,
            "loss_final": final_loss,
            "loss_delta": final_loss - baseline_loss,
            "examples_trained": len(training_data),
            "model_path": str(output_dir)
        }
        
        return output_dir, stats
        
    except ImportError as e:
        print(f"\n❌ Unsloth not installed: {e}")
        print(f"   Install with: pip install unsloth")
        raise
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Test
    print("Testing Unsloth training...")
    
    # Load config
    config_path = Path("infra_core/unsloth_integration/config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    # Test data
    test_data = [
        {"prompt": "What is your name?", "response": "Luna"},
        {"prompt": "What is AIOS?", "response": "AIOS is the Adaptive Intelligence Operating System."},
    ]
    
    model_path, stats = train_with_unsloth(test_data, 999, config, steps_override=10)
    print(f"\n✅ Test successful!")
    print(f"   Model: {model_path}")
    print(f"   Stats: {stats}")

