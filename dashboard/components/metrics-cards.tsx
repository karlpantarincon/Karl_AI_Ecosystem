"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, CheckCircle2, Clock, Zap, TrendingUp, DollarSign } from "lucide-react"

interface MetricsData {
  total_tasks: number
  completed_tasks: number
  in_progress_tasks: number
  active_agents: number
  success_rate: number
  ai_cost_24h: number
}

export function MetricsCards() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMetrics = async () => {
    try {
      setLoading(true)
      const [overviewRes, tasksRes, metricsRes] = await Promise.all([
        fetch("http://localhost:8000/dashboard/overview"),
        fetch("http://localhost:8000/dashboard/tasks"),
        fetch("http://localhost:8000/dashboard/metrics"),
      ])

      if (!overviewRes.ok || !tasksRes.ok || !metricsRes.ok) {
        throw new Error("Error al obtener métricas")
      }

      const overview = await overviewRes.json()
      const tasks = await tasksRes.json()
      const metricsData = await metricsRes.json()

      setMetrics({
        total_tasks: tasks.total || 0,
        completed_tasks: tasks.completed || 0,
        in_progress_tasks: tasks.in_progress || 0,
        active_agents: overview.active_agents || 0,
        success_rate: metricsData.success_rate || 0,
        ai_cost_24h: metricsData.ai_cost_24h || 0,
      })
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al obtener métricas")
      setMetrics(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 30000)

    const handleRefresh = () => fetchMetrics()
    window.addEventListener("dashboard-refresh", handleRefresh)

    return () => {
      clearInterval(interval)
      window.removeEventListener("dashboard-refresh", handleRefresh)
    }
  }, [])

  const metricCards = [
    {
      title: "Total de Tareas",
      value: metrics?.total_tasks ?? "-",
      icon: Activity,
      color: "text-blue-500",
    },
    {
      title: "Completadas",
      value: metrics?.completed_tasks ?? "-",
      icon: CheckCircle2,
      color: "text-green-500",
    },
    {
      title: "En Progreso",
      value: metrics?.in_progress_tasks ?? "-",
      icon: Clock,
      color: "text-yellow-500",
    },
    {
      title: "Agentes Activos",
      value: metrics?.active_agents ?? "-",
      icon: Zap,
      color: "text-purple-500",
    },
    {
      title: "Tasa de Éxito",
      value: `${metrics?.success_rate ?? "-"}%`,
      icon: TrendingUp,
      color: "text-green-500",
    },
    {
      title: "Costo IA (24h)",
      value: `$${metrics?.ai_cost_24h?.toFixed(2) ?? "-"}`,
      icon: DollarSign,
      color: "text-orange-500",
    },
  ]

  if (error) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="col-span-full bg-destructive/10 border-destructive/20">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">{error}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {metricCards.map((metric) => {
        const Icon = metric.icon
        return (
          <Card key={metric.title} className="bg-card border-border hover:border-primary/50 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{metric.title}</CardTitle>
              <Icon className={`w-4 h-4 ${metric.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{loading ? "..." : metric.value}</div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
