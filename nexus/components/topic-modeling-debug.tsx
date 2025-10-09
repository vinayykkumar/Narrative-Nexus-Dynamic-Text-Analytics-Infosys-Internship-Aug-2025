"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Brain, Play, Copy, Download, AlertCircle, CheckCircle } from "lucide-react"

export function TopicModelingDebug() {
  const [inputText, setInputText] = useState(`Machine learning and artificial intelligence are transforming the world.
Natural language processing helps computers understand human text and speech.
Data science involves statistical analysis, programming, and domain expertise.
Computer vision enables machines to interpret and analyze visual information.
Deep learning neural networks require large datasets for effective training.`)

  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const runTopicModeling = async () => {
    setIsLoading(true)
    setError(null)
    setResults(null)

    try {
      const texts = inputText.split('\n').filter(line => line.trim().length > 0)
      
      console.log('🚀 Sending request to topic modeling API...')
      console.log('📝 Input texts:', texts)
      
      const response = await fetch('http://localhost:8000/topic-modeling', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          texts: texts,
          algorithm: 'lda',
          num_topics: 3,
          num_iterations: 20
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('✅ Topic modeling results:', data)
      setResults(data)
      
    } catch (err) {
      console.error('❌ Error:', err)
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const copyResults = () => {
    if (results) {
      navigator.clipboard.writeText(JSON.stringify(results, null, 2))
    }
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Topic Modeling Debug Console
          </CardTitle>
          <CardDescription>
            Test and debug topic modeling functionality with real-time output
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Input Text (one document per line)</label>
            <Textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter text documents, one per line..."
              className="min-h-32"
            />
          </div>
          
          <Button 
            onClick={runTopicModeling} 
            disabled={isLoading || !inputText.trim()}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Brain className="w-4 h-4 mr-2 animate-spin" />
                Processing Topics...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Run Topic Modeling
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="w-4 h-4" />
          <AlertDescription>
            Error: {error}
          </AlertDescription>
        </Alert>
      )}

      {results && (
        <div className="space-y-6">
          <Alert>
            <CheckCircle className="w-4 h-4" />
            <AlertDescription>
              ✅ Topic modeling completed successfully! Found {results.num_topics} topics using {results.algorithm_used} algorithm.
            </AlertDescription>
          </Alert>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{results.num_topics}</div>
                <p className="text-xs text-muted-foreground">Topics Found</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{results.coherence_score?.toFixed(3) || 'N/A'}</div>
                <p className="text-xs text-muted-foreground">Coherence Score</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{results.model_performance?.documents_processed || 0}</div>
                <p className="text-xs text-muted-foreground">Documents</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{(results.processing_time * 1000)?.toFixed(0) || 0}ms</div>
                <p className="text-xs text-muted-foreground">Processing Time</p>
              </CardContent>
            </Card>
          </div>

          {/* Topics Detail */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Discovered Topics</CardTitle>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={copyResults}>
                    <Copy className="w-4 h-4 mr-2" />
                    Copy Results
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {results.topics?.map((topic: any, index: number) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold">Topic {index + 1}: {topic.label}</h3>
                      <Badge variant="secondary">
                        {topic.keywords?.length || 0} keywords
                      </Badge>
                    </div>
                    
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium mb-2">Keywords</h4>
                        <div className="flex flex-wrap gap-1">
                          {topic.keywords?.map((keyword: string, i: number) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {keyword}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium mb-2">Top Words (with weights)</h4>
                        <div className="space-y-1">
                          {topic.top_words?.slice(0, 5).map(([word, weight]: [string, number], i: number) => (
                            <div key={i} className="flex items-center justify-between">
                              <span className="text-sm">{word}</span>
                              <div className="flex items-center gap-2">
                                <Progress value={weight * 100} className="w-16" />
                                <span className="text-xs text-muted-foreground w-12">
                                  {(weight * 100).toFixed(1)}%
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Document-Topic Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Document-Topic Distribution</CardTitle>
              <CardDescription>How each document relates to discovered topics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {results.document_topic_distribution?.map((doc: any, index: number) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="text-sm font-medium">Document {doc.document_id + 1}</h4>
                        <p className="text-xs text-muted-foreground mt-1">
                          {doc.document_preview}
                        </p>
                      </div>
                      <Badge variant="secondary">
                        Dominant: Topic {doc.dominant_topic + 1} ({(doc.dominant_topic_probability * 100).toFixed(1)}%)
                      </Badge>
                    </div>
                    
                    <div className="grid gap-2">
                      {doc.topic_probabilities?.map((prob: number, topicIndex: number) => (
                        <div key={topicIndex} className="flex items-center gap-2">
                          <span className="text-xs w-16">Topic {topicIndex + 1}</span>
                          <Progress value={prob * 100} className="flex-1" />
                          <span className="text-xs text-muted-foreground w-10">
                            {(prob * 100).toFixed(0)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Raw JSON Output */}
          <Card>
            <CardHeader>
              <CardTitle>Raw API Response (Debug)</CardTitle>
              <CardDescription>Complete JSON response from the topic modeling API</CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg text-xs overflow-auto max-h-96">
                {JSON.stringify(results, null, 2)}
              </pre>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
