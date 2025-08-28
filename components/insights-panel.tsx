"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Lightbulb, TrendingUp, Users, DollarSign, Target, ArrowRight } from "lucide-react"

export function InsightsPanel() {
  const insights = [
    {
      category: "Market Position",
      title: "Technology Innovation Leadership",
      description:
        "Analysis reveals strong positive sentiment (85%) around technology and innovation topics, indicating market leadership potential and competitive advantage.",
      impact: "High",
      confidence: 92,
      metrics: {
        sentiment: 85,
        mentions: 234,
        reach: "34% of content",
      },
      icon: TrendingUp,
      color: "text-green-600",
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
    },
    {
      category: "Customer Relations",
      title: "Strong Customer Satisfaction Signals",
      description:
        "Customer experience topics show consistently high positive sentiment (78%), with particular strength in service quality and support responsiveness.",
      impact: "High",
      confidence: 88,
      metrics: {
        sentiment: 78,
        mentions: 189,
        reach: "28% of content",
      },
      icon: Users,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      borderColor: "border-blue-200",
    },
    {
      category: "Strategic Communication",
      title: "Business Strategy Clarity Gap",
      description:
        "Neutral sentiment (45%) in business strategy discussions suggests opportunities for clearer strategic messaging and vision communication.",
      impact: "Medium",
      confidence: 79,
      metrics: {
        sentiment: 45,
        mentions: 98,
        reach: "18% of content",
      },
      icon: Target,
      color: "text-yellow-600",
      bgColor: "bg-yellow-50",
      borderColor: "border-yellow-200",
    },
    {
      category: "Financial Performance",
      title: "Mixed Financial Sentiment Patterns",
      description:
        "Financial performance topics show mixed sentiment (35% positive), indicating potential concerns about financial communication and investor relations.",
      impact: "Medium",
      confidence: 85,
      metrics: {
        sentiment: 35,
        mentions: 67,
        reach: "8% of content",
      },
      icon: DollarSign,
      color: "text-red-600",
      bgColor: "bg-red-50",
      borderColor: "border-red-200",
    },
  ]

  const getImpactColor = (impact: string) => {
    switch (impact) {
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
    <div className="space-y-6">
      <div className="mb-6">
        <h3 className="text-lg font-serif font-semibold mb-2">Strategic Insights</h3>
        <p className="text-muted-foreground">
          Key insights derived from comprehensive analysis of your text data, ranked by potential impact and confidence
          level.
        </p>
      </div>

      <div className="grid gap-6">
        {insights.map((insight, index) => {
          const Icon = insight.icon
          return (
            <Card key={index} className={`${insight.bgColor} ${insight.borderColor} border-2`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white rounded-lg">
                      <Icon className={`w-5 h-5 ${insight.color}`} />
                    </div>
                    <div>
                      <Badge variant="outline" className="mb-2 text-xs">
                        {insight.category}
                      </Badge>
                      <CardTitle className="font-serif text-lg">{insight.title}</CardTitle>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right text-xs">
                      <div className="flex items-center gap-1">
                        <span>Impact:</span>
                        <div className={`w-2 h-2 rounded-full ${getImpactColor(insight.impact)}`} />
                        <span>{insight.impact}</span>
                      </div>
                      <div className="mt-1">
                        <span>Confidence: {insight.confidence}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base mb-4">{insight.description}</CardDescription>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="text-center p-3 bg-white/50 rounded-lg">
                    <div className="text-lg font-bold">{insight.metrics.sentiment}%</div>
                    <div className="text-xs text-muted-foreground">Sentiment</div>
                    <Progress value={insight.metrics.sentiment} className="h-1 mt-1" />
                  </div>
                  <div className="text-center p-3 bg-white/50 rounded-lg">
                    <div className="text-lg font-bold">{insight.metrics.mentions}</div>
                    <div className="text-xs text-muted-foreground">Mentions</div>
                  </div>
                  <div className="text-center p-3 bg-white/50 rounded-lg">
                    <div className="text-lg font-bold">{insight.metrics.reach}</div>
                    <div className="text-xs text-muted-foreground">Content Reach</div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <Badge className={`${getImpactColor(insight.impact)} text-white`}>{insight.impact} Impact</Badge>
                  <Button variant="outline" size="sm">
                    Deep Dive Analysis
                    <ArrowRight className="w-3 h-3 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Insight Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <Lightbulb className="w-5 h-5" />
            Insight Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium mb-3">Key Strengths</h4>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  Strong technology and innovation positioning
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  High customer satisfaction indicators
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  Clear market differentiation potential
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-3">Areas for Improvement</h4>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                  Strategic communication clarity
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                  Financial messaging optimization
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                  Investor relations enhancement
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
