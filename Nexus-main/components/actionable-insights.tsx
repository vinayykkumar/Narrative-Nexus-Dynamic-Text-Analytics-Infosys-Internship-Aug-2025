"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Progress } from "@/components/ui/progress"
import { CheckCircle, Clock, Users, Calendar, ArrowRight, Plus } from "lucide-react"
import { useState } from "react"

export function ActionableInsights() {
  const [checkedItems, setCheckedItems] = useState<number[]>([])

  const actionItems = [
    {
      id: 1,
      title: "Create Technology Leadership Content Series",
      description:
        "Develop 5-part content series highlighting innovation capabilities based on 85% positive sentiment in tech topics",
      priority: "High",
      effort: "Medium",
      timeline: "2 weeks",
      owner: "Marketing Team",
      category: "Content Strategy",
      impact: "Brand positioning and thought leadership",
      status: "ready",
      dependencies: [],
      resources: ["Content Writer", "Designer", "SME Interview"],
    },
    {
      id: 2,
      title: "Improve Financial Communication Framework",
      description:
        "Develop clearer financial messaging templates to address 35% positive sentiment in financial topics",
      priority: "High",
      effort: "High",
      timeline: "1 week",
      owner: "Finance & IR Team",
      category: "Communications",
      impact: "Investor confidence and stakeholder trust",
      status: "urgent",
      dependencies: ["Legal review", "Executive approval"],
      resources: ["IR Manager", "Communications Lead", "CFO"],
    },
    {
      id: 3,
      title: "Launch Customer Success Story Campaign",
      description: "Create customer testimonial campaign leveraging 78% positive sentiment in customer experience",
      priority: "Medium",
      effort: "Medium",
      timeline: "3 weeks",
      owner: "Customer Success",
      category: "Customer Marketing",
      impact: "Customer acquisition and retention",
      status: "ready",
      dependencies: ["Customer interviews"],
      resources: ["Customer Success Manager", "Video Producer", "Marketing"],
    },
    {
      id: 4,
      title: "Strategic Messaging Workshop",
      description: "Conduct workshop to clarify business strategy messaging (currently 45% positive sentiment)",
      priority: "Medium",
      effort: "Low",
      timeline: "1 week",
      owner: "Strategy Team",
      category: "Internal Alignment",
      impact: "Message consistency and clarity",
      status: "planning",
      dependencies: ["Leadership availability"],
      resources: ["Strategy Lead", "Communications", "Facilitator"],
    },
    {
      id: 5,
      title: "Sentiment Monitoring Dashboard",
      description: "Set up automated monitoring for ongoing sentiment tracking across key topics",
      priority: "Low",
      effort: "Medium",
      timeline: "2 weeks",
      owner: "Analytics Team",
      category: "Infrastructure",
      impact: "Continuous improvement and early warning",
      status: "ready",
      dependencies: ["Tool selection"],
      resources: ["Data Analyst", "Developer", "Marketing Ops"],
    },
    {
      id: 6,
      title: "Product Development Communication Plan",
      description: "Enhance communication around product development to build on 68% positive sentiment",
      priority: "Low",
      effort: "Low",
      timeline: "2 weeks",
      owner: "Product Team",
      category: "Product Marketing",
      impact: "Product adoption and user engagement",
      status: "ready",
      dependencies: [],
      resources: ["Product Marketing", "Product Manager", "Content"],
    },
  ]

  const handleItemCheck = (id: number) => {
    setCheckedItems((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]))
  }

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
      case "ready":
        return "bg-green-500 text-white"
      case "planning":
        return "bg-yellow-500 text-white"
      case "blocked":
        return "bg-gray-500 text-white"
      default:
        return "bg-blue-500 text-white"
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

  const completionRate = (checkedItems.length / actionItems.length) * 100

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h3 className="text-lg font-serif font-semibold mb-2">Action Items</h3>
        <p className="text-muted-foreground">
          Specific, actionable tasks derived from analysis insights, prioritized by impact and urgency.
        </p>
      </div>

      {/* Progress Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="font-serif flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Action Plan Progress
          </CardTitle>
          <CardDescription>Track completion of recommended action items</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4 mb-4">
            <div className="text-center p-3 bg-muted/30 rounded-lg">
              <div className="text-2xl font-bold">{actionItems.length}</div>
              <div className="text-sm text-muted-foreground">Total Actions</div>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {actionItems.filter((item) => item.priority === "High").length}
              </div>
              <div className="text-sm text-red-700">High Priority</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{checkedItems.length}</div>
              <div className="text-sm text-green-700">Completed</div>
            </div>
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{completionRate.toFixed(0)}%</div>
              <div className="text-sm text-blue-700">Progress</div>
            </div>
          </div>
          <Progress value={completionRate} className="h-2" />
        </CardContent>
      </Card>

      {/* Action Items List */}
      <div className="space-y-4">
        {actionItems.map((item) => (
          <Card key={item.id} className={`transition-all ${checkedItems.includes(item.id) ? "opacity-60" : ""}`}>
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <Checkbox
                  id={`action-${item.id}`}
                  checked={checkedItems.includes(item.id)}
                  onCheckedChange={() => handleItemCheck(item.id)}
                  className="mt-1"
                />

                <div className="flex-1">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-serif font-semibold">{item.title}</h4>
                        <div className={`w-3 h-3 rounded-full ${getPriorityColor(item.priority)}`} />
                        <Badge className={getStatusColor(item.status)}>{item.status}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">{item.description}</p>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 mb-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium">Priority:</span>
                        <span
                          className={`font-medium ${item.priority === "High" ? "text-red-600" : item.priority === "Medium" ? "text-yellow-600" : "text-green-600"}`}
                        >
                          {item.priority}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium">Effort:</span>
                        <span className={`font-medium ${getEffortColor(item.effort)}`}>{item.effort}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium">Timeline:</span>
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          <span>{item.timeline}</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium">Owner:</span>
                        <div className="flex items-center gap-1">
                          <Users className="w-3 h-3" />
                          <span>{item.owner}</span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div>
                        <span className="text-sm font-medium mb-1 block">Category:</span>
                        <Badge variant="outline" className="text-xs">
                          {item.category}
                        </Badge>
                      </div>
                      <div>
                        <span className="text-sm font-medium mb-1 block">Expected Impact:</span>
                        <p className="text-xs text-muted-foreground">{item.impact}</p>
                      </div>
                      {item.dependencies.length > 0 && (
                        <div>
                          <span className="text-sm font-medium mb-1 block">Dependencies:</span>
                          <div className="flex flex-wrap gap-1">
                            {item.dependencies.map((dep, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {dep}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium mb-1 block">Required Resources:</span>
                      <div className="flex flex-wrap gap-1">
                        {item.resources.map((resource, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {resource}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Calendar className="w-3 h-3 mr-2" />
                        Schedule
                      </Button>
                      <Button size="sm" className="bg-secondary hover:bg-secondary/90">
                        Start Task
                        <ArrowRight className="w-3 h-3 ml-2" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Add Custom Action */}
      <Card className="border-dashed border-2">
        <CardContent className="p-6 text-center">
          <Plus className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
          <h4 className="font-medium mb-2">Add Custom Action Item</h4>
          <p className="text-sm text-muted-foreground mb-4">
            Create additional action items based on your specific needs
          </p>
          <Button variant="outline">
            <Plus className="w-4 h-4 mr-2" />
            Add Action Item
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
