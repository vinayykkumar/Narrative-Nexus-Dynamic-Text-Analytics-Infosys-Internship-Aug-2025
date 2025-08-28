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

export function TextInputForm() {
  const [textInput, setTextInput] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [activeTab, setActiveTab] = useState("text")
  const router = useRouter()

  const handleAnalyze = async () => {
    if (!canAnalyze) return
    
    setIsAnalyzing(true)
    
    // Store analysis data in localStorage for demo purposes
    const analysisData = {
      input: textInput,
      timestamp: new Date().toISOString(),
      type: activeTab,
    }
    localStorage.setItem('currentAnalysis', JSON.stringify(analysisData))
    
    // Brief delay to show loading state
    await new Promise((resolve) => setTimeout(resolve, 1000))
    
    setIsAnalyzing(false)
    
    // Navigate to processing page
    router.push('/processing')
  }

  const canAnalyze = textInput.trim().length > 0 || activeTab !== "text"

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
                Your text will be processed using advanced NLP algorithms to extract insights.
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
                  Analyzing...
                </>
              ) : (
                <>
                  Start Analysis
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
