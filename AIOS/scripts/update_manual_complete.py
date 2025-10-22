#!/usr/bin/env python3
"""
Complete Manual Update Workflow
Updates AIOS_MANUAL.md, regenerates TOC, rebuilds RAG database with embeddings
This is the ONE script to run after editing the manual.
"""

import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'=' * 70}")
    print(f"{text}")
    print(f"{'=' * 70}{Colors.RESET}\n")

def print_step(step, total, text):
    print(f"{Colors.YELLOW}[{step}/{total}] {text}...{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}   {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}   {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.WHITE}   {text}{Colors.RESET}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Update AIOS Manual and RAG database')
    parser.add_argument('--skip-toc', action='store_true', help='Skip TOC regeneration')
    parser.add_argument('--skip-embeddings', action='store_true', help='Skip RAG database rebuild')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    print_header("AIOS MANUAL UPDATE WORKFLOW")
    start_time = time.time()
    
    repo_root = Path.cwd()
    manual_path = repo_root / "AIOS_MANUAL.md"
    toc_path = repo_root / "MANUAL_TOC.md"
    
    # Step 1: Verify manual exists
    print_step(1, 4, "Verifying AIOS_MANUAL.md")
    if not manual_path.exists():
        print_error("ERROR: AIOS_MANUAL.md not found!")
        return 1
    
    manual_size = manual_path.stat().st_size / (1024 * 1024)  # MB
    with open(manual_path, 'r', encoding='utf-8') as f:
        manual_lines = len(f.readlines())
    
    print_success(f"Manual found: {manual_size:.2f} MB, {manual_lines:,} lines")
    
    # Step 2: Regenerate TOC
    if not args.skip_toc:
        print_step(2, 4, "Regenerating MANUAL_TOC.md")
        
        try:
            # Read manual
            with open(manual_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Generate TOC
            toc_lines = []
            toc_lines.append('# AIOS Manual - Table of Contents\n')
            toc_lines.append('\n')
            toc_lines.append('**Note:** Use line numbers for navigation. Canonical PDF is 660 pages (Letter, 1" margins).\n')
            toc_lines.append('\n')
            toc_lines.append('| Line | Section | Topic |\n')
            toc_lines.append('|------|---------|-------|\n')
            
            section_num = ''
            in_code_block = False
            
            for i, line in enumerate(lines, 1):
                line_stripped = line.rstrip()
                
                # Track code blocks
                if line_stripped.startswith('```'):
                    in_code_block = not in_code_block
                    continue
                
                # Skip lines inside code blocks
                if in_code_block:
                    continue
                
                # Only process headings with anchor IDs {#...}
                # This filters out command examples and inline TOC
                if ' {#' in line_stripped:
                    if line_stripped.startswith('## '):
                        # Second level heading with anchor
                        title = line_stripped[3:].split('{')[0].strip()
                        section_num = title.split()[0] if title and title[0].isdigit() else ''
                        toc_lines.append(f'| {i} | {section_num} | {title} |\n')
                    elif line_stripped.startswith('### '):
                        # Third level heading with anchor
                        title = line_stripped[4:].split('{')[0].strip()
                        section_num = title.split()[0] if title and title[0].isdigit() else ''
                        toc_lines.append(f'| {i} | {section_num} | {title} |\n')
                elif line_stripped.startswith('# ') and not line_stripped.startswith('# AIOS'):
                    # Main heading (no anchor required for top-level)
                    title = line_stripped[2:].split('{')[0].strip()
                    # Must be numbered (1. Getting Started, etc.)
                    if title and title[0].isdigit():
                        section_num = title.split()[0]
                        toc_lines.append(f'| {i} | {section_num} | **{title}** |\n')
            
            # Write TOC
            with open(toc_path, 'w', encoding='utf-8') as f:
                f.writelines(toc_lines)
            
            print_success(f"TOC updated: {len(toc_lines):,} entries")
            
        except Exception as e:
            print_error(f"ERROR: TOC generation failed: {e}")
            return 1
    else:
        print_step(2, 4, "Skipping TOC regeneration (--skip-toc)")
    
    # Step 3: Update manual metadata
    print_step(3, 4, "Updating manual metadata")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    print_success(f"Timestamp: {timestamp}")
    print_success(f"Lines: {manual_lines:,}")
    
    # Step 4: Rebuild RAG database
    if not args.skip_embeddings:
        print_step(4, 4, "Rebuilding RAG database with embeddings")
        print_info("This will take ~10-20 seconds for embedding generation...")
        
        embed_start = time.time()
        
        try:
            # Run embedding script
            result = subprocess.run(
                [sys.executable, "scripts/build_oracle_with_embeddings.py"],
                capture_output=True,
                text=True,
                cwd=repo_root
            )
            
            embed_duration = time.time() - embed_start
            
            if result.returncode == 0:
                print_success(f"RAG database rebuilt in {embed_duration:.1f}s")
                
                # Check index file
                index_path = repo_root / "rag_core" / "manual_oracle" / "oracle_index.json"
                if index_path.exists():
                    index_size = index_path.stat().st_size / 1024  # KB
                    print_success(f"Index size: {index_size:.0f} KB")
                
                # Show embedding stats from output
                if args.verbose:
                    print(f"\n{Colors.GRAY}{result.stdout}{Colors.RESET}")
            else:
                print_error("WARNING: RAG database rebuild had issues")
                if args.verbose:
                    print(f"{Colors.RED}{result.stderr}{Colors.RESET}")
        
        except Exception as e:
            print_error(f"ERROR: RAG rebuild failed: {e}")
            return 1
    else:
        print_step(4, 4, "Skipping RAG database rebuild (--skip-embeddings)")
    
    # Summary
    total_duration = time.time() - start_time
    
    print_header("UPDATE COMPLETE!")
    
    print(f"{Colors.WHITE}Summary:{Colors.RESET}")
    print(f"{Colors.WHITE}  Manual: {manual_lines:,} lines ({manual_size:.2f} MB){Colors.RESET}")
    if not args.skip_toc:
        print(f"{Colors.WHITE}  TOC: Updated{Colors.RESET}")
    if not args.skip_embeddings:
        print(f"{Colors.WHITE}  RAG Database: Rebuilt with embeddings{Colors.RESET}")
    print(f"{Colors.WHITE}  Total time: {total_duration:.1f}s{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}Next steps:{Colors.RESET}")
    print(f"{Colors.GRAY}  - Test search: py main.py --rag search 'your query'{Colors.RESET}")
    print(f"{Colors.GRAY}  - Run audit: py main.py --audit --v3{Colors.RESET}")
    print(f"{Colors.GRAY}  - Commit changes: git add AIOS_MANUAL.md MANUAL_TOC.md rag_core/{Colors.RESET}")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

