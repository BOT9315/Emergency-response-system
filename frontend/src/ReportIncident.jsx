import React, { useState } from "react";

export default function ReportIncident({ open, onClose, onSubmit, defaultCenter }) {
  const [form, setForm] = useState({
    description: "",
    reporter_name: "",
    casualties_reported: 0,
    latitude: defaultCenter[0],
    longitude: defaultCenter[1],
    address: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  if (!open) return null;

  const update = (field) => (e) => {
    const value = e.target.type === "number" ? parseFloat(e.target.value) : e.target.value;
    setForm((f) => ({ ...f, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.description.trim().length < 5) {
      setError("Please describe what's happening in a bit more detail.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const created = await onSubmit(form);
      setResult(created);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const reset = () => {
    setResult(null);
    setForm({ ...form, description: "", reporter_name: "", casualties_reported: 0, address: "" });
  };

  return (
    <div className="overlay" onClick={onClose}>
      <div className="panel" onClick={(e) => e.stopPropagation()}>
        <div className="panel-head">
          <h2>Report an Incident</h2>
          <button className="close-btn" onClick={onClose}>Close</button>
        </div>

        {result ? (
          <div className="result">
            <div className={`result-badge severity-${result.severity}`}>
              AI Triage: {result.incident_type.replace("_", " ")} · {result.severity}
            </div>
            <p className="result-line">Priority score <strong className="mono">{result.priority_score}</strong> / 100</p>
            {result.ai_notes && <p className="result-note">{result.ai_notes}</p>}
            <p className="result-sub">The dispatch queue and map have been updated in real time.</p>
            <div className="panel-actions">
              <button className="btn-primary" onClick={() => { reset(); onClose(); }}>Done</button>
              <button className="btn-ghost" onClick={reset}>Report Another</button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="form">
            <label>
              What's happening?
              <textarea
                rows={4}
                placeholder="Describe the situation in your own words — the AI engine will classify type and severity automatically."
                value={form.description}
                onChange={update("description")}
                required
              />
            </label>

            <div className="form-row">
              <label>
                Your name (optional)
                <input type="text" value={form.reporter_name} onChange={update("reporter_name")} placeholder="Anonymous" />
              </label>
              <label>
                People affected
                <input type="number" min="0" value={form.casualties_reported} onChange={update("casualties_reported")} />
              </label>
            </div>

            <label>
              Address / landmark (optional)
              <input type="text" value={form.address} onChange={update("address")} placeholder="Nearest cross street or landmark" />
            </label>

            <div className="form-row">
              <label>
                Latitude
                <input type="number" step="0.0001" value={form.latitude} onChange={update("latitude")} required />
              </label>
              <label>
                Longitude
                <input type="number" step="0.0001" value={form.longitude} onChange={update("longitude")} required />
              </label>
            </div>

            {error && <div className="form-error">{error}</div>}

            <button className="btn-primary" type="submit" disabled={submitting}>
              {submitting ? "Submitting to AI triage…" : "Submit Report"}
            </button>
          </form>
        )}
      </div>

      <style>{`
        .overlay {
          position: fixed; inset: 0; z-index: 1000;
          background: rgba(6, 9, 13, 0.6);
          display: flex; justify-content: flex-end;
          backdrop-filter: blur(2px);
        }
        .panel {
          width: 420px; max-width: 92vw; height: 100%;
          background: var(--panel);
          border-left: 1px solid var(--line);
          padding: 22px;
          overflow-y: auto;
          animation: slidein 0.2s ease;
        }
        @keyframes slidein { from { transform: translateX(24px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        .panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
        .panel-head h2 { font-family: var(--font-display); font-size: 18px; margin: 0; }
        .close-btn {
          background: var(--panel-raised); border: 1px solid var(--line); color: var(--text-muted);
          padding: 6px 12px; border-radius: var(--radius-sm); font-size: 12px;
        }
        .close-btn:hover { color: var(--text-primary); }

        .form { display: flex; flex-direction: column; gap: 14px; }
        .form label { display: flex; flex-direction: column; gap: 6px; font-size: 12.5px; color: var(--text-muted); }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .form input, .form textarea {
          background: var(--panel-raised);
          border: 1px solid var(--line);
          border-radius: var(--radius-sm);
          padding: 9px 10px;
          color: var(--text-primary);
          font-family: var(--font-body);
          font-size: 13px;
          resize: vertical;
        }
        .form input:focus, .form textarea:focus { border-color: var(--signal); }
        .form-error {
          background: var(--critical-bg); border: 1px solid var(--critical); color: var(--critical);
          padding: 8px 10px; border-radius: var(--radius-sm); font-size: 12.5px;
        }
        .btn-primary {
          background: var(--signal); color: #06121f; border: none;
          font-weight: 600; font-size: 13px; padding: 11px; border-radius: var(--radius-sm);
        }
        .btn-primary:disabled { opacity: 0.6; cursor: wait; }
        .btn-primary:hover:not(:disabled) { filter: brightness(1.08); }
        .btn-ghost {
          background: transparent; border: 1px solid var(--line); color: var(--text-muted);
          font-size: 13px; padding: 11px; border-radius: var(--radius-sm);
        }
        .panel-actions { display: flex; gap: 10px; margin-top: 6px; }
        .panel-actions button { flex: 1; }

        .result-badge {
          display: inline-block; padding: 6px 12px; border-radius: 999px;
          background: var(--panel-raised); border: 1px solid currentColor;
          font-size: 12.5px; font-weight: 600; text-transform: capitalize;
        }
        .result-line { margin: 14px 0 4px; font-size: 14px; }
        .result-note { color: var(--text-muted); font-size: 12.5px; }
        .result-sub { color: var(--text-faint); font-size: 12px; margin-top: 10px; }
      `}</style>
    </div>
  );
}
