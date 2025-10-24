"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  TrendingUp,
  Server,
  Database,
  Cpu,
  HardDrive,
  Wifi
} from "lucide-react"
import { apiClient, isApiError, getErrorMessage } from "@/lib/api"
import { API_CONFIG } from "@/config/api"

interface SystemMetrics {
  timestamp: string
  cpu_percent: number
  memory_percent: number
  memory_used_mb: number
  memory_total_mb: number
  disk_percent: number
  disk_used_gb: number
  disk_total_gb: number
  network_sent_mb: number
  network_recv_mb: number
  load_average: number[]
}

interface ApplicationMetrics {
  timestamp: string
  active_connections: number
  requests_per_minute: number
  response_time_avg: number
  error_rate: number
  cache_hit_ratio: number
  database_connections: number
  queue_size: number
}

interface Alert {
  id: string
  type: string
  severity: string
  status: string
  title: string
  message: string
  timestamp: string
  source: string
  metadata: Record<string, any>
}

export function MonitoringDashboard() {
  const { toast } = useToast()
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null)
  const [appMetrics, setAppMetrics] = useState<ApplicationMetrics | null>(null)
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const fetchSystemMetrics = async () => {
    try {
      const response = await apiClient.request('/monitoring/metrics/system')
      if (isApiError(response)) {
        throw new Error(getErrorMessage(response))
      }
      setSystemMetrics(response.data)
    } catch (error) {
      console.error('Error fetching system metrics:', error)
    }
  }

  const fetchApplicationMetrics = async () => {
    try {
      const response = await apiClient.request('/monitoring/metrics/application')
      if (isApiError(response)) {
        throw new Error(getErrorMessage(response))
      }
      setAppMetrics(response.data)
    } catch (error) {
      console.error('Error fetching application metrics:', error)
    }
  }

  const fetchAlerts = async () => {
    try {
      const response = await apiClient.request('/monitoring/alerts/active')
      if (isApiError(response)) {
        throw new Error(getErrorMessage(response))
      }
      setAlerts(response.data || [])
    } catch (error) {
      console.error('Error fetching alerts:', error)
    }
  }

  const fetchAllMetrics = async () => {
    setLoading(true)
    try {
      await Promise.all([
        fetchSystemMetrics(),
        fetchApplicationMetrics(),
        fetchAlerts()
      ])
    } catch (error) {
      toast({
        title: "Error",
        description: "Error al obtener métricas de monitoreo",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllMetrics()
    
    if (autoRefresh) {
      const interval = setInterval(fetchAllMetrics, API_CONFIG.REFRESH_INTERVALS.METRICS)
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'info': return 'bg-blue-500'
      case 'warning': return 'bg-yellow-500'
      case 'critical': return 'bg-red-500'
      case 'emergency': return 'bg-red-700'
      default: return 'bg-gray-500'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500'
      case 'degraded': return 'bg-yellow-500'
      case 'critical': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const systemCards = [
    {
      title: "CPU Usage",
      value: systemMetrics ? `${systemMetrics.cpu_percent.toFixed(1)}%` : "-",
      icon: Cpu,
      color: systemMetrics && systemMetrics.cpu_percent > 80 ? "text-red-500" : "text-blue-500",
      status: systemMetrics && systemMetrics.cpu_percent > 80 ? "warning" : "normal"
    },
    {
      title: "Memory Usage",
      value: systemMetrics ? `${systemMetrics.memory_percent.toFixed(1)}%` : "-",
      icon: Database,
      color: systemMetrics && systemMetrics.memory_percent > 85 ? "text-red-500" : "text-green-500",
      status: systemMetrics && systemMetrics.memory_percent > 85 ? "warning" : "normal"
    },
    {
      title: "Disk Usage",
      value: systemMetrics ? `${systemMetrics.disk_percent.toFixed(1)}%` : "-",
      icon: HardDrive,
      color: systemMetrics && systemMetrics.disk_percent > 90 ? "text-red-500" : "text-orange-500",
      status: systemMetrics && systemMetrics.disk_percent > 90 ? "critical" : "normal"
    },
    {
      title: "Network",
      value: systemMetrics ? `${(systemMetrics.network_sent_mb + systemMetrics.network_recv_mb).toFixed(1)} MB` : "-",
      icon: Wifi,
      color: "text-purple-500",
      status: "normal"
    }
  ]

  const applicationCards = [
    {
      title: "Active Connections",
      value: appMetrics ? appMetrics.active_connections.toString() : "-",
      icon: Server,
      color: "text-blue-500",
      status: "normal"
    },
    {
      title: "Requests/min",
      value: appMetrics ? appMetrics.requests_per_minute.toString() : "-",
      icon: Activity,
      color: "text-green-500",
      status: "normal"
    },
    {
      title: "Response Time",
      value: appMetrics ? `${appMetrics.response_time_avg.toFixed(2)}s` : "-",
      icon: Clock,
      color: appMetrics && appMetrics.response_time_avg > 2 ? "text-red-500" : "text-blue-500",
      status: appMetrics && appMetrics.response_time_avg > 2 ? "warning" : "normal"
    },
    {
      title: "Error Rate",
      value: appMetrics ? `${appMetrics.error_rate.toFixed(1)}%` : "-",
      icon: XCircle,
      color: appMetrics && appMetrics.error_rate > 5 ? "text-red-500" : "text-green-500",
      status: appMetrics && appMetrics.error_rate > 5 ? "warning" : "normal"
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Monitoreo del Sistema</h2>
          <p className="text-muted-foreground">Métricas en tiempo real del ecosistema Karl AI</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={autoRefresh ? "bg-green-100" : ""}
          >
            {autoRefresh ? "🔄 Auto" : "⏸️ Manual"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchAllMetrics}
            disabled={loading}
          >
            {loading ? "⏳" : "🔄"} Actualizar
          </Button>
        </div>
      </div>

      {/* System Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="w-5 h-5" />
            Métricas del Sistema
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {systemCards.map((card) => {
              const Icon = card.icon
              return (
                <div key={card.title} className="p-4 rounded-lg border border-border bg-muted/30">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium text-muted-foreground">{card.title}</h3>
                    <Icon className={`w-4 h-4 ${card.color}`} />
                  </div>
                  <div className="text-2xl font-bold text-foreground">{card.value}</div>
                  {card.status !== "normal" && (
                    <Badge className={`${getStatusColor(card.status)} text-white text-xs mt-1`}>
                      {card.status === "warning" ? "⚠️ Warning" : "🚨 Critical"}
                    </Badge>
                  )}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Application Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Métricas de la Aplicación
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {applicationCards.map((card) => {
              const Icon = card.icon
              return (
                <div key={card.title} className="p-4 rounded-lg border border-border bg-muted/30">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium text-muted-foreground">{card.title}</h3>
                    <Icon className={`w-4 h-4 ${card.color}`} />
                  </div>
                  <div className="text-2xl font-bold text-foreground">{card.value}</div>
                  {card.status !== "normal" && (
                    <Badge className={`${getStatusColor(card.status)} text-white text-xs mt-1`}>
                      {card.status === "warning" ? "⚠️ Warning" : "🚨 Critical"}
                    </Badge>
                  )}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Alerts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Alertas Activas ({alerts.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {alerts.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <CheckCircle2 className="w-12 h-12 mx-auto mb-4 text-green-500" />
              <p>No hay alertas activas</p>
            </div>
          ) : (
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="p-4 rounded-lg border border-border bg-muted/30 hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className={`${getSeverityColor(alert.severity)} text-white`}>
                        {alert.severity.toUpperCase()}
                      </Badge>
                      <span className="text-sm text-muted-foreground">{alert.source}</span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <h4 className="font-semibold text-foreground mb-1">{alert.title}</h4>
                  <p className="text-sm text-muted-foreground">{alert.message}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
