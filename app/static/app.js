const icons = {
  check:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 6a6 6 0 1 1-5.2 9H4.6A8 8 0 1 0 4 12H1l4-4 4 4H6a6 6 0 0 1 6-6Z"/></svg>',
  download:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 4h2v8l3.3-3.3 1.4 1.4L12 15.8 6.3 10.1l1.4-1.4L11 12V4Zm-5 14h12v2H6v-2Z"/></svg>',
  folder:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7.5h6l2 2H21v8.5A2 2 0 0 1 19 20H5a2 2 0 0 1-2-2V7.5Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="miter"/><path d="M3 10h18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="square"/></svg>',
  pause:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7V5Zm6 0h4v14h-4V5Z"/></svg>',
  trash:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 3h6l1 2h4v2H4V5h4l1-2Zm-2 6h10l-.8 11H7.8L7 9Z"/></svg>',
  retry:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.7 6.3A8 8 0 1 0 20 12h-2a6 6 0 1 1-1.8-4.2L13 11h8V3l-3.3 3.3Z"/></svg>',
  pirate:
    '<svg viewBox="0 0 128 128" aria-hidden="true"><path d="M26 30 54 63M102 30 74 63" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/><path d="M19 104 54 63M109 104 74 63" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/><circle cx="18" cy="29" r="7" fill="none" stroke="currentColor" stroke-width="6"/><circle cx="110" cy="29" r="7" fill="none" stroke="currentColor" stroke-width="6"/><circle cx="18" cy="104" r="7" fill="none" stroke="currentColor" stroke-width="6"/><circle cx="110" cy="104" r="7" fill="none" stroke="currentColor" stroke-width="6"/><path d="M64 25c-19 0-34 13.6-34 31 0 12.1 7.2 22.3 17.5 27.1V96l7.2-5 9.3 6 9.3-6 7.2 5V83.1C90.8 78.3 98 68.1 98 56c0-17.4-15-31-34-31Z" fill="currentColor"/><path d="M51 56.5c0 4.8 3.6 8.5 8 8.5s8-3.7 8-8.5c0-4.5-3.5-8.3-8-8.3s-8 3.8-8 8.3Zm20 0c0 4.8 3.6 8.5 8 8.5s8-3.7 8-8.5c0-4.5-3.5-8.3-8-8.3s-8 3.8-8 8.3Z" fill="#f7f3eb"/><path d="m64 63.5-5 8h10l-5-8Z" fill="#f7f3eb"/><path d="M52 78h24c-2 7.7-6.9 13.5-12 13.5S54 85.7 52 78Z" fill="#f7f3eb"/><path d="M40 31c4.4-10.2 14.3-16.5 24-16.5S83.6 20.8 88 31l-13.8-.6c-2.5-2.9-6.1-4.8-10.2-4.8s-7.7 1.9-10.2 4.8L40 31Z" fill="#e2d0a6"/><path d="M33 32c7.8-8.2 18.8-12.8 31-12.8S87.2 23.8 95 32v5.8H33V32Z" fill="#e0c983"/><path d="M27 38h74c0 4.8-3.9 8.2-8.6 8.2H35.6C30.9 46.2 27 42.8 27 38Z" fill="#1c1713"/></svg>',
  moon:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 18a6 6 0 0 0 5.2-9A7.5 7.5 0 1 1 9 17.7 6 6 0 0 0 12 18Z"/></svg>',
  sun:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 2h2v3h-2V2Zm0 17h2v3h-2v-3ZM4.2 5.6l1.4-1.4 2.1 2.1-1.4 1.4-2.1-2.1Zm12.1 12.1 1.4-1.4 2.1 2.1-1.4 1.4-2.1-2.1ZM2 11h3v2H2v-2Zm17 0h3v2h-3v-2ZM5.6 19.8l-1.4-1.4 2.1-2.1 1.4 1.4-2.1 2.1ZM18.4 4.2l1.4 1.4-2.1 2.1-1.4-1.4 2.1-2.1ZM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10Z"/></svg>',
  chevronDown:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  search:
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10.5 4a6.5 6.5 0 1 1 0 13 6.5 6.5 0 0 1 0-13Zm9.2 15.3-4.1-4.1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square"/></svg>',
};

const CHAPTER_FILTERS = [
  {
    id: "all",
    label: "All",
    matches: () => true,
  },
  {
    id: "found",
    label: "Found",
    matches: (chapter) => chapter.status === "skipped",
  },
  {
    id: "queued",
    label: "Queued",
    matches: (chapter) => chapter.status === "pending" || chapter.status === "downloading",
  },
  {
    id: "downloaded",
    label: "Downloaded",
    matches: (chapter) => chapter.status === "downloaded",
  },
  {
    id: "failed",
    label: "Failed",
    matches: (chapter) => chapter.status === "failed",
  },
];

const JIKAN_API_BASE = "https://api.jikan.moe/v4";
const ART_CACHE_KEY = "tcbscanner-jikan-art-v4";
const ART_CACHE_TTL_MS = 1000 * 60 * 60 * 24;

const state = {
  series: [],
  events: [],
  meta: {
    version: "0.2.0",
    version_label: "0.2.0",
    supported_source_count: 0,
    supported_sources: [],
  },
  selectedSeriesId: null,
  chapters: [],
  selectedChapterIds: new Set(),
  settings: {
    default_naming_format: "{ChapterFullTitle}",
    variables: [],
  },
  chapterFilter: "all",
  chapterBulkOpen: false,
  lastRefreshAt: null,
  isRefreshing: false,
  seriesArt: {},
  artRequests: new Set(),
  libraryFilter: "",
  focusTab: "chapters",
  sidebarMode: "discover",
  sidebarHistory: [],
  sidebarHistoryLoading: false,
  sidebarHistoryLoadedFor: null,
  sidebarSearchQuery: "",
  sidebarSearchResults: {
    query: "",
    library_matches: [],
    source_matches: [],
  },
  sidebarSearching: false,
  sidebarSearchMessage: "",
  discoverDraft: defaultSeriesDraft(),
  editDraft: null,
  editDraftSeriesId: null,
  editDraftDirty: false,
};

const $ = (selector) => document.querySelector(selector);
const themeKey = "tcbscanner-theme-v4";
const legacyThemeKey = "tcbscanner-theme-v3";
const themeMediaQuery =
  typeof window.matchMedia === "function"
    ? window.matchMedia("(prefers-color-scheme: dark)")
    : null;
const themeLabels = {
  light: "Light",
  dark: "Dark",
  system: "System",
};
const relativeFormatter = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
let noticeTimer = null;
let artQueue = Promise.resolve();
state.seriesArt = loadArtCache();

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

function loadArtCache() {
  try {
    const parsed = JSON.parse(localStorage.getItem(ART_CACHE_KEY) || "{}");
    const now = Date.now();
    const entries = Object.entries(parsed).filter(([, value]) => {
      const cachedAt = Number(value?.cached_at || 0);
      return cachedAt && now - cachedAt < ART_CACHE_TTL_MS;
    });
    return Object.fromEntries(entries);
  } catch {
    return {};
  }
}

function persistArtCache() {
  try {
    localStorage.setItem(ART_CACHE_KEY, JSON.stringify(state.seriesArt));
  } catch {
    console.warn("Unable to persist artwork cache.");
  }
}

