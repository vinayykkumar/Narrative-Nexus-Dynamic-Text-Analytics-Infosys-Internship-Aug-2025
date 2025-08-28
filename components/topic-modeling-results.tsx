"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { TopicDistributionChart } from "@/components/visualizations/topic-distribution-chart"
import { WordCloud } from "@/components/visualizations/word-cloud"
import { MetricsDashboard } from "@/components/visualizations/metrics-dashboard"
import { Brain, TrendingUp, Eye, MoreHorizontal, FileText, Target } from "lucide-react"

export function TopicModelingResults() {
  const topics = [
    {
      id: 1,
      name: "Technology & Innovation",
      prevalence: 34,
      keywords: ["technology", "innovation", "digital", "AI", "automation", "future"],
      coherence: 0.92,
      documents: 156,
      sentiment: "positive",
    },
    {
      id: 2,
      name: "Customer Experience",
      prevalence: 28,
      keywords: ["customer", "service", "experience", "satisfaction", "support", "quality"],
      coherence: 0.88,
      documents: 134,
      sentiment: "positive",
    },
    {
      id: 3,
      name: "Business Strategy",
      prevalence: 18,
      keywords: ["strategy", "business", "growth", "market", "competitive", "planning"],
      coherence: 0.85,
      documents: 89,
      sentiment: "neutral",
    },
    {
      id: 4,
      name: "Product Development",
      prevalence: 12,
      keywords: ["product", "development", "features", "design", "user", "interface"],
      coherence: 0.81,
      documents: 67,
      sentiment: "positive",
    },
    {
      id: 5,
      name: "Financial Performance",
      prevalence: 8,
      keywords: ["revenue", "profit", "cost", "budget", "financial", "investment"],
      coherence: 0.79,
      documents: 45,
      sentiment: "neutral",
    },
  ]

  const topicChartData = topics.map((topic, index) => ({
    name: topic.name,
    value: topic.prevalence,
    documents: topic.documents,
    color: `hsl(${index * 60}, 70%, 50%)`,
    keywords: topic.keywords,
  }))

  const wordCloudData = topics
    .flatMap((topic) =>
      topic.keywords.map((keyword) => ({
        text: keyword,
        value: Math.floor(Math.random() * 50) + 10, // Simulated frequency
      })),
    )
    .sort((a, b) => b.value - a.value)

  const metricsData = [
    {
      title: "Total Topics",
      value: topics.length,
      change: "Optimal range",
      changeType: "neutral" as const,
      icon: Brain,
      color: "#6366f1",
      description: "Well-structured content",
    },
    {
      title: "Avg Coherence",
      value: "0.85",
      change: "+0.05",
      changeType: "increase" as const,
      progress: 85,
      icon: TrendingUp,
      color: "#10b981",
      description: "Good quality topics",
    },
    {
      title: "Coverage",
      value: "100%",
      change: "Complete",
      changeType: "neutral" as const,
      progress: 100,
      icon: Target,
      color: "#3b82f6",
      description: "All docs classified",
    },
    {
      title: "Documents",
      value: "491",
      change: "+23",
      changeType: "increase" as const,
      icon: FileText,
      color: "#f59e0b",
      description: "Total analyzed",
    },
  ]

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "text-green-600 bg-green-50"
      case "negative":
        return "text-red-600 bg-red-50"
      case "neutral":
        return "text-gray-600 bg-gray-50"
      default:
        return "text-gray-600 bg-gray-50"
    }
  }

  const getCoherenceLevel = (score: number) => {
    if (score >= 0.9) return { label: "Excellent", color: "bg-green-500" }
    if (score >= 0.8) return { label: "Good", color: "bg-blue-500" }
    if (score >= 0.7) return { label: "Fair", color: "bg-yellow-500" }
    return { label: "Poor", color: "bg-red-500" }
  }

  return (
    <div className="space-y-6">
      <MetricsDashboard
        metrics={metricsData}
        title="Topic Analysis Overview"
        description="Key performance indicators for topic modeling results"
      />

      <TopicDistributionChart
        data={topicChartData}
        title="Topic Distribution"
        description="Visual representation of topic prevalence in your content"
      />

      <WordCloud
        words={wordCloudData}
        title="Key Terms"
        description="Most frequently mentioned words across all topics"
        maxWords={30}
      />

      {/* Topic Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Detailed Topic Analysis
          </CardTitle>
          <CardDescription>Comprehensive breakdown of identified topics and their characteristics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topics.map((topic) => {
              const coherence = getCoherenceLevel(topic.coherence)
              return (
                <div key={topic.id} className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-serif font-semibold">{topic.name}</h3>
                        <Badge className={getSentimentColor(topic.sentiment)}>{topic.sentiment}</Badge>
                        <Badge variant="outline" className="text-xs">
                          {topic.documents} docs
                        </Badge>
                      </div>

                      <div className="flex items-center gap-4 mb-3">
                        <div className="flex-1">
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-sm font-medium">Prevalence</span>
                            <span className="text-sm text-muted-foreground">{topic.prevalence}%</span>
                          </div>
                          <Progress value={topic.prevalence} className="h-2" />
                        </div>

                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">Coherence:</span>
                          <Badge className={`${coherence.color} text-white text-xs`}>{coherence.label}</Badge>
                          <span className="text-sm text-muted-foreground">({topic.coherence})</span>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        {topic.keywords.map((keyword, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4 mr-2" />
                        View Details
                      </Button>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Topic Relationships */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif">Topic Relationships</CardTitle>
          <CardDescription>How topics relate to each other in your content</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-muted-foreground">
            <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Topic relationship visualization will be displayed here</p>
            <p className="text-sm">Interactive network graph showing topic connections</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
