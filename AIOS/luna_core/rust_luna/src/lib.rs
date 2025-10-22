use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::SystemTime;
use uuid::Uuid;
use regex::Regex;
use chrono::{DateTime, Utc};

/// Represents a Luna response with personality traits
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct LunaResponse {
    #[pyo3(get, set)]
    pub response: String,
    #[pyo3(get, set)]
    pub personality_trait: String,
    #[pyo3(get, set)]
    pub karma_score: f64,
    #[pyo3(get, set)]
    pub timestamp: f64,
    #[pyo3(get, set)]
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl LunaResponse {
    #[new]
    fn new(response: String, personality_trait: String, karma_score: f64) -> Self {
        Self {
            response,
            personality_trait,
            karma_score,
            timestamp: SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .unwrap()
                .as_secs_f64(),
            metadata: HashMap::new(),
        }
    }
}

/// Represents a learning session result
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct LearningSessionResult {
    #[pyo3(get)]
    pub total_questions: usize,
    #[pyo3(get)]
    pub total_responses: usize,
    #[pyo3(get)]
    pub average_karma: f64,
    #[pyo3(get)]
    pub session_duration: f64,
    #[pyo3(get)]
    pub responses: Vec<LunaResponse>,
}

#[pymethods]
impl LearningSessionResult {
    #[new]
    fn new(total_questions: usize, total_responses: usize, average_karma: f64, session_duration: f64) -> Self {
        Self {
            total_questions,
            total_responses,
            average_karma,
            session_duration,
            responses: Vec::new(),
        }
    }
}

/// Main Luna Rust implementation
#[pyclass]
pub struct RustLunaCore {
    responses: Vec<LunaResponse>,
    total_interactions: u64,
    karma_history: Vec<f64>,
    personality_traits: HashMap<String, f64>,
}

#[pymethods]
impl RustLunaCore {
    #[new]
    fn new() -> Self {
        Self {
            responses: Vec::new(),
            total_interactions: 0,
            karma_history: Vec::new(),
            personality_traits: HashMap::new(),
        }
    }

    /// Generate a response with personality traits
    fn generate_response(&mut self, question: String, personality_trait: String, karma_score: f64) -> LunaResponse {
        self.total_interactions += 1;
        
        let response = LunaResponse::new(
            format!("Luna's response to: {}", question),
            personality_trait.clone(),
            karma_score
        );
        
        // Update personality traits
        let current_trait_value = self.personality_traits.get(&personality_trait).unwrap_or(&0.5);
        let new_trait_value = (current_trait_value + karma_score) / 2.0;
        self.personality_traits.insert(personality_trait, new_trait_value.clamp(0.0, 1.0));
        
        // Store response and karma
        self.responses.push(response.clone());
        self.karma_history.push(karma_score);
        
        response
    }

    /// Run a learning session with multiple questions
    fn run_learning_session(&mut self, questions: Vec<String>, traits: Vec<String>) -> LearningSessionResult {
        let start_time = SystemTime::now();
        
        if questions.len() != traits.len() {
            return LearningSessionResult::new(0, 0, 0.0, 0.0);
        }
        
        let mut responses = Vec::new();
        let mut total_karma = 0.0;
        
        for (question, personality_trait) in questions.iter().zip(traits.iter()) {
            // Generate karma score based on question complexity and trait
            let karma_score = self.calculate_karma_score(question, personality_trait);
            let response = self.generate_response(question.clone(), personality_trait.clone(), karma_score);
            
            total_karma += karma_score;
            responses.push(response);
        }
        
        let session_duration = start_time
            .duration_since(SystemTime::now())
            .unwrap_or_default()
            .as_secs_f64();
        
        let average_karma = if responses.is_empty() { 0.0 } else { total_karma / responses.len() as f64 };
        
        let mut result = LearningSessionResult::new(
            questions.len(),
            responses.len(),
            average_karma,
            session_duration
        );
        result.responses = responses;
        
        result
    }

    /// Calculate karma score based on question analysis
    fn calculate_karma_score(&self, question: &str, personality_trait: &str) -> f64 {
        let mut score = 0.5; // Base score
        
        // Analyze question complexity
        let word_count = question.split_whitespace().count();
        score += (word_count as f64 / 100.0).min(0.2); // Up to 0.2 bonus for complexity
        
        // Analyze emotional content
        let emotional_words = ["love", "hate", "happy", "sad", "angry", "excited", "worried"];
        let emotional_count = emotional_words.iter()
            .filter(|word| question.to_lowercase().contains(*word))
            .count();
        score += (emotional_count as f64 * 0.1).min(0.3); // Up to 0.3 bonus for emotion
        
        // Trait-specific adjustments
        match personality_trait {
            "openness" => score += 0.1,
            "conscientiousness" => score += 0.05,
            "extraversion" => score += 0.15,
            "agreeableness" => score += 0.1,
            "neuroticism" => score -= 0.05,
            _ => {}
        }
        
        score.clamp(0.0, 1.0)
    }

    /// Analyze emotional tone of text
    fn analyze_emotional_tone(&self, text: &str) -> String {
        let positive_words = ["happy", "good", "great", "wonderful", "amazing", "love", "joy"];
        let negative_words = ["sad", "bad", "terrible", "awful", "hate", "angry", "fear"];
        
        let positive_count = positive_words.iter()
            .filter(|word| text.to_lowercase().contains(*word))
            .count();
        let negative_count = negative_words.iter()
            .filter(|word| text.to_lowercase().contains(*word))
            .count();
        
        if positive_count > negative_count {
            "positive".to_string()
        } else if negative_count > positive_count {
            "negative".to_string()
        } else {
            "neutral".to_string()
        }
    }

    /// Classify question type
    fn classify_question_type(&self, question: &str) -> String {
        if question.contains("?") {
            "question".to_string()
        } else if question.contains("!") {
            "exclamation".to_string()
        } else if question.len() > 100 {
            "complex".to_string()
        } else {
            "simple".to_string()
        }
    }

    /// Get personality trait scores
    fn get_personality_traits(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let traits = PyDict::new(py);
            for (personality_trait, value) in &self.personality_traits {
                traits.set_item(personality_trait, value)?;
            }
            Ok(traits.into())
        })
    }

    /// Get system statistics
    fn get_stats(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let stats = PyDict::new(py);
            stats.set_item("total_interactions", self.total_interactions)?;
            stats.set_item("total_responses", self.responses.len())?;
            stats.set_item("average_karma", self.calculate_average_karma())?;
            stats.set_item("personality_traits", self.personality_traits.len())?;
            Ok(stats.into())
        })
    }

    /// Calculate average karma score
    fn calculate_average_karma(&self) -> f64 {
        if self.karma_history.is_empty() {
            0.0
        } else {
            self.karma_history.iter().sum::<f64>() / self.karma_history.len() as f64
        }
    }

    /// Get all responses
    fn get_all_responses(&self) -> Vec<LunaResponse> {
        self.responses.clone()
    }

    /// Clear all data
    fn clear_all(&mut self) {
        self.responses.clear();
        self.total_interactions = 0;
        self.karma_history.clear();
        self.personality_traits.clear();
    }
}

