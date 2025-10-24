"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Play, Pause, CheckCircle2 } from "lucide-react"
import { apiClient, Task, isApiError, getErrorMessage } from "@/lib/api"
import { API_CONFIG } from "@/config/api"

export function TasksSection() {
  const { toast } = useToast()
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    status: "all" as string,
    type: "all" as string,
    priority: "all" as string,
  })
  const [page, setPage] = useState(1)
  const itemsPerPage = 10

  const fetchTasks = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getTasks()
      
      if (isApiError(response)) {
        throw new Error(getErrorMessage(response))
      }
      
      setTasks(Array.isArray(response.data?.tasks) ? response.data.tasks : [])
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Error al obtener tareas",
        variant: "destructive",
      })
      setTasks([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTasks()
    const interval = setInterval(fetchTasks, API_CONFIG.REFRESH_INTERVALS.TASKS)

    const handleRefresh = () => fetchTasks()
    window.addEventListener("dashboard-refresh", handleRefresh)

    return () => {
      clearInterval(interval)
      window.removeEventListener("dashboard-refresh", handleRefresh)
    }
  }, [])

  const filteredTasks = tasks.filter((task) => {
    if (filters.status !== "all" && task.status !== filters.status) return false
    if (filters.type !== "all" && task.type !== filters.type) return false
    if (filters.priority !== "all" && task.priority !== Number.parseInt(filters.priority)) return false
    return true
  })

  const paginatedTasks = filteredTasks.slice((page - 1) * itemsPerPage, page * itemsPerPage)

  const statusColors = {
    todo: "bg-gray-500",
    in_progress: "bg-blue-500",
    done: "bg-green-500",
    blocked: "bg-red-500",
  }

  const typeColors = {
    dev: "bg-purple-500",
    ops: "bg-orange-500",
    test: "bg-cyan-500",
  }

  const handleTaskAction = (taskId: string, action: string) => {
    const actionMessages: Record<string, string> = {
      started: "iniciada",
      paused: "pausada",
      completed: "completada",
    }
    toast({
      title: "Acción ejecutada",
      description: `Tarea ${actionMessages[action] || action}`,
    })
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Tareas</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <select
            value={filters.status}
            onChange={(e) => {
              setFilters({ ...filters, status: e.target.value })
              setPage(1)
            }}
            className="px-3 py-2 rounded-md bg-muted text-foreground text-sm border border-border"
          >
            <option value="all">Todos los Estados</option>
            <option value="todo">Por Hacer</option>
            <option value="in_progress">En Progreso</option>
            <option value="done">Completada</option>
            <option value="blocked">Bloqueada</option>
          </select>

          <select
            value={filters.type}
            onChange={(e) => {
              setFilters({ ...filters, type: e.target.value })
              setPage(1)
            }}
            className="px-3 py-2 rounded-md bg-muted text-foreground text-sm border border-border"
          >
            <option value="all">Todos los Tipos</option>
            <option value="dev">Desarrollo</option>
            <option value="ops">Operaciones</option>
            <option value="test">Pruebas</option>
          </select>

          <select
            value={filters.priority}
            onChange={(e) => {
              setFilters({ ...filters, priority: e.target.value })
              setPage(1)
            }}
            className="px-3 py-2 rounded-md bg-muted text-foreground text-sm border border-border"
          >
            <option value="all">Todas las Prioridades</option>
            <option value="1">Prioridad 1</option>
            <option value="2">Prioridad 2</option>
            <option value="3">Prioridad 3</option>
            <option value="4">Prioridad 4</option>
            <option value="5">Prioridad 5</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Tarea</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Estado</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Tipo</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Prioridad</th>
                <th className="text-left py-3 px-4 font-semibold text-muted-foreground">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-muted-foreground">
                    Cargando tareas...
                  </td>
                </tr>
              ) : paginatedTasks.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-muted-foreground">
                    No se encontraron tareas
                  </td>
                </tr>
              ) : (
                paginatedTasks.map((task) => (
                  <tr key={task.id} className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4 text-foreground">{task.name}</td>
                    <td className="py-3 px-4">
                      <Badge className={`${statusColors[task.status]} text-white`}>
                        {task.status === "todo" && "Por Hacer"}
                        {task.status === "in_progress" && "En Progreso"}
                        {task.status === "done" && "Completada"}
                        {task.status === "blocked" && "Bloqueada"}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">
                      <Badge className={`${typeColors[task.type]} text-white`}>
                        {task.type === "dev" && "Desarrollo"}
                        {task.type === "ops" && "Operaciones"}
                        {task.type === "test" && "Pruebas"}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-foreground">P{task.priority}</td>
                    <td className="py-3 px-4 flex gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleTaskAction(task.id, "started")}
                        className="h-8 w-8 p-0"
                        title="Iniciar"
                      >
                        <Play className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleTaskAction(task.id, "paused")}
                        className="h-8 w-8 p-0"
                        title="Pausar"
                      >
                        <Pause className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleTaskAction(task.id, "completed")}
                        className="h-8 w-8 p-0"
                        title="Completar"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {filteredTasks.length > itemsPerPage && (
          <div className="flex items-center justify-between pt-4">
            <p className="text-sm text-muted-foreground">
              Página {page} de {Math.ceil(filteredTasks.length / itemsPerPage)}
            </p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1}>
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(Math.min(Math.ceil(filteredTasks.length / itemsPerPage), page + 1))}
                disabled={page === Math.ceil(filteredTasks.length / itemsPerPage)}
              >
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
