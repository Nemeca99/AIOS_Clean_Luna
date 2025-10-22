"""
Fossilization system for generational hygiene.

Creates immutable artifacts per generation:
- 8 required files
- Lineage ledger updates
- HEAD pointer management

Never overwrites history, only the working HEAD.
"""

import json
import hashlib
import csv
import shutil
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def calculate_sha256_bytes(data: bytes) -> str:
    """Calculate SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


def create_generation_directory(gen_id: int, parent_gen: Optional[str] = None) -> Path:
    """
    Create generation directory with timestamp.
    
    Format: Luna-G{NNN}-YYYYMMDD-HHMMSS/
    
    Args:
        gen_id: Generation number
        parent_gen: Parent generation name (if exists)
    
    Returns:
        Path to generation directory
    """
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    gen_name = f"Luna-G{gen_id:03d}-{timestamp}"
    gen_dir = Path("models") / gen_name
    
    gen_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Created generation directory: {gen_name}")
    
    # Record parent
    if parent_gen:
        parent_file = gen_dir / "parent_gen.txt"
        parent_file.write_text(parent_gen)
        print(f"  Parent: {parent_gen}")
    
    return gen_dir


def fossilize_generation(
    gen_id: int,
    gen_dir: Path,
    model_path: Path,
    training_args: Dict,
    metrics: Dict,
    data_delta_sha: str,
    parent_gen: Optional[str] = None
) -> Dict:
    """
    Create all required artifacts for a generation.
    
    8 required files:
    1. model.gguf
    2. tokenizer.json
    3. config.json
    4. train_args.json
    5. data_delta.sha256
    6. parent_gen.txt
    7. metrics.json
    8. EVAL.md
    
    Args:
        gen_id: Generation ID
        gen_dir: Generation directory
        model_path: Path to trained model
        training_args: Training hyperparameters
        metrics: Evaluation results
        data_delta_sha: SHA-256 of training data
        parent_gen: Parent generation name
    
    Returns:
        dict with artifact paths and hashes
    """
    
    print(f"\n📦 Fossilizing Generation {gen_id}...")
    
    artifacts = {}
    
    # 1. Model weights (copy if not already in gen_dir)
    model_file = gen_dir / "model"
    if model_path != model_file:
        if model_path.exists():
            if model_path.is_dir():
                # Copy entire directory
                shutil.copytree(model_path, model_file)
                print(f"  ✅ model/ (directory)")
            else:
                # Copy single file
                shutil.copy2(model_path, model_file)
                print(f"  ✅ model.gguf")
        else:
            print(f"  ⚠️ model.gguf (placeholder - model not trained yet)")
            model_file.write_bytes(b"placeholder")
    
    artifacts['model'] = str(model_file)
    
    # 2. Tokenizer (placeholder for now)
    tokenizer_file = gen_dir / "tokenizer.json"
    tokenizer_file.write_text(json.dumps({"vocab_size": 32000, "type": "llama"}, indent=2))
    print(f"  ✅ tokenizer.json")
    artifacts['tokenizer'] = str(tokenizer_file)
    
    # 3. Config (placeholder)
    config_file = gen_dir / "config.json"
    config_file.write_text(json.dumps({
        "model_type": "llama",
        "hidden_size": 2048,
        "num_layers": 22,
        "vocab_size": 32000
    }, indent=2))
    print(f"  ✅ config.json")
    artifacts['config'] = str(config_file)
    
    # 4. Training args
    train_args_file = gen_dir / "train_args.json"
    train_args_file.write_text(json.dumps(training_args, indent=2))
    print(f"  ✅ train_args.json")
    artifacts['train_args'] = str(train_args_file)
    
    # 5. Data delta hash
    data_hash_file = gen_dir / "data_delta.sha256"
    data_hash_file.write_text(data_delta_sha)
    print(f"  ✅ data_delta.sha256")
    artifacts['data_delta'] = str(data_hash_file)
    
    # 6. Parent gen (already written in create_generation_directory)
    if parent_gen:
        print(f"  ✅ parent_gen.txt")
    
    # 7. Metrics
    metrics_file = gen_dir / "metrics.json"
    metrics_file.write_text(json.dumps(metrics, indent=2))
    print(f"  ✅ metrics.json")
    artifacts['metrics'] = str(metrics_file)
    
    # 8. Human-readable eval report
    eval_md = generate_eval_md(gen_id, metrics, training_args, parent_gen)
    eval_file = gen_dir / "EVAL.md"
    eval_file.write_text(eval_md, encoding='utf-8')
    print(f"  ✅ EVAL.md")
    artifacts['eval'] = str(eval_file)
    
    # Calculate model hash (Merkle tree style for directories)
    if model_file.exists():
        if model_file.is_dir():
            # Merkle tree hash: combine hashes of all files in directory
            import hashlib
            file_hashes = []
            for file in sorted(model_file.rglob("*")):
                if file.is_file():
                    rel_path = str(file.relative_to(model_file))
                    file_hash = calculate_sha256(file)
                    combined = f"{rel_path}:{file_hash}"
                    file_hashes.append(combined)
            
            # Hash the combined list
            merkle_content = "\n".join(file_hashes)
            weights_sha = hashlib.sha256(merkle_content.encode()).hexdigest()
        elif model_file.stat().st_size > 100:
            weights_sha = calculate_sha256(model_file)
        else:
            weights_sha = "placeholder"
    else:
        weights_sha = "placeholder"
    
    artifacts['weights_sha256'] = weights_sha
    
    print(f"\n  Generation {gen_id} fossilized: {gen_dir.name}")
    print(f"  Model hash: {weights_sha[:16]}...")
    
    return artifacts


def generate_eval_md(gen_id: int, metrics: Dict, training_args: Dict, parent_gen: Optional[str]) -> str:
    """
    Generate human-readable evaluation report.
    
    Args:
        gen_id: Generation ID
        metrics: Evaluation results
        training_args: Training hyperparameters
        parent_gen: Parent generation name
    
    Returns:
        Markdown report
    """
    
    summary = metrics.get('summary', {})
    eval_results = metrics.get('evals', {})
    all_passed = metrics.get('all_passed', False)
    
    recall = summary.get('recall', 0.0)
    generalization = summary.get('generalization', 0.0)
    style_drift = summary.get('style_drift', 0)
    
    # Build report
    lines = [
        f"# Generation {gen_id} Evaluation",
        "",
        f"**Parent**: {parent_gen or 'None (Gen 0)'}",
        f"**Training Steps**: {training_args.get('steps', 'N/A')}",
        f"**Training Time**: {training_args.get('walltime_minutes', 'N/A')} minutes",
        "",
        "## Eval Results",
        f"- **Recall**: {recall:.3f} {'✅' if eval_results.get('recall', {}).get('passed', False) else '❌'} (>0.90 required)",
        f"- **Generalization**: {generalization:.3f} {'✅' if eval_results.get('generalization', {}).get('passed', False) else '❌'} (>0.80 required)",
        f"- **Style Drift**: {style_drift}/10 {'✅' if eval_results.get('style_drift', {}).get('passed', False) else '❌'} (<2 required)",
        "",
        "## Decision",
        f"{'✅ **PROMOTED TO HEAD**' if all_passed else '❌ **REJECTED**'} (evals {'passed' if all_passed else 'failed'})",
        "",
        "## Notes",
    ]
    
    if not all_passed:
        lines.append("- Generation failed evaluation gates")
        lines.append("- HEAD remains at parent generation")
    else:
        lines.append("- All evaluation gates passed")
        lines.append("- Generation promoted to HEAD")
    
    return "\n".join(lines)


def update_lineage_ledger(
    gen_id: int,
    parent_gen: Optional[str],
    weights_sha: str,
    data_delta_sha: str,
    training_args: Dict,
    metrics: Dict,
    promoted: bool
) -> None:
    """
    Append generation to lineage.csv.
    
    Args:
        gen_id: Generation ID
        parent_gen: Parent generation name
        weights_sha: Model weights SHA-256
        data_delta_sha: Training data SHA-256
        training_args: Training hyperparameters
        metrics: Evaluation results
        promoted: Whether generation was promoted to HEAD
    """
    
    ledger_path = Path("models/lineage.csv")
    
    # Ensure file exists with headers
    if not ledger_path.exists():
        with open(ledger_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'gen_id', 'parent', 'weights_sha256', 'data_delta_sha256',
                'steps', 'lr', 'loss_final', 'eval_recall', 'eval_gen',
                'eval_tone', 'weight_change_%', 'promoted_to_head', 'timestamp'
            ])
    
    # Extract metrics
    summary = metrics.get('summary', {})
    
    # Append row
    with open(ledger_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            gen_id,
            parent_gen or 'base',
            weights_sha[:8],
            data_delta_sha[:8],
            training_args.get('steps', 0),
            training_args.get('learning_rate', 0),
            training_args.get('loss_final', 0.0),
            summary.get('recall', 0.0),
            summary.get('generalization', 0.0),
            summary.get('style_drift', 0),
            training_args.get('weight_change_%', 0.0),
            promoted,
            datetime.now().isoformat()
        ])
    
    print(f"\n📊 Updated lineage ledger: {ledger_path}")


def promote_to_head(gen_dir: Path) -> None:
    """
    Update Luna-GHEAD pointer to new generation.
    
    Atomic operation using symlink.
    
    Args:
        gen_dir: Generation directory to promote
    """
    
    head_path = Path("models/Luna-GHEAD")
    
    print(f"\n🔄 Promoting to HEAD...")
    
    # Remove old HEAD if exists
    if head_path.exists() or head_path.is_symlink():
        if head_path.is_symlink():
            head_path.unlink()
        else:
            shutil.rmtree(head_path)
        print(f"  Removed old HEAD")
    
    # Create new symlink
    try:
        # Try symbolic link first (Unix/Linux)
        os.symlink(gen_dir.absolute(), head_path, target_is_directory=True)
        print(f"  ✅ HEAD → {gen_dir.name} (symlink)")
    except (OSError, NotImplementedError):
        # Fallback to directory junction (Windows) or copy
        try:
            import _winapi
            _winapi.CreateJunction(str(gen_dir.absolute()), str(head_path))
            print(f"  ✅ HEAD → {gen_dir.name} (junction)")
        except:
            # Final fallback: copy
            shutil.copytree(gen_dir, head_path)
            print(f"  ✅ HEAD → {gen_dir.name} (copy)")