/// Arbiter Assessment Result
#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct ArbiterAssessment {
    #[pyo3(get)]
    pub utility_score: f64,
    #[pyo3(get)]
    pub karma_delta: f64,
    #[pyo3(get)]
    pub quality_gap: f64,
    #[pyo3(get)]
    pub reasoning: String,
    #[pyo3(get)]
    pub lessons_generated: usize,
}

#[pymethods]
impl ArbiterAssessment {
    #[new]
    fn new(utility_score: f64, karma_delta: f64, quality_gap: f64, reasoning: String) -> Self {
        Self {
            utility_score,
            karma_delta,
            quality_gap,
            reasoning,
            lessons_generated: 0,
        }
    }
}

/// Fast Arbiter implementation in Rust
#[pyclass]
pub struct RustArbiter {
    current_karma: f64,
    total_assessments: u64,
    lesson_count: usize,
}

#[pymethods]
impl RustArbiter {
    #[new]
    fn new(initial_karma: f64) -> Self {
        Self {
            current_karma: initial_karma,
            total_assessments: 0,
            lesson_count: 0,
        }
    }

    /// Fast utility score calculation
    fn calculate_utility_score(&self, luna_response: &str, gold_standard: &str) -> f64 {
        // Word overlap similarity (fast approximation)
        let luna_words: Vec<&str> = luna_response.split_whitespace().collect();
        let gold_words: Vec<&str> = gold_standard.split_whitespace().collect();
        
        if luna_words.is_empty() || gold_words.is_empty() {
            return 0.0;
        }
        
        // Count matching words
        let mut matches = 0;
        for luna_word in &luna_words {
            if gold_words.contains(luna_word) {
                matches += 1;
            }
        }
        
        // Jaccard similarity approximation
        let total_unique = (luna_words.len() + gold_words.len() - matches) as f64;
        if total_unique == 0.0 {
            return 1.0;
        }
        
        matches as f64 / total_unique
    }