function normalizeSeriesKey(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function enqueueArtTask(task) {
  artQueue = artQueue
    .catch(() => undefined)
    .then(async () => {
      const result = await task();
      await wait(360);
      return result;
    });
  return artQueue;
}

async function fetchJson(url) {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Artwork lookup failed with ${response.status}.`);
  }
  return response.json();
}

function getArtworkForSeries(series) {
  if (!series) return null;
  const normalized = normalizeSeriesKey(series.title);
  return state.seriesArt[normalized] || null;
}

function selectArtworkUrl(entry, preferred = "hero") {
  if (!entry) return "";
  if (preferred === "hero") {
    return entry.hero_image_url || entry.cover_image_url || "";
  }
  return entry.cover_image_url || entry.hero_image_url || "";
}

function getSeriesCoverUrl(series, art) {
  return selectArtworkUrl(art, "cover") || getMockupCoverUrl(series) || "";
}

function getMockupCoverUrl(series) {
  const slug = normalizeSeriesKey(series?.title).replaceAll(" ", "-");
  if (slug === "one-piece") {
    return "/static/mockup_assets/series-one-piece-cover.png";
  }
  if (slug.startsWith("jujutsu-kaisen")) {
    return "/static/mockup_assets/series-jujutsu-cover.png";
  }
  return "";
}

function pickBestJikanMatch(title, candidates) {
  const target = normalizeSeriesKey(title);
  const targetWords = new Set(target.split(" ").filter(Boolean));
  let winner = null;
  let winnerScore = -Infinity;

  for (const candidate of candidates || []) {
    const candidateTitles = [
      candidate.title,
      candidate.title_english,
      ...(candidate.titles || []).map((item) => item.title),
    ]
      .filter(Boolean)
      .map(normalizeSeriesKey);

    let bestScore = -Infinity;
    for (const candidateTitle of candidateTitles) {
      const candidateWords = new Set(candidateTitle.split(" ").filter(Boolean));
      const overlap = [...targetWords].filter((word) => candidateWords.has(word)).length;
      let score = overlap * 22;
      if (candidateTitle === target) score += 180;
      if (candidateTitle.startsWith(target) || target.startsWith(candidateTitle)) score += 70;
      if (candidate.type === "Manga") score += 12;
      if (candidate.status === "Publishing") score += 8;
      score += Number(candidate.score || 0);
      bestScore = Math.max(bestScore, score);
    }

    if (bestScore > winnerScore) {
      winner = candidate;
      winnerScore = bestScore;
    }
  }

  return winner;
}

function buildArtEntry(candidate, existing = null) {
  const images = candidate?.images || {};
  const webp = images.webp || {};
  const jpg = images.jpg || {};
  return {
    cached_at: Date.now(),
    mal_id: candidate?.mal_id || existing?.mal_id || null,
    title: candidate?.title || existing?.title || "",
    mal_url: candidate?.url || existing?.mal_url || "",
    cover_image_url:
      webp.large_image_url ||
      webp.image_url ||
      jpg.large_image_url ||
      jpg.image_url ||
      existing?.cover_image_url ||
      "",
    hero_image_url: existing?.hero_image_url || "",
    pictures_hydrated: existing?.pictures_hydrated || false,
  };
}

function getPictureUrl(picture) {
  if (!picture) return "";
  return (
    picture?.webp?.large_image_url ||
    picture?.webp?.image_url ||
    picture?.jpg?.large_image_url ||
    picture?.jpg?.image_url ||
    ""
  );
}

async function fetchSeriesArtwork(series) {
  const cacheKey = normalizeSeriesKey(series.title);
  const cached = state.seriesArt[cacheKey];
  if (cached) {
    return cached;
  }

  const query = encodeURIComponent(series.title);
  const search = await fetchJson(`${JIKAN_API_BASE}/manga?q=${query}&limit=3`);
  const match = pickBestJikanMatch(series.title, search.data || []);
  if (!match) return null;

  const entry = buildArtEntry(match);
  state.seriesArt[cacheKey] = entry;
  persistArtCache();

  if (entry.mal_id) {
    void enqueueArtTask(() => hydrateHeroArtwork(cacheKey, entry.mal_id));
  }

  return entry;
}

async function hydrateHeroArtwork(cacheKey, malId) {
  const current = state.seriesArt[cacheKey];
  if (!current || current.pictures_hydrated) return current;

  try {
    const response = await fetchJson(`${JIKAN_API_BASE}/manga/${malId}/pictures`);
    const pictures = response.data || [];
    const pictureUrls = pictures.map(getPictureUrl).filter(Boolean);
    const coverUrl = pictureUrls[0] || current.cover_image_url;
    const heroUrl =
      pictureUrls.find((url) => url !== coverUrl) ||
      pictureUrls[1] ||
      coverUrl ||
      current.hero_image_url ||
      current.cover_image_url;

    state.seriesArt[cacheKey] = {
      ...current,
      cached_at: Date.now(),
      cover_image_url: coverUrl || current.cover_image_url,
      hero_image_url: heroUrl || current.cover_image_url,
      pictures_hydrated: true,
    };
    persistArtCache();
    renderArtwork();
    return state.seriesArt[cacheKey];
  } catch (error) {
    console.warn(error);
    return current;
  }
}

async function queueArtworkHydration(seriesList = state.series) {
  for (const series of seriesList) {
    const cacheKey = normalizeSeriesKey(series.title);
    if (state.seriesArt[cacheKey] || state.artRequests.has(cacheKey)) {
      continue;
    }

    state.artRequests.add(cacheKey);
    void enqueueArtTask(async () => {
      try {
        await fetchSeriesArtwork(series);
        renderArtwork();
      } catch (error) {
        console.warn(error);
      } finally {
        state.artRequests.delete(cacheKey);
      }
    });
  }
}

function renderArtwork() {
  renderBrandPanel();
  renderSeries();
  renderSeriesFocus();
}

function wait(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function defaultSeriesDraft(overrides = {}) {
  return {
    title: "",
    source_url: "",
    folder: "",
    check_interval_hours: "0.5",
    naming_format: "",
    enabled: true,
    backfill_existing: false,
    ...overrides,
  };
}

function seriesToDraft(series) {
  if (!series) {
    return defaultSeriesDraft();
  }
  return defaultSeriesDraft({
    title: String(series.title || ""),
    source_url: String(series.source_url || ""),
    folder: String(series.folder || ""),
    check_interval_hours: String(Math.max(0.5, Number(series.check_interval_minutes || 30) / 60)),
    naming_format: String(series.naming_format || ""),
    enabled: Boolean(series.enabled),
    backfill_existing: Boolean(series.backfill_existing),
  });
}

function ensureEditDraft(force = false) {
  const selected = getSelectedSeries();
  if (!selected) {
    state.editDraft = null;
    state.editDraftSeriesId = null;
    state.editDraftDirty = false;
    return;
  }
  if (
    force ||
    !state.editDraft ||
    state.editDraftSeriesId !== selected.id ||
    !state.editDraftDirty
  ) {
    state.editDraft = seriesToDraft(selected);
    state.editDraftSeriesId = selected.id;
    state.editDraftDirty = false;
  }
}

function setSidebarMode(mode) {
  state.sidebarMode = mode;
  if (mode === "settings") {
    ensureEditDraft();
  }
}

function setFocusTab(tab) {
  state.focusTab = tab;
  setSidebarMode(tab);
}

function resetDiscoverDraft(overrides = {}) {
  state.discoverDraft = defaultSeriesDraft(overrides);
}

function getDisplayedSeries() {
  const query = normalizeSeriesKey(state.libraryFilter);
  if (!query) return state.series;
  const queryTokens = query.split(" ").filter(Boolean);
  return state.series.filter((series) => {
    const haystack = `${normalizeSeriesKey(series.title)} ${normalizeSeriesKey(series.source_url)}`;
    return queryTokens.every((token) => haystack.includes(token));
  });
}

function getLibrarySearchMatches(query, limit = 8) {
  const normalized = normalizeSeriesKey(query);
  if (!normalized) return [];
  const queryTokens = normalized.split(" ").filter(Boolean);
  return [...state.series]
    .map((series) => {
      const title = normalizeSeriesKey(series.title);
      const source = normalizeSeriesKey(series.source_url);
      let score = 0;
      if (title === normalized) score += 220;
      if (title.startsWith(normalized)) score += 140;
      if (title.includes(normalized)) score += 90;
      if (source.includes(normalized)) score += 28;
      score += queryTokens.filter((token) => title.includes(token) || source.includes(token)).length * 22;
      return { series, score };
    })
    .filter((item) => item.score > 0)
    .sort((left, right) => right.score - left.score || compareSeries(left.series, right.series))
    .slice(0, Math.max(1, limit))
    .map((item) => item.series);
}

function setSearchMeta(message = "Search your tracked library first, then supported sources.") {
  const meta = $("#librarySearchMeta");
  if (meta) {
    meta.textContent = message;
  }
}

function syncLibrarySearchInput() {
  const input = $("#librarySearchInput");
  if (!input || document.activeElement === input) return;
  input.value = state.libraryFilter || "";
}

function getSelectedSeries() {
  return state.series.find((item) => item.id === state.selectedSeriesId) || null;
}

function syncSelectedSeries() {
  if (!state.selectedSeriesId && state.series.length) {
    state.selectedSeriesId = state.series[0].id;
    return;
  }
  if (state.selectedSeriesId && !state.series.some((item) => item.id === state.selectedSeriesId)) {
    state.selectedSeriesId = state.series[0]?.id ?? null;
    state.chapterFilter = "all";
  }
}

function compareSeries(left, right) {
  const leftHero = normalizeSeriesKey(left.title) === "one piece" ? 1 : 0;
  const rightHero = normalizeSeriesKey(right.title) === "one piece" ? 1 : 0;
  if (leftHero !== rightHero) {
    return rightHero - leftHero;
  }

  const chapterDelta = Number(right.chapter_count || 0) - Number(left.chapter_count || 0);
  if (chapterDelta) return chapterDelta;

  const checkedDelta =
    new Date(right.last_checked_at || 0).getTime() - new Date(left.last_checked_at || 0).getTime();
  if (checkedDelta) return checkedDelta;

  return String(left.title || "").localeCompare(String(right.title || ""));
}

async function fetchCoreState() {
  const [settingsData, seriesData, eventsData, metaData] = await Promise.all([
    api("/api/settings"),
    api("/api/series"),
    api("/api/events"),
    api("/api/meta"),
  ]);

  state.settings = settingsData;
  state.series = [...seriesData.series].sort(compareSeries);
  state.events = eventsData.events;
  state.meta = metaData;
  syncSelectedSeries();

  if (state.selectedSeriesId) {
    const chapterData = await api(`/api/series/${state.selectedSeriesId}/chapters`);
    state.chapters = chapterData.chapters;
  } else {
    state.chapters = [];
    state.selectedChapterIds.clear();
  }

  pruneSelectedChapters();
}

async function refreshAll({ quiet = false } = {}) {
  if (state.isRefreshing) return;
  state.isRefreshing = true;
  renderShellMeta();
  try {
    await fetchCoreState();
    state.lastRefreshAt = new Date();
    if (!quiet) {
      clearNotice();
    }
    renderAll();
    void queueArtworkHydration();
  } catch (error) {
    handleError(error, quiet ? "Background refresh failed." : "Unable to refresh scanner state.");
  } finally {
    state.isRefreshing = false;
    renderShellMeta();
  }
}

async function loadChaptersForSeries(seriesId) {
  if (!seriesId) {
    state.chapters = [];
    state.selectedChapterIds.clear();
    renderAll();
    return;
  }
  const data = await api(`/api/series/${seriesId}/chapters`);
  state.chapters = data.chapters;
  pruneSelectedChapters();
  renderAll();
  const selected = getSelectedSeries();
  if (selected) {
    void queueArtworkHydration([selected]);
  }
}

function renderAll() {
  renderBrandPanel();
  renderSettings();
  renderOverview();
  renderSeries();
  renderSeriesFocus();
  renderSidebar();
  syncLibrarySearchInput();
  renderFilters();
  renderChapters();
  renderEvents();
  renderShellMeta();
}

function renderBrandPanel() {
  const illustration = $("#brandIllustration");

  if (!illustration) return;
  illustration.innerHTML = "";
}

function renderSettings() {
  const optionsForm = $("#optionsForm");
  const optionsInput = optionsForm?.elements.default_naming_format;
  if (optionsInput && document.activeElement !== optionsInput) {
    optionsInput.value = state.settings.default_naming_format || "{ChapterFullTitle}";
  }

  const variables = $("#namingVariables");
  const variableMarkup = (state.settings.variables || [])
    .map(
      (variable) => `
        <article class="variable-item">
          <code>{${escapeHtml(variable.name)}}</code>
          <span>${escapeHtml(variable.description)}</span>
        </article>
      `,
    )
    .join("");
  variables.innerHTML = variableMarkup;

  const supportedSites = $("#supportedSitesList");
  if (supportedSites) {
    const groups = state.meta.supported_sources || [];
    supportedSites.innerHTML = groups.length
      ? groups
          .map(
            (group) => `
              <section class="supported-site-group">
                <div class="supported-site-group-head">
                  <strong>${escapeHtml(group.family || group.provider || "Supported sources")}</strong>
                  <span>${Number(group.count || 0)} site${Number(group.count || 0) === 1 ? "" : "s"}</span>
                </div>
                <div class="supported-site-list">
                  ${(group.sites || [])
                    .map(
                      (site) => `
                        <a
                          class="supported-site-link"
                          href="${escapeHtml(site.url || `https://${site.domain}/`)}"
                          target="_blank"
                          rel="noreferrer noopener"
                        >
                          <span>${escapeHtml(site.name || site.domain || "Unknown source")}</span>
                          <small>${escapeHtml(site.domain || "")}</small>
                        </a>
                      `,
                    )
                    .join("")}
                </div>
              </section>
            `,
          )
          .join("")
      : `
          <div class="inline-alert">
            <strong>No source metadata available</strong>
            <p>The current build did not return a supported-site list.</p>
          </div>
        `;
  }
}

function renderOverview() {
  const totals = state.series.reduce(
    (summary, series) => {
      summary.tracked += 1;
      summary.monitored += series.enabled ? 1 : 0;
      summary.indexed += Number(series.chapter_count || 0);
      summary.downloaded += Number(series.downloaded_count || 0);
      summary.queued += Number(series.pending_count || 0);
      summary.failed += Number(series.failed_count || 0);
      return summary;
    },
    { tracked: 0, monitored: 0, indexed: 0, downloaded: 0, queued: 0, failed: 0 },
  );

  $("#seriesCount").textContent = `${totals.tracked} tracked`;
  $("#overviewStats").innerHTML = `
    ${metricCard(totals.tracked, "total series", "in library")}
    ${metricCard(totals.monitored, "monitored", "active checks")}
    ${metricCard(totals.indexed, "total chapters", "indexed")}
  `;
  $("#libraryBreakdown").innerHTML = `
    ${breakdownRow("Found", totals.indexed, "neutral")}
    ${breakdownRow("Downloaded", totals.downloaded, "success")}
    ${breakdownRow("Queued", totals.queued, "accent")}
    ${breakdownRow("Failed", totals.failed, totals.failed ? "danger" : "neutral")}
  `;
}

function renderSeries() {
  const list = $("#seriesList");
  const displayedSeries = getDisplayedSeries();

  if (!state.series.length) {
    list.innerHTML = `
      <div class="empty-state">
        <strong>No tracked series yet</strong>
        <p>Add a title from the right rail to start indexing chapters and filling the queue.</p>
      </div>
    `;
    return;
  }

  if (!displayedSeries.length) {
    list.innerHTML = `
      <div class="empty-state">
        <strong>No tracked series match this search</strong>
        <p>Press Search to look across supported sites, or clear the filter to see your full library again.</p>
      </div>
    `;
    return;
  }

  list.innerHTML = displayedSeries
    .map((series) => {
      const isSelected = series.id === state.selectedSeriesId;
      const art = getArtworkForSeries(series);
      const coverUrl = getSeriesCoverUrl(series, art);
      const densityClass = getSeriesDensityClass(series.title);
      return `
        <article
          class="series-card${isSelected ? " selected" : ""}${densityClass}"
          data-series-id="${series.id}"
          data-series-slug="${escapeHtml(normalizeSeriesKey(series.title).replaceAll(" ", "-"))}"
          tabindex="0"
          role="button"
          aria-pressed="${isSelected ? "true" : "false"}"
        >
          <div class="series-cover${coverUrl ? "" : " fallback"}">
            ${
              coverUrl
                ? `<img src="${escapeHtml(coverUrl)}" alt="" loading="lazy" />`
                : `<div class="series-mark">${escapeHtml(seriesMark(series.title))}</div>`
            }
          </div>

          <div class="series-body">
            <div class="series-top">
              <div class="series-copy">
                <h3>${escapeHtml(series.title)}</h3>
                <p>${escapeHtml(getHostLabel(series.source_url))}</p>
              </div>
              <span class="status-pill status-${series.enabled ? "enabled" : "paused"}">
                ${series.enabled ? "Monitored" : "Paused"}
              </span>
            </div>

            <div class="series-stats">
              ${seriesInlineStat(series.chapter_count, "found")}
              ${seriesInlineStat(series.downloaded_count, "downloaded")}
              ${seriesInlineStat(series.pending_count, "queued")}
              ${seriesInlineStat(series.failed_count, "failed")}
            </div>

            <div class="series-meta">
              <span>${escapeHtml(formatCadence(series.check_interval_minutes))}</span>
              <span>${escapeHtml(formatRelativeTime(series.last_checked_at))}</span>
            </div>

            ${
              series.last_error
                ? `<p class="series-error">${escapeHtml(series.last_error)}</p>`
                : ""
            }
          </div>
        </article>
      `;
    })
    .join("");
}

function seriesInlineStat(value, label) {
  return `
    <span class="series-stat-inline series-stat-${escapeHtml(label)}">
      <i aria-hidden="true"></i>
      <strong>${Number(value || 0)}</strong>
    </span>
  `;
}

function renderSeriesFocus() {
  const panel = $("#selectedSeriesPanel");
  const selected = getSelectedSeries();

  if (!selected) {
    panel.innerHTML = `
      <div class="empty-state spacious">
        <strong>Choose a series to open the queue deck</strong>
        <p>The chapter workspace highlights naming rules, monitoring state, and the fastest actions for the selected title.</p>
      </div>
    `;
    return;
  }

  const statusClass = selected.enabled ? "enabled" : "paused";
  const statusText = selected.enabled ? "Monitored" : "Paused";
  const art = getArtworkForSeries(selected);
  const heroUrl = selectArtworkUrl(art, "hero") || selectArtworkUrl(art, "cover");
  const seriesSlug = normalizeSeriesKey(selected.title).replaceAll(" ", "-");
  const useMockupArt = seriesSlug === "one-piece";
  const focusArtUrl = useMockupArt ? "/static/mockup_assets/hero-art.png" : heroUrl;
  const focusDensityClass = getFocusDensityClass(selected.title);
  const focusEmblem = getFocusEmblem(selected, art, useMockupArt);
  const artStyle = focusArtUrl
    ? ` style="--focus-art: url('${focusArtUrl.replaceAll("'", "%27")}')"`
    : "";
  const namingPreview = getNamingPreview(selected);
  const sourceDisplay = formatSourceDisplay(selected.source_url);
  const folderDisplay = formatFolderDisplay(selected.folder || selected.title);

  panel.innerHTML = `
    <div class="focus-hero${useMockupArt ? " use-mockup-art" : ""}${focusDensityClass}" data-series-id="${selected.id}" data-series-slug="${escapeHtml(seriesSlug)}"${artStyle}>
      <div class="focus-watermark" aria-hidden="true"></div>
      <div class="focus-banner">
        <div class="focus-aside">
          <div class="${focusEmblem.className}" aria-hidden="true">${focusEmblem.markup}</div>
          <span class="status-pill status-${statusClass}">${statusText}</span>
        </div>
        <div class="focus-copy">
          <div class="focus-heading">
            <h2>${escapeHtml(selected.title)}</h2>
          </div>
          <p class="focus-detail focus-detail-source">
            <strong>Source:</strong>
            <a class="focus-link" href="${escapeHtml(selected.source_url)}" target="_blank" rel="noreferrer">
              ${escapeHtml(sourceDisplay)}
            </a>
          </p>
          <div class="focus-detail-grid">
            <span><strong>Library:</strong><em>${escapeHtml(selected.title)}</em></span>
            <span><strong>Folder:</strong><em>${escapeHtml(folderDisplay)}</em></span>
            <span><strong>Interval:</strong><em>${escapeHtml(formatInterval(selected.check_interval_minutes))}</em></span>
          </div>
          <p class="focus-detail focus-detail-naming"><strong>Naming:</strong><span>${escapeHtml(namingPreview)}</span></p>
          <div class="focus-tabs" aria-label="Series workspace sections">
            <button class="focus-tab${state.focusTab === "chapters" ? " active" : ""}" type="button" data-tab="chapters">Chapters</button>
            <button class="focus-tab${state.focusTab === "details" ? " active" : ""}" type="button" data-tab="details">Details</button>
            <button class="focus-tab${state.focusTab === "history" ? " active" : ""}" type="button" data-tab="history">History</button>
            <button class="focus-tab${state.focusTab === "files" ? " active" : ""}" type="button" data-tab="files">Files</button>
            <button class="focus-tab${state.focusTab === "settings" ? " active" : ""}" type="button" data-tab="settings">Settings</button>
          </div>
        </div>
        <div class="focus-art" aria-hidden="true"></div>
      </div>

      <div class="focus-actions sr-only" data-series-id="${selected.id}">
        <label class="monitor-toggle compact">
          <input type="checkbox" data-action="monitor" ${selected.enabled ? "checked" : ""} />
          <span>${selected.enabled ? "Monitor new chapters automatically" : "Series is currently paused"}</span>
        </label>

        <div class="focus-action-row">
          <button class="small-action" data-action="check">${icons.check}<span>Check now</span></button>
          <button class="small-action" data-action="download">${icons.download}<span>Queue missing</span></button>
          <button class="small-action danger-action" data-action="delete">${icons.trash}<span>Delete series</span></button>
        </div>
      </div>
    </div>
  `;
}

function renderSidebar() {
  const panel = $("#sidebarPanel");
  if (!panel) return;

  const selected = getSelectedSeries();
  if (state.sidebarMode === "settings") {
    ensureEditDraft();
  }

  if (state.sidebarMode === "discover") {
    panel.innerHTML = renderDiscoverSidebar();
    return;
  }

  if (!selected) {
    panel.innerHTML = `
      <div class="panel-heading">
        <div>
          <h2>Sidebar</h2>
          <p>Select a series from the left rail to open details, history, files, or settings here.</p>
        </div>
      </div>
      <div class="empty-state">
        <strong>No series selected</strong>
        <p>Use the tracked series list on the left, or press the plus button to search and add a new title.</p>
      </div>
    `;
    return;
  }

  if (state.sidebarMode === "details") {
    panel.innerHTML = renderDetailsSidebar(selected);
    return;
  }

  if (state.sidebarMode === "history") {
    panel.innerHTML = renderHistorySidebar(selected);
    return;
  }

  if (state.sidebarMode === "files") {
    panel.innerHTML = renderFilesSidebar(selected);
    return;
  }

  if (state.sidebarMode === "settings") {
    panel.innerHTML = renderSeriesSettingsSidebar(selected);
    return;
  }

  panel.innerHTML = renderChaptersSidebar(selected);
}

function renderDiscoverSidebar() {
  const results = state.sidebarSearchResults || { library_matches: [], source_matches: [] };
  const hasQuery = Boolean(state.sidebarSearchQuery.trim());
  const hasResults = results.library_matches.length || results.source_matches.length;
  return `
    <div class="panel-heading">
      <div>
        <h2>Add new series</h2>
        <p>Search your library first, then supported sites. Picking a site suggestion fills the form, but you can still change every setting before tracking it.</p>
      </div>
    </div>

    <div class="sidebar-block">
      <form class="series-search-form" id="sidebarSearchForm">
        <label class="field-span">
          <span>Series search</span>
          <div class="search-input-shell">
            <span class="search-input-icon" aria-hidden="true">${icons.search}</span>
            <input name="query" type="search" value="${escapeHtml(state.sidebarSearchQuery)}" placeholder="Search library or supported sites" autocomplete="off" />
          </div>
        </label>
        <button class="primary-action field-span" type="submit">
          ${icons.search}
          <span>${state.sidebarSearching ? "Searching..." : "Search"}</span>
        </button>
      </form>
      ${renderSearchResults(hasQuery, hasResults, results)}
    </div>

    ${renderSeriesForm({
      mode: "create",
      title: "Track series",
      description: "Use a search suggestion or paste a supported series URL manually.",
      draft: state.discoverDraft,
      submitLabel: "Track series",
      submitIcon: icons.download,
    })}
  `;
}

function renderChaptersSidebar(selected) {
  return `
    <div class="panel-heading">
      <div>
        <h2>Chapter actions</h2>
        <p>Queue, check, and monitor ${escapeHtml(selected.title)} from the sidebar.</p>
      </div>
    </div>
    <div class="sidebar-block">
      <div class="sidebar-series-summary">
        <strong>${escapeHtml(selected.title)}</strong>
        <span>${escapeHtml(getHostLabel(selected.source_url))}</span>
      </div>
      <div class="sidebar-stat-grid">
        ${miniStat(selected.chapter_count, "Found")}
        ${miniStat(selected.downloaded_count, "Downloaded")}
        ${miniStat(selected.pending_count, "Queued")}
        ${miniStat(selected.failed_count, "Failed")}
      </div>
      <label class="toggle-line">
        <input type="checkbox" data-sidebar-monitor="true" ${selected.enabled ? "checked" : ""} />
        <span>Keep monitoring this series for new chapters</span>
      </label>
      <div class="sidebar-action-stack">
        <button class="small-action" type="button" data-sidebar-action="check">
          ${icons.check}
          <span>Check now</span>
        </button>
        <button class="small-action" type="button" data-sidebar-action="download">
          ${icons.download}
          <span>Queue missing</span>
        </button>
        <button class="small-action danger-action" type="button" data-sidebar-action="delete">
          ${icons.trash}
          <span>Delete series</span>
        </button>
      </div>
      <div class="inline-alert">
        <strong>Queue summary</strong>
        <p>${escapeHtml(buildSeriesNote(selected))}</p>
      </div>
    </div>
  `;
}

function renderDetailsSidebar(selected) {
  return `
    <div class="panel-heading">
      <div>
        <h2>Series details</h2>
        <p>The selected title's current source, cadence, folder, and naming summary.</p>
      </div>
    </div>
    <div class="sidebar-detail-list">
      ${sidebarDetailRow("Library title", selected.title)}
      ${sidebarDetailRow("Source URL", `<a href="${escapeHtml(selected.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(selected.source_url)}</a>`)}
      ${sidebarDetailRow("Save folder", escapeHtml(formatFolderDisplay(selected.folder || selected.title)))}
      ${sidebarDetailRow("Check interval", escapeHtml(formatCadence(selected.check_interval_minutes)))}
      ${sidebarDetailRow("Naming format", escapeHtml(getNamingPreview(selected)))}
      ${sidebarDetailRow("Monitoring", selected.enabled ? "Enabled" : "Paused")}
      ${sidebarDetailRow("Backfill existing", selected.backfill_existing ? "Enabled" : "Disabled")}
      ${sidebarDetailRow("Last check", escapeHtml(formatDate(selected.last_checked_at) || "Not yet"))}
      ${selected.last_error ? sidebarDetailRow("Last error", escapeHtml(selected.last_error)) : ""}
    </div>
  `;
}

function renderHistorySidebar(selected) {
  if (state.sidebarHistoryLoading) {
    return `
      <div class="panel-heading">
        <div>
          <h2>Series history</h2>
          <p>Loading update, queue, download, and failure events for ${escapeHtml(selected.title)}.</p>
        </div>
      </div>
      <div class="empty-state">
        <strong>Loading history…</strong>
        <p>Recent events for this series are being collected now.</p>
      </div>
    `;
  }

  return `
    <div class="panel-heading">
      <div>
        <h2>Series history</h2>
        <p>Recent update, download, and failure events for ${escapeHtml(selected.title)}.</p>
      </div>
    </div>
    <div class="sidebar-history-list">
      ${
        state.sidebarHistory.length
          ? state.sidebarHistory
              .map(
                (event) => `
                  <article class="sidebar-history-row tone-${escapeHtml(eventTone(event))}">
                    <strong>${escapeHtml(summarizeEvent(event).title)}</strong>
                    <span>${escapeHtml(summarizeEvent(event).detail || event.message || "")}</span>
                    <time>${escapeHtml(formatRelativeTime(event.created_at))}</time>
                  </article>
                `,
              )
              .join("")
          : `
              <div class="empty-state">
                <strong>No series events yet</strong>
                <p>This title has not produced any dedicated update or download events yet.</p>
              </div>
            `
      }
    </div>
  `;
}

function renderFilesSidebar(selected) {
  const downloaded = [...state.chapters]
    .filter((chapter) => chapter.status === "downloaded" && chapter.cbz_path)
    .sort(
      (left, right) =>
        new Date(right.downloaded_at || right.discovered_at || 0).getTime() -
        new Date(left.downloaded_at || left.discovered_at || 0).getTime(),
    );

  return `
    <div class="panel-heading">
      <div>
        <h2>Downloaded files</h2>
        <p>Open or download packaged CBZ files for ${escapeHtml(selected.title)}.</p>
      </div>
    </div>
    <div class="sidebar-file-list">
      ${
        downloaded.length
          ? downloaded
              .map(
                (chapter) => `
                  <article class="sidebar-file-row">
                    <div>
                      <strong>${escapeHtml(chapter.display_title)}</strong>
                      <span>${escapeHtml(fileNameFromPath(chapter.cbz_path))}</span>
                    </div>
                    <div class="sidebar-file-meta">
                      <span>${escapeHtml(chapter.file_size_label || "—")}</span>
                      <a class="small-action" href="/api/chapters/${chapter.id}/file" target="_blank" rel="noreferrer">
                        ${icons.folder}
                        <span>Open CBZ</span>
                      </a>
                    </div>
                  </article>
                `,
              )
              .join("")
          : `
              <div class="empty-state">
                <strong>No downloaded files yet</strong>
                <p>Downloaded chapters will appear here as soon as packaging finishes.</p>
              </div>
            `
      }
    </div>
  `;
}

function renderSeriesSettingsSidebar(selected) {
  return renderSeriesForm({
    mode: "edit",
    title: "Series settings",
    description: `Change the tracked source, naming, monitoring cadence, and archive behavior for ${selected.title}.`,
    draft: state.editDraft || seriesToDraft(selected),
    submitLabel: "Save series settings",
    submitIcon: icons.check,
  });
}

function renderSearchResults(hasQuery, hasResults, results) {
  if (state.sidebarSearching) {
    return `
      <div class="inline-alert">
        <strong>Searching…</strong>
        <p>Checking your tracked library first, then supported site families.</p>
      </div>
    `;
  }
  if (!hasQuery) return "";
  if (!hasResults) {
    return `
      <div class="inline-alert">
        <strong>No matches found</strong>
        <p>Nothing in your tracked library or the searchable supported-site families matched that query. You can still paste a supported source URL below.</p>
      </div>
    `;
  }
  return `
    <div class="sidebar-search-results">
      <section class="sidebar-result-group">
        <div class="sidebar-result-heading">
          <strong>Library matches</strong>
          <span>${results.library_matches.length}</span>
        </div>
        ${
          results.library_matches.length
            ? results.library_matches
                .map(
                  (series) => `
                    <button class="sidebar-result-button" type="button" data-sidebar-select-series="${series.id}">
                      <strong>${escapeHtml(series.title)}</strong>
                      <span>${escapeHtml(getHostLabel(series.source_url))}</span>
                    </button>
                  `,
                )
                .join("")
            : `<p class="sidebar-result-empty">Nothing already tracked matched this query.</p>`
        }
      </section>
      <section class="sidebar-result-group">
        <div class="sidebar-result-heading">
          <strong>Supported site results</strong>
          <span>${results.source_matches.length}</span>
        </div>
        ${
          results.source_matches.length
            ? results.source_matches
                .map(
                  (match) => `
                    <button
                      class="sidebar-result-button"
                      type="button"
                      data-sidebar-source-url="${escapeHtml(match.url)}"
                      data-sidebar-source-title="${escapeHtml(match.title)}"
                      data-sidebar-source-site="${escapeHtml(match.site_name)}"
                    >
                      <strong>${escapeHtml(match.title)}</strong>
                      <span>${escapeHtml(match.site_name)} · ${escapeHtml(match.site_domain)}</span>
                    </button>
                  `,
                )
                .join("")
            : `<p class="sidebar-result-empty">No supported-source suggestions came back for that query.</p>`
        }
      </section>
    </div>
  `;
}

function renderSeriesForm({ mode, title, description, draft, submitLabel, submitIcon }) {
  const safeDraft = draft || defaultSeriesDraft();
  return `
    <div class="panel-heading">
      <div>
        <h2>${escapeHtml(title)}</h2>
        <p>${escapeHtml(description)}</p>
      </div>
    </div>

    <form class="series-form" id="seriesForm" data-mode="${escapeHtml(mode)}">
      <label class="field-span">
        <span>Source URL</span>
        <input name="source_url" type="url" required value="${escapeHtml(safeDraft.source_url)}" placeholder="https://example.com/manga" />
      </label>
      <label class="field-span">
        <span>Library title</span>
        <input name="title" type="text" required value="${escapeHtml(safeDraft.title)}" placeholder="e.g. My Hero Academia" />
      </label>
      <label class="field-span">
        <span>Save Folder</span>
        <input name="folder" type="text" value="${escapeHtml(safeDraft.folder)}" placeholder="D:\\Manga\\My Hero Academia" />
      </label>
      <label class="field-span">
        <span>Check interval</span>
        <span class="select-shell">
          <select name="check_interval_hours">
            ${renderIntervalOptions(String(safeDraft.check_interval_hours || "0.5"))}
          </select>
          <span class="select-caret" aria-hidden="true"></span>
        </span>
      </label>
      <label class="field-span">
        <span>Naming format</span>
        <input
          name="naming_format"
          type="text"
          value="${escapeHtml(safeDraft.naming_format)}"
          placeholder="{title} - c{chapter} - {title} [{scanlators}].cbz"
        />
      </label>
      <div class="variable-list compact field-span">
        ${renderCompactVariableTokens()}
      </div>
      <label class="toggle-line">
        <input name="backfill_existing" type="checkbox" ${safeDraft.backfill_existing ? "checked" : ""} />
        <span>Download every chapter already listed on first scan</span>
      </label>
      <label class="toggle-line">
        <input name="enabled" type="checkbox" ${safeDraft.enabled ? "checked" : ""} />
        <span>Keep monitoring this series for new chapters</span>
      </label>
      <button class="primary-action field-span" type="submit">
        ${submitIcon}
        <span>${escapeHtml(submitLabel)}</span>
      </button>
    </form>
  `;
}

function renderCompactVariableTokens() {
  return (state.settings.variables || [])
    .map(
      (variable) => `
        <article class="variable-item compact">
          <code>${escapeHtml(formatVariableToken(variable.name))}</code>
        </article>
      `,
    )
    .join("");
}

function renderIntervalOptions(selectedValue) {
  const options = [
    ["0.5", "30 minutes"],
    ["1", "1 hour"],
    ["2", "2 hours"],
    ["6", "6 hours"],
    ["12", "12 hours"],
    ["24", "24 hours"],
    ["48", "48 hours"],
    ["72", "72 hours"],
    ["168", "1 week"],
  ];
  return options
    .map(
      ([value, label]) =>
        `<option value="${value}" ${String(selectedValue) === String(value) ? "selected" : ""}>${label}</option>`,
    )
    .join("");
}

function sidebarDetailRow(label, value) {
  return `
    <article class="sidebar-detail-row">
      <span>${escapeHtml(label)}</span>
      <div>${value}</div>
    </article>
  `;
}

function getNamingPreview(series) {
  const raw = series?.naming_format || state.settings.default_naming_format || "";
  const seriesTitle = series?.title || "{series}";
  if (!raw) {
    return `${seriesTitle} Chapter {chapter} {chapter.title}.cbz`;
  }

  const preview = String(raw)
    .replaceAll("{ChapterFullTitle}", `${seriesTitle} Chapter {chapter} {chapter.title}`)
    .replaceAll("{SeriesName}", seriesTitle)
    .replaceAll("{SeriesTitle}", seriesTitle)
    .replaceAll("{ChapterNumberPadded}", "{chapter.pad}")
    .replaceAll("{ChapterNumber}", "{chapter}")
    .replaceAll("{ChapterTitle}", "{chapter.title}")
    .replaceAll("{ChapterName}", "{chapter.title}")
    .replaceAll("{PageCount}", "{pages}")
    .replaceAll("{Scanlator}", "{scanlators}")
    .replaceAll("{Group}", "{group}")
    .replaceAll("{Date}", "{date}");
  return preview.endsWith(".cbz") ? preview : `${preview}.cbz`;
}

function formatVariableToken(name) {
  const mapping = {
    ChapterFullTitle: "{title}",
    ChapterNumber: "{chapter}",
    ChapterNumberPadded: "{chapter.pad}",
    ChapterTitle: "{chapter.title}",
    ChapterName: "{chapter.title}",
    SeriesName: "{series}",
    SeriesTitle: "{series}",
    PageCount: "{pages}",
    Scanlator: "{scanlators}",
    Group: "{group}",
    Date: "{date}",
  };
  return mapping[name] || `{${name}}`;
}

function formatSourceDisplay(url) {
  try {
    return `https://${cleanHost(new URL(url).host)}`;
  } catch {
    return url;
  }
}

