const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send');
const stopBtn = document.getElementById('stop');
const modelSelectEl = document.getElementById('model-select');
const taResizerEl = document.getElementById('ta-resizer');
const downloadLocalModelBtn = document.getElementById('download-local-model');
const localModelStatusEl = document.getElementById('local-model-status');
const localModelOptionEl = modelSelectEl
  ? modelSelectEl.querySelector('option[value="local-qwen-medical"]')
  : null;

let localModelState = 'unknown';
let localModelPollHandle = null;

/** @type {{ role: 'user'|'assistant'|'system', content: string }[]} */
let conversation = [];
let isSending = false;

function markHasContentIfNeeded() {
  if (!messagesEl.classList.contains('has-content')) {
    messagesEl.classList.add('has-content');
  }
}

function appendBubble(role, content, { asHtml = false } = {}) {
  const div = document.createElement('div');
  div.className = `bubble ${role === 'user' ? 'user' : 'assistant'}`;
  if (asHtml) {
    div.innerHTML = content;
  } else {
    div.textContent = content;
  }
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  markHasContentIfNeeded();
  return div;
}

function sanitizeUserInput(text) {
  return text.replace(/\s+$/g, '').trim();
}

function clearLocalModelPoll() {
  if (localModelPollHandle) {
    clearTimeout(localModelPollHandle);
    localModelPollHandle = null;
  }
}

function scheduleLocalModelPoll() {
  clearLocalModelPoll();
  localModelPollHandle = setTimeout(() => {
    fetchLocalModelStatus({ showErrors: false });
  }, 3000);
}

function applyLocalModelStatusUI(status) {
  if (!localModelStatusEl || !downloadLocalModelBtn) return;

  clearLocalModelPoll();

  const state = status?.state || 'error';
  localModelState = state;
  const detail = status?.detail || null;
  const device = status?.device || null;

  if (localModelOptionEl) {
    localModelOptionEl.disabled = state !== 'ready';
  }

  if (state !== 'ready' && modelSelectEl && modelSelectEl.value === 'local-qwen-medical') {
    modelSelectEl.value = 'grok-4';
    localStorage.setItem('selected_model', 'grok-4');
  }

  switch (state) {
    case 'ready':
      const deviceLabel = device === 'cuda' ? 'GPU' : device === 'cpu' ? 'CPU' : '';
      localModelStatusEl.textContent = detail
        ? detail
        : deviceLabel
          ? `Ready (${deviceLabel})`
          : 'Ready to use';
      downloadLocalModelBtn.textContent = deviceLabel ? `Ready (${deviceLabel})` : 'Ready';
      downloadLocalModelBtn.disabled = true;
      break;
    case 'downloading':
      const downloadDetail = detail || 'Downloading model files from HuggingFace...';
      localModelStatusEl.textContent = downloadDetail;
      if (device === 'cuda') {
        localModelStatusEl.textContent += ' (GPU mode: ~8 GB)';
      } else if (device === 'cpu') {
        localModelStatusEl.textContent += ' (CPU mode: ~22 GB)';
      }
      downloadLocalModelBtn.textContent = 'Downloading...';
      downloadLocalModelBtn.disabled = true;
      scheduleLocalModelPoll();
      break;
    case 'loading':
      const loadingDetail = detail || 'Loading model into memory...';
      localModelStatusEl.textContent = loadingDetail;
      downloadLocalModelBtn.textContent = 'Loading...';
      downloadLocalModelBtn.disabled = true;
      scheduleLocalModelPoll();
      break;
    case 'error':
      if (status?.error) {
        localModelStatusEl.textContent = `Error: ${status.error}`;
      } else if (detail) {
        localModelStatusEl.textContent = detail;
      } else {
        localModelStatusEl.textContent = 'Error preparing local model.';
      }
      downloadLocalModelBtn.textContent = 'Retry';
      downloadLocalModelBtn.disabled = false;
      break;
    default:
      localModelStatusEl.textContent = 'Not installed';
      downloadLocalModelBtn.textContent = 'Download';
      downloadLocalModelBtn.disabled = false;
      break;
  }
}

