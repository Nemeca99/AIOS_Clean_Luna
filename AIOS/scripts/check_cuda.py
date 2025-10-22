#!/usr/bin/env python3
import torch

print("CUDA Detection:")
print(f"  CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  CUDA version: {torch.version.cuda}")
    print(f"  Device count: {torch.cuda.device_count()}")
    print(f"  Device 0: {torch.cuda.get_device_name(0)}")
    props = torch.cuda.get_device_properties(0)
    print(f"  VRAM: {props.total_memory / (1024**3):.1f} GB")
    print(f"  Compute capability: {props.major}.{props.minor}")
else:
    print("  CUDA not available - CPU-only torch installed")
    print("  To enable CUDA: pip uninstall torch")
    print("  Then: pip install torch --index-url https://download.pytorch.org/whl/cu121")

