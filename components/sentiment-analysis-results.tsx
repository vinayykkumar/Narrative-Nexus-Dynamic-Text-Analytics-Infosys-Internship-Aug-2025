"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { SentimentChart } from "@/components/visualizations/sentiment-chart"
import { MetricsDashboard } from "@/components/visualizations/metrics-dashboard"
import { BarChart3, TrendingUp, TrendingDown, Minus, Eye } from "lucide-react"

export function SentimentAnalysisResults() {
  const sentimentOverview = {
    positive: 72,
    neutral: 18,
    negative: 10,
    averageScore: 0.72,
    confidence: 88,
  }

  const sentimentByTopic = [
    {
      topic: "Technology & Innovation",
      positive: 85,
      neutral: 12,
      negative: 3,
      score: 0.91,
      trend: "up",
    },
    {
      topic: "Customer Experience",
      positive: 78,
      neutral: 15,
      negative: 7,
      score: 0.86,
      trend: "up",
    },
    {
      topic: "Business Strategy",
      positive: 45,
      neutral: 35,
      negative: 20,
      score: 0.25,
      trend: "stable",
    },
    {
      topic: "Product Development",
      positive: 68,
      neutral: 22,
      negative: 10,
      score: 0.58,
      trend: "up",
    },
    {
      topic: "Financial Performance",
      positive: 35,
      neutral: 40,
      negative: 25,
      score: 0.1,
      trend: "down",
    },
  ]

  const sentimentChartData = sentimentByTopic.map((item) => ({
    name: item.topic,
    positive: item.positive,
    neutral: item.neutral,
    negative: item.negative,
    score: item.score,
  }))

  const timelineData = [
    { time: "Week 1", sentiment: 0.65, volume: 120 },
    { time: "Week 2", sentiment: 0.72, volume: 145 },
    { time: "Week 3", sentiment: 0.68, volume: 132 },
    { time: "Week 4", sentiment: 0.75, volume: 158 },
    { time: "Week 5", sentiment: 0.72, volume: 142 },
  ]

  const metricsData = [
    {
      title: "Positive",
      value: `${sentimentOverview.positive}%`,
      change: "+5%",
      changeType: "increase" as const,
      progress: sentimentOverview.positive,
      icon: TrendingUp,
      color: "#10b981",
      description: "Above average",
    },
    {
      title: "Neutral",
      value: `${sentimentOverview.neutral}%`,
      change: "Stable",
      changeType: "neutral" as const,
      progress: sentimentOverview.neutral,
      icon: Minus,
      color: "#6b7280",
      description: "Balanced tone",
    },
    {
      title: "Negative",
      value: `${sentimentOverview.negative}%`,
      change: "-2%",
      changeType: "decrease" as const,
      progress: sentimentOverview.negative,
      icon: TrendingDown,
      color: "#ef4444",
      description: "Improving trend",
    },
    {
      title: "Avg Score",
      value: sentimentOverview.averageScore,
      change: "+0.08",
      changeType: "increase" as const,
      progress: sentimentOverview.confidence,
      icon: BarChart3,
      color: "#6366f1",
      description: `${sentimentOverview.confidence}% confidence`,
    },
  ]

  const keyInsights = [
    {
      type: "Positive Driver",
      description: "Technology and innovation topics show consistently high positive sentiment",
      impact: "high",
      sentiment: "positive",
    },
    {
      type: "Concern Area",
      description: "Financial performance discussions tend to be more neutral or negative",
      impact: "medium",
      sentiment: "negative",
    },
    {
      type: "Opportunity",
      description: "Customer experience sentiment is strong but has room for improvement",
      impact: "medium",
      sentiment: "positive",
    },
  ]

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="w-4 h-4 text-green-500" />
      case "down":
        return <TrendingDown className="w-4 h-4 text-red-500" />
      default:
        return <Minus className="w-4 h-4 text-gray-500" />
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "text-green-600 bg-green-50 border-green-200"
      case "negative":
        return "text-red-600 bg-red-50 border-red-200"
      default:
        return "text-blue-600 bg-blue-50 border-blue-200"
    }
  }

  return (
    <div className="space-y-6">
      <MetricsDashboard
        metrics={metricsData}
        title="Sentiment Overview"
        description="Key sentiment indicators across your content"
      />

      <SentimentChart
        data={sentimentChartData}
        timeData={timelineData}
        title="Sentiment Analysis"
        description="Detailed sentiment breakdown by topic with timeline view"
        showTimeline={true}
      />

      {/* Sentiment by Topic */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Detailed Sentiment by Topic
          </CardTitle>
          <CardDescription>How sentiment varies across different topics in your content</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sentimentByTopic.map((item, index) => (
              <div key={index} className="p-4 border border-border rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <h3 className="font-serif font-semibold">{item.topic}</h3>
                    {getTrendIcon(item.trend)}
                    <Badge variant="outline" className="text-xs">
                      Score: {item.score}
                    </Badge>
                  </div>
                  <Button variant="outline" size="sm">
                    <Eye className="w-4 h-4 mr-2" />
                    Details
                  </Button>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-green-600">Positive</span>
                      <span className="text-sm text-muted-foreground">{item.positive}%</span>
                    </div>
                    <Progress value={item.positive} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-600">Neutral</span>
                      <span className="text-sm text-muted-foreground">{item.neutral}%</span>
                    </div>
                    <Progress value={item.neutral} className="h-2" />
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-red-600">Negative</span>
                      <span className="text-sm text-muted-foreground">{item.negative}%</span>
                    </div>
                    <Progress value={item.negative} className="h-2" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Key Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif">Sentiment Insights</CardTitle>
          <CardDescription>Key findings and recommendations based on sentiment analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {keyInsights.map((insight, index) => (
              <div key={index} className={`p-4 border rounded-lg ${getSentimentColor(insight.sentiment)}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-medium">{insight.type}</h4>
                      <Badge variant="outline" className="text-xs">
                        {insight.impact} impact
                      </Badge>
                    </div>
                    <p className="text-sm">{insight.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
