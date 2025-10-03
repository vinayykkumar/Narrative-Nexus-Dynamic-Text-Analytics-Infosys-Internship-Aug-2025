import React, { useMemo } from "react";

const KeywordWordCloud = ({ keywords = [], onKeywordSelect, selectedKeyword }) => {
  const prepared = useMemo(() => {
    if (!Array.isArray(keywords) || keywords.length === 0) return [];

    const trimmed = keywords.slice(0, 80);
    const maxScore = trimmed.reduce((acc, item) => {
      const value = Number(item?.score ?? 0);
      return value > acc ? value : acc;
    }, 0.0001);

    const seededRandom = (seed) => {
      let value = 0;
      for (let i = 0; i < seed.length; i += 1) {
        value = (value * 31 + seed.charCodeAt(i)) % 233;
      }
      return () => {
        value = (value * 9301 + 49297) % 233280;
        return value / 233280;
      };
    };

    return trimmed
      .map((item, index) => {
        const term = item?.term ?? `term-${index}`;
        const score = Number(item?.score ?? 0);
        const weight = Math.max(0.15, score / maxScore);
        const fontSize = 18 + weight * 28;
        const random = seededRandom(term + index);
        const angle = (random() > 0.75 ? random() * 20 - 10 : random() * 10 - 5).toFixed(2);
        const saturation = 60 + random() * 30;
        const lightness = 65 - weight * 22;
        const hue = (index * 47 + random() * 60) % 360;

        return {
          term,
          score,
          weight,
          fontSize,
          rotation: angle,
          hue,
          saturation,
          lightness,
          column: index % 3,
          row: Math.floor(index / 3),
        };
      })
      .sort((a, b) => b.score - a.score);
  }, [keywords]);

  if (!prepared.length) {
    return (
      <div className="w-full p-6 text-center text-sm text-slate-300 border border-white/10 rounded-xl bg-slate-900/40">
        Keyword cloud will appear once we detect high-signal phrases.
      </div>
    );
  }

  const rows = prepared.reduce((acc, word) => {
    const key = word.row;
    if (!acc[key]) acc[key] = [];
    acc[key].push(word);
    return acc;
  }, {});

  const handleClick = (term) => {
    if (!onKeywordSelect) return;
    onKeywordSelect(term);
  };

  return (
    <div className="w-full overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 p-6 sm:p-8 shadow-xl">
      <div className="space-y-4">
        {Object.values(rows).map((rowWords, rowIndex) => (
          <div
            key={`row-${rowIndex}`}
            className="flex flex-wrap items-center justify-center gap-3 sm:gap-6"
          >
            {rowWords.map((word, columnIndex) => {
              const isActive = selectedKeyword === word.term;
              const jitter = ((columnIndex + rowIndex) % 2 === 0 ? -1 : 1) * 6;
              return (
                <button
                  key={`${word.term}-${rowIndex}-${columnIndex}`}
                  type="button"
                  onClick={() => handleClick(word.term)}
                  className={`select-none transition-all duration-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-400 ${
                    isActive ? "scale-105 text-white drop-shadow-[0_4px_20px_rgba(99,102,241,0.55)]" : "opacity-90 hover:opacity-100"
                  }`}
                  style={{
                    fontSize: `${word.fontSize}px`,
                    color: `hsl(${word.hue}, ${word.saturation}%, ${word.lightness}%)`,
                    transform: `rotate(${word.rotation}deg) translateY(${jitter}px)`,
                    fontWeight: isActive ? 700 : 500,
                    textShadow: "0 18px 30px rgba(15, 23, 42, 0.45)",
                  }}
                >
                  {word.term}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      <div className="mt-6 rounded-2xl border border-white/5 bg-white/5 p-4 text-center text-sm text-white/70">
        {selectedKeyword ? (
          <span>
            Highlighting narrative around <span className="font-semibold text-white">{selectedKeyword}</span>
          </span>
        ) : (
          <span>Select a keyword to spotlight related suggestions and topics.</span>
        )}
      </div>
    </div>
  );
};

export default KeywordWordCloud;
