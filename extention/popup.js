// popup.js

let currentMobile = '';

const $ = (id) => document.getElementById(id);

function showStatus(elId, msg, type = 'info') {
  const el = $(elId);
  el.textContent = msg;
  el.className = `status-msg ${type}`;
  el.classList.remove('hidden');
}

function hideStatus(elId) {
  $(elId).classList.add('hidden');
}

function setLoading(btnId, loading, label) {
  const btn = $(btnId);
  btn.disabled = loading;
  btn.innerHTML = loading
    ? `<span class="spinner"></span> ${label}`
    : label;
}

// Check auth state on open
async function init() {
  // Check if we're on localhost:8080 (Jira page)
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const currentTab = tabs[0];
  
  if (!currentTab || !currentTab.url.includes('localhost:8080')) {
    $('step-mobile').innerHTML = `
      <div style="padding: 20px; text-align: center; color: #9d9ab8;">
        <div style="font-size: 32px; margin-bottom: 12px;">🔒</div>
        <div style="font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #f1f0ff;">Not on Jira Page</div>
        <div style="font-size: 12px; line-height: 1.5;">
          This extension only works on <strong>localhost:8080</strong>
        </div>
      </div>
    `;
    return;
  }

  const state = await chrome.runtime.sendMessage({ type: 'GET_AUTH_STATE' });

  if (state.isAuthenticated && state.user) {
    showLoggedIn(state.user, state.sessionId);
  } else {
    $('step-mobile').classList.remove('hidden');
    $('step-otp').classList.add('hidden');
    $('step-loggedin').classList.add('hidden');
  }
}

function showLoggedIn(user, sessionId) {
  $('step-mobile').classList.add('hidden');
  $('step-otp').classList.add('hidden');
  $('step-loggedin').classList.remove('hidden');

  const name = user.name || user.mobile;
  $('user-avatar').textContent = name.charAt(0).toUpperCase();
  $('user-name-display').textContent = user.name || 'Manager';
  $('user-mobile-display').textContent = user.mobile;

  // Detect project from active tab
  detectProject();
}

async function detectProject() {
  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tabs[0]) return;

    const results = await chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      func: () => {
        const urlMatch = window.location.pathname.match(/\/projects\/([A-Z][A-Z0-9_-]*)/i);
        if (urlMatch) return urlMatch[1].toUpperCase();
        const titleMatch = document.title.match(/^([A-Z][A-Z0-9_-]+)\s*[-|]/);
        if (titleMatch) return titleMatch[1];
        return null;
      }
    });

    const projectName = results?.[0]?.result;
    $('project-name-display').textContent = projectName
      ? `Project: ${projectName}`
      : 'No project detected';

    // Store for chat
    if (projectName) {
      chrome.storage.local.set({ currentProject: projectName });
    }
  } catch {
    $('project-name-display').textContent = 'Not on Jira page';
  }
}

// Send OTP
$('send-otp-btn').addEventListener('click', async () => {
  const mobile = $('mobile-input').value.trim();
  if (!mobile) {
    showStatus('mobile-status', 'Please enter your mobile number.', 'error');
    return;
  }

  currentMobile = mobile;
  setLoading('send-otp-btn', true, 'Sending...');
  hideStatus('mobile-status');

  try {
    const res = await chrome.runtime.sendMessage({ type: 'SEND_OTP', mobile });

    if (res.message === 'OTP sent') {
      $('step-mobile').classList.add('hidden');
      $('step-otp').classList.remove('hidden');

      // Dev hint: show OTP in dev mode
      if (res.otp) {
        $('otp-hint').textContent = `Dev hint: ${res.otp}`;
      }
    } else {
      showStatus('mobile-status', res.message || 'Failed to send OTP.', 'error');
    }
  } catch (err) {
    showStatus('mobile-status', 'Network error. Is the backend running?', 'error');
  } finally {
    setLoading('send-otp-btn', false, 'Send OTP');
  }
});

// Verify OTP
$('verify-otp-btn').addEventListener('click', async () => {
  const otp = $('otp-input').value.trim();
  if (!otp) {
    showStatus('otp-status', 'Please enter the OTP.', 'error');
    return;
  }

  setLoading('verify-otp-btn', true, 'Verifying...');
  hideStatus('otp-status');

  try {
    const res = await chrome.runtime.sendMessage({
      type: 'VERIFY_OTP',
      mobile: currentMobile,
      otp
    });

    if (res.success) {
      showStatus('otp-status', 'Authenticated!', 'success');
      setTimeout(() => showLoggedIn(res.user, res.sessionId), 600);
    } else {
      showStatus('otp-status', res.message || 'Invalid OTP.', 'error');
    }
  } catch (err) {
    showStatus('otp-status', 'Network error.', 'error');
  } finally {
    setLoading('verify-otp-btn', false, 'Verify');
  }
});

// Resend OTP
$('resend-btn').addEventListener('click', async () => {
  if (!currentMobile) {
    $('step-otp').classList.add('hidden');
    $('step-mobile').classList.remove('hidden');
    return;
  }
  setLoading('resend-btn', true, 'Resending...');
  try {
    const res = await chrome.runtime.sendMessage({ type: 'SEND_OTP', mobile: currentMobile });
    if (res.otp) $('otp-hint').textContent = `Dev hint: ${res.otp}`;
    showStatus('otp-status', 'OTP resent.', 'success');
  } catch {
    showStatus('otp-status', 'Failed to resend.', 'error');
  } finally {
    setLoading('resend-btn', false, 'Resend OTP');
  }
});

// Open chat window
// popup.js — open-chat-btn fix
// Use user_id as fallback, and log state for debugging
$('open-chat-btn').addEventListener('click', async () => {
  const state = await chrome.runtime.sendMessage({ type: 'GET_AUTH_STATE' });
  const stored = await chrome.storage.local.get(['currentProject']);

  // Normalize: backend may return user_id instead of id
  const userId = state.user?.id || state.user?.user_id || '';
  const sessionId = state.sessionId || '';

  console.debug('[popup] open-chat state:', { userId, sessionId, state, stored });

  const params = new URLSearchParams({
    userId,
    sessionId,
    project: stored.currentProject || '',
    mobile: state.user?.mobile || ''
  });

  const chatUrl = chrome.runtime.getURL(`chat.html?${params}`);
  // Open chat inside the extension popup instead of a new browser tab
  window.location.href = chatUrl;
});

// Logout
$('logout-btn').addEventListener('click', async () => {
  await chrome.runtime.sendMessage({ type: 'LOGOUT' });
  $('step-loggedin').classList.add('hidden');
  $('step-mobile').classList.remove('hidden');
  $('mobile-input').value = '';
  $('otp-input').value = '';
  currentMobile = '';
});

// Enter key support
$('mobile-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') $('send-otp-btn').click();
});
$('otp-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') $('verify-otp-btn').click();
});

init();
