import requests
import gradio as gr
import os

api_key = os.getenv("CEREBRAS_API_KEY")
url = "https://api.cerebras.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def analyze_log(log_text):
    if not log_text.strip():
        return "Error: Please enter a log."
    data = {
        "model": "llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": "Analyze this satellite radio log and summarize in bullet points:\n- Issues (e.g., low signal, noise)\n- High-priority messages (e.g., emergencies)\n- Key details (e.g., coordinates, times)\nLog:\n" + log_text
            }
        ],
        "max_completion_tokens": 200,
        "temperature": 0.5
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: API call failed - {str(e)}"

interface = gr.Interface(
    fn=analyze_log,
    inputs=gr.Textbox(lines=5, label="Paste Satellite Radio Log"),
    outputs=gr.Textbox(label="Analysis Summary"),
    title="Satellite Signal Log Analyzer",
    description="Enter a satellite radio log to detect issues and priorities using Llama 4 and Cerebras."
)
interface.launch()
