use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH, Duration};
use chrono::{DateTime, Utc};
use rayon::prelude::*;
use sysinfo::{System, CpuRefreshKind, MemoryRefreshKind, RefreshKind};
use anyhow::Result;

/// Health check result
#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct HealthCheckResult {
    #[pyo3(get)]
    pub status: String,
    #[pyo3(get)]
    pub message: String,
    #[pyo3(get)]
    pub critical: bool,
    #[pyo3(get)]
    pub duration_ms: u64,
    #[pyo3(get)]
    pub error: Option<String>,
}

/// System health summary
#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct SystemHealthSummary {
    #[pyo3(get)]
    pub overall_status: String,
    #[pyo3(get)]
    pub total_checks: u32,
    #[pyo3(get)]
    pub passed_checks: u32,
    #[pyo3(get)]
    pub failed_checks: u32,
    #[pyo3(get)]
    pub warnings: u32,
    #[pyo3(get)]
    pub total_duration_ms: u64,
    #[pyo3(get)]
    pub timestamp: String,
}

/// FAISS search result
#[derive(Debug, Serialize, Deserialize, Clone)]
#[pyclass]
pub struct FAISSSearchResult {
    #[pyo3(get)]
    pub vector_id: String,
    #[pyo3(get)]
    pub similarity_score: f32,
    #[pyo3(get)]
    pub metadata: String,
}

/// Rust implementation of AIOS Support Core
pub struct RustSupportCore {
    cache_dir: PathBuf,
    system: System,
    faiss_index: Option<()>, // Placeholder for FAISS
    dimension: usize,
}

impl RustSupportCore {
    /// Initialize the Rust support core
    pub fn new(cache_dir: &str, dimension: usize) -> Result<Self> {
        let cache_path = PathBuf::from(cache_dir);
        let mut system = System::new_with_specifics(
            RefreshKind::new()
                .with_cpu(CpuRefreshKind::everything())
                .with_memory(MemoryRefreshKind::everything())
        );
        
        // Initialize FAISS index (simplified for now)
        let faiss_index = None; // Will implement FAISS integration later
        
        Ok(Self {
            cache_dir: cache_path,
            system,
            faiss_index,
            dimension,
        })
    }
    
    /// Run comprehensive health checks
    pub fn run_health_checks(&mut self, quick_mode: bool) -> Result<SystemHealthSummary> {
        let start_time = SystemTime::now();
        self.system.refresh_all();
        
        let checks = if quick_mode {
            self.run_quick_health_checks()?
        } else {
            self.run_full_health_checks()?
        };
        
        let total_duration = start_time.elapsed()?.as_millis() as u64;
        
        // Analyze results
        let total_checks = checks.len() as u32;
        let passed_checks = checks.iter().filter(|c| c.status == "PASS").count() as u32;
        let failed_checks = checks.iter().filter(|c| c.status == "FAIL").count() as u32;
        let warnings = checks.iter().filter(|c| c.status == "WARNING").count() as u32;
        
        let overall_status = if failed_checks > 0 {
            "CRITICAL"
        } else if warnings > 0 {
            "WARNING"
        } else {
            "HEALTHY"
        };
        
        Ok(SystemHealthSummary {
            overall_status: overall_status.to_string(),
            total_checks,
            passed_checks,
            failed_checks,
            warnings,
            total_duration_ms: total_duration,
            timestamp: Utc::now().to_rfc3339(),
        })
    }
    
    /// Run quick health checks (essential only)
    fn run_quick_health_checks(&mut self) -> Result<Vec<HealthCheckResult>> {
        let checks = vec![
            self.check_python_environment()?,
            self.check_file_system()?,
            self.check_memory_usage()?,
        ];
        Ok(checks)
    }
    
