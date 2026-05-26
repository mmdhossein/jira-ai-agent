// api.js — message passing helpers

const API = {
  send: (msg) => chrome.runtime.sendMessage(msg),

  getAuthState: () => API.send({ type: 'GET_AUTH_STATE' }),

  getMessages: (userId, sessionId) =>
    API.send({ type: 'GET_MESSAGES', userId, sessionId }),

  sendMessage: (userId, sessionId, text, projectName) =>
    API.send({ type: 'SEND_MESSAGE', userId, sessionId, text, projectName }),

  getSessions: (userId) =>
    API.send({ type: 'GET_SESSIONS', userId }),

  logout: () => API.send({ type: 'LOGOUT' }),

  downloadPdf: (reportId) =>
    API.send({ type: 'DOWNLOAD_PDF', reportId })
};
