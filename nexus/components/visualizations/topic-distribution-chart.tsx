"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip } from "@/components/ui/chart"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"
import { BarChart3, PieChartIcon, Download, Eye } from "lucide-react"
import { useState } from "react"

interface TopicData {
  name: string
  value: number
  documents: number
  color: string
  keywords: string[]
}

interface TopicDistributionChartProps {
  data: TopicData[]
  title?: string
  description?: string
  chartType?: "bar" | "pie"
}

export function TopicDistributionChart({
  data,
  title = "Topic Distribution",
  description,
  chartType = "bar",
}: TopicDistributionChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)
  const [currentChartType, setCurrentChartType] = useState(chartType)

  const chartConfig = {
    value: {
      label: "Prevalence (%)",
      color: "hsl(var(--chart-1))",
    },
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <h4 className="font-medium mb-2">{data.name}</h4>
          <div className="space-y-1 text-sm">
            <p>Prevalence: {data.value}%</p>
            <p>Documents: {data.documents}</p>
            <div className="flex flex-wrap gap-1 mt-2">
              {data.keywords.slice(0, 3).map((keyword: string, index: number) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {keyword}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      )
    }
    return null
  }

  const PieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <h4 className="font-medium mb-2">{data.name}</h4>
          <div className="space-y-1 text-sm">
            <p>Prevalence: {data.value}%</p>
            <p>Documents: {data.documents}</p>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="font-serif flex items-center gap-2">
              {currentChartType === "bar" ? <BarChart3 className="w-5 h-5" /> : <PieChartIcon className="w-5 h-5" />}
              {title}
            </CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={currentChartType === "bar" ? "default" : "outline"}
              size="sm"
              onClick={() => setCurrentChartType("bar")}
            >
              <BarChart3 className="w-4 h-4" />
            </Button>
            <Button
              variant={currentChartType === "pie" ? "default" : "outline"}
              size="sm"
              onClick={() => setCurrentChartType("pie")}
            >
              <PieChartIcon className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[400px]">
          {currentChartType === "bar" ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} fontSize={12} />
                <YAxis fontSize={12} />
                <ChartTooltip content={<CustomTooltip />} />
                <Bar
                  dataKey="value"
                  fill="var(--color-value)"
                  radius={[4, 4, 0, 0]}
                  onMouseEnter={(_, index) => setActiveIndex(index)}
                  onMouseLeave={() => setActiveIndex(null)}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                  labelLine={false}
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <ChartTooltip content={<PieTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </ChartContainer>

        {/* Topic Legend */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3">
          {data.map((topic, index) => (
            <div
              key={index}
              className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                activeIndex === index ? "bg-secondary/10 border-secondary" : "bg-muted/30 border-border"
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 rounded-full" style={{ backgroundColor: topic.color }} />
                <div>
                  <h4 className="font-medium text-sm">{topic.name}</h4>
                  <p className="text-xs text-muted-foreground">{topic.documents} documents</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-xs">
                  {topic.value}%
                </Badge>
                <Button variant="ghost" size="sm">
                  <Eye className="w-3 h-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
