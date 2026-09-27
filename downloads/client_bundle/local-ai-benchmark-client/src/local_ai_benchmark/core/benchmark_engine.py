import requests
import time
import json
import os
import psutil
import platform
import ctypes

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

class HardwareProfiler:
    @staticmethod
    def get_system_info():
        try:
            cpu_info = platform.processor()
            if not cpu_info:
                import subprocess
                cpu_info = subprocess.check_output("wmic cpu get name", shell=True).decode().split('\n')[1].strip()
        except:
            cpu_info = "Unknown CPU"

        ram = psutil.virtual_memory().total // (1024**3)
        
        return {
            "cpu": cpu_info,
            "ram": ram,
            "os": platform.system() + " " + platform.release()
        }

class BenchmarkRunner:
    def __init__(self, provider_url="http://localhost:11434/api/generate"):
        self.url = provider_url
        self.gpu_initialized = False
        
        if NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.gpu_initialized = True
            except Exception:
                # Fallback: Try to load DLL manually if Init fails
                try:
                    ctypes.CDLL("C:\\Windows\\System32\\nvml.dll")
                    pynvml.nvmlInit()
                    self.gpu_initialized = True
                except:
                    self.gpu_initialized = False

    def get_gpu_metrics(self):
        if not self.gpu_initialized:
            return {"vram": "N/A", "util": "N/A", "temp": "N/A"}
        
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            return {
                "vram": f"{info.used // (1024**2)} MB",
                "util": f"{util.gpu}%",
                "temp": f"{temp}C"
            }
        except Exception as e:
            return {"vram": f"Err", "util": "Err", "temp": "Err"}

    def run(self, model, prompt):
        payload = {"model": model, "prompt": prompt, "stream": False}
        start = time.time()
        try:
            r = requests.post(self.url, json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            end = time.time()
            
            ttft = data.get('prompt_eval_duration', 0) / 1e9
            eval_dur = data.get('eval_duration', 0) / 1e9
            tokens = data.get('eval_count', 0)
            tps = tokens / eval_dur if eval_dur > 0 else 0
            
            return {
                "model": model,
                "ttft": ttft,
                "tps": tps,
                "tokens": tokens,
                "gpu": self.get_gpu_metrics(),
                "status": "OK"
            }
        except Exception as e:
            return {"model": model, "status": "Error", "error": str(e)}

class ReportGenerator:
    def generate(self, results, hw, path):
        cpu = hw.get('cpu', 'N/A')
        ram = hw.get('ram', 'N/A')
        os_name = hw.get('os', 'N/A')
        
        rows = ""
        for r in results:
            if r['status'] == "OK":
                gpu = r.get('gpu', {})
                rows += f"<tr><td>{r['model']}</td><td>{r['ttft']:.2f}s</td><td>{r['tps']:.2f}</td><td>{r['tokens']}</td><td>{gpu['vram']}</td><td>{gpu['util']}</td><td>OK</td></tr>"
            else:
                rows += f"<tr><td>{r['model']}</td><td colspan='6'>{r.get('error', 'Error')}</td></tr>"

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Local AI Benchmark Report</title>
    <style>
        body {{ background: #020202; color: #fff; font-family: 'Inter', sans-serif; padding: 40px; }}
        .card {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 20px; margin-bottom: 20px; }}
        h1 {{ color: #00d2ff; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        th {{ color: #00d2ff; }}
    </style>
</head>
<body>
    <h1 style="color:#00d2ff">REAL-TIME HARDWARE BENCHMARK</h1>
    <div class="card">
        <h2 style="color:#00d2ff">Detected System Profile</h2>
        <p>CPU: {cpu} | RAM: {ram} GB | OS: {os_name}</p>
    </div>
    <div class="card">
        <h2 style="color:#00d2ff">Execution Results</h2>
        <table>
            <tr><th>Model</th><th>TTFT</th><th>Tokens/s</th><th>Total Tokens</th><th>VRAM Used</th><th>GPU Util</th><th>Status</th></tr>
            {rows}
        </table>
    </div>
</body>
</html>"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

if __name__ == "__main__":
    profiler = HardwareProfiler()
    real_hw = profiler.get_system_info()
    
    runner = BenchmarkRunner()
    # Final test with qwen2:0.5b
    results = [runner.run("qwen2:0.5b", "Hello")]
    
    reporter = ReportGenerator()
    report_path = "C:\\Users\\Dayve\\Documents\\GitHub\\local-ai-benchmark\\benchmark_report.html"
    reporter.generate(results, real_hw, report_path)
    print(f"Report generated at: {report_path}")
