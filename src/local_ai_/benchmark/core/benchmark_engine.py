import requests
import time
import json
import os
import psutil
import platform

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

class BenchmarkRunner:
    def __init__(self, provider_url="http://localhost:11434/api/generate"):
        self.url = provider_url
        if NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
            except:
                pass

    def get_gpu_metrics(self):
        if not NVML_AVAILABLE:
            return {"vram_used": "N/A", "gpu_util": "N/A", "temp": "N/A"}
        
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            return {
                "vram_used": str(info.used // (1024**2)) + " MB",
                "gpu_util": str(util.gpu) + "%",
                "temp": str(temp) + "C"
            }
        except Exception:
            return {"vram_used": "Error", "gpu_util": "Error", "temp": "Error"}

    def run_benchmark(self, model, prompt):
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        start_time = time.time()
        try:
            response = requests.post(self.url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            
            total_time = time.time() - start_//time
            # Fixing potential variable name issue
            total_time = time.time() - start_time
            
            ttft = data.get('prompt_eval_duration', 0) / 1e9 if 'prompt_eval_duration' in data else total_time * 0.1
            eval_duration = data.get('eval_duration', 0) / 1e9 if 'eval_duration' in data else total_time
            tokens = data.get('eval_count', 0)
            tps = tokens / eval_duration if eval_duration > 0 else 0
            
            return {
                "model": model,
                "ttft": ttft,
                "total_time": total_time,
                "tokens": tokens,
                "tps": tps,
                "gpu": self.get_gpu_metrics(),
                "status": "success"
            }
        except Exception as e:
            return {"model": model, "status": "error", "error": str(e)}

class ReportGenerator:
    def generate_html(self, results, hardware_info, output_path):
        cpu = hardware_info.get('cpu', {}).get('model', 'N/A')
        ram = hardware_info.get('ram', {}).get('total', 'N/A')
        os_name = hardware_info.get('os', 'N/A')

        rows = ""
        for r in results:
            if r['status'] == 'success':
                gpu = r.get('gpu', {})
                vram = gpu.get('vram_used', 'N/A')
                util = gpu.get('gpu_util', 'N/A')
                rows += "<tr><td>" + str(r['model']) + "</td><td>" + f"{r.get('ttft', 0):.2f}s" + "</td><td>" + f"{r.get('tps', 0):.2f}" + "</td><td>" + str(r.get('tokens', 0)) + "</td><td>" + str(vram) + "</td><td>" + str(util) + "</td><td>" + r['status'] + "</td></tr>"
            else:
                rows += "<tr><td>" + str(r['model']) + "</td><td colspan='6'>" + str(r['error']) + "</td></tr>"

        html_start = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Local AI Benchmark Report</title>
    <style>
        body { background: #020202; color: #fff; font-family: 'Inter', sans-serif; padding: 40px; }
        .card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 20px; margin-bottom: 20px; }
        h1 { color: #00d2ff; text-align: center; margin-bottom: 40px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { color: #00d2ff; }
        .highlight { color: #00ff88; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Local AI Benchmark Report</h1>
    <div class="card">
        <h2 style="color:#00d2ff">System Profile</h2>
        <p>CPU: """ + str(cpu) + """</p>
        <p>RAM: """ + str(ram) + """ GB</p>
        <p>OS: """ + str(os_name) + """</p>
    </div>
    <div class="card">
        <h2 style="color:#00d2ff">Results</h2>
        <table>
            <tr><th>Model</th><th>TTFT</th><th>Tokens/s</th><th>Total Tokens</th><th>VRAM</th><th>GPU Util</th><th>Status</th></tr>
            """ + rows + """
        </table>
    </div>
</body>
</html>"""
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_start)
        return output_path

if __name__ == "__main__":
    hw = {
        "cpu": {"model": "Ryzen 3 3100"},
        "ram": {"total": 16},
        "os": "Windows 11"
    }
    
    runner = BenchmarkRunner()
    # Testing with a light model to ensure success
    results = [runner.run_benchmark("qwen2:0.5b", "Hello")]
    
    reporter = ReportGenerator()
    report_path = "C:\\Users\\Dayve\\Documents\\GitHub\\local-ai-benchmark\\benchmark_report.html"
    reporter.generate_html(results, hw, report_path)
    print(f"Report generated at: {report_path}")
