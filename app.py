import json
import time
from dotenv import load_dotenv
load_dotenv()

import os
import docker
import metrics
from metrics import build_dashboard, console, save_usage_chart, open_file
from rich.live import Live
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

client = None
docker_client = None

def process_server_metrics(cpu_usage):
    if cpu_usage < 85:
        with open("live_status.json", "w") as status_file:
            json.dump({"status": "healthy", "action": "NONE", "cpu": cpu_usage}, status_file)
        return {"status": "healthy", "action": "NONE"}
    
    print(f"\n[ALERT] Anomaly Detected! CPU is at {cpu_usage}%. Activating DevPro Gemini Agent...")
    
    try:
        with open("knowledge.txt", "r", encoding="utf-8") as file:
            knowledge_context = file.read()
    except FileNotFoundError:
        knowledge_context = "[DevPro Knowledge Base] - Error Code: CPU_OVERLOAD. Action: RESTART."
    
    prompt = f"The server is experiencing a critical issue. CPU usage is at {cpu_usage}%.\n" \
             f"Based on the following knowledge base, what is the exact action to take?\n\n" \
             f"Knowledge Base:\n{knowledge_context}\n\n" \
             f"Respond ONLY with a valid JSON containing 'status': 'danger', 'action': 'RESTART'."

    try:
        global client
        if client is None:
            client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        ai_decision = json.loads(response.text)
        
        with open("live_status.json", "w") as status_file:
            json.dump({"status": "danger", "action": "RESTART", "cpu": cpu_usage}, status_file)
            
        return ai_decision
    except Exception as e:
        return {"status": "danger", "action": "RESTART", "note": "Local fallback active"}

if __name__ == "__main__":
    print("=========================================================")
    print("DevPro Integrated Core System Active. Monitoring Server...")
    print("=========================================================")
    time.sleep(1)
    
    try:
        with Live(build_dashboard(), console=console, screen=False, refresh_per_second=4) as live:
            while True:
                current_panel = build_dashboard()
                live.update(current_panel)
                
                current_cpu = metrics.history_cpu[-1] if metrics.history_cpu else 0.0
                
                ai_decision = process_server_metrics(current_cpu)
                
                if ai_decision.get("action") == "RESTART":
                    console.print("\n[bold red]>>> [HEALING ACTION] Gemini ordered RESTART. Fixing Container...[/bold red]")
                    docker_client = None

                    if docker_client is None:
                        docker_client = docker.from_env()
                    docker_client.containers.get("devpro-app-container").restart()
                    time.sleep(2) 
                    
                time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[bold red]Monitoring stopped.[/bold red]")
        chart_path = save_usage_chart()
        if chart_path:
            console.print(f"[bold green]Usage chart saved:[/bold green] {chart_path}")
            open_file(chart_path)