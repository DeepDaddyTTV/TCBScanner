const icons = {
  check:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 6a6 6 0 1 1-5.2 9H4.6A8 8 0 1 0 4 12H1l4-4 4 4H6a6 6 0 0 1 6-6Z"/></svg>',
  download:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 4h2v8l3.3-3.3 1.4 1.4L12 15.8 6.3 10.1l1.4-1.4L11 12V4Zm-5 14h12v2H6v-2Z"/></svg>',
  pause:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7V5Zm6 0h4v14h-4V5Z"/></svg>',
  play:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7L8 5Z"/></svg>',
  trash:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 3h6l1 2h4v2H4V5h4l1-2Zm-2 6h10l-.8 11H7.8L7 9Z"/></svg>',
  retry:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.7 6.3A8 8 0 1 0 20 12h-2a6 6 0 1 1-1.8-4.2L13 11h8V3l-3.3 3.3Z"/></svg>',
};

const state = {
  series: [],
  selectedSeriesId: null,
  chapters: [],
  selectedChapterIds: new Set(),
};

const $ = (selector) => document.querySelector(selector);

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

async function refreshAll() {
  await loadSeries();
  if (state.selectedSeriesId) {
    await loadChapters(state.selectedSeriesId);
  }
  await loadEvents();
}

async function loadSeries() {
  const data = await api("/api/series");
  state.series = data.series;
  if (!state.selectedSeriesId && state.series.length) {
    state.selectedSeriesId = state.series[0].id;
  }
  if (state.selectedSeriesId && !state.series.some((item) => item.id === state.selectedSeriesId)) {
    state.selectedSeriesId = state.series[0]?.id ?? null;
  }
  renderSeries();
}

async function loadChapters(seriesId) {
  if (!seriesId) {
    state.chapters = [];
    state.selectedChapterIds.clear();
    renderChapters();
    return;
  }
  const data = await api(`/api/series/${seriesId}/chapters`);
  state.chapters = data.chapters;
  pruneSelectedChapters();
  renderChapters();
}

async function loadEvents() {
  const data = await api("/api/events");
  renderEvents(data.events);
}

