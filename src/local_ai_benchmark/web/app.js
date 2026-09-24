const $ = (id) => document.getElementById(id);
const formatBytes = (bytes) => bytes == null ? "N/A" : `${(bytes / 1073741824).toFixed(2)} GB`;
const api = async (path, options = {}) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(path, { ...options, signal: controller.signal });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Local API error");
    return data;
  } catch (error) {
    if (error.name === "AbortError") throw new Error("The local API did not respond within 10 seconds");
    throw error;
  } finally {
    clearTimeout(timeout);
  }
};

function renderResults(results) {
  if (!results.length) return;
  $("results-empty").classList.add("hidden"); $("results-table").classList.remove("hidden");
  $("results-table").innerHTML = `<div class="result-row header"><span>Task</span><span>Speed</span><span>TTFT</span><span>Quality</span></div>` + results.map((item) => {
    const metrics = item.metrics || {}; const passed = item.passed === true;
    return `<div class="result-row"><div><strong>${item.task}</strong><small>${item.category}</small></div><div><strong>${metrics.tokens_per_second ?? "N/A"}</strong><small>tokens/s</small></div><div><strong>${metrics.time_to_first_token_seconds == null ? "N/A" : metrics.time_to_first_token_seconds.toFixed(3) + "s"}</strong><small>first token</small></div><div class="${passed ? "pass" : "fail"}"><strong>${item.passed == null ? "N/A" : passed ? "PASS" : "FAIL"}</strong><small>validator</small></div></div>`;
  }).join("");
}

async function loadDashboard() {
  const hardwareRequest = api("/api/system").then((hardware) => {
    const gpu = hardware.gpus?.[0];
    $("gpu-name").textContent = gpu?.name || "No GPU detected"; $("gpu-memory").textContent = gpu ? `${gpu.vram_total_mb / 1024} GB VRAM` : "N/A";
    $("ram-total").textContent = formatBytes(hardware.ram.total_bytes); $("ram-used").textContent = `${formatBytes(hardware.ram.used_bytes)} used`;
    $("cpu-name").textContent = hardware.cpu.model || "Unknown CPU"; $("cpu-threads").textContent = `${hardware.cpu.threads || "N/A"} threads`;
  }).catch((error) => {
    $("gpu-name").textContent = "Unavailable";
    $("gpu-memory").textContent = error.message;
  });
  const modelsRequest = api("/api/models").then((models) => {
    $("model-count").textContent = models.length; $("model-status").textContent = models.length ? "Ready to benchmark" : "No models installed";
    $("model-select").innerHTML = models.length ? models.map((model) => `<option value="${model.name}">${model.name}</option>`).join("") : '<option value="">No local models</option>';
    $("connection-label").textContent = "Ollama runtime online"; $("connection-label").previousElementSibling.classList.add("online");
  }).catch((error) => {
    $("model-count").textContent = "--";
    $("model-status").textContent = error.message;
    $("connection-label").textContent = "Ollama runtime unavailable";
  });
  api("/api/results").then(renderResults).catch(() => {});
  await Promise.all([hardwareRequest, modelsRequest]);
}

$("run-button").addEventListener("click", async () => { const model = $("model-select").value; if (!model) return; const button = $("run-button"); button.disabled = true; $("run-status").textContent = "Running local tasks. Keep this tab open..."; try { const results = await api("/api/run", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({ model, category:$("category-select").value }) }); renderResults(results); $("run-status").textContent = "Benchmark saved locally. Results shown below."; } catch (error) { $("run-status").textContent = error.message; } finally { button.disabled = false; } });
loadDashboard();