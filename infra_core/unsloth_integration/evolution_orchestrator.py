"""
Evolution Orchestrator - Core loop for micro-evolutionary training.

Coordinates:
1. Load HEAD model
2. Prepare training data
3. Train child generation
4. Run 3 evals
5. Fossilize artifacts
6. Promote HEAD if evals pass
7. Update lineage ledger

Dual-mode operation: heartbeat (autonomous) or CLI (manual).
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional

from .training.train_micro_gen import (
    train_micro_generation,
    load_training_data,
    save_replay_data,
    calculate_data_delta_hash,
    BudgetExceededError
)
from .evals.eval_suite import EvalSuite, create_qa_set_for_generation
from .fossils.fossilize_generation import (
    create_generation_directory,
    fossilize_generation,
    update_lineage_ledger,
    promote_to_head
)


def load_config() -> Dict:
    """Load evolution configuration."""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path) as f:
        return json.load(f)


def get_current_head_gen() -> Optional[int]:
    """
    Get current HEAD generation ID.
    
    Returns:
        Generation ID or None if no HEAD exists
    """
    
    head_path = Path("models/Luna-GHEAD")
    
    if not head_path.exists():
        return None
    
    # Try to read parent_gen.txt to determine current gen
    parent_file = head_path / "parent_gen.txt"
    if parent_file.exists():
        parent_name = parent_file.read_text().strip()
        # Extract gen ID from parent name (Luna-G###-...)
        if parent_name.startswith("Luna-G"):
            parent_id = int(parent_name.split("-")[1][1:])
            return parent_id + 1
    
    # Fallback: check lineage.csv
    lineage_path = Path("models/lineage.csv")
    if lineage_path.exists():
        with open(lineage_path) as f:
            lines = f.readlines()
        if len(lines) > 1:  # Has data beyond header
            last_line = lines[-1]
            gen_id = int(last_line.split(',')[0])
            return gen_id
    
    return 0


def get_parent_model_path() -> Optional[Path]:
    """
    Get path to current HEAD model.
    
    Returns:
        Path to parent model or None for Gen 0
    """
    
    head_path = Path("models/Luna-GHEAD")
    
    if not head_path.exists():
        return None
    
    model_file = head_path / "model.gguf"
    if model_file.exists():
        return model_file
    
    return None


def run_evolution_window(
    mode: str = "cli",
    gen_id: Optional[int] = None,
    steps_override: Optional[int] = None,
    new_conversations: Optional[list] = None
) -> Dict:
    """
    Run one complete evolution cycle.
    
    Steps:
    1. Load HEAD model
    2. Prepare training data (new + replay)
    3. Train child generation
    4. Run 3 evals
    5. Fossilize artifacts
    6. Promote HEAD if evals pass
    7. Update lineage ledger
    
    Args:
        mode: "heartbeat" or "cli"
        gen_id: Generation ID (auto-detect if None)
        steps_override: Override training steps (for smoke tests)
        new_conversations: New training data (auto-load if None)
    
    Returns:
        dict with metrics and promotion status
    """
    
    print("\n" + "="*60)
    print(f"EVOLUTION WINDOW OPENED (mode: {mode})")
    print("="*60)
    
    start_time = time.time()
    
    # Load config
    config = load_config()
    
    # Determine generation ID
    if gen_id is None:
        current_head = get_current_head_gen()
        gen_id = (current_head + 1) if current_head is not None else 0
    
    print(f"\nGeneration: {gen_id}")
    
    # Get parent
    parent_model_path = get_parent_model_path()
    parent_gen_name = None
    if parent_model_path:
        parent_gen_name = parent_model_path.parent.name
        print(f"Parent: {parent_gen_name}")
    else:
        print(f"Parent: None (Gen 0 - base model)")
    
    result = {
        'gen_id': gen_id,
        'parent': parent_gen_name,
        'mode': mode,
        'promoted': False,
        'reason': '',
        'metrics': {},
        'artifacts': {},
        'walltime_seconds': 0
    }
    
    try:
        # Step 1: Create generation directory
        gen_dir = create_generation_directory(gen_id, parent_gen_name)
        result['gen_dir'] = str(gen_dir)
        
        # Step 2: Load training data
        print(f"\n📚 Loading training data...")
        if gen_id == 0:
            # Create real training data for Gen 0
            training_data = [
                {"prompt": "What is your name?", "response": "Luna"},
                {"prompt": "What is AIOS?", "response": "AI Operating System"},
                {"prompt": "Hello", "response": "Hello! I'm Luna."},
                {"prompt": "How are you?", "response": "I'm doing well, thank you!"},
                {"prompt": "What can you do?", "response": "I can help with AI and technology questions."}
            ]
            print(f"  Created {len(training_data)} real training examples for Gen 0")
        else:
            training_data = load_training_data(gen_id, new_conversations)
        data_delta_sha = calculate_data_delta_hash(training_data)
        print(f"  Data hash: {data_delta_sha[:16]}...")
        
        # Step 3: Train child generation
        print(f"\n🔨 Training Generation {gen_id}...")
        
        try:
            model_path, training_stats = train_micro_generation(
                parent_model_path=parent_model_path,
                training_data=training_data,
                gen_id=gen_id,
                config=config,
                steps_override=steps_override
            )
            
            result['model_path'] = str(model_path)
            result['training_stats'] = training_stats
            
        except BudgetExceededError as e:
            print(f"\n❌ BUDGET EXCEEDED: {e}")
            result['reason'] = f"Budget exceeded: {e}"
            result['promoted'] = False
            return result
        
        # Step 4: Run evaluations
        print(f"\n⚖️ Running evaluation suite...")
        
        eval_suite = EvalSuite(config)
        
        # Create QA set for future recall testing
        create_qa_set_for_generation(gen_id, training_data)
        
        # Run evals with actual model
        eval_results = eval_suite.run_full_suite(
            model=model_path,  # Pass model path
            prior_gen_id=gen_id - 1,
            new_data=training_data
        )
        
        result['metrics'] = {
            'evals': eval_results,
            'summary': eval_results['summary'],
            'all_passed': eval_results['all_passed']
        }
        
        # Step 5: Fossilize generation
        print(f"\n📦 Creating immutable artifacts...")
        
        artifacts = fossilize_generation(
            gen_id=gen_id,
            gen_dir=gen_dir,
            model_path=model_path,
            training_args=training_stats,
            metrics=result['metrics'],
            data_delta_sha=data_delta_sha,
            parent_gen=parent_gen_name
        )
        
        result['artifacts'] = artifacts
        
        # Step 6: Promotion decision
        all_passed = eval_results['all_passed']
        
        if all_passed:
            print(f"\n✅ ALL EVALS PASSED - Promoting to HEAD")
            
            promote_to_head(gen_dir)
            result['promoted'] = True
            result['reason'] = "All evals passed"
            
        else:
            print(f"\n❌ EVALS FAILED - HEAD unchanged")
            result['promoted'] = False
            result['reason'] = "Evals failed: " + ", ".join([
                k for k, v in eval_results.items()
                if isinstance(v, dict) and not v.get('passed', True)
            ])
        
        # Step 7: Update lineage ledger
        print(f"\n📊 Updating lineage ledger...")
        
        update_lineage_ledger(
            gen_id=gen_id,
            parent_gen=parent_gen_name,
            weights_sha=artifacts['weights_sha256'],
            data_delta_sha=data_delta_sha,
            training_args=training_stats,
            metrics=result['metrics'],
            promoted=result['promoted']
        )
        
        # Save replay data for next generation
        save_replay_data(gen_id, training_data)
        
        # Final summary
        elapsed = time.time() - start_time
        result['walltime_seconds'] = elapsed
        
        print(f"\n" + "="*60)
        print(f"EVOLUTION CYCLE COMPLETE")
        print(f"="*60)
        print(f"\nGeneration: {gen_id}")
        print(f"Status: {'✅ PROMOTED' if result['promoted'] else '❌ REJECTED'}")
        print(f"Reason: {result['reason']}")
        print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"Artifacts: {gen_dir}")
        print(f"\n" + "="*60 + "\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ EVOLUTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        
        result['promoted'] = False
        result['reason'] = f"Error: {e}"
        result['walltime_seconds'] = time.time() - start_time
        
        return result


def check_evolution_window(heartbeat_cycle: int, config: Optional[Dict] = None) -> bool:
    """
    Check if evolution window is open based on heartbeat cycle.
    
    Args:
        heartbeat_cycle: Current heartbeat cycle number
        config: Evolution config (auto-load if None)
    
    Returns:
        True if evolution window is open
    """
    
    if config is None:
        config = load_config()
    
    evo_period = config['evo_period_cycles']
    
    return heartbeat_cycle % evo_period == 0

