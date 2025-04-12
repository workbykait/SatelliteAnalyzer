# Satellite Signal Log Analyzer
Built for the Cerebras Llama 4 Hackathon (April 2025).

Analyzes satellite radio logs to detect issues (e.g., interference at specific frequencies) and priorities (e.g., emergencies) using Llama 4 via Cerebras API. Features sample and random log generators, a clear button, and a sleek dark theme.

## How to Use
1. Visit: https://workbykait-satelliteanalyzer.hf.space/
2. Click "Load Sample Log," "Generate Random Log," or enter your own (format in `sample_log.txt`).
3. Click "Analyze" for a summary, or "Clear Log" to start fresh.

## Sample Log
```text
2025-04-12 10:01 UTC | 40.7N, 74.0W | Frequency: 14.5 GHz | Signal Strength: 85% | Message: Routine check, systems OK.
2025-04-12 10:02 UTC | 40.8N, 74.1W | Frequency: 14.7 GHz | Signal Strength: 60% | Message: Noise detected, possible interference.
2025-04-12 10:03 UTC | 40.9N, 74.2W | Frequency: 14.6 GHz | Signal Strength: 90% | Message: Emergency: Low battery alert.
