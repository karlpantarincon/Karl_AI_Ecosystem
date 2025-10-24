"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Play, Square, Pause } from "lucide-react"
import { apiClient, Agent, isApiError, getErrorMessage } from "@/lib/api"
import { API_CONFIG } from "@/config/api"

export function AgentsSection() {
  const { toast } = useToast()
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)

  const fetchAgents = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getAgents()
      
      if (isApiError(response)) {
        throw new Error(getErrorMessage(response))
      }
      
      setAgents(Array.isArray(response.data?.agents) ? response.data.agents : [])
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Error al obtener agentes",
        variant: "destructive",
      })
      setAgents([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAgents()
    const interval = setInterval(fetchAgents, API_CONFIG.REFRESH_INTERVALS.AGENTS)

    const handleRefresh = () => fetchAgents()
    window.addEventListener("dashboard-refresh", handleRefresh)

    return () => {
      clearInterval(interval)
      window.removeEventListener("dashboard-refresh", handleRefresh)
    }
  }, [])

  const statusColors = {
    running: "bg-green-500",
    stopped: "bg-gray-500",
    paused: "bg-yellow-500",
  }

  const handleAgentAction = (agentId: string, action: string) => {
    const actionMessages: Record<string, string> = {
      started: "iniciado",
      stopped: "detenido",
      paused: "pausado",
    }
    toast({
      title: "Acción del agente",
      description: `Agente ${actionMessages[action] || action}`,
    })
  }

  const formatTime = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString()
    } catch {
      return "N/A"
    }
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Agentes</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading ? (
            <div className="col-span-full text-center py-8 text-muted-foreground">Cargando agentes...</div>
          ) : agents.length === 0 ? (
            <div className="col-span-full text-center py-8 text-muted-foreground">No se encontraron agentes</div>
          ) : (
            agents.map((agent) => (
              <div
                key={agent.id}
                className="p-4 rounded-lg border border-border bg-muted/30 hover:border-primary/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-foreground">{agent.name}</h3>
                    <Badge className={`${statusColors[agent.status]} text-white mt-1`}>
                      {agent.status === "running" && "Ejecutándose"}
                      {agent.status === "stopped" && "Detenido"}
                      {agent.status === "paused" && "Pausado"}
                    </Badge>
                  </div>
                </div>

                <div className="space-y-2 mb-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Último latido:</span>
                    <span className="text-foreground font-mono">{formatTime(agent.last_heartbeat)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Tareas (24h):</span>
                    <span className="text-foreground font-semibold">{agent.tasks_completed_24h}</span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleAgentAction(agent.id, "started")}
                    className="flex-1 h-8"
                    title="Iniciar"
                  >
                    <Play className="w-4 h-4 mr-1" />
                    Iniciar
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleAgentAction(agent.id, "stopped")}
                    className="flex-1 h-8"
                    title="Detener"
                  >
                    <Square className="w-4 h-4 mr-1" />
                    Detener
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleAgentAction(agent.id, "paused")}
                    className="flex-1 h-8"
                    title="Pausar"
                  >
                    <Pause className="w-4 h-4 mr-1" />
                    Pausar
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
