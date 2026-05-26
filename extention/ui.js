// ui.js — DOM rendering helpers

const UI = {

  // Format timestamp
  formatTime(ts) {
    if (!ts) return '';
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  },

  // Auto-resize textarea
  autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  },

  // Scroll messages to bottom
  scrollToBottom(container) {
    container.scrollTop = container.scrollHeight;
  },

  // Show typing indicator
  showTyping(container, avatarChar) {
    const row = document.createElement('div');
    row.className = 'message-row bot typing-indicator';
    row.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar bot';
    avatar.textContent = avatarChar;

    const dotsContainer = document.createElement('div');
    dotsContainer.className = 'typing-dots';
    
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement('span');
      dotsContainer.appendChild(dot);
    }

    row.appendChild(avatar);
    row.appendChild(dotsContainer);
    container.appendChild(row);
    return row;
  },

  // Remove typing indicator
  removeTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
  },

  // Render a single message bubble
  renderMessage(container, msg, userAvatarChar) {
    const isUser = msg.role === 'user';
    const row = document.createElement('div');
    row.className = `message-row ${isUser ? 'user' : 'bot'}`;

    const avatar = document.createElement('div');
    avatar.className = `msg-avatar ${isUser ? 'user-av' : 'bot'}`;
    avatar.textContent = isUser ? userAvatarChar : '🤖';

    const content = document.createElement('div');
    content.className = 'msg-content';

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    
    // Sanitize and render text
    const text = UI.escapeHtml(msg.content || msg.text || '');
    bubble.innerHTML = text;

    const time = document.createElement('div');
    time.className = 'msg-time';
    time.textContent = UI.formatTime(msg.timestamp || msg.created_at);

    content.appendChild(bubble);

    // Add image if present
    if (msg.resolvedImageUrl) {
      const imgWrapper = document.createElement('div');
      imgWrapper.style.marginTop = '8px';
      const img = document.createElement('img');
      img.src = msg.resolvedImageUrl;
      img.alt = 'Chart';
      img.loading = 'lazy';
      img.style.maxWidth = '100%';
      img.style.borderRadius = '8px';
      img.onerror = function() { this.parentElement.remove(); };
      imgWrapper.appendChild(img);
      content.appendChild(imgWrapper);
    }

    // Add PDF download button if present
    if (msg.resolvedPdfUrl) {
      const pdfBtn = document.createElement('a');
      pdfBtn.href = msg.resolvedPdfUrl;
      pdfBtn.target = '_blank';
      pdfBtn.download = true;
      pdfBtn.style.marginTop = '8px';
      pdfBtn.style.display = 'inline-block';
      pdfBtn.style.padding = '8px 12px';
      pdfBtn.style.background = 'rgba(139, 92, 246, 0.15)';
      pdfBtn.style.border = '1px solid rgba(139, 92, 246, 0.3)';
      pdfBtn.style.borderRadius = '8px';
      pdfBtn.style.color = '#c4b5fd';
      pdfBtn.style.textDecoration = 'none';
      pdfBtn.style.fontSize = '12px';
      pdfBtn.textContent = '📄 Download PDF';
      content.appendChild(pdfBtn);
    }

    content.appendChild(time);

    row.appendChild(avatar);
    row.appendChild(content);
    container.appendChild(row);
    return row;
  },

  // Render all history messages
  renderHistory(container, messages, userAvatarChar) {
    messages.forEach((msg) => UI.renderMessage(container, msg, userAvatarChar));
  },

  // Basic HTML escape to prevent XSS
  escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
      .replace(/\n/g, '<br>');
  }
};
