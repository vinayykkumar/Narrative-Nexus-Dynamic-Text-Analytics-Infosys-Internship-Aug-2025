import React, { useMemo } from "react";
import {
  ResponsiveContainer,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Bar,
  Cell,
  ReferenceLine,
} from "recharts";

const DEFAULT_COLORS = ["#60a5fa", "#a855f7", "#38bdf8", "#f87171", "#fbbf24", "#34d399"];

const TopicDistribution = ({ topics = [], onTopicSelect, selectedTopicKey }) => {
  const chartData = useMemo(() => {
    return topics.map((topic, index) => {
      const label = topic?.label ?? `Topic ${index + 1}`;
      const share = Number.isFinite(topic?.share)
        ? topic.share
        : Number.isFinite(topic?.confidence)
        ? topic.confidence
        : 0;
      const identifier =
        topic?.__id ??
        topic?.category_key ??
        `topic-${typeof topic?.original_topic_id !== "undefined" && topic?.original_topic_id !== null ? topic.original_topic_id : index}`;

      return {
        key: identifier,
        topicId: topic?.original_topic_id ?? index,
        label,
        share: Math.max(0, Math.min(share, 1)),
        mentions: topic?.mentions ?? 0,
        keywords: Array.isArray(topic?.keywords) ? topic.keywords : [],
      };
    });
  }, [topics]);

  const handleClick = (payload) => {
    if (!onTopicSelect) return;
    onTopicSelect(payload?.key ?? null);
  };

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 24, left: 0, bottom: 24 }}
          barSize={28}
        >
          <CartesianGrid strokeDasharray="4 8" stroke="rgba(148, 163, 184, 0.18)" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: "#cbd5f5", fontSize: 12 }}
            interval={0}
            angle={-20}
            textAnchor="end"
            height={80}
          />
          <YAxis
            tick={{ fill: "#cbd5f5" }}
            tickFormatter={(value) => `${Math.round(value * 100)}%`}
            width={48}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(15, 23, 42, 0.95)",
              border: "1px solid rgba(148, 163, 184, 0.3)",
              borderRadius: "0.75rem",
              color: "#f8fafc",
            }}
            formatter={(value, _name, { payload }) => [
              `${(value * 100).toFixed(1)}% share`,
              payload?.label ?? "Share",
            ]}
          />
          <Legend
            wrapperStyle={{ color: "#f1f5f9" }}
            formatter={(value) => <span className="text-xs text-slate-200">{value}</span>}
          />
          <ReferenceLine y={0.2} stroke="rgba(14, 165, 233, 0.35)" strokeDasharray="3 3" />
          <Bar
            dataKey="share"
            name="Topic Share"
            radius={[10, 10, 0, 0]}
            onClick={(_, index) => handleClick(chartData[index])}
          >
            {chartData.map((item, index) => {
              const color = DEFAULT_COLORS[index % DEFAULT_COLORS.length];
              const isSelected = selectedTopicKey && selectedTopicKey === item.key;
              return (
                <Cell
                  key={`cell-${item.key}`}
                  fill={color}
                  opacity={isSelected ? 1 : 0.65}
                  stroke={isSelected ? "#f8fafc" : color}
                  strokeWidth={isSelected ? 2 : 0.5}
                  cursor="pointer"
                />
              );
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TopicDistribution;
