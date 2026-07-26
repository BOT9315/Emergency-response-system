import React from "react";
import IncidentFeed from "./IncidentFeed.jsx";
import MapView from "./MapView.jsx";

export default function Dashboard({
  incidents, units, hotspots, stats, selectedId, onSelect,
  onDispatch, dispatchingId, onAutoOptimize, optimizing, onReportClick, center,
}) {
  const pendingCount = incidents.filter((i) => i.status === "triaged").length;

  return (
    <div className="dashboard">
      <div className="stat-row">
        <MiniStat label="Active" value={stats?.active_incidents ?? "—"} accent="var(--high)" />
        <MiniStat label="Pending Dispatch" value={pendingCount} accent="var(--critical)" />
        <MiniStat label="Units Available" value={stats ? `${stats.units_available}/${stats.units_total}` : "—"} accent="var(--low)" />
        <MiniStat label="Avg Response" value={stats ? `${stats.avg_response_minutes}m` : "—"} accent="var(--moderate)" />

        <div className="stat-actions">
          <button className="btn-outline" onClick={onAutoOptimize} disabled={optimizing || pendingCount === 0}>
            {optimizing ? "Optimizing…" : `AI Auto-Dispatch (${pendingCount})`}
          </button>
          <button className="btn-solid" onClick={onReportClick}>+ Report Incident</button>
        </div>
      </div>

      <div className="dashboard-grid">
        <IncidentFeed
          incidents={incidents}
          selectedId={selectedId}
          onSelect={onSelect}
          onDispatch={onDispatch}
          dispatchingId={dispatchingId}
        />
        <MapView incidents={incidents} units={units} hotspots={hotspots} center={center} />
      </div>

      <style>{`
        .dashboard { display: flex; flex-direction: column; gap: 16px; height: 100%; }
        .stat-row { display: flex; align-items: stretch; gap: 12px; }
        .stat-actions { display: flex; gap: 10px; margin-left: auto; align-items: center; }
        .btn-outline {
          background: var(--panel-raised); border: 1px solid var(--line); color: var(--text-primary);
          font-size: 12.5px; font-weight: 500; padding: 0 16px; border-radius: var(--radius-md);
        }
        .btn-outline:hover:not(:disabled) { border-color: var(--signal); }
        .btn-outline:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-solid {
          background: var(--signal); border: none; color: #06121f;
          font-size: 12.5px; font-weight: 600; padding: 0 16px; border-radius: var(--radius-md);
        }
        .btn-solid:hover { filter: brightness(1.08); }

        .dashboard-grid {
          display: grid;
          grid-template-columns: 360px 1fr;
          gap: 16px;
          flex: 1;
          min-height: 0;
        }
        @media (max-width: 980px) {
          .dashboard-grid { grid-template-columns: 1fr; }
        }
      `}</style>
    </div>
  );
}

function MiniStat({ label, value, accent }) {
  return (
    <div className="mini-stat" style={{ "--accent": accent }}>
      <div className="mini-value mono">{value}</div>
      <div className="mini-label">{label}</div>
      <style>{`
        .mini-stat {
          background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius-md);
          padding: 10px 16px; min-width: 130px;
          border-left: 3px solid var(--accent);
        }
        .mini-value { font-size: 20px; font-weight: 600; }
        .mini-label { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
      `}</style>
    </div>
  );
}
