# Rust Biomedical Signal Processing Library

This directory contains Rust implementations for high-performance biomedical signal processing functionality for the Biomed Chat application.

## Features

### 🧠 **Signal Processing Library** (`src/lib.rs`)
- **Signal Data Structure**: Efficient handling of biomedical signals with sample rate information
- **Moving Average Filtering**: Real-time signal filtering for noise reduction
- **Statistical Analysis**: Mean, standard deviation, and variance calculations
- **Peak Detection**: Automated detection of signal peaks using threshold-based methods
- **ECG Analysis**: Specialized functions for heart rate calculation and rhythm analysis

### 🖥️ **Command Line Interface** (`src/main.rs`)
A powerful CLI tool for signal processing operations:

```bash
# Generate test signals
./target/debug/biomed-chat-rust generate <frequency> <duration> <sample_rate>

# Process signal samples
./target/debug/biomed-chat-rust process <sample_rate> <sample1> <sample2> ...

# Analyze ECG signals
./target/debug/biomed-chat-rust analyze <sample1> <sample2> ...
```

## Usage Examples

### Signal Generation
```bash
# Generate a 1 Hz sine wave for 2 seconds at 1000 Hz sample rate
./target/debug/biomed-chat-rust generate 1.0 2.0 1000
```

### ECG Analysis
```bash
# Analyze ECG samples (sample rate defaults to 1000 Hz)
./target/debug/biomed-chat-rust analyze 0.1 0.8 1.0 0.3 0.2 0.9 0.8 0.1
```

### Signal Processing
```bash
# Process signal samples with 1000 Hz sample rate
./target/debug/biomed-chat-rust process 1000 1.0 2.0 3.0 2.0 1.0
```

## Building and Running

### Prerequisites
- Rust 1.70+ (install with `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`)

### Build
```bash
cargo build
```

### Run Tests
```bash
cargo test
```

### Run CLI
```bash
cargo run -- <command> [args...]
```

## Performance Benefits

- **Memory Safety**: Rust's ownership system prevents memory-related bugs
- **Zero-Cost Abstractions**: High-level code with low-level performance
- **Concurrency**: Safe concurrent processing for real-time applications
- **Speed**: Significantly faster than equivalent Python implementations

## Integration with JavaScript/TypeScript

The Rust library can be integrated with the existing JavaScript/TypeScript codebase using:

1. **WebAssembly**: Compile to WASM for browser usage
2. **Node.js Addon**: Create native Node.js bindings
3. **HTTP API**: Expose as a microservice with REST API
4. **File-based Communication**: Process files and exchange data via filesystem

## API Reference

### SignalData
```rust
let signal = SignalData::new(vec![1.0, 2.0, 3.0], 1000.0);
```

### Processing Pipeline
```rust
let processed = signal.process();
println!("Mean: {:.2}", processed.mean);
println!("Peaks: {:?}", processed.peaks);
```

### ECG Functions
```rust
use biomed_rust::ecg;

let heart_rate = ecg::calculate_heart_rate(&signal, &peaks);
let rhythm = ecg::analyze_rhythm(&signal, &peaks);
```

## Future Enhancements

- **FFT Analysis**: Fast Fourier Transform for frequency domain analysis
- **Machine Learning**: Integration with Rust ML frameworks
- **Real-time Processing**: WebSocket-based streaming for live signals
- **File Format Support**: DICOM, EDF, and other biomedical formats
- **GPU Acceleration**: Performance optimization for large datasets

## Contributing

When adding new features:
1. Follow Rust best practices and idioms
2. Add comprehensive tests
3. Update documentation
4. Ensure performance benchmarks
