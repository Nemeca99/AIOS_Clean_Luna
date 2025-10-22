"""
Main runner for CodeGraph Mapper
Orchestrates the complete mapping workflow with dry-run and approval
"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, List, Dict

from .logging_util import CGMLogger
from .laws_gate import LawsGate
from .manifest import load_manifest, hash_manifest, validate_params
from .fs_walk import FileInventory
from .graph_build import GraphBuilder
from .emit_json import JSONEmitter
from .emit_csv import CSVEmitter
from .emit_dot import DOTEmitter
from .emit_mermaid import MermaidEmitter
from .report_md import MarkdownReporter
from .report_html import HTMLReporter


@dataclass
class CGMParams:
    """Parameters for code graph mapping"""
    root: str
    out_base: str
    include: List[str] = None
    exclude: List[str] = None
    dry_run: bool = True
    require_approval: bool = False
    allow_large: bool = False
    no_dot: bool = False
    no_mermaid: bool = False
    budget_ms: Optional[int] = None


class CGMResult:
    """Result of code graph mapping run"""
    def __init__(self):
        self.ok = False
        self.exit_code = 0
        self.run_id = None
        self.plan_path = None
        self.artifacts = []
        self.provenance_path = None
        self.metrics = {}
        self.error = None


def run_map(params: CGMParams) -> CGMResult:
    """
    Execute complete code graph mapping
    Returns: CGMResult with artifacts and metrics
    """
    result = CGMResult()
    start_time = time.perf_counter()
    
    # Initialize logger
    logger = CGMLogger()
    
    # Load manifest
    tool_root = Path(__file__).parent.parent
    manifest_path = tool_root / "tool.manifest.yaml"
    manifest = load_manifest(manifest_path)
    manifest_hash = hash_manifest(manifest_path)
    
    # Generate run ID
    run_id = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')[:20]
    result.run_id = run_id
    
    logger.info("start", run_id=run_id, params=params.__dict__)
    
    try:
        # Convert paths
        root = Path(params.root)
        out_base = Path(params.out_base)
        out_run_dir = out_base / run_id
        
        # Validate params against manifest
        if not validate_params(params.__dict__, manifest):
            logger.error("validation_failed", msg="Parameters violate manifest capabilities")
            result.error = "Parameter validation failed"
            result.exit_code = 2
            return result
        
        # Entry law check
        laws = LawsGate(root)
        ok, msg = laws.check_entry(root, out_run_dir)
        logger.info("law_check", stage="entry", ok=ok, msg=msg)
        
        if not ok:
            logger.error("law_violation", stage="entry", msg=msg)
            result.error = f"Law violation: {msg}"
            result.exit_code = 2
            return result
        
        # Compute law hash
        law_hash = laws.compute_law_hash()
        
        # Set defaults
        include = params.include or ["**/*.py"]
        exclude = params.exclude or ["**/__pycache__/**", "**/.venv/**", "**/.git/**", "**/python/Lib/**"]
        
        # Create output directory if not dry-run
        if not params.dry_run:
            out_run_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: File inventory
        inventory = FileInventory(
            root, 
            include, 
            exclude, 
            logger,
            progress_callback=lambda files, dirs: logger.info("scan_progress", files=files, dirs=dirs)
        )
        
        file_inv = inventory.walk()
        
        # Check budget
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        budget_limit = params.budget_ms or manifest['limits']['cpu_ms']
        
        if elapsed_ms > budget_limit * 0.8:
            logger.warn("budget_warning", elapsed_ms=elapsed_ms, limit=budget_limit)
        
        # Step 2: Build graph
        builder = GraphBuilder(root, file_inv, logger)
        graph_data = builder.build()
        
        # Check for output explosion
        if not params.allow_large and graph_data['stats']['edges'] > 250000:
            logger.error("circuit_breaker", 
                        reason="output_explosion", 
                        edges=graph_data['stats']['edges'],
                        limit=250000)
            result.error = "Circuit breaker: too many edges (use --allow-large to override)"
            result.exit_code = 4
            return result
        
        logger.info("graph_counts", **graph_data['stats'])
        
        # Generate provenance
        provenance = {
            "tool": "codegraph-mapper",
            "version": "1.0.0",
            "run_id": run_id,
            "params": params.__dict__,
            "counts": graph_data['stats'],
            "timestamps": {
                "start": datetime.now(timezone.utc).isoformat(),
                "end": None,
                "duration_ms": None
            },
            "law_hash": law_hash,
            "manifest_sha256": manifest_hash,
            "code_hash": _hash_cgm_code(tool_root / "cgm"),
            "budget_usage": {
                "cpu_ms": elapsed_ms,
                "files_opened": inventory.files_scanned,
                "ops_count": inventory.files_scanned + graph_data['stats']['nodes']
            }
        }
        
        # Step 3: Generate plan
        plan = _generate_plan(out_run_dir, graph_data, file_inv, params)
        
        if params.dry_run:
            # Dry-run: write plan only
            plan_path = out_base / f"plan_{run_id}.json"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(plan_path, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2)
            
            logger.info("dry_run_complete", plan=str(plan_path), writes=len(plan['writes']))
            result.ok = True
            result.plan_path = plan_path
            result.metrics = graph_data['stats']
            return result
        
        # Real run: check approval if required
        if params.require_approval:
            approval_file = out_run_dir / "APPROVAL_REQUIRED.txt"
            approval_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(approval_file, 'w', encoding='utf-8') as f:
                f.write(f"CodeGraph Mapper - Approval Required\n\n")
                f.write(f"Run ID: {run_id}\n")
                f.write(f"Artifacts to write: {len(plan['writes'])}\n\n")
                f.write(f"To approve, create file: approval.ok\n")
            
            logger.info("approval_wait", out=str(approval_file))
            
            # Wait for approval
            approval_ok = out_run_dir / "approval.ok"
            timeout = 300  # 5 minutes
            waited = 0
            
            while not approval_ok.exists() and waited < timeout:
                time.sleep(1)
                waited += 1
            
            if not approval_ok.exists():
                logger.error("approval_timeout", waited_sec=waited)
                result.error = "Approval timeout"
                result.exit_code = 5
                return result
            
            logger.info("approval_ok", by="human", file="approval.ok")
        
        # Step 4: Emit all artifacts
        written_files = []
        
        # JSON
        json_emitter = JSONEmitter(out_run_dir, logger)
        written_files.extend(json_emitter.emit_all(graph_data, file_inv))
        
        # CSV
        csv_emitter = CSVEmitter(out_run_dir, logger)
        written_files.extend(csv_emitter.emit_all(graph_data))
        
        # DOT (optional)
        if not params.no_dot:
            dot_emitter = DOTEmitter(out_run_dir, logger)
            written_files.append(dot_emitter.emit(graph_data))
        
        # Mermaid (optional)
        if not params.no_mermaid:
            mermaid_emitter = MermaidEmitter(out_run_dir, logger)
            written_files.append(mermaid_emitter.emit(graph_data))
        
        # Reports
        md_reporter = MarkdownReporter(out_run_dir, logger)
        written_files.append(md_reporter.generate(graph_data, file_inv, provenance))
        
        html_reporter = HTMLReporter(out_run_dir, logger)
        written_files.append(html_reporter.generate(graph_data, file_inv, provenance))
        
        # Pre-commit law check
        ok, msg = laws.check_precommit(written_files)
        logger.info("law_check", stage="precommit", ok=ok, msg=msg)
        
        if not ok:
            logger.error("law_violation", stage="precommit", msg=msg)
            result.error = f"Pre-commit law violation: {msg}"
            result.exit_code = 2
            return result
        
        # Write provenance
        end_time = time.perf_counter()
        provenance['timestamps']['end'] = datetime.now(timezone.utc).isoformat()
        provenance['timestamps']['duration_ms'] = int((end_time - start_time) * 1000)
        
        prov_path = out_run_dir / "provenance.json"
        with open(prov_path, 'w', encoding='utf-8') as f:
            json.dump(provenance, f, indent=2)
        written_files.append(prov_path)
        
        # Write shadow plan
        shadow_plan_path = out_run_dir / "plan.json"
        with open(shadow_plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2)
        
        logger.info("done", 
                   dur_ms=provenance['timestamps']['duration_ms'],
                   nodes=graph_data['stats']['nodes'],
                   edges=graph_data['stats']['edges'],
                   artifacts=len(written_files))
        
        result.ok = True
        result.artifacts = [str(p) for p in written_files]
        result.provenance_path = prov_path
        result.metrics = graph_data['stats']
        
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error("fatal", error=str(e), type=type(e).__name__, traceback=tb)
        result.error = str(e)
        result.exit_code = 1
    
    return result


def _generate_plan(out_dir: Path, graph_data: Dict, file_inv: Dict, params: CGMParams) -> Dict:
    """Generate execution plan (predicted artifacts and sizes)"""
    plan = {
        "run_id": out_dir.name,
        "dry_run": params.dry_run,
        "writes": []
    }
    
    # Predict artifact sizes (rough estimates)
    nodes_size = len(json.dumps(graph_data['nodes'])) if graph_data['nodes'] else 1000
    edges_size = len(json.dumps(graph_data['edges'])) if graph_data['edges'] else 1000
    
    artifacts = [
        ("graph/code_graph.json", nodes_size + edges_size + 100),
        ("graph/nodes.json", nodes_size),
        ("graph/edges.json", edges_size),
        ("graph/symbol_index.json", len(json.dumps(graph_data['symbol_index']))),
        ("graph/call_index.json", len(json.dumps(graph_data['call_index']))),
        ("graph/file_index.json", len(json.dumps(file_inv))),
        ("graph/import_matrix.csv", graph_data['stats']['modules'] * 100),
        ("graph/edges.csv", graph_data['stats']['edges'] * 80),
        ("reports/summary.md", 10000),
        ("reports/summary.html", 15000),
        ("provenance.json", 2000),
    ]
    
    if not params.no_dot:
        artifacts.append(("graph/code_graph.dot", graph_data['stats']['edges'] * 50))
    
    if not params.no_mermaid:
        artifacts.append(("graph/code_graph.mmd", graph_data['stats']['modules'] * 30))
    
    for rel_path, size_est in artifacts:
        plan['writes'].append({
            "path": str(out_dir / rel_path),
            "size_estimate": size_est
        })
    
    return plan


def _hash_cgm_code(cgm_dir: Path) -> str:
    """Compute hash of all CGM Python files (for provenance)"""
    hasher = hashlib.sha256()
    
    for py_file in sorted(cgm_dir.glob("*.py")):
        with open(py_file, 'rb') as f:
            hasher.update(f.read())
    
    return hasher.hexdigest()

