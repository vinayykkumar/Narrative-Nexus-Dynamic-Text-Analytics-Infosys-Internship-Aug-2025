import { Metadata } from 'next';
import DataPreprocessingDemo from '@/components/data-preprocessing-demo';
import { ThemeToggle } from '@/components/theme-toggle';

export const metadata: Metadata = {
  title: 'Data Preprocessing | AI Narrative Nexus',
  description: 'Text preprocessing pipeline for cleaning, normalizing, and tokenizing text data',
};

export default function PreprocessingPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">AI Narrative Nexus</h1>
            <p className="text-sm text-muted-foreground">Data Preprocessing Pipeline</p>
          </div>
          <ThemeToggle />
        </div>
      </header>
      
      <main>
        <DataPreprocessingDemo />
      </main>
    </div>
  );
}
