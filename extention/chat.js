// chat.js — main chat page controller

(async () => {
  // Parse URL params
  const params = new URLSearchParams(window.location.search);
  const userId    = params.get('userId')    || '';
  const sessionId = params.get('sessionId') || '1';
  const project   = params.get('project')   || '';
  const mobile    = params.get('mobile')    || '';

  // Guard: redirect if not authenticated
  const authState = await API.getAuthState();
  if (!authState.isAuthenticated) {
    window.close();
    return;
  }

  // Handle tab visibility changes — keep chat open while waiting for messages
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      // User came back to the extension, keep it open
      console.debug('[chat] User returned to extension tab');
    }
  });

  const user = authState.user;
  const avatarChar = (user?.name || mobile || 'U').charAt(0).toUpperCase();

  // ── Populate sidebar ──
  document.getElementById('sidebar-project-name').textContent =
    project || 'No project';
  document.getElementById('topbar-project-label').textContent =
    project ? `Project: ${project}` : 'No project detected';
  document.getElementById('session-label').textContent =
    `Session #${sessionId}`;
  document.getElementById('sidebar-avatar').textContent = avatarChar;
  document.getElementById('sidebar-name').textContent =
    user?.name || 'Manager';
  document.getElementById('sidebar-mobile').textContent =
    user?.mobile || mobile;

  // ── DOM refs ──
  const messagesContainer = document.getElementById('messages-container');
  const welcomeBlock      = document.getElementById('welcome-block');
  const chatInput         = document.getElementById('chat-input');
  const sendBtn           = document.getElementById('send-btn');

  // ── Load message history ──
  try {
    const history = await API.getMessages(userId, sessionId);
    const msgs = Array.isArray(history) ? history : (history.messages || []);

    if (msgs.length > 0) {
      welcomeBlock.classList.add('hidden');
      UI.renderHistory(messagesContainer, msgs, avatarChar);
      UI.scrollToBottom(messagesContainer);
    }
  } catch (err) {
    console.warn('Could not load history:', err);
  }

  // ── Input handling ──
  chatInput.addEventListener('input', () => {
    UI.autoResize(chatInput);
    sendBtn.disabled = chatInput.value.trim().length === 0;
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) sendMessage();
    }
  });

  sendBtn.addEventListener('click', sendMessage);

  // ── Suggestion chips ──
  document.querySelectorAll('.chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      chatInput.value = chip.textContent;
      chatInput.dispatchEvent(new Event('input'));
      sendMessage();
    });
  });

  // ── Send message ──
  async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Hide welcome block on first message
    welcomeBlock.classList.add('hidden');

    // Render user bubble immediately
    UI.renderMessage(
      messagesContainer,
      { role: 'user', content: text, timestamp: new Date().toISOString() },
      avatarChar
    );

    chatInput.value = '';
    chatInput.style.height = 'auto';
    sendBtn.disabled = true;
    UI.scrollToBottom(messagesContainer);

    // Show typing indicator
    UI.showTyping(messagesContainer, '🤖');
    UI.scrollToBottom(messagesContainer);

    try {
      const res = await API.sendMessage(userId, sessionId, text, project);
      UI.removeTyping();

      if (res.error) {
        UI.renderMessage(
          messagesContainer,
          {
            role: 'bot',
            content: `⚠️ Error: ${res.error}`,
            timestamp: new Date().toISOString()
          },
          avatarChar
        );
      } else {
        // Build the message object for rendering
        const botMsg = {
          role: 'bot',
          content: res.answer || res.message || res.text || '' ,
          timestamp: new Date().toISOString(),
          resolvedImageUrl: res.resolvedImageUrl || null,
          resolvedPdfUrl:   res.resolvedPdfUrl   || null
        };
        UI.renderMessage(messagesContainer, botMsg, avatarChar);
      }
    } catch (err) {
      UI.removeTyping();
      UI.renderMessage(
        messagesContainer,
        {
          role: 'bot',
          content: '⚠️ Something went wrong. Please try again.',
          timestamp: new Date().toISOString()
        },
        avatarChar
      );
      console.error('sendMessage error:', err);
    }

    UI.scrollToBottom(messagesContainer);
  }

  // ── New session ──
  document.getElementById('new-session-btn').addEventListener('click', async () => {
    // Get sessions to determine next session number
    try {
      const sessionsRes = await API.getSessions(userId);
      const sessions = Array.isArray(sessionsRes)
        ? sessionsRes
        : (sessionsRes.sessions || []);
      const nextId = sessions.length + 1;

      // Reload chat page with new session
      const newParams = new URLSearchParams({
        userId,
        sessionId: String(nextId),
        project,
        mobile
      });
      window.location.search = newParams.toString();
    } catch (err) {
      console.error('new session error:', err);
    }
  });

  // ── Logout ──
  document.getElementById('logout-btn').addEventListener('click', async () => {
    await API.logout();
    window.close();
  });

})();
