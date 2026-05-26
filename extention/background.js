// background.js — service worker

const API_BASE = 'http://localhost:8000';

// Store auth token and user info
let authState = {
  token: null,
  user: null,
  sessionId: null,
  lastReportId: null
};

// Load persisted auth on startup
// background.js — GET_AUTH_STATE case fix
// Also normalize user.id when loading from storage on startup

chrome.storage.local.get(['authToken', 'authUser', 'sessionId'], (result) => {
  if (result.authToken) authState.token = result.authToken;
  if (result.authUser) {
    authState.user = result.authUser;
    // Normalize id field on load too
    if (authState.user.user_id && !authState.user.id) {
      authState.user.id = authState.user.user_id;
    }
  }
  if (result.sessionId) authState.sessionId = result.sessionId;
});

// Listen for messages from popup/chat
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender)
    .then(sendResponse)
    .catch((err) => sendResponse({ error: err.message }));
  return true; // keep channel open for async
});

async function handleMessage(message, sender) {
  switch (message.type) {

    case 'SEND_OTP': {
      const res = await fetch(`${API_BASE}/api/auth/send-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', accept: 'application/json' },
        body: JSON.stringify({ mobile_number: message.mobile })
      });
      return res.json();
    }

// background.js — VERIFY_OTP case fix

case 'VERIFY_OTP': {
  const res = await fetch(`${API_BASE}/api/auth/verify-otp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', accept: 'application/json' },
    body: JSON.stringify({ mobile: message.mobile, otp: message.otp })
  });
  const data = await res.json();
  if (data.success) {
    authState.token = data.token;
    authState.user = data.user;

    // Normalize user id — handle both `id` and `user_id` from backend
    if (authState.user && authState.user.user_id && !authState.user.id) {
      authState.user.id = authState.user.user_id;
    }


    // fetchSessions returns raw json — extract the session id correctly
    const sessions = await fetchSessions(authState.user.id, data.token);
    console.log('Fetched sessions on login:', sessions);
    // sessions may be an array of objects or array of strings
    const firstSession = sessions?.at(-1);
    console.log('last session:', firstSession);

    authState.sessionId = firstSession
      ? (typeof firstSession === 'object' ? (firstSession.id || firstSession.session_id || firstSession._id) : firstSession)
      : null;

    await chrome.storage.local.set({
      authToken: data.token,
      authUser: authState.user,
      sessionId: authState.sessionId
    });
  }
  return { ...data, sessionId: authState.sessionId };
}


    case 'GET_AUTH_STATE': {
      return {
        isAuthenticated: !!authState.token,
        user: authState.user,
        sessionId: authState.sessionId
      };
    }

    case 'LOGOUT': {
      authState = { token: null, user: null, sessionId: null };
      await chrome.storage.local.remove(['authToken', 'authUser', 'sessionId']);
      return { success: true };
    }

    case 'GET_SESSIONS': {
      const sessions = await fetchSessions(message.userId, authState.token);
      return { sessions };
    }

    case 'GET_MESSAGES': {
      const res = await fetch(
        `${API_BASE}/api/sessions/${message.userId}/${message.sessionId}/messages`,
        { headers: { accept: 'application/json' } }
      );
      return res.json();
    }

    case 'SEND_MESSAGE': {
      const res = await fetch(`${API_BASE}/api/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', accept: 'application/json' },
        body: JSON.stringify({
          session_id: String(message.sessionId),
          user_id: String(message.userId),
          message: message.text,
          project_name: message.projectName
        })
      });
      const data = await res.json();

      // Handle flags — check both top-level and nested data.flags
      const flags = data.flags || data.data?.flags || {};
      if(data.report_id){
      authState.lastReportId = data.report_id

      }
      const reportId = authState.lastReportId || null;

      let imageUrl = null;
      let pdfUrl = null;

      if (flags.ask_chart && reportId) {
        imageUrl = `${API_BASE}/api/reports/images/chart/generate/${reportId}`;
      }
      if (flags.ask_pdf && reportId) {
        pdfUrl = `${API_BASE}/api/reports/${reportId}/pdf`;
      }

      // Also handle top-level generate_image / generate_pdf flags (scenario 5/6)
      if ((data.generate_image || data.flags?.generate_image) && reportId) {
        imageUrl = `${API_BASE}/api/reports/images/chart/generate/${reportId}`;
      }
      if ((data.generate_pdf || data.flags?.generate_pdf) && reportId) {
        pdfUrl = `${API_BASE}/api/reports/${reportId}/pdf`;
      }

      return { ...data, resolvedImageUrl: imageUrl, resolvedPdfUrl: pdfUrl };
    }

    case 'DOWNLOAD_PDF': {
      // Trigger download via chrome.downloads if available, else return URL
      const url = `${API_BASE}/api/reports/${message.reportId}/pdf`;
      if (chrome.downloads) {
        chrome.downloads.download({ url, filename: `report_${message.reportId}.pdf` });
        return { success: true };
      }
      return { url };
    }

    case 'GET_PROJECT_FROM_TAB': {
      // Ask content script for project name
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tabs[0]) return { projectName: null };
      try {
        const results = await chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          func: extractProjectName
        });
        return { projectName: results[0]?.result || null };
      } catch {
        return { projectName: null };
      }
    }

    default:
      return { error: 'Unknown message type' };
  }
}

async function fetchSessions(userId, token) {
  try {
    const res = await fetch(`${API_BASE}/api/sessions/${userId}`, {
      headers: { accept: 'application/json' }
    });
    if (!res.ok) return [];
    const data = await res.json();
    // data might be an array directly, or { sessions: [...] }
    return Array.isArray(data) ? data : (data.sessions || []);
  } catch {
    return [];
  }
}

// Injected into page to extract Jira project name
function extractProjectName() {
  // Try URL pattern: /jira/software/projects/KEY/...
  const urlMatch = window.location.pathname.match(/\/projects\/([A-Z][A-Z0-9_-]*)/i);
  if (urlMatch) return urlMatch[1].toUpperCase();

  // Try breadcrumb
  const breadcrumb = document.querySelector('[data-testid="project-breadcrumb"] span, .project-title, [aria-label*="project"]');
  if (breadcrumb) return breadcrumb.textContent.trim();

  // Try page title
  const titleMatch = document.title.match(/^([A-Z][A-Z0-9_-]+)\s*[-|]/);
  if (titleMatch) return titleMatch[1];

  return null;
}
