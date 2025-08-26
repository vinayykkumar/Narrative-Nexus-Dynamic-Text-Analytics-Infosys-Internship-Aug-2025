"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { FileText, Copy, Download, Edit, Sparkles } from "lucide-react"

export function TextSummaryResults() {
  const summaries = [
    {
      type: "Executive Summary",
      length: "short",
      content:
        "The analysis reveals a predominantly positive sentiment across technology and customer experience topics, with 72% positive mentions. Key themes include innovation, digital transformation, and customer satisfaction, indicating strong market positioning and growth potential.",
      wordCount: 35,
      readingTime: "15 seconds",
    },
    {
      type: "Detailed Summary",
      length: "medium",
      content:
        "This comprehensive text analysis identifies eight distinct topics with technology and innovation leading at 34% prevalence. Customer experience follows at 28%, showing strong positive sentiment (78% positive mentions). Business strategy discussions maintain neutral sentiment, while product development shows promising positive trends. The analysis suggests focusing on technology advancement and customer satisfaction as key growth drivers, while addressing concerns in financial performance discussions.",
      wordCount: 68,
      readingTime: "30 seconds",
    },
    {
      type: "Key Points",
      length: "bullets",
      content:
        "• Technology & Innovation dominates content (34% prevalence)\n• Overall positive sentiment at 72% with high confidence (88%)\n• Customer experience shows strong satisfaction indicators\n• Business strategy discussions remain neutral, requiring attention\n• Product development trending positively\n• Financial performance topics show mixed sentiment patterns",
      wordCount: 45,
      readingTime: "20 seconds",
    },
  ]

  const keyExtracts = [
    {
      topic: "Technology & Innovation",
      extract:
        "The integration of AI and automation technologies has revolutionized our approach to digital transformation, creating unprecedented opportunities for innovation and growth.",
      relevance: 95,
      sentiment: "positive",
    },
    {
      topic: "Customer Experience",
      extract:
        "Customer satisfaction scores have consistently improved, with feedback highlighting the quality of service and responsiveness of our support team.",
      relevance: 92,
      sentiment: "positive",
    },
    {
      topic: "Business Strategy",
      extract:
        "Market analysis indicates competitive pressures require strategic repositioning and careful resource allocation to maintain growth trajectory.",
      relevance: 88,
      sentiment: "neutral",
    },
  ]

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "text-green-600 bg-green-50"
      case "negative":
        return "text-red-600 bg-red-50"
      default:
        return "text-gray-600 bg-gray-50"
    }
  }

  const getLengthBadgeColor = (length: string) => {
    switch (length) {
      case "short":
        return "bg-green-500"
      case "medium":
        return "bg-blue-500"
      case "bullets":
        return "bg-purple-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <div className="space-y-6">
      {/* Generated Summaries */}
      <div className="space-y-4">
        {summaries.map((summary, index) => (
          <Card key={index}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <CardTitle className="font-serif flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    {summary.type}
                  </CardTitle>
                  <Badge className={`${getLengthBadgeColor(summary.length)} text-white text-xs`}>
                    {summary.length}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    <Copy className="w-4 h-4 mr-2" />
                    Copy
                  </Button>
                  <Button variant="outline" size="sm">
                    <Edit className="w-4 h-4 mr-2" />
                    Edit
                  </Button>
                </div>
              </div>
              <CardDescription>
                {summary.wordCount} words • {summary.readingTime} reading time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Textarea value={summary.content} readOnly className="min-h-[120px] resize-none bg-muted/30" />
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>Generated using extractive and abstractive techniques</span>
                  <Button variant="ghost" size="sm">
                    <Sparkles className="w-4 h-4 mr-2" />
                    Regenerate
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Key Extracts */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif">Key Extracts</CardTitle>
          <CardDescription>Most relevant sentences and phrases from your content</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {keyExtracts.map((extract, index) => (
              <div key={index} className="p-4 border border-border rounded-lg">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <h4 className="font-medium">{extract.topic}</h4>
                    <Badge className={getSentimentColor(extract.sentiment)}>{extract.sentiment}</Badge>
                    <Badge variant="outline" className="text-xs">
                      {extract.relevance}% relevance
                    </Badge>
                  </div>
                  <Button variant="outline" size="sm">
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
                <blockquote className="text-sm italic text-muted-foreground border-l-4 border-secondary pl-4">
                  "{extract.extract}"
                </blockquote>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Summary Statistics */}
      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Compression Ratio</p>
                <p className="text-2xl font-bold">15:1</p>
                <p className="text-xs text-muted-foreground mt-1">Original to summary</p>
              </div>
              <div className="p-2 rounded-lg bg-blue-100">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Key Points</p>
                <p className="text-2xl font-bold">12</p>
                <p className="text-xs text-muted-foreground mt-1">Main concepts</p>
              </div>
              <div className="p-2 rounded-lg bg-green-100">
                <Sparkles className="w-5 h-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Quality Score</p>
                <p className="text-2xl font-bold">8.7/10</p>
                <p className="text-xs text-muted-foreground mt-1">Summary quality</p>
              </div>
              <div className="p-2 rounded-lg bg-purple-100">
                <Download className="w-5 h-5 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
