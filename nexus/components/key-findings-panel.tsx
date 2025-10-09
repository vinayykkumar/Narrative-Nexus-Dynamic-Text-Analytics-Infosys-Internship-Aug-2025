"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BarChart3, Brain, MessageSquare, TrendingUp, Target, Eye } from "lucide-react"

export function KeyFindingsPanel() {
  const topicFindings = [
    {
      topic: "Technology & Innovation",
      prevalence: 34,
      sentiment: 85,
      keyWords: ["AI", "automation", "digital", "innovation", "future"],
      insights: "Strongest positive sentiment indicates market leadership potential",
      documents: 156,
      trend: "increasing",
    },
    {
      topic: "Customer Experience",
      prevalence: 28,
      sentiment: 78,
      keyWords: ["customer", "service", "satisfaction", "support", "quality"],
      insights: "High satisfaction scores with room for improvement in response time",
      documents: 134,
      trend: "stable",
    },
    {
      topic: "Business Strategy",
      prevalence: 18,
      sentiment: 45,
      keyWords: ["strategy", "growth", "market", "competitive", "planning"],
      insights: "Neutral sentiment suggests need for clearer strategic communication",
      documents: 89,
      trend: "declining",
    },
    {
      topic: "Product Development",
      prevalence: 12,
      sentiment: 68,
      keyWords: ["product", "features", "design", "user", "development"],
      insights: "Positive reception of new features and development approach",
      documents: 67,
      trend: "increasing",
    },
    {
      topic: "Financial Performance",
      prevalence: 8,
      sentiment: 35,
      keyWords: ["revenue", "profit", "financial", "investment", "cost"],
      insights: "Mixed sentiment indicates investor relations challenges",
      documents: 45,
      trend: "declining",
    },
  ]

  const sentimentFindings = [
    {
      category: "Overall Sentiment",
      positive: 72,
      neutral: 18,
      negative: 10,
      score: 0.72,
      confidence: 92,
      trend: "improving",
    },
    {
      category: "Topic-Specific",
      positive: 65,
      neutral: 25,
      negative: 10,
      score: 0.68,
      confidence: 88,
      trend: "stable",
    },
    {
      category: "Temporal Trends",
      positive: 75,
      neutral: 15,
      negative: 10,
      score: 0.75,
      confidence: 85,
      trend: "improving",
    },
  ]

  const contentFindings = [
    {
      metric: "Total Documents",
      value: "491",
      change: "+23",
      description: "Documents analyzed in this session",
    },
    {
      metric: "Word Count",
      value: "12,847",
      change: "+2.3%",
      description: "Total words processed",
    },
    {
      metric: "Unique Terms",
      value: "2,156",
      change: "+156",
      description: "Distinct terms identified",
    },
    {
      metric: "Processing Time",
      value: "2m 34s",
      change: "-15s",
      description: "Analysis completion time",
    },
  ]

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "increasing":
        return <TrendingUp className="w-4 h-4 text-green-500" />
      case "declining":
        return <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />
      default:
        return <Target className="w-4 h-4 text-gray-500" />
    }
  }

  const getSentimentColor = (sentiment: number) => {
    if (sentiment >= 70) return "text-green-600"
    if (sentiment >= 50) return "text-yellow-600"
    return "text-red-600"
  }

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h3 className="text-lg font-serif font-semibold mb-2">Detailed Analysis Findings</h3>
        <p className="text-muted-foreground">
          Comprehensive breakdown of all analysis results with detailed metrics and supporting data.
        </p>
      </div>

      <Tabs defaultValue="topics" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="topics">Topic Analysis</TabsTrigger>
          <TabsTrigger value="sentiment">Sentiment Analysis</TabsTrigger>
          <TabsTrigger value="content">Content Metrics</TabsTrigger>
        </TabsList>

        <TabsContent value="topics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="font-serif flex items-center gap-2">
                <Brain className="w-5 h-5" />
                Topic Distribution Analysis
              </CardTitle>
              <CardDescription>
                Detailed breakdown of identified topics with prevalence and sentiment metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {topicFindings.map((topic, index) => (
                  <div key={index} className="p-4 border border-border rounded-lg">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-serif font-semibold">{topic.topic}</h4>
                          {getTrendIcon(topic.trend)}
                          <Badge variant="outline" className="text-xs">
                            {topic.documents} docs
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">{topic.insights}</p>
                      </div>
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4 mr-2" />
                        Details
                      </Button>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium">Prevalence</span>
                          <span className="text-sm text-muted-foreground">{topic.prevalence}%</span>
                        </div>
                        <Progress value={topic.prevalence} className="h-2" />
                      </div>
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium">Sentiment</span>
                          <span className={`text-sm font-medium ${getSentimentColor(topic.sentiment)}`}>
                            {topic.sentiment}%
                          </span>
                        </div>
                        <Progress value={topic.sentiment} className="h-2" />
                      </div>
                    </div>

                    <div>
                      <span className="text-sm font-medium mb-2 block">Key Terms:</span>
                      <div className="flex flex-wrap gap-2">
                        {topic.keyWords.map((word, wordIndex) => (
                          <Badge key={wordIndex} variant="secondary" className="text-xs">
                            {word}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sentiment" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="font-serif flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Sentiment Analysis Results
              </CardTitle>
              <CardDescription>Comprehensive sentiment metrics across different analysis dimensions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {sentimentFindings.map((finding, index) => (
                  <div key={index} className="p-4 border border-border rounded-lg">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-serif font-semibold">{finding.category}</h4>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {finding.confidence}% confidence
                        </Badge>
                        <Badge className={finding.trend === "improving" ? "bg-green-500" : "bg-gray-500"}>
                          {finding.trend}
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-4 gap-4 mb-4">
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="text-lg font-bold text-green-600">{finding.positive}%</div>
                        <div className="text-xs text-green-700">Positive</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className="text-lg font-bold text-gray-600">{finding.neutral}%</div>
                        <div className="text-xs text-gray-700">Neutral</div>
                      </div>
                      <div className="text-center p-3 bg-red-50 rounded-lg">
                        <div className="text-lg font-bold text-red-600">{finding.negative}%</div>
                        <div className="text-xs text-red-700">Negative</div>
                      </div>
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <div className="text-lg font-bold text-blue-600">{finding.score}</div>
                        <div className="text-xs text-blue-700">Score</div>
                      </div>
                    </div>

                    <Progress value={finding.positive} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="content" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="font-serif flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                Content Analysis Metrics
              </CardTitle>
              <CardDescription>Statistical overview of processed content and analysis performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {contentFindings.map((finding, index) => (
                  <div key={index} className="p-4 border border-border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{finding.metric}</h4>
                      <Badge variant="outline" className="text-xs">
                        {finding.change}
                      </Badge>
                    </div>
                    <div className="text-2xl font-bold text-secondary mb-1">{finding.value}</div>
                    <p className="text-sm text-muted-foreground">{finding.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
