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

const ART_CACHE_KEY = "tcbscanner-series-art-v10";
const ARTWORK_API_PATH = "/api/artwork";
const ART_CACHE_TTL_MS = 1000 * 60 * 60 * 24;
const MIN_POSTER_CHOICES = 5;

const state = {
  series: [],
  events: [],
  queue: {
    downloading: [],
    pending: [],
    downloading_count: 0,
    pending_count: 0,
  },
  meta: {
    version: "0.2.0",
    version_label: "0.2.0",
    supported_source_count: 0,
    supported_sources: [],
    metadata_providers: [
      { id: "anilist", name: "AniList" },
      { id: "mangaupdates", name: "MangaUpdates" },
    ],
  },
  selectedSeriesId: null,
  chapters: [],
  selectedChapterIds: new Set(),
  settings: {
    default_naming_format: "{ChapterFullTitle}",
    default_metadata_provider: "anilist",
    variables: [],
    kavita_url: "",
    komga_url: "",
    library_roots: [],
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
  searchPreview: null,
  discoverDraft: defaultSeriesDraft(),
  editDraft: null,
  editDraftSeriesId: null,
  editDraftDirty: false,
  activityDrawerOpen: false,
  openErrorSeriesIds: new Set(),
  posterPickerSeriesId: null,
  posterChoices: [],
  posterChoicesLoading: false,
  catalogMatches: [],
  catalogSearching: false,
  catalogMessage: "",
};

const $ = (selector) => document.querySelector(selector);
const themeKey = "sakurarr-theme-v1";
const legacyThemeKey = "tcbscanner-theme-v4";
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
let preservedFocus = null;
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

function proxyImageUrl(url) {
  const cleaned = String(url || "").trim();
  if (!cleaned) return "";
  if (!/^https?:\/\//i.test(cleaned)) return cleaned;
  return `/api/artwork/image?url=${encodeURIComponent(cleaned)}`;
}

function getSeriesCoverUrl(series, art) {
  return (
    String(series?.poster_image_url || "").trim() ||
    selectArtworkUrl(art, "cover") ||
    getMockupCoverUrl(series) ||
    ""
  );
}

function getMockupCoverUrl(series) {
  return "";
}

function buildArtEntry(payload, existing = null) {
  const coverImageUrl = String(payload?.cover_image_url || existing?.cover_image_url || "").trim();
  const heroImageUrl = String(payload?.hero_image_url || coverImageUrl || existing?.hero_image_url || "").trim() || coverImageUrl;
  const resolvedChoices = Array.isArray(payload?.poster_choices) ? payload.poster_choices : [];
  const existingChoices = Array.isArray(existing?.poster_choices) ? existing.poster_choices : [];
  const hasFreshChoices = Boolean(coverImageUrl || heroImageUrl || resolvedChoices.length);
  return {
    cached_at: Date.now(),
    mal_id: null,
    title: existing?.title || "",
    mal_url: "",
    cover_image_url: coverImageUrl,
    hero_image_url: heroImageUrl,
    pictures_hydrated: true,
    lookup_complete: true,
    poster_choices: dedupePosterChoices(
      hasFreshChoices
        ? [
            coverImageUrl,
            heroImageUrl,
            ...resolvedChoices,
          ]
        : [
            coverImageUrl,
            heroImageUrl,
            ...existingChoices,
          ],
    ),
  };
}

function dedupePosterChoices(choices) {
  return [...new Set((choices || []).map((value) => String(value || "").trim()).filter(Boolean))];
}

function artworkChoiceCount(art) {
  return dedupePosterChoices([
    art?.cover_image_url,
    art?.hero_image_url,
    ...(art?.poster_choices || []),
  ]).length;
}

async function fetchSeriesArtwork(series, options = {}) {
  const { forceRefresh = false } = options;
  const cacheKey = normalizeSeriesKey(series.title);
  const cached = state.seriesArt[cacheKey];
  if (cached && !forceRefresh) {
    return cached;
  }

  const params = new URLSearchParams({
    title: String(series?.title || ""),
    source_url: String(series?.source_url || ""),
  });
  const resolved = await api(`${ARTWORK_API_PATH}?${params.toString()}`);
  if (!resolved?.cover_image_url && !(resolved?.poster_choices || []).length) {
    return cached || null;
  }

  const entry = buildArtEntry(resolved, cached);
  state.seriesArt[cacheKey] = entry;
  persistArtCache();
  return entry;
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

async function openPosterPicker(selected) {
  if (!selected) return;
  state.posterPickerSeriesId = selected.id;
  state.posterChoicesLoading = true;
  state.posterChoices = [];
  renderSidebar();
  try {
    let art = getArtworkForSeries(selected);
    if (!art || (!art.lookup_complete && artworkChoiceCount(art) < MIN_POSTER_CHOICES)) {
      art = await fetchSeriesArtwork(selected, {
        forceRefresh: !art || (!art.lookup_complete && artworkChoiceCount(art) < MIN_POSTER_CHOICES),
      });
    }
    const latest = art || getArtworkForSeries(selected);
    state.posterChoices = dedupePosterChoices([
      latest?.cover_image_url,
      latest?.hero_image_url,
      ...(latest?.poster_choices || []),
      getMockupCoverUrl(selected),
    ]);
  } catch (error) {
    console.warn(error);
  } finally {
    state.posterChoicesLoading = false;
    renderSidebar();
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
    backup_source_urls: "",
    metadata_provider: "",
    metadata_provider_override: "",
    metadata_id: "",
    metadata_title: "",
    metadata_url: "",
    metadata_chapter_count: "",
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
    backup_source_urls: normalizeBackupSourceUrls(series.backup_source_urls).join("\n"),
    metadata_provider: String(series.metadata_provider || ""),
    metadata_provider_override: String(series.metadata_provider_override || ""),
    metadata_id: String(series.metadata_id || ""),
    metadata_title: String(series.metadata_title || ""),
    metadata_url: String(series.metadata_url || ""),
    metadata_chapter_count: String(series.metadata_chapter_count || ""),
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
    if (force || state.editDraftSeriesId !== selected.id) {
      state.catalogMatches = [];
      state.catalogMessage = "";
    }
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
  state.catalogMatches = [];
  state.catalogMessage = "";
}

function readDraftValue(draft, key, fallback) {
  if (draft && Object.prototype.hasOwnProperty.call(draft, key)) {
    return draft[key];
  }
  return fallback;
}

function buildSeriesFromDraft(draft, fallback = {}) {
  const intervalHours = Number(
    readDraftValue(
      draft,
      "check_interval_hours",
      String(Math.max(0.5, Number(fallback.check_interval_minutes || 30) / 60)),
    ) || 0.5,
  );

  return {
    ...fallback,
    title: String(readDraftValue(draft, "title", fallback.title || "")),
    source_url: String(readDraftValue(draft, "source_url", fallback.source_url || fallback.url || "")),
    backup_source_urls: normalizeBackupSourceUrls(
      readDraftValue(draft, "backup_source_urls", fallback.backup_source_urls || []),
    ),
    metadata_provider: String(readDraftValue(draft, "metadata_provider", fallback.metadata_provider || "")),
    metadata_provider_override: String(
      readDraftValue(
        draft,
        "metadata_provider_override",
        fallback.metadata_provider_override || "",
      ),
    ),
    metadata_id: String(readDraftValue(draft, "metadata_id", fallback.metadata_id || "")),
    metadata_title: String(readDraftValue(draft, "metadata_title", fallback.metadata_title || "")),
    metadata_url: String(readDraftValue(draft, "metadata_url", fallback.metadata_url || "")),
    metadata_chapter_count: readDraftValue(
      draft,
      "metadata_chapter_count",
      fallback.metadata_chapter_count || null,
    ) || null,
    folder: String(readDraftValue(draft, "folder", fallback.folder || fallback.title || "")),
    check_interval_minutes: Math.max(30, Math.round(intervalHours * 60)),
    naming_format: String(readDraftValue(draft, "naming_format", fallback.naming_format || "")),
    poster_image_url: String(readDraftValue(draft, "poster_image_url", fallback.poster_image_url || "")),
    enabled: Boolean(readDraftValue(draft, "enabled", fallback.enabled)),
    backfill_existing: Boolean(readDraftValue(draft, "backfill_existing", fallback.backfill_existing)),
  };
}

function clearSearchPreview({ resetDraft = false } = {}) {
  state.searchPreview = null;
  if (resetDraft) {
    resetDiscoverDraft();
  }
}

function getPreviewSeries() {
  if (!state.searchPreview) return null;
  return buildSeriesFromDraft(state.discoverDraft, {
    title: state.searchPreview.title || "",
    source_url: state.searchPreview.url || "",
    backup_source_urls: [],
    metadata_provider: "",
    metadata_provider_override: "",
    metadata_id: "",
    metadata_title: "",
    metadata_url: "",
    metadata_chapter_count: null,
    folder: state.searchPreview.title || "",
    check_interval_minutes: 30,
    naming_format: "",
    enabled: true,
    backfill_existing: false,
    chapter_count: 0,
    downloaded_count: 0,
    pending_count: 0,
    failed_count: 0,
    last_checked_at: null,
    preview: true,
    site_name: state.searchPreview.site_name || "",
    site_domain: state.searchPreview.site_domain || "",
  });
}

function getFocusSeries() {
  const preview = getPreviewSeries();
  if (preview) return preview;

  const selected = getSelectedSeries();
  if (!selected) return null;

  if (state.sidebarMode === "settings" && state.editDraft) {
    return buildSeriesFromDraft(state.editDraft, selected);
  }

  return selected;
}

function selectSearchPreview(match) {
  if (!match) return;
  state.searchPreview = {
    title: String(match.title || ""),
    url: String(match.url || ""),
    site_name: String(match.site_name || ""),
    site_domain: String(match.site_domain || ""),
  };
  resetDiscoverDraft({
    title: match.title || "",
    source_url: match.url || "",
    folder: match.title || "",
    check_interval_hours: "0.5",
    naming_format: "",
    enabled: true,
    backfill_existing: false,
  });
  state.focusTab = "settings";
  setSidebarMode("discover");
  setNotice(`Prepared ${match.title} from ${match.site_name}. Adjust the settings on the right, then track it.`, "success");
  renderAll();
  void queueArtworkHydration([{ title: match.title, source_url: match.url }]);
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
  const [settingsData, seriesData, eventsData, metaData, queueData] = await Promise.all([
    api("/api/settings"),
    api("/api/series"),
    api("/api/events"),
    api("/api/meta"),
    api("/api/queue"),
  ]);

  state.settings = settingsData;
  state.series = [...seriesData.series].sort(compareSeries);
  state.events = eventsData.events;
  state.meta = metaData;
  state.queue = queueData;
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
  preservedFocus = captureFocusState();
  renderBrandPanel();
  renderSettings();
  renderOverview();
  renderSeries();
  renderSeriesFocus();
  renderSidebar();
  renderQueueDrawer();
  syncLibrarySearchInput();
  renderFilters();
  renderChapters();
  renderEvents();
  renderShellMeta();
  restoreFocusState(preservedFocus);
  preservedFocus = null;
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
  const kavitaInput = optionsForm?.elements.kavita_url;
  if (kavitaInput && document.activeElement !== kavitaInput) {
    kavitaInput.value = state.settings.kavita_url || "";
  }
  const komgaInput = optionsForm?.elements.komga_url;
  if (komgaInput && document.activeElement !== komgaInput) {
    komgaInput.value = state.settings.komga_url || "";
  }
  const metadataProviderInput = optionsForm?.elements.default_metadata_provider;
  if (metadataProviderInput && document.activeElement !== metadataProviderInput) {
    metadataProviderInput.value = state.settings.default_metadata_provider || "anilist";
  }

  const variables = $("#namingVariables");
  const variableMarkup = (state.settings.variables || [])
    .map(
      (variable) => `
        <button class="variable-item" type="button" data-insert-variable="${escapeHtml(formatVariableToken(variable.name))}" data-variable-context="settings">
          <code>{${escapeHtml(variable.name)}}</code>
          <span>${escapeHtml(variable.description)}</span>
        </button>
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
      summary.queued += Number(series.pending_count || 0) + Number(series.downloading_count || 0);
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
  const queryActive = Boolean(state.sidebarSearchQuery.trim());
  const displayedSeries = getDisplayedSeries();
  const sourceMatches = queryActive ? state.sidebarSearchResults.source_matches || [] : [];

  if (!state.series.length && !queryActive) {
    list.innerHTML = `
      <div class="empty-state">
        <strong>No tracked series yet</strong>
        <p>Add a title from the right rail to start indexing chapters and filling the queue.</p>
      </div>
    `;
    return;
  }

  if (!queryActive && !displayedSeries.length) {
    list.innerHTML = `
      <div class="empty-state">
        <strong>No tracked series match this search</strong>
        <p>Press Search to look across supported sites, or clear the filter to see your full library again.</p>
      </div>
    `;
    return;
  }

  if (!queryActive) {
    list.innerHTML = displayedSeries.map((series) => renderTrackedSeriesCard(series)).join("");
    return;
  }

  const sections = [];
  if (displayedSeries.length) {
    sections.push(
      renderSeriesListSection(
        "Tracked matches",
        displayedSeries.map((series) => renderTrackedSeriesCard(series, { searchMode: true })).join(""),
      ),
    );
  }

  if (state.sidebarSearching) {
    sections.push(`
      <div class="series-search-state">
        <strong>Searching supported sites…</strong>
        <span>Checking indexed families for fresh matches.</span>
      </div>
    `);
  }

  if (sourceMatches.length) {
    sections.push(
      renderSeriesListSection(
        "Supported site results",
        sourceMatches.map((match, index) => renderSearchSuggestionCard(match, index)).join(""),
      ),
    );
  }

  if (!sections.length) {
    list.innerHTML = `
      <div class="empty-state">
        <strong>No matches found for this search</strong>
        <p>Nothing in your tracked library or the searchable supported-site families matched that query.</p>
      </div>
    `;
    return;
  }

  list.innerHTML = sections.join("");
}

function seriesInlineStat(value, label) {
  return `
    <span class="series-stat-inline series-stat-${escapeHtml(label)}">
      <i aria-hidden="true"></i>
      <strong>${Number(value || 0)}</strong>
    </span>
  `;
}

function renderSeriesListSection(title, content) {
  return `
    <div class="series-list-group-label">${escapeHtml(title)}</div>
    ${content}
  `;
}

function renderSeriesErrorDisclosure(series) {
  const failedCount = Number(series.failed_count || 0);
  const lastError = String(series.last_error || "").trim();
  if (!lastError && !failedCount) return "";

  const isOpen = state.openErrorSeriesIds.has(Number(series.id));
  const issueCount = failedCount + (lastError ? 1 : 0);
  const panelId = `series-errors-${Number(series.id)}`;
  return `
    <div class="series-error-disclosure">
      <button
        class="series-error-toggle"
        type="button"
        data-series-error-toggle="${Number(series.id)}"
        aria-expanded="${isOpen ? "true" : "false"}"
        aria-controls="${panelId}"
      >
        <span>${isOpen ? "Hide Errors" : "Show Errors"}</span>
        <strong>${issueCount}</strong>
        ${icons.chevronDown}
      </button>
      <div id="${panelId}" class="series-error-panel${isOpen ? "" : " hidden"}">
        ${
          lastError
            ? `<p class="series-error"><strong>Latest scan</strong><span>${escapeHtml(lastError)}</span></p>`
            : ""
        }
        ${
          failedCount
            ? `<p class="series-error-note"><strong>${failedCount} failed chapter${failedCount === 1 ? "" : "s"}</strong><span>Open this series and select Failed to inspect or retry individual chapters.</span></p>`
            : ""
        }
      </div>
    </div>
  `;
}

function renderTrackedSeriesCard(series, { searchMode = false } = {}) {
  const isSelected = !state.searchPreview && series.id === state.selectedSeriesId;
  const art = getArtworkForSeries(series);
  const coverUrl = getSeriesCoverUrl(series, art);
  const densityClass = getSeriesDensityClass(series.title);
  return `
    <article
      class="series-card${isSelected ? " selected" : ""}${densityClass}"
      data-series-id="${series.id}"
      data-series-slug="${escapeHtml(normalizeSeriesKey(series.title).replaceAll(" ", "-"))}"
      ${searchMode ? 'data-search-context="query"' : ""}
      tabindex="0"
      role="button"
      aria-pressed="${isSelected ? "true" : "false"}"
    >
      <div class="series-cover${coverUrl ? "" : " fallback"}">
        ${
          coverUrl
            ? `<img src="${escapeHtml(proxyImageUrl(coverUrl))}" alt="" loading="lazy" />`
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
          ${seriesInlineStat(Number(series.pending_count || 0) + Number(series.downloading_count || 0), "queued")}
          ${seriesInlineStat(series.failed_count, "failed")}
        </div>

        <div class="series-meta">
          <span>${escapeHtml(formatCadence(series.check_interval_minutes))}</span>
          <span>${escapeHtml(formatRelativeTime(series.last_checked_at))}</span>
        </div>

        ${renderSeriesErrorDisclosure(series)}
      </div>
    </article>
  `;
}

function renderSearchSuggestionCard(match, index) {
  const art = getArtworkForSeries({ title: match.title, source_url: match.url });
  const coverUrl = getSeriesCoverUrl({ title: match.title, source_url: match.url }, art);
  const densityClass = getSeriesDensityClass(match.title);
  const isSelected = state.searchPreview?.url === match.url;
  const sourceLabel = [match.site_name, match.site_domain].filter(Boolean).join(" · ");
  return `
    <article
      class="series-card search-preview${isSelected ? " selected" : ""}${densityClass}"
      data-preview-index="${index}"
      tabindex="0"
      role="button"
      aria-pressed="${isSelected ? "true" : "false"}"
    >
      <div class="series-cover${coverUrl ? "" : " fallback"}">
        ${
          coverUrl
            ? `<img src="${escapeHtml(proxyImageUrl(coverUrl))}" alt="" loading="lazy" />`
            : `<div class="series-mark">${escapeHtml(seriesMark(match.title))}</div>`
        }
      </div>

      <div class="series-body">
        <div class="series-top">
          <div class="series-copy">
            <h3>${escapeHtml(match.title)}</h3>
            <p>${escapeHtml(sourceLabel || getHostLabel(match.url))}</p>
          </div>
          <span class="status-pill status-enabled">Preview</span>
        </div>

        <p class="series-suggestion-copy">Open this result in the center pane, then adjust its tracking settings on the right.</p>

        <div class="series-meta">
          <span>${escapeHtml(formatSourceDisplay(match.url))}</span>
          <span>Select to tune settings</span>
        </div>
      </div>
    </article>
  `;
}

function renderSeriesFocus() {
  const panel = $("#selectedSeriesPanel");
  const selected = getSelectedSeries();
  const focusSeries = getFocusSeries();
  const preview = getPreviewSeries();
  const isPreview = Boolean(preview);

  if (!focusSeries) {
    panel.innerHTML = `
      <div class="empty-state spacious">
        <strong>Choose a series to open the queue deck</strong>
        <p>The chapter workspace highlights naming rules, monitoring state, and the fastest actions for the selected title.</p>
      </div>
    `;
    return;
  }

  const statusClass = focusSeries.enabled ? "enabled" : "paused";
  const statusText = focusSeries.enabled ? "Monitored" : "Paused";
  const artSeries = isPreview
    ? { title: state.searchPreview?.title || focusSeries.title, source_url: focusSeries.source_url }
    : selected || focusSeries;
  const art = getArtworkForSeries(artSeries);
  const heroUrl = selectArtworkUrl(art, "hero") || selectArtworkUrl(art, "cover");
  const seriesSlug = normalizeSeriesKey(focusSeries.title).replaceAll(" ", "-");
  const useMockupArt = false;
  const focusArtUrl = useMockupArt ? "/static/mockup_assets/hero-art.png" : proxyImageUrl(heroUrl);
  const focusDensityClass = getFocusDensityClass(focusSeries.title);
  const focusEmblem = getFocusEmblem(focusSeries, art, useMockupArt);
  const artStyle = focusArtUrl
    ? ` style="--focus-art: url('${focusArtUrl.replaceAll("'", "%27")}')"`
    : "";
  const namingPreview = getNamingPreview(focusSeries);
  const sourceDisplay = formatSourceDisplay(focusSeries.source_url);
  const folderDisplay = formatFolderDisplay(focusSeries.folder || focusSeries.title);
  const focusIdentity = isPreview
    ? 'data-preview="true"'
    : `data-series-id="${selected.id}" data-series-slug="${escapeHtml(seriesSlug)}"`;
  const tabMarkup = isPreview
    ? `
        <div class="focus-tabs" aria-label="Series workspace sections">
          <span class="focus-tab active static">Settings</span>
        </div>
      `
    : `
        <div class="focus-tabs" aria-label="Series workspace sections">
          <button class="focus-tab${state.focusTab === "chapters" ? " active" : ""}" type="button" data-tab="chapters">Chapters</button>
          <button class="focus-tab${state.focusTab === "details" ? " active" : ""}" type="button" data-tab="details">Details</button>
          <button class="focus-tab${state.focusTab === "history" ? " active" : ""}" type="button" data-tab="history">History</button>
          <button class="focus-tab${state.focusTab === "files" ? " active" : ""}" type="button" data-tab="files">Files</button>
          <button class="focus-tab${state.focusTab === "settings" ? " active" : ""}" type="button" data-tab="settings">Settings</button>
        </div>
      `;

  panel.innerHTML = `
    <div class="focus-hero${useMockupArt ? " use-mockup-art" : ""}${focusDensityClass}${isPreview ? " preview-focus" : ""}" ${focusIdentity}${artStyle}>
      <div class="focus-watermark" aria-hidden="true"></div>
      <div class="focus-banner">
        <div class="focus-aside">
          <div class="${focusEmblem.className}" aria-hidden="true">${focusEmblem.markup}</div>
          <span class="status-pill status-${statusClass}">${statusText}</span>
        </div>
        <div class="focus-copy">
          <div class="focus-heading">
            <h2>${escapeHtml(focusSeries.title)}</h2>
          </div>
          <p class="focus-detail focus-detail-source">
            <strong>Source:</strong>
            <a class="focus-link" href="${escapeHtml(focusSeries.source_url)}" target="_blank" rel="noreferrer">
              ${escapeHtml(sourceDisplay)}
            </a>
          </p>
          <div class="focus-detail-grid">
            <span><strong>Library:</strong><em>${escapeHtml(focusSeries.title)}</em></span>
            <span><strong>Folder:</strong><em>${escapeHtml(folderDisplay)}</em></span>
            <span><strong>Interval:</strong><em>${escapeHtml(formatInterval(focusSeries.check_interval_minutes))}</em></span>
          </div>
          <p class="focus-detail focus-detail-naming"><strong>Naming:</strong><span>${escapeHtml(namingPreview)}</span></p>
        </div>
        <div class="focus-art" aria-hidden="true"></div>
        ${tabMarkup}
      </div>

      <div class="focus-actions sr-only" data-series-id="${selected?.id || ""}">
        <label class="monitor-toggle compact">
          <input type="checkbox" data-action="monitor" ${focusSeries.enabled ? "checked" : ""} />
          <span>${focusSeries.enabled ? "Monitor new chapters automatically" : "Series is currently paused"}</span>
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
  const preview = getPreviewSeries();
  if (state.sidebarMode === "settings") {
    ensureEditDraft();
  }

  if (preview) {
    panel.innerHTML = renderDiscoverSidebar();
    return;
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
  const preview = getPreviewSeries();
  const helperCopy = preview
    ? `
        <div class="sidebar-block">
          <div class="sidebar-series-summary">
            <strong>${escapeHtml(preview.title || "Search result preview")}</strong>
            <span>${escapeHtml(preview.site_name || getHostLabel(preview.source_url))}</span>
          </div>
          <div class="inline-alert">
            <strong>Search result selected</strong>
            <p>This preview came from the left rail. Adjust the tracking settings below, then add it to your library.</p>
          </div>
        </div>
      `
    : `
        <div class="sidebar-block">
          <div class="inline-alert">
            <strong>Use the left rail to search</strong>
            <p>Search results stay in the tracked-series column. Pick a result there to preview it in the middle pane, or paste a supported series URL below.</p>
          </div>
        </div>
      `;

  return `
    <div class="panel-heading">
      <div>
        <h2>Add new series</h2>
        <p>Search the left rail first, then fine-tune the selected result here before tracking it.</p>
      </div>
    </div>

    ${helperCopy}

    ${renderSeriesForm({
      mode: "create",
      title: "Track series",
      description: preview
        ? `This form is prefilled from ${preview.site_name || getHostLabel(preview.source_url)}.`
        : "Paste a supported series URL manually, or choose a result from the left rail to prefill this form.",
      draft: state.discoverDraft,
      submitLabel: "Track series",
      submitIcon: icons.download,
    })}
  `;
}

function renderChaptersSidebar(selected) {
  const downloadingNow = state.chapters.filter((chapter) => chapter.status === "downloading");
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
        ${miniStat(Number(selected.pending_count || 0) + Number(selected.downloading_count || 0), "Queued")}
        ${miniStat(selected.failed_count, "Failed")}
      </div>
      <div class="sidebar-subsection">
        <div class="sidebar-subsection-head">
          <strong>Currently downloading</strong>
          <span>${downloadingNow.length}</span>
        </div>
        ${
          downloadingNow.length
            ? downloadingNow
                .map(
                  (chapter) => `
                    <article class="sidebar-history-row tone-downloaded">
                      <strong>${escapeHtml(chapter.display_title)}</strong>
                      <span>${escapeHtml(chapter.page_count ? `${chapter.page_count} pages staged` : "Packaging pages now")}</span>
                    </article>
                  `,
                )
                .join("")
            : `<div class="inline-alert compact"><strong>No active download</strong><p>This series is not downloading a chapter right now.</p></div>`
        }
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
        <button class="small-action" type="button" data-sidebar-action="queue-failed">
          ${icons.retry}
          <span>Queue failed</span>
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

function catalogProviderName(provider) {
  const normalized = String(provider || "anilist").toLowerCase();
  const configured = (state.meta.metadata_providers || []).find((item) => item.id === normalized);
  if (configured?.name) return configured.name;
  return normalized === "mangaupdates" ? "MangaUpdates" : "AniList";
}

function catalogFallbackUrl(provider, id) {
  if (String(provider || "").toLowerCase() === "anilist") {
    return `https://anilist.co/manga/${id}`;
  }
  return "";
}

function renderDetailsSidebar(selected) {
  const backupSources = normalizeBackupSourceUrls(selected.backup_source_urls);
  const backupSourceSummary = backupSources.length
    ? backupSources
        .map(
          (sourceUrl) =>
            `<a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer">${escapeHtml(sourceUrl)}</a>`,
        )
        .join("<br />")
    : "None configured";
  return `
    <div class="panel-heading">
      <div>
        <h2>Series details</h2>
        <p>The selected title's current source, cadence, folder, and naming summary.</p>
      </div>
      <button class="small-action compact-action" type="button" data-sidebar-switch="settings">Edit</button>
    </div>
    <div class="sidebar-detail-list">
      ${sidebarDetailRow("Library title", selected.title)}
      ${sidebarDetailRow("Source URL", `<a href="${escapeHtml(selected.source_url)}" target="_blank" rel="noreferrer">${escapeHtml(selected.source_url)}</a>`)}
      ${sidebarDetailRow("Backup sources", backupSourceSummary)}
      ${sidebarDetailRow(
        "Metadata match",
        selected.metadata_id
          ? `<a href="${escapeHtml(selected.metadata_url || catalogFallbackUrl(selected.metadata_provider, selected.metadata_id))}" target="_blank" rel="noreferrer">${escapeHtml(selected.metadata_title || `${catalogProviderName(selected.metadata_provider)} #${selected.metadata_id}`)}</a>`
          : "Not matched",
      )}
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
                      ${renderReaderButtons(selected, chapter)}
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

function buildReaderUrl(template, series, chapter) {
  const raw = String(template || "").trim();
  if (!raw) return "";
  return raw
    .replaceAll("{series}", encodeURIComponent(series?.title || ""))
    .replaceAll("{title}", encodeURIComponent(series?.title || ""))
    .replaceAll("{chapter}", encodeURIComponent(chapter?.display_title || chapter?.chapter_key || ""))
    .replaceAll("{file}", encodeURIComponent(fileNameFromPath(chapter?.cbz_path || "")));
}

function renderReaderButtons(selected, chapter) {
  const links = [
    ["Kavita", state.settings.kavita_url],
    ["Komga", state.settings.komga_url],
  ]
    .map(([label, template]) => [label, buildReaderUrl(template, selected, chapter)])
    .filter(([, url]) => url);

  return links
    .map(
      ([label, url]) => `
        <a class="small-action tertiary-action" href="${escapeHtml(url)}" target="_blank" rel="noreferrer">
          <span>Open in ${escapeHtml(label)}</span>
        </a>
      `,
    )
    .join("");
}

function renderPosterPicker(selected) {
  const open = state.posterPickerSeriesId === selected.id;
  const selectedUrl = getSeriesCoverUrl(selected, getArtworkForSeries(selected));
  return `
    <section class="settings-section poster-picker-section">
      <div class="settings-section-heading">
        <div>
          <h3>Poster artwork</h3>
          <p>Pick a different cover for this series from the available artwork we found.</p>
        </div>
        <button class="small-action compact-action" type="button" data-sidebar-action="toggle-poster-picker">
          <span>${open ? "Hide posters" : "Edit poster"}</span>
        </button>
      </div>
      <div class="poster-picker-current">
        ${
          selectedUrl
            ? `<img src="${escapeHtml(proxyImageUrl(selectedUrl))}" alt="" loading="lazy" />`
            : `<div class="series-mark">${escapeHtml(seriesMark(selected.title))}</div>`
        }
      </div>
      ${
        open
          ? `
            <div class="poster-picker-grid">
              <button class="poster-choice${!selected.poster_image_url ? " active" : ""}" type="button" data-poster-url="">
                <span>Auto</span>
              </button>
              ${
                state.posterChoicesLoading
                  ? `<div class="inline-alert compact"><strong>Loading posters…</strong><p>Pulling available cover art for this series.</p></div>`
                  : state.posterChoices
                      .map(
                        (url) => `
                          <button class="poster-choice${selected.poster_image_url === url ? " active" : ""}" type="button" data-poster-url="${escapeHtml(url)}">
                            <img src="${escapeHtml(proxyImageUrl(url))}" alt="" loading="lazy" />
                          </button>
                        `,
                      )
                      .join("")
              }
            </div>
          `
          : ""
      }
    </section>
  `;
}

function renderSeriesSettingsSidebar(selected) {
  return `
    ${renderSeriesForm({
      mode: "edit",
      title: "Series settings",
      description: `Change the tracked source, naming, monitoring cadence, and archive behavior for ${selected.title}.`,
      draft: state.editDraft || seriesToDraft(selected),
      submitLabel: "Save series settings",
      submitIcon: icons.check,
    })}
    ${renderPosterPicker(selected)}
    ${renderSeriesDangerZone(selected)}
  `;
}

function renderSeriesDangerZone(selected) {
  return `
    <section class="settings-section danger-zone">
      <div class="settings-section-heading">
        <div>
          <h3>Reset chapter index</h3>
          <p>Clear every indexed chapter and error for ${escapeHtml(selected.title)}, then rescan the current primary and backup sources.</p>
        </div>
      </div>
      <label class="toggle-line">
        <input id="resetDeleteFiles" type="checkbox" />
        <span>Also permanently delete downloaded CBZ files recorded for this series</span>
      </label>
      <button class="small-action danger-action" type="button" data-sidebar-action="reset-series">
        ${icons.retry}
        <span>Clear index and rescan</span>
      </button>
    </section>
  `;
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
  const namingPlaceholder = state.settings.default_naming_format || "{ChapterFullTitle}";
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
        <span>Backup source URLs</span>
        <textarea name="backup_source_urls" rows="3" placeholder="One supported series URL per line">${escapeHtml(normalizeBackupSourceUrls(safeDraft.backup_source_urls).join("\n"))}</textarea>
        <small class="field-hint">Fill missing chapters and take over when the primary source fails.</small>
      </label>
      <label class="field-span">
        <span>Library title</span>
        <input name="title" type="text" required value="${escapeHtml(safeDraft.title)}" placeholder="e.g. My Hero Academia" />
      </label>
      ${renderCatalogMatcher(safeDraft)}
      <label class="field-span">
        <span>Save Folder</span>
        <span class="select-shell">
          <select name="folder">
            ${renderFolderOptions(safeDraft.folder, safeDraft.title)}
          </select>
          <span class="select-caret" aria-hidden="true"></span>
        </span>
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
          placeholder="${escapeHtml(namingPlaceholder)}"
        />
      </label>
      <div class="variable-list compact field-span">
        ${renderCompactVariableTokens("series")}
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

function renderCatalogMatcher(draft) {
  const matched = Boolean(draft.metadata_id);
  const providerOverride = draft.metadata_provider_override || "";
  const provider = providerOverride || state.settings.default_metadata_provider || "anilist";
  const providerName = catalogProviderName(provider);
  const catalogUrl = draft.metadata_url || (matched ? catalogFallbackUrl(provider, draft.metadata_id) : "");
  const providerOptions = (state.meta.metadata_providers || [])
    .map(
      (item) =>
        `<option value="${escapeHtml(item.id)}" ${item.id === providerOverride ? "selected" : ""}>${escapeHtml(item.name)}</option>`,
    )
    .join("");
  return `
    <section class="catalog-match field-span">
      <input name="metadata_provider" type="hidden" value="${escapeHtml(draft.metadata_provider || "")}" />
      <input name="metadata_id" type="hidden" value="${escapeHtml(draft.metadata_id || "")}" />
      <input name="metadata_title" type="hidden" value="${escapeHtml(draft.metadata_title || "")}" />
      <input name="metadata_url" type="hidden" value="${escapeHtml(draft.metadata_url || "")}" />
      <input name="metadata_chapter_count" type="hidden" value="${escapeHtml(draft.metadata_chapter_count || "")}" />
      <div class="settings-section-heading">
        <div>
          <h3>Metadata match</h3>
          <p>The metadata provider identifies the series; source URLs remain responsible for chapter availability.</p>
        </div>
        <button class="small-action compact-action" type="button" data-sidebar-action="search-catalog">
          <span>${state.catalogSearching ? "Searching…" : matched ? "Change match" : "Find match"}</span>
        </button>
      </div>
      <label>
        Metadata provider override
        <select name="metadata_provider_override">
          <option value="" ${providerOverride ? "" : "selected"}>Use global default (${escapeHtml(catalogProviderName(state.settings.default_metadata_provider))})</option>
          ${providerOptions}
        </select>
      </label>
      <div class="catalog-current${matched ? " matched" : ""}">
        ${
          matched
            ? `<strong>${escapeHtml(draft.metadata_title || `${providerName} #${draft.metadata_id}`)}</strong><a href="${escapeHtml(catalogUrl)}" target="_blank" rel="noreferrer">${escapeHtml(providerName)} #${escapeHtml(draft.metadata_id)}</a>`
            : `<strong>Not matched</strong><span>Use the library title to find the canonical ${escapeHtml(providerName)} entry.</span>`
        }
      </div>
      ${
        state.catalogMessage
          ? `<p class="field-hint">${escapeHtml(state.catalogMessage)}</p>`
          : ""
      }
      ${
        state.catalogMatches.length
          ? `<div class="catalog-results">${state.catalogMatches
              .map(
                (match) => `
                  <button
                    class="catalog-result"
                    type="button"
                    data-catalog-id="${escapeHtml(match.id)}"
                    data-catalog-title="${escapeHtml(match.title)}"
                    data-catalog-url="${escapeHtml(match.url)}"
                    data-catalog-provider="${escapeHtml(match.provider || "anilist")}"
                    data-catalog-chapters="${escapeHtml(match.chapter_count || "")}"
                  >
                    <strong>${escapeHtml(match.title)}</strong>
                    <span>${escapeHtml([match.format, match.status, match.country_of_origin].filter(Boolean).join(" · "))}</span>
                  </button>
                `,
              )
              .join("")}</div>`
          : ""
      }
    </section>
  `;
}

function renderCompactVariableTokens(context = "series") {
  return (state.settings.variables || [])
    .map(
      (variable) => `
        <button class="variable-item compact" type="button" data-insert-variable="${escapeHtml(formatVariableToken(variable.name))}" data-variable-context="${escapeHtml(context)}">
          <code>${escapeHtml(formatVariableToken(variable.name))}</code>
        </button>
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

function renderFolderOptions(selectedFolder, title) {
  const currentTitle = String(title || "").trim() || "Library Title";
  const roots = Array.isArray(state.settings.library_roots) ? state.settings.library_roots : [];
  const options = roots.length ? roots.map((root) => buildFolderFromRoot(root, currentTitle)) : [currentTitle];
  let selected = String(selectedFolder || "").trim();
  if (roots.length && selected && !/[\\/]/.test(selected)) {
    selected = buildFolderFromRoot(roots[0], selected);
  } else if (roots.length && !selected) {
    selected = buildFolderFromRoot(roots[0], currentTitle);
  }
  const uniqueOptions = [...new Set([...options, ...(selected ? [selected] : [])])];
  return uniqueOptions
    .map((option) => {
      const isSelected = option === (selected || options[0]);
      return `<option value="${escapeHtml(option)}" ${isSelected ? "selected" : ""}>${escapeHtml(option)}</option>`;
    })
    .join("");
}

function buildFolderFromRoot(root, title) {
  const cleanRoot = String(root || "").trim().replace(/[\\/]+$/, "");
  const cleanTitle = String(title || "").trim() || "Library Title";
  if (!cleanRoot) return cleanTitle;
  return `${cleanRoot}/${cleanTitle}`.replace(/\/{2,}/g, "/");
}

function folderRootForValue(value) {
  const folder = String(value || "").trim();
  const roots = Array.isArray(state.settings.library_roots) ? state.settings.library_roots : [];
  return roots.find((root) => folder === root || folder.startsWith(`${String(root).replace(/[\\/]+$/, "")}/`)) || "";
}

function suggestedFolderValue(currentValue, title) {
  const root = folderRootForValue(currentValue) || String((state.settings.library_roots || [])[0] || "");
  return root ? buildFolderFromRoot(root, title) : String(title || "").trim();
}

function updateFolderSelectOptions(form, title, { preserveRoot = true } = {}) {
  const select = form?.elements?.folder;
  if (!(select instanceof HTMLSelectElement)) return;
  const nextTitle = String(title || "").trim() || "Library Title";
  const currentValue = String(select.value || "");
  const nextValue = preserveRoot ? suggestedFolderValue(currentValue, nextTitle) : currentValue;
  select.innerHTML = renderFolderOptions(nextValue, nextTitle);
  select.value = nextValue || select.value;
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
  return `{${name}}`;
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
  if (Array.isArray(state.settings.library_roots) && state.settings.library_roots.length) {
    return buildFolderFromRoot(state.settings.library_roots[0], value);
  }
  return `D:\\Manga\\${value}`;
}

function renderFilters() {
  const filters = $("#chapterFilters");
  const selected = getSelectedSeries();
  const preview = getPreviewSeries();

  if (!selected || preview) {
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
  const preview = getPreviewSeries();
  const list = $("#chapterList");
  const head = $("#chapterListHead");
  const visibleChapters = getVisibleChapters();

  $("#chapterCount").textContent = preview
    ? "Track this preview to build its queue."
    : buildChapterCountLabel(selected, visibleChapters.length);

  if (preview) {
    head.classList.add("hidden");
    list.innerHTML = `
      <div class="empty-state">
        <strong>This title is still a search preview</strong>
        <p>Select Track series on the right to add it to your library. Once tracked, the chapter queue will populate here.</p>
      </div>
    `;
    renderSelectionTools();
    return;
  }

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

function renderQueueDrawer() {
  const drawer = $("#activityDrawer");
  const summary = $("#statusSecondary");
  const title = $("#statusPrimary");
  if (!drawer || !summary || !title) return;

  const downloading = Array.isArray(state.queue.downloading) ? state.queue.downloading : [];
  const pending = Array.isArray(state.queue.pending) ? state.queue.pending : [];
  const totalActivity = downloading.length + pending.length;

  title.textContent = "Activity";
  summary.textContent = totalActivity
    ? `${downloading.length} downloading · ${pending.length} pending`
    : getNextScanLabel();
  drawer.classList.toggle("hidden", !state.activityDrawerOpen);

  const downloadingMarkup = downloading.length
    ? downloading
        .map(
          (chapter) => `
            <article class="activity-drawer-row tone-downloading">
              <strong>${escapeHtml(chapter.series_title || "Unknown series")}</strong>
              <span>${escapeHtml(chapter.display_title || chapter.chapter_key || "Downloading chapter")}</span>
            </article>
          `,
        )
        .join("")
    : `<div class="empty-state"><strong>No downloads in progress</strong><p>Queued downloads will appear here while packaging is active.</p></div>`;

  const pendingMarkup = pending.length
    ? pending
        .slice(0, 30)
        .map(
          (chapter) => `
            <article class="activity-drawer-row tone-pending">
              <strong>${escapeHtml(chapter.series_title || "Unknown series")}</strong>
              <span>${escapeHtml(chapter.display_title || chapter.chapter_key || "Queued chapter")}</span>
            </article>
          `,
        )
        .join("")
    : `<div class="empty-state"><strong>No pending chapters</strong><p>The queue is clear right now.</p></div>`;

  drawer.innerHTML = `
    <div class="activity-drawer-inner">
      <div class="activity-drawer-heading">
        <div>
          <h2>Activity</h2>
          <p>Currently downloading and pending chapters across the scanner.</p>
        </div>
        <button class="settings-drawer-close" id="activityDrawerClose" type="button" aria-label="Close activity drawer">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6 18 18M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square"/></svg>
        </button>
      </div>
      <div class="activity-drawer-columns">
        <section class="activity-drawer-section">
          <div class="activity-drawer-section-head">
            <strong>Downloading</strong>
            <span>${downloading.length}</span>
          </div>
          <div class="activity-drawer-list">${downloadingMarkup}</div>
        </section>
        <section class="activity-drawer-section">
          <div class="activity-drawer-section-head">
            <strong>Pending</strong>
            <span>${pending.length}</span>
          </div>
          <div class="activity-drawer-list">${pendingMarkup}</div>
        </section>
      </div>
    </div>
  `;
}

function toggleActivityDrawer(forceOpen) {
  state.activityDrawerOpen =
    typeof forceOpen === "boolean" ? forceOpen : !state.activityDrawerOpen;
  renderQueueDrawer();
}

function renderSelectionTools() {
  const tools = $("#chapterTools");
  const bulkToggle = $("#bulkActionsToggle");
  const bulkMenu = $("#chapterBulkMenu");
  const dock = $("#selectionDock");
  const selected = getSelectedSeries();
  const preview = getPreviewSeries();
  const visibleChapters = getVisibleChapters();
  const selectableCount = visibleChapters.filter(isChapterSelectable).length;
  const selectedCount = countSelectedVisibleChapters();

  tools.classList.toggle("hidden", !selected || preview);
  bulkToggle.disabled = !selectableCount && !selectedCount;
  bulkToggle.setAttribute("aria-expanded", String(!preview && state.chapterBulkOpen));
  bulkMenu.classList.toggle("hidden", preview || !state.chapterBulkOpen || !selected);
  $("#selectVisibleChapters").disabled = !selectableCount;
  $("#clearSelectedChapters").disabled = !selectedCount;
  $("#queueSelectedChapters").disabled = !selectedCount;
  $("#selectedCount").textContent = `${selectedCount} selected`;

  dock.classList.toggle("hidden", preview || !selectedCount);
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
  const queued = state.series.reduce(
    (sum, series) => sum + Number(series.pending_count || 0) + Number(series.downloading_count || 0),
    0,
  );
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
  return ["light", "dark", "system"].includes(theme) ? theme : "dark";
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

  version.textContent = `Version ${state.meta.version_label || "0.2.0"}`;
  primary.textContent = "Activity";
  secondary.textContent = state.isRefreshing
    ? "Refreshing scanner"
    : `${Number(state.queue.downloading_count || 0)} downloading · ${Number(state.queue.pending_count || 0)} pending`;
}

function initTheme() {
  const saved = localStorage.getItem(themeKey) || localStorage.getItem(legacyThemeKey) || "dark";
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
  if (!parts.length) return "SK";
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
      markup: `<img src="${escapeHtml(proxyImageUrl(coverUrl))}" alt="" loading="lazy" />`,
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

function guessTitleFromSeriesUrl(url) {
  try {
    const parsed = new URL(url);
    const parts = parsed.pathname
      .split("/")
      .map((part) => decodeURIComponent(part).trim())
      .filter(Boolean);
    if (!parts.length) return "";
    let slug = parts[parts.length - 1];
    if (/^(chapter|ch)[-_ ]*\d/i.test(slug) && parts.length > 1) {
      slug = parts[parts.length - 2];
    }
    if (parts[0]?.toLowerCase() === "webtoon" && parts[1]) {
      slug = parts[1];
    }
    slug = slug
      .replace(/(?:^|[-_ ])(?:chapter|ch)[-_ ]*\d.*$/i, "")
      .replace(/\.(html|php)$/i, "");
    return slug
      .split(/[-_]+/)
      .filter(Boolean)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ")
      .trim();
  } catch {
    return "";
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
    const intervalMs = Math.max(1, Number(series.check_interval_minutes || 0)) * 60 * 1000;
    const dueAt = (Math.floor(lastChecked.getTime() / intervalMs) + 1) * intervalMs;
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

function captureFocusState() {
  const active = document.activeElement;
  if (!(active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement || active instanceof HTMLSelectElement)) {
    return null;
  }
  const selector = active.id
    ? `#${active.id}`
    : active.name
      ? `${active.form?.id ? `#${active.form.id} ` : ""}[name="${CSS.escape(active.name)}"]`
      : null;
  if (!selector) return null;
  return {
    selector,
    start: typeof active.selectionStart === "number" ? active.selectionStart : null,
    end: typeof active.selectionEnd === "number" ? active.selectionEnd : null,
  };
}

function restoreFocusState(snapshot) {
  if (!snapshot || document.activeElement?.tagName === "INPUT" || document.activeElement?.tagName === "TEXTAREA") {
    return;
  }
  const target = document.querySelector(snapshot.selector);
  if (!(target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement)) {
    return;
  }
  target.focus({ preventScroll: true });
  if (
    typeof snapshot.start === "number" &&
    typeof snapshot.end === "number" &&
    typeof target.setSelectionRange === "function"
  ) {
    target.setSelectionRange(snapshot.start, snapshot.end);
  }
}

function insertTextAtCursor(element, text) {
  if (!(element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement)) return;
  const start = typeof element.selectionStart === "number" ? element.selectionStart : element.value.length;
  const end = typeof element.selectionEnd === "number" ? element.selectionEnd : start;
  const before = element.value.slice(0, start);
  const after = element.value.slice(end);
  element.value = `${before}${text}${after}`;
  const nextCursor = start + text.length;
  element.focus();
  element.setSelectionRange(nextCursor, nextCursor);
  element.dispatchEvent(new Event("input", { bubbles: true }));
}

function resolveVariableTarget(button) {
  const context = button?.dataset.variableContext || "series";
  if (context === "settings") {
    return $("#optionsForm [name='default_naming_format']");
  }
  return $("#sidebarPanel #seriesForm [name='naming_format']");
}

function readSeriesFormPayload(form) {
  const formData = new FormData(form);
  return {
    source_url: String(formData.get("source_url") || "").trim(),
    backup_source_urls: normalizeBackupSourceUrls(formData.get("backup_source_urls")),
    metadata_provider: String(formData.get("metadata_provider") || "").trim() || null,
    metadata_provider_override:
      String(formData.get("metadata_provider_override") || "").trim() || null,
    metadata_id: String(formData.get("metadata_id") || "").trim() || null,
    metadata_title: String(formData.get("metadata_title") || "").trim() || null,
    metadata_url: String(formData.get("metadata_url") || "").trim() || null,
    metadata_chapter_count: Number(formData.get("metadata_chapter_count") || 0) || null,
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
    backup_source_urls: normalizeBackupSourceUrls(payload.backup_source_urls),
    naming_format: payload.naming_format || null,
  };
}

function normalizeBackupSourceUrls(value) {
  const items = Array.isArray(value) ? value : String(value || "").split(/[\n,;]+/);
  const seen = new Set();
  return items
    .map((item) => String(item || "").trim())
    .filter((item) => {
      if (!item) return false;
      const key = item.replace(/\/+$/, "").toLowerCase();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
}

function syncDraftFromPayload(payload, mode) {
  const draft = defaultSeriesDraft({
    title: payload.title,
    source_url: payload.source_url,
    backup_source_urls: normalizeBackupSourceUrls(payload.backup_source_urls).join("\n"),
    metadata_provider: payload.metadata_provider || "",
    metadata_provider_override: payload.metadata_provider_override || "",
    metadata_id: payload.metadata_id || "",
    metadata_title: payload.metadata_title || "",
    metadata_url: payload.metadata_url || "",
    metadata_chapter_count: payload.metadata_chapter_count || "",
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
  selectSearchPreview(match);
}

async function selectSeries(seriesId, tab = "chapters") {
  if (!seriesId) return;
  clearSearchPreview();
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
  clearSearchPreview({ resetDraft: true });
  if (!cleaned) {
    state.sidebarSearchResults = { query: "", library_matches: [], source_matches: [] };
    state.sidebarSearching = false;
    setSearchMeta();
    renderAll();
    return;
  }

  state.sidebarSearching = true;
  state.sidebarSearchResults = { query: cleaned, library_matches: [], source_matches: [] };
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
    if (remoteCount) {
      void queueArtworkHydration(
        result.source_matches.map((match) => ({
          title: match.title,
          source_url: match.url,
        })),
      );
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
      default_metadata_provider: String(form.get("default_metadata_provider") || "anilist"),
      kavita_url: String(form.get("kavita_url") || "").trim(),
      komga_url: String(form.get("komga_url") || "").trim(),
    }),
  });
  setNotice("Global defaults saved.", "success");
  await refreshAll({ quiet: true });
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
  const errorToggle = event.target.closest("[data-series-error-toggle]");
  if (errorToggle) {
    event.preventDefault();
    event.stopPropagation();
    const seriesId = Number(errorToggle.dataset.seriesErrorToggle);
    if (state.openErrorSeriesIds.has(seriesId)) {
      state.openErrorSeriesIds.delete(seriesId);
    } else {
      state.openErrorSeriesIds.add(seriesId);
    }
    renderSeries();
    return;
  }

  const previewCard = event.target.closest("[data-preview-index]");
  if (previewCard) {
    const match = state.sidebarSearchResults.source_matches?.[Number(previewCard.dataset.previewIndex)];
    if (match) {
      selectSearchPreview(match);
    }
    return;
  }

  const card = event.target.closest("[data-series-id]");
  if (!card) return;
  const seriesId = Number(card.dataset.seriesId);
  if (!seriesId) return;
  const nextTab = state.sidebarSearchQuery.trim() ? "settings" : state.focusTab;
  await selectSeries(seriesId, nextTab);
  if (nextTab === "history") {
    await loadSeriesHistory(true);
  }
});

$("#seriesList").addEventListener("keydown", (event) => {
  if (event.target.closest("[data-series-error-toggle]")) return;
  const card = event.target.closest("[data-series-id], [data-preview-index]");
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
  const hadPreview = Boolean(state.searchPreview);
  state.libraryFilter = "";
  state.sidebarSearchQuery = "";
  state.sidebarSearchResults = { query: "", library_matches: [], source_matches: [] };
  clearSearchPreview({ resetDraft: hadPreview });
  if (hadPreview && state.selectedSeriesId) {
    setSidebarMode(state.focusTab);
  }
  setSearchMeta();
  renderAll();
});

$("#openAddSeriesButton").addEventListener("click", () => {
  setSidebarMode("discover");
  clearSearchPreview({ resetDraft: true });
  renderAll();
  const searchInput = $("#librarySearchInput");
  if (searchInput) {
    searchInput.focus();
    searchInput.select();
  }
});

$("#optionsForm").addEventListener("click", (event) => {
  const variableButton = event.target.closest("[data-insert-variable]");
  if (!variableButton) return;
  const target = resolveVariableTarget(variableButton);
  if (target) {
    insertTextAtCursor(target, variableButton.dataset.insertVariable || "");
  }
});

$("#statusPrimary").addEventListener("click", () => {
  toggleActivityDrawer();
});

document.addEventListener("click", (event) => {
  if (event.target.closest("#activityDrawerClose")) {
    toggleActivityDrawer(false);
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
  clearSearchPreview({ resetDraft: true });
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
  const target = event.target;
  if (target?.name === "source_url") {
    const titleInput = form.elements.title;
    if (titleInput && !String(titleInput.value || "").trim()) {
      const guessed = guessTitleFromSeriesUrl(target.value);
      if (guessed) {
        titleInput.value = guessed;
      }
    }
  }
  if (target?.name === "source_url" || target?.name === "title") {
    updateFolderSelectOptions(form, form.elements.title?.value || "");
  }
  const mode = form.dataset.mode || "create";
  syncDraftFromPayload(normalizeSeriesPayload(readSeriesFormPayload(form)), mode);
  renderSeriesFocus();
});

listen($("#sidebarPanel"), "change", async (event) => {
  const form = event.target.closest("#seriesForm");
  if (form) {
    if (event.target?.name === "metadata_provider_override") {
      for (const fieldName of [
        "metadata_provider",
        "metadata_id",
        "metadata_title",
        "metadata_url",
        "metadata_chapter_count",
      ]) {
        if (form.elements[fieldName]) form.elements[fieldName].value = "";
      }
      state.catalogMatches = [];
      state.catalogMessage = "";
    }
    if (event.target?.name === "title" || event.target?.name === "folder") {
      updateFolderSelectOptions(form, form.elements.title?.value || "");
    }
    const mode = form.dataset.mode || "create";
    syncDraftFromPayload(normalizeSeriesPayload(readSeriesFormPayload(form)), mode);
    renderSeriesFocus();
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
  const variableButton = event.target.closest("[data-insert-variable]");
  if (variableButton) {
    const target = resolveVariableTarget(variableButton);
    if (target) {
      insertTextAtCursor(target, variableButton.dataset.insertVariable || "");
    }
    return;
  }

  const switchButton = event.target.closest("[data-sidebar-switch]");
  if (switchButton) {
    const nextMode = switchButton.dataset.sidebarSwitch || "settings";
    setSidebarMode(nextMode);
    renderAll();
    return;
  }

  const selectExisting = event.target.closest("[data-sidebar-select-series]");
  if (selectExisting) {
    await selectSeries(Number(selectExisting.dataset.sidebarSelectSeries), "chapters");
    return;
  }

  const sourceSuggestion = event.target.closest("[data-sidebar-source-url]");
  if (sourceSuggestion) {
    selectSearchPreview({
      title: sourceSuggestion.dataset.sidebarSourceTitle,
      url: sourceSuggestion.dataset.sidebarSourceUrl,
      site_name: sourceSuggestion.dataset.sidebarSourceSite,
    });
    return;
  }

  const catalogResult = event.target.closest("[data-catalog-id]");
  if (catalogResult) {
    const form = $("#sidebarPanel #seriesForm");
    if (!form) return;
    const mode = form.dataset.mode || "create";
    syncDraftFromPayload(normalizeSeriesPayload(readSeriesFormPayload(form)), mode);
    const draft = mode === "edit" ? state.editDraft : state.discoverDraft;
    Object.assign(draft, {
      metadata_provider: catalogResult.dataset.catalogProvider || "anilist",
      metadata_id: catalogResult.dataset.catalogId || "",
      metadata_title: catalogResult.dataset.catalogTitle || "",
      metadata_url: catalogResult.dataset.catalogUrl || "",
      metadata_chapter_count: catalogResult.dataset.catalogChapters || "",
    });
    if (mode === "edit") state.editDraftDirty = true;
    state.catalogMatches = [];
    state.catalogMessage = `Matched to ${draft.metadata_title}. Save series settings to persist it.`;
    renderSidebar();
    return;
  }

  const actionButton = event.target.closest("[data-sidebar-action]");
  const selected = getSelectedSeries();
  if (actionButton?.dataset.sidebarAction === "search-catalog") {
    const form = $("#sidebarPanel #seriesForm");
    if (!form || state.catalogSearching) return;
    const mode = form.dataset.mode || "create";
    const payload = normalizeSeriesPayload(readSeriesFormPayload(form));
    const provider =
      payload.metadata_provider_override ||
      state.settings.default_metadata_provider ||
      "anilist";
    const providerName = catalogProviderName(provider);
    syncDraftFromPayload(payload, mode);
    state.catalogSearching = true;
    state.catalogMatches = [];
    state.catalogMessage = `Searching ${providerName}…`;
    renderSidebar();
    try {
      const result = await api(
        `/api/metadata/catalog?provider=${encodeURIComponent(provider)}&query=${encodeURIComponent(payload.title)}&limit=8`,
      );
      state.catalogMatches = result.matches || [];
      state.catalogMessage = state.catalogMatches.length
        ? "Choose the canonical series entry."
        : `No ${providerName} matches were found for this title.`;
    } catch (error) {
      state.catalogMessage = error.message || `${providerName} lookup failed.`;
    } finally {
      state.catalogSearching = false;
      renderSidebar();
    }
    return;
  }
  if (actionButton?.dataset.sidebarAction === "toggle-poster-picker") {
    if (!selected) return;
    if (state.posterPickerSeriesId === selected.id) {
      state.posterPickerSeriesId = null;
      state.posterChoices = [];
      state.posterChoicesLoading = false;
      renderSidebar();
    } else {
      await openPosterPicker(selected);
    }
    return;
  }

  const posterButton = event.target.closest("[data-poster-url]");
  if (posterButton) {
    if (!selected) return;
    await api(`/api/series/${selected.id}/poster`, {
      method: "POST",
      body: JSON.stringify({ poster_image_url: posterButton.dataset.posterUrl || null }),
    });
    setNotice("Series poster updated.", "success");
    await refreshAll({ quiet: true });
    await openPosterPicker(getSelectedSeries());
    return;
  }

  if (!actionButton || !selected) return;

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

  if (actionButton.dataset.sidebarAction === "queue-failed") {
    const result = await api(`/api/series/${selected.id}/queue-failed`, { method: "POST" });
    setNotice(`Queued ${Number(result.queued || 0)} failed chapter${Number(result.queued || 0) === 1 ? "" : "s"}.`, "success");
    await refreshAll({ quiet: true });
    return;
  }

  if (actionButton.dataset.sidebarAction === "reset-series") {
    const deleteFiles = Boolean($("#resetDeleteFiles")?.checked);
    const warning = deleteFiles
      ? `Clear every indexed chapter for ${selected.title} and permanently delete its recorded CBZ files?`
      : `Clear every indexed chapter and error for ${selected.title}, keep its CBZ files, and rescan now?`;
    if (!window.confirm(warning)) return;
    const result = await api(`/api/series/${selected.id}/reset`, {
      method: "POST",
      body: JSON.stringify({ delete_files: deleteFiles, rescan: true }),
    });
    setNotice(
      `Cleared ${Number(result.removed_records || 0)} chapter records${deleteFiles ? ` and deleted ${Number(result.deleted_files || 0)} files` : ""}. Rescan queued.`,
      "success",
    );
    state.selectedChapterIds.clear();
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
    const selectedTheme = localStorage.getItem(themeKey) || "dark";
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
