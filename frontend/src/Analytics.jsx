import React, { useEffect, useState } from "react";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import { api } from "../api.js";
import { TYPE_LABEL } from "../utils.js";

const SEV_COLORS = { critical: "#FF4757", high: "#FFA33D", moderate: "#3D9BFF", low: "#2FD9A8" };
const TYPE_COLORS = ["#3D9BFF", "#FF4757", "#FFA33D", "#2FD9A8", "#C77DFF", "#FF7A9C", "#8492A6"];

export default function Analytics({ stats }) {
  const [timeline, setTimeline] = useState([]);

  useEffect(() => {
    api.getTimeline(14).then(setTimeline).catch(() => { });
  }, []);


  if (!stats) return null;

  const typeData = Object.entries(stats.incidents_by_type).map(([name, value]) => ({
    name: TYPE_LABEL[name] || name, value,
  }));

  return (
    <div className="analytics">
      <h2 className="analytics-title">System Analytics</h2>

      <div className="stat-strip">
        <StatCard label="Total Incidents" value={stats.total_incidents} />
        <StatCard label="Active Now" value={stats.active_incidents} accent="var(--high)" />
        <StatCard label="Resolved" value={stats.resolved_incidents} accent="var(--low)" />
        <StatCard label="Avg Response" value={`${stats.avg_response_minutes}m`} accent="var(--moderate)" />
        <StatCard label="Units Available" value={`${stats.units_available}/${stats.units_total}`} />
      </div>

      <div className="chart-grid">
        <div className="chart-card">
          <div className="chart-head">Incidents · Last 14 Days by Severity</div>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={timeline}>
              <CartesianGrid stroke="#212A38" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#8492A6" }} tickFormatter={(d) => d.slice(5)} />
              <YAxis tick={{ fontSize: 10, fill: "#8492A6" }} allowDecimals={false} />
              <Tooltip contentStyle={{ background: "#161C26", border: "1px solid #212A38", fontSize: 12 }} />
              <Area type="monotone" dataKey="critical" stackId="1" stroke={SEV_COLORS.critical} fill={SEV_COLORS.critical} fillOpacity={0.5} />
              <Area type="monotone" dataKey="high" stackId="1" stroke={SEV_COLORS.high} fill={SEV_COLORS.high} fillOpacity={0.5} />
              <Area type="monotone" dataKey="moderate" stackId="1" stroke={SEV_COLORS.moderate} fill={SEV_COLORS.moderate} fillOpacity={0.5} />
              <Area type="monotone" dataKey="low" stackId="1" stroke={SEV_COLORS.low} fill={SEV_COLORS.low} fillOpacity={0.5} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-head">Incidents by Type</div>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={typeData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={3}>
                {typeData.map((entry, i) => (
                  <Cell key={entry.name} fill={TYPE_COLORS[i % TYPE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#161C26", border: "1px solid #212A38", fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 11, color: "#8492A6" }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <style>{`
        .analytics { padding: 4px; }
        .analytics-title { font-family: var(--font-display); font-size: 20px; margin: 0 0 16px; }
        .stat-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 20px; }
        .chart-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px; }
        @media (max-width: 900px) { .chart-grid { grid-template-columns: 1fr; } }
        .chart-card { background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius-lg); padding: 16px; }
        .chart-head { font-family: var(--font-display); font-size: 12.5px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-faint); margin-bottom: 10px; }
      `}</style>
    </div>
  );
}

function StatCard({ label, value, accent }) {
  return (
    <div className="stat-card" style={{ "--accent": accent || "var(--text-primary)" }}>
      <div className="stat-value mono">{value}</div>
      <div className="stat-label">{label}</div>
      <style>{`
        .stat-card {
          background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius-lg);
          padding: 14px 16px;
        }
        .stat-value { font-size: 24px; font-weight: 600; color: var(--accent); }
        .stat-label { font-size: 11.5px; color: var(--text-muted); margin-top: 2px; }
      `}</style>
    </div>
  );
}
