import { BarChart, CheckCircle, FileSearch, LayoutDashboard, Sparkles, Upload } from 'lucide-react';

const features = [
  {
    icon: Upload,
    title: "Multi-Source Data Input",
    desc: "Upload reports, articles, or social media posts in multiple formats (.txt, .csv, .docx).",
    bg: { from: '#3588F2', to: '#0BB0D7' }
  },
  {
    icon: Sparkles,
    title: "AI-Powered Topic Modeling",
    desc: "Automatically identify key themes using advanced models like LDA and NMF.",
    bg: { from: '#B153EA', to: '#E549A3' }
  },
  {
    icon: CheckCircle,
    title: "Sentiment Analysis",
    desc: "Detect emotional tones and categorize them as positive, neutral, or negative.",
    bg: { from: '#20C363', to: '#11B97E' }
  },
  {
    icon: BarChart,
    title: "Smart Summarization",
    desc: "Generate concise summaries with extractive and abstractive techniques.",
    bg: { from: '#F76C1C', to: '#F04A3C' }
  },
  {
    icon: LayoutDashboard,
    title: "Interactive Dashboards",
    desc: "Visualize insights with word clouds, bar charts, and topic graphs.",
    bg: { from: '#5C6AF1', to: '#427DF5' }
  },
  {
    icon: FileSearch, // import from lucide-react
    title: "Entity Recognition",
    desc: "Identify and highlight people, organizations, places, and keywords for deeper context understanding.",
    bg: { from: '#FFB800', to: '#FF7A00' }
},
];

const KeyFeatures = () => {
  return (
    <div className="px-4 py-20 sm:px-20 xl:px-32 bg-[url(bg_gradient.png)] bg-black min-h-screen" id="ai-features">
      <div className="text-center">
        <h2 className="text-primary text-3xl md:text-5xl
         font-bold mb-4">AI Features</h2>
        <p className="text-gray-300 max-w-lg mx-auto">
          Upload, analyze, and visualize — transform raw text into meaningful insights with NarrativeNexus AI.
        </p>
      </div>

      <div className="flex flex-wrap mt-10 justify-center">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <div
              key={index}
              className="p-8 m-4 max-w-xs rounded-lg bg-white/60 shadow-lg border border-gray-100 hover:-translate-y-1 transition-all duration-300 cursor-pointer"
            >
              <div
                className="w-12 h-12 flex items-center justify-center rounded-xl"
                style={{ background: `linear-gradient(to bottom, ${feature.bg.from}, ${feature.bg.to})` }}
              >
                <Icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="mt-6 mb-3 text-lg font-semibold">{feature.title}</h3>
              <p className="text-gray-900 text-sm max-w-[95%]">{feature.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default KeyFeatures;