function cleanHost(host) {
  return String(host || "")
    .replace(/^www\./i, "")
    .replace(/^tcb(?=[a-z])/i, "");
}

function formatFolderDisplay(folder) {
  const value = String(folder || "").trim();
  if (!value) return "D:\\Manga\\Series";
  if (/[\\/]/.test(value)) return value;
  return `D:\\Manga\\${value}`;
}

function renderFilters() {
  const filters = $("#chapterFilters");
  const selected = getSelectedSeries();

  if (!selected) {
    filters.innerHTML = "";
    return;
  }

  filters.innerHTML = CHAPTER_FILTERS.map((filter) => {
    const count = state.chapters.filter(filter.matches).length;
    return `
      <button
        class="filter-pill${state.chapterFilter === filter.id ? " active" : ""}"
        type="button"
        data-filter="${filter.id}"
      >
        <span>${filter.label}</span>
        <strong>${count}</strong>
      </button>
    `;
  }).join("");
}

function renderChapters() {
  const selected = getSelectedSeries();
  const list = $("#chapterList");
  const head = $("#chapterListHead");
  const visibleChapters = getVisibleChapters();

  $("#chapterCount").textContent = buildChapterCountLabel(selected, visibleChapters.length);

  if (!selected) {
    head.classList.add("hidden");
    list.innerHTML = `
      <div class="empty-state">
        <strong>Queue is waiting for a series</strong>
        <p>Select a tracked title from the left rail to inspect skipped, queued, downloaded, and failed chapters.</p>
      </div>
    `;
    renderSelectionTools();
    return;
  }

  if (!state.chapters.length) {
    head.classList.add("hidden");
    list.innerHTML = `
      <div class="empty-state">
        <strong>No chapters indexed yet</strong>
        <p>Run a check for this series and the queue will populate as soon as chapters are discovered.</p>
      </div>
    `;
    renderSelectionTools();
    return;
  }

  if (!visibleChapters.length) {
    head.classList.add("hidden");
    list.innerHTML = `
      <div class="empty-state">
        <strong>No chapters match this filter</strong>
        <p>Switch filters to review other chapter states for ${escapeHtml(selected.title)}.</p>
      </div>
    `;
    renderSelectionTools();
    return;
  }

  head.classList.remove("hidden");
  list.innerHTML = visibleChapters
    .map((chapter) => {
      const selectable = isChapterSelectable(chapter);
      const checked = state.selectedChapterIds.has(chapter.id) ? "checked" : "";
      const addedLabel = chapterTimestampLabel(chapter);
      const addedTitle = chapterTimestampTitle(chapter);
      const titleText = chapterDisplayName(selected, chapter);
      return `
        <article class="chapter-row chapter-${escapeHtml(chapter.status)}">
          <div class="chapter-cell chapter-select-cell">
            ${
              selectable
                ? `<input class="chapter-select" type="checkbox" data-chapter-id="${chapter.id}" ${checked} aria-label="Select ${escapeHtml(chapter.display_title)}" />`
                : '<span class="chapter-select-spacer" aria-hidden="true"></span>'
            }
          </div>

          <div class="chapter-cell chapter-key">
            <span>${escapeHtml(chapter.chapter_key)}</span>
          </div>

          <div class="chapter-cell chapter-main">
            <h3>${escapeHtml(titleText)}</h3>
            <div class="chapter-meta">
              <span>${chapter.page_count ? `${Number(chapter.page_count)} pages` : "Awaiting download"}</span>
              ${
                chapter.cbz_path
                  ? `<span class="path-pill" title="${escapeHtml(chapter.cbz_path)}">${escapeHtml(fileNameFromPath(chapter.cbz_path))}</span>`
                  : ""
              }
              ${
                chapter.error
                  ? `<span class="error-pill" title="${escapeHtml(chapter.error)}">${escapeHtml(chapter.error)}</span>`
                  : ""
              }
            </div>
          </div>

          <div class="chapter-cell chapter-status-cell">
            <span class="status-pill status-${escapeHtml(chapter.status)}">${escapeHtml(statusLabel(chapter.status))}</span>
          </div>

          <div class="chapter-cell chapter-added-cell">
            <time title="${escapeHtml(addedTitle)}">${escapeHtml(addedLabel)}</time>
          </div>

          <div class="chapter-cell chapter-size-cell">
            <span>${escapeHtml(chapterSizeLabel(chapter))}</span>
          </div>

          <div class="chapter-cell chapter-action-cell">
            ${chapterActionMarkup(chapter, selectable)}
          </div>
        </article>
      `;
    })
    .join("");

  renderSelectionTools();
}

