//! Fractal Core Rust Implementations
//! Fast operations for split/merge, knapsack, policy interpolation
//! 
//! Week 3: Structure created, implementation pending
//! Week 4-5: Implement + property tests

use pyo3::prelude::*;

/// Fast split decision
/// 
/// τ_split = σ(a + b·entropy + c·error_density)
/// 
/// Returns true if fragment should be split
#[pyfunction]
fn should_split(entropy: f64, error_density: f64, params: Vec<f64>) -> bool {
    if params.len() < 3 {
        return false;
    }
    
    let a = params[0];
    let b = params[1];
    let c = params[2];
    
    let threshold = sigmoid(a + b * entropy + c * error_density);
    
    entropy > threshold
}

/// Fast merge decision
/// 
/// τ_merge = σ(d + e·js_div + f·topic_shift)
/// 
/// Returns true if fragments should be merged
#[pyfunction]
fn should_merge(js_div: f64, topic_shift: f64, params: Vec<f64>) -> bool {
    if params.len() < 3 {
        return false;
    }
    
    let d = params[0];
    let e = params[1];
    let f = params[2];
    
    let threshold = sigmoid(d + e * js_div + f * topic_shift);
    
    js_div < threshold
}

/// Fast greedy knapsack
/// 
/// Args:
///   gains: Predicted decision gains per span
///   costs: Token costs per span
///   budget: Total token budget
/// 
/// Returns: Indices of selected spans
#[pyfunction]
fn greedy_knapsack(gains: Vec<f64>, costs: Vec<usize>, budget: usize) -> Vec<usize> {
    if gains.len() != costs.len() {
        return vec![];
    }
    
    // Calculate ratios
    let mut items: Vec<(usize, f64)> = gains
        .iter()
        .zip(costs.iter())
        .enumerate()
        .filter_map(|(i, (&gain, &cost))| {
            if cost > 0 {
                Some((i, gain / cost as f64))
            } else {
                None
            }
        })
        .collect();
    
    // Sort by ratio descending
    items.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
    
    // Greedy selection
    let mut selected = Vec::new();
    let mut used = 0;
    
    for (idx, _ratio) in items {
        if used + costs[idx] <= budget {
            selected.push(idx);
            used += costs[idx];
        }
    }
    
    selected
}

/// Sigmoid function
fn sigmoid(x: f64) -> f64 {
    1.0 / (1.0 + (-x).exp())
}

/// Python module
#[pymodule]
fn rust_fractal(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(should_split, m)?)?;
    m.add_function(wrap_pyfunction!(should_merge, m)?)?;
    m.add_function(wrap_pyfunction!(greedy_knapsack, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_sigmoid() {
        assert!(sigmoid(0.0) > 0.49 && sigmoid(0.0) < 0.51);
        assert!(sigmoid(10.0) > 0.99);
        assert!(sigmoid(-10.0) < 0.01);
    }
    
    #[test]
    fn test_should_split() {
        let params = vec![0.5, 0.1, 0.05];
        
        // High entropy should split
        assert!(should_split(0.9, 0.5, params.clone()));
        
        // Low entropy should not split
        assert!(!should_split(0.1, 0.1, params.clone()));
    }
    
    #[test]
    fn test_greedy_knapsack() {
        let gains = vec![10.0, 8.0, 5.0, 3.0];
        let costs = vec![300, 250, 200, 150];
        let budget = 600;
        
        let selected = greedy_knapsack(gains, costs, budget);
        
        // Should select items 0 and 1 (best ratios, fit in budget)
        assert!(selected.contains(&0));
        assert!(selected.contains(&1));
        
        // Total cost should not exceed budget
        let total_cost: usize = selected.iter().map(|&i| costs[i]).sum();
        assert!(total_cost <= budget);
    }
}

