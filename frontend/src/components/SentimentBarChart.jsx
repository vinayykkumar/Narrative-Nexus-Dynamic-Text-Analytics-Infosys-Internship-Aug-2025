import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList } from "recharts";

export default function SentimentBarChart({ data = [] }) {
  if (!Array.isArray(data)) data = [];
  return (
    <div className="glass rounded-xl p-4 shadow-md min-h-[220px]">
      <div className="font-bold text-lg mb-2 text-fuchsia-700 text-center">Sentiment Distribution</div>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={data}>
          <XAxis dataKey="name" tick={{fontSize: 12}} />
          <YAxis domain={[0,100]} tick={{fontSize: 12}} />
          <Tooltip />
          <Bar dataKey="value" radius={[8,8,0,0]} fill="#a855f7">
            <LabelList dataKey="value" position="top" fontSize={14} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
