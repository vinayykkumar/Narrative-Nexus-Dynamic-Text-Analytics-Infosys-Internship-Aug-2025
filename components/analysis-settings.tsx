"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { 
  Settings, 
  Brain, 
  BarChart3, 
  FileText, 
  Target,
  Bell,
  Download,
  Shield,
  Globe,
  Save,
  RotateCcw
} from "lucide-react"

interface AnalysisSettings {
  // Analysis Configuration
  defaultTopicCount: number
  sentimentThreshold: number
  summaryLength: string
  confidenceThreshold: number
  
  // Processing Options
  enableParallelProcessing: boolean
  maxFileSize: number
  autoSaveResults: boolean
  
  // Notification Settings
  emailNotifications: boolean
  progressNotifications: boolean
  completionNotifications: boolean
  
  // Export Settings
  defaultExportFormat: string
  includeRawData: boolean
  includeVisualizations: boolean
  
  // Privacy & Security
  dataRetentionDays: number
  anonymizeData: boolean
  secureProcessing: boolean
}

export function AnalysisSettings() {
  const [settings, setSettings] = useState<AnalysisSettings>({
    defaultTopicCount: 5,
    sentimentThreshold: 0.5,
    summaryLength: "medium",
    confidenceThreshold: 0.8,
    enableParallelProcessing: true,
    maxFileSize: 10,
    autoSaveResults: true,
    emailNotifications: false,
    progressNotifications: true,
    completionNotifications: true,
    defaultExportFormat: "pdf",
    includeRawData: false,
    includeVisualizations: true,
    dataRetentionDays: 30,
    anonymizeData: false,
    secureProcessing: true,
  })

  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  const updateSetting = (key: keyof AnalysisSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }))
    setHasUnsavedChanges(true)
  }

  const handleSave = () => {
    // In a real app, this would save to backend/localStorage
    localStorage.setItem('analysisSettings', JSON.stringify(settings))
    setHasUnsavedChanges(false)
    console.log('Settings saved:', settings)
  }

  const handleReset = () => {
    // Reset to default values
    const defaultSettings: AnalysisSettings = {
      defaultTopicCount: 5,
      sentimentThreshold: 0.5,
      summaryLength: "medium",
      confidenceThreshold: 0.8,
      enableParallelProcessing: true,
      maxFileSize: 10,
      autoSaveResults: true,
      emailNotifications: false,
      progressNotifications: true,
      completionNotifications: true,
      defaultExportFormat: "pdf",
      includeRawData: false,
      includeVisualizations: true,
      dataRetentionDays: 30,
      anonymizeData: false,
      secureProcessing: true,
    }
    setSettings(defaultSettings)
    setHasUnsavedChanges(true)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-serif font-bold text-foreground">Analysis Settings</h2>
          <p className="text-muted-foreground">Configure how your text analysis is performed</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleReset}>
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset to Defaults
          </Button>
          <Button 
            onClick={handleSave}
            disabled={!hasUnsavedChanges}
            className="bg-secondary hover:bg-secondary/90"
          >
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>

      {/* Analysis Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Analysis Configuration
          </CardTitle>
          <CardDescription>Default settings for text analysis algorithms</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Label>Default Topic Count: {settings.defaultTopicCount}</Label>
            <Slider
              value={[settings.defaultTopicCount]}
              onValueChange={(value) => updateSetting('defaultTopicCount', value[0])}
              max={20}
              min={2}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              Number of topics to extract by default (can be overridden per analysis)
            </p>
          </div>

          <div className="space-y-3">
            <Label>Sentiment Threshold: {settings.sentimentThreshold}</Label>
            <Slider
              value={[settings.sentimentThreshold]}
              onValueChange={(value) => updateSetting('sentimentThreshold', value[0])}
              max={1}
              min={0}
              step={0.1}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              Minimum confidence level for sentiment classification
            </p>
          </div>

          <div className="space-y-3">
            <Label>Default Summary Length</Label>
            <Select 
              value={settings.summaryLength} 
              onValueChange={(value) => updateSetting('summaryLength', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="short">Short (50-100 words)</SelectItem>
                <SelectItem value="medium">Medium (100-200 words)</SelectItem>
                <SelectItem value="long">Long (200-300 words)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-3">
            <Label>Confidence Threshold: {Math.round(settings.confidenceThreshold * 100)}%</Label>
            <Slider
              value={[settings.confidenceThreshold]}
              onValueChange={(value) => updateSetting('confidenceThreshold', value[0])}
              max={1}
              min={0.5}
              step={0.05}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              Minimum confidence level to display results
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Processing Options */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Processing Options
          </CardTitle>
          <CardDescription>Configure how files and data are processed</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Parallel Processing</Label>
              <p className="text-sm text-muted-foreground">
                Process multiple files simultaneously for faster results
              </p>
            </div>
            <Switch
              checked={settings.enableParallelProcessing}
              onCheckedChange={(checked) => updateSetting('enableParallelProcessing', checked)}
            />
          </div>

          <Separator />

          <div className="space-y-3">
            <Label>Maximum File Size: {settings.maxFileSize} MB</Label>
            <Slider
              value={[settings.maxFileSize]}
              onValueChange={(value) => updateSetting('maxFileSize', value[0])}
              max={100}
              min={1}
              step={1}
              className="w-full"
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Auto-save Results</Label>
              <p className="text-sm text-muted-foreground">
                Automatically save analysis results to prevent data loss
              </p>
            </div>
            <Switch
              checked={settings.autoSaveResults}
              onCheckedChange={(checked) => updateSetting('autoSaveResults', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Notifications
          </CardTitle>
          <CardDescription>Choose when and how you receive notifications</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Email Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Receive email updates about analysis progress
              </p>
            </div>
            <Switch
              checked={settings.emailNotifications}
              onCheckedChange={(checked) => updateSetting('emailNotifications', checked)}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Progress Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Show notifications during analysis processing
              </p>
            </div>
            <Switch
              checked={settings.progressNotifications}
              onCheckedChange={(checked) => updateSetting('progressNotifications', checked)}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Completion Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Notify when analysis is complete
              </p>
            </div>
            <Switch
              checked={settings.completionNotifications}
              onCheckedChange={(checked) => updateSetting('completionNotifications', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Export Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <Download className="w-5 h-5" />
            Export Settings
          </CardTitle>
          <CardDescription>Default options for exporting analysis results</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Label>Default Export Format</Label>
            <Select 
              value={settings.defaultExportFormat} 
              onValueChange={(value) => updateSetting('defaultExportFormat', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pdf">PDF Report</SelectItem>
                <SelectItem value="excel">Excel Workbook</SelectItem>
                <SelectItem value="json">JSON Data</SelectItem>
                <SelectItem value="csv">CSV Data</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Include Raw Data</Label>
              <p className="text-sm text-muted-foreground">
                Include detailed data tables in exports
              </p>
            </div>
            <Switch
              checked={settings.includeRawData}
              onCheckedChange={(checked) => updateSetting('includeRawData', checked)}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Include Visualizations</Label>
              <p className="text-sm text-muted-foreground">
                Include charts and graphs in exports
              </p>
            </div>
            <Switch
              checked={settings.includeVisualizations}
              onCheckedChange={(checked) => updateSetting('includeVisualizations', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Privacy & Security */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Privacy & Security
          </CardTitle>
          <CardDescription>Control how your data is handled and stored</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <Label>Data Retention: {settings.dataRetentionDays} days</Label>
            <Slider
              value={[settings.dataRetentionDays]}
              onValueChange={(value) => updateSetting('dataRetentionDays', value[0])}
              max={365}
              min={7}
              step={7}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              How long to keep analysis results and uploaded files
            </p>
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Anonymize Data</Label>
              <p className="text-sm text-muted-foreground">
                Remove personally identifiable information from text
              </p>
            </div>
            <Switch
              checked={settings.anonymizeData}
              onCheckedChange={(checked) => updateSetting('anonymizeData', checked)}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label className="font-medium">Secure Processing</Label>
              <p className="text-sm text-muted-foreground">
                Use encrypted processing for sensitive data
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge className="bg-green-500 text-white text-xs">Enabled</Badge>
              <Switch
                checked={settings.secureProcessing}
                onCheckedChange={(checked) => updateSetting('secureProcessing', checked)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Save Changes Banner */}
      {hasUnsavedChanges && (
        <Card className="border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20 dark:border-yellow-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
                <span className="font-medium">You have unsaved changes</span>
              </div>
              <Button 
                onClick={handleSave}
                size="sm"
                className="bg-secondary hover:bg-secondary/90"
              >
                <Save className="w-4 h-4 mr-2" />
                Save Now
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