function chapterDisplayName(series, chapter) {
  const full = String(chapter.display_title || "").trim();
  const prefix = `${series?.title || ""} Chapter ${chapter.chapter_key}`.trim();
  if (full.toLowerCase().startsWith(prefix.toLowerCase())) {
    return full.slice(prefix.length).trim() || full;
  }
  return full;
}

function chapterSizeLabel(chapter) {
  if (chapter.file_size_label) return chapter.file_size_label;
  return "—";
}

function chapterActionMarkup(chapter, selectable) {
  if (chapter.status === "downloaded") {
    return `<a class="chapter-action-button" href="/api/chapters/${chapter.id}/file" target="_blank" rel="noreferrer" aria-label="Open chapter file">${icons.folder}</a>`;
  }
  if (chapter.status === "pending" || chapter.status === "downloading") {
    return `<button class="chapter-action-button" type="button" disabled aria-label="Queued chapter">${icons.pause}</button>`;
  }
  if (selectable) {
    return `<button class="chapter-action-button" data-chapter-id="${chapter.id}" data-action="retry" aria-label="${chapter.status === "failed" ? "Retry chapter" : "Queue chapter"}">${chapter.status === "failed" ? icons.retry : icons.download}</button>`;
  }
  return '<span class="chapter-action-spacer" aria-hidden="true"></span>';
}

