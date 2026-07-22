import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Shield, Send, Trash2, AlertTriangle, Search, Plus, Clock, ChevronRight, Activity } from 'lucide-react';

const API = 'http://localhost:8000';

const COLORS = {
  bg: '#F8F9FA',
  surface: '#FFFFFF',
  border: '#E2E8F0',
  borderStrong: '#CBD5E1',
  text: '#0F172A',
  textSecondary: '#475569',
  textMuted: '#94A3B8',
  accent: '#E63946',
  accentLight: '#FEF2F2',
  accentSecondary: '#1D3557',
  success: '#059669',
  warning: '#D97706',
  info: '#2563EB',
  infoLight: '#EFF6FF',
  sidebarBg: '#1A2332',
  sidebarText: '#CBD5E1',
  sidebarActive: '#2D3F55',
  sidebarAccent: '#E63946',
};

const styles = {
  app: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    backgroundColor: COLORS.bg,
    minHeight: '100vh',
    color: COLORS.text,
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    backgroundColor: COLORS.accentSecondary,
    color: '#FFFFFF',
    padding: '0 20px',
    height: '52px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottom: `3px solid ${COLORS.accent}`,
    flexShrink: 0,
    zIndex: 10,
  },
  headerLeft: { display: 'flex', alignItems: 'center', gap: '10px' },
  headerTitle: { fontSize: '15px', fontWeight: '700', letterSpacing: '0.5px', margin: 0 },
  headerSubtitle: { fontSize: '10px', opacity: 0.6, margin: 0, letterSpacing: '1.5px', textTransform: 'uppercase' },
  liveBadge: {
    display: 'flex', alignItems: 'center', gap: '6px',
    backgroundColor: 'rgba(255,255,255,0.1)', padding: '4px 10px',
    borderRadius: '4px', fontSize: '11px', border: '1px solid rgba(255,255,255,0.15)',
  },
  liveDot: { width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#4ADE80', animation: 'pulse 2s infinite' },
  body: { display: 'flex', flex: 1, overflow: 'hidden', height: 'calc(100vh - 52px)' },

  // SIDEBAR
  sidebar: {
    width: '240px', backgroundColor: COLORS.sidebarBg, display: 'flex',
    flexDirection: 'column', flexShrink: 0, overflow: 'hidden',
    borderRight: '1px solid rgba(255,255,255,0.06)',
  },
  newInvestigationBtn: {
    margin: '12px', padding: '9px 14px', borderRadius: '6px',
    backgroundColor: COLORS.accent, color: '#fff', border: 'none',
    fontSize: '12px', fontWeight: '600', cursor: 'pointer',
    display: 'flex', alignItems: 'center', gap: '7px', letterSpacing: '0.3px',
  },
  sidebarSection: { padding: '0 12px 8px' },
  sidebarLabel: {
    fontSize: '9px', fontWeight: '700', letterSpacing: '1.5px',
    textTransform: 'uppercase', color: 'rgba(255,255,255,0.3)',
    padding: '10px 4px 6px', display: 'block',
  },
  sessionItem: {
    padding: '8px 10px', borderRadius: '5px', marginBottom: '2px',
    cursor: 'pointer', display: 'flex', alignItems: 'flex-start',
    gap: '8px', transition: 'background 0.15s',
  },
  sessionItemActive: { backgroundColor: COLORS.sidebarActive },
  sessionItemInactive: { backgroundColor: 'transparent' },
  sessionIcon: { marginTop: '1px', flexShrink: 0 },
  sessionTitle: { fontSize: '12px', fontWeight: '500', color: '#E2E8F0', lineHeight: '1.3', marginBottom: '2px' },
  sessionTime: { fontSize: '10px', color: 'rgba(255,255,255,0.35)' },
  statRow: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '6px 10px', borderRadius: '5px', marginBottom: '3px',
    cursor: 'pointer', transition: 'background 0.15s',
  },
  statLabel: { fontSize: '12px', color: COLORS.sidebarText },
  statBadge: { fontSize: '11px', fontWeight: '700', padding: '1px 7px', borderRadius: '3px' },
  recentAlert: {
    padding: '7px 10px', borderRadius: '5px', marginBottom: '3px',
    borderLeft: `2px solid ${COLORS.accent}`, cursor: 'pointer',
    backgroundColor: 'rgba(255,255,255,0.04)', transition: 'background 0.15s',
  },
  recentAlertType: { fontSize: '11px', fontWeight: '700', color: COLORS.accent, textTransform: 'uppercase', letterSpacing: '0.5px' },
  recentAlertIp: { fontSize: '10px', color: 'rgba(255,255,255,0.4)', fontFamily: 'monospace', marginTop: '1px' },

  // MAIN CHAT AREA
  chatArea: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' },
  chatToolbar: {
    padding: '10px 20px', borderBottom: `1px solid ${COLORS.border}`,
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    backgroundColor: COLORS.surface, flexShrink: 0,
  },
  toolbarLeft: { display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: '600', color: COLORS.textSecondary },
  sessionName: { fontSize: '13px', color: COLORS.text, fontWeight: '600' },
  clearBtn: {
    display: 'flex', alignItems: 'center', gap: '5px', padding: '5px 11px',
    borderRadius: '4px', border: `1px solid ${COLORS.border}`, backgroundColor: COLORS.surface,
    color: COLORS.textSecondary, fontSize: '12px', cursor: 'pointer', fontWeight: '500',
  },
  messages: { flex: 1, overflow: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' },
  userBubble: {
    maxWidth: '75%', padding: '10px 14px', borderRadius: '8px', fontSize: '14px',
    lineHeight: '1.5', backgroundColor: COLORS.accentSecondary, color: '#fff',
    alignSelf: 'flex-end', borderBottomRightRadius: '3px',
  },
  assistantBubble: {
    maxWidth: '92%', padding: '12px 16px', borderRadius: '8px', fontSize: '14px',
    lineHeight: '1.5', backgroundColor: COLORS.surface, border: `1px solid ${COLORS.border}`,
    alignSelf: 'flex-start', borderBottomLeftRadius: '3px',
  },
  intentBadge: {
    display: 'inline-block', fontSize: '10px', fontWeight: '700', padding: '2px 8px',
    borderRadius: '3px', backgroundColor: COLORS.infoLight, color: COLORS.info,
    marginBottom: '8px', letterSpacing: '0.5px', textTransform: 'uppercase',
  },
  explanationBox: {
    backgroundColor: COLORS.accentLight, border: `1px solid #FECACA`,
    borderLeft: `3px solid ${COLORS.accent}`, borderRadius: '4px',
    padding: '9px 12px', fontSize: '13px', color: '#991B1B',
    marginTop: '10px', display: 'flex', gap: '8px', alignItems: 'flex-start',
  },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '12px', marginTop: '10px', fontFamily: 'monospace' },
  th: {
    backgroundColor: COLORS.accentSecondary, color: '#fff', padding: '7px 10px',
    textAlign: 'left', fontSize: '10px', fontWeight: '700', letterSpacing: '0.5px', textTransform: 'uppercase',
  },
  td: { padding: '6px 10px', borderBottom: `1px solid ${COLORS.border}`, color: COLORS.textSecondary, maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' },
  inputArea: {
    padding: '14px 20px', borderTop: `1px solid ${COLORS.border}`,
    backgroundColor: COLORS.surface, display: 'flex', gap: '10px', alignItems: 'center', flexShrink: 0,
  },
  input: {
    flex: 1, padding: '10px 16px', borderRadius: '6px', border: `1px solid ${COLORS.borderStrong}`,
    fontSize: '14px', outline: 'none', color: COLORS.text, backgroundColor: COLORS.bg, fontFamily: 'inherit',
  },
  sendBtn: {
    padding: '10px 18px', borderRadius: '6px', border: 'none', backgroundColor: COLORS.accentSecondary,
    color: '#fff', fontSize: '14px', fontWeight: '600', cursor: 'pointer',
    display: 'flex', alignItems: 'center', gap: '6px',
  },
  chips: { display: 'flex', gap: '7px', flexWrap: 'wrap', padding: '0 20px 10px', backgroundColor: COLORS.surface },
  chip: {
    padding: '4px 11px', borderRadius: '20px', border: `1px solid ${COLORS.border}`,
    fontSize: '11px', color: COLORS.textSecondary, cursor: 'pointer', backgroundColor: COLORS.bg, fontWeight: '500',
  },
  loading: { display: 'flex', gap: '4px', alignItems: 'center', padding: '10px 14px' },
  dot: { width: '6px', height: '6px', borderRadius: '50%', backgroundColor: COLORS.textMuted, animation: 'bounce 1.4s infinite ease-in-out' },
  countResult: { fontSize: '28px', fontWeight: '800', color: COLORS.accent, marginTop: '8px' },
  countLabel: { fontSize: '13px', color: COLORS.textSecondary, marginTop: '4px' },
};

