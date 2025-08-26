"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Brain, 
  BarChart3, 
  FileText, 
  Target, 
  CheckCircle, 
  Loader2,
  AlertCircle,
  Clock
} from "lucide-react"

interface AnalysisStep {
  id: string
  name: string
  description: string
  icon: React.ComponentType<any>
  status: "pending" | "processing" | "completed" | "error"
  progress?: number
  estimatedTime?: string
  result?: any
}

interface AnalysisProgressProps {
  onComplete?: (results: any) => void
  inputData?: string
}

export function AnalysisProgress({ onComplete, inputData }: AnalysisProgressProps) {
  const [steps, setSteps] = useState<AnalysisStep[]>([
    {
      id: "preprocessing",
      name: "Text Preprocessing",
      description: "Cleaning and preparing text data",
      icon: FileText,
      status: "pending",
      estimatedTime: "10s",
    },
    {
      id: "tokenization",
      name: "Tokenization & NLP",
      description: "Breaking down text into analyzable components",
      icon: Target,
      status: "pending",
      estimatedTime: "15s",
    },
    {
      id: "sentiment",
      name: "Sentiment Analysis",
      description: "Analyzing emotional tone and sentiment patterns",
      icon: BarChart3,
      status: "pending",
      estimatedTime: "20s",
    },
    {
      id: "topics",
      name: "Topic Modeling",
      description: "Identifying key themes using LDA algorithms",
      icon: Brain,
      status: "pending",
      estimatedTime: "25s",
    },
    {
      id: "summary",
      name: "Content Summarization",
      description: "Generating executive summaries",
      icon: FileText,
      status: "pending",
      estimatedTime: "10s",
    },
  ])

  const [currentStep, setCurrentStep] = useState(0)
  const [overallProgress, setOverallProgress] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [startTime, setStartTime] = useState<Date | null>(null)
  const [elapsedTime, setElapsedTime] = useState(0)

  useEffect(() => {
    if (!startTime) {
      setStartTime(new Date())
      startAnalysis()
    }
  }, [])

  useEffect(() => {
    if (startTime && !isComplete) {
      const timer = setInterval(() => {
        const now = new Date()
        const elapsed = Math.floor((now.getTime() - startTime.getTime()) / 1000)
        setElapsedTime(elapsed)
      }, 1000)

      return () => clearInterval(timer)
    }
  }, [startTime, isComplete])

  const startAnalysis = async () => {
    for (let i = 0; i < steps.length; i++) {
      setCurrentStep(i)
      
      // Start processing current step
      setSteps(prev => 
        prev.map((step, index) => 
          index === i 
            ? { ...step, status: "processing", progress: 0 }
            : step
        )
      )

      // Simulate step processing with progress updates
      const stepDuration = 2000 + Math.random() * 3000 // 2-5 seconds per step
      const progressInterval = stepDuration / 100

      for (let progress = 0; progress <= 100; progress += 5) {
        await new Promise(resolve => setTimeout(resolve, progressInterval))
        
        setSteps(prev => 
          prev.map((step, index) => 
            index === i 
              ? { ...step, progress }
              : step
          )
        )

        // Update overall progress
        const overallProg = ((i * 100) + progress) / steps.length
        setOverallProgress(overallProg)
      }

      // Complete current step
      setSteps(prev => 
        prev.map((step, index) => 
          index === i 
            ? { 
                ...step, 
                status: "completed", 
                progress: 100,
                result: generateMockResult(step.id)
              }
            : step
        )
      )

      // Small delay between steps
      await new Promise(resolve => setTimeout(resolve, 500))
    }

    // Analysis complete
    setIsComplete(true)
    setOverallProgress(100)
    
    if (onComplete) {
      const results = generateCompleteResults()
      onComplete(results)
    }
  }

  const generateMockResult = (stepId: string) => {
    switch (stepId) {
      case "preprocessing":
        return {
          cleaned_words: 1247,
          removed_words: 89,
          sentences: 45,
        }
      case "tokenization":
        return {
          tokens: 1158,
          entities: 23,
          pos_tags: 892,
        }
      case "sentiment":
        return {
          positive: 72,
          neutral: 18,
          negative: 10,
          confidence: 0.88,
        }
      case "topics":
        return {
          topics_found: 5,
          coherence_score: 0.85,
          dominant_topic: "Technology & Innovation",
        }
      case "summary":
        return {
          summary_length: 150,
          compression_ratio: 0.12,
          key_points: 8,
        }
      default:
        return {}
    }
  }

  const generateCompleteResults = () => {
    return {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toISOString(),
      input_length: inputData?.length || 1500,
      processing_time: elapsedTime,
      steps: steps,
      overall_sentiment: 0.72,
      topic_count: 5,
      summary_generated: true,
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getStatusIcon = (status: string, icon: React.ComponentType<any>) => {
    const Icon = icon
    
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case "processing":
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
      case "error":
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <Icon className="w-5 h-5 text-muted-foreground" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center justify-between">
            <span>Analysis Progress</span>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="w-4 h-4" />
              {formatTime(elapsedTime)}
            </div>
          </CardTitle>
          <CardDescription>
            {isComplete 
              ? "Analysis completed successfully!" 
              : `Processing step ${currentStep + 1} of ${steps.length}`
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span>Overall Progress</span>
              <span>{Math.round(overallProgress)}%</span>
            </div>
            <Progress value={overallProgress} className="h-3" />
            
            {isComplete && (
              <div className="flex items-center gap-2 text-green-600 font-medium">
                <CheckCircle className="w-4 h-4" />
                Analysis completed in {formatTime(elapsedTime)}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Step Details */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif">Processing Steps</CardTitle>
          <CardDescription>Detailed breakdown of analysis components</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center gap-4 p-4 border border-border rounded-lg">
                <div className="flex-shrink-0">
                  {getStatusIcon(step.status, step.icon)}
                </div>
                
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">{step.name}</h4>
                    <div className="flex items-center gap-2">
                      {step.status === "completed" && (
                        <Badge className="bg-green-500 text-white text-xs">
                          Completed
                        </Badge>
                      )}
                      {step.status === "processing" && (
                        <Badge className="bg-blue-500 text-white text-xs">
                          Processing
                        </Badge>
                      )}
                      {step.status === "pending" && step.estimatedTime && (
                        <Badge variant="outline" className="text-xs">
                          ~{step.estimatedTime}
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  <p className="text-sm text-muted-foreground">{step.description}</p>
                  
                  {step.status === "processing" && step.progress !== undefined && (
                    <Progress value={step.progress} className="h-2" />
                  )}
                  
                  {step.status === "completed" && step.result && (
                    <div className="text-xs text-muted-foreground mt-2">
                      {Object.entries(step.result).map(([key, value]) => (
                        <span key={key} className="mr-4">
                          {key.replace(/_/g, ' ')}: {value as string}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
