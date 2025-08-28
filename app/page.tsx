import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, FileText, BarChart3, Brain, Target, Upload, Zap } from "lucide-react"
import Link from "next/link"
import { ThemeToggle } from "@/components/theme-toggle"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-serif font-semibold text-foreground">NarrativeNexus</span>
            </div>

            <div className="hidden md:flex items-center space-x-8">
              <Link href="#features" className="text-muted-foreground hover:text-foreground transition-colors">
                Features
              </Link>
              <Link href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-colors">
                How It Works
              </Link>
              <Link href="#pricing" className="text-muted-foreground hover:text-foreground transition-colors">
                Pricing
              </Link>
              <ThemeToggle />
              <Button variant="outline" size="sm">
                Sign In
              </Button>
              <Button size="sm" className="bg-secondary hover:bg-secondary/90">
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <Badge variant="secondary" className="mb-6">
            <Zap className="w-3 h-3 mr-1" />
            Advanced Text Analysis Platform
          </Badge>

          <h1 className="text-4xl md:text-6xl font-serif font-bold text-foreground mb-6 leading-tight">
            Transform Text Into
            <span className="text-secondary block">Actionable Insights</span>
          </h1>

          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
            NarrativeNexus processes diverse text inputs, extracts key themes, performs sentiment analysis, and delivers
            comprehensive insights to drive informed decision-making.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/analyze">
              <Button size="lg" className="bg-secondary hover:bg-secondary/90 text-lg px-8">
                Start Analysis
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Link href="/preprocessing">
              <Button variant="outline" size="lg" className="text-lg px-8 bg-transparent">
                Data Preprocessing
                <Zap className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-foreground mb-4">
              Powerful Analysis Capabilities
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Leverage advanced algorithms to extract meaningful insights from your text data
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border-border hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-4">
                  <FileText className="w-6 h-6 text-secondary" />
                </div>
                <CardTitle className="font-serif">Multi-Format Input</CardTitle>
                <CardDescription>
                  Upload documents, articles, social media content, and more in various formats
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-4">
                  <Brain className="w-6 h-6 text-secondary" />
                </div>
                <CardTitle className="font-serif">Topic Modeling</CardTitle>
                <CardDescription>
                  Advanced LDA and NMF algorithms identify key themes and topics automatically
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-secondary" />
                </div>
                <CardTitle className="font-serif">Sentiment Analysis</CardTitle>
                <CardDescription>
                  Understand emotional tone and sentiment patterns across your text data
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-4">
                  <Target className="w-6 h-6 text-secondary" />
                </div>
                <CardTitle className="font-serif">Smart Summarization</CardTitle>
                <CardDescription>
                  Generate concise summaries using both extractive and abstractive techniques
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-secondary" />
                </div>
                <CardTitle className="font-serif">Interactive Dashboards</CardTitle>
                <CardDescription>
                  Visualize insights with word clouds, charts, and comprehensive reports
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="w-6 h-6 text-secondary" />
                </div>
                <CardTitle className="font-serif">Data Preprocessing</CardTitle>
                <CardDescription>
                  Clean, normalize, and tokenize text data with advanced preprocessing pipelines
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="w-6 h-6 text-secondary" />
                </div>
                <CardTitle className="font-serif">Actionable Insights</CardTitle>
                <CardDescription>Get strategic recommendations based on your analysis results</CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-foreground mb-4">How It Works</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Simple three-step process to transform your text into insights
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mx-auto mb-6">
                <Upload className="w-8 h-8 text-secondary-foreground" />
              </div>
              <h3 className="text-xl font-serif font-semibold mb-4">1. Upload Your Data</h3>
              <p className="text-muted-foreground">
                Upload documents, paste text, or connect data sources. We support multiple formats including .txt, .csv,
                .docx, and more.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mx-auto mb-6">
                <Brain className="w-8 h-8 text-secondary-foreground" />
              </div>
              <h3 className="text-xl font-serif font-semibold mb-4">2. AI Analysis</h3>
              <p className="text-muted-foreground">
                Our advanced algorithms process your text, extract themes, analyze sentiment, and identify key patterns
                automatically.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mx-auto mb-6">
                <Target className="w-8 h-8 text-secondary-foreground" />
              </div>
              <h3 className="text-xl font-serif font-semibold mb-4">3. Get Insights</h3>
              <p className="text-muted-foreground">
                Receive comprehensive reports, interactive visualizations, and actionable recommendations to drive your
                decisions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-secondary/5">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-serif font-bold text-foreground mb-6">
            Ready to Transform Your Text Analysis?
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Join thousands of professionals who trust NarrativeNexus for their text analysis needs.
          </p>
          <Button size="lg" className="bg-secondary hover:bg-secondary/90 text-lg px-8">
            <Link href="/analyze" className="flex items-center">
              Start Your Free Trial
              <ArrowRight className="w-5 h-5 ml-2" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-serif font-semibold text-foreground">NarrativeNexus</span>
            </div>

            <div className="flex items-center space-x-6 text-sm text-muted-foreground">
              <Link href="#" className="hover:text-foreground transition-colors">
                Privacy Policy
              </Link>
              <Link href="#" className="hover:text-foreground transition-colors">
                Terms of Service
              </Link>
              <Link href="#" className="hover:text-foreground transition-colors">
                Contact
              </Link>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-border text-center text-sm text-muted-foreground">
            © 2024 NarrativeNexus. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}
