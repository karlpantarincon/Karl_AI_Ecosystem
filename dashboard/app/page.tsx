"use client"

import { useState } from "react"
import { DashboardHeader } from "@/components/dashboard-header"
import { MetricsCards } from "@/components/metrics-cards"
import { TasksSection } from "@/components/tasks-section"
import { AgentsSection } from "@/components/agents-section"
import { LogsSection } from "@/components/logs-section"
import { Toaster } from "@/components/ui/toaster"
import { useToast } from "@/hooks/use-toast"

export default function Dashboard() {
  const { toast } = useToast()
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      // Trigger a refresh event that child components can listen to
      window.dispatchEvent(new Event("dashboard-refresh"))
      toast({
        title: "Panel actualizado",
        description: "Todos los datos han sido actualizados",
      })
      setLastRefresh(new Date())
    } catch (error) {
      toast({
        title: "Error en la actualización",
        description: "No se pudo actualizar los datos del panel",
        variant: "destructive",
      })
    } finally {
      setIsRefreshing(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader onRefresh={handleRefresh} isRefreshing={isRefreshing} lastRefresh={lastRefresh} />

      <main className="container mx-auto px-4 py-8 space-y-8">
        <MetricsCards />
        <TasksSection />
        <AgentsSection />
        <LogsSection />
      </main>

      <Toaster />
    </div>
  )
}
