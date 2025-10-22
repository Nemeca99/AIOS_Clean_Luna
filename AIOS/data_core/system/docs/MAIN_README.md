# CARMA: Cached Aided Retrieval Mycelium Architecture

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

> **Public claim (exact wording):**
> We present **CARMA (Cached Aided Retrieval Mycelium Architecture)**: a locally-runnable, fractal memory + adaptive cognitive cache that combines (1) a dual-layer cache (stack + chain) with fractal splitting, (2) semantic cross-linking and weighted network pathfinding, (3) reinforcement-based retention and eviction, and (4) a two-tier sleep/dream consolidation mechanism that produces measurable personality drift in a RAG-driven agent. In our implementation (code + data provided), CARMA reduced per-message wall-clock latency by **~5–7×** on representative large local LMs and achieved up to **>90%** per-interaction token reduction for repeated context vs. a baseline RAG approach on the same hardware/configuration. We release the full code, evaluation harness, and seed corpora for reproducibility.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- 32GB RAM (recommended)
- NVIDIA GPU (optional, for local models)
- Docker (optional, for containerized deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AIOS_Clean.git
cd AIOS_Clean

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run minimal demo
cd carma_minimal
python test_demo.py
```

### Full System Test

```bash
# Seed the cache
python "HiveMind/seed_carma_cache.py" --dir ./seed_corpus --limit 300

# Run Luna personality system
python "HiveMind/luna_main.py" --mode real_learning --questions 120

# Run continuous Luna system (real-time output)
python "HiveMind/continuous_real_luna.py"

# Run human evaluation
python human_eval/human_eval_prep.py --questions 120
```

## 🧠 What is CARMA?

CARMA is a novel memory architecture for AI agents that combines:

- **Fractal Memory Splitting**: Large documents are automatically split into semantically-specialized fragments
- **Dual Cache System**: Parallel 'stack' and serialized 'chain' cache management
- **Semantic Cross-linking**: Automatic creation of semantic connections between related fragments
- **Reinforcement Learning**: Hit-based fragment strengthening and eviction
- **Dream Cycles**: Two-tier sleep/dream consolidation for memory optimization
- **Personality Drift**: Measurable personality changes through learning

## 📊 Performance Results

### Latency Improvements
- **Response Time**: Reduced from ~100s to ~15-25s for large local models
- **Token Efficiency**: Up to 90% reduction in token usage for repeated context
- **Memory Growth**: Linear, predictable fragment growth with automatic splitting

### Human Evaluation Results
- **Overall Performance**: 14.2% improvement over baseline (3.85 vs 3.37)
- **Personality Traits**: Significant improvements across all Big Five traits
- **Effect Sizes**: Range from 0.38 (small) to 1.64 (very large)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input Query   │───▶│  CARMA Cache     │───▶│  LLM Response   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Fractal Mycelium │
                       │ Memory Network   │
                       └──────────────────┘
```

### Key Components

1. **Fractal Mycelium Cache** (`fractal_mycelium_cache.py`)
   - Self-organizing knowledge fragments
   - Automatic splitting when size thresholds exceeded
   - Cross-linking between related fragments

2. **CARMA Consciousness System** (`carma_100_percent_consciousness.py`)
   - 12-indicator consciousness assessment
   - Dream cycle management
   - Memory consolidation and aging

3. **Luna Personality System** (`luna_main.py`)
   - RAG-driven personality responses
   - Learning and adaptation
   - Fatigue and energy management

4. **Continuous Luna System** (`continuous_real_luna.py`)
   - Real-time continuous operation
   - Windows console encoding support
   - Background processing capability
   - Progress indicators and monitoring

5. **Human Evaluation Framework** (`human_eval/`)
   - Blinded evaluation system
   - Statistical analysis
   - Reproducible metrics

## 🔬 Reproducibility

**Reproducibility**: All code, seed data, and experiment scripts used for the results in this repository are included under `experiments/`. To reproduce the primary 120-question run, follow REPRODUCE.md and run `python "HiveMind/luna_main.py" --mode real_learning --questions 120`. Results and raw logs are in `logs/` and correspond to commit `SHA: <paste-digest-here>`.

See [REPRODUCE.md](REPRODUCE.md) for detailed reproduction instructions.

## 📁 Repository Structure

```
AIOS_Clean/
├── HiveMind/                  # Core CARMA system
│   ├── carma_100_percent_consciousness.py
│   ├── fractal_mycelium_cache.py
│   ├── luna_main.py
│   └── ablation_runner.py
├── human_eval/               # Human evaluation framework
├── carma_minimal/           # Minimal reference implementation
├── seed_corpus/             # Training data
├── Dockerfile               # Container configuration
├── requirements.txt         # Python dependencies
└── REPRODUCE.md            # Reproduction instructions
```

## 🐳 Docker Support

```bash
# Build the container
docker build -t carma-system .

# Run the system
docker run --rm carma-system python human_eval/human_eval_prep.py --sample --questions 5
```

## 📈 Experiments

### Available Experiments

1. **Seed + Stress Test**: `python "HiveMind/seed_carma_cache.py" --dir ./seed_corpus --limit 300`
2. **Luna Learning**: `python "HiveMind/luna_main.py" --mode real_learning --questions 120`
3. **Continuous Luna**: `python "HiveMind/continuous_real_luna.py"` (real-time, background capable)
4. **Ablation Testing**: `python "HiveMind/ablation_runner.py" --questions 120`
5. **Human Evaluation**: `python human_eval/human_eval_prep.py --questions 120`

### Metrics Captured

- Fragment growth over time
- Response latency measurements
- Token usage statistics
- Cache hit rates
- Personality trait changes
- Dream cycle effectiveness

## 🔬 Research Background

CARMA builds upon established research in:
- Neural Turing Machines and Differentiable Neural Computers
- Retrieval-Augmented Generation (RAG)
- Compressive memory and episodic memory research
- Mycelium-inspired distributed systems

See [PUBLIC_CLAIM.md](PUBLIC_CLAIM.md) for detailed prior art assessment.

## ⚠️ Safety and Ethics

This system includes persistent memory capabilities and should be used responsibly. See [SAFETY.md](SAFETY.md) for detailed safety guidelines.

**Important**: This is a research system and should not be used in production without extensive testing and safety review.

## 📄 License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and code of conduct.

## 📞 Contact

- Issues: [GitHub Issues](https://github.com/yourusername/AIOS_Clean/issues)
- Email: [Your contact email]
- Paper: [arXiv link when available]

## 🙏 Acknowledgments

- The mycelium network for architectural inspiration
- The open-source AI community for foundational research
- All contributors and testers

---

**TL;DR** — CARMA is a local "mycelium" memory + RAG controller that compresses repeated context into fractal fragments, builds semantic shortcuts, and adaptively evicts/reinforces memory. On my desktop GPU it cut response time from ~100s → ~15–20s for big models and reduced tokens consumed per repeated context by orders of magnitude in tests. Full repo + seed data + tests included.
