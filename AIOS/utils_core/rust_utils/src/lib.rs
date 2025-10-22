use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::{SystemTime, Duration};
use uuid::Uuid;
use chrono::{DateTime, Utc};
use rand::Rng;
use sha2::{Sha256, Digest};
use regex::Regex;
use std::fs;
use std::path::Path;

/// Represents a validation result
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct ValidationResult {
    #[pyo3(get)]
    pub is_valid: bool,
    #[pyo3(get)]
    pub data_type: String,
    #[pyo3(get)]
    pub sanitized_data: String,
    #[pyo3(get)]
    pub warnings: Vec<String>,
    #[pyo3(get)]
    pub timestamp: f64,
}

#[pymethods]
impl ValidationResult {
    #[new]
    fn new(is_valid: bool, data_type: String) -> Self {
        Self {
            is_valid,
            data_type,
            sanitized_data: String::new(),
            warnings: Vec::new(),
            timestamp: SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .unwrap()
                .as_secs_f64(),
        }
    }
}

/// Represents a file operation result
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct FileOperationResult {
    #[pyo3(get)]
    pub success: bool,
    #[pyo3(get)]
    pub file_path: String,
    #[pyo3(get)]
    pub operation: String,
    #[pyo3(get)]
    pub bytes_processed: u64,
    #[pyo3(get)]
    pub hash: String,
    #[pyo3(get)]
    pub timestamp: f64,
}

#[pymethods]
impl FileOperationResult {
    #[new]
    fn new(success: bool, file_path: String, operation: String) -> Self {
        Self {
            success,
            file_path,
            operation,
            bytes_processed: 0,
            hash: String::new(),
            timestamp: SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .unwrap()
                .as_secs_f64(),
        }
    }
}

/// Represents system metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct SystemMetrics {
    #[pyo3(get)]
    pub uptime_seconds: f64,
    #[pyo3(get)]
    pub memory_usage_mb: f64,
    #[pyo3(get)]
    pub disk_usage_percent: f64,
    #[pyo3(get)]
    pub cpu_usage_percent: f64,
    #[pyo3(get)]
    pub active_utilities: u32,
    #[pyo3(get)]
    pub timestamp: f64,
}

#[pymethods]
impl SystemMetrics {
    #[new]
    fn new() -> Self {
        Self {
            uptime_seconds: 0.0,
            memory_usage_mb: 0.0,
            disk_usage_percent: 0.0,
            cpu_usage_percent: 0.0,
            active_utilities: 0,
            timestamp: SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .unwrap()
                .as_secs_f64(),
        }
    }
}

/// Main Utils Rust implementation
#[pyclass]
pub struct RustUtilsCore {
    usage_stats: HashMap<String, u32>,
    utility_registry: HashMap<String, String>,
    file_operations: Vec<FileOperationResult>,
    validation_cache: HashMap<String, ValidationResult>,
    start_time: SystemTime,
}

#[pymethods]
impl RustUtilsCore {
    #[new]
    fn new() -> Self {
        Self {
            usage_stats: HashMap::new(),
            utility_registry: HashMap::new(),
            file_operations: Vec::new(),
            validation_cache: HashMap::new(),
            start_time: SystemTime::now(),
        }
    }

