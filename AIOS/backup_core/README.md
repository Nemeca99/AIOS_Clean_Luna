# AIOS Backup Core - Git-like Version Control System

A full-featured version control system for AIOS Clean, inspired by Git. Provides commit history, branching, staging, and content-addressable storage with both Python and Rust implementations.

## 🚀 Features

### Core Git-like Features
- **Content-Addressable Storage**: Deduplicates files using SHA256 hashes
- **Full Commit History**: Track all changes with detailed commit metadata
- **Branching & Merging**: Create, switch, and merge branches
- **Staging Area**: Selectively stage files for commit
- **Diff & Status**: See what changed and when
- **Tags**: Version your commits with meaningful tags
- **Detached HEAD**: Checkout specific commits

### Implementation
- **Python**: Full-featured implementation with all Git-like features
- **Rust**: High-performance implementation for basic backup operations
- **Hybrid Mode**: Automatically use Rust when available, fallback to Python

## 📦 Installation

The backup core is part of the AIOS Clean project. No additional installation needed if you have the project set up.

### Dependencies
```bash
# Python dependencies (already in main project)
- Python 3.8+
- pathlib, json, hashlib (standard library)

# Rust dependencies (optional, for performance)
- Rust 1.70+
- Cargo
```

## 🎯 Quick Start

### Initialize and Create First Commit

```python
from backup_core import BackupCore

# Initialize backup system
backup = BackupCore()

# Stage files for commit
backup.add(all_files=True)  # Stage all files
# OR
backup.add(["carma_core/", "data_core/"])  # Stage specific files

# Create a commit
backup.commit("Initial commit", author="Travis")

# View status
backup.status()

# View commit history
backup.log()
```

### Working with Branches

```python
# Create a new branch
backup.branch_create("feature-meditation")

# Switch to branch
backup.branch_switch("feature-meditation")

# Make changes, stage, and commit
backup.add(["dream_core/"])
backup.commit("Add meditation features")

# List all branches
backup.branch_list()

# Merge branch back to main
backup.branch_switch("main")
backup.branch_merge("feature-meditation")

# Delete branch after merge
backup.branch_delete("feature-meditation")
```

### Tags and Versioning

```python
# Create a tag at current commit
backup.tag_create("v1.0.0")

# Create a tag at specific commit
backup.tag_create("v0.9.0", "abc123def")

# List all tags
backup.tag_list()

# Checkout a tag
backup.checkout("v1.0.0")
```

### Viewing Changes

```python
# See working directory status
backup.status()

# See changes in a file
backup.diff("carma_core/carma_core.py")

# See staged changes
backup.diff("carma_core/carma_core.py", cached=True)

# View commit details
backup.show()  # Show HEAD commit
backup.show("abc123def")  # Show specific commit
```

## 📚 Complete API Reference

### BackupCore Class

#### Initialization
```python
BackupCore(workspace_root: Optional[Path] = None)
```
Creates a new backup system instance. If `workspace_root` is not specified, uses parent directory of backup_core.

#### Staging Operations

**`add(paths: Optional[List[str]] = None, all_files: bool = False)`**
- Add files to staging area
- `paths`: List of file/directory paths
- `all_files`: Stage all files in workspace

**`unstage(file_path: str)`**
- Remove specific file from staging area

**`unstage_all()`**
- Clear entire staging area

#### Commit Operations

**`commit(message: str, author: Optional[str] = None) -> Optional[str]`**
- Create commit from staged files
- Returns commit hash

**`log(max_count: Optional[int] = 20)`**
- Show commit history
- `max_count`: Maximum commits to show

**`show(commit_hash: Optional[str] = None)`**
- Show details of a commit
- Defaults to HEAD if not specified

#### Branch Operations

**`branch_create(branch_name: str, start_point: Optional[str] = None) -> bool`**
- Create new branch
- `start_point`: Commit/branch/tag to start from (defaults to HEAD)

**`branch_delete(branch_name: str, force: bool = False) -> bool`**
- Delete a branch
- `force`: Delete even if not merged

**`branch_rename(old_name: str, new_name: str) -> bool`**
- Rename a branch

**`branch_switch(branch_name: str, create: bool = False) -> bool`**
- Switch to different branch
- `create`: Create branch if doesn't exist

**`branch_list(verbose: bool = False)`**
- List all branches
- `verbose`: Show detailed information

**`branch_merge(branch_name: str, message: Optional[str] = None) -> bool`**
- Merge branch into current branch
- Fast-forward merge only (for now)

#### Status and Diff Operations

**`status()`**
- Show working directory status
- Lists staged, modified, untracked, and deleted files

**`diff(file_path: Optional[str] = None, cached: bool = False)`**
- Show file changes
- `cached`: Show staged changes vs unstaged

