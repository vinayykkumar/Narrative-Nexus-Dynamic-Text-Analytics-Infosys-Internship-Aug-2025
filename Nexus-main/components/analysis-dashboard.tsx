"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { AnalysisOverview } from "@/components/analysis-overview"
import { TopicModelingResults } from "@/components/topic-modeling-results"
import { SentimentAnalysisResults } from "@/components/sentiment-analysis-results"
import { TextSummaryResults } from "@/components/text-summary-results"
import { BarChart3, Brain, FileText, Target, Clock, CheckCircle, AlertCircle, Pause, RotateCcw } from "lucide-react"

export function AnalysisDashboard() {
  const [analysisStatus, setAnalysisStatus] = useState<"running" | "completed" | "paused" | "error">("completed")
  const [activeTab, setActiveTab] = useState("overview")

  const analysisProgress = {
    preprocessing: 100,
    topicModeling: 100,
    sentimentAnalysis: 100,
    summarization: 85,
    overall: 92,
  }

  const analysisSteps = [
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
            {getStatusBadge(analysisStatus)}
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
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview" className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Overview
                </TabsTrigger>
                <TabsTrigger value="topics" className="flex items-center gap-2">
                  <Brain className="w-4 h-4" />
                  Topics
                </TabsTrigger>
                <TabsTrigger value="sentiment" className="flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Sentiment
                </TabsTrigger>
                <TabsTrigger value="summary" className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Summary
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="p-6">
              <TabsContent value="overview" className="mt-0">
                <AnalysisOverview />
              </TabsContent>

              <TabsContent value="topics" className="mt-0">
                <TopicModelingResults />
              </TabsContent>

              <TabsContent value="sentiment" className="mt-0">
                <SentimentAnalysisResults />
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