function renderSeries() {
  const list = $("#seriesList");
  $("#seriesCount").textContent = `${state.series.length} tracked`;
  if (!state.series.length) {
    list.innerHTML = '<div class="empty-state">No series tracked yet.</div>';
    return;
  }
  list.innerHTML = state.series
    .map((series) => {
      const selected = series.id === state.selectedSeriesId ? " selected" : "";
      const enabled = series.enabled ? "enabled" : "paused";
      return `
        <article class="series-card${selected}" data-series-id="${series.id}">
          <div class="card-head">
            <div>
              <h3>${escapeHtml(series.title)}</h3>
              <p class="source-url">${escapeHtml(series.source_url)}</p>
            </div>
            <div class="series-status">
              <label class="monitor-toggle">
                <input type="checkbox" data-action="monitor" ${series.enabled ? "checked" : ""} />
                <span>Monitor</span>
              </label>
              <span class="status-pill status-${enabled}">${enabled}</span>
            </div>
          </div>
          <p class="path-text">${escapeHtml(series.folder)}</p>
          <div class="stats">
            ${stat(series.chapter_count, "found")}
            ${stat(series.downloaded_count, "cbz")}
            ${stat(series.pending_count, "queued")}
            ${stat(series.failed_count, "failed")}
          </div>
          <div class="actions">
            <button class="small-action" data-action="select" title="Show chapters">${icons.retry}<span>Open</span></button>
            <button class="small-action" data-action="check" title="Check now">${icons.check}<span>Check</span></button>
            <button class="small-action" data-action="download" title="Queue skipped and failed chapters">${icons.download}<span>Missing</span></button>
            <button class="small-action danger-action" data-action="delete" title="Delete series">${icons.trash}<span>Delete</span></button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderChapters() {
  const selected = state.series.find((item) => item.id === state.selectedSeriesId);
  $("#chapterTitle").textContent = selected ? selected.title : "Chapters";
  $("#chapterCount").textContent = selected
    ? `${state.chapters.length} chapter${state.chapters.length === 1 ? "" : "s"}`
    : "Select a series";
  const list = $("#chapterList");
  if (!selected) {
    renderSelectionTools();
    list.innerHTML = '<div class="empty-state">Select a series to see chapters.</div>';
    return;
  }
  if (!state.chapters.length) {
    renderSelectionTools();
    list.innerHTML = '<div class="empty-state">No chapters indexed yet.</div>';
    return;
  }
  renderSelectionTools();
  list.innerHTML = state.chapters
    .map((chapter) => {
      const selectable = isChapterSelectable(chapter);
      const checked = state.selectedChapterIds.has(chapter.id) ? "checked" : "";
      const selectBox = selectable
        ? `<input class="chapter-select" type="checkbox" data-chapter-id="${chapter.id}" ${checked} aria-label="Select ${escapeHtml(chapter.display_title)}" />`
        : '<span class="chapter-select-spacer"></span>';
      const retryButton =
        selectable
          ? `<button class="small-action" data-chapter-id="${chapter.id}" data-action="retry">${icons.retry}<span>Queue</span></button>`
          : "";
      const meta = [
        `Chapter ${escapeHtml(chapter.chapter_key)}`,
        chapter.page_count ? `${chapter.page_count} pages` : "",
        chapter.cbz_path ? escapeHtml(chapter.cbz_path) : "",
        chapter.error ? escapeHtml(chapter.error) : "",
      ]
        .filter(Boolean)
        .map((item) => `<span>${item}</span>`)
        .join("");
      return `
        <article class="chapter-row">
          <div class="chapter-content">
            ${selectBox}
            <div class="chapter-main">
              <h3>${escapeHtml(chapter.display_title)}</h3>
              <div class="chapter-meta">${meta}</div>
            </div>
          </div>
          <div class="actions">
            <span class="status-pill status-${escapeHtml(chapter.status)}">${escapeHtml(chapter.status)}</span>
            ${retryButton}
          </div>
        </article>
      `;
    })
    .join("");
}

function renderEvents(events) {
  const list = $("#eventList");
  if (!events.length) {
    list.innerHTML = '<div class="empty-state">No activity yet.</div>';
    return;
  }
  list.innerHTML = events
    .map(
      (event) => `
        <article class="event-row ${escapeHtml(event.level)}">
          <span class="event-dot"></span>
          <div class="event-copy">
            <p>${escapeHtml(event.message)}</p>
            <time>${formatDate(event.created_at)}</time>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderSelectionTools() {
  const tools = $("#chapterTools");
  const selectableCount = state.chapters.filter(isChapterSelectable).length;
  const selectedCount = countSelectedVisibleChapters();
  tools.classList.toggle("hidden", selectableCount === 0);
  $("#selectedCount").textContent = `${selectedCount} selected`;
  $("#queueSelectedChapters").disabled = selectedCount === 0;
  $("#selectVisibleChapters").disabled = selectableCount === 0;
  $("#clearSelectedChapters").disabled = selectedCount === 0;
}

function stat(value, label) {
  return `<div class="stat"><strong>${Number(value || 0)}</strong><span>${label}</span></div>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function isChapterSelectable(chapter) {
  return chapter.status === "failed" || chapter.status === "skipped";
}

function pruneSelectedChapters() {
  const selectableIds = new Set(state.chapters.filter(isChapterSelectable).map((chapter) => chapter.id));
  for (const chapterId of state.selectedChapterIds) {
    if (!selectableIds.has(chapterId)) {
      state.selectedChapterIds.delete(chapterId);
    }
  }
}

function countSelectedVisibleChapters() {
  const visibleIds = new Set(state.chapters.map((chapter) => chapter.id));
  return [...state.selectedChapterIds].filter((chapterId) => visibleIds.has(chapterId)).length;
}

$("#seriesForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = {
    source_url: String(form.get("source_url") || ""),
    title: String(form.get("title") || ""),
    folder: String(form.get("folder") || ""),
    check_interval_hours: Number(form.get("check_interval_hours") || 1),
    enabled: form.get("enabled") === "on",
    backfill_existing: form.get("backfill_existing") === "on",
  };
  await api("/api/series", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  event.currentTarget.reset();
  event.currentTarget.elements.enabled.checked = true;
  event.currentTarget.elements.check_interval_hours.value = 1;
  await refreshAll();
});

$("#refreshAll").addEventListener("click", refreshAll);

$("#seriesList").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const card = event.target.closest("[data-series-id]");
  const seriesId = Number(card?.dataset.seriesId);
  const action = button.dataset.action;
  if (!seriesId) return;

  if (action === "select") {
    state.selectedSeriesId = seriesId;
    await loadChapters(seriesId);
    renderSeries();
    return;
  }
  if (action === "check") {
    await api(`/api/series/${seriesId}/check`, { method: "POST" });
  }
  if (action === "download") {
    await api(`/api/series/${seriesId}/download-missing`, { method: "POST" });
  }
  if (action === "delete") {
    await api(`/api/series/${seriesId}`, { method: "DELETE" });
  }
  await refreshAll();
});

$("#seriesList").addEventListener("change", async (event) => {
  const input = event.target.closest("input[data-action='monitor']");
  if (!input) return;
  const card = event.target.closest("[data-series-id]");
  const seriesId = Number(card?.dataset.seriesId);
  if (!seriesId) return;
  await api(`/api/series/${seriesId}/enabled`, {
    method: "POST",
    body: JSON.stringify({ enabled: input.checked }),
  });
  await refreshAll();
});

$("#chapterList").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action='retry']");
  if (!button) return;
  await api(`/api/chapters/${Number(button.dataset.chapterId)}/retry`, { method: "POST" });
  await refreshAll();
});

$("#chapterList").addEventListener("change", (event) => {
  const input = event.target.closest(".chapter-select");
  if (!input) return;
  const chapterId = Number(input.dataset.chapterId);
  if (input.checked) {
    state.selectedChapterIds.add(chapterId);
  } else {
    state.selectedChapterIds.delete(chapterId);
  }
  renderSelectionTools();
});

$("#selectVisibleChapters").addEventListener("click", () => {
  for (const chapter of state.chapters.filter(isChapterSelectable)) {
    state.selectedChapterIds.add(chapter.id);
  }
  renderChapters();
});

$("#clearSelectedChapters").addEventListener("click", () => {
  for (const chapter of state.chapters) {
    state.selectedChapterIds.delete(chapter.id);
  }
  renderChapters();
});

$("#queueSelectedChapters").addEventListener("click", async () => {
  const selectedIds = state.chapters
    .filter((chapter) => state.selectedChapterIds.has(chapter.id) && isChapterSelectable(chapter))
    .map((chapter) => chapter.id);
  if (!state.selectedSeriesId || !selectedIds.length) return;
  await api(`/api/series/${state.selectedSeriesId}/queue-chapters`, {
    method: "POST",
    body: JSON.stringify({ chapter_ids: selectedIds }),
  });
  for (const chapterId of selectedIds) {
    state.selectedChapterIds.delete(chapterId);
  }
  await refreshAll();
});

refreshAll();
setInterval(refreshAll, 8000);
