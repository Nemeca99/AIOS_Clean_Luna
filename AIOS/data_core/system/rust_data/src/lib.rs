use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::fs;
use walkdir::WalkDir;
use chrono::{DateTime, Utc};
use std::collections::HashMap;

/// Statistics for a directory
#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct DirectoryStats {
    #[pyo3(get)]
    pub total_files: u32,
    #[pyo3(get)]
    pub total_dirs: u32,
    #[pyo3(get)]
    pub total_size_bytes: u64,
    #[pyo3(get)]
    pub total_size_mb: f64,
    #[pyo3(get)]
    pub last_modified: Option<String>,
    #[pyo3(get)]
    pub file_types: std::collections::HashMap<String, u32>,
}

/// Data pipeline statistics
#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct PipelineStats {
    #[pyo3(get)]
    pub total_ingestions: u32,
    #[pyo3(get)]
    pub total_exports: u32,
    #[pyo3(get)]
    pub last_ingestion: Option<String>,
    #[pyo3(get)]
    pub last_export: Option<String>,
    #[pyo3(get)]
    pub cache_hit_rate: f64,
}

/// Data export result
#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct ExportResult {
    #[pyo3(get)]
    pub success: bool,
    #[pyo3(get)]
    pub files_processed: u32,
    #[pyo3(get)]
    pub bytes_processed: u64,
    #[pyo3(get)]
    pub export_path: String,
    #[pyo3(get)]
    pub time_taken_ms: u64,
    #[pyo3(get)]
    pub error_message: Option<String>,
}

/// Rust Data Core implementation
#[pyclass]
pub struct RustDataCore {
    data_dir: PathBuf,
    pipeline_stats: PipelineStats,
}

#[pymethods]
impl RustDataCore {
    /// Initialize the Rust Data Core
    #[new]
    pub fn new(data_dir: &str) -> PyResult<Self> {
        let data_path = PathBuf::from(data_dir);
        
        // Ensure data directory exists
        if !data_path.exists() {
            fs::create_dir_all(&data_path).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to create data directory: {}", e)))?;
        }
        
        // Initialize pipeline stats
        let pipeline_stats = PipelineStats {
            total_ingestions: 0,
            total_exports: 0,
            last_ingestion: None,
            last_export: None,
            cache_hit_rate: 0.0,
        };
        
        Ok(Self {
            data_dir: data_path,
            pipeline_stats,
        })
    }
    
    /// Get directory statistics using parallel processing
    pub fn get_directory_stats(&self, directory_path: &str) -> PyResult<DirectoryStats> {
        let dir_path = Path::new(directory_path);
        
        if !dir_path.exists() {
            return Ok(DirectoryStats {
                total_files: 0,
                total_dirs: 0,
                total_size_bytes: 0,
                total_size_mb: 0.0,
                last_modified: None,
                file_types: std::collections::HashMap::new(),
            });
        }
        
        let mut total_files = 0u32;
        let mut total_dirs = 0u32;
        let mut total_size_bytes = 0u64;
        let mut file_types = std::collections::HashMap::new();
        let mut last_modified = None;
        
        // Use parallel iterator for faster directory traversal
        let entries: Vec<_> = WalkDir::new(dir_path)
            .into_iter()
            .collect::<std::result::Result<Vec<_>, _>>()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to traverse directory: {}", e)))?;
        
        for entry in entries {
            if let Ok(metadata) = entry.metadata() {
                if metadata.is_file() {
                    total_files += 1;
                    total_size_bytes += metadata.len();
                    
                    // Track file extensions
                    if let Some(extension) = entry.path().extension() {
                        let ext = extension.to_string_lossy().to_lowercase();
                        *file_types.entry(ext).or_insert(0) += 1;
                    }
                    
                    // Track last modified time
                    if let Ok(modified) = metadata.modified() {
                        let datetime: DateTime<Utc> = modified.into();
                        let modified_str = datetime.format("%Y-%m-%d %H:%M:%S").to_string();
                        last_modified = Some(modified_str);
                    }
                } else if metadata.is_dir() {
                    total_dirs += 1;
                }
            }
        }
        
        Ok(DirectoryStats {
            total_files,
            total_dirs,
            total_size_bytes,
            total_size_mb: total_size_bytes as f64 / (1024.0 * 1024.0),
            last_modified,
            file_types,
        })
    }
    