#### Tag Operations

**`tag_create(tag_name: str, commit_hash: Optional[str] = None)`**
- Create tag at commit (defaults to HEAD)

**`tag_delete(tag_name: str)`**
- Delete a tag

**`tag_list()`**
- List all tags

#### Checkout and Navigation

**`checkout(ref: str)`**
- Checkout commit, branch, or tag
- `ref`: Branch name, tag name, or commit hash

#### Information

**`info()`**
- Print comprehensive system information

**`get_system_info() -> Dict[str, Any]`**
- Get system information as dictionary

#### Legacy Compatibility

**`create_backup(...) -> str`**
- Legacy method for compatibility
- Creates commit with all files

## 🏗️ Architecture

### Module Structure

```
backup_core/
├── core/                       # Core components
│   ├── objects.py             # Object storage (blobs, trees, commits)
│   ├── refs.py                # Reference management (branches, tags, HEAD)
│   ├── staging.py             # Staging area (index)
│   ├── commits.py             # Commit operations
│   ├── branches.py            # Branch management
│   ├── diff.py                # Diff and status
│   ├── file_ops.py            # File system operations
│   └── config.py              # Configuration
├── rust_backup/               # Rust implementation
│   ├── src/lib.rs            # Rust backup code
│   └── Cargo.toml            # Rust dependencies
├── backup_core.py             # Main Python API
├── hybrid_backup_core.py      # Hybrid Python/Rust wrapper
├── __init__.py               # Module exports
└── README.md                 # This file
```

### Repository Structure

```
.aios_backup/                  # Repository directory
├── objects/                   # Content-addressable storage
│   ├── ab/                   # Sharded by first 2 hash chars
│   │   └── c123...           # Compressed object files
│   └── ...
├── refs/
│   ├── heads/                # Branch references
│   │   ├── main
│   │   └── feature-branch
│   └── tags/                 # Tag references
│       └── v1.0.0
├── HEAD                       # Current branch/commit
├── index                      # Staging area
└── config                     # Repository configuration
```

### Object Storage

Three types of Git-like objects:

1. **Blob**: File content
2. **Tree**: Directory structure (list of files/subdirs)
3. **Commit**: Commit metadata (tree hash, parents, author, message)

All objects are:
- Content-addressed using SHA256
- Compressed with zlib
- Deduplicated (identical content = same hash)
- Stored in `.aios_backup/objects/`

## 🔧 Core Modules

### objects.py - Object Storage
- `ObjectStore`: Content-addressable storage
- `BlobObject`: File content storage
- `TreeObject`: Directory structure
- `CommitObject`: Commit metadata

### refs.py - Reference Management
- `RefManager`: Manages branches, tags, and HEAD
- Branch operations (create, delete, rename)
- Tag operations
- HEAD management (attached/detached)

### staging.py - Staging Area
- `StagingArea`: Git-like index
- Stage/unstage files
- Build tree for commit

### commits.py - Commit Management
- `CommitManager`: Create and manage commits
- Commit history walking
- Parent/ancestor tracking

### branches.py - Branch Management
- `BranchManager`: Branch operations
- Create, delete, rename, switch
- Fast-forward merging

### diff.py - Diff Engine
- `DiffEngine`: Status and diff operations
- Working directory status
- File change detection
- Simple unified diff

### file_ops.py - File Operations
- `FileOperations`: File system helpers
- Ignore pattern support (.backupignore)
- File mode detection
- Safe file reading/writing

### config.py - Configuration
- `BackupConfig`: Configuration management
- Default settings
- Save/load configuration
- Dot-notation access

## 🚀 Hybrid Python/Rust Implementation

The system supports both Python and Rust implementations:

```python
from backup_core import HybridBackupCore

# Initialize hybrid system
backup = HybridBackupCore()

# Use Python implementation (full features)
backup.switch_to_python()

# Use Rust implementation (basic backup only)
backup.switch_to_rust()

# Benchmark both implementations
backup.benchmark()
```

### Python Implementation
- ✅ All Git-like features
- ✅ Full compatibility
- ✅ Easy to extend

### Rust Implementation
- ✅ High performance
- ✅ Basic backup operations
- ⚠️ Limited Git features (no branching yet)

## 📋 Usage Examples

### Example 1: Daily Backup Workflow

```python
backup = BackupCore()

# Morning: Start feature work
backup.branch_create("feature-auth")
backup.branch_switch("feature-auth")

# Work on files...
backup.add(["carma_core/", "data_core/"])
backup.commit("Add authentication system")

# Afternoon: More work
backup.add(["utils_core/"])
backup.commit("Add utility functions for auth")

# Evening: Merge back to main
backup.branch_switch("main")
backup.branch_merge("feature-auth")
backup.tag_create("daily-2025-10-09")
```

