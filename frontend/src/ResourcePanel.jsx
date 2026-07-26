import React from "react";

const STATUS_COLOR = {
  available: "var(--low)",
  dispatched: "var(--high)",
  en_route: "var(--moderate)",
  on_scene: "var(--critical)",
  out_of_service: "var(--text-faint)",
};

export default function ResourcePanel({ units }) {
  const grouped = units.reduce((acc, u) => {
    acc[u.unit_type] = acc[u.unit_type] || [];
    acc[u.unit_type].push(u);
    return acc;
  }, {});

  return (
    <div className="fleet">
      <h2 className="fleet-title">Responder Fleet</h2>
      <p className="fleet-sub">{units.filter(u => u.status === "available").length} of {units.length} units available for dispatch</p>

      <div className="fleet-grid">
        {Object.entries(grouped).map(([type, list]) => (
          <div className="fleet-group" key={type}>
            <div className="fleet-group-head">{type.replace("_", " ")}</div>
            {list.map((u) => (
              <div className="fleet-card" key={u.id}>
                <div>
                  <div className="fleet-callsign mono">{u.call_sign}</div>
                  <div className="fleet-base">{u.base_station || "Unassigned base"}</div>
                </div>
                <div className="fleet-status" style={{ color: STATUS_COLOR[u.status] }}>
                  <span className="fleet-dot" style={{ background: STATUS_COLOR[u.status] }} />
                  {u.status.replace("_", " ")}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>

      <style>{`
        .fleet { padding: 4px; }
        .fleet-title { font-family: var(--font-display); font-size: 20px; margin: 0 0 4px; }
        .fleet-sub { color: var(--text-muted); font-size: 13px; margin: 0 0 20px; }
        .fleet-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
        .fleet-group {
          background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius-lg);
          padding: 14px;
        }
        .fleet-group-head {
          font-family: var(--font-display); font-size: 12px; text-transform: uppercase;
          letter-spacing: 0.05em; color: var(--text-faint); margin-bottom: 10px;
        }
        .fleet-card {
          display: flex; justify-content: space-between; align-items: center;
          padding: 9px 4px; border-top: 1px solid var(--line-soft);
        }
        .fleet-card:first-of-type { border-top: none; }
        .fleet-callsign { font-size: 13px; font-weight: 600; }
        .fleet-base { font-size: 11.5px; color: var(--text-muted); }
        .fleet-status { display: flex; align-items: center; gap: 6px; font-size: 11.5px; text-transform: capitalize; }
        .fleet-dot { width: 7px; height: 7px; border-radius: 50%; }
      `}</style>
    </div>
  );
}
