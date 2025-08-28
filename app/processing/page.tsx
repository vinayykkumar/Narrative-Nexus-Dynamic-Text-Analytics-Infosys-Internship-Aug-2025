"use client"

import { AnalysisProgress } from "@/components/analysis-progress"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Brain } from "lucide-react"
import Link from "next/link"
import { ThemeToggle } from "@/components/theme-toggle"

export default function ProcessingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/analyze">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Input
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

      {/* Main Content */}
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-serif font-bold text-foreground mb-2">Processing Analysis</h1>
          <p className="text-muted-foreground">
            Your text is being analyzed using advanced NLP algorithms. This typically takes 1-2 minutes.
          </p>
        </div>

        <AnalysisProgress 
          onComplete={(results) => {
            // Store results and redirect to dashboard
            localStorage.setItem('analysisResults', JSON.stringify(results))
            setTimeout(() => {
              window.location.href = '/dashboard'
            }, 2000)
          }}
        />
      </div>
    </div>
  )
}
