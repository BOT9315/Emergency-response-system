import React from "react";
import { SEVERITY_COLOR, TYPE_LABEL, STATUS_LABEL, timeAgo } from "../utils.js";

export default function IncidentFeed({ incidents, selectedId, onSelect, onDispatch, dispatchingId }) {
  return (
    <div className="feed">
      <div className="feed-head">
        <span>Incident Queue</span>
        <span className="feed-count mono">{incidents.length}</span>
      </div>
      <div className="feed-list">
        {incidents.length === 0 && (
          <div className="feed-empty">No incidents reported yet. The queue is clear.</div>
        )}
        {incidents.map((inc) => (
          <button
            key={inc.id}
            className={`feed-card ${selectedId === inc.id ? "is-selected" : ""}`}
            style={{ "--sev-color": SEVERITY_COLOR[inc.severity] || "var(--text-muted)" }}
            onClick={() => onSelect(inc.id)}
          >
            <div className="feed-card-bar" />
            <div className="feed-card-body">
              <div className="feed-card-row">
                <span className="feed-type">{TYPE_LABEL[inc.incident_type] || inc.incident_type}</span>
                <span className="feed-priority mono">{inc.priority_score.toFixed(0)}</span>
              </div>
              <p className="feed-desc">{inc.description}</p>
              <div className="feed-card-row feed-meta">
                <span className={`sev-tag severity-${inc.severity}`}>{inc.severity}</span>
                <span className="dot-sep">·</span>
                <span>{STATUS_LABEL[inc.status] || inc.status}</span>
                <span className="dot-sep">·</span>
                <span className="mono">{timeAgo(inc.created_at)}</span>
              </div>
            </div>
            {inc.status === "triaged" && (
              <span
                className="feed-dispatch-btn"
                role="button"
                tabIndex={0}
                onClick={(e) => { e.stopPropagation(); onDispatch(inc.id); }}
              >
                {dispatchingId === inc.id ? "Assigning…" : "Dispatch"}
              </span>
            )}
          </button>
        ))}
      </div>

      <style>{`
        .feed {
          display: flex;
          flex-direction: column;
          background: var(--panel);
          border: 1px solid var(--line);
          border-radius: var(--radius-lg);
          overflow: hidden;
          height: 100%;
        }
        .feed-head {
          display: flex; justify-content: space-between; align-items: center;
          padding: 14px 16px;
          border-bottom: 1px solid var(--line);
          font-family: var(--font-display);
          font-size: 13px;
          font-weight: 600;
          letter-spacing: 0.03em;
          text-transform: uppercase;
          color: var(--text-muted);
        }
        .feed-count {
          background: var(--panel-raised);
          border: 1px solid var(--line);
          padding: 2px 8px;
          border-radius: 999px;
          color: var(--text-primary);
        }
        .feed-list { overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 6px; }
        .feed-empty { padding: 32px 16px; text-align: center; color: var(--text-faint); font-size: 13px; }

        .feed-card {
          display: flex;
          align-items: stretch;
          background: var(--panel-raised);
          border: 1px solid var(--line);
          border-radius: var(--radius-md);
          padding: 0;
          text-align: left;
          color: inherit;
          overflow: hidden;
          position: relative;
          transition: border-color 0.15s ease, transform 0.1s ease;
        }
        .feed-card:hover { border-color: var(--sev-color); }
        .feed-card.is-selected { border-color: var(--sev-color); background: var(--panel-hover); }
        .feed-card-bar { width: 4px; background: var(--sev-color); flex-shrink: 0; }
        .feed-card-body { padding: 10px 12px; flex: 1; min-width: 0; }
        .feed-card-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
        .feed-type { font-family: var(--font-display); font-size: 12.5px; font-weight: 600; }
        .feed-priority { font-size: 12px; color: var(--sev-color); }
        .feed-desc {
          margin: 4px 0 6px;
          font-size: 12.5px;
          color: var(--text-muted);
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        .feed-meta { justify-content: flex-start; gap: 6px; font-size: 11px; color: var(--text-faint); text-transform: capitalize; }
        .sev-tag { text-transform: uppercase; font-size: 10.5px; letter-spacing: 0.04em; font-weight: 600; }
        .dot-sep { opacity: 0.5; }

        .feed-dispatch-btn {
          align-self: center;
          margin-right: 10px;
          flex-shrink: 0;
          font-size: 11px;
          font-weight: 600;
          padding: 6px 10px;
          border-radius: var(--radius-sm);
          background: var(--signal);
          color: #06121f;
          white-space: nowrap;
        }
        .feed-dispatch-btn:hover { filter: brightness(1.1); }
      `}</style>
    </div>
  );
}
