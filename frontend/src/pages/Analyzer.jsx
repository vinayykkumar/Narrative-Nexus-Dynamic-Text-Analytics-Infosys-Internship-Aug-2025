import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Upload, FileText, BarChart3 } from "lucide-react";

export default function Analyzer() {
  const [text, setText] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setAnalysis(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error("Error analyzing text:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card className="shadow-lg border-0">
          <CardContent className="p-6 space-y-4">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-blue-600" />
              SmartInsights Analyzer
            </h1>

            <textarea
              className="w-full p-4 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none resize-none"
              rows={6}
              placeholder="Paste your text here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />

            <Button
              onClick={handleAnalyze}
              disabled={loading || !text.trim()}
              className="w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <FileText className="w-5 h-5" />
                  Generate Analysis
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {analysis && (
          <Card className="shadow-lg border-0">
            <CardContent className="p-6 space-y-4">
              <h2 className="text-xl font-semibold">Analysis Results</h2>
              <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                {JSON.stringify(analysis, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
