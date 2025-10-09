"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Cloud, Download, Palette } from "lucide-react"

interface WordData {
  text: string
  value: number
  color?: string
}

interface WordCloudProps {
  words: WordData[]
  title?: string
  description?: string
  maxWords?: number
}

export function WordCloud({ words, title = "Word Cloud", description, maxWords = 50 }: WordCloudProps) {
  const [selectedWord, setSelectedWord] = useState<string | null>(null)
  const [colorScheme, setColorScheme] = useState("default")

  const colorSchemes = {
    default: ["#6366f1", "#d97706", "#be123c", "#1f2937", "#f59e0b"],
    blue: ["#3b82f6", "#1d4ed8", "#1e40af", "#1e3a8a", "#312e81"],
    green: ["#10b981", "#059669", "#047857", "#065f46", "#064e3b"],
    purple: ["#8b5cf6", "#7c3aed", "#6d28d9", "#5b21b6", "#4c1d95"],
  }

  const getWordSize = (value: number, maxValue: number) => {
    const minSize = 12
    const maxSize = 48
    const ratio = value / maxValue
    return minSize + (maxSize - minSize) * ratio
  }

  const getWordColor = (index: number) => {
    const colors = colorSchemes[colorScheme as keyof typeof colorSchemes]
    return colors[index % colors.length]
  }

  const maxValue = Math.max(...words.map((w) => w.value))
  const displayWords = words.slice(0, maxWords)

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="font-serif flex items-center gap-2">
              <Cloud className="w-5 h-5" />
              {title}
            </CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Palette className="w-4 h-4 mr-2" />
              Colors
            </Button>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="relative min-h-[300px] p-6 bg-muted/20 rounded-lg overflow-hidden">
          <div className="flex flex-wrap items-center justify-center gap-2 h-full">
            {displayWords.map((word, index) => (
              <span
                key={word.text}
                className={`cursor-pointer transition-all duration-200 hover:scale-110 font-medium ${
                  selectedWord === word.text ? "opacity-100 scale-110" : "opacity-80 hover:opacity-100"
                }`}
                style={{
                  fontSize: `${getWordSize(word.value, maxValue)}px`,
                  color: getWordColor(index),
                  lineHeight: 1.2,
                }}
                onClick={() => setSelectedWord(selectedWord === word.text ? null : word.text)}
                title={`${word.text}: ${word.value} occurrences`}
              >
                {word.text}
              </span>
            ))}
          </div>
        </div>

        {selectedWord && (
          <div className="mt-4 p-3 bg-secondary/10 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">"{selectedWord}"</h4>
                <p className="text-sm text-muted-foreground">
                  Appears {words.find((w) => w.text === selectedWord)?.value} times
                </p>
              </div>
              <Badge variant="secondary">
                {(
                  ((words.find((w) => w.text === selectedWord)?.value || 0) /
                    words.reduce((sum, w) => sum + w.value, 0)) *
                  100
                ).toFixed(1)}
                %
              </Badge>
            </div>
          </div>
        )}

        <div className="mt-4 text-xs text-muted-foreground text-center">
          Showing {displayWords.length} of {words.length} words • Click words for details
        </div>
      </CardContent>
    </Card>
  )
}
