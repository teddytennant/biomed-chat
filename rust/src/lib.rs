use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct SignalData {
    pub samples: Vec<f64>,
    pub sample_rate: f64,
}

#[derive(Serialize, Deserialize)]
pub struct ProcessedSignal {
    pub filtered: Vec<f64>,
    pub mean: f64,
    pub std_dev: f64,
    pub peaks: Vec<usize>,
}

impl SignalData {
    pub fn new(samples: Vec<f64>, sample_rate: f64) -> Self {
        SignalData { samples, sample_rate }
    }

    /// Apply a simple moving average filter
    pub fn moving_average_filter(&self, window_size: usize) -> Vec<f64> {
        let mut filtered = Vec::new();
        for i in 0..self.samples.len() {
            let start = if i < window_size { 0 } else { i - window_size + 1 };
            let window: Vec<f64> = self.samples[start..=i].to_vec();
            let avg = window.iter().sum::<f64>() / window.len() as f64;
            filtered.push(avg);
        }
        filtered
    }

    /// Calculate basic statistics
    pub fn statistics(&self) -> (f64, f64) {
        let mean = self.samples.iter().sum::<f64>() / self.samples.len() as f64;
        let variance = self.samples.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / self.samples.len() as f64;
        let std_dev = variance.sqrt();
        (mean, std_dev)
    }

    /// Detect peaks using a simple threshold method
    pub fn detect_peaks(&self, threshold: f64) -> Vec<usize> {
        let mut peaks = Vec::new();
        for i in 1..self.samples.len() - 1 {
            if self.samples[i] > self.samples[i - 1] && self.samples[i] > self.samples[i + 1] && self.samples[i] > threshold {
                peaks.push(i);
            }
        }
        peaks
    }

    /// Process the signal with filtering and analysis
    pub fn process(&self) -> ProcessedSignal {
        let filtered = self.moving_average_filter(5);
        let (mean, std_dev) = self.statistics();
        let peaks = self.detect_peaks(mean + std_dev);

        ProcessedSignal {
            filtered,
            mean,
            std_dev,
            peaks,
        }
    }
}

/// ECG-specific processing functions
pub mod ecg {
    use super::SignalData;

    pub fn calculate_heart_rate(signal: &SignalData, peaks: &[usize]) -> f64 {
        if peaks.len() < 2 {
            return 0.0;
        }

        let intervals: Vec<f64> = peaks.windows(2)
            .map(|w| (w[1] - w[0]) as f64 / signal.sample_rate)
            .collect();
        let avg_interval = intervals.iter().sum::<f64>() / intervals.len() as f64;
        60.0 / avg_interval
    }

    pub fn analyze_rhythm(_signal: &SignalData, peaks: &[usize]) -> String {
        if peaks.is_empty() {
            return "No peaks detected".to_string();
        }

        let regularity = calculate_regularity(peaks);
        if regularity < 0.1 {
            "Regular rhythm".to_string()
        } else if regularity < 0.3 {
            "Mildly irregular rhythm".to_string()
        } else {
            "Irregular rhythm".to_string()
        }
    }

    fn calculate_regularity(peaks: &[usize]) -> f64 {
        if peaks.len() < 3 {
            return 0.0;
        }

        let intervals: Vec<f64> = peaks.windows(2)
            .map(|w| (w[1] - w[0]) as f64)
            .collect();
        let mean_interval = intervals.iter().sum::<f64>() / intervals.len() as f64;
        let variance = intervals.iter().map(|x| (x - mean_interval).powi(2)).sum::<f64>() / intervals.len() as f64;
        (variance.sqrt() / mean_interval).abs()
    }
}

/// Utility functions for signal generation (useful for testing)
pub mod utils {
    use super::SignalData;

    pub fn generate_sine_wave(frequency: f64, sample_rate: f64, duration: f64) -> SignalData {
        let num_samples = (sample_rate * duration) as usize;
        let mut samples = Vec::with_capacity(num_samples);

        for i in 0..num_samples {
            let t = i as f64 / sample_rate;
            let sample = (2.0 * std::f64::consts::PI * frequency * t).sin();
            samples.push(sample);
        }

        SignalData::new(samples, sample_rate)
    }

    pub fn add_noise(signal: &mut SignalData, noise_level: f64) {
        // Use a simple deterministic noise generation
        let seed = 12345u64; // Fixed seed for reproducibility

        for i in 0..signal.samples.len() {
            let noise = ((seed as f64 + i as f64) * 0.1).sin() * noise_level;
            signal.samples[i] += noise;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_signal_processing() {
        let samples = vec![1.0, 2.0, 3.0, 2.0, 1.0];
        let signal = SignalData::new(samples, 1000.0);

        let processed = signal.process();
        assert_eq!(processed.filtered.len(), 5);
        assert!(processed.mean >= 1.8 && processed.mean < 2.2);
    }

    #[test]
    fn test_ecg_analysis() {
        let mut signal = utils::generate_sine_wave(1.0, 1000.0, 2.0);
        utils::add_noise(&mut signal, 0.1);

        let processed = signal.process();
        let heart_rate = ecg::calculate_heart_rate(&signal, &processed.peaks);
        let rhythm = ecg::analyze_rhythm(&signal, &processed.peaks);

        assert!(heart_rate >= 0.0);
        assert!(!rhythm.is_empty());
    }
}