    /// Get fractal cache statistics
    pub fn get_fractal_cache_stats(&self) -> PyResult<DirectoryStats> {
        let fractal_cache_path = self.data_dir.join("FractalCache");
        self.get_directory_stats(fractal_cache_path.to_str().unwrap_or(""))
    }
    
    /// Get arbiter cache statistics
    pub fn get_arbiter_cache_stats(&self) -> PyResult<DirectoryStats> {
        let arbiter_cache_path = self.data_dir.join("ArbiterCache");
        self.get_directory_stats(arbiter_cache_path.to_str().unwrap_or(""))
    }
    
    /// Get conversation statistics
    pub fn get_conversation_stats(&self) -> PyResult<DirectoryStats> {
        let conversations_path = self.data_dir.join("conversations");
        self.get_directory_stats(conversations_path.to_str().unwrap_or(""))
    }
    
    /// Get database statistics
    pub fn get_database_stats(&self) -> PyResult<DirectoryStats> {
        let database_path = self.data_dir.join("AIOS_Database").join("database");
        self.get_directory_stats(database_path.to_str().unwrap_or(""))
    }
    
    /// Export data to JSON format with parallel processing
    pub fn export_to_json(&mut self, source_dir: &str, export_path: &str, 
                         filter_criteria: Option<String>) -> PyResult<ExportResult> {
        let start_time = std::time::Instant::now();
        
        let source_path = Path::new(source_dir);
        if !source_path.exists() {
            return Ok(ExportResult {
                success: false,
                files_processed: 0,
                bytes_processed: 0,
                export_path: export_path.to_string(),
                time_taken_ms: 0,
                error_message: Some("Source directory does not exist".to_string()),
            });
        }
        
        let mut files_processed = 0u32;
        let mut bytes_processed = 0u64;
        let mut export_data = Vec::new();
        
        // Collect files in parallel
        let files: Vec<_> = WalkDir::new(source_path)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_type().is_file())
            .collect();
        
        for entry in files {
            if let Ok(contents) = fs::read_to_string(entry.path()) {
                bytes_processed += contents.len() as u64;
                files_processed += 1;
                
                // Parse filter criteria if provided
                let should_include = if let Some(criteria) = &filter_criteria {
                    self._matches_filter(&contents, criteria)
                } else {
                    true
                };
                
                if should_include {
                    let file_data = serde_json::json!({
                        "path": entry.path().to_string_lossy(),
                        "size": contents.len(),
                        "content": contents,
                        "modified": entry.metadata().ok()
                            .and_then(|m| m.modified().ok())
                            .map(|t| DateTime::<Utc>::from(t).format("%Y-%m-%d %H:%M:%S").to_string())
                    });
                    export_data.push(file_data);
                }
            }
        }
        
