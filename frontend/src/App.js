import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Shield, Send, Trash2, AlertTriangle, Activity, Search } from 'lucide-react';

const API = 'http://localhost:8000';
const SESSION_ID = 'siem-session-' + Math.random().toString(36).substr(2, 9);

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
};

const styles = {
  app: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    backgroundColor: COLORS.bg,
    minHeight: '100vh',
    color: COLORS.text,
  },
  header: {
    backgroundColor: COLORS.accentSecondary,
    color: '#FFFFFF',
    padding: '0 24px',
    height: '56px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottom: `3px solid ${COLORS.accent}`,
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  headerTitle: {
    fontSize: '16px',
    fontWeight: '700',
    letterSpacing: '0.5px',
    margin: 0,
  },
  headerSubtitle: {
    fontSize: '11px',
    opacity: 0.7,
    margin: 0,
    letterSpacing: '1px',
    textTransform: 'uppercase',
  },
  liveBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    backgroundColor: 'rgba(255,255,255,0.1)',
    padding: '4px 10px',
    borderRadius: '4px',
    fontSize: '12px',
    border: '1px solid rgba(255,255,255,0.2)',
  },
  liveDot: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
    backgroundColor: '#4ADE80',
    animation: 'pulse 2s infinite',
  },
  main: {
    display: 'grid',
    gridTemplateColumns: '280px 1fr',
    height: 'calc(100vh - 56px)',
  },
  sidebar: {
    backgroundColor: COLORS.surface,
    borderRight: `1px solid ${COLORS.border}`,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  },
  sidebarSection: {
    padding: '16px',
    borderBottom: `1px solid ${COLORS.border}`,
  },
  sidebarTitle: {
    fontSize: '10px',
    fontWeight: '700',
    letterSpacing: '1.5px',
    textTransform: 'uppercase',
    color: COLORS.textMuted,
    marginBottom: '12px',
  },
  statCard: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 12px',
    borderRadius: '6px',
    marginBottom: '6px',
    border: `1px solid ${COLORS.border}`,
  },
  statLabel: {
    fontSize: '13px',
    fontWeight: '500',
    color: COLORS.textSecondary,
  },
  statBadge: {
    fontSize: '12px',
    fontWeight: '700',
    padding: '2px 8px',
    borderRadius: '4px',
  },
  alertItem: {
    padding: '10px 12px',
    borderRadius: '6px',
    marginBottom: '6px',
    border: `1px solid ${COLORS.border}`,
    borderLeft: `3px solid ${COLORS.accent}`,
    cursor: 'pointer',
  },
  alertItemType: {
    fontSize: '12px',
    fontWeight: '700',
    color: COLORS.accent,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  alertItemIp: {
    fontSize: '11px',
    color: COLORS.textMuted,
    fontFamily: 'monospace',
    marginTop: '2px',
  },
  alertItemTime: {
    fontSize: '10px',
    color: COLORS.textMuted,
    marginTop: '2px',
  },
  chatArea: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    overflow: 'hidden',
  },
  chatToolbar: {
    padding: '12px 20px',
    borderBottom: `1px solid ${COLORS.border}`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: COLORS.surface,
  },
  toolbarTitle: {
    fontSize: '13px',
    fontWeight: '600',
    color: COLORS.textSecondary,
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  clearBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '6px 12px',
    borderRadius: '4px',
    border: `1px solid ${COLORS.border}`,
    backgroundColor: COLORS.surface,
    color: COLORS.textSecondary,
    fontSize: '12px',
    cursor: 'pointer',
    fontWeight: '500',
  },
  messages: {
    flex: 1,
    overflow: 'auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  messageBubble: {
    maxWidth: '85%',
    padding: '12px 16px',
    borderRadius: '8px',
    fontSize: '14px',
    lineHeight: '1.5',
  },
  userMessage: {
    backgroundColor: COLORS.accentSecondary,
    color: '#FFFFFF',
    alignSelf: 'flex-end',
    borderBottomRightRadius: '2px',
  },
  assistantMessage: {
    backgroundColor: COLORS.surface,
    border: `1px solid ${COLORS.border}`,
    alignSelf: 'flex-start',
    borderBottomLeftRadius: '2px',
    maxWidth: '90%',
  },
  intentBadge: {
    display: 'inline-block',
    fontSize: '10px',
    fontWeight: '700',
    padding: '2px 8px',
    borderRadius: '3px',
    backgroundColor: COLORS.infoLight,
    color: COLORS.info,
    marginBottom: '8px',
    letterSpacing: '0.5px',
    textTransform: 'uppercase',
  },
  explanationBox: {
    backgroundColor: COLORS.accentLight,
    border: `1px solid #FECACA`,
    borderLeft: `3px solid ${COLORS.accent}`,
    borderRadius: '4px',
    padding: '10px 12px',
    fontSize: '13px',
    color: '#991B1B',
    marginTop: '10px',
    display: 'flex',
    gap: '8px',
    alignItems: 'flex-start',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '12px',
    marginTop: '10px',
    fontFamily: 'monospace',
  },
  th: {
    backgroundColor: COLORS.accentSecondary,
    color: '#FFFFFF',
    padding: '8px 10px',
    textAlign: 'left',
    fontSize: '11px',
    fontWeight: '700',
    letterSpacing: '0.5px',
    textTransform: 'uppercase',
  },
  td: {
    padding: '7px 10px',
    borderBottom: `1px solid ${COLORS.border}`,
    color: COLORS.textSecondary,
    maxWidth: '200px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  trEven: { backgroundColor: COLORS.bg },
  trOdd: { backgroundColor: COLORS.surface },
  inputArea: {
    padding: '16px 20px',
    borderTop: `1px solid ${COLORS.border}`,
    backgroundColor: COLORS.surface,
    display: 'flex',
    gap: '10px',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    padding: '10px 16px',
    borderRadius: '6px',
    border: `1px solid ${COLORS.borderStrong}`,
    fontSize: '14px',
    outline: 'none',
    color: COLORS.text,
    backgroundColor: COLORS.bg,
    fontFamily: 'inherit',
  },
  sendBtn: {
    padding: '10px 20px',
    borderRadius: '6px',
    border: 'none',
    backgroundColor: COLORS.accentSecondary,
    color: '#FFFFFF',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  suggestionChips: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
    padding: '0 20px 12px',
    backgroundColor: COLORS.surface,
  },
  chip: {
    padding: '5px 12px',
    borderRadius: '20px',
    border: `1px solid ${COLORS.border}`,
    fontSize: '12px',
    color: COLORS.textSecondary,
    cursor: 'pointer',
    backgroundColor: COLORS.bg,
    fontWeight: '500',
  },
  loading: {
    display: 'flex',
    gap: '4px',
    alignItems: 'center',
    padding: '12px 16px',
  },
  dot: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
    backgroundColor: COLORS.textMuted,
    animation: 'bounce 1.4s infinite ease-in-out',
  },
  countResult: {
    fontSize: '28px',
    fontWeight: '800',
    color: COLORS.accent,
    marginTop: '8px',
  },
  countLabel: {
    fontSize: '13px',
    color: COLORS.textSecondary,
    marginTop: '4px',
  },
};

