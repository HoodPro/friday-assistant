import React, { useState, useRef, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&family=Orbitron:wght@400;500;600;700;800;900&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --gold: #c8a44a;
    --gold-bright: #f0c060;
    --gold-dim: #7a6030;
    --red: #c0392b;
    --red-bright: #e74c3c;
    --bg: #050810;
    --bg2: #080d18;
    --panel: rgba(10, 20, 40, 0.85);
    --border: rgba(200, 164, 74, 0.25);
    --border-bright: rgba(200, 164, 74, 0.6);
    --text: #d0ddf0;
    --text-dim: #607090;
    --glow: 0 0 20px rgba(200, 164, 74, 0.3);
    --glow-strong: 0 0 40px rgba(200, 164, 74, 0.5);
  }

  html, body { height: 100%; background: var(--bg); color: var(--text); font-family: 'Rajdhani', sans-serif; overflow: hidden; }
  #root { height: 100%; }

  @keyframes scanline {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
  }
  @keyframes pulse-ring {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.05); opacity: 0.4; }
    100% { transform: scale(0.95); opacity: 0.8; }
  }
  @keyframes rotate-slow {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  @keyframes rotate-rev {
    from { transform: rotate(360deg); }
    to { transform: rotate(0deg); }
  }
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes waveform {
    0%, 100% { height: 4px; }
    50% { height: 22px; }
  }
  @keyframes flicker {
    0%, 100% { opacity: 1; }
    92% { opacity: 1; }
    93% { opacity: 0.6; }
    94% { opacity: 1; }
  }

  .app {
    height: 100vh; display: flex; flex-direction: column;
    background: var(--bg); position: relative; overflow: hidden;
  }

  .bg-grid {
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
      linear-gradient(rgba(200,164,74,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(200,164,74,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  .bg-scanline {
    position: fixed; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(transparent, rgba(200,164,74,0.12), transparent);
    z-index: 1; pointer-events: none;
    animation: scanline 7s linear infinite;
  }

  .header {
    position: relative; z-index: 10;
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 24px;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(5,8,16,0.99), rgba(8,13,24,0.97));
    backdrop-filter: blur(20px);
    animation: flicker 8s infinite;
  }

  .header-left { display: flex; align-items: center; gap: 16px; }

  .arc-reactor { width: 46px; height: 46px; position: relative; flex-shrink: 0; }
  .arc-reactor svg { width: 100%; height: 100%; }
  .arc-outer { animation: rotate-slow 8s linear infinite; transform-origin: 23px 23px; }
  .arc-inner { animation: rotate-rev 5s linear infinite; transform-origin: 23px 23px; }
  .arc-core { animation: pulse-ring 2s ease-in-out infinite; transform-origin: 23px 23px; }

  .title-block {}
  .title-main {
    font-family: 'Orbitron', monospace;
    font-size: clamp(15px, 3vw, 20px);
    font-weight: 800; color: var(--gold-bright);
    letter-spacing: 5px;
    text-shadow: 0 0 25px rgba(240,192,96,0.7);
    line-height: 1;
  }
  .title-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px; color: var(--text-dim);
    letter-spacing: 2px; margin-top: 3px;
  }

  .header-right { display: flex; align-items: center; gap: 14px; }

  .status-pill {
    display: flex; align-items: center; gap: 6px;
    padding: 5px 12px;
    border: 1px solid rgba(46,204,113,0.3);
    border-radius: 2px;
    background: rgba(46,204,113,0.05);
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px; color: #2ecc71; letter-spacing: 2px;
  }
  .status-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #2ecc71; box-shadow: 0 0 8px #2ecc71;
    animation: pulse-ring 2s infinite;
  }

  .gemini-badge {
    padding: 5px 12px;
    border: 1px solid var(--border);
    border-radius: 2px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px; color: var(--gold-dim); letter-spacing: 2px;
    background: rgba(200,164,74,0.05);
  }

  .main { flex: 1; display: flex; flex-direction: column; position: relative; z-index: 5; overflow: hidden; }

  .chat-area {
    flex: 1; overflow-y: auto; padding: 24px;
    display: flex; flex-direction: column; gap: 18px;
    scrollbar-width: thin; scrollbar-color: var(--gold-dim) transparent;
  }
  .chat-area::-webkit-scrollbar { width: 3px; }
  .chat-area::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 2px; }

  .welcome { text-align: center; padding: 30px 20px; animation: fadeIn 1s ease; }
  .welcome-ring { width: 110px; height: 110px; margin: 0 auto 28px; }
  .welcome-ring svg { width: 100%; height: 100%; }

  .welcome-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(18px, 5vw, 30px);
    font-weight: 900; color: var(--gold-bright);
    letter-spacing: 8px;
    text-shadow: 0 0 40px rgba(240,192,96,0.6);
    margin-bottom: 6px;
  }
  .welcome-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px; color: var(--text-dim);
    letter-spacing: 3px; margin-bottom: 10px;
  }
  .welcome-model {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px; color: var(--gold-dim);
    letter-spacing: 2px; margin-bottom: 32px;
  }

  .suggestions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; max-width: 650px; margin: 0 auto; }
  .suggestion {
    padding: 8px 16px; border: 1px solid var(--border); border-radius: 3px;
    font-family: 'Rajdhani', sans-serif; font-size: 13px; color: var(--text-dim);
    cursor: pointer; background: var(--panel); transition: all 0.2s; letter-spacing: 0.5px;
  }
  .suggestion:hover { border-color: var(--gold); color: var(--gold-bright); box-shadow: var(--glow); background: rgba(200,164,74,0.05); }

  .message { display: flex; gap: 12px; animation: fadeIn 0.35s ease; max-width: 820px; }
  .message.user { align-self: flex-end; flex-direction: row-reverse; }
  .message.assistant { align-self: flex-start; }

  .msg-avatar {
    width: 34px; height: 34px; flex-shrink: 0; border-radius: 2px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Orbitron', monospace; font-size: 8px; letter-spacing: 1px; font-weight: 700;
  }
  .msg-avatar.user-av { background: rgba(192,57,43,0.15); border: 1px solid rgba(192,57,43,0.4); color: var(--red-bright); }
  .msg-avatar.fri-av { background: rgba(200,164,74,0.08); border: 1px solid var(--border); color: var(--gold); }

  .msg-body {}
  .msg-label { font-family: 'Share Tech Mono', monospace; font-size: 9px; letter-spacing: 2px; margin-bottom: 5px; }
  .message.user .msg-label { color: var(--red); text-align: right; }
  .message.assistant .msg-label { color: var(--gold-dim); }

  .msg-bubble {
    padding: 13px 17px; border-radius: 3px;
    font-size: 15px; line-height: 1.65;
    max-width: calc(100% - 46px); white-space: pre-wrap;
  }
  .message.user .msg-bubble { background: rgba(192,57,43,0.08); border: 1px solid rgba(192,57,43,0.25); border-radius: 3px 0 3px 3px; }
  .message.assistant .msg-bubble { background: var(--panel); border: 1px solid var(--border); border-radius: 0 3px 3px 3px; }

  .typing { display: flex; gap: 3px; align-items: flex-end; height: 24px; }
  .typing-bar {
    width: 3px; background: var(--gold); border-radius: 2px;
    animation: waveform 0.7s ease-in-out infinite;
  }
  .typing-bar:nth-child(2) { animation-delay: 0.1s; }
  .typing-bar:nth-child(3) { animation-delay: 0.2s; }
  .typing-bar:nth-child(4) { animation-delay: 0.3s; }
  .typing-bar:nth-child(5) { animation-delay: 0.4s; }

  .input-area {
    padding: 16px 24px;
    border-top: 1px solid var(--border);
    background: linear-gradient(0deg, rgba(5,8,16,0.99), rgba(8,13,24,0.97));
    backdrop-filter: blur(20px);
  }

  .input-row { display: flex; gap: 10px; align-items: flex-end; max-width: 900px; margin: 0 auto; }

  .input-wrap {
    flex: 1; border: 1px solid var(--border); border-radius: 3px;
    background: rgba(10,20,40,0.8); transition: border-color 0.2s, box-shadow 0.2s;
  }
  .input-wrap:focus-within { border-color: var(--gold-dim); box-shadow: 0 0 15px rgba(200,164,74,0.1); }

  .input-field {
    width: 100%; min-height: 46px; max-height: 130px;
    padding: 13px 16px; background: transparent; border: none; outline: none;
    color: var(--text); font-family: 'Rajdhani', sans-serif;
    font-size: 15px; line-height: 1.4; resize: none;
  }
  .input-field::placeholder { color: var(--text-dim); }

  .icon-btn {
    width: 46px; height: 46px; flex-shrink: 0; border-radius: 3px;
    border: 1px solid var(--border); background: rgba(10,20,40,0.8);
    color: var(--text-dim); cursor: pointer; display: flex;
    align-items: center; justify-content: center;
    transition: all 0.2s; font-size: 17px;
  }
  .icon-btn:hover:not(:disabled) { border-color: var(--gold); color: var(--gold); box-shadow: var(--glow); }
  .icon-btn.mic-active { border-color: var(--red-bright); color: var(--red-bright); box-shadow: 0 0 15px rgba(231,76,60,0.4); animation: pulse-ring 1s infinite; }
  .icon-btn.send-btn { background: rgba(200,164,74,0.08); border-color: var(--gold-dim); color: var(--gold); }
  .icon-btn.send-btn:hover:not(:disabled) { background: rgba(200,164,74,0.18); box-shadow: var(--glow-strong); }
  .icon-btn:disabled { opacity: 0.3; cursor: not-allowed; }

  .footer-bar {
    display: flex; justify-content: space-between; align-items: center;
    margin: 8px auto 0; padding: 0 2px;
    font-family: 'Share Tech Mono', monospace; font-size: 9px;
    color: var(--text-dim); letter-spacing: 1px;
    max-width: 900px; width: 100%;
  }

  @media (max-width: 600px) {
    .header { padding: 10px 14px; }
    .chat-area { padding: 14px; gap: 14px; }
    .input-area { padding: 12px 14px; }
    .gemini-badge { display: none; }
  }
