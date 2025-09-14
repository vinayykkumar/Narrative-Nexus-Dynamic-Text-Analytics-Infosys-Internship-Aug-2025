import React from "react";

const About = () => {
  return (
    <section className="py-16 bg-[url(/bg_gradient.png)] bg-center bg-cover bg-black">
      <h1 className="text-3xl md:text-5xl text-primary font-semibold text-center mx-auto">
        About NarrativeNexus
      </h1>
      <p className="text-lg text-slate-300 text-center mt-6 max-w-2xl mx-auto">
        A dynamic text analysis platform that transforms unstructured text into
        clear, actionable insights — helping you make smarter, faster decisions.
      </p>

      <div className="max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-center gap-8 px-4 md:px-0 py-16">
        {/* About Image */}
        <img
          className="max-w-sm w-full m-auto rounded-xl h-auto"
          src="https://images.wondershare.com/edrawmax/article2023/ai-text-analysis/ai-concept.jpg"
          alt="NarrativeNexus"
        />

        {/* About Content */}
        <div>
          <h1 className="text-3xl text-primary font-semibold">Our Core Features</h1>
          <p className="text-md text-slate-300 mt-6">
            NarrativeNexus leverages advanced AI algorithms to analyze text
            data, identify key themes, detect sentiment, and summarize insights
            in easy-to-understand visual dashboards.
          </p>

          <div className="flex flex-col gap-10 mt-6">
            {/* Feature 1 */}
            <div className="flex items-center gap-4">
              <div className="size-9 p-2 bg-primary/30 border border-indigo-200 rounded-md">
                <img
                  src="https://raw.githubusercontent.com/prebuiltui/prebuiltui/main/assets/aboutSection/flashEmoji.png"
                  alt=""
                />
              </div>
              <div>
                <h3 className="text-base font-medium text-slate-200">
                  AI-Powered Insights
                </h3>
                <p className="text-sm text-slate-400">
                  Extract topics and sentiment automatically from any text data.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="flex items-center gap-4">
              <div className="size-9 p-2 bg-primary/30 border border-indigo-200 rounded-md">
                <img
                  src="https://raw.githubusercontent.com/prebuiltui/prebuiltui/main/assets/aboutSection/colorsEmoji.png"
                  alt=""
                />
              </div>
              <div>
                <h3 className="text-base font-medium text-slate-200">
                  Smart Summarization
                </h3>
                <p className="text-sm text-slate-400">
                  Generate concise summaries — both extractive and abstractive.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="flex items-center gap-4">
              <div className="size-9 p-2 bg-primary/30 border border-indigo-200 rounded-md">
                <img
                  src="https://raw.githubusercontent.com/prebuiltui/prebuiltui/main/assets/aboutSection/puzzelEmoji.png"
                  alt=""
                />
              </div>
              <div>
                <h3 className="text-base font-medium text-slate-200">
                  Interactive Dashboards
                </h3>
                <p className="text-sm text-slate-400">
                  Visualize results with word clouds, charts, and topic graphs
                  in real time.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
