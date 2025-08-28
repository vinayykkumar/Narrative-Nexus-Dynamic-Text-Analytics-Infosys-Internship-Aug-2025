"use client"

import { useState } from "react"
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
  const [options, setOptions] = useState<ExportOptions>({
    format: "pdf",
    includeRawData: false,
    includeVisualizations: true,
    includeSummary: true,
    includeRecommendations: true,
  })

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

  const handleExport = async () => {
    setIsExporting(true)
    
    // Simulate export process
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    setIsExporting(false)
    setExportComplete(true)
    
    // Reset after showing success
    setTimeout(() => {
      setExportComplete(false)
      setIsOpen(false)
    }, 2000)
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
