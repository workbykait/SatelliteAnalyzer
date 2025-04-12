import requests
import gradio as gr
import os
import random
from datetime import datetime, timedelta
import plotly.express as px
import re
import io

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

LOG_HISTORY = []

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
            "Signal stable, no issues.",
            "Warning: Solar flare detected."
        ]
        message = random.choice(messages)
        entries.append(f"{time} | {lat}N, {lon}W | Frequency: {freq} GHz | Signal Strength: {signal}% | Message: {message}")
    return "\n".join(entries)

def analyze_log(log_text):
    if not log_text.strip():
        return "Error: Please enter a log.", None, None, None
    LOG_HISTORY.append(log_text)
    data = {
        "model": "llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": "Analyze this satellite radio log and summarize in bullet points. Include interference risk scores (0-100, low signal <70% = high risk >80, emergency = 90). Ensure frequencies in issues and details:\n- Issues (e.g., low signal, noise, interference with frequency, risk score)\n- High-priority messages (e.g., emergencies, warnings)\n- Key details (coordinates, times, frequencies, signal strengths)\nLog:\n" + log_text
            }
        ],
        "max_completion_tokens": 500,
        "temperature": 0.5
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        summary = response.json()["choices"][0]["message"]["content"]
        html = "<div style='font-family:Roboto; color:black; background:white; padding:10px; border-radius:5px; border:1px solid #ff6200;'><h3>Analysis</h3><ul>"
        for line in summary.split("\n"):
            if "Issues:" in line:
                html += "<li><b style='color:#ff6200;'>Issues:</b><ul>"
            elif "High-priority messages:" in line:
                html += "</ul><li><b style='color:#ff6200;'>Priority Alerts:</b><ul>"
            elif "Key details:" in line:
                html += "</ul><li><b style='color:#ff6200;'>Details:</b><ul>"
            elif line.strip():
                html += f"<li>{line.strip()}</li>"
        html += "</ul></div>"
        signals = []
        times = []
        for line in log_text.split("\n"):
            if "Signal Strength" in line:
                match = re.search(r"Signal Strength: (\d+)%", line)
                if match:
                    signals.append(int(match.group(1)))
                time_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC", line)
                if time_match:
                    times.append(time_match.group(1)[-5:])
        fig = px.line(x=times, y=signals, labels={"x": "Time", "y": "Signal (%)"}, title="Signal Trend") if signals and len(signals) == len(times) else None
        export_file = io.StringIO(summary)
        return summary, html, fig, gr.File(value=export_file, file_name="summary.txt", visible=True)
    except Exception as e:
        return f"Error: API call failed - {str(e)}", None, None, None

def generate_alert(log_text):
    if not log_text.strip():
        return "Error: Please enter a log."
    data = {
        "model": "llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": "Generate an urgent satellite alert based on this log’s conditions (e.g., interference for noise/low signal, escalation for emergencies). Include frequency, time, coordinates:\nLog:\n" + log_text
            }
        ],
        "max_completion_tokens": 100,
        "temperature": 0.7
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        alert = response.json()["choices"][0]["message"]["content"]
        return f"<div style='font-family:Roboto; background:#ff6200; color:white; padding:10px; border-radius:5px;'>{alert}</div>"
    except Exception as e:
        return f"Error: Alert failed - {str(e)}"

def compare_logs():
    if len(LOG_HISTORY) < 2:
        return "Error: Need at least two logs.", None
    compare_text = "Previous log:\n" + LOG_HISTORY[-2] + "\nCurrent log:\n" + LOG_HISTORY[-1]
    data = {
        "model": "llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": "Compare these two satellite radio logs and summarize trends in bullet points (e.g., signal strength changes, frequency issues, new emergencies):\n" + compare_text
            }
        ],
        "max_completion_tokens": 400,
        "temperature": 0.5
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        comparison = response.json()["choices"][0]["message"]["content"]
        html = "<div style='font-family:Roboto; color:black; background:white; padding:10px; border-radius:5px; border:1px solid #ff6200;'><h3>Comparison</h3><ul>"
        for line in comparison.split("\n"):
            if line.strip():
                html += f"<li>{line.strip()}</li>"
        html += "</ul></div>"
        return comparison, html
    except Exception as e:
        return f"Error: Comparison failed - {str(e)}", None

def load_sample_log():
    return SAMPLE_LOG

def clear_log():
    return ""

css = """
body, .gradio-container { background: white; color: black; font-family: Roboto, sans-serif; }
button { background: #ff6200; color: white; border: none; padding: 8px 16px; border-radius: 5px; }
button:hover { background: #e55a00; }
.input-text, .output-text { background: white; color: black; border: 1px solid #ff6200; border-radius: 5px; }
h3 { color: #ff6200; }
.header, .subheader { color: #ff6200; text-align: center; }
"""
with gr.Blocks(css=css) as interface:
    gr.Markdown("# Satellite Signal Log Analyzer", elem_classes="header")
    gr.Markdown("Analyze logs for issues, alerts, and trends.", elem_classes="subheader")
    log_input = gr.Textbox(lines=5, show_label=False, placeholder="Enter or generate a log...")
    with gr.Row():
        sample_button = gr.Button("Sample Log")
        random_button = gr.Button("Random Log")
        clear_button = gr.Button("Clear")
    with gr.Row():
        analyze_button = gr.Button("Analyze")
        alert_button = gr.Button("Alert")
        compare_button = gr.Button("Compare Logs")
        export_button = gr.Button("Export")
    output = gr.HTML(show_label=False)
    plot_output = gr.Plot(show_label=False)
    alert_output = gr.HTML(show_label=False)
    compare_output = gr.HTML(show_label=False)
    export_output = gr.File(show_label=False, visible=False)
    sample_button.click(fn=load_sample_log, outputs=log_input)
    random_button.click(fn=generate_random_log, outputs=log_input)
    clear_button.click(fn=clear_log, outputs=log_input)
    analyze_button.click(fn=analyze_log, inputs=log_input, outputs=[output, output, plot_output, export_output])
    alert_button.click(fn=generate_alert, inputs=log_input, outputs=alert_output)
    compare_button.click(fn=compare_logs, outputs=[compare_output, compare_output])
    export_button.click(fn=lambda: None, outputs=export_output)

interface.launch()
