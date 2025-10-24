"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { 
  Bot, 
  Activity, 
  Cpu, 
  Database, 
  Clock, 
  CheckCircle2, 
  AlertTriangle,
  TrendingUp,
  Settings,
  Info
} from "lucide-react"
import { apiClient, isApiError, getErrorMessage } from "@/lib/api"
import { API_CONFIG } from "@/config/api"

interface AgentContext {
  agent_id: string
  name: string
  status: string
  capabilities: string[]
  current_task: string | null
  performance_metrics: Record<string, any>
  resource_usage: Record<string, any>
  last_activity: string
  uptime_seconds: number
  version: string
  environment: string
  health_score: number
  context_hash: string
}

interface ProjectContext {
  project_name: string
  project_type: string
  technologies: string[]
  architecture: string
  current_phase: string
  business_rules: string[]
  constraints: string[]
  goals: string[]
  last_updated: string
}

interface SystemInsights {
  total_agents: number
  active_agents: number
  idle_agents: number
  busy_agents: number
  error_agents: number
  average_health_score: number
  system_status: string
  timestamp: string
}

export function AgentContextDashboard() {
  const { toast } = useToast()
  const [agents, setAgents] = useState<AgentContext[]>([])
  const [projectContext, setProjectContext] = useState<ProjectContext | null>(null)
  const [insights, setInsights] = useState<SystemInsights | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

  const fetchAgents = async () => {
    try {
      const response = await apiClient.request('/agent-context/agents')
      if (isApiError(response)) {
        throw new Error(getErrorMessage(response))
      }
      setAgents(response.data?.agents || [])
    } catch (error) {
      console.error('Error fetching agents:', error)
    }
  }

  const fetchProjectContext = async () => {
    try {
      const response = await apiClient.request('/agent-context/project/context')
      if (isApiError(response)) {
        // Project context might not be set
        return
      }
      setProjectContext(response.data)
    } catch (error) {
      console.error('Error fetching project context:', error)
    }
  }

  const fetchInsights = async () => {
    try {
      const response = await apiClient.request('/agent-context/system/insights')
      if (isApiError(response)) {
        throw new Error(getErrorMessage(response))
      }
      setInsights(response.data)
    } catch (error) {
      console.error('Error fetching insights:', error)
    }
  }

  const fetchAllData = async () => {
    setLoading(true)
    try {
      await Promise.all([
        fetchAgents(),
        fetchProjectContext(),
        fetchInsights()
      ])
    } catch (error) {
      toast({
        title: "Error",
        description: "Error al obtener contexto de agentes",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllData()
    const interval = setInterval(fetchAllData, API_CONFIG.REFRESH_INTERVALS.AGENTS)
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'idle': return 'bg-blue-500'
      case 'busy': return 'bg-yellow-500'
      case 'error': return 'bg-red-500'
      case 'offline': return 'bg-gray-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return CheckCircle2
      case 'idle': return Clock
      case 'busy': return Activity
      case 'error': return AlertTriangle
      case 'offline': return Bot
      default: return Bot
    }
  }

  const getHealthScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-500'
    if (score >= 0.6) return 'text-yellow-500'
    return 'text-red-500'
  }

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const formatLastActivity = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Contexto de Agentes</h2>
          <p className="text-muted-foreground">Información detallada y contexto de todos los agentes</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchAllData}
          disabled={loading}
        >
          {loading ? "⏳" : "🔄"} Actualizar
        </Button>
      </div>

      {/* System Insights */}
      {insights && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Insights del Sistema
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-foreground">{insights.total_agents}</div>
                <div className="text-sm text-muted-foreground">Total Agentes</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-500">{insights.active_agents}</div>
                <div className="text-sm text-muted-foreground">Activos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-500">{insights.idle_agents}</div>
                <div className="text-sm text-muted-foreground">Inactivos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-500">{insights.error_agents}</div>
                <div className="text-sm text-muted-foreground">Con Errores</div>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <div>
                <span className="text-sm text-muted-foreground">Health Score Promedio:</span>
                <span className={`ml-2 font-semibold ${getHealthScoreColor(insights.average_health_score)}`}>
                  {(insights.average_health_score * 100).toFixed(1)}%
                </span>
              </div>
              <Badge className={insights.system_status === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'}>
                {insights.system_status === 'healthy' ? '✅ Saludable' : '⚠️ Degradado'}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Project Context */}
      {projectContext && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Contexto del Proyecto
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold text-foreground mb-2">Información Básica</h4>
                <div className="space-y-1 text-sm">
                  <div><span className="text-muted-foreground">Proyecto:</span> {projectContext.project_name}</div>
                  <div><span className="text-muted-foreground">Tipo:</span> {projectContext.project_type}</div>
                  <div><span className="text-muted-foreground">Arquitectura:</span> {projectContext.architecture}</div>
                  <div><span className="text-muted-foreground">Fase:</span> {projectContext.current_phase}</div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-foreground mb-2">Tecnologías</h4>
                <div className="flex flex-wrap gap-1">
                  {projectContext.technologies.map((tech, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {tech}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
            {projectContext.business_rules.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold text-foreground mb-2">Reglas de Negocio</h4>
                <ul className="text-sm space-y-1">
                  {projectContext.business_rules.map((rule, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-muted-foreground">•</span>
                      <span>{rule}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Agents List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="w-5 h-5" />
            Agentes ({agents.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Cargando agentes...
            </div>
          ) : agents.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No hay agentes registrados
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((agent) => {
                const StatusIcon = getStatusIcon(agent.status)
                return (
                  <div
                    key={agent.agent_id}
                    className={`p-4 rounded-lg border border-border bg-muted/30 hover:border-primary/50 transition-colors cursor-pointer ${
                      selectedAgent === agent.agent_id ? 'border-primary' : ''
                    }`}
                    onClick={() => setSelectedAgent(selectedAgent === agent.agent_id ? null : agent.agent_id)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-foreground">{agent.name}</h3>
                        <p className="text-xs text-muted-foreground">{agent.agent_id}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <StatusIcon className="w-4 h-4" />
                        <Badge className={`${getStatusColor(agent.status)} text-white text-xs`}>
                          {agent.status.toUpperCase()}
                        </Badge>
                      </div>
                    </div>

                    <div className="space-y-2 mb-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Health Score:</span>
                        <span className={`font-semibold ${getHealthScoreColor(agent.health_score)}`}>
                          {(agent.health_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Uptime:</span>
                        <span className="text-foreground">{formatUptime(agent.uptime_seconds)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Última Actividad:</span>
                        <span className="text-foreground">{formatLastActivity(agent.last_activity)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Versión:</span>
                        <span className="text-foreground">{agent.version}</span>
                      </div>
                    </div>

                    <div className="mb-3">
                      <h4 className="text-xs font-semibold text-muted-foreground mb-1">Capacidades:</h4>
                      <div className="flex flex-wrap gap-1">
                        {agent.capabilities.map((capability, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {capability}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {agent.current_task && (
                      <div className="mb-3">
                        <h4 className="text-xs font-semibold text-muted-foreground mb-1">Tarea Actual:</h4>
                        <p className="text-sm text-foreground">{agent.current_task}</p>
                      </div>
                    )}

                    {selectedAgent === agent.agent_id && (
                      <div className="mt-3 pt-3 border-t border-border">
                        <h4 className="text-xs font-semibold text-muted-foreground mb-2">Métricas de Rendimiento:</h4>
                        <div className="space-y-1 text-xs">
                          {Object.entries(agent.performance_metrics).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-muted-foreground">{key}:</span>
                              <span className="text-foreground">{value}</span>
                            </div>
                          ))}
                        </div>
                        
                        <h4 className="text-xs font-semibold text-muted-foreground mb-2 mt-3">Uso de Recursos:</h4>
                        <div className="space-y-1 text-xs">
                          {Object.entries(agent.resource_usage).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-muted-foreground">{key}:</span>
                              <span className="text-foreground">{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
