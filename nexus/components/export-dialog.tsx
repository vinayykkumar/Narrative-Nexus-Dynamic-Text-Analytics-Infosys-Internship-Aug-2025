"use client"

import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog"
import { 
  Download, 
  FileText, 
  FileSpreadsheet, 
  FileJson, 
  Mail, 
  Share2,
  Settings,
  CheckCircle,
  Loader2
} from "lucide-react"
import AnalysisReport from "@/components/analysis-report"
import html2canvas from "html2canvas"
import { jsPDF } from "jspdf"

interface ExportOptions {
  format: string
  includeRawData: boolean
  includeVisualizations: boolean
  includeSummary: boolean
  includeRecommendations: boolean
}

export function ExportDialog({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [exportComplete, setExportComplete] = useState(false)
  const [exportError, setExportError] = useState<string | null>(null)
  const [options, setOptions] = useState<ExportOptions>({
    format: "pdf",
    includeRawData: false,
    includeVisualizations: true,
    includeSummary: true,
    includeRecommendations: true,
  })

  // Offscreen render target for PDF capture
  const exportRef = useRef<HTMLDivElement | null>(null)
  const [renderForExport, setRenderForExport] = useState(false)

  const exportFormats = [
    { 
      value: "pdf", 
      label: "PDF Report", 
      icon: FileText, 
      description: "Comprehensive formatted report" 
    },
    { 
      value: "excel", 
      label: "Excel Workbook", 
      icon: FileSpreadsheet, 
      description: "Data tables and charts" 
    },
    { 
      value: "json", 
      label: "JSON Data", 
      icon: FileJson, 
      description: "Raw analysis results" 
    },
  ]

  const generatePdf = async () => {
    if (!exportRef.current) return
    await new Promise((r) => setTimeout(r, 50))
    const node = exportRef.current
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
  }

  const handleExport = async () => {
    setExportError(null)
    setIsExporting(true)
    try {
      if (options.format === "pdf") {
        // Render the full AnalysisReport offscreen to capture into PDF
        setRenderForExport(true)
        await new Promise((r) => setTimeout(r, 50))
        await generatePdf()
      } else if (options.format === "excel") {
        // If enriched CSV exists, navigate to it as a quick win
        try {
          const raw = localStorage.getItem('analysisArtifacts')
          const artifacts = raw ? JSON.parse(raw) : null
          if (artifacts?.enriched_csv) {
            window.open(artifacts.enriched_csv, '_blank')
          }
        } catch {}
        // Simulate small delay for UX
        await new Promise((r) => setTimeout(r, 800))
      } else if (options.format === "json") {
        // Download structured results JSON
        try {
          const raw = localStorage.getItem('analysisResults')
          if (raw) {
            const blob = new Blob([raw], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            const ts = new Date().toISOString().replace(/[:.]/g, "-")
            link.download = `analysis-results-${ts}.json`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            URL.revokeObjectURL(url)
          }
        } catch {}
        await new Promise((r) => setTimeout(r, 300))
      }

      setExportComplete(true)
      setIsExporting(false)
      // Reset after showing success
      setTimeout(() => {
        setExportComplete(false)
        setRenderForExport(false)
        setIsOpen(false)
      }, 1200)
    } catch (e) {
      console.error('Export failed', e)
      // Fallback: open print dialog with clean HTML if PDF export fails due to color parsing (oklch)
      try {
        const content = exportRef.current?.innerHTML || ''
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
        setExportError('Failed to export. Please try again.')
      }
      setIsExporting(false)
      setRenderForExport(false)
    }
  }

  const handleEmailReport = () => {
    // In a real app, this would trigger an email dialog or API call
    const subject = encodeURIComponent("NarrativeNexus Analysis Report")
    const body = encodeURIComponent("Please find the attached analysis report from NarrativeNexus.")
    window.open(`mailto:?subject=${subject}&body=${body}`)
  }

  const handleShare = () => {
    // In a real app, this would generate a shareable link
    if (navigator.share) {
      navigator.share({
        title: "NarrativeNexus Analysis Report",
        text: "Check out this text analysis report",
        url: window.location.href,
      })
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href)
    }
  }

  const selectedFormat = exportFormats.find(f => f.value === options.format)

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="font-serif">Export Analysis Results</DialogTitle>
          <DialogDescription>
            Choose your export format and options to download or share your analysis results.
          </DialogDescription>
        </DialogHeader>

        {/* Offscreen render target for PDF export (use same rendering as report) */}
        {renderForExport && (
          <div style={{ position: 'absolute', left: -10000, top: 0, width: 1024 }}>
            <div ref={exportRef}>
              <AnalysisReport />
            </div>
          </div>
        )}
        
        <div className="space-y-6">
          {/* Export Format Selection */}
          <div className="space-y-3">
            <h4 className="font-medium">Export Format</h4>
            <div className="grid grid-cols-1 gap-3">
              {exportFormats.map((format) => {
                const Icon = format.icon
                return (
                  <Card 
                    key={format.value}
                    className={`cursor-pointer transition-colors ${
                      options.format === format.value 
                        ? "ring-2 ring-secondary bg-secondary/5" 
                        : "hover:bg-muted/30"
                    }`}
                    onClick={() => setOptions(prev => ({ ...prev, format: format.value }))}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-secondary/10 rounded-lg flex items-center justify-center">
                          <Icon className="w-5 h-5 text-secondary" />
                        </div>
                        <div className="flex-1">
                          <h5 className="font-semibold">{format.label}</h5>
                          <p className="text-sm text-muted-foreground">{format.description}</p>
                        </div>
                        {options.format === format.value && (
                          <CheckCircle className="w-5 h-5 text-secondary" />
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>

          <Separator />

          {/* Content Options */}
          <div className="space-y-3">
            <h4 className="font-medium">Include in Export</h4>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="summary"
                  checked={options.includeSummary}
                  onCheckedChange={(checked) => 
                    setOptions(prev => ({ ...prev, includeSummary: checked as boolean }))
                  }
                />
                <label htmlFor="summary" className="text-sm font-medium">
                  Executive Summary
                </label>
                <Badge variant="secondary" className="text-xs">Recommended</Badge>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="visualizations"
                  checked={options.includeVisualizations}
                  onCheckedChange={(checked) => 
                    setOptions(prev => ({ ...prev, includeVisualizations: checked as boolean }))
                  }
                />
                <label htmlFor="visualizations" className="text-sm font-medium">
                  Charts and Visualizations
                </label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="recommendations"
                  checked={options.includeRecommendations}
                  onCheckedChange={(checked) => 
                    setOptions(prev => ({ ...prev, includeRecommendations: checked as boolean }))
                  }
                />
                <label htmlFor="recommendations" className="text-sm font-medium">
                  Actionable Recommendations
                </label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="rawdata"
                  checked={options.includeRawData}
                  onCheckedChange={(checked) => 
                    setOptions(prev => ({ ...prev, includeRawData: checked as boolean }))
                  }
                />
                <label htmlFor="rawdata" className="text-sm font-medium">
                  Raw Data Tables
                </label>
              </div>
            </div>
          </div>

          <Separator />

          {/* Action Buttons */}
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row gap-3">
              <Button 
                onClick={handleExport}
                disabled={isExporting || exportComplete}
                className="flex-1 bg-secondary hover:bg-secondary/90"
              >
                {isExporting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : exportComplete ? (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Downloaded!
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Export {selectedFormat?.label}
                  </>
                )}
              </Button>
            </div>
            {exportError && (
              <div className="text-sm text-destructive">{exportError}</div>
            )}
            
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleEmailReport} className="flex-1">
                <Mail className="w-4 h-4 mr-2" />
                Email Report
              </Button>
              <Button variant="outline" onClick={handleShare} className="flex-1">
                <Share2 className="w-4 h-4 mr-2" />
                Share Link
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
