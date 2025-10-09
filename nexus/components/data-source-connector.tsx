"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Database, Globe, MessageSquare, FileText, Settings } from "lucide-react"

export function DataSourceConnector() {
  const [selectedSource, setSelectedSource] = useState("")
  const [isConnecting, setIsConnecting] = useState(false)

  const dataSources = [
    {
      id: "api",
      name: "REST API",
      icon: Globe,
      description: "Connect to any REST API endpoint",
      status: "available",
    },
    {
      id: "database",
      name: "Database",
      icon: Database,
      description: "Connect to SQL databases",
      status: "available",
    },
    {
      id: "social",
      name: "Social Media",
      icon: MessageSquare,
      description: "Import from Twitter, Reddit, etc.",
      status: "coming-soon",
    },
    {
      id: "documents",
      name: "Document Store",
      icon: FileText,
      description: "Connect to Google Drive, Dropbox",
      status: "coming-soon",
    },
  ]

  const handleConnect = async () => {
    setIsConnecting(true)
    // Simulate connection process
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setIsConnecting(false)
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {dataSources.map((source) => {
          const Icon = source.icon
          return (
            <Card
              key={source.id}
              className={`cursor-pointer transition-colors ${
                selectedSource === source.id ? "ring-2 ring-secondary" : "hover:bg-muted/30"
              } ${source.status === "coming-soon" ? "opacity-60" : ""}`}
              onClick={() => source.status === "available" && setSelectedSource(source.id)}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-secondary/10 rounded-lg flex items-center justify-center">
                      <Icon className="w-5 h-5 text-secondary" />
                    </div>
                    <div>
                      <h3 className="font-serif font-semibold">{source.name}</h3>
                      <p className="text-sm text-muted-foreground">{source.description}</p>
                    </div>
                  </div>
                  {source.status === "coming-soon" && (
                    <Badge variant="outline" className="text-xs">
                      Soon
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {selectedSource && (
        <Card>
          <CardHeader>
            <CardTitle className="font-serif flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Configure Connection
            </CardTitle>
            <CardDescription>Set up your data source connection parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {selectedSource === "api" && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="api-url">API Endpoint URL</Label>
                  <Input id="api-url" placeholder="https://api.example.com/data" type="url" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="api-method">HTTP Method</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select method" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="GET">GET</SelectItem>
                        <SelectItem value="POST">POST</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="api-auth">Authentication</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Auth type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="bearer">Bearer Token</SelectItem>
                        <SelectItem value="api-key">API Key</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </>
            )}

            {selectedSource === "database" && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="db-type">Database Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select database" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="postgresql">PostgreSQL</SelectItem>
                      <SelectItem value="mysql">MySQL</SelectItem>
                      <SelectItem value="mongodb">MongoDB</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="db-connection">Connection String</Label>
                  <Input
                    id="db-connection"
                    placeholder="postgresql://user:password@host:port/database"
                    type="password"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="db-query">SQL Query</Label>
                  <Input id="db-query" placeholder="SELECT text_column FROM your_table WHERE..." />
                </div>
              </>
            )}

            <Button
              onClick={handleConnect}
              disabled={isConnecting}
              className="w-full bg-secondary hover:bg-secondary/90"
            >
              {isConnecting ? "Connecting..." : "Test Connection"}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