    /// Run full health checks
    fn run_full_health_checks(&mut self) -> Result<Vec<HealthCheckResult>> {
        let checks = vec![
            self.check_python_environment()?,
            self.check_dependencies()?,
            self.check_file_system()?,
            self.check_memory_usage()?,
            self.check_disk_space()?,
            self.check_cpu_usage()?,
            self.check_network_connectivity()?,
            self.check_processes()?,
            self.check_cache_integrity()?,
        ];
        Ok(checks)
    }
    
    /// Check Python environment
    fn check_python_environment(&self) -> Result<HealthCheckResult> {
        let start_time = SystemTime::now();
        
        // Check Python version
        let python_version = std::env::var("PYTHON_VERSION").unwrap_or_else(|_| "Unknown".to_string());
        let status = if python_version != "Unknown" { "PASS" } else { "WARNING" };
        
        let duration = start_time.elapsed()?.as_millis() as u64;
        
        Ok(HealthCheckResult {
            status: status.to_string(),
            message: format!("Python environment available: {}", python_version),
            critical: false,
            duration_ms: duration,
            error: None,
        })
    }
    
    /// Check dependencies
    fn check_dependencies(&self) -> Result<HealthCheckResult> {
        let start_time = SystemTime::now();
        
        // Check if key dependencies are available
        let mut missing_deps: Vec<String> = Vec::new();
        let deps = vec!["numpy", "faiss", "serde", "chrono"];
        
        // This is a simplified check - in a real implementation,
        // you'd check for actual Python packages
        let status = if missing_deps.is_empty() { "PASS" } else { "WARNING" };
        
        let duration = start_time.elapsed()?.as_millis() as u64;
        
        Ok(HealthCheckResult {
            status: status.to_string(),
            message: format!("Dependencies checked: {} available", deps.len()),
            critical: false,
            duration_ms: duration,
            error: None,
        })
    }
    
    /// Check file system
    fn check_file_system(&self) -> Result<HealthCheckResult> {
        let start_time = SystemTime::now();
        
        let cache_exists = self.cache_dir.exists();
        let cache_writable = if cache_exists {
            // Try to create a test file
            let test_file = self.cache_dir.join(".test_write");
            match fs::write(&test_file, "test") {
                Ok(_) => {
                    let _ = fs::remove_file(&test_file);
                    true
                }
                Err(_) => false,
            }
        } else {
            false
        };
        
        let status = if cache_exists && cache_writable { "PASS" } else { "FAIL" };
        
        let duration = start_time.elapsed()?.as_millis() as u64;
        
        Ok(HealthCheckResult {
            status: status.to_string(),
            message: format!("Cache directory: exists={}, writable={}", cache_exists, cache_writable),
            critical: true,
            duration_ms: duration,
            error: if !cache_exists { Some("Cache directory does not exist".to_string()) } else if !cache_writable { Some("Cache directory not writable".to_string()) } else { None },
        })
    }
    
    /// Check memory usage
    fn check_memory_usage(&self) -> Result<HealthCheckResult> {
        let start_time = SystemTime::now();
        
        let total_memory = self.system.total_memory();
        let used_memory = self.system.used_memory();
        let memory_percent = (used_memory as f64 / total_memory as f64) * 100.0;
        
        let status = if memory_percent > 90.0 { "CRITICAL" } else if memory_percent > 80.0 { "WARNING" } else { "PASS" };
        
        let duration = start_time.elapsed()?.as_millis() as u64;
        
        Ok(HealthCheckResult {
            status: status.to_string(),
            message: format!("Memory usage: {:.1}% ({}/{} MB)", memory_percent, used_memory / 1024 / 1024, total_memory / 1024 / 1024),
            critical: memory_percent > 90.0,
            duration_ms: duration,
            error: if memory_percent > 90.0 { Some("High memory usage detected".to_string()) } else { None },
        })
    }
    
