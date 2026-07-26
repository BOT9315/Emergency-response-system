import React, { useMemo } from "react";
import { MapContainer, TileLayer, CircleMarker, Circle, Popup, Tooltip } from "react-leaflet";
import { SEVERITY_COLOR, TYPE_LABEL } from "../utils.js";

const UNIT_COLOR = {
  ambulance: "#2FD9A8",
  fire_engine: "#FF4757",
  police: "#3D9BFF",
  hazmat_unit: "#C77DFF",
  rescue_team: "#FFA33D",
};

export default function MapView({ incidents, units, hotspots, center }) {
  const mapCenter = useMemo(() => center || [28.6139, 77.209], [center]);

  return (
    <div className="mapview">
      <MapContainer
        center={mapCenter}
        zoom={12}
        style={{ height: "100%", width: "100%", background: "#0c1119" }}
        zoomControl={true}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; OpenStreetMap &copy; CARTO'
        />

        {hotspots.map((h, i) => (
          <Circle
            key={`hs-${i}`}
            center={[h.latitude, h.longitude]}
            radius={Math.max(150, h.weight * 400)}
            pathOptions={{ color: "#FFA33D", weight: 1, fillColor: "#FFA33D", fillOpacity: 0.08 }}
          >
            <Tooltip>{`Hotspot · ${h.incident_count} incidents · ${TYPE_LABEL[h.dominant_type] || h.dominant_type}`}</Tooltip>
          </Circle>
        ))}

        {units.map((u) => (
          <CircleMarker
            key={`u-${u.id}`}
            center={[u.latitude, u.longitude]}
            radius={6}
            pathOptions={{
              color: UNIT_COLOR[u.unit_type] || "#8492A6",
              fillColor: UNIT_COLOR[u.unit_type] || "#8492A6",
              fillOpacity: u.status === "available" ? 0.9 : 0.35,
              weight: 2,
            }}
          >
            <Popup>
              <strong>{u.call_sign}</strong><br />
              {u.unit_type.replace("_", " ")}<br />
              Status: {u.status}
            </Popup>
          </CircleMarker>
        ))}

        {incidents.map((inc) => (
          <CircleMarker
            key={`i-${inc.id}`}
            center={[inc.latitude, inc.longitude]}
            radius={9}
            pathOptions={{
              color: SEVERITY_COLOR[inc.severity]?.replace("var(--", "").replace(")", "") || "#8492A6",
              fillColor: "#000",
              fillOpacity: 0.4,
              weight: 3,
            }}
          >
            <Popup>
              <strong>{TYPE_LABEL[inc.incident_type] || inc.incident_type}</strong> · {inc.severity}<br />
              {inc.description}<br />
              Priority: {inc.priority_score}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      <div className="map-legend">
        <div className="legend-title">Legend</div>
        {Object.entries(UNIT_COLOR).map(([type, color]) => (
          <div className="legend-row" key={type}>
            <span className="legend-dot" style={{ background: color }} />
            {type.replace("_", " ")}
          </div>
        ))}
        <div className="legend-row"><span className="legend-ring" /> incident</div>
        <div className="legend-row"><span className="legend-zone" /> AI hotspot</div>
      </div>

      <style>{`
        .mapview {
          position: relative;
          height: 100%;
          border-radius: var(--radius-lg);
          overflow: hidden;
          border: 1px solid var(--line);
        }
        .leaflet-container { font-family: var(--font-body); }
        .map-legend {
          position: absolute;
          bottom: 14px;
          left: 14px;
          z-index: 500;
          background: rgba(15, 20, 27, 0.9);
          border: 1px solid var(--line);
          border-radius: var(--radius-md);
          padding: 10px 12px;
          font-size: 11px;
          color: var(--text-muted);
          backdrop-filter: blur(4px);
        }
        .legend-title {
          font-family: var(--font-display);
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-faint);
          margin-bottom: 6px;
        }
        .legend-row { display: flex; align-items: center; gap: 6px; padding: 2px 0; text-transform: capitalize; }
        .legend-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
        .legend-ring { width: 8px; height: 8px; border-radius: 50%; border: 2px solid var(--text-muted); display: inline-block; }
        .legend-zone { width: 10px; height: 10px; border-radius: 50%; background: rgba(255,163,61,0.2); border: 1px solid var(--high); display: inline-block; }
      `}</style>
    </div>
  );
}
