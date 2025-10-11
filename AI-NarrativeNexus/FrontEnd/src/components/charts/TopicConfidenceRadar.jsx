import React, { useMemo } from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const TopicConfidenceRadar = ({ topics = [] }) => {
  const data = useMemo(() => {
    if (!Array.isArray(topics)) return [];
    return topics.slice(0, 8).map((topic, index) => {
      const label = topic?.label ?? `Topic ${topic?.rank ?? index + 1}`;
      const share = Number.isFinite(topic?.share)
        ? topic.share
        : Number.isFinite(topic?.confidence)
        ? topic.confidence
        : 0;
      const confidence = Number.isFinite(topic?.confidence) ? topic.confidence : share;
      return {
        label,
        share: Number((Math.max(0, Math.min(share, 1)) * 100).toFixed(1)),
        confidence: Number((Math.max(0, Math.min(confidence, 1)) * 100).toFixed(1)),
      };
    });
  }, [topics]);

  if (!data.length) {
    return (
      <div className="h-72 w-full rounded-2xl border border-white/10 bg-slate-900/40 p-6 text-sm text-white/60">
        Topic radar will appear after relevant themes are detected.
      </div>
    );
  }

  return (
    <div className="h-72 w-full rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-6">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} outerRadius="70%">
          <PolarGrid stroke="rgba(148, 163, 184, 0.25)" radialLines={false} />
          <PolarAngleAxis dataKey="label" tick={{ fill: "#e2e8f0", fontSize: 11 }} />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "#cbd5f5", fontSize: 10 }}
            tickFormatter={(value) => `${value}%`}
            stroke="rgba(148, 163, 184, 0.2)"
          />
          <Tooltip
            wrapperStyle={{ borderRadius: "0.75rem", border: "1px solid rgba(99, 102, 241, 0.25)" }}
            contentStyle={{
              backgroundColor: "rgba(15, 23, 42, 0.95)",
              borderRadius: "0.75rem",
              border: "1px solid rgba(148, 163, 184, 0.35)",
              color: "#f8fafc",
            }}
            formatter={(value, key) => [`${value}%`, key === "share" ? "Share" : "Confidence"]}
          />
          <Radar
            name="Share"
            dataKey="share"
            stroke="rgba(129, 140, 248, 0.8)"
            fill="rgba(129, 140, 248, 0.3)"
            strokeWidth={2}
          />
          <Radar
            name="Confidence"
            dataKey="confidence"
            stroke="rgba(16, 185, 129, 0.85)"
            fill="rgba(16, 185, 129, 0.25)"
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TopicConfidenceRadar;
