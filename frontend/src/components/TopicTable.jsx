import React from "react";
export default function TopicTable({ topics = [] }) {
  return (
    <div className="glass rounded-xl p-4 shadow-md min-h-[190px]">
      <div className="font-bold text-lg mb-2 text-blue-700">Topics (LDA/NMF)</div>
      <table className="w-full text-sm">
        <thead>
          <tr>
            <th className="text-left font-semibold pr-2">#</th>
            <th className="text-left font-semibold">Key Words</th>
            <th className="font-semibold text-right">%</th>
          </tr>
        </thead>
        <tbody>
          {topics.map((t,i) => (
            <tr key={i} className="border-t border-gray-200">
              <td>{t.topic}</td>
              <td>{t.keyWords}</td>
              <td className="text-right">{t.percent}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
