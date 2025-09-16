"use client"

import { useEffect, useState, useCallback } from "react"
import { useSearchParams } from "next/navigation"
import { AnalysisDashboard } from "@/components/analysis-dashboard"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Brain, Settings, Download, Share, Loader2 } from "lucide-react"
import Link from "next/link"
import { ThemeToggle } from "@/components/theme-toggle"
import { ExportDialog } from "@/components/export-dialog"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function DashboardPage() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('session')
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [reportData, setReportData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasTriedFetch, setHasTriedFetch] = useState(false)
  const [artifacts, setArtifacts] = useState<any | null>(null)

  console.log("🚀 DashboardPage rendered, sessionId:", sessionId)

  const fetchSessionData = useCallback(async (sessionId: string) => {
    setIsLoading(true)
    setError(null)
    
    try {
      console.error("🔍 Fetching dashboard data for session:", sessionId)
      
      // Fetch dashboard data
      const dashboardResponse = await fetch(`http://localhost:8000/dashboard/${sessionId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        mode: 'cors'
      })
      
      console.error("📡 Dashboard response status:", dashboardResponse.status, dashboardResponse.statusText)
      
      if (!dashboardResponse.ok) {
        throw new Error(`Failed to fetch dashboard data: ${dashboardResponse.status} ${dashboardResponse.statusText}`)
      }
      
      const dashboardResult = await dashboardResponse.json()
      console.error("✅ Dashboard data loaded successfully")
      
      setDashboardData(dashboardResult)
      
      // Try to fetch report data (optional)
      try {
        const reportResponse = await fetch(`http://localhost:8000/reports/generate/${sessionId}`)
        if (reportResponse.ok) {
          const reportResult = await reportResponse.json()
          setReportData(reportResult)
        }
      } catch (reportError) {
        console.warn("⚠️ Report generation failed, continuing without reports:", reportError)
      }
      
    } catch (error) {
      console.error("❌ Error fetching session data:", error)
      setError(error instanceof Error ? error.message : "Failed to load analysis results")
    } finally {
      setIsLoading(false)
      setHasTriedFetch(true)
    }
  }, [])

  // Trigger fetch when component loads and has session ID
  if (sessionId && !hasTriedFetch && !isLoading) {
    console.error("🚀 Triggering initial fetch...")
    fetchSessionData(sessionId).catch(console.error)
  }

  // Load artifacts saved by upload flow
  useEffect(() => {
    try {
      const raw = typeof window !== 'undefined' ? localStorage.getItem('analysisArtifacts') : null
      if (raw) {
        const parsed = JSON.parse(raw)
        setArtifacts(parsed)
        // Also populate minimal dashboard data to mark analysis as complete
        setDashboardData((prev: any) => prev ? { ...prev, artifacts: parsed } : {
          overview: { analysis_types_completed: 2, insights_generated: 0, total_texts_processed: 1 },
          architecture_complete: true,
          charts_data: {},
          artifacts: parsed,
        })
      }
    } catch (e) {
      console.warn('Failed to load artifacts from storage', e)
    }
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center space-y-4">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <h3 className="text-lg font-semibold">Loading Analysis Results</h3>
              <p className="text-sm text-muted-foreground text-center">
                Retrieving your complete analysis data from session {sessionId}...
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Results</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">{error}</p>
            <div className="flex gap-2">
              <Link href="/analyze">
                <Button variant="outline" size="sm">
                  Start New Analysis
                </Button>
              </Link>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => fetchSessionData(sessionId || '')}
                disabled={!sessionId}
              >
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }
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
                  New Analysis
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
                Share
              </Button>
              <ExportDialog>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
              </ExportDialog>
              <Link href="/settings">
                <Button variant="outline" size="sm">
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Dashboard */}
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
  {/* Debug Panel removed per request */}

        <div className="mb-6">
          <h1 className="text-3xl font-serif font-bold text-foreground mb-2">Analysis Dashboard</h1>
          <p className="text-muted-foreground">
            {sessionId 
              ? `Complete analysis results for session ${sessionId}` 
              : "Comprehensive insights from your text analysis"}
          </p>
        </div>

        {/* Quick Download Button for Enriched CSV */}
        {artifacts?.enriched_csv && (
          <div className="mb-8">
            <a
              href={artifacts.enriched_csv}
              className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground"
              target="_blank"
              rel="noreferrer"
            >
              <Download className="w-4 h-4" />
              Download Enriched CSV
            </a>
          </div>
        )}

  {/* Visual Previews removed from main dashboard; shown in individual sections */}

        {/* Pass the real data to the dashboard component */}
        <AnalysisDashboard 
          dashboardData={dashboardData} 
          reportData={reportData}
          sessionId={sessionId}
        />
      </div>
    </div>
  )
}
