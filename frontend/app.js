/**
 * HelvetiaVeritas v2.0 - Frontend Application Logic
 * ==================================================
 * Sovereign Swiss Multi-Cantonal Normalization & Federated Legal Alignment Pipeline
 * Connects to CSCS Alps Apertus 70B / 8B Multi-Tier Inference, ReportLab PDF Attestation,
 * and high-contrast Grandma Theory Swiss Dark UI.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements - Input & Controls
  const dialectInput = document.getElementById("dialect-input");
  const cantonHintSelect = document.getElementById("canton-hint-select");
  const charWordCounter = document.getElementById("char-word-counter");
  const clearBtn = document.getElementById("clear-btn");
  const submitBtn = document.getElementById("submit-btn");
  const submitBadge = document.getElementById("submit-badge");
  const presetsContainer = document.getElementById("presets-container");

  // Model Selection Elements
  const modelSwitch70b = document.getElementById("model-switch-70b");
  const modelSwitch8b = document.getElementById("model-switch-8b");
  const modelDescText = document.getElementById("model-desc-text");
  const headerStatusText = document.getElementById("header-status-text");

  // Telemetry Dashboard Elements
  const telemDuration = document.getElementById("telem-duration");
  const telemTokensSec = document.getElementById("telem-tokens-sec");
  const telemTtft = document.getElementById("telem-ttft");
  const telemModelTier = document.getElementById("telem-model-tier");

  // Output Elements
  const runtimeBadge = document.getElementById("runtime-badge");
  const runtimeText = document.getElementById("runtime-text");
  const normalizedOutput = document.getElementById("normalized-output");
  const copyNormalizedBtn = document.getElementById("copy-normalized-btn");

  // Cantonal Analysis Elements
  const cantonConfidence = document.getElementById("canton-confidence");
  const cantonFlagDisplay = document.getElementById("canton-flag-display");
  const cantonNameDisplay = document.getElementById("canton-name-display");
  const cantonDialectDisplay = document.getElementById("canton-dialect-display");
  const distZh = document.getElementById("dist-zh");
  const distBe = document.getElementById("dist-be");
  const distBs = document.getElementById("dist-bs");
  const distSg = document.getElementById("dist-sg");

  // Cantonal Gauges Elements
  const gaugeCardZh = document.getElementById("gauge-card-zh");
  const gaugePctZh = document.getElementById("gauge-pct-zh");
  const gaugeFillZh = document.getElementById("gauge-fill-zh");

  const gaugeCardBe = document.getElementById("gauge-card-be");
  const gaugePctBe = document.getElementById("gauge-pct-be");
  const gaugeFillBe = document.getElementById("gauge-fill-be");

  const gaugeCardBs = document.getElementById("gauge-card-bs");
  const gaugePctBs = document.getElementById("gauge-pct-bs");
  const gaugeFillBs = document.getElementById("gauge-fill-bs");

  const gaugeCardSg = document.getElementById("gauge-card-sg");
  const gaugePctSg = document.getElementById("gauge-pct-sg");
  const gaugeFillSg = document.getElementById("gauge-fill-sg");

  const lexicalTagsContainer = document.getElementById("lexical-tags-container");
  const phonologyList = document.getElementById("phonology-list");

  // Statutory Elements
  const primaryDomainBadge = document.getElementById("primary-domain-badge");
  const articlesListContainer = document.getElementById("articles-list-container");
  const proceduralCard = document.getElementById("procedural-card");
  const proceduralStepsList = document.getElementById("procedural-steps-list");

  // Attestation & Dossier Elements
  const hashInput = document.getElementById("hash-input");
  const hashNormalized = document.getElementById("hash-normalized");
  const hashComposite = document.getElementById("hash-composite");
  const hashSignature = document.getElementById("hash-signature");
  const downloadPdfBtn = document.getElementById("download-pdf-btn");
  const downloadAuditBtn = document.getElementById("download-audit-btn");
  const viewCertModalBtn = document.getElementById("view-cert-modal-btn");

  // Red Action Banner Elements
  const bannerTransformBtn = document.getElementById("banner-transform-btn");
  const bannerOpenReportBtn = document.getElementById("banner-open-report-btn");
  const heroStatusText = document.getElementById("hero-status-text");

  // Modal Elements
  const certModal = document.getElementById("cert-modal");
  const closeModalBtn = document.getElementById("close-modal-btn");
  const modalCloseActionBtn = document.getElementById("modal-close-action-btn");
  const modalDownloadPdfBtn = document.getElementById("modal-download-pdf-btn");
  const modalDownloadBtn = document.getElementById("modal-download-btn");
  const copyJsonBtn = document.getElementById("copy-json-btn");
  const modalAuditId = document.getElementById("modal-audit-id");
  const modalTimestamp = document.getElementById("modal-timestamp");
  const modalInfrastructure = document.getElementById("modal-infrastructure");
  const modalRegulation = document.getElementById("modal-regulation");
  const modalModel = document.getElementById("modal-model");
  const modalJsonContent = document.getElementById("modal-json-content");

  // State
  let currentResponse = null;
  let selectedModel = "apertus-1.5-70b";

  // Curated Fallback Presets
  const DEFAULT_PRESETS = [
    {
      id: "zh-tenancy-mold",
      title: "Zürich: Mietzinsstreit & Schimmel",
      canton: "ZH",
      category: "Mietrecht (Tenancy)",
      dialect_sample: "Sali zäme, mini Wöschchuchi isch sit zwoo Wuche voll Schimmel und d'Heizig im dritte Stock lauft nüüt meh ghörig. Ich han de Verwaltig scho drüü Mal aglüütet, aber die mached eifach nüüt und händ geschter sogar abghänkt! Chinde huested scho wägem Gstank. Ich han am 1. Oktober CHF 2'400.- Mietzins zahlt und wott jetzt wüsse, wie ich de Mietzins chan hinterlege oder reduziere."
    },
    {
      id: "be-building-permit",
      title: "Bern: Baueinsprache Autowerkstatt",
      canton: "BE",
      category: "Öffentliches Baurecht",
      dialect_sample: "Grüessech wohl, mir hei im Quartier vernoo, dass dr Nachber e grossi Autowerkstatt mit Spritzwärch ir Wohnzone boue wott. Äuä spint dä ganz! Dä Lärm u d'Abgas si für üsi Ching e Katastrophe. Mir wöi geng e ruhigi Wohnstrass bhalte u wüsse nid, bis wenn mir d'Einsprache bi dr Gmeind muesch ireiche u was für Paragraphe mir bruuche."
    },
    {
      id: "bs-labor-overtime",
      title: "Basel: Lohnausstand & Überstunden",
      canton: "BS",
      category: "Arbeitsrecht",
      dialect_sample: "Sälü zämme, ich bi geschter bim Schugger gsi, wäje mim Chef wo mir sit drei Mönet d'Überstunde (über 140 Stunde) nit zahlt und mir mit Kündigung droht, wenn ich nit ruehig bi. Er het gseit das sig vorig und mir händ kai Rächt druff. Daas cha doch nit verhebe vor Gricht! Ich bruuch e formelli Abmahnig für s'Arbeitsgricht."
    },
    {
      id: "sg-property-noise",
      title: "St. Gallen: Sonntags-Lärmbelästigung",
      canton: "SG",
      category: "Nachbarrecht",
      dialect_sample: "Hoi mitenand, de Nachber lauft d'Chreissägi jede Sunntig am Morge ab de Sibni diräkt bim Bomm a de Grundstücksgränze. Mir hend scho mehrmols gredt, aber er seit er heg s'Rächt dezue uf sim Grund. Das isch e Ruumstörig wo mer nöd länger dulde chönd. Ich bruuche e Verzeigig und e Unterlassigsklag bim Friedensrichter."
    }
  ];

  let presetsData = [...DEFAULT_PRESETS];

  // Helper: Update Character and Word Count
  function updateCounters() {
    if (!dialectInput || !charWordCounter) return;
    const text = dialectInput.value.trim();
    const chars = dialectInput.value.length;
    const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
    charWordCounter.textContent = `${chars} Zeichen • ${words} Wörter`;
  }

  // =====================================================================
  // 1. PRESET BUTTONS (ZH, BE, BS, SG)
  // =====================================================================
  function wireExistingPresetButtons() {
    if (!presetsContainer) return;
    const existingButtons = presetsContainer.querySelectorAll(".preset-btn");
    existingButtons.forEach(btn => {
      btn.onclick = () => {
        presetsContainer.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const presetId = btn.dataset.preset;
        if (presetId) {
          selectPreset(presetId, true);
        }
      };
    });
  }

  async function loadPresets() {
    wireExistingPresetButtons();
    try {
      const res = await fetch("/api/v1/presets");
      if (res.ok) {
        const fetched = await res.json();
        if (Array.isArray(fetched) && fetched.length > 0) {
          presetsData = fetched;
          renderPresetButtons();
        }
      }
    } catch {
      // Keep DEFAULT_PRESETS
    }
  }

  function renderPresetButtons() {
    if (!presetsContainer) return;
    const currentActive = presetsContainer.querySelector(".preset-btn.active")?.dataset.preset;
    presetsContainer.innerHTML = "";
    presetsData.forEach((preset, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      const isActive = currentActive ? preset.id === currentActive : idx === 0;
      btn.className = `preset-btn ${isActive ? "active" : ""}`;
      btn.dataset.preset = preset.id;
      btn.innerHTML = `
        <span class="canton-tag ${preset.canton.toLowerCase()}">${preset.canton}</span>
        <span>${preset.title.includes(":") ? preset.title.split(":")[1].trim() : preset.title}</span>
      `;
      btn.onclick = () => {
        presetsContainer.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        selectPreset(preset.id, true);
      };
      presetsContainer.appendChild(btn);
    });
  }

  function selectPreset(presetId, triggerPipeline = false) {
    const preset = presetsData.find(p => p.id === presetId) || DEFAULT_PRESETS.find(p => p.id === presetId);
    if (!preset || !dialectInput) return;

    dialectInput.value = preset.dialect_sample;
    if (cantonHintSelect) {
      cantonHintSelect.value = preset.canton;
    }
    updateCounters();

    // Trigger real-time heuristic parsing and normalization if requested
    if (triggerPipeline) {
      runPipeline();
    }
  }

  // Input listeners
  dialectInput?.addEventListener("input", updateCounters);
  clearBtn?.addEventListener("click", () => {
    if (dialectInput) {
      dialectInput.value = "";
      updateCounters();
      dialectInput.focus();
    }
  });

  // =====================================================================
  // 2. MODEL SELECTOR SWITCHER (70B vs 8B)
  // =====================================================================
  function updateModelSelection(modelKey) {
    selectedModel = modelKey;
    const is8b = modelKey === "apertus-1.5-8b";

    if (is8b) {
      modelSwitch8b?.classList.add("active");
      modelSwitch70b?.classList.remove("active");
      modelSwitch8b?.setAttribute("aria-checked", "true");
      modelSwitch70b?.setAttribute("aria-checked", "false");
      if (modelDescText) modelDescText.textContent = "Apertus 8B für extrem schnelle Mundart-Vorschau (<800ms)";
      if (submitBadge) submitBadge.textContent = "Apertus 8B (Fast)";
      if (telemModelTier) telemModelTier.textContent = "Apertus 8B (Fast)";
      if (headerStatusText) headerStatusText.textContent = "CSCS Alps (Lugano) • Apertus 8B Fast";
    } else {
      modelSwitch70b?.classList.add("active");
      modelSwitch8b?.classList.remove("active");
      modelSwitch70b?.setAttribute("aria-checked", "true");
      modelSwitch8b?.setAttribute("aria-checked", "false");
      if (modelDescText) modelDescText.textContent = "Apertus 70B für höchste juristische Präzision";
      if (submitBadge) submitBadge.textContent = "Apertus 70B";
      if (telemModelTier) telemModelTier.textContent = "Apertus 70B (Souverän)";
      if (headerStatusText) headerStatusText.textContent = "CSCS Alps (Lugano) • Apertus 70B Sovereign";
    }
  }

  modelSwitch70b?.addEventListener("click", () => updateModelSelection("apertus-1.5-70b"));
  modelSwitch8b?.addEventListener("click", () => updateModelSelection("apertus-1.5-8b"));

  // =====================================================================
  // 3. MAIN TRANSFORM PIPELINE ("Souverän Transformieren & Prüfen")
  // =====================================================================
  async function runPipeline(options = {}) {
    const rawText = dialectInput ? dialectInput.value.trim() : "";
    if (rawText.length < 5) {
      alert("Bitte geben Sie einen Text von mindestens 5 Zeichen ein.");
      return;
    }

    const cantonHint = cantonHintSelect ? cantonHintSelect.value || null : null;

    // Loading states
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <span class="btn-icon">⏳</span>
        <span>CSCS Alps Inferenz läuft...</span>
      `;
    }
    if (bannerTransformBtn) {
      bannerTransformBtn.disabled = true;
      bannerTransformBtn.innerHTML = `<span>⏳ Inferenz...</span>`;
    }
    if (heroStatusText) {
      heroStatusText.textContent = "Inferenz läuft...";
    }
    if (runtimeText) runtimeText.textContent = "Verarbeitung...";
    runtimeBadge?.querySelector(".runtime-dot")?.classList.remove("active");

    try {
      const response = await fetch("/api/v1/normalize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_dialect_text: rawText,
          canton_hint: cantonHint,
          model_selection: selectedModel
        })
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: "Verarbeitungsfehler aufgetreten" }));
        const msg = typeof err.detail === "string"
          ? err.detail
          : (Array.isArray(err.detail) ? err.detail.map(d => d.msg || JSON.stringify(d)).join("; ") : "Verarbeitungsfehler aufgetreten");
        throw new Error(msg);
      }

      currentResponse = await response.json();
      renderResults(currentResponse);

      if (heroStatusText) {
        heroStatusText.textContent = "Analyse abgeschlossen";
      }

      // If triggered by "Bericht öffnen", open modal immediately
      if (options.openModalOnSuccess) {
        openModal();
      }
    } catch (err) {
      alert(`Fehler bei der souveränen Transformation: ${err.message}`);
      if (runtimeText) runtimeText.textContent = "Fehler";
      if (heroStatusText) heroStatusText.textContent = "Fehler bei Inferenz";
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        const badgeText = selectedModel === "apertus-1.5-8b" ? "Apertus 8B (Fast)" : "Apertus 70B";
        submitBtn.innerHTML = `
          <span aria-hidden="true">⚖️</span>
          <span>Souverän Transformieren & Prüfen</span>
          <span class="btn-badge" id="submit-badge">${badgeText}</span>
        `;
      }
      if (bannerTransformBtn) {
        bannerTransformBtn.disabled = false;
        bannerTransformBtn.innerHTML = `<span>⚡ Jetzt Prüfen</span>`;
      }
    }
  }

  // Submit button listeners
  submitBtn?.addEventListener("click", () => runPipeline());

  // Red Action Banner shortcuts
  if (bannerTransformBtn) {
    bannerTransformBtn.addEventListener("click", () => runPipeline());
  }

  if (bannerOpenReportBtn) {
    bannerOpenReportBtn.addEventListener("click", () => {
      if (currentResponse) {
        openModal();
      } else {
        runPipeline({ openModalOnSuccess: true });
      }
    });
  }

  // =====================================================================
  // RENDER RESULTS
  // =====================================================================
  function renderResults(data) {
    // 1. Runtime & Inference Telemetry
    if (runtimeText) {
      runtimeText.textContent = `${data.processing_time_ms} ms • ${data.model_used.split("/").pop()}`;
    }
    runtimeBadge?.querySelector(".runtime-dot")?.classList.add("active");

    if (data.performance) {
      if (telemDuration) telemDuration.textContent = `${data.performance.total_duration_ms} ms`;
      if (telemTokensSec) telemTokensSec.textContent = `${data.performance.tokens_per_second} tok/s`;
      if (telemTtft) telemTtft.textContent = `${data.performance.ttft_ms} ms`;
      if (telemModelTier) {
        telemModelTier.textContent = data.performance.model_tier.includes("8b") ? "Apertus 8B (Fast)" : "Apertus 70B (Souverän)";
      }
    } else {
      if (telemDuration) telemDuration.textContent = `${data.processing_time_ms} ms`;
      if (telemModelTier) telemModelTier.textContent = data.model_used.split("/").pop();
    }

    // 2. Cantonal Heuristic Card
    const cAnalysis = data.canton_analysis;
    const confidencePct = Math.round(cAnalysis.confidence * 100);
    if (cantonConfidence) cantonConfidence.textContent = `${confidencePct}% Konfidenz`;
    if (cantonNameDisplay) cantonNameDisplay.textContent = `${cAnalysis.canton_name} (${cAnalysis.canton_code})`;
    if (cantonDialectDisplay) {
      cantonDialectDisplay.textContent = `${cAnalysis.dialect_name} • ${Math.round(cAnalysis.dialect_density * 100)}% Dialektdichte • Hauptort: ${cAnalysis.canton_name}`;
    }

    // Heraldic Coat of Arms
    const flagEmojis = {
      "ZH": "🔵⚪",
      "BE": "🐻",
      "BS": "⬛⚪",
      "SG": "🟢⚪"
    };
    if (cantonFlagDisplay) {
      cantonFlagDisplay.textContent = flagEmojis[cAnalysis.canton_code] || "🇨🇭";
    }

    // Distribution Bar & Percentages
    const dist = cAnalysis.distribution || { ZH: 0.25, BE: 0.25, BS: 0.25, SG: 0.25 };
    const pZH = Math.round((dist.ZH || 0) * 100);
    const pBE = Math.round((dist.BE || 0) * 100);
    const pBS = Math.round((dist.BS || 0) * 100);
    const pSG = Math.round((dist.SG || 0) * 100);

    if (distZh) distZh.style.width = `${pZH}%`;
    if (distBe) distBe.style.width = `${pBE}%`;
    if (distBs) distBs.style.width = `${pBS}%`;
    if (distSg) distSg.style.width = `${pSG}%`;

    const distLabels = document.querySelector(".distribution-labels");
    if (distLabels) {
      distLabels.innerHTML = `<span>ZH (${pZH}%)</span><span>BE (${pBE}%)</span><span>BS (${pBS}%)</span><span>SG (${pSG}%)</span>`;
    }

    // Cantonal Confidence Gauges
    if (gaugePctZh) gaugePctZh.textContent = `${pZH}%`;
    if (gaugeFillZh) gaugeFillZh.style.width = `${pZH}%`;
    if (gaugePctBe) gaugePctBe.textContent = `${pBE}%`;
    if (gaugeFillBe) gaugeFillBe.style.width = `${pBE}%`;
    if (gaugePctBs) gaugePctBs.textContent = `${pBS}%`;
    if (gaugeFillBs) gaugeFillBs.style.width = `${pBS}%`;
    if (gaugePctSg) gaugePctSg.textContent = `${pSG}%`;
    if (gaugeFillSg) gaugeFillSg.style.width = `${pSG}%`;

    [gaugeCardZh, gaugeCardBe, gaugeCardBs, gaugeCardSg].forEach(card => card?.classList.remove("active-canton"));
    const activeCode = cAnalysis.canton_code;
    if (activeCode === "ZH") gaugeCardZh?.classList.add("active-canton");
    else if (activeCode === "BE") gaugeCardBe?.classList.add("active-canton");
    else if (activeCode === "BS") gaugeCardBs?.classList.add("active-canton");
    else if (activeCode === "SG") gaugeCardSg?.classList.add("active-canton");

    // Lexical Marker Tags
    if (lexicalTagsContainer) {
      lexicalTagsContainer.innerHTML = "";
      if (cAnalysis.detected_markers && cAnalysis.detected_markers.length > 0) {
        cAnalysis.detected_markers.forEach(m => {
          const tag = document.createElement("span");
          tag.className = "marker-tag";
          tag.innerHTML = `
            <span class="marker-token">${m.token}</span>
            <span class="marker-arrow">→</span>
            <span class="marker-gloss">${m.gloss_de}</span>
          `;
          lexicalTagsContainer.appendChild(tag);
        });
      } else {
        lexicalTagsContainer.innerHTML = `<span class="empty-hint">Keine spezifischen dialektalen Lexeme identifiziert.</span>`;
      }
    }

    // Phonology List
    if (phonologyList) {
      phonologyList.innerHTML = "";
      if (cAnalysis.phonology_matches && cAnalysis.phonology_matches.length > 0) {
        cAnalysis.phonology_matches.forEach(rule => {
          const li = document.createElement("li");
          li.className = "phonology-item";
          li.innerHTML = `<strong>${rule.rule_name}:</strong> ${rule.description} <em>(Fundstellen: ${rule.matched_sample})</em>`;
          phonologyList.appendChild(li);
        });
      } else {
        phonologyList.innerHTML = `<li class="empty-hint">Standard-alemannische Phonologie ohne spezifische Verschiebungen.</li>`;
      }
    }

    // 3. Normalized High German Output
    if (normalizedOutput) {
      normalizedOutput.textContent = data.normalized_hochdeutsch;
    }

    // 4. Statutory Provisions (ZGB, OR, SchKG, DBG)
    const lAnalysis = data.legal_analysis;
    if (primaryDomainBadge) {
      primaryDomainBadge.textContent = `Hauptrechtsgebiet: ${lAnalysis.primary_domain}`;
    }

    if (articlesListContainer) {
      articlesListContainer.innerHTML = "";
      if (lAnalysis.matched_articles && lAnalysis.matched_articles.length > 0) {
        lAnalysis.matched_articles.forEach(art => {
          const row = document.createElement("div");
          row.className = "article-row";
          const relPct = Math.round(art.relevance_score * 100);
          row.innerHTML = `
            <div class="article-headline">
              <span class="article-badge-law">${art.law} Art. ${art.article_number}</span>
              <span class="article-name">${art.title_de}</span>
              <span class="article-relevance">${relPct}% Relevanz</span>
            </div>
            <p class="article-summary">${art.summary_de}</p>
            <div class="article-remedy">
              <strong>Handlungsempfehlung:</strong> ${art.remedy_action_de}
            </div>
            <div class="article-footer">
              <span class="article-authority">Zuständig: ${art.competent_authority}</span>
              <a href="${art.fedlex_url}" target="_blank" rel="noopener noreferrer" class="article-fedlex-link">
                Fedlex Gesetzestext ↗
              </a>
            </div>
          `;
          articlesListContainer.appendChild(row);
        });
      } else {
        articlesListContainer.innerHTML = `
          <div class="empty-card">Keine direkten Gesetzesartikel oberhalb des Relevanz-Schwellenwerts identifiziert.</div>
        `;
      }
    }

    // Procedural steps
    if (proceduralCard && proceduralStepsList) {
      if (lAnalysis.recommended_procedural_steps && lAnalysis.recommended_procedural_steps.length > 0) {
        proceduralCard.style.display = "block";
        proceduralStepsList.innerHTML = "";
        lAnalysis.recommended_procedural_steps.forEach(step => {
          const li = document.createElement("li");
          li.textContent = step;
          proceduralStepsList.appendChild(li);
        });
      } else {
        proceduralCard.style.display = "none";
      }
    }

    // 5. Cryptographic Attestation Card
    const cert = data.attestation;
    if (hashInput) hashInput.textContent = cert.input_sha256;
    if (hashNormalized) hashNormalized.textContent = cert.normalized_sha256;
    if (hashComposite) hashComposite.textContent = cert.pipeline_composite_hash;
    if (hashSignature) hashSignature.textContent = cert.signature_token;
  }

  // =====================================================================
  // 4. COPY BUTTON ("Kopieren")
  // =====================================================================
  async function copyNormalizedText() {
    if (!normalizedOutput || !copyNormalizedBtn) return;
    const text = normalizedOutput.textContent?.trim();
    if (!text || text.includes("Die durch das souveräne Modell")) return;

    let copied = false;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        copied = true;
      }
    } catch {
      // Fallback below
    }

    if (!copied) {
      try {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        ta.style.top = "-9999px";
        ta.setAttribute("readonly", "");
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        copied = document.execCommand("copy");
        document.body.removeChild(ta);
      } catch (err) {
        console.error("Fallback copy failed:", err);
      }
    }

    if (copied) {
      const origHtml = copyNormalizedBtn.innerHTML;
      copyNormalizedBtn.innerHTML = `<span>✓ Kopiert!</span>`;
      setTimeout(() => {
        copyNormalizedBtn.innerHTML = origHtml;
      }, 1800);
    }
  }

  copyNormalizedBtn?.addEventListener("click", copyNormalizedText);

  // =====================================================================
  // 5. AUDIT DOSSIER BUTTONS (.PDF & .JSON)
  // =====================================================================
  async function downloadAuditPdf() {
    if (!currentResponse) {
      await runPipeline();
    }
    if (!currentResponse) return;

    const btn = downloadPdfBtn;
    const origHtml = btn ? btn.innerHTML : "";
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span>⏳ Offizielles Dossier wird generiert...</span>`;
    }

    try {
      const res = await fetch("/api/v1/attest/pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(currentResponse)
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "PDF-Export fehlgeschlagen" }));
        throw new Error(err.detail || "Serverfehler beim PDF-Export");
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const auditId = (currentResponse.attestation && currentResponse.attestation.audit_id)
        ? currentResponse.attestation.audit_id.slice(0, 8)
        : "SOVEREIGN";
      a.download = `HelvetiaVeritas_Audit_Dossier_${auditId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Fehler beim PDF-Export: ${err.message}`);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origHtml;
      }
    }
  }

  async function downloadAuditJson() {
    if (!currentResponse) {
      await runPipeline();
    }
    if (!currentResponse) return;

    const auditData = {
      project: "HelvetiaVeritas v2.0 (CantonalAudit Enterprise)",
      track: "Hack Apertus - Track 1B: Swiss Voices",
      attestation: currentResponse.attestation,
      canton_classification: currentResponse.canton_analysis,
      legal_statutory_alignment: currentResponse.legal_analysis,
      raw_citizen_input: currentResponse.raw_input,
      normalized_schweizer_hochdeutsch: currentResponse.normalized_hochdeutsch,
      upstream_execution: {
        provider: currentResponse.upstream_provider,
        model: currentResponse.model_used,
        duration_ms: currentResponse.processing_time_ms,
        performance: currentResponse.performance
      }
    };

    const blob = new Blob([JSON.stringify(auditData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const auditId = (currentResponse.attestation && currentResponse.attestation.audit_id)
      ? currentResponse.attestation.audit_id.slice(0, 8)
      : "SOVEREIGN";
    a.download = `HelvetiaVeritas_Audit_${auditId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  downloadPdfBtn?.addEventListener("click", downloadAuditPdf);
  modalDownloadPdfBtn?.addEventListener("click", downloadAuditPdf);
  downloadAuditBtn?.addEventListener("click", downloadAuditJson);
  modalDownloadBtn?.addEventListener("click", downloadAuditJson);

  // =====================================================================
  // 6. SIDEBAR NAVIGATION ITEMS (TAB TOGGLING)
  // =====================================================================
  const navItems = document.querySelectorAll(".sidebar-nav .nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      navItems.forEach(n => {
        n.classList.remove("active");
        n.removeAttribute("aria-current");
        const ind = n.querySelector(".nav-active-indicator");
        if (ind) ind.remove();
      });
      item.classList.add("active");
      item.setAttribute("aria-current", "page");

      const indicator = document.createElement("span");
      indicator.className = "nav-active-indicator";
      indicator.setAttribute("aria-hidden", "true");
      item.appendChild(indicator);

      const target = item.getAttribute("href");
      if (target === "#berichte" || target === "#dokumente") {
        openModal();
      } else if (target === "#analysen") {
        document.getElementById("canton-card")?.scrollIntoView({ behavior: "smooth" });
      } else if (target === "#dashboard") {
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  });

  // =====================================================================
  // MODAL HANDLERS
  // =====================================================================
  function openModal() {
    if (!currentResponse) {
      runPipeline({ openModalOnSuccess: true });
      return;
    }
    const cert = currentResponse.attestation;
    if (modalAuditId) modalAuditId.textContent = cert.audit_id;
    if (modalTimestamp) modalTimestamp.textContent = cert.timestamp_iso;
    if (modalInfrastructure) modalInfrastructure.textContent = `${cert.supercomputer} (${cert.infrastructure})`;
    if (modalRegulation) modalRegulation.textContent = cert.fadp_revdsg_compliance;
    if (modalModel) modalModel.textContent = cert.model_id;

    if (modalJsonContent) {
      modalJsonContent.textContent = JSON.stringify(currentResponse, null, 2);
    }
    if (certModal) certModal.style.display = "flex";
  }

  function closeModal() {
    if (certModal) certModal.style.display = "none";
  }

  viewCertModalBtn?.addEventListener("click", openModal);
  closeModalBtn?.addEventListener("click", closeModal);
  modalCloseActionBtn?.addEventListener("click", closeModal);

  certModal?.addEventListener("click", (e) => {
    if (e.target === certModal) closeModal();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && certModal && certModal.style.display === "flex") {
      closeModal();
    }
  });

  copyJsonBtn?.addEventListener("click", () => {
    if (!modalJsonContent) return;
    const jsonStr = modalJsonContent.textContent;
    navigator.clipboard.writeText(jsonStr).then(() => {
      copyJsonBtn.textContent = "✓ Kopiert!";
      setTimeout(() => { copyJsonBtn.textContent = "JSON kopieren"; }, 1600);
    });
  });

  // =====================================================================
  // INITIALIZATION
  // =====================================================================
  loadPresets();
  updateCounters();

  // Pre-initialize baseline Zurich result if input matches default preset
  setTimeout(() => {
    if (dialectInput && dialectInput.value.length > 20 && !currentResponse) {
      runPipeline();
    }
  }, 250);
});
