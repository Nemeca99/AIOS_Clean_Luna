use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::SystemTime;
use uuid::Uuid;

/// Represents a memory fragment for CARMA processing
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct MemoryFragment {
    #[pyo3(get, set)]
    pub id: String,
    #[pyo3(get, set)]
    pub content: String,
    #[pyo3(get, set)]
    pub embedding: Vec<f32>,
    #[pyo3(get, set)]
    pub timestamp: f64,
    #[pyo3(get, set)]
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl MemoryFragment {
    #[new]
    fn new(id: String, content: String, embedding: Vec<f32>) -> Self {
        Self {
            id,
            content,
            embedding,
            timestamp: SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .unwrap()
                .as_secs_f64(),
            metadata: HashMap::new(),
        }
    }
}

/// Represents clustering results
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct ClusterResult {
    #[pyo3(get)]
    pub clusters: HashMap<i32, Vec<MemoryFragment>>,
    #[pyo3(get)]
    pub metadata: HashMap<String, f64>,
    #[pyo3(get)]
    pub num_clusters: usize,
}

#[pymethods]
impl ClusterResult {
    #[new]
    fn new(clusters: HashMap<i32, Vec<MemoryFragment>>, metadata: HashMap<String, f64>) -> Self {
        let num_clusters = clusters.len();
        Self {
            clusters,
            metadata,
            num_clusters,
        }
    }
}

/// Main CARMA Rust implementation
#[pyclass]
pub struct RustCarmaCore {
    fragments: Vec<MemoryFragment>,
    clusters: HashMap<i32, Vec<MemoryFragment>>,
    total_queries: u64,
}

#[pymethods]
impl RustCarmaCore {
    #[new]
    fn new() -> Self {
        Self {
            fragments: Vec::new(),
            clusters: HashMap::new(),
            total_queries: 0,
        }
    }

    /// Add a memory fragment
    fn add_fragment(&mut self, content: String, embedding: Vec<f32>) -> String {
        let id = Uuid::new_v4().to_string();
        let fragment = MemoryFragment::new(id.clone(), content, embedding);
        self.fragments.push(fragment);
        id
    }

    /// Find relevant fragments using cosine similarity
    fn find_relevant_fragments(&self, query_embedding: Vec<f32>, topk: usize) -> Vec<MemoryFragment> {
        if self.fragments.is_empty() {
            return Vec::new();
        }

        let mut similarities: Vec<(usize, f32)> = self
            .fragments
            .iter()
            .enumerate()
            .map(|(i, fragment)| {
                let similarity = cosine_similarity(&query_embedding, &fragment.embedding);
                (i, similarity)
            })
            .collect();

        // Sort by similarity (descending)
        similarities.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

        // Return top k fragments
        similarities
            .iter()
            .take(topk)
            .map(|(i, _)| self.fragments[*i].clone())
            .collect()
    }

    /// Cluster fragments using simple k-means
    fn cluster_fragments(&mut self, num_clusters: usize) -> ClusterResult {
        if self.fragments.len() < 2 {
            let mut clusters = HashMap::new();
            clusters.insert(0, self.fragments.clone());
            let metadata = HashMap::new();
            return ClusterResult::new(clusters, metadata);
        }

        // Extract features (embeddings)
        let features: Vec<&Vec<f32>> = self.fragments.iter().map(|f| &f.embedding).collect();
        
        // Simple k-means clustering
        let cluster_assignments = kmeans_clustering(&features, num_clusters);
        
        // Group fragments by cluster
        let mut clusters: HashMap<i32, Vec<MemoryFragment>> = HashMap::new();
        for (i, cluster_id) in cluster_assignments.iter().enumerate() {
            clusters
                .entry(*cluster_id)
                .or_insert_with(Vec::new)
                .push(self.fragments[i].clone());
        }

        // Calculate metadata
        let metadata = calculate_cluster_metadata(&clusters);
        
        self.clusters = clusters.clone();
        
        ClusterResult::new(clusters, metadata)
    }

    /// Process a query and return relevant fragments
    fn process_query(&mut self, query: String, query_embedding: Vec<f32>, topk: usize) -> PyResult<PyObject> {
        self.total_queries += 1;
        
        let relevant_fragments = self.find_relevant_fragments(query_embedding, topk);
        
        // Create response dictionary
        Python::with_gil(|py| {
            let result = PyDict::new(py);
            result.set_item("query", query)?;
            result.set_item("total_queries", self.total_queries)?;
            result.set_item("fragments_found", relevant_fragments.len())?;
            // Convert fragments to Python objects
            let fragment_list = PyList::empty(py);
            for fragment in relevant_fragments {
                let py_fragment = Py::new(py, fragment)?;
                fragment_list.append(py_fragment)?;
            }
            result.set_item("fragments", fragment_list)?;
            Ok(result.into())
        })
    }

    /// Get system statistics
    fn get_stats(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let stats = PyDict::new(py);
            stats.set_item("total_fragments", self.fragments.len())?;
            stats.set_item("total_queries", self.total_queries)?;
            stats.set_item("num_clusters", self.clusters.len())?;
            Ok(stats.into())
        })
    }

    /// Get all fragments
    fn get_all_fragments(&self) -> Vec<MemoryFragment> {
        self.fragments.clone()
    }

    /// Clear all data
    fn clear_all(&mut self) {
        self.fragments.clear();
        self.clusters.clear();
        self.total_queries = 0;
    }
}

