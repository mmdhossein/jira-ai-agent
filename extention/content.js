// content.js — injected into Jira pages (localhost:8080)

// Check if we're on localhost:8080
const isLocalJira = window.location.hostname === 'localhost' && window.location.port === '8080';
if (!isLocalJira) {
  console.debug('[content] Not on localhost:8080, extension hidden');
  // Extension won't load on non-Jira pages due to manifest restrictions
}

// Extract project name and send to background when page loads
function getProjectName() {
  const urlMatch = window.location.pathname.match(/\/projects\/([A-Z][A-Z0-9_-]*)/i);
  if (urlMatch) return urlMatch[1].toUpperCase();

  const breadcrumb = document.querySelector(
    '[data-testid="project-breadcrumb"] span, .project-title'
  );
  if (breadcrumb) return breadcrumb.textContent.trim();

  const titleMatch = document.title.match(/^([A-Z][A-Z0-9_-]+)\s*[-|]/);
  if (titleMatch) return titleMatch[1];

  return null;
}

// Notify background of current project
chrome.runtime.sendMessage({
  type: 'PAGE_PROJECT',
  projectName: getProjectName(),
  url: window.location.href
});

// Listen for project name requests
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'REQUEST_PROJECT_NAME') {
    sendResponse({ projectName: getProjectName() });
  }
});
