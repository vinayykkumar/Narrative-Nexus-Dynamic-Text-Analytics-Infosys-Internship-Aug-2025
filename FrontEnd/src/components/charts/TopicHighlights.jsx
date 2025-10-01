import React, { useMemo } from "react";

const TopicHighlights = ({ topics = [], selectedTopicKey, onTopicSelect }) => {
  const prepared = useMemo(() => {
    if (!Array.isArray(topics)) return [];
    return topics.map((topic, index) => {
      const key = topic?.__id ?? topic?.category_key ?? `topic-${index}`;
      const label = topic?.label ?? `Topic ${topic?.rank ?? index + 1}`;
      const shareBase = Number(topic?.share ?? topic?.confidence ?? topic?.score ?? 0);
      const share = Number.isFinite(shareBase) ? Math.max(0, Math.min(shareBase, 1)) : 0;
      const mentions = Number(topic?.mentions ?? 0);
      const confidence = Number.isFinite(topic?.confidence)
        ? Math.max(0, Math.min(topic.confidence, 1))
        : share;
      const keywords = Array.isArray(topic?.keywords) ? topic.keywords.slice(0, 6) : [];

      return {
        key,
        label,
        share,
        confidence,
        mentions,
        keywords,
        rank: topic?.rank ?? index + 1,
      };
    });
  }, [topics]);

  if (!prepared.length) {
    return (
      <div className="w-full rounded-xl border border-white/10 bg-slate-900/40 p-5 text-sm text-white/60">
        Topic highlights will appear once the analysis detects thematic clusters.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3">
      {prepared.map((topic) => {
        const isActive = selectedTopicKey === topic.key;
        return (
          <button
            key={topic.key}
            type="button"
            onClick={() => onTopicSelect?.(topic.key)}
            className={`group rounded-2xl border px-4 py-4 text-left transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-400 ${
              isActive
                ? "border-primary/70 bg-primary/10 shadow-lg"
                : "border-white/10 bg-slate-900/50 hover:border-primary/40"
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-white/60">
                  <span>#{topic.rank}</span>
                  <span className="hidden sm:inline">Theme focus</span>
                </div>
                <p className="mt-1 text-lg font-semibold text-white">{topic.label}</p>
                {topic.keywords.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {topic.keywords.map((keyword) => (
                      <span
                        key={`${topic.key}-${keyword}`}
                        className="rounded-full bg-white/10 px-3 py-1 text-[11px] uppercase tracking-wide text-white/70"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="flex flex-col items-end text-white/70 text-xs">
                <span className="text-sm font-semibold text-white">
                  {(topic.share * 100).toFixed(1)}%
                </span>
                <span className="mt-1">Relevance</span>
                {topic.mentions > 0 && (
                  <span className="mt-2 rounded-lg bg-white/10 px-2 py-1 text-[10px] uppercase tracking-wide text-white/60">
                    {topic.mentions} mention{topic.mentions === 1 ? "" : "s"}
                  </span>
                )}
                <span className="mt-2 text-[10px] text-white/50">
                  Confidence {(topic.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
};

export default TopicHighlights;
