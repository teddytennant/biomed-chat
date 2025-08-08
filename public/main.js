const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send');
const taResizerEl = document.getElementById('ta-resizer');

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

// Minimal markdown renderer for headings, bullets, code fences and inline code
function renderMarkdown(md) {
  // Escape HTML first
  let html = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Code fences ```
  html = html.replace(/```([\s\S]*?)```/g, (m, p1) => {
    return `<pre><code>${p1.replace(/\n$/, '')}</code></pre>`;
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
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Paragraphs
  html = html
    .split(/\n\n+/)
    .map(block => /<(h\d|ul|ol|pre)/.test(block) ? block : `<p>${block}</p>`)
    .join('');

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

  inputEl.value = '';
  appendBubble('user', text);
  conversation.push({ role: 'user', content: text });

  // Thinking placeholder
  const thinkingHtml = '<div class="md"><p class="thinking">Thinking<span class="dots"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span></p></div>';
  const assistantBubble = appendBubble('assistant', thinkingHtml, { asHtml: true });
  let assistantAccum = '';

  const controller = new AbortController();
  isSending = true;
  sendBtn.disabled = true;
  sendBtn.classList.add('loading');

  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: conversation }),
      signal: controller.signal,
    });

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
    assistantBubble.innerHTML = `<div class="md"><p>Error: ${err.message}</p></div>`;
  } finally {
    isSending = false;
    sendBtn.disabled = false;
    sendBtn.classList.remove('loading');
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

 