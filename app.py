import requests
import gradio as gr
import os
import random
from datetime import datetime, timedelta

api_key = os.getenv("CEREBRAS_API_KEY")
url = "https://api.cerebras.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

SAMPLE_LOG = """
2025-04-12 10:01 UTC | 40.7N, 74.0W | Frequency: 14.5 GHz | Signal Strength: 85% | Message: Routine check, systems OK.
2025-04-12 10:02 UTC | 40.8N, 74.1W | Frequency: 14.7 GHz | Signal Strength: 60% | Message: Noise detected, possible interference.
2025-04-12 10:03 UTC | 40.9N, 74.2W | Frequency: 14.6 GHz | Signal Strength: 90% | Message: Emergency: Low battery alert.
"""

def generate_random_log():
    base_time = datetime(2025, 4, 12, 10, 0)
    entries = []
    for i in range(3):
        time = (base_time + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M UTC")
        lat = round(random.uniform(40.0, 41.0), 1)
        lon = round(random.uniform(73.0, 74.0), 1)
        freq = round(random.uniform(14.0, 15.0), 1)
        signal = random.randint(50, 100)
        messages = [
            "Routine check, systems OK.",
            "Noise detected, possible interference.",
            "Emergency: Low battery alert.",
            "Signal stable, no issues."
        ]
        message = random.choice(messages)
        entries.append(f"{time} | {lat}N, {lon}W | Frequency: {freq} GHz | Signal Strength: {signal}% | Message: {message}")
    return "\n".join(entries)

def analyze_log(log_text):
    if not log_text.strip():
        return "Error: Please enter a log."
    data = {
        "model": "llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": "Analyze this satellite radio log and summarize in bullet points. Ensure frequencies are included in issues (if relevant) and key details:\n- Issues (e.g., low signal, noise, interference with frequency)\n- High-priority messages (e.g., emergencies)\n- Key details (coordinates, times, frequencies, signal strengths)\nLog:\n" + log_text
            }
        ],
        "max_completion_tokens": 400,
        "temperature": 0.5
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: API call failed - {str(e)}"

def load_sample_log():
    return SAMPLE_LOG

def clear_log():
    return ""

with gr.Blocks(theme="huggingface/dark") as interface:
    gr.Markdown("# Satellite Signal Log Analyzer")
    gr.Markdown("Enter, generate, or load a satellite radio log to detect issues, priorities, and details (including frequencies) using Llama 4 and Cerebras.")
    log_input = gr.Textbox(lines=5, label="Satellite Radio Log")
    with gr.Row():
        sample_button = gr.Button("Load Sample Log")
        random_button = gr.Button("Generate Random Log")
        clear_button = gr.Button("Clear Log")
    output = gr.Textbox(label="Analysis Summary")
    analyze_button = gr.Button("Analyze")
    sample_button.click(fn=load_sample_log, outputs=log_input)
    random_button.click(fn=generate_random_log, outputs=log_input)
    clear_button.click(fn=clear_log, outputs=log_input)
    analyze_button.click(fn=analyze_log, inputs=log_input, outputs=output)

interface.launch()
