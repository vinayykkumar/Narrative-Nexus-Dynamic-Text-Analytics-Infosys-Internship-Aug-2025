import { AnalysisResults } from "@/components/analysis-results"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Brain, Download, Share, Mail } from "lucide-react"
import Link from "next/link"
import { ThemeToggle } from "@/components/theme-toggle"
import { ExportDialog } from "@/components/export-dialog"

export default function ResultsPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Dashboard
                </Button>
              </Link>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-primary-foreground" />
                </div>
                <span className="text-xl font-serif font-semibold text-foreground">NarrativeNexus</span>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <ThemeToggle />
              <Button variant="outline" size="sm">
                <Share className="w-4 h-4 mr-2" />
                Share Results
              </Button>
              <Button variant="outline" size="sm">
                <Mail className="w-4 h-4 mr-2" />
                Email Report
              </Button>
              <ExportDialog>
                <Button size="sm" className="bg-secondary hover:bg-secondary/90">
                  <Download className="w-4 h-4 mr-2" />
                  Export PDF
                </Button>
              </ExportDialog>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Results */}
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-serif font-bold text-foreground mb-2">Analysis Results</h1>
              <p className="text-muted-foreground">
                Comprehensive insights and recommendations from your text analysis
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-right text-sm text-muted-foreground">
                <p>Analysis ID: #1247</p>
                <p>Completed: Dec 19, 2024</p>
              </div>
            </div>
          </div>
        </div>

        <AnalysisResults />
      </div>
    </div>
  )
}
