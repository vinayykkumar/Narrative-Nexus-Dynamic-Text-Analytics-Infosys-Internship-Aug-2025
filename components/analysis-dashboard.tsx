"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { AnalysisOverview } from "@/components/analysis-overview"
import { TopicModelingResults } from "@/components/topic-modeling-results"
import { SentimentAnalysisResults } from "@/components/sentiment-analysis-results"
import TextSummaryResults from "@/components/text-summary-results"
import { BarChart3, Brain, FileText, Target, Clock, CheckCircle, AlertCircle, Pause, RotateCcw } from "lucide-react"
import Link from "next/link"

interface AnalysisDashboardProps {
  dashboardData?: any
  reportData?: any  
  sessionId?: string | null
}

export function AnalysisDashboard({ dashboardData, reportData, sessionId }: AnalysisDashboardProps) {
  const [analysisStatus, setAnalysisStatus] = useState<"running" | "completed" | "paused" | "error">("completed")
  const [activeTab, setActiveTab] = useState("overview")
  const [analysisResults, setAnalysisResults] = useState<any | null>(null)
  const [localArtifacts, setLocalArtifacts] = useState<any | null>(null)
  const [reportUrl, setReportUrl] = useState<string | null>(null)

  // Debug: Log what data we're receiving
  console.log("🔍 AnalysisDashboard received data:", { 
    dashboardData: dashboardData, 
    analysisResults: dashboardData?.charts_data?.analysis_results,
    sessionId 
  })

  // Load structured results from localStorage (set by upload flow)
  useEffect(() => {
    try {
      const raw = typeof window !== 'undefined' ? localStorage.getItem('analysisResults') : null
      if (raw) {
        const parsed = JSON.parse(raw)
        setAnalysisResults(parsed)
  if (parsed?.report_html) setReportUrl("/reports/analysis")
      }
    } catch (e) {
      console.warn('Failed to load analysisResults from storage', e)
    }
  }, [])

  // Load artifacts from localStorage as a fallback
  useEffect(() => {
    try {
      const raw = typeof window !== 'undefined' ? localStorage.getItem('analysisArtifacts') : null
      if (raw) setLocalArtifacts(JSON.parse(raw))
    } catch (e) {
      console.warn('Failed to load analysisArtifacts from storage', e)
    }
  }, [])

  // Set status based on real data
  useEffect(() => {
    if (dashboardData?.architecture_complete) {
      setAnalysisStatus("completed")
    } else if (dashboardData) {
      setAnalysisStatus("running")
    }
  }, [dashboardData])

  // Use real data if available, fallback to demo data
  const dashboard = dashboardData?.dashboard || dashboardData
  // Access artifacts from dashboardData or local fallback
  const artifacts = (dashboardData && (dashboardData as any).artifacts) || localArtifacts || null
  const analysisProgress = dashboard ? {
    preprocessing: 100,
    topicModeling: dashboard.overview?.analysis_types_completed >= 1 ? 100 : 0,
    sentimentAnalysis: dashboard.overview?.analysis_types_completed >= 2 ? 100 : 0,
    summarization: dashboard.overview?.insights_generated > 0 ? 100 : 0,
    overall: dashboard.overview?.analysis_types_completed >= 2 && dashboard.overview?.insights_generated > 0 ? 100 : 80,
  } : {
    preprocessing: 100,
    topicModeling: 100,
    sentimentAnalysis: 100,
    summarization: 85,
    overall: 92,
  }

  const analysisSteps = dashboard ? [
    { name: "Text Input Processing", status: "completed", progress: 100 },
    { name: "Data Processing", status: "completed", progress: 100 },
    { name: "Sentiment Analysis", status: dashboard.overview?.analysis_types_completed >= 1 ? "completed" : "pending", progress: dashboard.overview?.analysis_types_completed >= 1 ? 100 : 0 },
    { name: "Topic Modeling", status: dashboard.overview?.analysis_types_completed >= 2 ? "completed" : "pending", progress: dashboard.overview?.analysis_types_completed >= 2 ? 100 : 0 },
    { name: "Insight Generation", status: dashboard.overview?.insights_generated > 0 ? "completed" : "pending", progress: dashboard.overview?.insights_generated > 0 ? 100 : 0 },
  ] : [
    { name: "Text Preprocessing", status: "completed", progress: 100 },
    { name: "Topic Modeling", status: "completed", progress: 100 },
    { name: "Sentiment Analysis", status: "completed", progress: 100 },
    { name: "Text Summarization", status: "running", progress: 85 },
    { name: "Insight Generation", status: "pending", progress: 0 },
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case "running":
        return <Clock className="w-4 h-4 text-secondary animate-pulse" />
      case "error":
        return <AlertCircle className="w-4 h-4 text-destructive" />
      default:
        return <Clock className="w-4 h-4 text-muted-foreground" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "running":
        return (
          <Badge variant="secondary" className="animate-pulse">
            Processing
          </Badge>
        )
      case "completed":
        return <Badge className="bg-green-500 hover:bg-green-600">Completed</Badge>
      case "paused":
        return <Badge variant="outline">Paused</Badge>
      case "error":
        return <Badge variant="destructive">Error</Badge>
      default:
        return <Badge variant="outline">Pending</Badge>
    }
  }

  return (
    <div className="space-y-6">
      {/* Analysis Status Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="font-serif flex items-center gap-2">
                <Brain className="w-5 h-5" />
                Analysis Progress
              </CardTitle>
              <CardDescription>Real-time progress of your text analysis pipeline</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              {/* Report link removed; use Generate Report button in Overview */}
              {getStatusBadge(analysisStatus)}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Overall Progress</span>
              <span className="text-sm text-muted-foreground">{analysisProgress.overall}%</span>
            </div>
            <Progress value={analysisProgress.overall} className="h-2" />
          </div>

          <div className="grid gap-4">
            {analysisSteps.map((step, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(step.status)}
                  <span className="font-medium">{step.name}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Progress value={step.progress} className="w-20 h-2" />
                  <span className="text-sm text-muted-foreground w-12">{step.progress}%</span>
                </div>
              </div>
            ))}
          </div>

          {analysisStatus === "running" && (
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Pause className="w-4 h-4 mr-2" />
                Pause
              </Button>
              <Button variant="outline" size="sm">
                <RotateCcw className="w-4 h-4 mr-2" />
                Restart
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analysis Results Tabs */}
      <Card>
        <CardContent className="p-0">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <div className="border-b border-border px-6 pt-6">
              <TabsList className="h-10 w-full justify-start">
                <TabsTrigger value="overview" className="flex items-center gap-2 px-4">
                  <BarChart3 className="w-4 h-4" />
                  Overview
                </TabsTrigger>
                <TabsTrigger value="topics" className="flex items-center gap-2 px-4">
                  <Brain className="w-4 h-4" />
                  Topics
                </TabsTrigger>
                <TabsTrigger value="sentiment" className="flex items-center gap-2 px-4">
                  <Target className="w-4 h-4" />
                  Sentiment
                </TabsTrigger>
                <TabsTrigger value="summary" className="flex items-center gap-2 px-4">
                  <FileText className="w-4 h-4" />
                  Summary
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="p-6">
              <TabsContent value="overview" className="mt-0">
                <AnalysisOverview 
                  dashboardData={dashboardData} 
                  reportData={reportData}
                  sessionId={sessionId}
                />
              </TabsContent>

              <TabsContent value="topics" className="mt-0">
                {(() => {
                  const fromDashboard = dashboard?.charts_data?.analysis_results?.find((r: any) => r.analysis_type === 'topic_modeling')?.results
                  const topicResults = fromDashboard || analysisResults?.topic_modeling_results || null
                  console.log("🎯 Passing topic results to TopicModelingResults:", topicResults)
                  return (
                    <div className="space-y-6">
                      {artifacts && (
                        <div className="space-y-4">
                          <div className="text-sm text-muted-foreground">Visualizations</div>
                          <div className="grid md:grid-cols-3 gap-4">
                            {artifacts?.topic_distribution_pie && (
                              <div className="border border-border rounded-lg p-2">
                                <div className="text-sm mb-2">Topic Distribution</div>
                                <img src={artifacts.topic_distribution_pie} alt="Topic Distribution" className="w-full rounded" />
                              </div>
                            )}
                            {Array.isArray(artifacts?.wordclouds) && artifacts.wordclouds.slice(0, 5).map((url: string, idx: number) => (
                              <img key={idx} src={url} alt={`Wordcloud ${idx}`} className="w-full rounded border" />
                            ))}
                          </div>
                        </div>
                      )}
                      {topicResults && (
                        <TopicModelingResults results={topicResults} />
                      )}
                      {!topicResults && !artifacts && (
                        <div className="text-sm text-muted-foreground">No topic results available yet.</div>
                      )}
                    </div>
                  )
                })()}
              </TabsContent>


              <TabsContent value="sentiment" className="mt-0">
                {(() => {
                  const fromDashboard = dashboard?.charts_data?.analysis_results?.find((r: any) => r.analysis_type === 'sentiment')?.results
                  const sentimentResults = fromDashboard || analysisResults?.sentiment_results || null
                  console.log("🎯 Passing sentiment results to SentimentAnalysisResults:", sentimentResults)
                  return (
                    <div className="space-y-6">
                      {artifacts && (
                        <div className="space-y-4">
                          <div className="text-sm text-muted-foreground">Visualizations</div>
                          <div className="grid md:grid-cols-2 gap-4">
                            {artifacts?.sentiment_distribution_bar && (
                              <div className="border border-border rounded-lg p-2">
                                <div className="text-sm mb-2">Sentiment Distribution</div>
                                <img src={artifacts.sentiment_distribution_bar} alt="Sentiment Distribution" className="w-full rounded" />
                              </div>
                            )}
                            {artifacts?.topic_sentiment_pie && (
                              <div className="border border-border rounded-lg p-2">
                                <div className="text-sm mb-2">Topic vs Sentiment (Pie)</div>
                                <img src={artifacts.topic_sentiment_pie} alt="Topic Sentiment Pie" className="w-full rounded" />
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      {sentimentResults && (
                        <SentimentAnalysisResults results={sentimentResults} />
                      )}
                      {!sentimentResults && !artifacts && (
                        <div className="text-sm text-muted-foreground">No sentiment results available yet.</div>
                      )}
                    </div>
                  )
                })()}
              </TabsContent>

              <TabsContent value="summary" className="mt-0">
                <TextSummaryResults />
              </TabsContent>
            </div>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
