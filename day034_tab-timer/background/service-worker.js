const ALARM_NAME = 'tick';
const TICK_INTERVAL_MINUTES = 1 / 6; // 10 seconds for accuracy

// ─── helpers ────────────────────────────────────────────────────────────────

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

function extractDomain(url) {
  try {
    if (!url || url.startsWith('chrome://') || url.startsWith('chrome-extension://')) return null;
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return null;
  }
}

async function loadState() {
  return new Promise(resolve => {
    chrome.storage.local.get(['today', 'domains', 'active'], data => {
      const today = todayKey();
      // Reset if date changed
      if (data.today !== today) {
        resolve({ today, domains: {}, active: null });
      } else {
        resolve({
          today,
          domains: data.domains || {},
          active: data.active || null,
        });
      }
    });
  });
}

async function saveState(state) {
  return new Promise(resolve => chrome.storage.local.set(state, resolve));
}

// Flush elapsed time for the currently active session into domains map
function flushActive(state) {
  const { active, domains } = state;
  if (!active || !active.domain || !active.startTime) return state;

  const elapsed = Math.round((Date.now() - active.startTime) / 1000);
  if (elapsed <= 0) return state;

  return {
    ...state,
    domains: {
      ...domains,
      [active.domain]: (domains[active.domain] || 0) + elapsed,
    },
    active: { ...active, startTime: Date.now() }, // restart the clock
  };
}

// ─── core logic ─────────────────────────────────────────────────────────────

async function switchToTab(tabId) {
  let state = await loadState();
  state = flushActive(state);

  if (tabId == null) {
    state = { ...state, active: null };
    await saveState(state);
    return;
  }

  // Look up the tab URL
  try {
    const tab = await chrome.tabs.get(tabId);
    const domain = extractDomain(tab.url);
    state = {
      ...state,
      active: domain ? { domain, startTime: Date.now() } : null,
    };
  } catch {
    state = { ...state, active: null };
  }

  await saveState(state);
}

async function onTick() {
  let state = await loadState();
  state = flushActive(state);
  // After flushActive the startTime is already reset, so just save
  await saveState(state);
}

async function onFocusChanged(windowId) {
  let state = await loadState();

  if (windowId === chrome.windows.WINDOW_ID_NONE) {
    // Browser lost focus — flush & pause
    state = flushActive(state);
    state = { ...state, active: state.active ? { ...state.active, startTime: null } : null };
    await saveState(state);
    return;
  }

  // Browser regained focus — find the active tab in the focused window
  try {
    const [tab] = await chrome.tabs.query({ active: true, windowId });
    if (tab) {
      state = flushActive(state);
      const domain = extractDomain(tab.url);
      state = {
        ...state,
        active: domain ? { domain, startTime: Date.now() } : null,
      };
      await saveState(state);
    }
  } catch {
    /* ignore */
  }
}

// ─── event listeners ────────────────────────────────────────────────────────

chrome.tabs.onActivated.addListener(({ tabId }) => {
  switchToTab(tabId);
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete') return;
  chrome.tabs.query({ active: true, currentWindow: true }, ([activeTab]) => {
    if (activeTab && activeTab.id === tabId) {
      switchToTab(tabId);
    }
  });
});

chrome.windows.onFocusChanged.addListener(onFocusChanged);

chrome.alarms.onAlarm.addListener(alarm => {
  if (alarm.name === ALARM_NAME) onTick();
});

// ─── startup ────────────────────────────────────────────────────────────────

chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create(ALARM_NAME, { periodInMinutes: TICK_INTERVAL_MINUTES });
  // Start tracking the current active tab
  chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
    if (tab) switchToTab(tab.id);
  });
});

chrome.runtime.onStartup.addListener(() => {
  chrome.alarms.create(ALARM_NAME, { periodInMinutes: TICK_INTERVAL_MINUTES });
  chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
    if (tab) switchToTab(tab.id);
  });
});
