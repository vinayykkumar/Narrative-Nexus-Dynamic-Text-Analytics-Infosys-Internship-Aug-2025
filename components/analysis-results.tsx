"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { InsightsPanel } from "@/components/insights-panel"
import { RecommendationsPanel } from "@/components/recommendations-panel"
import { KeyFindingsPanel } from "@/components/key-findings-panel"
import { ActionableInsights } from "@/components/actionable-insights"
import {
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Brain,
  BarChart3,
  FileText,
  Lightbulb,
  ArrowRight,
} from "lucide-react"

export function AnalysisResults() {
  const executiveSummary = {
    overallScore: 8.7,
    confidence: 92,
    keyThemes: 8,
    sentimentScore: 0.72,
    recommendations: 12,
    criticalInsights: 4,
  }

  const quickStats = [
    {
      label: "Overall Quality",
      value: "Excellent",
      score: 87,
      color: "text-green-600",
      icon: CheckCircle,
    },
    {
      label: "Sentiment Trend",
      value: "Positive",
      score: 72,
      color: "text-blue-600",
      icon: TrendingUp,
    },
    {
      label: "Topic Coherence",
      value: "High",
      score: 85,
      color: "text-purple-600",
      icon: Brain,
    },
    {
      label: "Action Items",
      value: "12 Found",
      score: 100,
      color: "text-orange-600",
      icon: Target,
    },
  ]

  const criticalFindings = [
    {
      type: "Opportunity",
      title: "Technology Leadership Position",
      description:
        "Strong positive sentiment (85%) around technology and innovation topics suggests market leadership potential.",
      impact: "High",
      urgency: "Medium",
      category: "Strategic",
    },
    {
      type: "Risk",
      title: "Financial Performance Concerns",
      description:
        "Mixed sentiment (35% positive) in financial discussions indicates potential investor relations challenges.",
      impact: "Medium",
      urgency: "High",
      category: "Financial",
    },
    {
      type: "Insight",
      title: "Customer Experience Excellence",
      description: "Consistently high satisfaction scores (78% positive) across customer experience topics.",
      impact: "High",
      urgency: "Low",
      category: "Customer",
    },
    {
      type: "Alert",
      title: "Business Strategy Clarity",
      description: "Neutral sentiment (45% positive) suggests need for clearer strategic communication.",
      impact: "Medium",
      urgency: "Medium",
      category: "Strategic",
    },
  ]

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "Opportunity":
        return <TrendingUp className="w-4 h-4 text-green-500" />
      case "Risk":
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      case "Insight":
        return <Lightbulb className="w-4 h-4 text-blue-500" />
      case "Alert":
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      default:
        return <Target className="w-4 h-4 text-gray-500" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "Opportunity":
        return "bg-green-50 border-green-200 text-green-800"
      case "Risk":
        return "bg-red-50 border-red-200 text-red-800"
      case "Insight":
        return "bg-blue-50 border-blue-200 text-blue-800"
      case "Alert":
        return "bg-yellow-50 border-yellow-200 text-yellow-800"
      default:
        return "bg-gray-50 border-gray-200 text-gray-800"
    }
  }

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case "High":
        return "bg-red-500"
      case "Medium":
        return "bg-yellow-500"
      case "Low":
        return "bg-green-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <div className="space-y-8">
      {/* Executive Summary */}
      <Card className="border-2 border-secondary/20">
        <CardHeader>
          <CardTitle className="font-serif text-2xl flex items-center gap-2">
            <Target className="w-6 h-6 text-secondary" />
            Executive Summary
          </CardTitle>
          <CardDescription className="text-base">
            High-level overview of your text analysis with key performance indicators
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-serif font-semibold mb-2">Overall Analysis Score</h3>
                  <div className="flex items-center gap-3">
                    <span className="text-3xl font-bold text-secondary">{executiveSummary.overallScore}/10</span>
                    <Badge className="bg-green-500 hover:bg-green-600">Excellent</Badge>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Confidence Level</p>
                  <p className="text-xl font-semibold">{executiveSummary.confidence}%</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-muted/30 rounded-lg">
                  <div className="text-xl font-bold text-secondary">{executiveSummary.keyThemes}</div>
                  <div className="text-sm text-muted-foreground">Key Themes</div>
                </div>
                <div className="text-center p-3 bg-muted/30 rounded-lg">
                  <div className="text-xl font-bold text-secondary">{executiveSummary.recommendations}</div>
                  <div className="text-sm text-muted-foreground">Recommendations</div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {quickStats.map((stat, index) => {
                const Icon = stat.icon
                return (
                  <div key={index} className="p-4 border border-border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <Icon className={`w-5 h-5 ${stat.color}`} />
                      <span className="text-sm font-medium">{stat.score}%</span>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-medium">{stat.label}</p>
                      <p className={`text-sm ${stat.color}`}>{stat.value}</p>
                    </div>
                    <Progress value={stat.score} className="h-1 mt-2" />
                  </div>
                )
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Critical Findings */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Critical Findings
          </CardTitle>
          <CardDescription>Most important insights requiring immediate attention or action</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {criticalFindings.map((finding, index) => (
              <div key={index} className={`p-4 border rounded-lg ${getTypeColor(finding.type)}`}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {getTypeIcon(finding.type)}
                    <div>
                      <h4 className="font-serif font-semibold">{finding.title}</h4>
                      <Badge variant="outline" className="text-xs mt-1">
                        {finding.category}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right text-xs">
                      <div className="flex items-center gap-1">
                        <span>Impact:</span>
                        <Badge variant="outline" className="text-xs">
                          {finding.impact}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-1 mt-1">
                        <span>Urgency:</span>
                        <div className={`w-2 h-2 rounded-full ${getUrgencyColor(finding.urgency)}`} />
                        <span>{finding.urgency}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <p className="text-sm mb-3">{finding.description}</p>
                <Button variant="outline" size="sm">
                  View Details
                  <ArrowRight className="w-3 h-3 ml-2" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Results Tabs */}
      <Card>
        <CardContent className="p-0">
          <Tabs defaultValue="insights" className="w-full">
            <div className="border-b border-border px-6 pt-6">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="insights" className="flex items-center gap-2">
                  <Lightbulb className="w-4 h-4" />
                  Key Insights
                </TabsTrigger>
                <TabsTrigger value="recommendations" className="flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Recommendations
                </TabsTrigger>
                <TabsTrigger value="findings" className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Detailed Findings
                </TabsTrigger>
                <TabsTrigger value="actions" className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Action Items
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="p-6">
              <TabsContent value="insights" className="mt-0">
                <InsightsPanel />
              </TabsContent>

              <TabsContent value="recommendations" className="mt-0">
                <RecommendationsPanel />
              </TabsContent>

              <TabsContent value="findings" className="mt-0">
                <KeyFindingsPanel />
              </TabsContent>

              <TabsContent value="actions" className="mt-0">
                <ActionableInsights />
              </TabsContent>
            </div>
          </Tabs>
        </CardContent>
      </Card>

      {/* Next Steps */}
      <Card className="border-2 border-secondary/20">
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <ArrowRight className="w-5 h-5 text-secondary" />
            Recommended Next Steps
          </CardTitle>
          <CardDescription>Prioritized actions based on your analysis results</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-6 bg-green-50 border border-green-200 rounded-lg">
              <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-serif font-semibold mb-2">Leverage Technology Leadership</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Capitalize on strong positive sentiment around innovation topics
              </p>
              <Button size="sm" className="bg-green-500 hover:bg-green-600">
                View Strategy
              </Button>
            </div>

            <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="w-12 h-12 bg-yellow-500 rounded-lg flex items-center justify-center mb-4">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-serif font-semibold mb-2">Address Financial Communication</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Improve messaging around financial performance and strategy
              </p>
              <Button size="sm" className="bg-yellow-500 hover:bg-yellow-600">
                View Plan
              </Button>
            </div>

            <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center mb-4">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-serif font-semibold mb-2">Generate Detailed Report</h3>
              <p className="text-sm text-muted-foreground mb-4">Create comprehensive documentation of all findings</p>
              <Button size="sm" className="bg-blue-500 hover:bg-blue-600">
                Create Report
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
