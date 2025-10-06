"use client"

import { useSearchParams } from "next/navigation"
import { AnalysisProgress } from "@/components/analysis-progress"
import TextSummaryResults from "@/components/text-summary-results"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowLeft, Brain } from "lucide-react"
import Link from "next/link"
import { ThemeToggle } from "@/components/theme-toggle"

export default function ProcessingPage() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('session')
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
      <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-serif font-bold text-foreground mb-2">Text Analysis & Processing</h1>
          <p className="text-muted-foreground">
            Comprehensive analysis tools including topic modeling, sentiment analysis, and text summarization.
          </p>
        </div>

        <Tabs defaultValue="analysis" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="analysis">Topic Analysis</TabsTrigger>
            <TabsTrigger value="summarization">Text Summarization</TabsTrigger>
          </TabsList>
          
          <TabsContent value="analysis" className="mt-6">
            <AnalysisProgress 
              onComplete={(results) => {
                // Store results and redirect to dashboard with session ID
                localStorage.setItem('analysisResults', JSON.stringify(results))
                setTimeout(() => {
                  const dashboardUrl = sessionId 
                    ? `/dashboard?session=${sessionId}`
                    : '/dashboard'
                  window.location.href = dashboardUrl
                }, 2000)
              }}
            />
          </TabsContent>
          
          <TabsContent value="summarization" className="mt-6">
            <TextSummaryResults />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