const SUGGESTIONS = [
  "Show me XSS attempts this week",
  "Any IDOR attacks yesterday?",
  "Did any AI attacks bypass WAF today?",
  "Generate weekly attack report",
  "How many SQLi attacks this week?",
];

function generateSessionId() {
  return 'session-' + Math.random().toString(36).substr(2, 9);
}

function generateSessionTitle(messages) {
  const firstUserMsg = messages.find(m => m.role === 'user');
  if (firstUserMsg) {
    return firstUserMsg.text.length > 32
      ? firstUserMsg.text.substring(0, 32) + '...'
      : firstUserMsg.text;
  }
  return 'New Investigation';
}

function formatTime(iso) {
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now - d;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}

function AlertTable({ alerts }) {
  if (!alerts || alerts.length === 0)
    return <p style={{ color: COLORS.textMuted, fontSize: '13px', marginTop: '8px' }}>No alerts found.</p>;
  return (
    <table style={styles.table}>
      <thead>
        <tr>
          {['Time', 'Type', 'Source IP', 'URL', 'Status'].map(h => (
            <th key={h} style={styles.th}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {alerts.map((alert, i) => (
          <tr key={i} style={{ backgroundColor: i % 2 === 0 ? COLORS.bg : COLORS.surface }}>
            <td style={styles.td}>{alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : '-'}</td>
            <td style={{ ...styles.td, color: COLORS.accent, fontWeight: '700' }}>{alert.attack_type?.toUpperCase() || '-'}</td>
            <td style={styles.td}>{alert.source_ip || '-'}</td>
            <td style={styles.td} title={alert.url}>{alert.url || '-'}</td>
            <td style={styles.td}>{alert.status_code || '-'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ReportChart({ data }) {
  if (!data || data.length === 0) return null;
  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
        <XAxis dataKey="type" tick={{ fontSize: 10, fill: COLORS.textSecondary }} />
        <YAxis tick={{ fontSize: 10, fill: COLORS.textSecondary }} />
        <Tooltip contentStyle={{ backgroundColor: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: '6px', fontSize: '12px' }} />
        <Bar dataKey="count" fill={COLORS.accentSecondary} radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function MessageContent({ msg }) {
  if (msg.role === 'user') return <span>{msg.text}</span>;
  const { data } = msg;
  if (!data) return <span style={{ color: COLORS.textSecondary }}>{msg.text}</span>;

  if (data.type === 'clarification') {
    return (
      <div>
        <div style={styles.intentBadge}>Clarification Needed</div>
        <p style={{ margin: 0, color: COLORS.textSecondary }}>{data.explanation}</p>
      </div>
    );
  }

  if (data.type === 'count') {
    const result = data.result || {};
    return (
      <div>
        <div style={styles.intentBadge}>{data.intent?.replace(/_/g, ' ')}</div>
        <div style={styles.countResult}>{result.total || 0}</div>
        <div style={styles.countLabel}>Total alerts found</div>
        {result.breakdown?.length > 0 && <ReportChart data={result.breakdown} />}
        <div style={styles.explanationBox}>
          <AlertTriangle size={13} style={{ marginTop: '1px', flexShrink: 0 }} />
          <span>{data.explanation}</span>
        </div>
      </div>
    );
  }

  if (data.type === 'report') {
    const result = data.result || {};
    return (
      <div>
        <div style={styles.intentBadge}>Security Report</div>
        <p style={{ margin: '0 0 8px', fontSize: '13px', color: COLORS.textSecondary }}>
          Total: <strong>{result.total || 0}</strong> alerts
        </p>
        {result.by_attack_type?.length > 0 && (
          <>
            <p style={{ margin: '0 0 5px', fontSize: '11px', color: COLORS.textMuted, fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.5px' }}>By Attack Type</p>
            <ReportChart data={result.by_attack_type} />
          </>
        )}
        {result.raw_alerts?.length > 0 && (
          <AlertTable alerts={result.raw_alerts.map(a => ({
            timestamp: a['@timestamp'], attack_type: a.rule?.type,
            source_ip: a.source_ip, url: a.url, status_code: a.status_code,
          }))} />
        )}
        <div style={styles.explanationBox}>
          <AlertTriangle size={13} style={{ marginTop: '1px', flexShrink: 0 }} />
          <span>{data.explanation}</span>
        </div>
      </div>
    );
  }

  const result = data.result || {};
  return (
    <div>
      <div style={styles.intentBadge}>{data.intent?.replace(/_/g, ' ')}</div>
      <AlertTable alerts={result.alerts || []} />
      <div style={styles.explanationBox}>
        <AlertTriangle size={13} style={{ marginTop: '1px', flexShrink: 0 }} />
        <span>{data.explanation}</span>
      </div>
    </div>
  );
}

export default function App() {
  const STORAGE_KEY = 'siem_sessions';

  const loadSessions = () => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch { return []; }
  };

  const saveSessions = (sessions) => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions)); } catch {}
  };

  const createNewSession = () => ({
    id: generateSessionId(),
    title: 'New Investigation',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    messages: [{
      role: 'assistant',
      text: 'Investigation console ready. Ask me anything about your security alerts.',
      data: null,
    }]
  });

  const [sessions, setSessions] = useState(() => {
    const saved = loadSessions();
    if (saved.length === 0) {
      const first = createNewSession();
      return [first];
    }
    return saved;
  });

  const [activeSessionId, setActiveSessionId] = useState(() => {
    const saved = loadSessions();
    return saved.length > 0 ? saved[0].id : sessions[0]?.id;
  });

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [alertStats, setAlertStats] = useState({ XSS: 0, IDOR: 0, Total: 0 });
  const messagesEndRef = useRef(null);

  const activeSession = sessions.find(s => s.id === activeSessionId) || sessions[0];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeSession?.messages]);

  useEffect(() => {
    saveSessions(sessions);
  }, [sessions]);

  useEffect(() => {
    fetchRecentAlerts();
    const interval = setInterval(fetchRecentAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchRecentAlerts = async () => {
    try {
      const res = await axios.get(`${API}/alerts/recent`);
      const alerts = res.data.alerts || [];
      setRecentAlerts(alerts.slice(0, 6));
      const xss = alerts.filter(a => a.attack_type?.toLowerCase().includes('xss')).length;
      const idor = alerts.filter(a => a.attack_type?.toLowerCase() === 'idor').length;
      setAlertStats({ XSS: xss, IDOR: idor, Total: alerts.length });
    } catch {}
  };

  const updateSession = (sessionId, updates) => {
    setSessions(prev => prev.map(s =>
      s.id === sessionId ? { ...s, ...updates, updatedAt: new Date().toISOString() } : s
    ));
  };

  const sendMessage = async (text) => {
    const query = text || input;
    if (!query.trim() || loading) return;

    const newUserMsg = { role: 'user', text: query, data: null };
    const updatedMessages = [...(activeSession.messages || []), newUserMsg];

    updateSession(activeSessionId, {
      messages: updatedMessages,
      title: activeSession.title === 'New Investigation'
        ? generateSessionTitle(updatedMessages)
        : activeSession.title
    });

    setInput('');
    setLoading(true);

    try {
      const res = await axios.post(`${API}/query`, {
        text: query,
        session_id: activeSessionId,
      });

      const assistantMsg = {
        role: 'assistant',
        text: res.data.explanation || 'Done.',
        data: res.data,
      };

      setSessions(prev => prev.map(s =>
        s.id === activeSessionId
          ? { ...s, messages: [...(s.messages || []), newUserMsg, assistantMsg], updatedAt: new Date().toISOString() }
          : s
      ));

      // Fix: remove the duplicate user message we added optimistically
      setSessions(prev => prev.map(s => {
        if (s.id !== activeSessionId) return s;
        const msgs = s.messages;
        const withoutDupe = msgs.filter((m, i) => !(m.role === 'user' && m.text === query && i < msgs.length - 2));
        return { ...s, messages: withoutDupe };
      }));

      fetchRecentAlerts();
    } catch {
      setSessions(prev => prev.map(s =>
        s.id === activeSessionId
          ? {
            ...s,
            messages: [...(s.messages || []), {
              role: 'assistant',
              text: 'Error connecting to SIEM backend.',
              data: null,
            }],
          }
          : s
      ));
    }
    setLoading(false);
  };

  const startNewSession = async () => {
    const newSession = createNewSession();
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newSession.id);
    try { await axios.post(`${API}/clear`, { session_id: newSession.id }); } catch {}
  };

  const clearCurrentSession = async () => {
    try { await axios.post(`${API}/clear`, { session_id: activeSessionId }); } catch {}
    updateSession(activeSessionId, {
      messages: [{
        role: 'assistant',
        text: 'Session cleared. Ready for new investigation.',
        data: null,
      }],
      title: 'New Investigation',
    });
  };

  const messages = activeSession?.messages || [];

  return (
    <div style={styles.app}>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        @keyframes bounce { 0%,80%,100%{transform:scale(0)} 40%{transform:scale(1)} }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
        input:focus { border-color: #1D3557 !important; box-shadow: 0 0 0 3px rgba(29,53,87,0.1); }
        .session-hover:hover { background-color: rgba(255,255,255,0.07) !important; }
        .stat-hover:hover { background-color: rgba(255,255,255,0.07) !important; }
        .recent-hover:hover { background-color: rgba(255,255,255,0.08) !important; }
      `}</style>

      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <Shield size={18} color={COLORS.accent} />
          <div>
            <p style={styles.headerTitle}>SIEM ASSISTANT</p>
            <p style={styles.headerSubtitle}>Security Investigation Platform</p>
          </div>
        </div>
        <div style={styles.liveBadge}>
          <div style={styles.liveDot} />
          LIVE
        </div>
      </div>

      <div style={styles.body}>
        {/* LEFT SIDEBAR */}
        <div style={styles.sidebar}>

          {/* New Investigation Button */}
          <button style={styles.newInvestigationBtn} onClick={startNewSession}>
            <Plus size={13} />
            New Investigation
          </button>

          {/* Session History */}
          <div style={{ ...styles.sidebarSection, flex: sessions.length > 3 ? '0 0 auto' : undefined, maxHeight: '220px', overflowY: 'auto' }}>
            <span style={styles.sidebarLabel}>Investigation History</span>
            {sessions.map(session => (
              <div
                key={session.id}
                className="session-hover"
                style={{
                  ...styles.sessionItem,
                  ...(session.id === activeSessionId ? styles.sessionItemActive : styles.sessionItemInactive)
                }}
                onClick={() => setActiveSessionId(session.id)}
              >
                <Clock size={11} color="rgba(255,255,255,0.4)" style={styles.sessionIcon} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={styles.sessionTitle} title={session.title}>
                    {session.title.length > 28 ? session.title.substring(0, 28) + '...' : session.title}
                  </div>
                  <div style={styles.sessionTime}>{formatTime(session.updatedAt)}</div>
                </div>
                {session.id === activeSessionId && (
                  <ChevronRight size={11} color="rgba(255,255,255,0.4)" />
                )}
              </div>
            ))}
          </div>

          {/* Alert Summary */}
          <div style={styles.sidebarSection}>
            <span style={styles.sidebarLabel}>Alert Summary</span>
            {[
              { label: 'XSS Attacks', count: alertStats.XSS, color: COLORS.accent, query: 'Show me XSS attempts this week' },
              { label: 'IDOR Attempts', count: alertStats.IDOR, color: COLORS.warning, query: 'Show me IDOR attempts this week' },
              { label: 'Total Alerts', count: alertStats.Total, color: COLORS.info, query: 'Show me all alerts this week' },
            ].map(stat => (
              <div
                key={stat.label}
                className="stat-hover"
                style={styles.statRow}
                onClick={() => sendMessage(stat.query)}
                title={`Investigate ${stat.label}`}
              >
                <span style={styles.statLabel}>{stat.label}</span>
                <span style={{ ...styles.statBadge, backgroundColor: stat.color + '22', color: stat.color }}>
                  {stat.count}
                </span>
              </div>
            ))}
          </div>

          {/* Recent Detections */}
          <div style={{ ...styles.sidebarSection, flex: 1, overflowY: 'auto' }}>
            <span style={styles.sidebarLabel}>Recent Detections</span>
            {recentAlerts.length === 0 ? (
              <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.25)', padding: '4px' }}>No recent alerts</p>
            ) : (
              recentAlerts.map((alert, i) => (
                <div
                  key={i}
                  className="recent-hover"
                  style={styles.recentAlert}
                  onClick={() => sendMessage(`Show details for ${alert.attack_type} from ${alert.source_ip}`)}
                >
                  <div style={styles.recentAlertType}>{alert.attack_type}</div>
                  <div style={styles.recentAlertIp}>{alert.source_ip}</div>
                </div>
              ))
            )}
          </div>

        </div>

        {/* MAIN CHAT AREA */}
        <div style={styles.chatArea}>
          <div style={styles.chatToolbar}>
            <div style={styles.toolbarLeft}>
              <Search size={13} />
              <span style={styles.sessionName}>{activeSession?.title || 'Investigation Console'}</span>
            </div>
            <button style={styles.clearBtn} onClick={clearCurrentSession}>
              <Trash2 size={11} />
              Clear
            </button>
          </div>

          <div style={styles.messages}>
            {messages.map((msg, i) => (
              <div key={i} style={msg.role === 'user' ? styles.userBubble : styles.assistantBubble}>
                <MessageContent msg={msg} />
              </div>
            ))}
            {loading && (
              <div style={styles.assistantBubble}>
                <div style={styles.loading}>
                  {[0, 1, 2].map(i => (
                    <div key={i} style={{ ...styles.dot, animationDelay: `${i * 0.16}s` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div style={styles.chips}>
            {SUGGESTIONS.map((s, i) => (
              <button key={i} style={styles.chip} onClick={() => sendMessage(s)}>{s}</button>
            ))}
          </div>

          <div style={styles.inputArea}>
            <input
              style={styles.input}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about security alerts..."
            />
            <button style={styles.sendBtn} onClick={() => sendMessage()}>
              <Send size={13} />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
