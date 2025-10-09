"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Brain, Target } from "lucide-react"
import { useState } from "react"

interface TopicModelingResultsProps {
  results?: {
    algorithm: string
    num_topics: number
    topics: Array<{
      topic_id: number
      topic_label: string
      top_words: Array<[string, number]>
      keywords: string[]
      description: string
    }>
  }
}

export function TopicModelingResults({ results }: TopicModelingResultsProps) {
  const [selectedTopic, setSelectedTopic] = useState<number>(0)

  // Debug: Log what data we're receiving
  console.log("🔍 TopicModelingResults received data:", results)

  if (!results) {
    console.log("❌ No results data received")
    return (
      <Card className="border-border">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-secondary" />
            <CardTitle>Topic Modeling Results</CardTitle>
          </div>
          <CardDescription>
            Topic modeling results will appear here after analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Run topic modeling to see results</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const { topics, algorithm, num_topics } = results
  console.log("✅ Topic modeling data loaded:", { algorithm, num_topics, topicsCount: topics?.length })

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="border-border">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">Topics Found</CardTitle>
              <Brain className="w-4 h-4 text-secondary" />
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="text-2xl font-bold">{num_topics}</div>
            <p className="text-xs text-muted-foreground">Using {algorithm}</p>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">Algorithm</CardTitle>
              <Target className="w-4 h-4 text-secondary" />
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="text-2xl font-bold">{algorithm}</div>
            <p className="text-xs text-muted-foreground">Topic extraction method</p>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">Status</CardTitle>
              <Target className="w-4 h-4 text-secondary" />
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="text-2xl font-bold">Complete</div>
            <p className="text-xs text-muted-foreground">Analysis finished</p>
          </CardContent>
        </Card>
      </div>

      {/* Topics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {topics.map((topic, index) => (
          <Card key={topic.topic_id} className="border-border/50">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Topic {topic.topic_id + 1}</CardTitle>
                <Brain className="w-4 h-4 text-secondary/70" />
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Keywords */}
              <div>
                <p className="text-xs font-medium text-muted-foreground mb-2">Top Words</p>
                <div className="flex flex-wrap gap-1">
                  {topic.keywords && topic.keywords.length > 0 ? (
                    topic.keywords.slice(0, 6).map((word: string, i: number) => (
                      <Badge key={i} variant="secondary" className="text-xs">
                        {word}
                      </Badge>
                    ))
                  ) : (
                    <p className="text-xs text-muted-foreground">No words identified</p>
                  )}
                </div>
              </div>

              {/* Word Weights */}
              {topic.top_words && topic.top_words.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-2">Word Weights</p>
                  <div className="space-y-1">
                    {topic.top_words.slice(0, 5).map(([word, probability]: [string, number], i: number) => (
                      <div key={i} className="flex items-center justify-between text-xs">
                        <span>{word}</span>
                        <div className="flex items-center gap-2 flex-1 ml-2">
                          <Progress 
                            value={probability ? probability * 100 : 0} 
                            className="h-1 flex-1" 
                          />
                          <span className="text-muted-foreground w-8">
                            {probability ? (probability * 100).toFixed(0) : 0}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Analysis Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Topic Analysis Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="font-medium text-blue-900">Total Topics</div>
                <div className="text-blue-700">{num_topics} topics identified</div>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <div className="font-medium text-green-900">Algorithm</div>
                <div className="text-green-700">{algorithm} method used</div>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg">
                <div className="font-medium text-purple-900">Status</div>
                <div className="text-purple-700">Analysis complete</div>
              </div>
            </div>

            {topics.some(topic => topic.keywords.length === 0) && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="text-sm text-yellow-800">
                  <strong>Note:</strong> Some topics show no words. This may occur with very short text or when the algorithm needs more content to identify meaningful topics.
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