function chapterTimestamp(chapter) {
  return chapter.downloaded_at || chapter.discovered_at || "";
}

function chapterTimestampLabel(chapter) {
  const stamp = chapterTimestamp(chapter);
  if (!stamp) return "Pending";
  return formatRelativeTime(stamp);
}

function chapterTimestampTitle(chapter) {
  const stamp = chapterTimestamp(chapter);
  if (!stamp) return "";
  return formatDate(stamp);
}

function renderEvents() {
  const list = $("#eventList");
  $("#activityStatus").textContent = state.events.length ? "Live" : "Idle";

  if (!state.events.length) {
    list.innerHTML = `
      <div class="empty-state">
        <strong>No activity yet</strong>
        <p>Checks, downloads, and errors will stream into this log as the worker runs.</p>
      </div>
    `;
    return;
  }

  list.innerHTML = state.events
    .map(
      (event) => {
        const tone = eventTone(event);
        const summary = summarizeEvent(event);
        return `
        <article class="event-row tone-${escapeHtml(tone)} ${escapeHtml(event.level)}">
          <time class="event-time">
            <strong>${escapeHtml(formatRelativeTime(event.created_at))}</strong>
            <span>${escapeHtml(formatDate(event.created_at))}</span>
          </time>
          <span class="event-dot"></span>
          <div class="event-copy">
            <strong>${escapeHtml(summary.title)}</strong>
            ${summary.detail ? `<span>${escapeHtml(summary.detail)}</span>` : ""}
          </div>
          <span class="event-more" aria-hidden="true"></span>
        </article>
      `;
      },
    )
    .join("");
}

