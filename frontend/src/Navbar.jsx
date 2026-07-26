import React, { useEffect, useState } from "react";

const TABS = [
  { id: "dashboard", label: "Dashboard" },
  { id: "units", label: "Fleet" },
  { id: "analytics", label: "Analytics" },
];

export default function Navbar({ active, onChange, connected, activeCount }) {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <header className="navbar">
      <div className="navbar-brand">
        <span className="radar-pulse" aria-hidden="true">
          <span className="radar-sweep" />
        </span>
        <div>
          <div className="brand-title">IERCS</div>
          <div className="brand-sub">Emergency Response Coordination</div>
        </div>
      </div>

      <nav className="navbar-tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`navbar-tab ${active === t.id ? "is-active" : ""}`}
            onClick={() => onChange(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <div className="navbar-status">
        <div className="status-chip">
          <span className={`dot ${connected ? "dot-live" : "dot-dead"}`} />
          {connected ? "Live" : "Reconnecting"}
        </div>
        <div className="status-chip">
          {activeCount} active
        </div>
        <div className="status-clock mono">
          {now.toLocaleTimeString([], { hour12: false })}
        </div>
      </div>

      <style>{`
        .navbar {
          display: grid;
          grid-template-columns: auto 1fr auto;
          align-items: center;
          gap: 24px;
          padding: 14px 24px;
          background: var(--panel);
          border-bottom: 1px solid var(--line);
        }
        .navbar-brand { display: flex; align-items: center; gap: 12px; }
        .brand-title {
          font-family: var(--font-display);
          font-weight: 700;
          font-size: 18px;
          letter-spacing: 0.04em;
        }
        .brand-sub { font-size: 11px; color: var(--text-muted); margin-top: 1px; }

        .radar-pulse {
          position: relative;
          width: 30px; height: 30px;
          border-radius: 50%;
          border: 1px solid var(--line);
          background: radial-gradient(circle at center, var(--moderate-bg), transparent 70%);
          overflow: hidden;
          flex-shrink: 0;
        }
        .radar-sweep {
          position: absolute;
          inset: 0;
          background: conic-gradient(from 0deg, var(--signal) 0deg, transparent 60deg);
          animation: sweep 2.4s linear infinite;
          border-radius: 50%;
        }
        @keyframes sweep { to { transform: rotate(360deg); } }

        .navbar-tabs { display: flex; gap: 4px; justify-self: center; }
        .navbar-tab {
          background: transparent;
          border: 1px solid transparent;
          color: var(--text-muted);
          font-family: var(--font-display);
          font-size: 13px;
          font-weight: 500;
          padding: 8px 16px;
          border-radius: var(--radius-sm);
          transition: color 0.15s ease, background 0.15s ease;
        }
        .navbar-tab:hover { color: var(--text-primary); background: var(--panel-hover); }
        .navbar-tab.is-active {
          color: var(--void);
          background: var(--signal);
        }

        .navbar-status { display: flex; align-items: center; gap: 10px; }
        .status-chip {
          display: flex; align-items: center; gap: 6px;
          font-size: 12px; color: var(--text-muted);
          background: var(--panel-raised);
          border: 1px solid var(--line);
          padding: 5px 10px;
          border-radius: 999px;
        }
        .dot { width: 7px; height: 7px; border-radius: 50%; }
        .dot-live { background: var(--low); box-shadow: 0 0 0 3px var(--low-bg); }
        .dot-dead { background: var(--critical); box-shadow: 0 0 0 3px var(--critical-bg); }
        .status-clock {
          font-size: 13px;
          color: var(--text-primary);
          background: var(--panel-raised);
          border: 1px solid var(--line);
          padding: 6px 10px;
          border-radius: var(--radius-sm);
        }
      `}</style>
    </header>
  );
}
