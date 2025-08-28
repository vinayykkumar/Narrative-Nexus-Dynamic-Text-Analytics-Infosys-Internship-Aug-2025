"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { 
  FileText, 
  FileSpreadsheet, 
  File, 
  CheckCircle, 
  AlertCircle, 
  Eye,
  Trash2,
  Loader2,
  BarChart3
} from "lucide-react"

interface ProcessedFile {
  id: string
  name: string
  size: number
  type: string
  status: "processing" | "completed" | "error"
  extractedText?: string
  wordCount?: number
  processingProgress?: number
  error?: string
}

export function FileProcessor({ files }: { files: File[] }) {
  const [processedFiles, setProcessedFiles] = useState<ProcessedFile[]>([])
  const [isProcessing, setIsProcessing] = useState(false)

  const getFileIcon = (type: string) => {
    if (type.includes('spreadsheet') || type.includes('excel')) {
      return FileSpreadsheet
    }
    if (type.includes('text') || type.includes('document')) {
      return FileText
    }
    return File
  }

  const getFileTypeLabel = (type: string) => {
    if (type.includes('pdf')) return 'PDF'
    if (type.includes('document')) return 'Word'
    if (type.includes('spreadsheet')) return 'Excel'
    if (type.includes('csv')) return 'CSV'
    if (type.includes('text')) return 'Text'
    if (type.includes('json')) return 'JSON'
    return 'Unknown'
  }

  const simulateFileProcessing = async (file: File): Promise<ProcessedFile> => {
    const processedFile: ProcessedFile = {
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      status: "processing",
      processingProgress: 0,
    }

    setProcessedFiles(prev => [...prev, processedFile])

    // Simulate processing with progress updates
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 200))
      setProcessedFiles(prev => 
        prev.map(f => 
          f.id === processedFile.id 
            ? { ...f, processingProgress: progress }
            : f
        )
      )
    }

    // Simulate text extraction based on file type
    let extractedText = ""
    let wordCount = 0
    let finalStatus: "completed" | "error" = "completed"
    let error: string | undefined

    try {
      if (file.type.includes('text')) {
        extractedText = await file.text()
      } else if (file.type.includes('json')) {
        const jsonData = JSON.parse(await file.text())
        extractedText = JSON.stringify(jsonData, null, 2)
      } else {
        // Simulate extraction for other file types
        extractedText = `Extracted text content from ${file.name}. This is simulated content for demonstration purposes. In a real implementation, this would contain the actual extracted text from the document using appropriate parsers for PDF, Word documents, Excel files, etc.`
      }
      
      wordCount = extractedText.split(/\s+/).filter(word => word.length > 0).length
      
      // Simulate occasional processing errors
      if (Math.random() < 0.1) {
        finalStatus = "error"
        error = "Failed to extract text from file"
      }
    } catch (err) {
      finalStatus = "error"
      error = "Invalid file format or corrupted file"
    }

    // Update final status
    setProcessedFiles(prev => 
      prev.map(f => 
        f.id === processedFile.id 
          ? { 
              ...f, 
              status: finalStatus,
              extractedText,
              wordCount,
              error,
              processingProgress: 100
            }
          : f
      )
    )

    return {
      ...processedFile,
      status: finalStatus,
      extractedText,
      wordCount,
      error,
    }
  }

  const handleProcessFiles = async () => {
    setIsProcessing(true)
    
    // Process all files
    const promises = files.map(file => simulateFileProcessing(file))
    await Promise.all(promises)
    
    setIsProcessing(false)
  }

  const handleRemoveFile = (id: string) => {
    setProcessedFiles(prev => prev.filter(f => f.id !== id))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const totalWordCount = processedFiles
    .filter(f => f.status === "completed")
    .reduce((sum, f) => sum + (f.wordCount || 0), 0)

  const completedFiles = processedFiles.filter(f => f.status === "completed").length
  const errorFiles = processedFiles.filter(f => f.status === "error").length

  if (files.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No files selected for processing</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Processing Summary */}
      {processedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="font-serif flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Processing Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{completedFiles}</div>
                <div className="text-sm text-muted-foreground">Completed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{errorFiles}</div>
                <div className="text-sm text-muted-foreground">Errors</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{totalWordCount.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground">Total Words</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* File Processing Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif">File Processing</CardTitle>
          <CardDescription>
            {files.length} file{files.length !== 1 ? 's' : ''} ready for processing
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {processedFiles.length === 0 && (
              <Button 
                onClick={handleProcessFiles}
                disabled={isProcessing}
                className="w-full"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processing Files...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Process {files.length} File{files.length !== 1 ? 's' : ''}
                  </>
                )}
              </Button>
            )}

            {/* Processed Files List */}
            <div className="space-y-3">
              {processedFiles.map((file) => {
                const Icon = getFileIcon(file.type)
                return (
                  <Card key={file.id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 flex-1">
                        <div className="w-10 h-10 bg-secondary/10 rounded-lg flex items-center justify-center">
                          <Icon className="w-5 h-5 text-secondary" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium truncate">{file.name}</h4>
                            <Badge variant="outline" className="text-xs">
                              {getFileTypeLabel(file.type)}
                            </Badge>
                            {file.status === "completed" && (
                              <Badge className="bg-green-500 text-white text-xs">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Completed
                              </Badge>
                            )}
                            {file.status === "error" && (
                              <Badge className="bg-red-500 text-white text-xs">
                                <AlertCircle className="w-3 h-3 mr-1" />
                                Error
                              </Badge>
                            )}
                          </div>
                          
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span>{formatFileSize(file.size)}</span>
                            {file.wordCount && (
                              <span>{file.wordCount.toLocaleString()} words</span>
                            )}
                          </div>

                          {file.status === "processing" && file.processingProgress !== undefined && (
                            <div className="mt-2">
                              <Progress value={file.processingProgress} className="h-2" />
                            </div>
                          )}

                          {file.error && (
                            <div className="mt-2 text-sm text-red-600">
                              {file.error}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {file.status === "completed" && file.extractedText && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => {
                              // In a real app, this would open a preview modal
                              console.log("Preview:", file.extractedText?.substring(0, 200) + "...")
                            }}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                        )}
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleRemoveFile(file.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                )
              })}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
