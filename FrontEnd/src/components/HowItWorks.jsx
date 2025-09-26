import React from "react";
import { FileText, Settings, BarChart3, Lightbulb } from "lucide-react";

const HowItWorks = () => {
  const steps = [
    {
      icon: <FileText className="w-8 h-8 text-primary" />,
      title: "1. Upload or Enter Text",
      description:
        "Upload a .txt, .csv, .pdf, or .docx file, or paste your own text directly into the input box.",
    },
    {
      icon: <Settings className="w-8 h-8 text-primary" />,
      title: "2. Preprocessing",
      description:
        "We clean and preprocess the text: removing noise, normalizing words, and extracting useful features.",
    },
    {
      icon: <BarChart3 className="w-8 h-8 text-primary" />,
      title: "3. AI Analysis",
      description:
        "Our AI models run topic modeling, sentiment detection, and summarization on your text.",
    },
    {
      icon: <Lightbulb className="w-8 h-8 text-primary" />,
      title: "4. Results & Insights",
      description:
        "You receive key topics, sentiment, concise summaries, and actionable insights with visualization support.",
    },
  ];

  return (
    <section className="relative min-h-screen bg-black bg-[url(/bg.svg)] text-white pt-24 pb-16">
      <div className="max-w-5xl mx-auto px-6 text-center">
        <h1 className="text-4xl md:text-5xl font-semibold text-primary">
          How It Works ?
        </h1>
        <p className="text-gray-300 mt-4 max-w-2xl mx-auto">
          Our platform makes text analysis simple. Just upload your file or paste text, and let our AI do the heavy lifting in four easy steps.
        </p>

        <div className="grid md:grid-cols-2 gap-8 mt-12">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className="p-6 bg-black border border-white/20 rounded-xl shadow-xl hover:bg-primary/20 hover:backdrop-blur transition"
            >
              <div className="flex items-center justify-center w-12 h-12 mx-auto bg-white/10 rounded-full mb-4">
                {step.icon}
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">
                {step.title}
              </h3>
              <p className="text-gray-300 text-sm">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