    /// Validate data based on type
    fn validate_data(&mut self, data: String, data_type: String) -> ValidationResult {
        let cache_key = format!("{}:{}", data_type, data);
        
        // Check cache first
        if let Some(cached) = self.validation_cache.get(&cache_key) {
            return cached.clone();
        }
        
        let mut result = ValidationResult::new(true, data_type.clone());
        
        match data_type.as_str() {
            "json" => {
                if let Err(_) = serde_json::from_str::<serde_json::Value>(&data) {
                    result.is_valid = false;
                    result.warnings.push("Invalid JSON format".to_string());
                }
            }
            "email" => {
                let email_regex = Regex::new(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$").unwrap();
                if !email_regex.is_match(&data) {
                    result.is_valid = false;
                    result.warnings.push("Invalid email format".to_string());
                }
            }
            "url" => {
                let url_regex = Regex::new(r"^https?://[^\s/$.?#].[^\s]*$").unwrap();
                if !url_regex.is_match(&data) {
                    result.is_valid = false;
                    result.warnings.push("Invalid URL format".to_string());
                }
            }
            "general" => {
                if data.len() > 10000 {
                    result.warnings.push("Data length exceeds recommended limit".to_string());
                }
            }
            _ => {
                result.warnings.push(format!("Unknown data type: {}", data_type));
            }
        }
        
        result.sanitized_data = self.sanitize_input(&data, 10000);
        
        // Cache the result
        self.validation_cache.insert(cache_key, result.clone());
        
        result
    }

    /// Sanitize input data
    fn sanitize_input(&self, input_data: &str, max_length: usize) -> String {
        let mut sanitized = input_data.to_string();
        
        // Remove null bytes
        sanitized = sanitized.replace('\0', "");
        
        // Remove control characters except newlines and tabs
        sanitized = sanitized.chars()
            .filter(|c| !c.is_control() || *c == '\n' || *c == '\t' || *c == '\r')
            .collect();
        
        // Truncate if too long
        if sanitized.len() > max_length {
            sanitized.truncate(max_length);
            sanitized.push_str("...");
        }
        
        sanitized
    }

    /// Safe file read operation
    fn safe_file_read(&mut self, file_path: String, encoding: String) -> FileOperationResult {
        let mut result = FileOperationResult::new(false, file_path.clone(), "read".to_string());
        
        match fs::read_to_string(&file_path) {
            Ok(content) => {
                result.success = true;
                result.bytes_processed = content.len() as u64;
                result.hash = self.generate_content_hash(&content);
            }
            Err(e) => {
                // Log error but don't panic
                println!("File read error: {}", e);
            }
        }
        
        self.file_operations.push(result.clone());
        result
    }

    /// Safe file write operation
    fn safe_file_write(&mut self, file_path: String, content: String, encoding: String) -> FileOperationResult {
        let mut result = FileOperationResult::new(false, file_path.clone(), "write".to_string());
        
        // Create directory if it doesn't exist
        if let Some(parent) = Path::new(&file_path).parent() {
            if let Err(_) = fs::create_dir_all(parent) {
                return result;
            }
        }
        
        match fs::write(&file_path, &content) {
            Ok(_) => {
                result.success = true;
                result.bytes_processed = content.len() as u64;
                result.hash = self.generate_content_hash(&content);
            }
            Err(e) => {
                println!("File write error: {}", e);
            }
        }
        
        self.file_operations.push(result.clone());
        result
    }

    /// Generate file hash
    fn generate_file_hash(&self, file_path: String, algorithm: String) -> String {
        match fs::read(&file_path) {
            Ok(content) => self.generate_content_hash_bytes(&content, &algorithm),
            Err(_) => String::new()
        }
    }

    /// Generate content hash
    fn generate_content_hash(&self, content: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(content.as_bytes());
        format!("{:x}", hasher.finalize())
    }

    /// Generate content hash with specified algorithm
    fn generate_content_hash_bytes(&self, content: &[u8], algorithm: &str) -> String {
        match algorithm.to_lowercase().as_str() {
            "md5" => {
                // MD5 not available, use SHA256 instead
                let mut hasher = Sha256::new();
                hasher.update(content);
                format!("{:x}", hasher.finalize())
            }
            "sha256" => {
                let mut hasher = Sha256::new();
                hasher.update(content);
                format!("{:x}", hasher.finalize())
            }
            _ => {
                // Default to SHA256
                let mut hasher = Sha256::new();
                hasher.update(content);
                format!("{:x}", hasher.finalize())
            }
        }
    }

    /// Generate content ID
    fn generate_content_id(&self, content: &str, prefix: &str) -> String {
        let hash = self.generate_content_hash(content);
        let timestamp = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        format!("{}_{}_{}", prefix, timestamp, &hash[..8])
    }

    /// Create core message
    fn create_core_message(&self, source_core: &str, target_core: &str, message_type: &str, payload: String) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let message = PyDict::new(py);
            message.set_item("message_id", Uuid::new_v4().to_string())?;
            message.set_item("source_core", source_core)?;
            message.set_item("target_core", target_core)?;
            message.set_item("message_type", message_type)?;
            message.set_item("payload", payload)?;
            message.set_item("timestamp", SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .unwrap()
                .as_secs_f64())?;
            message.set_item("status", "pending")?;
            Ok(message.into())
        })
    }

    /// Validate core message
    fn validate_core_message(&self, message: PyObject) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let validation = PyDict::new(py);
            
            // Try to extract message data
            if let Ok(msg_dict) = message.extract::<&PyDict>(py) {
                let required_fields = ["message_id", "source_core", "target_core", "message_type", "payload"];
                let mut is_valid = true;
                let mut missing_fields = Vec::new();
                
                for field in required_fields {
                    if !msg_dict.contains(field).unwrap_or(false) {
                        is_valid = false;
                        missing_fields.push(field);
                    }
                }
                
                validation.set_item("is_valid", is_valid)?;
                validation.set_item("missing_fields", missing_fields)?;
            } else {
                validation.set_item("is_valid", false)?;
                validation.set_item("error", "Invalid message format")?;
            }
            
            Ok(validation.into())
        })
    }

    /// Get system metrics
    fn get_system_metrics(&self) -> SystemMetrics {
        let mut metrics = SystemMetrics::new();
        
        // Calculate uptime
        metrics.uptime_seconds = self.start_time
            .duration_since(SystemTime::now())
            .unwrap_or_default()
            .as_secs_f64();
        
        // Simulate system metrics (in a real implementation, you'd use system APIs)
        metrics.memory_usage_mb = 512.0; // Placeholder
        metrics.disk_usage_percent = 45.0; // Placeholder
        metrics.cpu_usage_percent = 25.0; // Placeholder
        metrics.active_utilities = self.utility_registry.len() as u32;
        
        metrics
    }

    /// Cleanup old data
    fn cleanup_old_data(&mut self, days_old: u32) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let cutoff_time = SystemTime::now() - Duration::from_secs(days_old as u64 * 86400);
            let mut cleaned_count = 0;
            
            // Clean up old file operations
            let original_count = self.file_operations.len();
            self.file_operations.retain(|op| {
                let op_time = SystemTime::UNIX_EPOCH + Duration::from_secs(op.timestamp as u64);
                op_time > cutoff_time
            });
            cleaned_count += original_count - self.file_operations.len();
            
            // Clean up old validation cache
            let original_cache_size = self.validation_cache.len();
            self.validation_cache.retain(|_, validation| {
                let validation_time = SystemTime::UNIX_EPOCH + Duration::from_secs(validation.timestamp as u64);
                validation_time > cutoff_time
            });
            cleaned_count += original_cache_size - self.validation_cache.len();
            
            let result = PyDict::new(py);
            result.set_item("cleaned_items", cleaned_count)?;
            result.set_item("remaining_file_operations", self.file_operations.len())?;
            result.set_item("remaining_cache_entries", self.validation_cache.len())?;
            result.set_item("days_old", days_old)?;
            
            Ok(result.into())
        })
    }

    /// Register utility
    fn register_utility(&mut self, name: &str, description: &str) {
        self.utility_registry.insert(name.to_string(), description.to_string());
        self.usage_stats.insert(name.to_string(), 0);
    }

    /// Track utility usage
    fn track_utility_usage(&mut self, utility_name: &str, success: bool) {
        let key = format!("{}:{}", utility_name, if success { "success" } else { "failure" });
        *self.usage_stats.entry(key).or_insert(0) += 1;
    }

    /// Get usage statistics
    fn get_usage_stats(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let stats = PyDict::new(py);
            for (key, count) in &self.usage_stats {
                stats.set_item(key, count)?;
            }
            Ok(stats.into())
        })
    }

    /// Get utility registry
    fn get_utility_registry(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let registry = PyDict::new(py);
            for (name, description) in &self.utility_registry {
                registry.set_item(name, description)?;
            }
            Ok(registry.into())
        })
    }

    /// Get all file operations
    fn get_file_operations(&self) -> Vec<FileOperationResult> {
        self.file_operations.clone()
    }

    /// Clear all data
    fn clear_all(&mut self) {
        self.usage_stats.clear();
        self.utility_registry.clear();
        self.file_operations.clear();
        self.validation_cache.clear();
    }
}

/// Python module definition
#[pymodule]
fn aios_utils_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<ValidationResult>()?;
    m.add_class::<FileOperationResult>()?;
    m.add_class::<SystemMetrics>()?;
    m.add_class::<RustUtilsCore>()?;
    Ok(())
}