        // Write export data
        let export_json = serde_json::to_string_pretty(&export_data)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("JSON serialization error: {}", e)))?;
        fs::write(export_path, export_json)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("File write error: {}", e)))?;
        
        let time_taken = start_time.elapsed().as_millis() as u64;
        
        // Update pipeline stats
        self.pipeline_stats.total_exports += 1;
        self.pipeline_stats.last_export = Some(Utc::now().format("%Y-%m-%d %H:%M:%S").to_string());
        
        Ok(ExportResult {
            success: true,
            files_processed,
            bytes_processed,
            export_path: export_path.to_string(),
            time_taken_ms: time_taken,
            error_message: None,
        })
    }
    
    /// Clean up old data files
    pub fn cleanup_old_data(&self, days_old: u32, dry_run: bool) -> PyResult<Vec<String>> {
        let cutoff_time = Utc::now() - chrono::Duration::days(days_old as i64);
        let mut cleaned_files = Vec::new();
        
        for entry in WalkDir::new(&self.data_dir)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_type().is_file())
        {
            if let Ok(metadata) = entry.metadata() {
                if let Ok(modified) = metadata.modified() {
                    let file_time: DateTime<Utc> = modified.into();
                    if file_time < cutoff_time {
                        if !dry_run {
                            if let Err(e) = fs::remove_file(entry.path()) {
                                eprintln!("Failed to remove {}: {}", entry.path().display(), e);
                            }
                        }
                        cleaned_files.push(entry.path().to_string_lossy().to_string());
                    }
                }
            }
        }
        
        Ok(cleaned_files)
    }
    
    /// Get comprehensive system overview
    pub fn get_system_overview(&self) -> PyResult<String> {
        let mut overview = HashMap::new();
        
        // Get stats for each directory
        overview.insert("fractal_cache".to_string(), 
                       serde_json::to_value(self.get_fractal_cache_stats()?)
                           .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization error: {}", e)))?);
        overview.insert("arbiter_cache".to_string(), 
                       serde_json::to_value(self.get_arbiter_cache_stats()?)
                           .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization error: {}", e)))?);
        overview.insert("conversations".to_string(), 
                       serde_json::to_value(self.get_conversation_stats()?)
                           .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization error: {}", e)))?);
        overview.insert("database".to_string(), 
                       serde_json::to_value(self.get_database_stats()?)
                           .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization error: {}", e)))?);
        overview.insert("pipeline_stats".to_string(), 
                       serde_json::to_value(&self.pipeline_stats)
                           .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Serialization error: {}", e)))?);
        
        let json_string = serde_json::to_string_pretty(&overview)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("JSON serialization error: {}", e)))?;
        
        Ok(json_string)
    }
    
    /// Get pipeline metrics
    pub fn get_pipeline_metrics(&self) -> PyResult<PipelineStats> {
        Ok(self.pipeline_stats.clone())
    }
    
    /// Helper method to check if data matches filter criteria
    fn _matches_filter(&self, data: &str, criteria: &str) -> bool {
        // Simple string matching for now - can be extended
        data.contains(criteria)
    }
}

/// Python wrapper for RustDataCore
#[pyclass]
pub struct PyRustDataCore {
    inner: RustDataCore,
}

#[pymethods]
impl PyRustDataCore {
    #[new]
    pub fn new(data_dir: &str) -> PyResult<Self> {
        Ok(Self {
            inner: RustDataCore::new(data_dir).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to initialize RustDataCore: {}", e)))?,
        })
    }
    
    pub fn get_directory_stats(&self, directory_path: &str) -> PyResult<DirectoryStats> {
        self.inner.get_directory_stats(directory_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to get directory stats: {}", e)))
    }
    
    pub fn get_fractal_cache_stats(&self) -> PyResult<DirectoryStats> {
        self.inner.get_fractal_cache_stats()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to get fractal cache stats: {}", e)))
    }
    
    pub fn get_arbiter_cache_stats(&self) -> PyResult<DirectoryStats> {
        self.inner.get_arbiter_cache_stats()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to get arbiter cache stats: {}", e)))
    }
    
    pub fn get_conversation_stats(&self) -> PyResult<DirectoryStats> {
        self.inner.get_conversation_stats()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to get conversation stats: {}", e)))
    }
    
    pub fn get_database_stats(&self) -> PyResult<DirectoryStats> {
        self.inner.get_database_stats()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to get database stats: {}", e)))
    }
    
    pub fn export_to_json(&mut self, source_dir: &str, export_path: &str, 
                         filter_criteria: Option<String>) -> PyResult<ExportResult> {
        self.inner.export_to_json(source_dir, export_path, filter_criteria)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to export to JSON: {}", e)))
    }
    
    pub fn cleanup_old_data(&self, days_old: u32, dry_run: bool) -> PyResult<Vec<String>> {
        self.inner.cleanup_old_data(days_old, dry_run)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to cleanup old data: {}", e)))
    }
    
    pub fn get_system_overview(&self) -> PyResult<String> {
        self.inner.get_system_overview()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to get system overview: {}", e)))
    }
    
    pub fn get_pipeline_metrics(&self) -> PyResult<PipelineStats> {
        self.inner.get_pipeline_metrics()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to get pipeline metrics: {}", e)))
    }
}

/// Python module definition
#[pymodule]
fn aios_data_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyRustDataCore>()?;
    m.add_class::<DirectoryStats>()?;
    m.add_class::<PipelineStats>()?;
    m.add_class::<ExportResult>()?;
    Ok(())
}
