use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};
use walkdir::WalkDir;
use sha2::{Digest, Sha256};
use hex;
use anyhow::Result;

/*
 * AIOS Backup Core - Rust Implementation
 * 
 * High-performance backup system with Git-like features
 * Provides basic backup operations with significant performance improvements
 * 
 * Note: This is the foundational Rust implementation. Full Git-like features
 * (branching, staging, etc.) are currently Python-only but can be ported here.
 */

/// Python-compatible backup result
/// 
/// Returned to Python layer after backup operations
#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct BackupResult {
    #[pyo3(get)]
    pub success: bool,
    #[pyo3(get)]
    pub files_processed: u32,
    #[pyo3(get)]
    pub files_changed: u32,
    #[pyo3(get)]
    pub time_taken_ms: u64,
    #[pyo3(get)]
    pub backup_path: String,
    #[pyo3(get)]
    pub error_message: Option<String>,
}

/// File metadata for tracking changes
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FileMetadata {
    pub path: String,
    pub checksum: String,
    pub size: u64,
    pub modified_time: u64,
}

/// Rust implementation of AIOS Backup Core
/// 
/// Provides high-performance backup operations with:
/// - SHA256-based change detection
/// - Incremental backups (only changed files)
/// - Archive management
/// - Checksum tracking
/// 
/// Compatible with Python implementation via PyO3 bindings
pub struct RustBackupCore {
    backup_dir: PathBuf,
    active_backup_dir: PathBuf,
    archive_backup_dir: PathBuf,
    file_checksums: HashMap<String, String>,
    last_backup_timestamp: u64,
}

impl RustBackupCore {
    /// Initialize the Rust backup core
    pub fn new(backup_dir: &str) -> Result<Self> {
        let backup_path = PathBuf::from(backup_dir);
        let active_backup = backup_path.join("active_backup");
        let archive_backup = backup_path.join("archive_backup");

        // Create directories
        fs::create_dir_all(&active_backup)?;
        fs::create_dir_all(&archive_backup)?;

        // Load existing checksums
        let checksums_file = backup_path.join("file_checksums.json");
        let file_checksums = if checksums_file.exists() {
            let content = fs::read_to_string(&checksums_file)?;
            serde_json::from_str(&content).unwrap_or_default()
        } else {
            HashMap::new()
        };

        // Load last backup timestamp
        let timestamp_file = backup_path.join("backup_tracking.json");
        let last_backup_timestamp = if timestamp_file.exists() {
            let content = fs::read_to_string(&timestamp_file)?;
            let data: serde_json::Value = serde_json::from_str(&content)?;
            data.get("last_backup_timestamp")
                .and_then(|v| v.as_u64())
                .unwrap_or(0)
        } else {
            0
        };

        Ok(Self {
            backup_dir: backup_path,
            active_backup_dir: active_backup,
            archive_backup_dir: archive_backup,
            file_checksums,
            last_backup_timestamp,
        })
    }

    /// Create/update backup with Git-like incremental behavior
    pub fn create_backup(
        &mut self,
        include_data: bool,
        include_logs: bool,
        include_config: bool,
    ) -> Result<BackupResult> {
        let start_time = SystemTime::now();

        // Get files to backup
        let files_to_backup = self.get_files_to_backup(include_data, include_logs, include_config)?;
        
        // Get changed files
        let changed_files = self.get_changed_files(&files_to_backup)?;
        
        // Archive changed files (Git-like: clear archive and create fresh)
        if !changed_files.is_empty() {
            self.archive_changed_files(&changed_files)?;
        }

        // Update active backup
        self.update_active_backup(&files_to_backup)?;

        // Update checksums and tracking
        self.update_file_checksums(&files_to_backup)?;
        self.update_backup_timestamp()?;

        let elapsed = start_time.elapsed()?.as_millis() as u64;

        Ok(BackupResult {
            success: true,
            files_processed: files_to_backup.len() as u32,
            files_changed: changed_files.len() as u32,
            time_taken_ms: elapsed,
            backup_path: self.active_backup_dir.to_string_lossy().to_string(),
            error_message: None,
        })
    }

    /// Get list of files to backup
    fn get_files_to_backup(
        &self,
        include_data: bool,
        include_logs: bool,
        include_config: bool,
    ) -> Result<Vec<PathBuf>> {
        let mut files = Vec::new();
        let current_dir = std::env::current_dir()?;

        // Core directories to backup (exclude backup_core to avoid recursion)
        let core_dirs = vec![
            "carma_core",
            "data_core", 
            "dream_core",
            "enterprise_core",
            "luna_core",
            "streamlit_core",
            "support_core",
            "utils_core",
        ];

        // Add core files
        for core_dir in core_dirs {
            let dir_path = current_dir.join(core_dir);
            if dir_path.exists() {
                for entry in WalkDir::new(&dir_path) {
                    let entry = entry?;
                    if entry.file_type().is_file() {
                        let path = entry.path();
                        // Skip problematic directories
                        if path.components().any(|c| {
                            matches!(c, std::path::Component::Normal(s) if 
                                s == ".git" || s == "__pycache__" || 
                                s == ".pytest_cache" || s == "node_modules")
                        }) {
                            continue;
                        }
                        files.push(path.to_path_buf());
                    }
                }
            }
        }

        // Add main files
        let main_files = vec!["main.py", "requirements.txt", "README.md"];
        for main_file in main_files {
            let file_path = current_dir.join(main_file);
            if file_path.exists() {
                files.push(file_path);
            }
        }

        // Add conditional directories
        if include_config {
            let config_dir = current_dir.join("config");
            if config_dir.exists() {
                for entry in WalkDir::new(&config_dir) {
                    let entry = entry?;
                    if entry.file_type().is_file() {
                        files.push(entry.path().to_path_buf());
                    }
                }
            }
        }

        if include_logs {
            let log_dir = current_dir.join("log");
            if log_dir.exists() {
                for entry in WalkDir::new(&log_dir) {
                    let entry = entry?;
                    if entry.file_type().is_file() {
                        files.push(entry.path().to_path_buf());
                    }
                }
            }
        }

        Ok(files)
    }

