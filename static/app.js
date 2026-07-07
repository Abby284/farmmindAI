(function () {
  "use strict";

  /* ======================================================================
     FORM PAGE — pill selects, sliders, live field-profile preview
     ====================================================================== */

  const SEASON_TIPS = {
    kharif: "<b>Tip —</b> Kharif season (June–October) suits water-loving crops like rice, maize, and cotton, timed with the monsoon.",
    rabi: "<b>Tip —</b> Rabi season (November–March) favors cooler-weather crops like wheat, mustard, chickpea, and lentils.",
    zaid: "<b>Tip —</b> Zaid is a short summer window (April–June) — fast-growing crops with reliable irrigation do best here.",
    tropical: "<b>Tip —</b> Year-round tropical conditions open the door to spice and high-value crops like turmeric.",
    "semi-arid": "<b>Tip —</b> Semi-arid conditions reward drought-hardy, low-water crops like chickpea, groundnut, and sunflower."
  };

  function initPillGroups() {
    document.querySelectorAll("[data-pill-group]").forEach((group) => {
      const groupName = group.getAttribute("data-pill-group");
      const hidden = document.getElementById(groupName + "-input");
      group.querySelectorAll(".pill-option").forEach((btn) => {
        btn.addEventListener("click", () => {
          group.querySelectorAll(".pill-option").forEach((b) => b.classList.remove("active"));
          btn.classList.add("active");
          if (hidden) hidden.value = btn.getAttribute("data-value");
          updatePreview();
        });
      });
    });
  }

  function initSliders() {
    const ph = document.getElementById("ph");
    const phValue = document.getElementById("ph-value");
    if (ph && phValue) {
      ph.addEventListener("input", () => {
        phValue.textContent = parseFloat(ph.value).toFixed(1);
        updatePreview();
      });
    }
    const farmSize = document.getElementById("farm_size");
    const farmSizeValue = document.getElementById("farm-size-value");
    if (farmSize && farmSizeValue) {
      farmSize.addEventListener("input", () => {
        farmSizeValue.textContent = farmSize.value;
        updatePreview();
      });
    }
  }

  function initLiveInputs() {
    ["soil", "season", "rainfall", "temp", "goal"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("input", updatePreview);
    });
  }

  function updatePreview() {
    const form = document.getElementById("farm-form");
    if (!form) return;

    setPreview("soil", capitalize(val("soil")));
    setPreview("season", selectedText("season"));
    setPreview("rainfall", val("rainfall") ? `${val("rainfall")} mm` : "Not set");
    setPreview("temp", val("temp") ? `${val("temp")} °C` : "Not set");
    setPreview("ph", parseFloat(val("ph")).toFixed(1));
    setPreview("nitrogen", activePillText("nitrogen"));
    setPreview("water", activePillText("water"));
    setPreview("farm_size", `${val("farm_size")} acres`);
    setPreview("goal", selectedText("goal"));

    const tipEl = document.getElementById("preview-tip");
    if (tipEl) {
      const season = val("season");
      tipEl.innerHTML = SEASON_TIPS[season] || SEASON_TIPS.kharif;
    }
  }

  function val(id) {
    const el = document.getElementById(id);
    return el ? el.value : "";
  }
  function selectedText(id) {
    const el = document.getElementById(id);
    if (!el) return "";
    return el.options[el.selectedIndex] ? el.options[el.selectedIndex].textContent : "";
  }
  function activePillText(group) {
    const active = document.querySelector(`[data-pill-group="${group}"] .pill-option.active`);
    return active ? active.textContent : "";
  }
  function setPreview(key, text) {
    const el = document.getElementById("pv-" + key);
    if (el) el.textContent = text;
  }
  function capitalize(s) {
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : "";
  }

  /* ======================================================================
     RESULTS PAGE — tabs, crop card expand, animated bars, what-if lab
     ====================================================================== */

  function initTabs() {
    const tabs = document.querySelectorAll(".tab-btn");
    if (!tabs.length) return;
    tabs.forEach((btn) => {
      btn.addEventListener("click", () => {
        tabs.forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        const panel = document.getElementById("panel-" + btn.getAttribute("data-tab"));
        if (panel) panel.classList.add("active");
      });
    });
  }

  function initCropCards() {
    document.querySelectorAll("[data-crop-toggle]").forEach((head) => {
      head.addEventListener("click", () => {
        const card = head.closest(".crop-card");
        if (card) card.classList.toggle("open");
      });
    });
  }

  function animateMatchBars() {
    document.querySelectorAll(".match-bar-fill").forEach((fill) => {
      const target = fill.style.width;
      fill.style.width = "0%";
      requestAnimationFrame(() => {
        setTimeout(() => { fill.style.width = target; }, 60);
      });
    });
  }

  function getResultsData() {
    const el = document.getElementById("results-data");
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }

  function initWhatIf() {
    const buttons = document.querySelectorAll(".scenario-btn");
    const panel = document.getElementById("whatif-panel");
    if (!buttons.length || !panel) return;
    const data = getResultsData();
    if (!data) return;

    buttons.forEach((btn) => {
      btn.addEventListener("click", async () => {
        buttons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        panel.innerHTML = `<div class="whatif-empty"><span class="loading-spin"></span> &nbsp; Running scenario…</div>`;

        try {
          const res = await fetch("/whatif", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              inp: data.inp,
              scenario_id: btn.getAttribute("data-scenario-id"),
              orig_ranked: data.origRanked
            })
          });
          if (!res.ok) throw new Error("Request failed");
          const result = await res.json();
          renderWhatIf(panel, result);
        } catch (err) {
          panel.innerHTML = `<div class="whatif-empty">Couldn't run that scenario right now. Please try again.</div>`;
        }
      });
    });
  }

  function renderWhatIf(panel, result) {
    const mover = result.top_mover;
    const moverSign = mover.delta > 0 ? "+" : "";
    const rows = result.results.map((r) => {
      const cls = r.delta > 0 ? "delta-up" : (r.delta < 0 ? "delta-down" : "delta-flat");
      const sign = r.delta > 0 ? "+" : "";
      return `<tr>
        <td>#${r.rank}</td>
        <td>${r.crop_emoji} ${r.crop_name}</td>
        <td class="mono">${r.old_pct}%</td>
        <td class="mono">${r.new_pct}%</td>
        <td class="${cls}">${sign}${r.delta} pts</td>
      </tr>`;
    }).join("");

    panel.innerHTML = `
      <div class="whatif-result-head">
        <h4>Scenario: ${result.scenario}</h4>
        <span class="mover-badge">${mover.crop_emoji} ${mover.crop_name} moved most (${moverSign}${mover.delta} pts)</span>
      </div>
      <table class="whatif-table">
        <thead><tr><th>Rank</th><th>Crop</th><th>Before</th><th>After</th><th>Change</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    `;
  }

  /* ======================================================================
     INIT
     ====================================================================== */

  document.addEventListener("DOMContentLoaded", () => {
    initPillGroups();
    initSliders();
    initLiveInputs();
    updatePreview();

    initTabs();
    initCropCards();
    animateMatchBars();
    initWhatIf();
  });
})();
