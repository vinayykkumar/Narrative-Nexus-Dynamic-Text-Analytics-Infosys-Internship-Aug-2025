"use client"

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { TrendingUp, BarChart3, PieChart as PieIcon, Activity } from 'lucide-react'

interface VisualizationProps {
  data?: {
    sentimentTrends?: any[];
    topicDistribution?: any[];
    confidenceScores?: any[];
    emotionalIndicators?: any[];
  }
}

export function AdvancedVisualizations({ data }: VisualizationProps) {
  // Sample data for demonstration
  const sentimentTrendData = data?.sentimentTrends || [
    { time: 'Jan', positive: 65, negative: 20, neutral: 15 },
    { time: 'Feb', positive: 72, negative: 18, neutral: 10 },
    { time: 'Mar', positive: 68, negative: 25, neutral: 7 },
    { time: 'Apr', positive: 78, negative: 15, neutral: 7 },
    { time: 'May', positive: 82, negative: 12, neutral: 6 },
    { time: 'Jun', positive: 75, negative: 18, neutral: 7 },
  ]

  const topicDistributionData = data?.topicDistribution || [
    { name: 'Technology', value: 34, color: '#0088FE' },
    { name: 'Customer Experience', value: 28, color: '#00C49F' },
    { name: 'Business Strategy', value: 18, color: '#FFBB28' },
    { name: 'Product Development', value: 12, color: '#FF8042' },
    { name: 'Financial Performance', value: 8, color: '#8884D8' }
  ]

  const confidenceData = data?.confidenceScores || [
    { category: 'Sentiment Analysis', confidence: 88, accuracy: 92 },
    { category: 'Topic Modeling', confidence: 85, accuracy: 89 },
    { category: 'Text Classification', confidence: 91, accuracy: 87 },
    { category: 'Entity Recognition', confidence: 79, accuracy: 84 },
    { category: 'Summarization', confidence: 76, accuracy: 81 }
  ]

  const emotionalData = data?.emotionalIndicators || [
    { emotion: 'Joy', current: 68, previous: 62, change: 6 },
    { emotion: 'Trust', current: 75, previous: 71, change: 4 },
    { emotion: 'Anticipation', current: 58, previous: 55, change: 3 },
    { emotion: 'Surprise', current: 45, previous: 52, change: -7 },
    { emotion: 'Fear', current: 23, previous: 28, change: -5 },
    { emotion: 'Sadness', current: 15, previous: 19, change: -4 }
  ]

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

  return (
    <div className="space-y-6">
      {/* Sentiment Trends Over Time */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Sentiment Trends Over Time
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sentimentTrendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="positive" 
                  stackId="1" 
                  stroke="#00C49F" 
                  fill="#00C49F" 
                  fillOpacity={0.8}
                />
                <Area 
                  type="monotone" 
                  dataKey="neutral" 
                  stackId="1" 
                  stroke="#FFBB28" 
                  fill="#FFBB28" 
                  fillOpacity={0.8}
                />
                <Area 
                  type="monotone" 
                  dataKey="negative" 
                  stackId="1" 
                  stroke="#FF8042" 
                  fill="#FF8042" 
                  fillOpacity={0.8}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Topic Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieIcon className="h-5 w-5" />
              Topic Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={topicDistributionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry: any) => `${entry.name} ${(entry.percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {topicDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Confidence Scores */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Model Confidence & Accuracy
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={confidenceData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="category" 
                    angle={-45}
                    textAnchor="end"
                    height={60}
                    interval={0}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="confidence" fill="#0088FE" name="Confidence %" />
                  <Bar dataKey="accuracy" fill="#00C49F" name="Accuracy %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Emotional Indicators */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Emotional Indicators Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {emotionalData.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="font-medium text-gray-900">{item.emotion}</div>
                  <Badge 
                    variant={item.change > 0 ? "default" : item.change < 0 ? "destructive" : "secondary"}
                    className="text-xs"
                  >
                    {item.change > 0 ? '+' : ''}{item.change}%
                  </Badge>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="text-sm text-gray-500">
                    Previous: {item.previous}%
                  </div>
                  <div className="font-semibold text-lg">
                    {item.current}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Real-time Processing Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Processing Performance Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={[
                  { stage: 'Preprocessing', time: 0.8, accuracy: 98 },
                  { stage: 'Tokenization', time: 1.2, accuracy: 96 },
                  { stage: 'Feature Extraction', time: 2.1, accuracy: 94 },
                  { stage: 'Topic Modeling', time: 3.5, accuracy: 89 },
                  { stage: 'Sentiment Analysis', time: 1.8, accuracy: 92 },
                  { stage: 'Summarization', time: 2.3, accuracy: 87 }
                ]}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="stage" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="time" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  name="Processing Time (s)"
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="accuracy" 
                  stroke="#82ca9d" 
                  strokeWidth={2}
                  name="Accuracy (%)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