const SUGGESTIONS = [
  "Show me XSS attempts today",
  "Any IDOR attacks yesterday?",
  "Generate weekly attack report",
  "How many attacks this week?",
  "Filter by IP 172.18.0.1",
];

function AlertTable({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return <p style={{ color: COLORS.textMuted, fontSize: '13px', marginTop: '8px' }}>No alerts found.</p>;
  }
  return (
    <table style={styles.table}>
      <thead>
        <tr>
          <th style={styles.th}>Time</th>
          <th style={styles.th}>Type</th>
          <th style={styles.th}>Source IP</th>
          <th style={styles.th}>URL</th>
          <th style={styles.th}>Status</th>
        </tr>
      </thead>
      <tbody>
        {alerts.map((alert, i) => (
          <tr key={i} style={i % 2 === 0 ? styles.trEven : styles.trOdd}>
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
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
        <XAxis dataKey="type" tick={{ fontSize: 11, fill: COLORS.textSecondary }} />
        <YAxis tick={{ fontSize: 11, fill: COLORS.textSecondary }} />
        <Tooltip
          contentStyle={{
            backgroundColor: COLORS.surface,
            border: `1px solid ${COLORS.border}`,
            borderRadius: '6px',
            fontSize: '12px',
          }}
        />
        <Bar dataKey="count" fill={COLORS.accentSecondary} radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function MessageContent({ msg }) {
  if (msg.role === 'user') {
    return <span>{msg.text}</span>;
  }

  const { data } = msg;
  if (!data) return <span>{msg.text}</span>;

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
        {result.breakdown && result.breakdown.length > 0 && (
          <ReportChart data={result.breakdown} />
        )}
        <div style={styles.explanationBox}>
          <AlertTriangle size={14} style={{ marginTop: '1px', flexShrink: 0 }} />
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
        <p style={{ margin: '0 0 10px', fontSize: '13px', color: COLORS.textSecondary }}>
          Total: <strong>{result.total || 0}</strong> alerts
        </p>
        {result.by_attack_type && result.by_attack_type.length > 0 && (
          <>
            <p style={{ margin: '0 0 6px', fontSize: '12px', color: COLORS.textMuted, fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px' }}>By Attack Type</p>
            <ReportChart data={result.by_attack_type} />
          </>
        )}
        {result.raw_alerts && result.raw_alerts.length > 0 && (
          <AlertTable alerts={result.raw_alerts.map(a => ({
            timestamp: a['@timestamp'],
            attack_type: a.rule?.type,
            source_ip: a.source_ip,
            url: a.url,
            status_code: a.status_code,
          }))} />
        )}
        <div style={styles.explanationBox}>
          <AlertTriangle size={14} style={{ marginTop: '1px', flexShrink: 0 }} />
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
        <AlertTriangle size={14} style={{ marginTop: '1px', flexShrink: 0 }} />
        <span>{data.explanation}</span>
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'SIEM Assistant online. I can investigate security alerts, detect web attacks, and generate reports. What would you like to investigate?',
      data: null,
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [alertStats, setAlertStats] = useState({ XSS: 0, IDOR: 0, Total: 0 });
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    fetchRecentAlerts();
    const interval = setInterval(fetchRecentAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchRecentAlerts = async () => {
    try {
      const res = await axios.get(`${API}/alerts/recent`);
      const alerts = res.data.alerts || [];
      setRecentAlerts(alerts.slice(0, 8));
      const xss = alerts.filter(a => a.attack_type?.toLowerCase() === 'xss').length;
      const idor = alerts.filter(a => a.attack_type?.toLowerCase() === 'idor').length;
      setAlertStats({ XSS: xss, IDOR: idor, Total: alerts.length });
    } catch (e) {}
  };

  const sendMessage = async (text) => {
    const query = text || input;
    if (!query.trim()) return;

    setMessages(prev => [...prev, { role: 'user', text: query, data: null }]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post(`${API}/query`, {
        text: query,
        session_id: SESSION_ID,
      });
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: res.data.explanation || 'Done.',
        data: res.data,
      }]);
      fetchRecentAlerts();
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: 'Error connecting to SIEM backend. Please check if the API is running.',
        data: null,
      }]);
    }
    setLoading(false);
  };

  const clearSession = async () => {
    try {
      await axios.post(`${API}/clear`, { session_id: SESSION_ID });
    } catch (e) {}
    setMessages([{
      role: 'assistant',
      text: 'Session cleared. Context memory reset. Ready for new investigation.',
      data: null,
    }]);
  };

  return (
    <div style={styles.app}>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        @keyframes bounce {
          0%,80%,100%{transform:scale(0)} 40%{transform:scale(1)}
        }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
        input:focus { border-color: #1D3557 !important; box-shadow: 0 0 0 3px rgba(29,53,87,0.1); }
      `}</style>

      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <Shield size={20} color={COLORS.accent} />
          <div>
            <p style={styles.headerTitle}>SIEM ASSISTANT</p>
            <p style={styles.headerSubtitle}>Security Investigation Platform</p>
          </div>
        </div>
        <div style={styles.liveBadge}>
          <div style={styles.liveDot} />
          LIVE MONITORING
        </div>
      </div>

      <div style={styles.main}>
        {/* Sidebar */}
        <div style={styles.sidebar}>
          <div style={styles.sidebarSection}>
            <p style={styles.sidebarTitle}>Alert Summary</p>
            {[
  { label: 'XSS Attacks', count: alertStats.XSS, color: COLORS.accent, query: 'Show me XSS attempts this week' },
  { label: 'IDOR Attempts', count: alertStats.IDOR, color: COLORS.warning, query: 'Show me IDOR attempts this week' },
  { label: 'Total Alerts', count: alertStats.Total, color: COLORS.info, query: 'Show me all alerts this week' },
].map(stat => (
  <div
    key={stat.label}
    style={{ ...styles.statCard, cursor: 'pointer', transition: 'all 0.15s' }}
    onClick={() => sendMessage(stat.query)}
    onMouseEnter={e => e.currentTarget.style.borderColor = stat.color}
    onMouseLeave={e => e.currentTarget.style.borderColor = COLORS.border}
    title={`Click to investigate ${stat.label}`}
  >
    <span style={styles.statLabel}>{stat.label}</span>
    <span style={{ ...styles.statBadge, backgroundColor: stat.color + '15', color: stat.color }}>
      {stat.count}
    </span>
  </div>
))}
          </div>

          <div style={{ ...styles.sidebarSection, flex: 1, overflow: 'auto' }}>
            <p style={styles.sidebarTitle}>Recent Detections</p>
            {recentAlerts.length === 0 ? (
              <p style={{ fontSize: '12px', color: COLORS.textMuted }}>No recent alerts</p>
            ) : (
              recentAlerts.map((alert, i) => (
                <div
                  key={i}
                  style={styles.alertItem}
                  onClick={() => sendMessage(`Show details for ${alert.attack_type} attack from ${alert.source_ip}`)}
                >
                  <div style={styles.alertItemType}>{alert.attack_type}</div>
                  <div style={styles.alertItemIp}>{alert.source_ip}</div>
                  <div style={styles.alertItemTime}>
                    {alert.timestamp ? new Date(alert.timestamp).toLocaleString() : ''}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div style={styles.chatArea}>
          <div style={styles.chatToolbar}>
            <span style={styles.toolbarTitle}>
              <Search size={14} />
              Investigation Console
            </span>
            <button style={styles.clearBtn} onClick={clearSession}>
              <Trash2 size={12} />
              Clear Session
            </button>
          </div>

          <div style={styles.messages}>
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  ...styles.messageBubble,
                  ...(msg.role === 'user' ? styles.userMessage : styles.assistantMessage),
                }}
              >
                <MessageContent msg={msg} />
              </div>
            ))}
            {loading && (
              <div style={{ ...styles.assistantMessage, ...styles.messageBubble }}>
                <div style={styles.loading}>
                  {[0, 1, 2].map(i => (
                    <div key={i} style={{ ...styles.dot, animationDelay: `${i * 0.16}s` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div style={styles.suggestionChips}>
            {SUGGESTIONS.map((s, i) => (
              <button key={i} style={styles.chip} onClick={() => sendMessage(s)}>
                {s}
              </button>
            ))}
          </div>

          <div style={styles.inputArea}>
            <input
              style={styles.input}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about security alerts... (e.g. Show me XSS attempts today)"
            />
            <button style={styles.sendBtn} onClick={() => sendMessage()}>
              <Send size={14} />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
