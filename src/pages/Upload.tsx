import { HeroButton } from "@/components/HeroButton";
import { FeatureCard } from "@/components/FeatureCard";
import { Upload, FileText, BarChart3, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";

const UploadPage = () => {
  const navigate = useNavigate();

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      console.log('File selected:', file.name);
      // Handle file upload logic here
    }
  };

  return (
    <div className="min-h-screen text-foreground">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <button 
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors"
        >
          <ArrowLeft size={20} />
          Back to Home
        </button>
      </header>

      {/* Upload Section */}
      <section className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto text-center animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold mb-6 gradient-text">
            Upload Your File
          </h1>
          <p className="text-lg text-muted-foreground mb-12">
            Supports .doc, .txt, .csv files
          </p>

          {/* Upload Card */}
          <Card className="p-12 bg-card/80 backdrop-blur-sm border-dashed border-2 border-primary/30 hover:border-primary/60 transition-all duration-300 hover-glow">
            <div className="flex flex-col items-center space-y-6">
              <div className="p-6 rounded-full bg-primary/10 text-primary animate-glow">
                <Upload size={48} />
              </div>
              
              <div className="space-y-4">
                <h3 className="text-xl font-semibold">
                  Drag & drop your file here
                </h3>
                <p className="text-muted-foreground">
                  or click to browse
                </p>
              </div>

              <input
                type="file"
                accept=".doc,.docx,.txt,.csv"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              
              <HeroButton 
                variant="secondary" 
                onClick={() => document.getElementById('file-upload')?.click()}
              >
                Choose File
              </HeroButton>
            </div>
          </Card>
        </div>
      </section>

      {/* Actions Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 gradient-text">
            Choose Your Action
          </h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            <FeatureCard
              icon={<FileText size={40} />}
              title="📄 Summarise"
              description="Get a quick overview of the content with AI-powered summarization."
              className="animate-fade-in cursor-pointer"
            />
            
            <FeatureCard
              icon={<BarChart3 size={40} />}
              title="📊 Visualise"
              description="See insights, charts, and trends from your data instantly."
              className="animate-fade-in cursor-pointer"
            />
          </div>
        </div>
      </section>
    </div>
  );
};

export default UploadPage;