`;

function ArcReactor() {
  return (
    <svg viewBox="0 0 46 46" fill="none">
      <g className="arc-outer">
        <circle cx="23" cy="23" r="21" stroke="#c8a44a" strokeWidth="0.5" strokeOpacity="0.35" />
        {[0,45,90,135,180,225,270,315].map(a => (
          <line key={a}
            x1={23 + 18 * Math.cos(a * Math.PI / 180)}
            y1={23 + 18 * Math.sin(a * Math.PI / 180)}
            x2={23 + 21 * Math.cos(a * Math.PI / 180)}
            y2={23 + 21 * Math.sin(a * Math.PI / 180)}
            stroke="#c8a44a" strokeWidth="1.2" strokeOpacity="0.6" />
        ))}
      </g>
      <g className="arc-inner">
        <circle cx="23" cy="23" r="14" stroke="#f0c060" strokeWidth="0.8" strokeOpacity="0.45" strokeDasharray="4 3" />
      </g>
      <g className="arc-core">
        <circle cx="23" cy="23" r="8" fill="rgba(200,164,74,0.06)" stroke="#f0c060" strokeWidth="1" strokeOpacity="0.8" />
        <circle cx="23" cy="23" r="4.5" fill="rgba(240,192,96,0.25)" />
        <circle cx="23" cy="23" r="2" fill="#f0c060" />
      </g>
    </svg>
  );
}

function WelcomeRing() {
  return (
    <svg viewBox="0 0 110 110" fill="none">
      <g style={{ animation: 'rotate-slow 12s linear infinite', transformOrigin: '55px 55px' }}>
        <circle cx="55" cy="55" r="51" stroke="#c8a44a" strokeWidth="0.5" strokeOpacity="0.3" strokeDasharray="8 5" />
      </g>
      <g style={{ animation: 'rotate-rev 8s linear infinite', transformOrigin: '55px 55px' }}>
        <circle cx="55" cy="55" r="42" stroke="#f0c060" strokeWidth="0.5" strokeOpacity="0.4" strokeDasharray="3 7" />
      </g>
      <circle cx="55" cy="55" r="30" fill="rgba(200,164,74,0.04)" stroke="#c8a44a" strokeWidth="1" strokeOpacity="0.5" />
      <circle cx="55" cy="55" r="18" fill="rgba(200,164,74,0.07)" />
      <circle cx="55" cy="55" r="7" fill="rgba(240,192,96,0.4)" />
      <circle cx="55" cy="55" r="3.5" fill="#f0c060" />
    </svg>
  );
}

const SUGGESTIONS = [
  "What's in the news today?",
  "Explain quantum entanglement",
  "Help me write a Python script",
  "Search: latest AI research 2025",
  "What is the speed of light?",
  "Tell me a fun science fact",
];

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const chatRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = styles;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [messages, loading]);

  const speak = useCallback((text) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text.substring(0, 600));
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v =>
      v.name.includes('Google UK English Female') ||
      v.name.includes('Samantha') ||
      v.name.includes('Victoria') ||
      (v.lang === 'en-US' && v.name.toLowerCase().includes('female'))
    ) || voices.find(v => v.lang.startsWith('en'));
    if (preferred) utter.voice = preferred;
    utter.rate = 0.93; utter.pitch = 1.05; utter.volume = 1;
    window.speechSynthesis.speak(utter);
  }, []);

  const sendMessage = useCallback(async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setInput('');
    const userMsg = { role: 'user', content: msg };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Request failed');
      }
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      speak(data.response);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `⚠️ System error: ${err.message}\n\nMake sure the backend is running and your GOOGLE_API_KEY is set correctly.`
      }]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, messages, speak]);

  const toggleVoice = useCallback(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { alert('Voice input requires Chrome or Edge browser.'); return; }
    if (listening) { recognitionRef.current?.stop(); setListening(false); return; }
    const rec = new SR();
    rec.lang = 'en-US'; rec.continuous = false; rec.interimResults = false;
    rec.onresult = (e) => { setInput(e.results[0][0].transcript); setListening(false); };
    rec.onerror = () => setListening(false);
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
    rec.start(); setListening(true);
  }, [listening]);

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div className="app">
      <div className="bg-grid" />
      <div className="bg-scanline" />

      <header className="header">
        <div className="header-left">
          <div className="arc-reactor"><ArcReactor /></div>
          <div className="title-block">
            <div className="title-main">F.R.I.D.A.Y.</div>
            <div className="title-sub">STARK INDUSTRIES · ADVANCED AI SYSTEM v2.0</div>
          </div>
        </div>
        <div className="header-right">
          <div className="gemini-badge">GEMINI 2.0 FLASH</div>
          <div className="status-pill">
            <div className="status-dot" />
            ONLINE
          </div>
        </div>
      </header>

      <main className="main">
        <div className="chat-area" ref={chatRef}>
          {messages.length === 0 && (
            <div className="welcome">
              <div className="welcome-ring"><WelcomeRing /></div>
              <div className="welcome-title">GOOD TO SEE YOU</div>
              <div className="welcome-sub">F.R.I.D.A.Y. ONLINE · ALL SYSTEMS NOMINAL</div>
              <div className="welcome-model">POWERED BY GEMINI 2.0 FLASH · WEB SEARCH ENABLED</div>
              <div className="suggestions">
                {SUGGESTIONS.map((s, i) => (
                  <button key={i} className="suggestion" onClick={() => sendMessage(s)}>{s}</button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className={`msg-avatar ${msg.role === 'user' ? 'user-av' : 'fri-av'}`}>
                {msg.role === 'user' ? 'YOU' : 'FRI'}
              </div>
              <div className="msg-body">
                <div className="msg-label">{msg.role === 'user' ? 'OPERATOR' : 'F.R.I.D.A.Y.'}</div>
                <div className="msg-bubble">{msg.content}</div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="msg-avatar fri-av">FRI</div>
              <div className="msg-body">
                <div className="msg-label">F.R.I.D.A.Y.</div>
                <div className="msg-bubble">
                  <div className="typing">
                    {[0,1,2,3,4].map(i => <div key={i} className="typing-bar" style={{ animationDelay: `${i * 0.1}s` }} />)}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="input-area">
          <div className="input-row">
            <button className={`icon-btn${listening ? ' mic-active' : ''}`} onClick={toggleVoice} title={listening ? 'Stop' : 'Voice input'}>
              {listening ? '⏹' : '🎙'}
            </button>
            <div className="input-wrap">
              <textarea
                className="input-field"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                placeholder={listening ? 'Listening...' : 'Speak or type your command...'}
                rows={1}
              />
            </div>
            <button className="icon-btn send-btn" onClick={() => sendMessage()} disabled={loading || !input.trim()} title="Send">
              ➤
            </button>
          </div>
          <div className="footer-bar">
            <span>SHIFT+ENTER FOR NEW LINE · ENTER TO SEND</span>
            <span>FREE · NO SUBSCRIPTION NEEDED</span>
          </div>
        </div>
      </main>
    </div>
  );
}
