/* ============================================================
   WORKSHEET ENGINE — shared logic & templates
   ============================================================ */

/* ====================== TEMPLATE REGISTRY ====================== */
const WS_TEMPLATES = {
  standard: { columns: 2, workMinHeight: 80,  showWork: true,  showAns: true,  pagePaddingMM: 20, rowSpacing: 5,  answerKeyNewPage: true },
  compact:  { columns: 2, workMinHeight: 50,  showWork: true,  showAns: true,  pagePaddingMM: 15, rowSpacing: 3,  answerKeyNewPage: true },
  exam:     { columns: 1, workMinHeight: 120, showWork: true,  showAns: true,  pagePaddingMM: 25, rowSpacing: 8,  answerKeyNewPage: true },
  word:     { columns: 1, workMinHeight: 150, showWork: true,  showAns: true,  pagePaddingMM: 25, rowSpacing: 10, answerKeyNewPage: true },
  noWork:   { columns: 2, workMinHeight: 0,   showWork: false, showAns: false, pagePaddingMM: 15, rowSpacing: 2,  answerKeyNewPage: true }
};

/* ====================== UTILS & MATHJAX ====================== */
function wsTypeset(element) {
  if (window.MathJax && MathJax.typesetPromise) return MathJax.typesetPromise([element]);
  return Promise.resolve();
}

function wsShowError(msg) {
  console.error(msg);
  const el = document.getElementById("ws-container");
  if (el) el.innerHTML = `<div class="ws-error">${msg}</div>`;
  const loading = document.getElementById("ws-loading");
  if (loading) loading.textContent = "❌ Error";
}

/* ====================== RENDERERS ====================== */
function wsRenderPartsGrid(parts) {
  const cols = (window.WS_CONFIG?.template === "word" || window.WS_CONFIG?.template === "exam") ? 1 : 2;
  const rows = [];
  for (let i = 0; i < parts.length; i += cols) rows.push(parts.slice(i, i + cols));

  return `<div class="parts-grid">` +
    rows.map(row => `
      <div class="parts-row">
        ${row.map(p => `
          <div class="part-card${(p.is_wide || p.is_word) ? " part-card-wide" : ""}">
            <div class="part-header"><span class="part-label">${p.label})</span></div>
            <div class="part-question">\\(${p.question_latex}\\)</div>
            <div class="part-work"></div>
            <div class="part-ans-line">Ans: <span class="part-ans-blank"></span></div>
          </div>`).join("")}
      </div>`).join("") +
    `</div>`;
}

function wsRenderHeader(ws) {
  return `
<div class="ws-header">
  <div class="ws-header-row">
    <div class="ws-left">
      <div class="ws-title">${ws.title}</div>
    </div>
    <div class="ws-right">
      Date: ____________________
    </div>
  </div>
  <div class="ws-header-row">
    <div class="ws-left">
      Name: _________________
    </div>
    <div class="ws-right">
      Grade: ___________________
    </div>
  </div>
</div>`;
}

function wsRender(data) {
  const { worksheet: ws, exercises: exs } = data;
  const container = document.getElementById("ws-container");
  const templateClass = `template-${window.WS_CONFIG?.template || "standard"}`;

  const html = `<div class="ws-paper ${templateClass}">` +
    wsRenderHeader(ws) +
    wsRenderExercises(exs, ws) +
    wsRenderAnswerKey(exs) +
    `</div>`;

  container.innerHTML = html;
  wsTypeset(container);
}

function wsRenderExercises(exercises, ws) {
  return exercises.map(ex => {
    const diagram = ex.diagram_svg
      ? `<div class="ws-diagram">${ex.diagram_svg}</div>`
      : "";
    return `
    <div class="ws-exercise">
      <div class="ws-exercise-header">
        <span class="ws-exercise-num">Ex ${ex.number}.</span>
        <span class="ws-exercise-title">${ex.title}</span>
      </div>
      <div class="ws-instruction">${ex.instruction}</div>
      ${diagram}
      ${wsRenderPartsGrid(ex.parts)}
    </div>`;
  }).join("");
}

