import Link from "next/link"
import AnalysisReport from "@/components/analysis-report"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Brain } from "lucide-react"
import { ThemeToggle } from "@/components/theme-toggle"

export default function ThemedReportPage() {
  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Dashboard
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
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <AnalysisReport />
      </main>
    </div>
  )
}
