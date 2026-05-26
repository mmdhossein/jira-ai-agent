// preferences.js — all-in-one
const BASE_URL = 'http://localhost:8000';

const store = {
  get: k => new Promise(r => chrome.storage.local.get(k, d => r(d[k] ?? null))),
  set: (k, v) => new Promise(r => chrome.storage.local.set({ [k]: v }, r)),
  remove: (...keys) => new Promise(r => chrome.storage.local.remove(keys, r)),
};

const $ = id => document.getElementById(id);
const show = id => $(id).classList.remove('hidden');
const hide = id => $(id).classList.add('hidden');

async function init() {
  const email     = await store.get('user_email');
  const sessionId = await store.get('session_id');

  if (email)     $('inp-email').value = email;
  if (sessionId) $('lbl-session').textContent = sessionId;

  $('btn-back').addEventListener('click', () => {
    window.location.href = 'popup.html';
  });

  $('btn-save').addEventListener('click', async () => {
    hide('msg-success');
    hide('msg-error');
    const email = $('inp-email').value.trim();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      $('msg-error').textContent = 'Enter a valid email.';
      show('msg-error');
      return;
    }
    try {
      const token = await store.get('auth_token');
      await fetch(`${BASE_URL}/api/user/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ email })
      });
      await store.set('user_email', email);
      show('msg-success');
    } catch {
      $('msg-error').textContent = 'Failed to save. Try again.';
      show('msg-error');
    }
  });

  $('btn-new-session').addEventListener('click', async () => {
    const newId = crypto.randomUUID();
    await store.set('session_id', newId);
    await store.remove('chat_history', 'last_report');
    $('lbl-session').textContent = newId;
  });

  $('btn-logout').addEventListener('click', async () => {
    await store.remove('auth_token', 'user_id', 'session_id', 'chat_history', 'last_report');
    window.location.href = 'auth.html';
  });
}

document.addEventListener('DOMContentLoaded', init);
