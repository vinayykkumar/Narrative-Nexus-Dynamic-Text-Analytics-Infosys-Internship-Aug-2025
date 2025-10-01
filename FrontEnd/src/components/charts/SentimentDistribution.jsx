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
    const data = keys.map((key) => Number(normalisedDistribution?.[key] ?? 0));
    const backgroundColor = keys.map((key) => SENTIMENT_COLORS[key].background);
    const borderColor = keys.map((key) => SENTIMENT_COLORS[key].border);

    return {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [
        {
          label: "Sentiment Share",
          data,
          backgroundColor,
          borderColor,
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
        legend: { display: false },
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
      cutout: "78%",
      onClick: (_evt, elements) => {
        if (!onSegmentSelect || !elements?.length) return;
        const index = elements[0].index;
        const key = ["positive", "neutral", "negative"][index];
        if (key) onSegmentSelect(key);
      },
    }),
    [onSegmentSelect]
  );

  const centerLabel = useMemo(
    () => (overallLabel ? String(overallLabel).toUpperCase() : null),
    [overallLabel]
  );

  const sentimentSummaries = useMemo(() => {
    const keys = ["positive", "neutral", "negative"];
    return keys.map((key) => {
      const percent = Math.max(
        0,
        Math.min(1, Number(normalisedDistribution?.[key] ?? 0))
      );
      const label = key.charAt(0).toUpperCase() + key.slice(1);
      const iconMap = { positive: "😄", neutral: "😐", negative: "😟" };
      const descriptionMap = {
        positive: "Optimistic cues and affirmative language appear often.",
        neutral: "Balanced, factual passages with limited emotional tone.",
        negative: "Critical wording or dissatisfaction signals are detected.",
      };
      return {
        key,
        label,
        percent,
        color: SENTIMENT_COLORS[key].border,
        icon: iconMap[key],
        description: descriptionMap[key],
      };
    });
  }, [normalisedDistribution]);

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,300px)_1fr] lg:items-start">
      {/* Chart Card */}
      <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-6 shadow-lg shadow-black/40">
        <div className="relative mx-auto w-full max-w-[14rem] aspect-square">
          <Doughnut data={chartData} options={options} />
          {centerLabel && (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center text-white">
              <span className="text-[11px] uppercase tracking-[0.4em] text-white/40">
                Dominant
              </span>
              <span className="mt-1 text-xl font-semibold">{centerLabel}</span>
            </div>
          )}
        </div>

        {/* Chips now wrap properly */}
        <div className="mt-6 grid grid-cols-3 gap-3 text-xs text-white/60 sm:grid-cols-3 xs:grid-cols-2">
          {sentimentSummaries.map((item) => (
            <div
              key={`${item.key}-chip`}
              className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-center"
            >
              <div
                className="mx-auto mb-2 h-2 w-2 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              <p className="text-[11px] uppercase tracking-wide text-white/50">
                {item.label}
              </p>
              <p className="mt-1 text-sm font-semibold text-white">
                {(item.percent * 100).toFixed(0)}%
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Sentiment Details */}
      <div className="space-y-3">
        {sentimentSummaries.map((item) => {
          const isActive = selectedKey === item.key;
          return (
            <button
              type="button"
              key={item.key}
              aria-pressed={isActive}
              onClick={() => onSegmentSelect?.(item.key)}
              className={`w-full rounded-2xl border px-5 py-4 text-left transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-300 ${
                isActive
                  ? "border-indigo-300 bg-indigo-500/20"
                  : "border-white/10 bg-white/5 hover:border-white/30"
              }`}
            >
              <div className="flex items-start justify-between gap-3 text-white">
                <div className="flex items-center gap-3">
                  <span className="text-xl" aria-hidden>
                    {item.icon}
                  </span>
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-wide text-white/80">
                      {item.label}
                    </p>
                    <p className="text-xs text-white/60">{item.description}</p>
                  </div>
                </div>
                <span className="text-base font-semibold text-white">
                  {(item.percent * 100).toFixed(1)}%
                </span>
              </div>
            </button>
          );
        })}

        {selectedKey && (
          <p className="rounded-2xl border border-indigo-300/40 bg-indigo-400/10 px-5 py-3 text-sm text-indigo-100">
            Spotlighting{" "}
            <span className="font-semibold capitalize">{selectedKey}</span>{" "}
            signals across the analysis.
          </p>
        )}
      </div>
    </div>
  );
};

export default SentimentDistribution;