    /// Get list of changed files
    fn get_changed_files(&self, files_to_backup: &[PathBuf]) -> Result<Vec<PathBuf>> {
        let mut changed_files = Vec::new();

        for file_path in files_to_backup {
            let current_checksum = self.calculate_file_checksum(file_path)?;
            let path_str = file_path.to_string_lossy().to_string();
            let stored_checksum = self.file_checksums.get(&path_str);

            if stored_checksum != Some(&current_checksum) {
                changed_files.push(file_path.clone());
            }
        }

        Ok(changed_files)
    }

    /// Archive changed files (Git-like: clear and recreate archive)
    fn archive_changed_files(&self, changed_files: &[PathBuf]) -> Result<()> {
        // Clear existing archive (Git-like behavior)
        if self.archive_backup_dir.exists() {
            fs::remove_dir_all(&self.archive_backup_dir)?;
        }
        fs::create_dir_all(&self.archive_backup_dir)?;

        let current_dir = std::env::current_dir()?;

        for file_path in changed_files {
            // Get relative path
            let relative_path = match file_path.strip_prefix(&current_dir) {
                Ok(rel) => rel,
                Err(_) => continue, // Skip files outside project directory
            };

            let archive_file_path = self.archive_backup_dir.join(relative_path);
            let active_backup_file = self.active_backup_dir.join(relative_path);

            // Create directory structure
            if let Some(parent) = archive_file_path.parent() {
                fs::create_dir_all(parent)?;
            }

            // Copy old version from active backup to archive
            if active_backup_file.exists() {
                fs::copy(&active_backup_file, &archive_file_path)?;
            }
        }

        Ok(())
    }

    /// Update active backup with current files
    fn update_active_backup(&self, files_to_backup: &[PathBuf]) -> Result<()> {
        let current_dir = std::env::current_dir()?;

        for file_path in files_to_backup {
            // Get relative path
            let relative_path = match file_path.strip_prefix(&current_dir) {
                Ok(rel) => rel,
                Err(_) => continue, // Skip files outside project directory
            };

            let backup_file_path = self.active_backup_dir.join(relative_path);

            // Create directory structure
            if let Some(parent) = backup_file_path.parent() {
                fs::create_dir_all(parent)?;
            }

            // Copy file to backup
            fs::copy(file_path, &backup_file_path)?;
        }

        Ok(())
    }

    /// Calculate SHA256 checksum of a file
    fn calculate_file_checksum(&self, file_path: &Path) -> Result<String> {
        let content = fs::read(file_path)?;
        let mut hasher = Sha256::new();
        hasher.update(&content);
        Ok(hex::encode(hasher.finalize()))
    }

    /// Update file checksums
    fn update_file_checksums(&mut self, files_to_backup: &[PathBuf]) -> Result<()> {
        for file_path in files_to_backup {
            let checksum = self.calculate_file_checksum(file_path)?;
            let path_str = file_path.to_string_lossy().to_string();
            self.file_checksums.insert(path_str, checksum);
        }

        // Save checksums to file
        let checksums_file = self.backup_dir.join("file_checksums.json");
        let content = serde_json::to_string_pretty(&self.file_checksums)?;
        fs::write(checksums_file, content)?;

        Ok(())
    }

    /// Update backup timestamp
    fn update_backup_timestamp(&mut self) -> Result<()> {
        self.last_backup_timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)?
            .as_secs();

        let tracking_data = serde_json::json!({
            "last_backup_timestamp": self.last_backup_timestamp,
            "backup_count": self.file_checksums.len()
        });

        let tracking_file = self.backup_dir.join("backup_tracking.json");
        let content = serde_json::to_string_pretty(&tracking_data)?;
        fs::write(tracking_file, content)?;

        Ok(())
    }
}

/// Python module interface
/// 
/// Exports Rust backup functionality to Python via PyO3
/// 
/// Available classes:
/// - BackupResult: Result of backup operations
/// - PyRustBackupCore: Main backup interface
/// 
/// Future enhancements planned:
/// - Object storage implementation (Git-like blobs/trees/commits)
/// - Branching support
/// - Staging area
/// - Diff engine
#[pymodule]
fn aios_backup_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<BackupResult>()?;
    m.add_class::<PyRustBackupCore>()?;
    Ok(())
}

/// Python wrapper for RustBackupCore
#[pyclass]
pub struct PyRustBackupCore {
    core: RustBackupCore,
}

#[pymethods]
impl PyRustBackupCore {
    #[new]
    fn new(backup_dir: &str) -> PyResult<Self> {
        let core = RustBackupCore::new(backup_dir)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to initialize backup core: {}", e)))?;
        Ok(Self { core })
    }

    fn create_backup(
        &mut self,
        include_data: bool,
        include_logs: bool,
        include_config: bool,
    ) -> PyResult<BackupResult> {
        match self.core.create_backup(include_data, include_logs, include_config) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Backup failed: {}", e)))
        }
    }
}
