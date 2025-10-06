"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Settings, Brain, BarChart3, FileText } from "lucide-react"

export function AnalysisOptions() {
  const [selectedAnalyses, setSelectedAnalyses] = useState(() => {
    // Initialize from localStorage to persist across navigation
    if (typeof window !== 'undefined') {
      try {
        const raw = localStorage.getItem('analysisSelectedAnalyses')
        if (raw) return JSON.parse(raw)
      } catch {}
    }
    return {
      topicModeling: true,
      sentimentAnalysis: true,
      summarization: true,
    }
  })

  const [topicCount, setTopicCount] = useState<number[]>(() => {
    if (typeof window !== 'undefined') {
      const raw = localStorage.getItem('analysisTopicCount')
      if (raw) return [Number(raw) || 5]
    }
    return [5]
  })
  const [summaryLength, setSummaryLength] = useState(() => {
    if (typeof window !== 'undefined') {
      const raw = localStorage.getItem('analysisSummaryLength')
      if (raw) return raw
    }
    return "medium"
  })

  const analysisTypes = [
    {
      id: "topicModeling",
      name: "Topic Modeling",
      description: "Extract key themes using LDA/NMF algorithms",
      icon: Brain,
      recommended: true,
    },
    {
      id: "sentimentAnalysis",
      name: "Sentiment Analysis",
      description: "Analyze emotional tone and sentiment patterns",
      icon: BarChart3,
      recommended: true,
    },
    {
      id: "summarization",
      name: "Text Summarization",
      description: "Generate concise summaries of your content",
      icon: FileText,
      recommended: true,
    },
  ]

  const handleAnalysisToggle = (analysisId: string, checked: boolean) => {
    setSelectedAnalyses((prev: { topicModeling: boolean; sentimentAnalysis: boolean; summarization: boolean }) => {
      const next = { ...prev, [analysisId]: checked } as typeof prev
      try { localStorage.setItem('analysisSelectedAnalyses', JSON.stringify(next)) } catch {}
      return next
    })
  }

  // Persist topic count changes
  const onTopicCountChange = (value: number[]) => {
    setTopicCount(value)
    try { localStorage.setItem('analysisTopicCount', String(value[0])) } catch {}
  }

  // Persist summary length changes
  const onSummaryLengthChange = (value: string) => {
    setSummaryLength(value)
    try { localStorage.setItem('analysisSummaryLength', value) } catch {}
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-serif flex items-center gap-2">
          <Settings className="w-5 h-5" />
          Analysis Options
        </CardTitle>
        <CardDescription>Configure which analyses to perform on your text data</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <h4 className="font-serif font-semibold">Analysis Types</h4>
          <div className="grid gap-4">
            {analysisTypes.map((analysis) => {
              const Icon = analysis.icon
              const isSelected = selectedAnalyses[analysis.id as keyof typeof selectedAnalyses]

              return (
                <div key={analysis.id} className="flex items-start space-x-3 p-3 rounded-lg border border-border">
                  <Checkbox
                    id={analysis.id}
                    checked={isSelected}
                    onCheckedChange={(checked) => handleAnalysisToggle(analysis.id, checked as boolean)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Icon className="w-4 h-4 text-secondary" />
                      <Label htmlFor={analysis.id} className="font-medium cursor-pointer">
                        {analysis.name}
                      </Label>
                      {analysis.recommended && (
                        <Badge variant="secondary" className="text-xs">
                          Recommended
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{analysis.description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {selectedAnalyses.topicModeling && (
          <div className="space-y-3">
            <h4 className="font-serif font-semibold">Topic Modeling Settings</h4>
            <div className="space-y-2">
              <Label>Number of Topics: {topicCount[0]}</Label>
              <Slider value={topicCount} onValueChange={onTopicCountChange} max={20} min={2} step={1} className="w-full" />
              <p className="text-xs text-muted-foreground">
                Higher values may reveal more specific themes but could be less coherent
              </p>
            </div>
          </div>
        )}

        {selectedAnalyses.summarization && (
          <div className="space-y-3">
            <h4 className="font-serif font-semibold">Summarization Settings</h4>
            <div className="space-y-2">
              <Label>Summary Length</Label>
              <Select value={summaryLength} onValueChange={onSummaryLengthChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="short">Short (1-2 sentences)</SelectItem>
                  <SelectItem value="medium">Medium (3-5 sentences)</SelectItem>
                  <SelectItem value="long">Long (6-10 sentences)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
