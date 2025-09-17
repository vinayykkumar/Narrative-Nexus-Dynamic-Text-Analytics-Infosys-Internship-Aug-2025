"use client"

import React, { useEffect, useRef, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { BarChart3, FileText, Brain, Target } from "lucide-react"
import { Button } from "@/components/ui/button"
import html2canvas from "html2canvas"
import { jsPDF } from "jspdf"

type SentimentAnalysisResult = {
  overall_sentiment: string
  overall_confidence: number
  sentiment_distribution: { positive: number; negative: number; neutral: number }
  emotional_indicators?: Record<string, number>
  results?: Array<{ sentence: string; sentiment: string; confidence: number }>
  summary?: {
    total_sentences: number
    positive_sentences: number
    negative_sentences: number
    neutral_sentences: number
    average_confidence: number
  }
}

type TopicModelingResults = {
  algorithm: string
  num_topics: number
  topics: Array<{ topic_id: number; topic_label: string; keywords: string[]; top_words: [string, number][] }>
}

export default function AnalysisReport() {
  const [sentiment, setSentiment] = useState<SentimentAnalysisResult | null>(null)
  const [topics, setTopics] = useState<TopicModelingResults | null>(null)
  const [datasetSummary, setDatasetSummary] = useState<any | null>(null)
  const [artifacts, setArtifacts] = useState<any | null>(null)
  const reportRef = useRef<HTMLDivElement | null>(null)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    try {
      const resultsRaw = localStorage.getItem("analysisResults")
      const artifactsRaw = localStorage.getItem("analysisArtifacts")
      if (resultsRaw) {
        const parsed = JSON.parse(resultsRaw)
        setSentiment(parsed?.sentiment_results || null)
        setTopics(parsed?.topic_modeling_results || null)
        setDatasetSummary(parsed?.dataset_summary || null)
      }
      if (artifactsRaw) setArtifacts(JSON.parse(artifactsRaw))
    } catch {}
  }, [])

  const saveAsPdf = async () => {
    if (!reportRef.current || exporting) return
    setExporting(true)
    try {
      const node = reportRef.current
      const canvas = await html2canvas(node, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        logging: false,
        backgroundColor: "#ffffff",
        onclone: (doc) => {
          const style = doc.createElement('style')
          style.innerHTML = `
            :root {
              --background: #ffffff;
              --foreground: #0f172a;
              --card: #ffffff;
              --card-foreground: #0f172a;
              --muted: #f3f4f6;
              --muted-foreground: #6b7280;
              --accent: #f1f5f9;
              --accent-foreground: #0f172a;
              --popover: #ffffff;
              --popover-foreground: #0f172a;
              --primary: #0ea5e9;
              --primary-foreground: #ffffff;
              --secondary: #8b5cf6;
              --secondary-foreground: #ffffff;
              --border: #e5e7eb;
            }
            body { background: #ffffff !important; }
          `
          doc.head.appendChild(style)
        }
      })
      const imgData = canvas.toDataURL("image/jpeg", 0.95)
      const pdf = new jsPDF("p", "mm", "a4")
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()
      const imgWidth = pageWidth
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      let heightLeft = imgHeight
      let position = 0
      pdf.addImage(imgData, "JPEG", 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
      while (heightLeft > 0) {
        position = heightLeft - imgHeight
        pdf.addPage()
        pdf.addImage(imgData, "JPEG", 0, position, imgWidth, imgHeight)
        heightLeft -= pageHeight
      }
      const ts = new Date().toISOString().replace(/[:.]/g, "-")
      pdf.save(`analysis-report-${ts}.pdf`)
    } catch (e: any) {
      console.error('Save as PDF failed', e)
      // Fallback: open print dialog in a clean window to allow user to Save as PDF
      try {
        const content = reportRef.current?.innerHTML || ''
        const css = `
          :root {
            --background: #ffffff;
            --foreground: #0f172a;
            --card: #ffffff;
            --card-foreground: #0f172a;
            --muted: #f3f4f6;
            --muted-foreground: #6b7280;
            --accent: #f1f5f9;
            --accent-foreground: #0f172a;
            --primary: #0ea5e9;
            --primary-foreground: #ffffff;
            --secondary: #8b5cf6;
            --secondary-foreground: #ffffff;
            --border: #e5e7eb;
          }
          * { box-sizing: border-box; }
          body { background: #ffffff; color: #0f172a; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial, "Apple Color Emoji", "Segoe UI Emoji"; }
          h1,h2,h3 { color: #0f172a; }
          .border { border-color: #e5e7eb !important; }
          img { max-width: 100%; height: auto; }
          .rounded, .rounded-lg { border-radius: 0.5rem; }
          .text-muted-foreground { color: #6b7280; }
          .bg-muted { background: #f3f4f6; }
        `
        const html = `<!doctype html><html><head><meta charset="utf-8"><title>Analysis Report</title><style>${css}</style></head><body>${content}</body></html>`
        const w = window.open('', '_blank', 'width=1024,height=768')
        if (w) {
          w.document.open()
          w.document.write(html)
          w.document.close()
          w.focus()
          w.onload = () => {
            try { w.print() } catch {}
          }
          w.onafterprint = () => { try { w.close() } catch {} }
        }
      } catch (fallbackErr) {
        console.error('Fallback print failed', fallbackErr)
      }
    } finally {
      setExporting(false)
    }
  }

  const getSentimentBadge = (s?: string) => {
    if (!s) return <Badge variant="outline">N/A</Badge>
    const c = s.toLowerCase()
    if (c === "positive") return <Badge className="bg-green-500">POSITIVE</Badge>
    if (c === "negative") return <Badge className="bg-red-500">NEGATIVE</Badge>
    return <Badge variant="secondary">NEUTRAL</Badge>
  }

  return (
    <div ref={reportRef} className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl font-serif font-semibold">Analysis Report</h1>
            <p className="text-sm text-muted-foreground">Generated with Narrative Nexus</p>
          </div>
        </div>
        <div>
          <Button variant="outline" size="sm" onClick={saveAsPdf} disabled={exporting}>
            {exporting ? 'Saving…' : 'Save as PDF'}
          </Button>
        </div>
      </div>

      {/* Executive Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-4 h-4" /> Executive Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-foreground">
            {datasetSummary?.summary || "Summary will appear after running analysis."}
          </p>
          {datasetSummary?.key_sentences?.length ? (
            <div>
              <div className="text-xs text-muted-foreground mb-1">Key Sentences</div>
              <ul className="list-disc pl-5 space-y-1">
                {datasetSummary.key_sentences.map((s: string, i: number) => (
                  <li key={i} className="text-sm">{s}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </CardContent>
      </Card>

      {/* Topics & Sentiment */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-4 h-4" /> Topic Modeling
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {topics ? (
              <>
                <div className="text-xs text-muted-foreground">Algorithm: {topics.algorithm}</div>
                <div className="space-y-2">
                  {topics.topics.slice(0, 8).map((t) => (
                    <div key={t.topic_id} className="p-2 border rounded-lg">
                      <div className="text-sm font-medium">{t.topic_label}</div>
                      <div className="mt-1 text-xs text-muted-foreground flex flex-wrap gap-1">
                        {t.keywords.slice(0, 10).map((kw, idx) => (
                          <span key={idx} className="px-2 py-0.5 rounded-full bg-muted">{kw}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                {Array.isArray(artifacts?.wordclouds) && artifacts.wordclouds.length > 0 && (
                  <div className="mt-3">
                    <div className="text-xs text-muted-foreground mb-2">Wordclouds</div>
                    <div className="grid grid-cols-2 gap-2">
                      {artifacts.wordclouds.map((url: string, i: number) => (
                        <img key={i} src={url} alt={`Wordcloud ${i}`} className="w-full rounded border" />
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-sm text-muted-foreground">No topic results yet.</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-4 h-4" /> Sentiment & Emotions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {sentiment ? (
              <>
                <div className="flex items-center justify-between">
                  <div className="text-sm">Overall Sentiment</div>
                  {getSentimentBadge(sentiment.overall_sentiment)}
                </div>
                <div>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span>Confidence</span>
                    <span className="font-medium">{(sentiment.overall_confidence * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={sentiment.overall_confidence * 100} />
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="text-center p-2 bg-green-50 rounded border">
                    <div className="font-medium text-green-700">Positive</div>
                    <div className="text-green-600">{(sentiment.sentiment_distribution.positive * 100).toFixed(1)}%</div>
                  </div>
                  <div className="text-center p-2 bg-red-50 rounded border">
                    <div className="font-medium text-red-700">Negative</div>
                    <div className="text-red-600">{(sentiment.sentiment_distribution.negative * 100).toFixed(1)}%</div>
                  </div>
                  <div className="text-center p-2 bg-gray-50 rounded border">
                    <div className="font-medium text-gray-700">Neutral</div>
                    <div className="text-gray-600">{(sentiment.sentiment_distribution.neutral * 100).toFixed(1)}%</div>
                  </div>
                </div>
                {sentiment.emotional_indicators && (
                  <div className="space-y-2">
                    <Separator />
                    <div className="text-xs text-muted-foreground">Emotional Indicators (NRC)</div>
                    {Object.entries(sentiment.emotional_indicators).map(([emo, sc]) => (
                      <div key={emo}>
                        <div className="flex items-center justify-between text-xs">
                          <span className="capitalize">{emo}</span>
                          <span className="font-medium">{(sc * 100).toFixed(1)}%</span>
                        </div>
                        <Progress value={sc * 100} />
                      </div>
                    ))}
                  </div>
                )}
                {artifacts?.sentiment_distribution_bar || artifacts?.topic_sentiment_pie ? (
                  <div className="grid grid-cols-1 gap-2">
                    {artifacts?.sentiment_distribution_bar && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Sentiment Distribution</div>
                        <img src={artifacts.sentiment_distribution_bar} className="w-full border rounded" />
                      </div>
                    )}
                    {artifacts?.topic_sentiment_pie && (
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Topic vs Sentiment (Pie)</div>
                        <img src={artifacts.topic_sentiment_pie} className="w-full border rounded" />
                      </div>
                    )}
                  </div>
                ) : null}
              </>
            ) : (
              <div className="text-sm text-muted-foreground">No sentiment results yet.</div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Topic Distribution Chart */}
      {artifacts?.topic_distribution_pie && (
        <Card>
          <CardHeader>
            <CardTitle>Topic Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <img
              src={artifacts.topic_distribution_pie}
              className="mx-auto w-full max-w-xl border rounded object-contain"
            />
          </CardContent>
        </Card>
      )}

      {/* Actionable Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Actionable Insights & Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-5 space-y-1 text-sm">
            {sentiment && sentiment.sentiment_distribution.negative > 0.4 && (
              <li>High negative sentiment detected. Investigate top drivers within dominant topics and prioritize service recovery.</li>
            )}
            {topics && <li>Focus on top keywords per topic to design targeted improvements and FAQs.</li>}
            {sentiment && (sentiment.emotional_indicators?.fear || 0) > 0.2 && (
              <li>Elevated fear detected. Improve clarity of communication and reduce uncertainty in user journeys.</li>
            )}
            <li>Leverage recurring positive themes to amplify what works (highlight in onboarding and documentation).</li>
            <li>Track KPIs over time: Positive%, Negative%, top topic prevalence, and key complaint categories.</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
