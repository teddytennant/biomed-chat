use biomed_rust::SignalData;
use biomed_rust::ecg;
use biomed_rust::utils;
use std::env;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        eprintln!("Usage: {} <command> [args...]", args[0]);
        eprintln!("Commands:");
        eprintln!("  process <sample_rate> <samples...>  - Process signal samples");
        eprintln!("  generate <frequency> <duration> <sample_rate>  - Generate test signal");
        eprintln!("  analyze <samples...>  - Analyze ECG signal (sample_rate=1000)");
        process::exit(1);
    }

    match args[1].as_str() {
        "process" => {
            if args.len() < 4 {
                eprintln!("Usage: {} process <sample_rate> <samples...>", args[0]);
                process::exit(1);
            }

            let sample_rate: f64 = args[2].parse().expect("Invalid sample rate");
            let samples: Vec<f64> = args[3..].iter()
                .map(|s| s.parse().expect("Invalid sample"))
                .collect();

            let signal = SignalData::new(samples, sample_rate);
            let processed = signal.process();

            println!("Processed Signal:");
            println!("  Mean: {:.2}", processed.mean);
            println!("  Standard Deviation: {:.2}", processed.std_dev);
            println!("  Number of peaks: {}", processed.peaks.len());
            println!("  Peaks at indices: {:?}", processed.peaks);
        }

        "generate" => {
            if args.len() != 5 {
                eprintln!("Usage: {} generate <frequency> <duration> <sample_rate>", args[0]);
                process::exit(1);
            }

            let frequency: f64 = args[2].parse().expect("Invalid frequency");
            let duration: f64 = args[3].parse().expect("Invalid duration");
            let sample_rate: f64 = args[4].parse().expect("Invalid sample rate");

            let mut signal = utils::generate_sine_wave(frequency, sample_rate, duration);
            utils::add_noise(&mut signal, 0.1);

            println!("Generated Signal:");
            println!("  Samples: {} (showing first 10)", signal.samples.len());
            println!("  First 10 samples: {:?}", &signal.samples[..10.min(signal.samples.len())]);
        }

        "analyze" => {
            if args.len() < 3 {
                eprintln!("Usage: {} analyze <samples...>", args[0]);
                process::exit(1);
            }

            let samples: Vec<f64> = args[2..].iter()
                .map(|s| s.parse().expect("Invalid sample"))
                .collect();

            let signal = SignalData::new(samples, 1000.0);
            let processed = signal.process();
            let heart_rate = ecg::calculate_heart_rate(&signal, &processed.peaks);
            let rhythm = ecg::analyze_rhythm(&signal, &processed.peaks);

            println!("ECG Analysis:");
            println!("  Heart Rate: {:.1} BPM", heart_rate);
            println!("  Rhythm: {}", rhythm);
            println!("  Mean amplitude: {:.2}", processed.mean);
            println!("  Standard deviation: {:.2}", processed.std_dev);
        }

        _ => {
            eprintln!("Unknown command: {}", args[1]);
            eprintln!("Use 'help' or run without arguments for usage");
            process::exit(1);
        }
    }
}