function renderSelectionTools() {
  const tools = $("#chapterTools");
  const bulkToggle = $("#bulkActionsToggle");
  const bulkMenu = $("#chapterBulkMenu");
  const dock = $("#selectionDock");
  const selected = getSelectedSeries();
  const visibleChapters = getVisibleChapters();
  const selectableCount = visibleChapters.filter(isChapterSelectable).length;
  const selectedCount = countSelectedVisibleChapters();

  tools.classList.toggle("hidden", !selected);
  bulkToggle.disabled = !selectableCount && !selectedCount;
  bulkToggle.setAttribute("aria-expanded", String(state.chapterBulkOpen));
  bulkMenu.classList.toggle("hidden", !state.chapterBulkOpen || !selected);
  $("#selectVisibleChapters").disabled = !selectableCount;
  $("#clearSelectedChapters").disabled = !selectedCount;
  $("#queueSelectedChapters").disabled = !selectedCount;
  $("#selectedCount").textContent = `${selectedCount} selected`;

  dock.classList.toggle("hidden", !selectedCount);
  $("#selectionDockCount").textContent = `${selectedCount} selected`;
  $("#clearSelectedChaptersDock").disabled = !selectedCount;
  $("#queueSelectedChaptersDock").disabled = !selectedCount;
}

function summarizeEvent(event) {
  const raw = String(event.message || "").trim();
  const normalized = raw.toLowerCase();
  const chapterDetail = event.chapter_title
    ? composeEventDetail(event.series_title, trimSeriesPrefix(event.series_title, event.chapter_title))
    : event.series_title || raw;

  if (normalized.includes("no new chapters")) {
    return {
      title: "No new chapters",
      detail: event.series_title || raw,
    };
  }

  if (normalized.includes("queued")) {
    return {
      title: "Queued chapter",
      detail: chapterDetail,
    };
  }

  if (normalized.includes("downloaded")) {
    return {
      title: "Downloaded",
      detail: chapterDetail,
    };
  }

  if (normalized.includes("failed")) {
    return {
      title: "Failed to download",
      detail: chapterDetail || raw,
    };
  }

  if (normalized.includes("series added")) {
    return {
      title: "Series added",
      detail: event.series_title || raw,
    };
  }

  if (normalized.includes("monitoring")) {
    return {
      title: raw.replace(/\.$/, ""),
      detail: event.series_title || "",
    };
  }

  return {
    title: raw || "Scanner update",
    detail: event.series_title || "",
  };
}

function trimSeriesPrefix(seriesTitle, chapterTitle) {
  const full = String(chapterTitle || "").trim();
  const prefix = String(seriesTitle || "").trim().toLowerCase();
  if (!prefix || !full.toLowerCase().startsWith(prefix)) {
    return full;
  }
  return full
    .slice(String(seriesTitle || "").trim().length)
    .trim()
    .replace(/^chapter\s+/i, "c");
}

function composeEventDetail(seriesTitle, chapterDetail) {
  const series = String(seriesTitle || "").trim();
  const chapter = String(chapterDetail || "").trim();
  if (series && chapter) return `${series} - ${chapter}`;
  return series || chapter;
}

function eventTone(event) {
  const normalized = String(event.message || "").toLowerCase();
  if (event.level === "error" || normalized.includes("failed")) return "failed";
  if (normalized.includes("queued")) return "queued";
  if (normalized.includes("downloaded")) return "downloaded";
  if (normalized.includes("found") || normalized.includes("discovered") || normalized.includes("no new chapters")) return "found";
  return "info";
}

function toggleChapterBulkMenu(force) {
  if (typeof force === "boolean") {
    state.chapterBulkOpen = force;
  } else {
    state.chapterBulkOpen = !state.chapterBulkOpen;
  }
  renderSelectionTools();
}

function renderShellMeta() {
  const refreshButton = $("#refreshAll");
  refreshButton.classList.toggle("is-spinning", state.isRefreshing);
  refreshButton.disabled = state.isRefreshing;

  if (state.isRefreshing) {
    $("#shellStatus").textContent = "Refreshing scanner state…";
    return;
  }

  const monitored = state.series.filter((series) => series.enabled).length;
  const queued = state.series.reduce((sum, series) => sum + Number(series.pending_count || 0), 0);
  const failed = state.series.reduce((sum, series) => sum + Number(series.failed_count || 0), 0);

  if (!state.series.length) {
    $("#shellStatus").textContent = "No monitored series yet. Add a title to begin scanning.";
  } else {
    const pieces = [
      `${monitored} active monitor${monitored === 1 ? "" : "s"}`,
      `${queued} queued`,
      `${failed} failed`,
    ];
    $("#shellStatus").textContent = pieces.join(" · ");
  }

  $("#lastSync").textContent = state.lastRefreshAt ? formatRelativeTime(state.lastRefreshAt) : "Not yet";
  renderStatusStrip();
}

function metricCard(value, label, meta) {
  return `
    <article class="metric-card">
      <span>${escapeHtml(label)}</span>
      <strong>${Number(value || 0)}</strong>
      <p>${escapeHtml(meta)}</p>
    </article>
  `;
}

function breakdownRow(label, value, tone) {
  return `
    <div class="breakdown-row tone-${escapeHtml(tone)}">
      <span>${escapeHtml(label)}</span>
      <strong>${Number(value || 0)}</strong>
    </div>
  `;
}

function miniStat(value, label) {
  return `
    <div class="mini-stat">
      <strong>${Number(value || 0)}</strong>
      <span>${escapeHtml(label)}</span>
    </div>
  `;
}

function buildSeriesNote(series) {
  if (Number(series.failed_count || 0) > 0) {
    return "This series has failed chapters waiting for a retry. Review the queue and re-run the misses once the source is healthy.";
  }
  if (Number(series.pending_count || 0) > 0) {
    return "Downloads are already queued for this title. The worker will continue packaging chapters into CBZ files in order.";
  }
  return "This title looks clean right now. Run a manual check if you want to force discovery ahead of the normal interval.";
}

function buildChapterCountLabel(selected, visibleCount) {
  if (!selected) {
    return "Select a series to see the queue.";
  }
  if (!state.chapters.length) {
    return "No chapters indexed yet.";
  }

  const total = state.chapters.length;
  if (state.chapterFilter === "all") {
    return `${total} chapter${total === 1 ? "" : "s"} in the queue.`;
  }
  return `${visibleCount} visible of ${total} indexed chapters.`;
}

function getVisibleChapters() {
  const activeFilter = CHAPTER_FILTERS.find((item) => item.id === state.chapterFilter) || CHAPTER_FILTERS[0];
  return state.chapters.filter(activeFilter.matches);
}

function normalizeThemeChoice(theme) {
  return ["light", "dark", "system"].includes(theme) ? theme : "light";
}

function resolveThemeChoice(theme) {
  if (theme === "system") {
    return themeMediaQuery?.matches ? "dark" : "light";
  }
  return theme;
}

function syncThemeSelector(theme) {
  const value = $("#themeSelectorValue");
  if (value) {
    value.textContent = themeLabels[theme] || themeLabels.light;
  }

  const icon = $("#themeModeIcon");
  if (icon) {
    icon.dataset.themeChoice = theme;
  }

  const button = $("#themeMenuButton");
  if (button) {
    button.dataset.themeChoice = theme;
  }

  document.querySelectorAll("[data-theme-option]").forEach((option) => {
    const isSelected = option.dataset.themeOption === theme;
    option.dataset.selected = String(isSelected);
    option.setAttribute("aria-selected", String(isSelected));
  });
}

function toggleThemeMenu(forceOpen) {
  const menu = $("#themeMenu");
  const button = $("#themeMenuButton");
  if (!menu || !button) return;
  const isOpen = typeof forceOpen === "boolean" ? forceOpen : menu.classList.contains("hidden");
  menu.classList.toggle("hidden", !isOpen);
  button.setAttribute("aria-expanded", String(isOpen));
}

function setTheme(theme) {
  const normalized = normalizeThemeChoice(theme);
  const resolved = resolveThemeChoice(normalized);
  document.documentElement.dataset.themeChoice = normalized;
  document.documentElement.dataset.theme = resolved;
  localStorage.setItem(themeKey, normalized);
  syncThemeSelector(normalized);
}

function renderStatusStrip() {
  const primary = $("#statusPrimary");
  const version = $("#statusVersion");
  const secondary = $("#statusSecondary");
  if (!primary || !version || !secondary) return;

  primary.textContent = state.isRefreshing ? "Refreshing scanner" : "Engine idle";
  version.textContent = `Version ${state.meta.version_label || "0.2.0"}`;
  secondary.textContent = getNextScanLabel();
}

function initTheme() {
  const saved = localStorage.getItem(themeKey) || localStorage.getItem(legacyThemeKey) || "light";
  const normalized = normalizeThemeChoice(saved);
  if (localStorage.getItem(legacyThemeKey) && !localStorage.getItem(themeKey)) {
    localStorage.setItem(themeKey, normalized);
  }
  setTheme(normalized);
}

function toggleOptionsPanel(forceOpen) {
  const panel = $("#settingsDrawer");
  if (!panel) return;
  const isOpen = typeof forceOpen === "boolean" ? forceOpen : panel.classList.contains("hidden");
  panel.classList.toggle("hidden", !isOpen);
  panel.setAttribute("aria-hidden", String(!isOpen));
  $("#optionsToggle").setAttribute("aria-expanded", String(isOpen));
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
  const visibleIds = new Set(getVisibleChapters().map((chapter) => chapter.id));
  return [...state.selectedChapterIds].filter((chapterId) => visibleIds.has(chapterId)).length;
}

function clearSelectedChapters() {
  for (const chapter of state.chapters) {
    state.selectedChapterIds.delete(chapter.id);
  }
  toggleChapterBulkMenu(false);
  renderChapters();
}

async function queueSelectedChapters() {
  const selectedIds = getVisibleChapters()
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

  toggleChapterBulkMenu(false);
  setNotice(`Queued ${selectedIds.length} selected chapter${selectedIds.length === 1 ? "" : "s"}.`, "success");
  await refreshAll({ quiet: true });
}

