"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FileUpload } from "@/components/file-upload"
import { DataSourceConnector } from "@/components/data-source-connector"
import { AnalysisOptions } from "@/components/analysis-options"
import { FileText, Type, Database, ArrowRight, Loader2 } from "lucide-react"
import { backendAPI } from "@/lib/api/backend-client"

export function TextInputForm() {
  const [textInput, setTextInput] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisStep, setAnalysisStep] = useState("")
  const [activeTab, setActiveTab] = useState("text")
  const router = useRouter()

  const handleAnalyze = async () => {
    if (!canAnalyze) return
    
    // Check if we're on the text tab and have text content
    if (activeTab === "text" && textInput.trim().length === 0) {
      console.log("❌ Cannot analyze: No text content provided");
      return;
    }
    
    // If we're on the file tab, the FileProcessor should handle the upload
    if (activeTab === "file") {
      console.log("📁 File upload should be handled by FileProcessor component");
      return;
    }
    
    setIsAnalyzing(true)
    
    try {
      console.log("🚀 Starting complete architecture-compliant analysis flow...");
      console.log("📝 Text length:", textInput.length, "characters");
      
      // STEP 1: Input Data Handling
      console.log("Step 1: Input Data Handling...");
      setAnalysisStep("Processing input data...");
      const inputResponse = await fetch('http://localhost:8000/input/text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: textInput,
          source: 'manual_input'
        }),
      });
      
      if (!inputResponse.ok) {
        throw new Error('Failed to process input data');
      }
      
      const inputResult = await inputResponse.json();
      const sessionId = inputResult.session_id;
      console.log("✅ Input data processed. Session ID:", sessionId);
      
      // STEP 2: Data Processing
      console.log("Step 2: Data Processing...");
      setAnalysisStep("Processing and cleaning text...");
      const processResponse = await fetch(`http://localhost:8000/process/data/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!processResponse.ok) {
        throw new Error('Failed to process data');
      }
      
      const processResult = await processResponse.json();
      console.log("✅ Data processing completed");
      
      // STEP 3: Sentiment Analysis
      console.log("Step 3: Sentiment Analysis...");
      setAnalysisStep("Analyzing sentiment and emotions...");
      const sentimentResponse = await fetch(`http://localhost:8000/analyze/sentiment/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!sentimentResponse.ok) {
        throw new Error('Failed to analyze sentiment');
      }
      
      const sentimentResult = await sentimentResponse.json();
      console.log("✅ Sentiment analysis completed");
      
      // STEP 4: Topic Modeling
      console.log("Step 4: Topic Modeling...");
      setAnalysisStep("Extracting topics and themes...");
      const topicResponse = await fetch(`http://localhost:8000/analyze/topics/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!topicResponse.ok) {
        throw new Error('Failed to analyze topics');
      }
      
      const topicResult = await topicResponse.json();
      console.log("✅ Topic modeling completed");
      
      // STEP 5: Insight Generation
      console.log("Step 5: Insight Generation...");
      setAnalysisStep("Generating insights and recommendations...");
      const insightResponse = await fetch(`http://localhost:8000/insights/generate/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!insightResponse.ok) {
        throw new Error('Failed to generate insights');
      }
      
      const insightResult = await insightResponse.json();
      console.log("✅ Insight generation completed");
      
      // Store the session ID and results for the dashboard
      const analysisData = {
        sessionId: sessionId,
        input: textInput,
        inputResult: inputResult,
        processResult: processResult,
        sentimentResult: sentimentResult,
        topicResult: topicResult,
        insightResult: insightResult,
        timestamp: new Date().toISOString(),
        type: activeTab,
        complete: true
      }
      localStorage.setItem('currentAnalysis', JSON.stringify(analysisData))
      
      console.log("🎉 Complete analysis flow finished! Redirecting to dashboard...");
      setIsAnalyzing(false)
      
      // Navigate directly to dashboard with session ID
      router.push(`/dashboard?session=${sessionId}`)
      
    } catch (error) {
      console.error("❌ Error during analysis:", error);
      setIsAnalyzing(false);
      
      // Store analysis data even if it fails
      const analysisData = {
        input: textInput,
        error: error instanceof Error ? error.message : "Unknown error occurred",
        timestamp: new Date().toISOString(),
        type: activeTab,
        complete: false
      }
      localStorage.setItem('currentAnalysis', JSON.stringify(analysisData))
      
      // Show error but still navigate to processing page for error display
      router.push('/processing')
    }
  }

  const canAnalyze = (activeTab === "text" && textInput.trim().length > 0) || (activeTab !== "text")

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="font-serif">Input Your Data</CardTitle>
          <CardDescription>
            Choose how you'd like to provide text for analysis. You can upload files, paste text directly, or connect to
            data sources.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="text" className="flex items-center gap-2">
                <Type className="w-4 h-4" />
                Text Input
              </TabsTrigger>
              <TabsTrigger value="file" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                File Upload
              </TabsTrigger>
              <TabsTrigger value="source" className="flex items-center gap-2">
                <Database className="w-4 h-4" />
                Data Source
              </TabsTrigger>
            </TabsList>

            <TabsContent value="text" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="text-input">Paste Your Text</Label>
                <Textarea
                  id="text-input"
                  placeholder="Paste your text here for analysis. This could be articles, reports, social media content, customer feedback, or any other text data you'd like to analyze..."
                  className="min-h-[300px] resize-none"
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                />
                <div className="flex justify-between items-center text-sm text-muted-foreground">
                  <span>{textInput.length} characters</span>
                  <span>Minimum 50 characters recommended</span>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="file" className="space-y-4">
              <FileUpload />
            </TabsContent>

            <TabsContent value="source" className="space-y-4">
              <DataSourceConnector />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <AnalysisOptions />

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-serif font-semibold mb-1">Ready to Analyze</h3>
              <p className="text-sm text-muted-foreground">
                Your text will be processed through the complete analysis pipeline: sentiment analysis, topic modeling, and insight generation.
              </p>
            </div>
            <Button
              onClick={handleAnalyze}
              disabled={!canAnalyze || isAnalyzing}
              size="lg"
              className="bg-secondary hover:bg-secondary/90"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {analysisStep || "Running Complete Analysis..."}
                </>
              ) : (
                <>
                  Start Complete Analysis
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