### Example 2: Exploring History

```python
backup = BackupCore()

# See what's changed
backup.status()

# View recent commits
backup.log(max_count=10)

# Look at specific commit
backup.show("abc123def")

# Go back in time
backup.checkout("v1.0.0")

# Come back to present
backup.branch_switch("main")
```

### Example 3: Emergency Recovery

```python
backup = BackupCore()

# Oh no, broke something!
backup.status()  # See what changed

# Checkout old working version
backup.checkout("yesterday-tag")

# Create recovery branch
backup.branch_create("recovery", "yesterday-tag")
backup.branch_switch("recovery")

# Fix and commit
backup.add(["broken_file.py"])
backup.commit("Fix critical bug")

# Merge fix back
backup.branch_switch("main")
backup.branch_merge("recovery")
```

## ⚙️ Configuration

Configuration is stored in `.aios_backup/config` as JSON.

### Default Configuration

```json
{
  "version": 1,
  "repository": {
    "name": "AIOS Backup",
    "type": "git-like",
    "compression": true,
    "default_branch": "main"
  },
  "author": {
    "name": "AIOS",
    "email": "aios@local"
  },
  "backup": {
    "auto_backup": false,
    "auto_commit": false
  },
  "storage": {
    "compression_level": 6,
    "deduplicate": true,
    "max_history": null
  }
}
```

### Customize Configuration

```python
backup = BackupCore()

# Set author info
backup.config.set("author.name", "Travis")
backup.config.set("author.email", "travis@aios")

# Change default branch
backup.config.set("repository.default_branch", "master")

# Save changes
backup.config.save()
```

## 🔍 Ignore Patterns

Create `.backupignore` in workspace root to exclude files:

```
# Python
__pycache__
*.pyc
*.pyo

# Logs
*.log

# Build artifacts
*.zip
*.tar.gz

# System files
.DS_Store
Thumbs.db
```

## 🐛 Troubleshooting

### Issue: "No commits yet"
**Solution**: Create your first commit:
```python
backup.add(all_files=True)
backup.commit("Initial commit")
```

### Issue: "Branch already exists"
**Solution**: Switch to existing branch or use different name:
```python
backup.branch_switch("existing-branch")
```

### Issue: "Cannot switch - staged changes"
**Solution**: Commit or unstage changes first:
```python
backup.commit("Save work before switching")
# OR
backup.unstage_all()
```

### Issue: Rust implementation not available
**Solution**: This is normal - Python implementation works fine:
```python
backup.switch_to_python()  # Explicitly use Python
```

## 📊 Performance

Object storage is optimized for:
- **Deduplication**: Identical files stored once
- **Compression**: zlib compression on all objects
- **Sharding**: First 2 hash chars used for directory structure
- **Lazy loading**: Objects loaded on demand

Typical performance:
- Stage 1000 files: ~2-3 seconds
- Create commit: ~0.1 seconds
- List branches: <0.01 seconds
- Show status: ~1-2 seconds

Rust implementation can be 2-10x faster for basic operations.

## 🔒 Data Safety

- All objects are content-addressed (tamper-evident)
- Compressed storage prevents accidental modification
- History is append-only (commits never deleted)
- Branch/tag references can be backed up separately

## 🎓 Git Comparison

| Feature | Git | AIOS Backup | Status |
|---------|-----|-------------|--------|
| Content addressing | SHA-1/SHA-256 | SHA-256 | ✅ |
| Object storage | Blobs, Trees, Commits | Blobs, Trees, Commits | ✅ |
| Branches | ✅ | ✅ | ✅ |
| Tags | ✅ | ✅ | ✅ |
| Staging area | ✅ | ✅ | ✅ |
| Fast-forward merge | ✅ | ✅ | ✅ |
| Three-way merge | ✅ | ❌ | 🚧 Planned |
| Remote repos | ✅ | ❌ | 🚧 Planned |
| Rebase | ✅ | ❌ | 🚧 Future |
| Submodules | ✅ | ❌ | Not planned |

## 🚧 Future Enhancements

- [ ] Three-way merge with conflict resolution
- [ ] Remote repository support (push/pull)
- [ ] Rebase operations
- [ ] Cherry-pick commits
- [ ] Interactive staging
- [ ] Better diff algorithms
- [ ] Rust implementation parity with Python
- [ ] Web UI for browsing history
- [ ] Commit hooks (pre-commit, post-commit)

## 📝 License

Part of the AIOS Clean project. See main project license.

## 👤 Author

AIOS Team - Travis

## 🤝 Contributing

This is part of the AIOS Clean project. Contributions welcome!

---

**Version**: 2.0.0  
**Last Updated**: October 2025