    /// Fast response quality assessment
    fn assess_response_fast(
        &mut self,
        user_prompt: &str,
        luna_response: &str,
        tte_used: usize,
        max_tte: usize,
        rvc_grade: &str
    ) -> ArbiterAssessment {
        self.total_assessments += 1;
        
        // Calculate efficiency
        let efficiency = if max_tte > 0 {
            tte_used as f64 / max_tte as f64
        } else {
            0.0
        };
        
        // Base utility score from efficiency
        let mut utility_score = efficiency.clamp(0.0, 1.0);
        
        // Adjust for RVC grade
        let grade_bonus = match rvc_grade {
            "A" => 0.2,
            "B" => 0.1,
            "C" => 0.0,
            "D" => -0.1,
            "F" => -0.2,
            _ => 0.0,
        };
        utility_score = (utility_score + grade_bonus).clamp(0.0, 1.0);
        
        // Calculate karma delta based on performance
        let karma_delta = if efficiency < 0.5 {
            -0.1
        } else if efficiency > 0.9 {
            2.0
        } else {
            efficiency * 2.0 - 1.0
        };
        
        self.current_karma += karma_delta;
        
        // Quality gap (how far from perfect)
        let quality_gap = 1.0 - utility_score;
        
        // Reasoning
        let reasoning = if efficiency < 0.5 {
            format!("Poor response quality or efficiency. Karma changed by {:.1}. TTE efficiency: {:.1}%.", karma_delta, efficiency * 100.0)
        } else if efficiency > 0.9 {
            format!("Excellent response! Karma increased by {:.1}. TTE efficiency: {:.1}%.", karma_delta, efficiency * 100.0)
        } else {
            format!("Adequate response. Karma changed by {:.1}. TTE efficiency: {:.1}%.", karma_delta, efficiency * 100.0)
        };
        
        ArbiterAssessment {
            utility_score,
            karma_delta,
            quality_gap,
            reasoning,
            lessons_generated: 0,
        }
    }

    /// Get current karma
    fn get_current_karma(&self) -> f64 {
        self.current_karma
    }

    /// Get stats
    fn get_stats(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let stats = PyDict::new(py);
            stats.set_item("current_karma", self.current_karma)?;
            stats.set_item("total_assessments", self.total_assessments)?;
            stats.set_item("lesson_count", self.lesson_count)?;
            Ok(stats.into())
        })
    }
}

/// Python module definition
#[pymodule]
fn aios_luna_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<LunaResponse>()?;
    m.add_class::<LearningSessionResult>()?;
    m.add_class::<RustLunaCore>()?;
    m.add_class::<ArbiterAssessment>()?;
    m.add_class::<RustArbiter>()?;
    Ok(())
}