async function fetchLocalModelStatus({ showErrors = true } = {}) {
  if (!localModelStatusEl || !downloadLocalModelBtn) return;
  try {
    const resp = await fetch('/api/models/local/status');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    applyLocalModelStatusUI(data);
  } catch (err) {
    localModelState = 'error';
    if (showErrors) {
      localModelStatusEl.textContent = 'Status unavailable';
    }
    downloadLocalModelBtn.textContent = 'Retry';
    downloadLocalModelBtn.disabled = false;
    if (localModelOptionEl) localModelOptionEl.disabled = true;
    console.error('[Local model status] failed', err);
  }
}

// Minimal markdown renderer for headings, bullets, code fences and inline code
function renderMarkdown(md) {
  // Escape HTML first
  let html = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Code fences ```
  html = html.replace(/```([\s\S]*?)```/g, (m, p1) => {
    const code = p1.replace(/\n$/, '');
    return `<pre><button class="copy-btn">Copy</button><code>${code}</code></pre>`;
  });
  // Headings ###, ##, #
  html = html
    .replace(/^###\s+(.*)$/gm, '<h3>$1</h3>')
    .replace(/^##\s+(.*)$/gm, '<h2>$1</h2>')
    .replace(/^#\s+(.*)$/gm, '<h1>$1</h1>');
  // Bulleted lists
  html = html.replace(/^(?:- |\* )(.*)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m.replace(/\n/g, '')}</ul>`);
  // Numbered lists
  html = html.replace(/^\d+\.\s+(.*)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ol>${m.replace(/\n/g, '')}</ol>`);
  // Inline code `code`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');  // Bold  html = html.replace(/\*\*([\s\S]+?)\*\*/g, '<strong>$1</strong>');  // Paragraphs  html = html    .split(/\n\n+/)    .map(block => /<(h\d|ul|ol|pre)/.test(block) ? block : `<p>${block}</p>`)    .join('');

  return `<div class="md">${html}</div>`;
}

// Textarea drag-to-resize
(function setupTextareaResizer() {
  if (!taResizerEl || !inputEl) return;
  const MIN = 80;  // px
  const MAX = Math.round(window.innerHeight * 0.6); // cap at 60% viewport

  // Restore previous height
  const saved = parseInt(localStorage.getItem('textarea_height_px') || '0', 10);
  if (saved && !Number.isNaN(saved)) {
    inputEl.style.minHeight = `${Math.min(MAX, Math.max(MIN, saved))}px`;
  }

  let isDragging = false;
  let startY = 0;
  let startH = 0;

  const onDown = (e) => {
    isDragging = true;
    startY = e.clientY;
    startH = parseInt(window.getComputedStyle(inputEl).minHeight);
    document.body.style.cursor = 'ns-resize';
    e.preventDefault();
  };

  const onMove = (e) => {
    if (!isDragging) return;
    const delta = startY - e.clientY; // drag upward increases height
    let next = startH + delta;
    next = Math.min(MAX, Math.max(MIN, next));
    inputEl.style.minHeight = `${next}px`;
  };

  const onUp = () => {
    if (!isDragging) return;
    isDragging = false;
    document.body.style.cursor = '';
    const h = parseInt(window.getComputedStyle(inputEl).minHeight);
    if (!Number.isNaN(h)) localStorage.setItem('textarea_height_px', String(h));
  };

  taResizerEl.addEventListener('mousedown', onDown);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);
})();

async function sendMessage() {
  if (isSending) return;
  const text = sanitizeUserInput(inputEl.value);
  if (!text) return;

  const selectedModel = modelSelectEl.value;
  if (selectedModel === 'local-qwen-medical' && localModelState !== 'ready') {
    appendBubble(
      'assistant',
      'Local model is not ready yet. Open Settings to finish the download before using it.'
    );
    return;
  }

  inputEl.value = '';
  appendBubble('user', text);
  conversation.push({ role: 'user', content: text });

  // Thinking placeholder
  const thinkingHtml = '<div class="md"><p class="thinking">Thinking<span class="dots"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span></p></div>';
  const assistantBubble = appendBubble('assistant', thinkingHtml, { asHtml: true });
  let assistantAccum = '';

  const controller = new AbortController();
  const signal = controller.signal;

  const stop = () => controller.abort();
  stopBtn.addEventListener('click', stop);

  isSending = true;
  sendBtn.classList.add('hidden');
  stopBtn.classList.remove('hidden');
  inputEl.disabled = true;

  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: conversation, model: selectedModel }),
      signal,
    });

    if (resp.status === 401) {
      window.location.href = '/login.html';
      return;
    }

    if (!resp.ok || !resp.body) {
      throw new Error(`HTTP ${resp.status}`);
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const blocks = buffer.split('\n\n');
      buffer = blocks.pop() || '';

      for (const block of blocks) {
        const line = block.trim();
        if (!line) continue;
        const dataLine = line.split('\n').find(l => l.startsWith('data: '));
        if (!dataLine) continue;
        const payload = dataLine.slice(6);
        if (payload === '[DONE]') continue;
        try {
          const parsed = JSON.parse(payload);
          const delta = parsed?.choices?.[0]?.delta?.content ?? '';
          if (delta) {
            assistantAccum += delta;
            assistantBubble.innerHTML = renderMarkdown(assistantAccum);
            messagesEl.scrollTop = messagesEl.scrollHeight;
          }
        } catch (_) {
          // Ignore parse errors on keepalive lines
        }
      }
    }

    if (assistantAccum.trim()) {
      conversation.push({ role: 'assistant', content: assistantAccum });
    }
  } catch (err) {
    if (err.name !== 'AbortError') {
      assistantBubble.innerHTML = `<div class="md"><p>Error: ${err.message}</p></div>`;
    } else {
      assistantBubble.innerHTML = renderMarkdown(assistantAccum + '...');
    }
  } finally {
    isSending = false;
    sendBtn.classList.remove('hidden');
    stopBtn.classList.add('hidden');
    inputEl.disabled = false;
    stopBtn.removeEventListener('click', stop);
    inputEl.focus();
  }
}

sendBtn.addEventListener('click', sendMessage);

inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Prefill a gentle nudge for first-time users
if (!localStorage.getItem('biomed_welcome_shown')) {
  const demo = 'Design a 3‑lead ECG analog front end meeting IEC 60601 leakage limits. Provide parts, gain structure, input filtering, and noise budget.';
  inputEl.value = demo;
  localStorage.setItem('biomed_welcome_shown', '1');
}

// Restore model selection
const savedModel = localStorage.getItem('selected_model');
if (savedModel) {
  modelSelectEl.value = savedModel;
}

modelSelectEl.addEventListener('change', () => {
  localStorage.setItem('selected_model', modelSelectEl.value);
});

if (downloadLocalModelBtn && localModelStatusEl) {
  downloadLocalModelBtn.addEventListener('click', async () => {
    downloadLocalModelBtn.disabled = true;
    downloadLocalModelBtn.textContent = 'Starting...';
    localModelStatusEl.textContent = 'Starting download...';

    try {
      const resp = await fetch('/api/models/local/download', { method: 'POST' });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      applyLocalModelStatusUI(data);
    } catch (err) {
      localModelState = 'error';
      localModelStatusEl.textContent = 'Failed to start download';
      downloadLocalModelBtn.textContent = 'Retry';
      downloadLocalModelBtn.disabled = false;
      console.error('[Local model download] failed', err);
    }
  });

  fetchLocalModelStatus();
} else {
  localModelState = 'unsupported';
}

messagesEl.addEventListener('click', (e) => {
  if (e.target.classList.contains('copy-btn')) {
    const pre = e.target.closest('pre');
    const code = pre.querySelector('code');
    navigator.clipboard.writeText(code.innerText);
    e.target.innerText = 'Copied!';
    setTimeout(() => {
      e.target.innerText = 'Copy';
    }, 2000);
  }
});

 