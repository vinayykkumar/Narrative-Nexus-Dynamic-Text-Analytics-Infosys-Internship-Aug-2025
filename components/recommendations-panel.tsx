"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Target, Clock, Users, TrendingUp, DollarSign, CheckCircle } from "lucide-react"

export function RecommendationsPanel() {
  const recommendations = [
    {
      id: 1,
      priority: "High",
      category: "Strategic Communication",
      title: "Enhance Technology Leadership Messaging",
      description:
        "Leverage the strong positive sentiment (85%) around technology topics by developing targeted content that reinforces innovation leadership position.",
      expectedImpact: "Increase brand perception and market positioning",
      timeframe: "2-4 weeks",
      effort: "Medium",
      resources: ["Content Team", "Marketing", "Product"],
      kpis: ["Brand sentiment", "Share of voice", "Engagement rates"],
      status: "recommended",
      icon: TrendingUp,
      color: "text-green-600",
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
    },
    {
      id: 2,
      priority: "High",
      category: "Financial Communication",
      title: "Improve Financial Performance Messaging",
      description:
        "Address mixed sentiment (35% positive) in financial discussions through clearer communication of financial strategy and performance metrics.",
      expectedImpact: "Improved investor confidence and stakeholder trust",
      timeframe: "1-2 weeks",
      effort: "High",
      resources: ["Finance Team", "IR Team", "Communications"],
      kpis: ["Investor sentiment", "Media coverage", "Analyst ratings"],
      status: "urgent",
      icon: DollarSign,
      color: "text-red-600",
      bgColor: "bg-red-50",
      borderColor: "border-red-200",
    },
    {
      id: 3,
      priority: "Medium",
      category: "Customer Experience",
      title: "Amplify Customer Success Stories",
      description:
        "Build on strong customer satisfaction sentiment (78%) by creating case studies and testimonials that showcase customer success.",
      expectedImpact: "Enhanced customer acquisition and retention",
      timeframe: "3-6 weeks",
      effort: "Medium",
      resources: ["Customer Success", "Marketing", "Content"],
      kpis: ["Customer acquisition", "NPS scores", "Testimonial engagement"],
      status: "recommended",
      icon: Users,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      borderColor: "border-blue-200",
    },
    {
      id: 4,
      priority: "Medium",
      category: "Strategic Planning",
      title: "Clarify Business Strategy Communication",
      description:
        "Address neutral sentiment (45%) in strategy discussions by developing clearer, more compelling strategic narratives.",
      expectedImpact: "Better stakeholder alignment and understanding",
      timeframe: "4-8 weeks",
      effort: "High",
      resources: ["Strategy Team", "Communications", "Leadership"],
      kpis: ["Message clarity", "Stakeholder feedback", "Internal alignment"],
      status: "in-review",
      icon: Target,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
      borderColor: "border-purple-200",
    },
  ]

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "High":
        return "bg-red-500"
      case "Medium":
        return "bg-yellow-500"
      case "Low":
        return "bg-green-500"
      default:
        return "bg-gray-500"
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "urgent":
        return "bg-red-500 text-white"
      case "recommended":
        return "bg-blue-500 text-white"
      case "in-review":
        return "bg-yellow-500 text-white"
      case "approved":
        return "bg-green-500 text-white"
      default:
        return "bg-gray-500 text-white"
    }
  }

  const getEffortColor = (effort: string) => {
    switch (effort) {
      case "High":
        return "text-red-600"
      case "Medium":
        return "text-yellow-600"
      case "Low":
        return "text-green-600"
      default:
        return "text-gray-600"
    }
  }

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h3 className="text-lg font-serif font-semibold mb-2">Strategic Recommendations</h3>
        <p className="text-muted-foreground">
          Prioritized action items based on analysis findings, designed to maximize impact and address key
          opportunities.
        </p>
      </div>

      {/* Priority Overview */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card className="text-center">
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-red-600">2</div>
            <div className="text-sm text-muted-foreground">High Priority</div>
          </CardContent>
        </Card>
        <Card className="text-center">
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-yellow-600">2</div>
            <div className="text-sm text-muted-foreground">Medium Priority</div>
          </CardContent>
        </Card>
        <Card className="text-center">
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-green-600">8</div>
            <div className="text-sm text-muted-foreground">Total Actions</div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Recommendations */}
      <div className="space-y-6">
        {recommendations.map((rec) => {
          const Icon = rec.icon
          return (
            <Card key={rec.id} className={`${rec.bgColor} ${rec.borderColor} border-2`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white rounded-lg">
                      <Icon className={`w-5 h-5 ${rec.color}`} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className="text-xs">
                          {rec.category}
                        </Badge>
                        <Badge className={getStatusColor(rec.status)}>{rec.status.replace("-", " ")}</Badge>
                      </div>
                      <CardTitle className="font-serif text-lg">{rec.title}</CardTitle>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${getPriorityColor(rec.priority)}`} />
                    <span className="text-sm font-medium">{rec.priority}</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base mb-4">{rec.description}</CardDescription>

                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Expected Impact:</span>
                      <span className="text-sm text-muted-foreground">High</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Timeframe:</span>
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span className="text-sm text-muted-foreground">{rec.timeframe}</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Effort Level:</span>
                      <span className={`text-sm font-medium ${getEffortColor(rec.effort)}`}>{rec.effort}</span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <span className="text-sm font-medium mb-2 block">Required Resources:</span>
                      <div className="flex flex-wrap gap-1">
                        {rec.resources.map((resource, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {resource}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <span className="text-sm font-medium mb-2 block">Key KPIs:</span>
                      <div className="flex flex-wrap gap-1">
                        {rec.kpis.map((kpi, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {kpi}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white/50 p-3 rounded-lg mb-4">
                  <h5 className="font-medium text-sm mb-1">Expected Impact:</h5>
                  <p className="text-sm text-muted-foreground">{rec.expectedImpact}</p>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-muted-foreground">Ready to implement</span>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                    <Button size="sm" className="bg-secondary hover:bg-secondary/90">
                      Approve & Start
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Implementation Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif">Implementation Timeline</CardTitle>
          <CardDescription>Suggested sequence for implementing recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                1
              </div>
              <div className="flex-1">
                <h4 className="font-medium">Week 1-2: Financial Communication</h4>
                <p className="text-sm text-muted-foreground">Address urgent financial messaging concerns</p>
              </div>
              <Badge className="bg-red-500 text-white">Urgent</Badge>
            </div>

            <div className="flex items-center gap-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                2
              </div>
              <div className="flex-1">
                <h4 className="font-medium">Week 2-4: Technology Leadership</h4>
                <p className="text-sm text-muted-foreground">Capitalize on innovation sentiment</p>
              </div>
              <Badge className="bg-green-500 text-white">High Impact</Badge>
            </div>

            <div className="flex items-center gap-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                3
              </div>
              <div className="flex-1">
                <h4 className="font-medium">Week 3-6: Customer Success Stories</h4>
                <p className="text-sm text-muted-foreground">Build on customer satisfaction</p>
              </div>
              <Badge className="bg-blue-500 text-white">Medium Priority</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
