"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { AlertCircle, AlertTriangle, Info } from "lucide-react"

interface Log {
  id: string
  timestamp: string
  level: "INFO" | "WARNING" | "ERROR"
  agent: string
  message: string
}

export function LogsSection() {
  const { toast } = useToast()
  const [logs, setLogs] = useState<Log[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    level: "all" as string,
    agent: "all" as string,
    search: "",
  })
  const [page, setPage] = useState(1)
  const itemsPerPage = 15

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const response = await fetch("http://localhost:8000/dashboard/logs")
      if (!response.ok) throw new Error("Error al obtener registros")
      const data = await response.json()
      setLogs(Array.isArray(data.logs) ? data.logs : [])
    } catch (error) {
      toast({
        title: "Error",
        description: "Error al obtener registros",
        variant: "destructive",
      })
      setLogs([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
    const interval = setInterval(fetchLogs, 30000)

    const handleRefresh = () => fetchLogs()
    window.addEventListener("dashboard-refresh", handleRefresh)

    return () => {
      clearInterval(interval)
      window.removeEventListener("dashboard-refresh", handleRefresh)
    }
  }, [])

  const filteredLogs = logs.filter((log) => {
    if (filters.level !== "all" && log.level !== filters.level) return false
    if (filters.agent !== "all" && log.agent !== filters.agent) return false
    if (filters.search && !log.message.toLowerCase().includes(filters.search.toLowerCase())) return false
    return true
  })

  const paginatedLogs = filteredLogs.slice((page - 1) * itemsPerPage, page * itemsPerPage)

  const uniqueAgents = Array.from(new Set(logs.map((log) => log.agent)))

  const levelColors = {
    INFO: "bg-blue-500",
    WARNING: "bg-yellow-500",
    ERROR: "bg-red-500",
  }

  const levelIcons = {
    INFO: Info,
    WARNING: AlertTriangle,
    ERROR: AlertCircle,
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Registros Recientes</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <select
            value={filters.level}
            onChange={(e) => {
              setFilters({ ...filters, level: e.target.value })
              setPage(1)
            }}
            className="px-3 py-2 rounded-md bg-muted text-foreground text-sm border border-border"
          >
            <option value="all">Todos los Niveles</option>
            <option value="INFO">Información</option>
            <option value="WARNING">Advertencia</option>
            <option value="ERROR">Error</option>
          </select>

          <select
            value={filters.agent}
            onChange={(e) => {
              setFilters({ ...filters, agent: e.target.value })
              setPage(1)
            }}
            className="px-3 py-2 rounded-md bg-muted text-foreground text-sm border border-border"
          >
            <option value="all">Todos los Agentes</option>
            {uniqueAgents.map((agent) => (
              <option key={agent} value={agent}>
                {agent}
              </option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Buscar registros..."
            value={filters.search}
            onChange={(e) => {
              setFilters({ ...filters, search: e.target.value })
              setPage(1)
            }}
            className="px-3 py-2 rounded-md bg-muted text-foreground text-sm border border-border placeholder-muted-foreground flex-1"
          />
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto">
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Cargando registros...</div>
          ) : paginatedLogs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">No se encontraron registros</div>
          ) : (
            paginatedLogs.map((log) => {
              const Icon = levelIcons[log.level]
              return (
                <div
                  key={log.id}
                  className="flex gap-3 p-3 rounded-lg bg-muted/30 border border-border/50 hover:border-primary/50 transition-colors"
                >
                  <div className="flex-shrink-0 mt-1">
                    <Icon className={`w-4 h-4 ${levelColors[log.level].replace("bg-", "text-")}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono text-muted-foreground">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      <Badge className={`${levelColors[log.level]} text-white text-xs`}>
                        {log.level === "INFO" && "Información"}
                        {log.level === "WARNING" && "Advertencia"}
                        {log.level === "ERROR" && "Error"}
                      </Badge>
                      <span className="text-xs text-muted-foreground">{log.agent}</span>
                    </div>
                    <p className="text-sm text-foreground break-words">{log.message}</p>
                  </div>
                </div>
              )
            })
          )}
        </div>

        {filteredLogs.length > itemsPerPage && (
          <div className="flex items-center justify-between pt-4 border-t border-border">
            <p className="text-sm text-muted-foreground">
              Página {page} de {Math.ceil(filteredLogs.length / itemsPerPage)}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-3 py-1 rounded-md bg-muted text-foreground text-sm border border-border hover:bg-muted/80 disabled:opacity-50"
              >
                Anterior
              </button>
              <button
                onClick={() => setPage(Math.min(Math.ceil(filteredLogs.length / itemsPerPage), page + 1))}
                disabled={page === Math.ceil(filteredLogs.length / itemsPerPage)}
                className="px-3 py-1 rounded-md bg-muted text-foreground text-sm border border-border hover:bg-muted/80 disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
