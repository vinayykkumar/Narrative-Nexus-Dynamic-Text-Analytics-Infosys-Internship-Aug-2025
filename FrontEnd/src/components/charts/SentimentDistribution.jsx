import React, { useMemo } from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

const SENTIMENT_COLORS = {
  positive: {
    background: "rgba(16, 185, 129, 0.75)",
    border: "rgba(16, 185, 129, 1)",
  },
  neutral: {
    background: "rgba(251, 191, 36, 0.75)",
    border: "rgba(251, 191, 36, 1)",
  },
  negative: {
    background: "rgba(239, 68, 68, 0.75)",
    border: "rgba(239, 68, 68, 1)",
  },
};

const SentimentDistribution = ({
  distribution = { positive: 0, neutral: 0, negative: 0 },
  overallLabel,
  onSegmentSelect,
  selectedKey,
}) => {
  const normalisedDistribution = useMemo(() => {
    const total = ["positive", "neutral", "negative"].reduce((acc, key) => {
      const value = Number(distribution?.[key] ?? 0);
      return acc + (Number.isFinite(value) && value > 0 ? value : 0);
    }, 0);

    if (total <= 0) {
      return { positive: 0, neutral: 0, negative: 0 };
    }

    return ["positive", "neutral", "negative"].reduce(
      (acc, key) => ({
        ...acc,
        [key]: Math.max(0, Number(distribution?.[key] ?? 0) / total),
      }),
      {}
    );
  }, [distribution]);

  const chartData = useMemo(() => {
    const keys = ["positive", "neutral", "negative"];
    const data = keys.map((key) => Math.max(0, normalisedDistribution?.[key] ?? 0));
    return {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [
        {
          label: "Sentiment Share",
          data,
          backgroundColor: keys.map((k) => SENTIMENT_COLORS[k].background),
          borderColor: keys.map((k) => SENTIMENT_COLORS[k].border),
          borderWidth: 2,
          hoverBorderWidth: 3,
          spacing: 4,
          hoverOffset: 12,
        },
      ],
    };
  }, [normalisedDistribution]);

  const options = useMemo(
    () => ({
      maintainAspectRatio: false,
      responsive: true,
      plugins: {
        legend: {
          labels: {
            color: "#e5e7eb",
            font: { size: 13 },
          },
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label ?? "";
              const value = context.parsed ?? 0;
              return `${label}: ${(value * 100).toFixed(1)}%`;
            },
          },
        },
      },
      layout: { padding: 8 },
      cutout: "70%",
      onClick: (_evt, elements) => {
        if (!onSegmentSelect || !elements?.length) return;
        const index = elements[0].index;
        const key = ["positive", "neutral", "negative"][index];
        if (key) onSegmentSelect(key);
      },
    }),
    [onSegmentSelect]
  );

  const centerLabel = useMemo(() => {
    if (!overallLabel) return null;
    return String(overallLabel).toUpperCase();
  }, [overallLabel]);

  const sentimentSummaries = useMemo(() => {
    const keys = ["positive", "neutral", "negative"];
    return keys.map((key) => {
      const percent = Math.max(0, Math.min(1, Number(normalisedDistribution?.[key] ?? 0)));
      return {
        key,
        label: key.charAt(0).toUpperCase() + key.slice(1),
        percent,
        color: SENTIMENT_COLORS[key].border,
      };
    });
  }, [normalisedDistribution]);

  return (
    <div className="grid gap-6 md:grid-cols-[minmax(0,320px)_1fr] lg:items-center">
      {/* Chart */}
      <div className="relative w-full max-w-xs md:max-w-none h-60 sm:h-64 md:h-72 mx-auto">
        <Doughnut data={chartData} options={options} />
        {centerLabel && (
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-[10px] tracking-[0.3em] text-gray-300 uppercase pt-10">
              Dominant
            </span>
            <span className="text-lg sm:text-xl md:text-2xl font-semibold text-white">
              {centerLabel}
            </span>
          </div>
        )}
      </div>

      {/* Summaries */}
      <div className="space-y-3">
        {sentimentSummaries.map((item) => {
          const isActive = selectedKey && selectedKey === item.key;
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => onSegmentSelect?.(item.key)}
              className={`w-full rounded-xl border px-4 py-3 text-left transition 
                ${isActive
                  ? "border-white/60 bg-white/10 shadow-lg"
                  : "border-white/10 bg-slate-900/40 hover:border-white/40"
                }`}
            >
              <div className="flex items-center justify-between text-sm text-white/70">
                <span className="font-medium text-white">{item.label}</span>
                <span className="text-xs">{(item.percent * 100).toFixed(1)}%</span>
              </div>
              <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full transition-all duration-300"
                  style={{
                    width: `${Math.min(item.percent * 100, 100)}%`,
                    background: item.color,
                  }}
                />
              </div>
              {isActive ? (
                <p className="mt-2 text-[11px] text-indigo-200 uppercase tracking-wide">
                  Focused
                </p>
              ) : (
                <p className="mt-2 text-[11px] text-white/50">
                  Click to spotlight {item.label.toLowerCase()} mentions
                </p>
              )}
            </button>
          );
        })}
      </div>

      {selectedKey && (
        <div className="md:col-span-2 text-center text-sm text-gray-300">
          Highlighting <span className="font-semibold text-white">{selectedKey}</span> segment
        </div>
      )}
    </div>
  );
};

export default SentimentDistribution;