function wsRenderAnswerKey(exercises) {
  const items = exercises.flatMap(ex =>
    ex.parts.map(p => {
      const isLong = p.answer_latex.length > 30 || p.answer_latex.includes("text{");
      return `<div class="ws-ans-item${isLong ? " ws-ans-wide" : ""}">
        <span class="ws-ans-num">${ex.number}${p.label})</span> 
        <span class="ws-ans-val">\\(${p.answer_latex}\\)</span>
      </div>`;
    })
  ).join("");
  return `<div class="ws-answer-key">
    <div class="ws-answer-key-title">✅ Answer Key</div>
    <div class="ws-answer-key-grid">${items}</div>
  </div>`;
}

/* ====================== PYODIDE BOOT ====================== */
let _pyodide = null;

async function wsBoot() {
  const cfg = window.WS_CONFIG;
  if (!cfg) return;
  const loadingEl = document.getElementById("ws-loading");

  try {
    // 1. Load Pyodide
    if (!_pyodide) {
      loadingEl.textContent = "⏳ Loading Python...";
      _pyodide = await loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/" });
    }

    // 2. Fetch all shared assets from assets/ into Pyodide's
    //    virtual filesystem — makes imports work in any generator
    //    Load order matters: components first, then schema, renderer, svg
    loadingEl.textContent = "⏳ Loading helpers...";
    const _assetFiles = [
      "components.py",
      "exercise_schema.py",
      "renderer.py",
      "svg_helpers.py",
    ];
    for (const fname of _assetFiles) {
      try {
        const resp = await fetch(`../../assets/${fname}`);
        if (resp.ok) {
          _pyodide.FS.writeFile(fname, await resp.text());
        }
      } catch (e) {
        // Non-fatal — generators degrade gracefully if asset missing
        console.warn(`${fname} not loaded:`, e);
      }
    }

    // 3. Fetch and run the unit generator (e.g. Indices.py)
    loadingEl.textContent = "⏳ Loading generator...";
    const resp = await fetch(cfg.pyPath);
    const src  = await resp.text();
    await _pyodide.runPythonAsync(src);

    // 4. Generate first session
    await wsGenerate();
    document.getElementById("btn-ws-new").disabled = false;
    loadingEl.textContent = "✅ Ready";

  } catch (e) {
    wsShowError(`Boot failed: ${e.message}`);
  }
}

async function wsGenerate(seed = null) {
  const cfg = window.WS_CONFIG;
  const container = document.getElementById("ws-container");
  container.innerHTML = `<p style="text-align:center;padding:3rem;color:#94a3b8">Generating...</p>`;
  try {
    const seedArg = seed !== null ? `, seed=${seed}` : '';
    const raw = await _pyodide.runPythonAsync(`
import json
json.dumps(generate(types=${JSON.stringify(cfg.types)}, count=${cfg.count || 6}${seedArg}))
`);
    wsRender(JSON.parse(raw));
    await wsTypeset(container);   
  } catch (e) {
    wsShowError(`Generation Error: ${e.message}`);
  }
}
/* ====================== LAYOUT ENGINE ====================== */
class WorksheetLayoutEngine {
  constructor(config = {}) {
    this.templateName = config.template || "standard";
    this.template = WS_TEMPLATES[this.templateName] || WS_TEMPLATES.standard;
    this.wrapper = document.createElement("div");
    this.currentPage = null;
    this.usedHeight = 0;
    this.pageHeight = 950;
    this.measureBox = null;
  }

  async init() {
    await document.fonts.ready;
    this._createMeasureBox();
    this._newPage();
  }

  _createMeasureBox() {
    this.measureBox = document.createElement("div");
    this.measureBox.style.cssText = "position:fixed;left:-9999px;top:0;width:714px;visibility:hidden;";
    document.body.appendChild(this.measureBox);
  }

