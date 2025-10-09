import React from "react";

export default function Modal({ open, onClose, title, children, footer }) {
  if (!open) return null;
  return (
    <div
      aria-modal="true"
      role="dialog"
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(2,6,23,0.6)",
        backdropFilter: "blur(8px)",
        display: "grid",
        placeItems: "center",
        zIndex: 1000
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          width: "min(1000px, 92vw)",
          height: "min(700px, 88vh)",
          display: "flex",
          flexDirection: "column",
          borderRadius: 16,
          overflow: "hidden"
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{display: "flex", alignItems: "center", justifyContent: "space-between", padding: 12}}>
          <h3 style={{margin: 0}}>{title || "Report Preview"}</h3>
          <button className="btn-tool" type="button" onClick={onClose}>Close</button>
        </div>
        <div style={{flex: 1, borderTop: "1px solid rgba(255,255,255,0.06)"}}>
          {children}
        </div>
        {footer && (
          <div style={{padding: 10, borderTop: "1px solid rgba(255,255,255,0.06)"}}>
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
