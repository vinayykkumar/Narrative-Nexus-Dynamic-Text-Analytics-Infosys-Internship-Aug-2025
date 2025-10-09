"use client"

import type React from "react"

import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Minus, ArrowUp, ArrowDown } from "lucide-react"

interface MetricData {
  title: string
  value: string | number
  change?: string
  changeType?: "increase" | "decrease" | "neutral"
  progress?: number
  icon: React.ComponentType<{ className?: string }>
  color: string
  description?: string
}

interface MetricsDashboardProps {
  metrics: MetricData[]
  title?: string
  description?: string
}

export function MetricsDashboard({ metrics, title = "Key Metrics", description }: MetricsDashboardProps) {
  const getChangeIcon = (changeType?: string) => {
    switch (changeType) {
      case "increase":
        return <ArrowUp className="w-3 h-3 text-green-500" />
      case "decrease":
        return <ArrowDown className="w-3 h-3 text-red-500" />
      default:
        return <Minus className="w-3 h-3 text-gray-500" />
    }
  }

  const getChangeColor = (changeType?: string) => {
    switch (changeType) {
      case "increase":
        return "text-green-600"
      case "decrease":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  return (
    <div className="space-y-4">
      {title && (
        <div>
          <h3 className="text-lg font-serif font-semibold">{title}</h3>
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => {
          const Icon = metric.icon
          return (
            <Card key={index} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-2 rounded-lg bg-opacity-10`} style={{ backgroundColor: `${metric.color}20` }}>
                    <Icon className={`w-5 h-5`} style={{ color: metric.color }} />
                  </div>
                  {metric.change && (
                    <div className={`flex items-center gap-1 text-sm ${getChangeColor(metric.changeType)}`}>
                      {getChangeIcon(metric.changeType)}
                      <span>{metric.change}</span>
                    </div>
                  )}
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-medium text-muted-foreground">{metric.title}</p>
                  <p className="text-2xl font-bold">{metric.value}</p>
                  {metric.description && <p className="text-xs text-muted-foreground">{metric.description}</p>}
                </div>

                {metric.progress !== undefined && (
                  <div className="mt-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs text-muted-foreground">Progress</span>
                      <span className="text-xs text-muted-foreground">{metric.progress}%</span>
                    </div>
                    <Progress value={metric.progress} className="h-2" />
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