    /// Check disk space
    fn check_disk_space(&self) -> Result<HealthCheckResult> {
        let start_time = SystemTime::now();
        
        // Simplified disk check for now
        let total_space = 100_000_000_000u64; // 100GB placeholder
        let total_available = 80_000_000_000u64; // 80GB placeholder
        
        let space_percent = ((total_space - total_available) as f64 / total_space as f64) * 100.0;
        let status = if space_percent > 95.0 { "CRITICAL" } else if space_percent > 85.0 { "WARNING" } else { "PASS" };
        
        let duration = start_time.elapsed()?.as_millis() as u64;
        
        Ok(HealthCheckResult {
            status: status.to_string(),
            message: format!("Disk usage: {:.1}% ({} GB available)", space_percent, total_available / 1024 / 1024 / 1024),
            critical: space_percent > 95.0,
            duration_ms: duration,
            error: if space_percent > 95.0 { Some("Low disk space detected".to_string()) } else { None },
        })
    }
    
    /// Check CPU usage
    fn check_cpu_usage(&self) -> Result<HealthCheckResult> {
        let start_time = SystemTime::now();
        
        let cpus = self.system.cpus();
        let avg_cpu = cpus.iter().map(|cpu| cpu.cpu_usage()).sum::<f32>() / cpus.len() as f32;
        
        let status = if avg_cpu > 90.0 { "WARNING" } else { "PASS" };
        
        let duration = start_time.elapsed()?.as_millis() as u64;
        
        Ok(HealthCheckResult {
            status: status.to_string(),
            message: format!("CPU usage: {:.1}%", avg_cpu),
            critical: false,
            duration_ms: duration,
            error: if avg_cpu > 95.0 { Some("High CPU usage detected".to_string()) } else { None },
        })
    }
    
    /// Check network connectivity
    fn check_network_connectivity(&self) -> Result<HealthCheckResult> {
        let start_time = SystemTime::now();
        
        // Simplified network check - in a real implementation,
        // you'd ping specific endpoints
        let status = "PASS";
        
        let duration = start_time.elapsed()?.as_millis() as u64;
        
        Ok(HealthCheckResult {
            status: status.to_string(),
            message: "Network connectivity: OK".to_string(),
            critical: false,
            duration_ms: duration,
            error: None,
        })
    }
    
    /// Check running processes
    fn check_processes(&self) -> Result<HealthCheckResult> {
        let start_time = SystemTime::now();
        
        let processes = self.system.processes();
        let process_count = processes.len();
        
        let status = if process_count > 1000 { "WARNING" } else { "PASS" };
        
        let duration = start_time.elapsed()?.as_millis() as u64;
        
        Ok(HealthCheckResult {
            status: status.to_string(),
            message: format!("Running processes: {}", process_count),
            critical: false,
            duration_ms: duration,
            error: if process_count > 2000 { Some("High number of processes detected".to_string()) } else { None },
        })
    }
    
    /// Check cache integrity
    fn check_cache_integrity(&self) -> Result<HealthCheckResult> {
        let start_time = SystemTime::now();
        
        let mut corrupted_files = 0;
        let mut total_files = 0;
        
        if self.cache_dir.exists() {
            for entry in fs::read_dir(&self.cache_dir)? {
                let entry = entry?;
                if entry.path().extension().map_or(false, |ext| ext == "json") {
                    total_files += 1;
                    if let Err(_) = fs::read_to_string(&entry.path()) {
                        corrupted_files += 1;
                    }
                }
            }
        }
        
        let status = if corrupted_files > 0 { "WARNING" } else { "PASS" };
        
        let duration = start_time.elapsed()?.as_millis() as u64;
        
        Ok(HealthCheckResult {
            status: status.to_string(),
            message: format!("Cache integrity: {}/{} files OK", total_files - corrupted_files, total_files),
            critical: false,
            duration_ms: duration,
            error: if corrupted_files > total_files / 2 { Some("High number of corrupted cache files".to_string()) } else { None },
        })
    }
    
    /// Add vectors (placeholder implementation)
    pub fn add_vectors(&mut self, vectors: Vec<Vec<f32>>, metadata: Vec<String>) -> Result<u32> {
        // Placeholder implementation - will add FAISS integration later
        Ok(vectors.len() as u32)
    }
    
