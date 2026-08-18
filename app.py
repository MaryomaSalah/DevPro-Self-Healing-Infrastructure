import json
from openai import OpenAI

client = OpenAI(api_key="sk-YOUR_ACTUAL_API_KEY_HERE")

def process_server_metrics(cpu_usage):
    
    if cpu_usage < 85:
        return {
            "status": "healthy", 
            "action": "NONE", 
            "message": "Server is running smoothly."
        }
    
    print(f"\n[ALERT] Anomaly Detected! CPU is at {cpu_usage}%. Activating DevPro AI Agent...")
    
    knowledge_context = (
        "[DevPro Knowledge Base]\n"
        "- Error Code: CPU_OVERLOAD (CPU usage > 85%)\n"
        "- Automated Fix Action: Issue a RESTART command to the Docker container."
    )
    
    prompt = f"The server is experiencing a critical issue. CPU usage is at {cpu_usage}%.\n" \
             f"Based on the following knowledge base, what is the exact action to take?\n\n" \
             f"Knowledge Base:\n{knowledge_context}\n\n" \
             f"Respond ONLY with a valid JSON containing 'status': 'danger', 'action': 'RESTART'."

    try:
        
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        ai_decision = json.loads(response.choices.message.content)
        return ai_decision

    except Exception as e:
        print("[System Note] Running local backup mechanism...")
        if cpu_usage >= 85:
            return {"status": "danger", "action": "RESTART", "note": "Local fallback active"}
        return {"status": "healthy", "action": "NONE"}

if __name__ == "__main__":
    final_output = process_server_metrics(90)
    print("\n[FINAL RESOURCE OUTPUT FOR TEAM]:")
    print(json.dumps(final_output, indent=4))
