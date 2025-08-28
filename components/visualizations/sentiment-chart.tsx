"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip } from "@/components/ui/chart"
import { Button } from "@/components/ui/button"
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Area, AreaChart } from "recharts"
import { BarChart3, TrendingUp, Download, Calendar } from "lucide-react"
import { useState } from "react"

interface SentimentData {
  name: string
  positive: number
  neutral: number
  negative: number
  score: number
}

interface SentimentTimeData {
  time: string
  sentiment: number
  volume: number
}

interface SentimentChartProps {
  data: SentimentData[]
  timeData?: SentimentTimeData[]
  title?: string
  description?: string
  showTimeline?: boolean
}

export function SentimentChart({
  data,
  timeData = [],
  title = "Sentiment Analysis",
  description,
  showTimeline = false,
}: SentimentChartProps) {
  const [activeView, setActiveView] = useState<"distribution" | "timeline">(showTimeline ? "timeline" : "distribution")

  const chartConfig = {
    positive: {
      label: "Positive",
      color: "#10b981",
    },
    neutral: {
      label: "Neutral",
      color: "#6b7280",
    },
    negative: {
      label: "Negative",
      color: "#ef4444",
    },
    sentiment: {
      label: "Sentiment Score",
      color: "hsl(var(--chart-1))",
    },
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <h4 className="font-medium mb-2">{label}</h4>
          <div className="space-y-1 text-sm">
            {payload.map((entry: any, index: number) => (
              <div key={index} className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
                  <span>{entry.dataKey}:</span>
                </div>
                <span className="font-medium">{entry.value}%</span>
              </div>
            ))}
          </div>
        </div>
      )
    }
    return null
  }

  const TimelineTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <h4 className="font-medium mb-2">{label}</h4>
          <div className="space-y-1 text-sm">
            <p>Sentiment Score: {payload[0]?.value?.toFixed(2)}</p>
            {payload[1] && <p>Volume: {payload[1].value}</p>}
          </div>
        </div>
      )
    }
    return null
  }

  const overallSentiment = {
    positive: data.reduce((sum, item) => sum + item.positive, 0) / data.length,
    neutral: data.reduce((sum, item) => sum + item.neutral, 0) / data.length,
    negative: data.reduce((sum, item) => sum + item.negative, 0) / data.length,
    score: data.reduce((sum, item) => sum + item.score, 0) / data.length,
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="font-serif flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              {title}
            </CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          <div className="flex items-center gap-2">
            {showTimeline && (
              <>
                <Button
                  variant={activeView === "distribution" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setActiveView("distribution")}
                >
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Distribution
                </Button>
                <Button
                  variant={activeView === "timeline" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setActiveView("timeline")}
                >
                  <Calendar className="w-4 h-4 mr-2" />
                  Timeline
                </Button>
              </>
            )}
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Overall Sentiment Summary */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{overallSentiment.positive.toFixed(0)}%</div>
            <div className="text-sm text-green-700">Positive</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-600">{overallSentiment.neutral.toFixed(0)}%</div>
            <div className="text-sm text-gray-700">Neutral</div>
          </div>
          <div className="text-center p-3 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{overallSentiment.negative.toFixed(0)}%</div>
            <div className="text-sm text-red-700">Negative</div>
          </div>
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{overallSentiment.score.toFixed(2)}</div>
            <div className="text-sm text-blue-700">Avg Score</div>
          </div>
        </div>

        <ChartContainer config={chartConfig} className="h-[400px]">
          {activeView === "distribution" ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} fontSize={12} />
                <YAxis fontSize={12} />
                <ChartTooltip content={<CustomTooltip />} />
                <Bar dataKey="positive" stackId="a" fill={chartConfig.positive.color} radius={[0, 0, 0, 0]} />
                <Bar dataKey="neutral" stackId="a" fill={chartConfig.neutral.color} radius={[0, 0, 0, 0]} />
                <Bar dataKey="negative" stackId="a" fill={chartConfig.negative.color} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <XAxis dataKey="time" fontSize={12} />
                <YAxis fontSize={12} />
                <ChartTooltip content={<TimelineTooltip />} />
                <Area
                  type="monotone"
                  dataKey="sentiment"
                  stroke={chartConfig.sentiment.color}
                  fill={chartConfig.sentiment.color}
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </ChartContainer>

        {/* Sentiment Insights */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-muted/30 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <h4 className="font-medium">Most Positive</h4>
            </div>
            <p className="text-sm text-muted-foreground">
              {data.sort((a, b) => b.positive - a.positive)[0]?.name} (
              {data.sort((a, b) => b.positive - a.positive)[0]?.positive}% positive)
            </p>
          </div>
          <div className="p-4 bg-muted/30 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-4 h-4 text-blue-500" />
              <h4 className="font-medium">Needs Attention</h4>
            </div>
            <p className="text-sm text-muted-foreground">
              {data.sort((a, b) => b.negative - a.negative)[0]?.name} (
              {data.sort((a, b) => b.negative - a.negative)[0]?.negative}% negative)
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
