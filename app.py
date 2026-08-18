# import metrics
# from metrics import build_dashboard, console, save_usage_chart, open_file
# from rich.live import Live

# from google import genai
# from google.genai import types

# client = genai.Client(api_key="AQ.Ab8RN6Lg79xK-XW3oVIzeVskLxfhIeRSBomqM9OqdLYYbN_OuQ")

# cpu_usage_now = 0.0
# is_stress_active = False

# def monitor_system_metrics():
#     global cpu_usage_now, is_stress_active
#     while True:
#         if not is_stress_active:
#             cpu_usage_now = psutil.cpu_percent(interval=1)
#         time.sleep(1)

# def create_cpu_stress():
#     global is_stress_active, cpu_usage_now
#     print("\n[STRESS TRIGGERED] Simulating silent failure (CPU Spike)...")
#     is_stress_active = True
    
#     count = 0
#     while count < 10:
#         cpu_usage_now = 95.8
#         time.sleep(1)
#         count += 1
        
#     is_stress_active = False
#     print("\n[STRESS ENDED] Server returning to normal load.")

# def trigger_failure_event():
#     stress_thread = threading.Thread(target=create_cpu_stress)
#     stress_thread.start()


# def process_server_metrics(cpu_usage):
#     if cpu_usage < 85:
#         return {
#             "status": "healthy", 
#             "action": "NONE", 
#             "message": "Server is running smoothly."
#         }
    
#     print(f"\n[ALERT] Anomaly Detected! CPU is at {cpu_usage}%. Activating DevPro Gemini Agent...")
    
#     try:
#         with open("knowledge.txt", "r", encoding="utf-8") as file:
#             knowledge_context = file.read()
#     except FileNotFoundError:
#         knowledge_context = "[DevPro Knowledge Base] - Error Code: CPU_OVERLOAD. Action: RESTART."
    
#     prompt = f"The server is experiencing a critical issue. CPU usage is at {cpu_usage}%.\n" \
#              f"Based on the following knowledge base, what is the exact action to take?\n\n" \
#              f"Knowledge Base:\n{knowledge_context}\n\n" \
#              f"Respond ONLY with a valid JSON containing 'status': 'danger', 'action': 'RESTART'."

#     try:
#         response = client.models.generate_content(
#             model='gemini-2.5-flash',
#             contents=prompt,
#             config=types.GenerateContentConfig(
#                 response_mime_type="application/json"
#             ),
#         )
#         return json.loads(response.text)
#     except Exception as e:
#         return {"status": "danger", "action": "RESTART", "note": "Local fallback active"}


# if __name__ == "__main__":
#     monitor_thread = threading.Thread(target=monitor_system_metrics, daemon=True)
#     monitor_thread.start()
    
#     print("DevPro System Active with Gemini Engine. Monitoring Server...")
#     time.sleep(2)
    
#     trigger_failure_event()
    
#     try:
#         for _ in range(15):
#             current_cpu = cpu_usage_now
#             print(f"Current CPU Load: {current_cpu}%")
            
#             ai_decision = process_server_metrics(current_cpu)
            
#             if ai_decision.get("action") == "RESTART":
#                 print(">>> [HEALING ACTION] Gemini ordered RESTART. Fixing Docker Container container...")
#                 import os
#                 os.system("docker restart devpro-app-container")
#                 is_stress_active = False 
                
#             time.sleep(1)
            
#     except KeyboardInterrupt:
#         print("System stopped.")
import json
import time
import os
import metrics
from metrics import build_dashboard, console, save_usage_chart, open_file
from rich.live import Live
from google import genai
from google.genai import types

# 1. إعداد عميل جوجل بمفتاحكِ الحقيقي المرفوع
client = genai.Client(api_key="AIzaSy...") # مفتاحكِ السري موجود هنا تلقائياً

# 🧠 [جزء مريم - الـ AI Agent & RAG المحترف]
def process_server_metrics(cpu_usage):
    if cpu_usage < 85:
        # 🟢 إرسال إشارة الاستقرار الأخضر اللحظية لـ سارة
        with open("live_status.json", "w") as status_file:
            json.dump({"status": "healthy", "action": "NONE", "cpu": cpu_usage}, status_file)
        return {"status": "healthy", "action": "NONE"}
    
    print(f"\n[ALERT] Anomaly Detected! CPU is at {cpu_usage}%. Activating DevPro Gemini Agent...")
    
    # تقنية الـ RAG الحقيقية: قراءة كتيب الحلول حياً من الفايل
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
        # مناداة عقل الـ Gemini وإجباره على إخراج قرار الإصلاح حياً عبر الإنترنت
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        ai_decision = json.loads(response.text)
        
        # 🚨 إرسال الإشارة الحية الفورية لـ سارة لتقلب اللمبة للأحمر في الـ Dashboard
        with open("live_status.json", "w") as status_file:
            json.dump({"status": "danger", "action": "RESTART", "cpu": cpu_usage}, status_file)
            
        return ai_decision
    except Exception as e:
        return {"status": "danger", "action": "RESTART", "note": "Local fallback active"}

# --- [حلقة التشغيل الرئيسية والربط الفعلي للمشروع كاملاً] ---
if __name__ == "__main__":
    print("=========================================================")
    print("DevPro Integrated Core System Active. Monitoring Server...")
    print("=========================================================")
    time.sleep(1)
    
    try:
        # تشغيل شاشة عمر الحية الملونة مباشرة في الـ Terminal
        with Live(build_dashboard(), console=console, screen=False, refresh_per_second=4) as live:
            while True:
                # 1. تحديث اللوحة وقراءة الـ CPU الحقيقي من جهازكِ حياً
                current_panel = build_dashboard()
                live.update(current_panel)
                
                # 2. سحب آخر رقم CPU تم تسجيله في تاريخ كود عمر
                current_cpu = metrics.history_cpu[-1] if metrics.history_cpu else 0.0
                
                # 3. تمرير الرقم الحقيقي لعقل الـ AI (جيمناي) بتاعكِ
                ai_decision = process_server_metrics(current_cpu)
                
                # 4. لو الـ AI لقط ضغط وقرر ريستارت، ينفذ الأمر فوراً
                if ai_decision.get("action") == "RESTART":
                    console.print("\n[bold red]>>> [HEALING ACTION] Gemini ordered RESTART. Fixing Container...[/bold red]")
                    os.system("docker restart devpro-app-container")
                    time.sleep(2) # مهلة لاستقرار السيرفر بعد الإصلاح
                    
                time.sleep(1) # فحص مستمر كل ثانية
    except KeyboardInterrupt:
        console.print("\n[bold red]Monitoring stopped.[/bold red]")
        # تشغيل نظام الشارت بتاع عمر وتسييفه تلقائياً عند الإيقاف
        chart_path = save_usage_chart()
        if chart_path:
            console.print(f"[bold green]Usage chart saved:[/bold green] {chart_path}")
            open_file(chart_path)