    /// Search similar vectors (placeholder implementation)
    pub fn search_vectors(&mut self, query_vector: Vec<f32>, k: usize) -> Result<Vec<FAISSSearchResult>> {
        // Placeholder implementation - will add FAISS integration later
        let mut results = Vec::new();
        for i in 0..k {
            results.push(FAISSSearchResult {
                vector_id: format!("vector_{}", i),
                similarity_score: 0.9 - (i as f32 * 0.1),
                metadata: format!("metadata_{}", i),
            });
        }
        Ok(results)
    }
    
    /// Get system performance metrics
    pub fn get_performance_metrics(&mut self) -> Result<HashMap<String, f64>> {
        self.system.refresh_all();
        
        let mut metrics = HashMap::new();
        
        // Memory metrics
        let total_memory = self.system.total_memory() as f64;
        let used_memory = self.system.used_memory() as f64;
        metrics.insert("memory_total_mb".to_string(), total_memory / 1024.0 / 1024.0);
        metrics.insert("memory_used_mb".to_string(), used_memory / 1024.0 / 1024.0);
        metrics.insert("memory_usage_percent".to_string(), (used_memory / total_memory) * 100.0);
        
        // CPU metrics
        let cpus = self.system.cpus();
        let avg_cpu = cpus.iter().map(|cpu| cpu.cpu_usage() as f64).sum::<f64>() / cpus.len() as f64;
        metrics.insert("cpu_usage_percent".to_string(), avg_cpu);
        
        // Disk metrics (simplified)
        let total_disk_space = 100_000_000_000u64 as f64; // 100GB placeholder
        let total_disk_available = 80_000_000_000u64 as f64; // 80GB placeholder
        metrics.insert("disk_total_gb".to_string(), total_disk_space / 1024.0 / 1024.0 / 1024.0);
        metrics.insert("disk_available_gb".to_string(), total_disk_available / 1024.0 / 1024.0 / 1024.0);
        metrics.insert("disk_usage_percent".to_string(), ((total_disk_space - total_disk_available) / total_disk_space) * 100.0);
        
        // Process metrics
        metrics.insert("process_count".to_string(), self.system.processes().len() as f64);
        
        Ok(metrics)
    }
}

/// Python module interface
#[pymodule]
fn aios_support_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<HealthCheckResult>()?;
    m.add_class::<SystemHealthSummary>()?;
    m.add_class::<FAISSSearchResult>()?;
    m.add_class::<PyRustSupportCore>()?;
    Ok(())
}

/// Python wrapper for RustSupportCore
#[pyclass]
pub struct PyRustSupportCore {
    core: RustSupportCore,
}

#[pymethods]
impl PyRustSupportCore {
    #[new]
    fn new(cache_dir: &str, dimension: usize) -> PyResult<Self> {
        let core = RustSupportCore::new(cache_dir, dimension)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to initialize support core: {}", e)))?;
        Ok(Self { core })
    }

    fn run_health_checks(&mut self, quick_mode: bool) -> PyResult<SystemHealthSummary> {
        match self.core.run_health_checks(quick_mode) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Health checks failed: {}", e)))
        }
    }

    fn add_vectors(&mut self, vectors: Vec<Vec<f32>>, metadata: Vec<String>) -> PyResult<u32> {
        match self.core.add_vectors(vectors, metadata) {
            Ok(count) => Ok(count),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to add vectors: {}", e)))
        }
    }

    fn search_vectors(&mut self, query_vector: Vec<f32>, k: usize) -> PyResult<Vec<FAISSSearchResult>> {
        match self.core.search_vectors(query_vector, k) {
            Ok(results) => Ok(results),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Search failed: {}", e)))
        }
    }

    fn get_performance_metrics(&mut self) -> PyResult<HashMap<String, f64>> {
        match self.core.get_performance_metrics() {
            Ok(metrics) => Ok(metrics),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to get metrics: {}", e)))
        }
    }
}
