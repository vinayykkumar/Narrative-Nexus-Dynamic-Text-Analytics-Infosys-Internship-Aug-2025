"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { MetricsDashboard } from "@/components/visualizations/metrics-dashboard"
import { FileText, MessageSquare, BarChart3, Brain, Target } from "lucide-react"
import { useRouter } from "next/navigation"

interface AnalysisOverviewProps {
  dashboardData?: any
  reportData?: any
  sessionId?: string | null
}

export function AnalysisOverview({ dashboardData, reportData, sessionId }: AnalysisOverviewProps) {
  const router = useRouter()
  // Load structured results from localStorage as a fallback
  const [localResults, setLocalResults] = useState<any | null>(null)
  useEffect(() => {
    try {
      const raw = typeof window !== 'undefined' ? localStorage.getItem('analysisResults') : null
      if (raw) setLocalResults(JSON.parse(raw))
    } catch {}
  }, [])

  // Extract real data if available (prefer dashboard, else local)
  const sentimentData = dashboardData?.charts_data?.analysis_results?.find((r: any) => r.analysis_type === 'sentiment')?.results
    || localResults?.sentiment_results
  const topicData = dashboardData?.charts_data?.analysis_results?.find((r: any) => r.analysis_type === 'topic_modeling')?.results
    || localResults?.topic_modeling_results
  const insights = dashboardData?.charts_data?.insights?.[0]

  // Derived metrics from available data
  const totalTexts: number = dashboardData?.overview?.total_texts_processed
    || localResults?.sentiment_results?.summary?.total_sentences
    || 1
  const overallSentiment: string = sentimentData?.overall_sentiment || 'Neutral'
  const overallConfidencePct: number | undefined =
    typeof sentimentData?.overall_confidence === 'number'
      ? sentimentData.overall_confidence * 100
      : undefined
  const dist = sentimentData?.sentiment_distribution as { positive?: number; negative?: number; neutral?: number } | undefined
  const topSentimentEntry = dist
    ? (Object.entries(dist) as Array<[string, number]>).sort((a, b) => b[1] - a[1])[0]
    : undefined

  // Metrics card values (no dummy data)
  const keyMetrics = [
    {
      title: "Total Texts",
      value: String(totalTexts),
      icon: FileText,
      color: "#3b82f6",
      description: "Texts analyzed",
    },
    {
      title: "Sentiment Confidence",
      value: overallConfidencePct != null ? `${overallConfidencePct.toFixed(1)}%` : "–",
      icon: MessageSquare,
      color: "#10b981",
      description: `Overall: ${overallSentiment}`,
    },
    {
      title: "Topics Found",
      value: topicData?.num_topics != null ? String(topicData.num_topics) : "–",
      icon: Brain,
      color: "#f59e0b",
      description: "Main themes",
    },
    {
      title: "Top Sentiment",
      value: topSentimentEntry ? `${topSentimentEntry[0].toUpperCase()} ${(topSentimentEntry[1] * 100).toFixed(1)}%` : "–",
      icon: Target,
      color: "#8b5cf6",
      description: dist ? `P ${(Math.round((dist.positive || 0) * 100))}% / N ${(Math.round((dist.negative || 0) * 100))}% / Neu ${(Math.round((dist.neutral || 0) * 100))}%` : undefined,
    },
  ]

  // Insights block: prefer dashboard insights; otherwise synthesize simple ones from results
  const analysisInsights = insights?.key_insights
    ? insights.key_insights.map((insight: any) => ({
        type: insight.category || insight.type || "Analysis",
        description: insight.description || insight.title || "No description available",
        confidence: Math.round((insight.confidence || 0.8) * 100),
        priority: insight.impact === "high" ? "high" : insight.impact === "medium" ? "medium" : "low",
      }))
    : [
        {
          type: "Sentiment",
          description: `Overall ${overallSentiment} with ${(overallConfidencePct ?? 0).toFixed(1)}% confidence`,
          confidence: Math.round(overallConfidencePct ?? 0),
          priority: "medium",
        },
        {
          type: "Topics",
          description: topicData?.num_topics ? `Identified ${topicData.num_topics} main topics` : "Topics identified",
          confidence: 80,
          priority: "low",
        },
      ]

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-500"
      case "medium":
        return "bg-yellow-500"
      case "low":
        return "bg-green-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <div className="space-y-6">
      <MetricsDashboard
        metrics={keyMetrics}
        title="Content Analysis Metrics"
        description="Key statistics from your text analysis"
      />

      {/* Analysis Summary */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="font-serif flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Analysis Summary
            </CardTitle>
            <CardDescription>High-level overview of your text analysis results</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Processing Completion</span>
                <span className="text-sm text-muted-foreground">{(sentimentData || topicData) ? '100%' : '0%'}</span>
              </div>
              <Progress value={(sentimentData || topicData) ? 100 : 0} className="h-2" />
            </div>

            {overallConfidencePct != null && (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Data Quality (Confidence)</span>
                  <Badge variant="secondary">{overallConfidencePct.toFixed(1)}%</Badge>
                </div>
                <Progress value={overallConfidencePct} className="h-2" />
              </div>
            )}

            <div className="pt-4 border-t border-border">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                Analysis completed
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-serif flex items-center gap-2">
              <Target className="w-5 h-5" />
              Key Insights
            </CardTitle>
            <CardDescription>Important findings and recommendations from your analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analysisInsights.map((insight: any, index: number) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-muted/30 rounded-lg">
                  <div className={`w-2 h-2 rounded-full mt-2 ${getPriorityColor(insight.priority)}`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium text-sm">{insight.type}</h4>
                      <Badge variant="outline" className="text-xs">
                        {insight.confidence}% confidence
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{insight.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif">Recommended Actions</CardTitle>
          <CardDescription>Based on your analysis results, here are some suggested next steps</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors cursor-pointer">
              <h4 className="font-medium mb-2">Explore Topic Details</h4>
              <p className="text-sm text-muted-foreground">
                Dive deeper into the {topicData?.num_topics ?? 'identified'} topics to understand content themes
              </p>
            </div>
            <div className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors cursor-pointer">
              <h4 className="font-medium mb-2">Analyze Sentiment Trends</h4>
              <p className="text-sm text-muted-foreground">
                Review sentiment patterns and identify areas for improvement
              </p>
            </div>
            <div
              className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors cursor-pointer"
              onClick={() => router.push('/reports/analysis')}
            >
              <h4 className="font-medium mb-2">Generate Report</h4>
              <p className="text-sm text-muted-foreground">
                Create a comprehensive report with all findings and insights
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
