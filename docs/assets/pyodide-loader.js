/**
 * pyodide-loader.js
 * =================
 * Shared Pyodide manager for all exercise pages.
 * Loaded once globally via _quarto.yml.
 *
 * Usage in any .qmd file:
 *
 *   ExerciseLoader.init({
 *     containerId: "exercises-container",
 *     pythonCode:  PYTHON_CODE,        // string of Python source
 *     sections: [
 *       { key: "easy",   label: "🟢 Easy",   cls: "easy"   },
 *       { key: "medium", label: "🟡 Medium", cls: "medium" },
 *       { key: "word",   label: "🔵 Word",   cls: "word"   },
 *     ]
 *   });
 */

const ExerciseLoader = (() => {

  // ── Internal state ────────────────────────────────────────────────────
  let _pyodide     = null;
  let _ready       = false;
  let _readyQueue  = [];   // callbacks waiting for Pyodide to load
  let _config      = {};

  // ── Pyodide singleton ─────────────────────────────────────────────────
  async function _loadPyodide() {
    if (_pyodide) return _pyodide;
    _pyodide = await loadPyodide({
      indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/"
    });
    _ready = true;
    _readyQueue.forEach(fn => fn(_pyodide));
    _readyQueue = [];
    return _pyodide;
  }

  function _whenReady(fn) {
    if (_ready) fn(_pyodide);
    else _readyQueue.push(fn);
  }

  // ── Helpers ───────────────────────────────────────────────────────────
  function _mdBold(text) {
    return String(text).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  }

  function _sep() {
    return `<div class="math-sep"><p>∑ × π ÷ √ ◆ ∞ ± ∫ ≠ Δ</p></div>`;
  }

  function _setLoading(msg) {
    const el = document.getElementById("loading-msg");
    if (el) el.textContent = msg;
  }

  function _setRefreshBtn(disabled) {
    const btn = document.getElementById("btn-refresh");
    if (btn) btn.disabled = disabled;
  }

  // ── Render ────────────────────────────────────────────────────────────
  let _exCount = 0;

  function _renderExercises(session) {
    _exCount = 0;
    const sections = _config.sections || [];
    let html = "";

    sections.forEach((sec, si) => {
      const exercises = session[sec.key];
      if (!exercises || exercises.length === 0) return;

      html += `<div class="ex-section-title ${sec.cls}">${sec.label}</div>`;

      exercises.forEach((ex, ei) => {
        _exCount++;
        const id = `ex-${_exCount}`;
        if (ei > 0) html += _sep();
        html += _buildCard(id, ex);
      });

      // separator between sections
      const nextSec = sections[si + 1];
      if (nextSec && session[nextSec.key]?.length > 0) {
        html += _sep();
      }
    });

    const container = document.getElementById(_config.containerId);
    if (container) container.innerHTML = html;
  }

  function _buildCard(id, ex) {
    const solHtml = _mdBold(
      String(ex.solution || "").replace(/\n/g, "<br>")
    );
    return `
      <div class="exercise-card" id="card-${id}">
        <div class="ex-label">Exercise ${_exCount}</div>
        <div class="ex-question">${ex.question}</div>
        <div class="answer-row">
          <input class="answer-input" id="input-${id}"
                 type="text" placeholder="e.g. 3/4"
                 onkeydown="if(event.key==='Enter') ExerciseLoader.check('${id}','${ex.answer}')">
          <button class="btn btn-check no-print"
                  onclick="ExerciseLoader.check('${id}','${ex.answer}')">
            ✅ Check
          </button>
          <button class="btn btn-new no-print"
                  onclick="ExerciseLoader.clear('${id}')">
            🔁 Try Again
          </button>
          <button class="btn btn-show no-print"
                  onclick="ExerciseLoader.toggleSolution('sol-${id}', this)">
            🔍 Solution
          </button>
        </div>
        <div class="feedback" id="fb-${id}"></div>
        <div class="solution-box" id="sol-${id}">
          <strong>Solution:</strong><br>${solHtml}
        </div>
      </div>`;
  }

  // ── Public API ────────────────────────────────────────────────────────

  /**
   * init({ containerId, pythonCode, sections })
   * Called once per page to boot up the exercise loader.
   */
  async function init(config) {
    _config = config;

    _setLoading("⏳ Loading Python engine...");
    _setRefreshBtn(true);

    const container = document.getElementById(config.containerId);
    if (container) {
      container.innerHTML = '<p style="color:#94a3b8">Generating exercises...</p>';
    }

    try {
      const py  = await _loadPyodide();
      const raw = py.runPython(config.pythonCode);
      _renderExercises(JSON.parse(raw));

      _setRefreshBtn(false);
      _setLoading("✅ Python ready");
      setTimeout(() => {
        const msg = document.getElementById("loading-msg");
        if (msg) msg.style.display = "none";
      }, 2000);
    } catch (e) {
      _setLoading("❌ Error loading Python");
      console.error("[pyodide-loader]", e);
    }
  }

  /**
   * refresh()
   * Called by the New Session button.
   */
  async function refresh() {
    const container = document.getElementById(_config.containerId);
    if (container) {
      container.innerHTML = '<p style="color:#94a3b8">Generating new exercises...</p>';
    }
    _whenReady(async (py) => {
      const raw = await py.runPythonAsync("generate_session()");
      _renderExercises(JSON.parse(raw));
    });
  }

  /**
   * check(id, correctAnswer)
   * Validates a single exercise answer.
   */
  function check(id, correct) {
    _whenReady((py) => {
      const userInput = document.getElementById(`input-${id}`)?.value || "";
      py.globals.set("_u", userInput);
      py.globals.set("_c", correct);
      const raw = py.runPython("check_answer(_u, _c)");
      const fb  = document.getElementById(`fb-${id}`);
      if (!fb) return;

      if (raw === "correct") {
        fb.className   = "feedback correct";
        fb.textContent = "✅ Correct! Well done.";
      } else if (raw === "invalid") {
        fb.className   = "feedback warn";
        fb.textContent = "⚠️ Enter a valid fraction (e.g. 3/4) or whole number.";
      } else {
        fb.className   = "feedback wrong";
        fb.textContent = `❌ Not quite. The answer is ${raw.split(":")[1]}.`;
      }
    });
  }

  /**
   * clear(id)
   * Clears answer and feedback for a single exercise.
   */
  function clear(id) {
    const input = document.getElementById(`input-${id}`);
    const fb    = document.getElementById(`fb-${id}`);
    if (input) input.value   = "";
    if (fb)    { fb.textContent = ""; fb.className = "feedback"; }
  }

  /**
   * toggleSolution(id, btn)
   * Shows/hides the solution box.
   */
  function toggleSolution(id, btn) {
    const box     = document.getElementById(id);
    if (!box) return;
    const visible = box.style.display === "block";
    box.style.display = visible ? "none" : "block";
    if (btn) btn.textContent = visible ? "🔍 Solution" : "🙈 Hide";
  }

  // ── Expose public API ─────────────────────────────────────────────────
  return { init, refresh, check, clear, toggleSolution };

})();