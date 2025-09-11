'use client'

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Upload, 
  FileText, 
  Database, 
  Brain, 
  TrendingUp, 
  BarChart3, 
  FileSpreadsheet,
  ArrowRight,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react';

interface ArchitectureStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  endpoint?: string;
  icon: React.ReactNode;
}

export default function ArchitectureCompliantInterface() {
  const [textInput, setTextInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Architecture flow steps from the diagram
  const architectureSteps: ArchitectureStep[] = [
    {
      id: 'user_interface',
      name: 'User Interface',
      description: 'Web app/Mobile app - Input text data',
      status: 'pending',
      icon: <FileText className="w-5 h-5" />
    },
    {
      id: 'input_handling',
      name: 'Input Data Handling',
      description: 'Upload Text Data - Process and validate input',
      status: 'pending',
      endpoint: '/input/text',
      icon: <Upload className="w-5 h-5" />
    },
    {
      id: 'data_processing',
      name: 'Data Processing',
      description: 'Cleaning, Normalizing - Prepare text for analysis',
      status: 'pending',
      endpoint: '/process/data',
      icon: <Database className="w-5 h-5" />
    },
    {
      id: 'text_storage',
      name: 'Text Data Storage',
      description: 'Store processed text data for analysis',
      status: 'pending',
      icon: <Database className="w-5 h-5" />
    },
    {
      id: 'sentiment_analysis',
      name: 'Sentiment Analysis',
      description: 'Sentiment Detection - Analyze emotional tone',
      status: 'pending',
      endpoint: '/analyze/sentiment',
      icon: <Brain className="w-5 h-5" />
    },
    {
      id: 'topic_modeling',
      name: 'Topic Modeling',
      description: 'LDA, NMF, etc. - Extract themes and topics',
      status: 'pending',
      endpoint: '/analyze/topics',
      icon: <Brain className="w-5 h-5" />
    },
    {
      id: 'insight_generation',
      name: 'Insight Generation and Summarization',
      description: 'Extracted Themes, Key Insights, Recommendations',
      status: 'pending',
      endpoint: '/insights/generate',
      icon: <TrendingUp className="w-5 h-5" />
    },
    {
      id: 'reporting',
      name: 'Reporting Module',
      description: 'Generate Reports - Create comprehensive analysis reports',
      status: 'pending',
      endpoint: '/reports/generate',
      icon: <FileSpreadsheet className="w-5 h-5" />
    },
    {
      id: 'visualization',
      name: 'Visualization Module',
      description: 'Dashboard and charts - Interactive data visualization',
      status: 'pending',
      endpoint: '/dashboard',
      icon: <BarChart3 className="w-5 h-5" />
    }
  ];

  const [steps, setSteps] = useState(architectureSteps);

  const updateStepStatus = (stepId: string, status: ArchitectureStep['status']) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId ? { ...step, status } : step
    ));
  };

  const processArchitectureFlow = async () => {
    if (!textInput.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setCurrentStep(0);

    try {
      // Step 1: User Interface (Complete)
      updateStepStatus('user_interface', 'completed');
      setCurrentStep(1);

      // Step 2: Input Data Handling
      updateStepStatus('input_handling', 'processing');
      const inputResponse = await fetch('http://localhost:8000/input/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: textInput,
          source_type: 'direct'
        })
      });

      if (!inputResponse.ok) throw new Error('Input handling failed');
      const inputResult = await inputResponse.json();
      setSessionId(inputResult.session_id);
      updateStepStatus('input_handling', 'completed');
      
      await delay(1000);
      setCurrentStep(2);

      // Step 3: Data Processing & Storage
      updateStepStatus('data_processing', 'processing');
      const processResponse = await fetch(`http://localhost:8000/process/data/${inputResult.session_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      if (!processResponse.ok) throw new Error('Data processing failed');
      await processResponse.json();
      updateStepStatus('data_processing', 'completed');
      updateStepStatus('text_storage', 'completed');
      
      await delay(1000);
      setCurrentStep(4);

      // Step 4: Sentiment Analysis
      updateStepStatus('sentiment_analysis', 'processing');
      const sentimentResponse = await fetch(`http://localhost:8000/analyze/sentiment/${inputResult.session_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      if (!sentimentResponse.ok) throw new Error('Sentiment analysis failed');
      await sentimentResponse.json();
      updateStepStatus('sentiment_analysis', 'completed');
      
      await delay(1000);
      setCurrentStep(5);

      // Step 5: Topic Modeling
      updateStepStatus('topic_modeling', 'processing');
      const topicResponse = await fetch(`http://localhost:8000/analyze/topics/${inputResult.session_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      if (!topicResponse.ok) throw new Error('Topic modeling failed');
      await topicResponse.json();
      updateStepStatus('topic_modeling', 'completed');
      
      await delay(1000);
      setCurrentStep(6);

      // Step 6: Insight Generation
      updateStepStatus('insight_generation', 'processing');
      const insightResponse = await fetch(`http://localhost:8000/insights/generate/${inputResult.session_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!insightResponse.ok) throw new Error('Insight generation failed');
      const insightResult = await insightResponse.json();
      updateStepStatus('insight_generation', 'completed');
      
      await delay(1000);
      setCurrentStep(7);

      // Step 7: Reporting Module
      updateStepStatus('reporting', 'processing');
      const reportResponse = await fetch(`http://localhost:8000/reports/generate/${inputResult.session_id}`);

      if (!reportResponse.ok) throw new Error('Report generation failed');
      const reportResult = await reportResponse.json();
      updateStepStatus('reporting', 'completed');
      
      await delay(1000);
      setCurrentStep(8);

      // Step 8: Visualization Module
      updateStepStatus('visualization', 'processing');
      const dashboardResponse = await fetch(`http://localhost:8000/dashboard/${inputResult.session_id}`);

      if (!dashboardResponse.ok) throw new Error('Dashboard generation failed');
      const dashboardResult = await dashboardResponse.json();
      updateStepStatus('visualization', 'completed');

      // Store final results
      setResults({
        insights: insightResult.insights,
        report: reportResult.report,
        dashboard: dashboardResult.dashboard
      });

      setCurrentStep(8);

    } catch (error) {
      console.error('Architecture flow error:', error);
      setError(error instanceof Error ? error.message : 'An error occurred');
      
      // Mark current step as error
      const currentStepId = steps[currentStep]?.id;
      if (currentStepId) {
        updateStepStatus(currentStepId, 'error');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const getStepStatusIcon = (status: ArchitectureStep['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <div className="w-4 h-4 rounded-full border-2 border-gray-300" />;
    }
  };

  const getProgressPercentage = () => {
    const completedSteps = steps.filter(step => step.status === 'completed').length;
    return (completedSteps / steps.length) * 100;
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI Narrative Nexus - Architecture Compliant Interface
        </h1>
        <p className="text-gray-600">
          Following the exact architecture diagram flow for text analysis
        </p>
      </div>

      <Tabs defaultValue="interface" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="interface">User Interface</TabsTrigger>
          <TabsTrigger value="flow">Architecture Flow</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="interface" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Step 1: User Interface (Web app/Mobile app)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Enter text for analysis
                </label>
                <Textarea
                  placeholder="Enter your text here for comprehensive analysis through the architecture pipeline..."
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  className="min-h-[120px]"
                />
              </div>

              <Button 
                onClick={processArchitectureFlow}
                disabled={isProcessing || !textInput.trim()}
                className="w-full"
                size="lg"
              >
                {isProcessing ? (
                  <>
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                    Processing through Architecture...
                  </>
                ) : (
                  <>
                    Start Architecture Flow
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>

              {error && (
                <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              )}

              {sessionId && (
                <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                  <strong>Session ID:</strong> {sessionId}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="flow" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Architecture Flow Progress</CardTitle>
              <div className="space-y-2">
                <Progress value={getProgressPercentage()} className="h-2" />
                <p className="text-sm text-gray-600">
                  {steps.filter(s => s.status === 'completed').length} of {steps.length} steps completed
                </p>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {steps.map((step, index) => (
                  <div key={step.id} className="flex items-start gap-4 p-4 rounded-lg border">
                    <div className="flex items-center gap-2 min-w-0">
                      {getStepStatusIcon(step.status)}
                      {step.icon}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-sm">{step.name}</h3>
                        <Badge 
                          variant={
                            step.status === 'completed' ? 'default' :
                            step.status === 'processing' ? 'secondary' :
                            step.status === 'error' ? 'destructive' : 'outline'
                          }
                          className="text-xs"
                        >
                          {step.status}
                        </Badge>
                        {index === currentStep && isProcessing && (
                          <Badge variant="secondary" className="text-xs animate-pulse">
                            Current
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{step.description}</p>
                      {step.endpoint && (
                        <code className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          {step.endpoint}
                        </code>
                      )}
                    </div>

                    {index < steps.length - 1 && (
                      <ArrowRight className="w-4 h-4 text-gray-400 mt-1" />
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-6">
          {results ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Architecture Flow Complete ✅</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-green-600 mb-4">
                    Successfully completed all steps in the architecture diagram!
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <TrendingUp className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                      <div className="font-semibold">Insights Generated</div>
                      <div className="text-2xl font-bold text-blue-600">
                        {results.insights?.key_insights?.length || 0}
                      </div>
                    </div>
                    
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <FileSpreadsheet className="w-8 h-8 mx-auto mb-2 text-green-600" />
                      <div className="font-semibold">Report Generated</div>
                      <div className="text-sm text-green-600">
                        {results.report ? 'Complete' : 'Processing'}
                      </div>
                    </div>
                    
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <BarChart3 className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                      <div className="font-semibold">Dashboard Ready</div>
                      <div className="text-sm text-purple-600">
                        {results.dashboard ? 'Available' : 'Processing'}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {results.insights && (
                <Card>
                  <CardHeader>
                    <CardTitle>Generated Insights</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="text-sm bg-gray-50 p-4 rounded-lg overflow-auto">
                      {JSON.stringify(results.insights, null, 2)}
                    </pre>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">
                  Complete the architecture flow to see results
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