function seriesMark(title) {
  const parts = String(title || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  if (!parts.length) return "TCB";
  return parts
    .slice(0, 3)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function getSeriesDensityClass(title) {
  const normalized = normalizeSeriesKey(title).replaceAll(" ", "");
  return normalized.length >= 18 ? " series-card-compact" : "";
}

function getFocusDensityClass(title) {
  const normalized = normalizeSeriesKey(title).replaceAll(" ", "");
  if (normalized.length >= 28) return " focus-condensed";
  if (normalized.length >= 18) return " focus-compact";
  return "";
}

function getFocusEmblem(series, art, useMockupArt) {
  const coverUrl = getSeriesCoverUrl(series, art);
  if (coverUrl) {
    return {
      className: "focus-emblem cover-emblem",
      markup: `<img src="${escapeHtml(coverUrl)}" alt="" loading="lazy" />`,
    };
  }

  return {
    className: `focus-emblem${useMockupArt ? " mockup-emblem" : ""}`,
    markup: `<div class="series-mark">${escapeHtml(seriesMark(series?.title))}</div>`,
  };
}

function getHostLabel(url) {
  try {
    return cleanHost(new URL(url).host);
  } catch {
    return url;
  }
}

function fileNameFromPath(value) {
  return String(value || "").split(/[\\/]/).filter(Boolean).pop() || value;
}

function formatInterval(minutes) {
  const totalMinutes = Number(minutes || 0);
  if (!totalMinutes) return "Manual cadence";
  if (totalMinutes < 60) {
    return `${totalMinutes}m`;
  }
  if (totalMinutes < 1440) {
    const hours = totalMinutes / 60;
    return `${Number.isInteger(hours) ? hours : hours.toFixed(1)}h`;
  }
  const days = totalMinutes / 1440;
  return `${Number.isInteger(days) ? days : days.toFixed(1)}d`;
}

function formatCadence(minutes) {
  const label = formatInterval(minutes);
  return label === "Manual cadence" ? label : `${label} cadence`;
}

function getNextScanLabel() {
  const enabled = state.series.filter((series) => series.enabled);
  if (!enabled.length) return "Next scan pending";

  let soonest = null;
  for (const series of enabled) {
    if (!series.last_checked_at) {
      return "Next scan due now";
    }
    const lastChecked = new Date(series.last_checked_at);
    if (Number.isNaN(lastChecked.getTime())) continue;
    const dueAt =
      lastChecked.getTime() + Number(series.check_interval_minutes || 0) * 60 * 1000;
    if (soonest === null || dueAt < soonest) {
      soonest = dueAt;
    }
  }

  if (soonest === null) return "Next scan pending";
  const diff = soonest - Date.now();
  if (diff <= 0) return "Next scan due now";
  return `Next scan in ${formatDuration(diff)}`;
}

function formatDuration(valueMs) {
  const totalSeconds = Math.max(0, Math.floor(valueMs / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return [hours, minutes, seconds]
    .map((value) => String(value).padStart(2, "0"))
    .join(":");
}

function formatRelativeTime(value) {
  if (!value) return "Never";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);

  const diffMs = date.getTime() - Date.now();
  const steps = [
    ["year", 1000 * 60 * 60 * 24 * 365],
    ["month", 1000 * 60 * 60 * 24 * 30],
    ["day", 1000 * 60 * 60 * 24],
    ["hour", 1000 * 60 * 60],
    ["minute", 1000 * 60],
    ["second", 1000],
  ];

  for (const [unit, size] of steps) {
    if (Math.abs(diffMs) >= size || unit === "second") {
      const valueForUnit = Math.round(diffMs / size);
      if (unit === "second" && Math.abs(valueForUnit) < 10) {
        return "just now";
      }
      return relativeFormatter.format(valueForUnit, unit);
    }
  }

  return "just now";
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function statusLabel(status) {
  switch (status) {
    case "skipped":
      return "Found";
    case "pending":
      return "Queued";
    case "downloading":
      return "Downloading";
    case "downloaded":
      return "Downloaded";
    case "failed":
      return "Failed";
    default:
      return status;
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setNotice(message, type = "info") {
  const bar = $("#noticeBar");
  bar.textContent = message;
  bar.className = `notice-bar ${type}`;
  bar.classList.remove("hidden");
  if (noticeTimer) {
    clearTimeout(noticeTimer);
  }
  noticeTimer = setTimeout(() => {
    clearNotice();
  }, type === "error" ? 7000 : 4000);
}

function clearNotice() {
  const bar = $("#noticeBar");
  bar.className = "notice-bar hidden";
  bar.textContent = "";
}

function fileNameFromDisposition(value) {
  const match = /filename=\"?([^\";]+)\"?/i.exec(String(value || ""));
  return match?.[1] || "";
}

async function exportLibrarySnapshot() {
  const response = await fetch("/api/library/export", {
    headers: {
      Accept: "application/json",
    },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Unable to export the library.");
  }

  const blob = await response.blob();
  const fileName =
    fileNameFromDisposition(response.headers.get("Content-Disposition")) ||
    `tcbscanner-library-${new Date().toISOString().replaceAll(":", "-")}.json`;
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

async function importLibrarySnapshot(file) {
  if (!file) return null;
  const raw = await file.text();
  let payload;
  try {
    payload = JSON.parse(raw);
  } catch {
    throw new Error("The selected file is not valid JSON.");
  }

  const result = await api("/api/library/import", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return result.counts || { series: 0, chapters: 0, events: 0, settings: 0 };
}

function handleError(error, prefix = "Something went wrong.") {
  console.error(error);
  const suffix = error instanceof Error ? error.message : String(error);
  setNotice(`${prefix} ${suffix}`.trim(), "error");
}

function readSeriesFormPayload(form) {
  const formData = new FormData(form);
  return {
    source_url: String(formData.get("source_url") || "").trim(),
    title: String(formData.get("title") || "").trim(),
    folder: String(formData.get("folder") || "").trim(),
    check_interval_hours: Number(formData.get("check_interval_hours") || 0.5),
    naming_format: String(formData.get("naming_format") || "").trim(),
    enabled: formData.get("enabled") === "on",
    backfill_existing: formData.get("backfill_existing") === "on",
  };
}

function normalizeSeriesPayload(payload) {
  return {
    ...payload,
    naming_format: payload.naming_format || null,
  };
}

function syncDraftFromPayload(payload, mode) {
  const draft = defaultSeriesDraft({
    title: payload.title,
    source_url: payload.source_url,
    folder: payload.folder,
    check_interval_hours: String(payload.check_interval_hours || "0.5"),
    naming_format: payload.naming_format || "",
    enabled: Boolean(payload.enabled),
    backfill_existing: Boolean(payload.backfill_existing),
  });
  if (mode === "edit") {
    state.editDraft = draft;
    state.editDraftDirty = true;
  } else {
    state.discoverDraft = draft;
  }
}

function applySearchSuggestion(match) {
  resetDiscoverDraft({
    title: match.title || "",
    source_url: match.url || "",
    folder: match.title || "",
    check_interval_hours: "0.5",
    naming_format: "",
    enabled: true,
    backfill_existing: false,
  });
  setSidebarMode("discover");
  setNotice(`Prepared ${match.title} from ${match.site_name}. You can still change the settings before tracking it.`, "success");
  renderSidebar();
}

async function selectSeries(seriesId, tab = "chapters") {
  if (!seriesId) return;
  if (state.selectedSeriesId !== seriesId) {
    state.selectedSeriesId = seriesId;
    state.chapterFilter = "all";
    await loadChaptersForSeries(seriesId);
  }
  setFocusTab(tab);
  renderAll();
}

async function runSidebarSearch(query) {
  const cleaned = String(query || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .join(" ");
  state.libraryFilter = cleaned;
  state.sidebarSearchQuery = cleaned;
  if (!cleaned) {
    state.sidebarSearchResults = { query: "", library_matches: [], source_matches: [] };
    state.sidebarSearching = false;
    setSearchMeta();
    renderAll();
    return;
  }

  state.sidebarSearching = true;
  setSidebarMode("discover");
  setSearchMeta(`Searching "${cleaned}" in your library and supported sites…`);
  renderAll();

  try {
    const result = await api(`/api/search?query=${encodeURIComponent(cleaned)}&limit=12`);
    state.sidebarSearchResults = result;
    const localCount = Number(result.library_matches?.length || 0);
    const remoteCount = Number(result.source_matches?.length || 0);
    if (localCount) {
      setSearchMeta(`${localCount} library match${localCount === 1 ? "" : "es"} found for "${cleaned}".`);
    } else if (remoteCount) {
      setSearchMeta(`No tracked matches for "${cleaned}". Showing ${remoteCount} supported-site suggestion${remoteCount === 1 ? "" : "s"}.`);
    } else {
      setSearchMeta(`No matches found for "${cleaned}".`);
    }
  } catch (error) {
    setSearchMeta(`Search failed for "${cleaned}".`);
    throw error;
  } finally {
    state.sidebarSearching = false;
    renderAll();
  }
}

async function loadSeriesHistory(force = false) {
  const selected = getSelectedSeries();
  if (!selected) return;
  if (!force && state.sidebarHistoryLoadedFor === selected.id && !state.sidebarHistoryLoading) {
    return;
  }
  state.sidebarHistoryLoading = true;
  renderSidebar();
  try {
    const response = await api(`/api/events?series_id=${selected.id}&limit=80`);
    state.sidebarHistory = response.events || [];
    state.sidebarHistoryLoadedFor = selected.id;
  } finally {
    state.sidebarHistoryLoading = false;
    renderSidebar();
  }
}

function listen(element, eventName, handler) {
  if (!element) return;
  element.addEventListener(eventName, (event) => {
    Promise.resolve(handler(event)).catch((error) => handleError(error));
  });
}

listen($("#optionsForm"), "submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  await api("/api/settings", {
    method: "POST",
    body: JSON.stringify({
      default_naming_format: String(form.get("default_naming_format") || "{ChapterFullTitle}"),
    }),
  });
  setNotice("Global naming defaults saved.", "success");
  await refreshAll({ quiet: true });
  toggleOptionsPanel(false);
});

listen($("#exportLibraryButton"), "click", async () => {
  await exportLibrarySnapshot();
  setNotice("Library snapshot exported.", "success");
});

$("#importLibraryButton").addEventListener("click", () => {
  $("#importLibraryFile").click();
});

listen($("#importLibraryFile"), "change", async (event) => {
  const input = event.currentTarget;
  const file = input.files?.[0];
  if (!file) return;

  const confirmed = window.confirm(
    "Importing a library snapshot will replace your entire current library, activity history, and saved settings. Continue?",
  );
  if (!confirmed) {
    input.value = "";
    return;
  }

  const counts = await importLibrarySnapshot(file);
  input.value = "";
  setNotice(
    `Imported ${Number(counts?.series || 0)} series and ${Number(counts?.chapters || 0)} chapters from the snapshot.`,
    "success",
  );
  await refreshAll({ quiet: true });
});

listen($("#seriesList"), "click", async (event) => {
  const card = event.target.closest("[data-series-id]");
  if (!card) return;
  const seriesId = Number(card.dataset.seriesId);
  if (!seriesId) return;
  await selectSeries(seriesId, state.focusTab);
  if (state.focusTab === "history") {
    await loadSeriesHistory(true);
  }
});

$("#seriesList").addEventListener("keydown", (event) => {
  const card = event.target.closest("[data-series-id]");
  if (!card || (event.key !== "Enter" && event.key !== " ")) return;
  event.preventDefault();
  card.click();
});

listen($("#selectedSeriesPanel"), "click", async (event) => {
  const tabButton = event.target.closest("button[data-tab]");
  if (tabButton) {
    const nextTab = tabButton.dataset.tab || "chapters";
    setFocusTab(nextTab);
    renderAll();
    if (nextTab === "history") {
      await loadSeriesHistory(true);
    }
    return;
  }

  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const seriesId = Number(button.closest("[data-series-id]")?.dataset.seriesId || state.selectedSeriesId);
  if (!seriesId) return;

  if (button.dataset.action === "check") {
    await api(`/api/series/${seriesId}/check`, { method: "POST" });
    setNotice("Manual check queued.", "success");
  }

  if (button.dataset.action === "download") {
    const result = await api(`/api/series/${seriesId}/download-missing`, { method: "POST" });
    setNotice(`Queued ${Number(result.queued || 0)} missing chapter${Number(result.queued || 0) === 1 ? "" : "s"}.`, "success");
  }

  if (button.dataset.action === "saveNaming") {
    const input = $("#selectedSeriesPanel input[data-field='naming-format']");
    await api(`/api/series/${seriesId}/naming-format`, {
      method: "POST",
      body: JSON.stringify({ naming_format: input?.value || null }),
    });
    setNotice("Series naming format updated.", "success");
  }

  if (button.dataset.action === "delete") {
    const confirmed = window.confirm("Delete this tracked series and its indexed chapter history?");
    if (!confirmed) return;
    await api(`/api/series/${seriesId}`, { method: "DELETE" });
    setNotice("Series removed from the scanner.", "success");
  }

  await refreshAll({ quiet: true });
});

listen($("#selectedSeriesPanel"), "change", async (event) => {
  const input = event.target.closest("input[data-action='monitor']");
  if (!input) return;
  const seriesId = Number(input.closest("[data-series-id]")?.dataset.seriesId || state.selectedSeriesId);
  if (!seriesId) return;
  await api(`/api/series/${seriesId}/enabled`, {
    method: "POST",
    body: JSON.stringify({ enabled: input.checked }),
  });
  setNotice(input.checked ? "Monitoring enabled." : "Monitoring paused.", "success");
  await refreshAll({ quiet: true });
});

listen($("#chapterFilters"), "click", async (event) => {
  const button = event.target.closest("button[data-filter]");
  if (!button) return;
  state.chapterFilter = button.dataset.filter || "all";
  renderChapters();
  renderFilters();
});

listen($("#chapterList"), "click", async (event) => {
  const button = event.target.closest("button[data-action='retry']");
  if (!button) return;
  await api(`/api/chapters/${Number(button.dataset.chapterId)}/retry`, { method: "POST" });
  setNotice("Chapter moved back into the queue.", "success");
  await refreshAll({ quiet: true });
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
  for (const chapter of getVisibleChapters().filter(isChapterSelectable)) {
    state.selectedChapterIds.add(chapter.id);
  }
  renderChapters();
});

$("#clearSelectedChapters").addEventListener("click", clearSelectedChapters);
$("#clearSelectedChaptersDock").addEventListener("click", clearSelectedChapters);
listen($("#queueSelectedChapters"), "click", queueSelectedChapters);
listen($("#queueSelectedChaptersDock"), "click", queueSelectedChapters);
$("#bulkActionsToggle").addEventListener("click", () => {
  toggleChapterBulkMenu();
});
document.addEventListener("click", (event) => {
  const tools = $("#chapterTools");
  if (!tools?.contains(event.target)) {
    toggleChapterBulkMenu(false);
  }
});

$("#refreshAll").addEventListener("click", () => {
  void refreshAll();
});

listen($("#librarySearchForm"), "submit", async (event) => {
  event.preventDefault();
  const query = event.currentTarget.elements.query?.value || "";
  await runSidebarSearch(query);
});

$("#librarySearchClear").addEventListener("click", () => {
  state.libraryFilter = "";
  state.sidebarSearchQuery = "";
  state.sidebarSearchResults = { query: "", library_matches: [], source_matches: [] };
  setSearchMeta();
  renderAll();
});

$("#openAddSeriesButton").addEventListener("click", () => {
  setSidebarMode("discover");
  renderSidebar();
  const searchInput = $("#sidebarPanel input[name='query']");
  if (searchInput) {
    searchInput.focus();
    searchInput.select();
  }
});

listen($("#sidebarPanel"), "submit", async (event) => {
  const form = event.target.closest("#seriesForm, #sidebarSearchForm");
  if (!form) return;
  event.preventDefault();

  if (form.id === "sidebarSearchForm") {
    await runSidebarSearch(form.elements.query?.value || "");
    return;
  }

  const mode = form.dataset.mode || "create";
  const payload = normalizeSeriesPayload(readSeriesFormPayload(form));
  syncDraftFromPayload(payload, mode);

  if (mode === "edit") {
    const selected = getSelectedSeries();
    if (!selected) return;
    const response = await api(`/api/series/${selected.id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    state.editDraftDirty = false;
    state.editDraft = seriesToDraft(response.series);
    setNotice(`Saved settings for ${payload.title}.`, "success");
    await refreshAll({ quiet: true });
    return;
  }

  const duplicate = getLibrarySearchMatches(payload.title, 1)[0];
  if (duplicate && normalizeSeriesKey(duplicate.title) === normalizeSeriesKey(payload.title)) {
    await selectSeries(duplicate.id, "chapters");
    setNotice(`${payload.title} is already in your library. Opened its entry instead.`, "success");
    return;
  }

  const response = await api("/api/series", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  resetDiscoverDraft();
  state.sidebarSearchQuery = "";
  state.sidebarSearchResults = { query: "", library_matches: [], source_matches: [] };
  state.libraryFilter = "";
  setSearchMeta();
  setNotice(`Tracking ${payload.title}.`, "success");
  const newSeriesId = Number(response.series?.id || 0);
  if (newSeriesId) {
    state.selectedSeriesId = newSeriesId;
    state.focusTab = "chapters";
    state.sidebarMode = "chapters";
  }
  renderAll();
  try {
    await refreshAll({ quiet: true });
  } catch (error) {
    console.warn(error);
  }
});

listen($("#sidebarPanel"), "input", async (event) => {
  const form = event.target.closest("#seriesForm");
  if (!form) return;
  const mode = form.dataset.mode || "create";
  syncDraftFromPayload(normalizeSeriesPayload(readSeriesFormPayload(form)), mode);
});

listen($("#sidebarPanel"), "change", async (event) => {
  const form = event.target.closest("#seriesForm");
  if (form) {
    const mode = form.dataset.mode || "create";
    syncDraftFromPayload(normalizeSeriesPayload(readSeriesFormPayload(form)), mode);
  }

  const monitor = event.target.closest("input[data-sidebar-monitor='true']");
  if (monitor) {
    const selected = getSelectedSeries();
    if (!selected) return;
    await api(`/api/series/${selected.id}/enabled`, {
      method: "POST",
      body: JSON.stringify({ enabled: monitor.checked }),
    });
    setNotice(monitor.checked ? "Monitoring enabled." : "Monitoring paused.", "success");
    await refreshAll({ quiet: true });
  }
});

listen($("#sidebarPanel"), "click", async (event) => {
  const selectExisting = event.target.closest("[data-sidebar-select-series]");
  if (selectExisting) {
    await selectSeries(Number(selectExisting.dataset.sidebarSelectSeries), "chapters");
    return;
  }

  const sourceSuggestion = event.target.closest("[data-sidebar-source-url]");
  if (sourceSuggestion) {
    applySearchSuggestion({
      title: sourceSuggestion.dataset.sidebarSourceTitle,
      url: sourceSuggestion.dataset.sidebarSourceUrl,
      site_name: sourceSuggestion.dataset.sidebarSourceSite,
    });
    return;
  }

  const actionButton = event.target.closest("[data-sidebar-action]");
  if (!actionButton) return;
  const selected = getSelectedSeries();
  if (!selected) return;

  if (actionButton.dataset.sidebarAction === "check") {
    await api(`/api/series/${selected.id}/check`, { method: "POST" });
    setNotice("Manual check queued.", "success");
    await refreshAll({ quiet: true });
    return;
  }

  if (actionButton.dataset.sidebarAction === "download") {
    const result = await api(`/api/series/${selected.id}/download-missing`, { method: "POST" });
    setNotice(`Queued ${Number(result.queued || 0)} missing chapter${Number(result.queued || 0) === 1 ? "" : "s"}.`, "success");
    await refreshAll({ quiet: true });
    return;
  }

  if (actionButton.dataset.sidebarAction === "delete") {
    const confirmed = window.confirm("Delete this tracked series and its indexed chapter history?");
    if (!confirmed) return;
    await api(`/api/series/${selected.id}`, { method: "DELETE" });
    setNotice("Series removed from the scanner.", "success");
    await refreshAll({ quiet: true });
  }
});

$("#optionsToggle").addEventListener("click", toggleOptionsPanel);
$("#settingsDrawerClose").addEventListener("click", () => {
  toggleOptionsPanel(false);
});

$("#themeMenuButton").addEventListener("click", (event) => {
  event.stopPropagation();
  toggleThemeMenu();
});

$("#themeMenu").addEventListener("click", (event) => {
  const option = event.target.closest("[data-theme-option]");
  if (!option) return;
  setTheme(option.dataset.themeOption);
  toggleThemeMenu(false);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    toggleThemeMenu(false);
    toggleOptionsPanel(false);
  }
});

document.addEventListener("click", (event) => {
  const themeSelector = $(".theme-selector");
  if (themeSelector && !themeSelector.contains(event.target)) {
    toggleThemeMenu(false);
  }
});

if (themeMediaQuery) {
  const handleThemeMediaChange = () => {
    const selectedTheme = localStorage.getItem(themeKey) || "light";
    if (normalizeThemeChoice(selectedTheme) === "system") {
      setTheme("system");
    }
  };

  if (typeof themeMediaQuery.addEventListener === "function") {
    themeMediaQuery.addEventListener("change", handleThemeMediaChange);
  } else if (typeof themeMediaQuery.addListener === "function") {
    themeMediaQuery.addListener(handleThemeMediaChange);
  }
}

initTheme();
renderAll();
void refreshAll();
setInterval(() => {
  void refreshAll({ quiet: true });
}, 8000);
