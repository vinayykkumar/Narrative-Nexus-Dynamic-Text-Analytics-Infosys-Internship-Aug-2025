"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { MetricsDashboard } from "@/components/visualizations/metrics-dashboard"
import { FileText, MessageSquare, TrendingUp, Clock, BarChart3, Brain, Target } from "lucide-react"

export function AnalysisOverview() {
  const keyMetrics = [
    {
      title: "Total Words",
      value: "12,847",
      change: "+2.3%",
      changeType: "increase" as const,
      icon: FileText,
      color: "#3b82f6",
      description: "Content volume",
    },
    {
      title: "Sentences",
      value: "1,234",
      change: "+1.8%",
      changeType: "increase" as const,
      icon: MessageSquare,
      color: "#10b981",
      description: "Text segments",
    },
    {
      title: "Avg Sentiment",
      value: "0.72",
      change: "+0.15",
      changeType: "increase" as const,
      progress: 72,
      icon: TrendingUp,
      color: "#8b5cf6",
      description: "Positive tone",
    },
    {
      title: "Topics Found",
      value: "8",
      change: "optimal",
      changeType: "neutral" as const,
      icon: Brain,
      color: "#f59e0b",
      description: "Well-structured",
    },
  ]

  const analysisInsights = [
    {
      type: "Topic Distribution",
      description: "Technology and Innovation themes dominate 34% of content",
      confidence: 92,
      priority: "high",
    },
    {
      type: "Sentiment Pattern",
      description: "Overall positive sentiment with 72% positive mentions",
      confidence: 88,
      priority: "medium",
    },
    {
      type: "Key Themes",
      description: "Customer satisfaction and product quality are recurring themes",
      confidence: 85,
      priority: "high",
    },
    {
      type: "Content Structure",
      description: "Well-structured content with clear topic transitions",
      confidence: 79,
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
                <span className="text-sm text-muted-foreground">92%</span>
              </div>
              <Progress value={92} className="h-2" />
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Data Quality Score</span>
                <Badge variant="secondary">Excellent</Badge>
              </div>
              <Progress value={88} className="h-2" />
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Topic Coherence</span>
                <span className="text-sm text-muted-foreground">0.85</span>
              </div>
              <Progress value={85} className="h-2" />
            </div>

            <div className="pt-4 border-t border-border">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="w-4 h-4" />
                Analysis completed in 2m 34s
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
              {analysisInsights.map((insight, index) => (
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
                Dive deeper into the 8 identified topics to understand content themes
              </p>
            </div>
            <div className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors cursor-pointer">
              <h4 className="font-medium mb-2">Analyze Sentiment Trends</h4>
              <p className="text-sm text-muted-foreground">
                Review sentiment patterns and identify areas for improvement
              </p>
            </div>
            <div className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors cursor-pointer">
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
