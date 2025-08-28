import { HeroButton } from "@/components/HeroButton";
import { FeatureCard } from "@/components/FeatureCard";
import { FileText, BarChart3, Zap } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Welcome = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen text-foreground">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto animate-fade-in">
          <h1 className="text-6xl md:text-7xl font-bold mb-6 gradient-text leading-tight">
            Smart Insights
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-12 animate-float-up">
            Your AI-powered tool for document understanding.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center animate-float-up">
            <HeroButton 
              variant="primary" 
              onClick={() => navigate('/upload')}
            >
              Try Now →
            </HeroButton>
          </div>
        </div>
      </section>

      {/* Main Value Proposition */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center max-w-5xl mx-auto animate-fade-in">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 gradient-text leading-tight">
            Turn your files into clear summaries and powerful visuals — instantly.
          </h2>
        </div>
      </section>

      {/* Core Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <FeatureCard
            icon={<FileText size={40} />}
            title="Summarise Documents"
            description="Quickly condense reports, articles, and notes into clear, easy-to-read summaries."
            className="animate-fade-in"
          />
          
          <FeatureCard
            icon={<BarChart3 size={40} />}
            title="Visualise Data"
            description="Upload spreadsheets or text, and see trends with instant visual insights."
            className="animate-fade-in"
          />
          
          <FeatureCard
            icon={<Zap size={40} />}
            title="Save Time & Effort"
            description="No more manual reading and analysis — let AI handle it while you focus on decisions."
            className="animate-fade-in"
          />
        </div>
      </section>

      {/* Call to Action */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="animate-fade-in">
          <HeroButton 
            variant="primary" 
            onClick={() => navigate('/upload')}
            className="text-xl px-12 py-6"
          >
            Try Now
          </HeroButton>
        </div>
      </section>
    </div>
  );
};

export default Welcome;