  _measure(node) {
    this.measureBox.innerHTML = "";
    this.measureBox.appendChild(node);
    return this.measureBox.offsetHeight;
  }

  _newPage() {
    if (this.currentPage) {
      this._addPageNumber(this.currentPage);
      const wrap = document.createElement("div");
      wrap.className = "ws-page-wrap";
      wrap.appendChild(this.currentPage);
      this.wrapper.appendChild(wrap);
    }
    this.currentPage = document.createElement("div");
    this.currentPage.className = `ws-preview-page template-${this.templateName}`;
    this.currentPage.style.padding = `${this.template.pagePaddingMM}mm`;
    this.usedHeight = 0;
    this._pageCount = (this._pageCount || 0) + 1;
  }

  _addPageNumber(page) {
    const num = document.createElement("div");
    num.className = "ws-page-number";
    num.textContent = this._pageCount || 1;
    page.appendChild(num);
  }

  _place(node) {
    const height = this._measure(node);
    if (this.usedHeight + height > this.pageHeight && this.usedHeight > 0) this._newPage();
    this.currentPage.appendChild(node.cloneNode(true));
    this.usedHeight += height;
  }

  _buildRow(cards) {
    const grid = document.createElement("div");
    grid.className = "parts-grid";
    const row = document.createElement("div");
    row.className = "parts-row";
    row.style.marginBottom = this.template.rowSpacing + "px";

    cards.forEach(card => {
      const clone = card.cloneNode(true);
      if (!this.template.showWork) {
        const work = clone.querySelector(".part-work");
        if (work) work.remove();
      } else {
        const work = clone.querySelector(".part-work");
        if (work) work.style.minHeight = this.template.workMinHeight + "px";
      }
      if (!this.template.showAns) {
        const ans = clone.querySelector(".part-ans-line");
        if (ans) ans.remove();
      }
      if (clone.classList.contains("part-card-wide")) {
        clone.style.gridColumn = "1 / -1";
      }
      row.appendChild(clone);
    });

    grid.appendChild(row);
    return grid;
  }

  _placeExercise(ex) {
    const header      = ex.querySelector(".ws-exercise-header");
    const instruction = ex.querySelector(".ws-instruction");
    const cards       = [...ex.querySelectorAll(".part-card")];
    if (!cards.length) return;

    const rows = this._chunk(cards, this.template.columns);

    // Header + instruction + first row — never split
    const firstBlock = document.createElement("div");
    firstBlock.className = "ws-exercise";
    if (header)      firstBlock.appendChild(header.cloneNode(true));
    if (instruction) firstBlock.appendChild(instruction.cloneNode(true));
    firstBlock.appendChild(this._buildRow(rows[0]));
    this._place(firstBlock);

    // Remaining rows
    for (let i = 1; i < rows.length; i++) {
      const rowBlock = document.createElement("div");
      rowBlock.className = "ws-exercise ws-exercise-continuation";
      rowBlock.appendChild(this._buildRow(rows[i]));
      this._place(rowBlock);
    }
  }

  _chunk(arr, size) {
    const out = [];
    for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
    return out;
  }

  build(sourceEl) {
    const paper      = sourceEl.querySelector(".ws-paper");
    if (!paper) return this.wrapper;

    const header     = paper.querySelector(".ws-header");
    const exercises  = [...paper.querySelectorAll(".ws-exercise")];
    const answerKey  = paper.querySelector(".ws-answer-key");

    if (header) this._place(header);
    exercises.forEach(ex => this._placeExercise(ex));

    if (this.currentPage.children.length) {
      const wrap = document.createElement("div");
      wrap.className = "ws-page-wrap";
      wrap.appendChild(this.currentPage);
      this.wrapper.appendChild(wrap);
    }

    if (answerKey && this.template.answerKeyNewPage) {
      const ansPage = document.createElement("div");
      ansPage.className = `ws-preview-page template-${this.templateName}`;
      ansPage.style.padding = `${this.template.pagePaddingMM}mm`;
      ansPage.appendChild(answerKey.cloneNode(true));
      const wrap = document.createElement("div");
      wrap.className = "ws-page-wrap";
      wrap.appendChild(ansPage);
      this.wrapper.appendChild(wrap);
    }

    return this.wrapper;
  }

