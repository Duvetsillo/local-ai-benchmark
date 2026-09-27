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
  const hasResults = Array.isArray(results) && results.length > 0;
  $("results-empty").classList.toggle("hidden", hasResults);
  $("results-content").classList.toggle("hidden", !hasResults);

  if (!hasResults) return;

  const average = (values) => {
    const valid = values.filter((value) => typeof value === "number");
    return valid.length ? valid.reduce((total, value) => total + value, 0) / valid.length : null;
  };

  const avgSpeed = average(results.map((item) => item.metrics?.tokens_per_second));
  const avgTtft = average(results.map((item) => item.metrics?.time_to_first_token_seconds));
  const validations = results.filter((item) => typeof item.passed === "boolean");
  const passRate = validations.length ? (validations.filter((item) => item.passed).length / validations.length) * 100 : null;

  $("results-summary").innerHTML = `
    <div><span>AVG SPEED</span><strong>${avgSpeed == null ? "N/A" : avgSpeed.toFixed(2)} <small>tokens/s</small></strong></div>
    <div><span>AVG TTFT</span><strong>${avgTtft == null ? "N/A" : `${avgTtft.toFixed(3)}s`}</strong></div>
    <div><span>VALIDATION</span><strong>${passRate == null ? "N/A" : `${passRate.toFixed(0)}%`}</strong></div>
  `;

  $("results-table").innerHTML = `
    <div class="result-row header"><span>Task</span><span>Speed</span><span>TTFT</span><span>Quality</span></div>
    ${results.map((item) => {
      const metrics = item.metrics || {};
      const passed = item.passed === true;
      return `
        <div class="result-row">
          <div><strong>${item.task}</strong><small>${item.category}</small></div>
          <div><strong>${metrics.tokens_per_second ?? "N/A"}</strong><small>tokens/s</small></div>
          <div><strong>${metrics.time_to_first_token_seconds == null ? "N/A" : `${metrics.time_to_first_token_seconds.toFixed(3)}s`}</strong><small>first token</small></div>
          <div class="${passed ? "pass" : "fail"}"><strong>${item.passed == null ? "N/A" : passed ? "PASS" : "FAIL"}</strong><small>validator</small></div>
        </div>
      `;
    }).join("")}
  `;
}

async function loadDashboard() {
  const hardwareRequest = api("/api/system").then((hardware) => {
    const gpu = hardware.gpus?.[0];
    $("profile-os").textContent = hardware.os || "Unknown";
    $("profile-architecture").textContent = hardware.architecture || "Unknown";
    $("profile-cpu").textContent = hardware.cpu.model || "Unknown CPU";
    $("profile-cpu-spec").textContent = `${hardware.cpu.cores ?? "N/A"} cores / ${hardware.cpu.threads ?? "N/A"} threads`;
    $("profile-memory").textContent = formatBytes(hardware.ram.total_bytes);
    $("profile-memory-spec").textContent = `${formatBytes(hardware.ram.available_bytes)} available`;
    $("profile-gpu").textContent = gpu?.name || "No GPU detected";
    $("profile-gpu-spec").textContent = gpu ? `${(gpu.vram_total_mb / 1024).toFixed(1)} GB VRAM / ${gpu.temperature_c ?? "N/A"} C` : "N/A";
    $("gpu-name").textContent = gpu?.name || "No GPU detected";
    $("gpu-memory").textContent = gpu ? `${(gpu.vram_total_mb / 1024).toFixed(1)} GB VRAM` : "N/A";
    $("ram-total").textContent = formatBytes(hardware.ram.total_bytes);
    $("ram-used").textContent = `${formatBytes(hardware.ram.used_bytes)} used`;
    $("cpu-name").textContent = hardware.cpu.model || "Unknown CPU";
    $("cpu-threads").textContent = `${hardware.cpu.threads || "N/A"} threads`;
  }).catch((error) => {
    $("gpu-name").textContent = "Unavailable";
    $("gpu-memory").textContent = error.message;
  });

  const modelsRequest = api("/api/models").then((models) => {
    const options = models.length ? models.map((model) => `<option value="${model.name}">${model.name}</option>`).join("") : '<option value="">No local models</option>';
    $("model-count").textContent = String(models.length || 0);
    $("model-status").textContent = models.length ? "Ready to benchmark" : "No models installed";
    $("model-select").innerHTML = options;
    $("connection-label").textContent = "Ollama runtime online";
    const statusDot = $("connection-label").previousElementSibling;
    if (statusDot) statusDot.classList.add("online");
  }).catch((error) => {
    $("model-count").textContent = "--";
    $("model-status").textContent = error.message;
    $("connection-label").textContent = "Ollama runtime unavailable";
  });

  const resultsRequest = api("/api/results").catch(() => []);
  await Promise.all([hardwareRequest, modelsRequest]);
  const results = await resultsRequest;
  if (results[0]?.model) $("model-select").value = results[0].model;
  renderResults(results);
}

const runButton = $("run-button");
if (runButton) {
  runButton.addEventListener("click", async () => {
    const model = $("model-select").value;
    if (!model) return;

    const button = $("run-button");
    button.disabled = true;
    renderResults([]);
    $("run-status").textContent = "Running local tasks. Keep this tab open...";

    try {
      const results = await api("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model, category: $("category-select").value })
      });
      renderResults(results);
      $("run-status").textContent = "Benchmark saved locally. Results shown below.";
    } catch (error) {
      $("run-status").textContent = error.message;
    } finally {
      button.disabled = false;
    }
  });
}

loadDashboard();