/// Calculate cosine similarity between two vectors
fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
    if a.len() != b.len() {
        return 0.0;
    }

    let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    let magnitude_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
    let magnitude_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

    if magnitude_a == 0.0 || magnitude_b == 0.0 {
        0.0
    } else {
        dot_product / (magnitude_a * magnitude_b)
    }
}

/// Simple k-means clustering implementation
fn kmeans_clustering(features: &[&Vec<f32>], k: usize) -> Vec<i32> {
    if features.is_empty() || k == 0 {
        return Vec::new();
    }

    let n = features.len();
    let dim = features[0].len();
    
    // Initialize centroids randomly
    let mut centroids: Vec<Vec<f32>> = (0..k)
        .map(|_| {
            (0..dim)
                .map(|_| rand::random::<f32>() * 2.0 - 1.0)
                .collect()
        })
        .collect();

    let mut assignments = vec![0; n];
    let max_iterations = 100;

    for _ in 0..max_iterations {
        let mut changed = false;

        // Assign points to closest centroid
        for (i, feature) in features.iter().enumerate() {
            let mut best_cluster = 0;
            let mut best_distance = f32::INFINITY;

            for (j, centroid) in centroids.iter().enumerate() {
                let distance = euclidean_distance(feature, centroid);
                if distance < best_distance {
                    best_distance = distance;
                    best_cluster = j;
                }
            }

            if assignments[i] != best_cluster as i32 {
                assignments[i] = best_cluster as i32;
                changed = true;
            }
        }

        if !changed {
            break;
        }

        // Update centroids
        for (j, centroid) in centroids.iter_mut().enumerate() {
            let cluster_points: Vec<&Vec<f32>> = features
                .iter()
                .zip(assignments.iter())
                .filter(|(_, &cluster)| cluster == j as i32)
                .map(|(point, _)| *point)
                .collect();

            if !cluster_points.is_empty() {
                for (i, component) in centroid.iter_mut().enumerate() {
                    *component = cluster_points.iter().map(|point| point[i]).sum::<f32>()
                        / cluster_points.len() as f32;
                }
            }
        }
    }

    assignments
}

/// Calculate Euclidean distance between two vectors
fn euclidean_distance(a: &[f32], b: &[f32]) -> f32 {
    if a.len() != b.len() {
        return f32::INFINITY;
    }

    a.iter()
        .zip(b.iter())
        .map(|(x, y)| (x - y).powi(2))
        .sum::<f32>()
        .sqrt()
}

/// Calculate cluster metadata
fn calculate_cluster_metadata(clusters: &HashMap<i32, Vec<MemoryFragment>>) -> HashMap<String, f64> {
    let mut metadata = HashMap::new();
    
    let total_fragments: usize = clusters.values().map(|v| v.len()).sum();
    metadata.insert("total_fragments".to_string(), total_fragments as f64);
    metadata.insert("num_clusters".to_string(), clusters.len() as f64);
    
    // Calculate average cluster size
    if !clusters.is_empty() {
        let avg_size = total_fragments as f64 / clusters.len() as f64;
        metadata.insert("avg_cluster_size".to_string(), avg_size);
    }

    metadata
}

/// Python module definition
#[pymodule]
fn aios_carma_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<MemoryFragment>()?;
    m.add_class::<ClusterResult>()?;
    m.add_class::<RustCarmaCore>()?;
    Ok(())
}