  destroy() {
    if (this.measureBox) {
      document.body.removeChild(this.measureBox);
      this.measureBox = null;
    }
  }
}

document.addEventListener("DOMContentLoaded", wsBoot);

/* ============================================================
   PREVIEW
   ============================================================ */
async function wsOpenPreview() {
  const overlay = document.getElementById("ws-preview-overlay");
  const scroll  = document.getElementById("ws-preview-scroll");
  const source  = document.getElementById("ws-container");

  document.body.appendChild(overlay);
  overlay.classList.add("open");
  scroll.innerHTML = `<p style="color:white;text-align:center;padding:3rem">⏳ Formatting for A4...</p>`;

  await wsTypeset(source);
  if (window.MathJax?.startup?.promise) await MathJax.startup.promise;
  await new Promise(r => setTimeout(r, 300));

  scroll.innerHTML = "";

  const engine = new WorksheetLayoutEngine({ template: window.WS_CONFIG?.template || "standard" });
  await engine.init();
  const pages = engine.build(source);
  engine.destroy();

  scroll.appendChild(pages);
  await wsTypeset(scroll);
}

function wsClosePreview() {
  document.getElementById("ws-preview-overlay").classList.remove("open");
}

/* ============================================================
   PRINT
   ============================================================ */
async function wsPrint() {
  const scroll = document.getElementById("ws-preview-scroll");

  if (!scroll.querySelector(".ws-page-wrap")) {
    await wsOpenPreview();
  }

  await wsTypeset(scroll);
  if (window.MathJax?.startup?.promise) await MathJax.startup.promise;
  await new Promise(r => setTimeout(r, 500));

  const pagesHTML = scroll.innerHTML;
  const wsCSS     = await fetch("../../assets/worksheet.css").then(r => r.text());

  let mjCSS = "";
  for (const sheet of document.styleSheets) {
    try {
      const id   = sheet.ownerNode?.id   || "";
      const href = sheet.ownerNode?.href || "";
      if (id.includes("MathJax") || href.includes("mathjax") || href.includes("MathJax")) {
        mjCSS += [...sheet.cssRules].map(r => r.cssText).join("\n");
      }
    } catch (e) { /* cross-origin — skip */ }
  }
  if (!mjCSS) {
    document.querySelectorAll("style").forEach(s => {
      if (s.textContent.includes("mjx-") || s.id?.includes("MathJax")) {
        mjCSS += s.textContent;
      }
    });
  }

  const printDoc = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${window.WS_CONFIG?.title || "Worksheet"}</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; padding: 0; background: white; font-family: "DejaVu Sans", sans-serif; }
    @page { size: A4; margin: 0; }
    .ws-page-wrap {
      width: 210mm; height: 297mm;
      page-break-after: always; break-after: page; display: block;
    }
    .ws-page-wrap:last-child {
      page-break-after: avoid !important; break-after: avoid !important; height: auto;
    }
    .ws-preview-page {
      width: 210mm; padding: 20mm; box-sizing: border-box;
      background: white; display: block;
    }
    ${wsCSS}
    ${mjCSS}
  </style>
</head>
<body>${pagesHTML}</body>
</html>`;

  await new Promise((resolve) => {
    const iframe = document.createElement("iframe");
    iframe.style.cssText = "position:fixed;left:-9999px;width:210mm;height:297mm;border:none;";
    document.body.appendChild(iframe);

    iframe.onload = () => {
      setTimeout(() => {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
      }, 500);
    };

    iframe.contentWindow.addEventListener("afterprint", () => {
      document.body.removeChild(iframe);
      resolve();
    });

    iframe.contentDocument.open();
    iframe.contentDocument.write(printDoc);
    iframe.contentDocument.close();
  });
}