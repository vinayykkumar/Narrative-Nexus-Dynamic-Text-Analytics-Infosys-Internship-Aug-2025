"use client"

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  FileDown, Mail, Share2, Copy, CheckCircle, 
  BarChart3, TrendingUp, FileText, AlertCircle 
} from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface ReportData {
  title: string;
  summary: string;
  sentiment_analysis: {
    overall_sentiment: string;
    confidence: number;
    distribution: { positive: number; negative: number; neutral: number; };
  };
  topic_analysis: {
    top_topics: Array<{ name: string; relevance: number; }>;
  };
  key_insights: string[];
  recommendations: string[];
}

export function ComprehensiveReporting() {
  const [loading, setLoading] = useState(false)
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [emailRecipient, setEmailRecipient] = useState('')
  const [reportTitle, setReportTitle] = useState('Text Analysis Report')
  const [customNotes, setCustomNotes] = useState('')
  const [reportFormat, setReportFormat] = useState('comprehensive')
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  // Sample report data
  const sampleReportData: ReportData = {
    title: "Comprehensive Text Analysis Report",
    summary: "Analysis of 2,847 text samples reveals predominantly positive sentiment (72%) with key themes in technology innovation and customer experience. High confidence scores (88%) indicate reliable insights for strategic decision-making.",
    sentiment_analysis: {
      overall_sentiment: "positive",
      confidence: 0.88,
      distribution: { positive: 72, negative: 18, neutral: 10 }
    },
    topic_analysis: {
      top_topics: [
        { name: "Technology & Innovation", relevance: 0.34 },
        { name: "Customer Experience", relevance: 0.28 },
        { name: "Business Strategy", relevance: 0.18 },
        { name: "Product Development", relevance: 0.12 },
        { name: "Market Analysis", relevance: 0.08 }
      ]
    },
    key_insights: [
      "Technology discussions dominate content with 34% prevalence",
      "Customer satisfaction indicators show strong positive trends",
      "Innovation themes correlate with higher engagement metrics",
      "Financial performance discussions require attention",
      "Product development sentiment trending upward"
    ],
    recommendations: [
      "Focus marketing efforts on technology innovation messaging",
      "Maintain current customer experience initiatives",
      "Address concerns in financial performance communications",
      "Leverage positive product development momentum",
      "Monitor business strategy sentiment closely"
    ]
  }

  const generateReport = async () => {
    setLoading(true)
    setError('')
    setSuccess('')
    
    try {
      // Simulate API call to generate report
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      setReportData(sampleReportData)
      setSuccess('Report generated successfully!')
    } catch (err) {
      setError('Failed to generate report. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const exportToPDF = async () => {
    try {
      // Dynamic import to avoid SSR issues
      const { jsPDF } = await import('jspdf')
      
      const pdf = new jsPDF()
      const pageWidth = pdf.internal.pageSize.width
      let yPosition = 20

      // Title
      pdf.setFontSize(20)
      pdf.text(reportData?.title || 'Analysis Report', 20, yPosition)
      yPosition += 20

      // Summary
      pdf.setFontSize(12)
      pdf.text('Executive Summary', 20, yPosition)
      yPosition += 10
      
      const summaryLines = pdf.splitTextToSize(reportData?.summary || '', pageWidth - 40)
      pdf.text(summaryLines, 20, yPosition)
      yPosition += summaryLines.length * 5 + 10

      // Sentiment Analysis
      pdf.text('Sentiment Analysis Results', 20, yPosition)
      yPosition += 10
      pdf.text(`Overall Sentiment: ${reportData?.sentiment_analysis.overall_sentiment}`, 20, yPosition)
      yPosition += 7
      pdf.text(`Confidence: ${((reportData?.sentiment_analysis.confidence || 0) * 100).toFixed(1)}%`, 20, yPosition)
      yPosition += 7
      pdf.text(`Distribution: Positive ${reportData?.sentiment_analysis.distribution.positive}%, Negative ${reportData?.sentiment_analysis.distribution.negative}%, Neutral ${reportData?.sentiment_analysis.distribution.neutral}%`, 20, yPosition)
      yPosition += 15

      // Topics
      pdf.text('Top Topics Identified', 20, yPosition)
      yPosition += 10
      reportData?.topic_analysis.top_topics.forEach((topic, index) => {
        pdf.text(`${index + 1}. ${topic.name} (${(topic.relevance * 100).toFixed(1)}%)`, 20, yPosition)
        yPosition += 7
      })
      yPosition += 10

      // Key Insights
      pdf.text('Key Insights', 20, yPosition)
      yPosition += 10
      reportData?.key_insights.forEach((insight, index) => {
        const insightLines = pdf.splitTextToSize(`• ${insight}`, pageWidth - 40)
        pdf.text(insightLines, 20, yPosition)
        yPosition += insightLines.length * 5 + 3
      })
      yPosition += 10

      // Recommendations
      if (yPosition > pdf.internal.pageSize.height - 60) {
        pdf.addPage()
        yPosition = 20
      }
      
      pdf.text('Recommendations', 20, yPosition)
      yPosition += 10
      reportData?.recommendations.forEach((rec, index) => {
        const recLines = pdf.splitTextToSize(`${index + 1}. ${rec}`, pageWidth - 40)
        pdf.text(recLines, 20, yPosition)
        yPosition += recLines.length * 5 + 5
      })

      // Custom notes
      if (customNotes) {
        yPosition += 10
        pdf.text('Additional Notes', 20, yPosition)
        yPosition += 10
        const notesLines = pdf.splitTextToSize(customNotes, pageWidth - 40)
        pdf.text(notesLines, 20, yPosition)
      }

      // Footer
      pdf.setFontSize(8)
      pdf.text(`Generated on ${new Date().toLocaleDateString()} by NarrativeNexus`, 20, pdf.internal.pageSize.height - 10)

      pdf.save(`${reportTitle.replace(/\s+/g, '_')}_Analysis_Report.pdf`)
      setSuccess('PDF report exported successfully!')
    } catch (err) {
      setError('Failed to export PDF. Please try again.')
    }
  }

  const sendEmailReport = async () => {
    if (!emailRecipient) {
      setError('Please enter an email recipient')
      return
    }

    setLoading(true)
    try {
      // Simulate email sending
      await new Promise(resolve => setTimeout(resolve, 1500))
      setSuccess(`Report emailed successfully to ${emailRecipient}!`)
    } catch (err) {
      setError('Failed to send email. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const copyReportLink = () => {
    const reportUrl = `${window.location.origin}/reports/shared/${Date.now()}`
    navigator.clipboard.writeText(reportUrl)
    setSuccess('Report link copied to clipboard!')
  }

  const exportToJSON = () => {
    if (reportData) {
      const dataStr = JSON.stringify(reportData, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${reportTitle.replace(/\s+/g, '_')}_data.json`
      link.click()
      URL.revokeObjectURL(url)
      setSuccess('Data exported as JSON successfully!')
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Report Configuration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Report Title</Label>
              <Input
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
                placeholder="Enter report title"
              />
            </div>
            
            <div className="space-y-2">
              <Label>Report Format</Label>
              <Select value={reportFormat} onValueChange={setReportFormat}>
                <SelectTrigger>
                  <SelectValue placeholder="Select format" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="comprehensive">Comprehensive Report</SelectItem>
                  <SelectItem value="executive">Executive Summary</SelectItem>
                  <SelectItem value="technical">Technical Analysis</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="mt-4">
            <Label>Custom Notes (Optional)</Label>
            <Textarea
              value={customNotes}
              onChange={(e) => setCustomNotes(e.target.value)}
              placeholder="Add any custom notes or observations..."
              rows={3}
              className="mt-2"
            />
          </div>
          
          <Button 
            onClick={generateReport} 
            disabled={loading}
            className="w-full mt-4"
          >
            {loading ? 'Generating Report...' : 'Generate Analysis Report'}
          </Button>
        </CardContent>
      </Card>

      {(success || error) && (
        <Alert variant={error ? "destructive" : "default"}>
          {error ? <AlertCircle className="h-4 w-4" /> : <CheckCircle className="h-4 w-4" />}
          <AlertDescription>{success || error}</AlertDescription>
        </Alert>
      )}

      {reportData && (
        <div className="space-y-6">
          {/* Report Preview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Report Preview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">{reportData.title}</h3>
                <p className="text-gray-700 mb-4">{reportData.summary}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center p-3 bg-blue-50 rounded-lg border">
                  <div className="text-2xl font-bold text-blue-600">
                    {reportData.sentiment_analysis.overall_sentiment.toUpperCase()}
                  </div>
                  <div className="text-sm text-blue-700">Overall Sentiment</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg border">
                  <div className="text-2xl font-bold text-green-600">
                    {(reportData.sentiment_analysis.confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-green-700">Confidence Score</div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg border">
                  <div className="text-2xl font-bold text-purple-600">
                    {reportData.topic_analysis.top_topics.length}
                  </div>
                  <div className="text-sm text-purple-700">Key Topics</div>
                </div>
              </div>

              <Tabs defaultValue="insights" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="insights">Key Insights</TabsTrigger>
                  <TabsTrigger value="topics">Top Topics</TabsTrigger>
                  <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
                </TabsList>
                
                <TabsContent value="insights" className="space-y-2">
                  {reportData.key_insights.map((insight, index) => (
                    <div key={index} className="p-2 bg-gray-50 rounded border-l-4 border-blue-500">
                      <p className="text-sm">{insight}</p>
                    </div>
                  ))}
                </TabsContent>
                
                <TabsContent value="topics" className="space-y-2">
                  {reportData.topic_analysis.top_topics.map((topic, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm font-medium">{topic.name}</span>
                      <Badge variant="outline">{(topic.relevance * 100).toFixed(1)}%</Badge>
                    </div>
                  ))}
                </TabsContent>
                
                <TabsContent value="recommendations" className="space-y-2">
                  {reportData.recommendations.map((rec, index) => (
                    <div key={index} className="p-2 bg-green-50 rounded border-l-4 border-green-500">
                      <p className="text-sm">{rec}</p>
                    </div>
                  ))}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Export and Share Options */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Share2 className="h-5 w-5" />
                Export & Share Options
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <Button onClick={exportToPDF} className="w-full flex items-center gap-2">
                    <FileDown className="h-4 w-4" />
                    Export as PDF
                  </Button>
                  
                  <Button onClick={exportToJSON} variant="outline" className="w-full flex items-center gap-2">
                    <FileDown className="h-4 w-4" />
                    Export Data (JSON)
                  </Button>
                  
                  <Button onClick={copyReportLink} variant="outline" className="w-full flex items-center gap-2">
                    <Copy className="h-4 w-4" />
                    Copy Share Link
                  </Button>
                </div>
                
                <div className="space-y-3">
                  <div className="space-y-2">
                    <Label>Email Report To:</Label>
                    <Input
                      type="email"
                      value={emailRecipient}
                      onChange={(e) => setEmailRecipient(e.target.value)}
                      placeholder="recipient@example.com"
                    />
                  </div>
                  
                  <Button 
                    onClick={sendEmailReport} 
                    disabled={loading || !emailRecipient}
                    className="w-full flex items-center gap-2"
                  >
                    <Mail className="h-4 w-4" />
                    {loading ? 'Sending...' : 'Email Report'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
