"use client"

import { RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState, useEffect } from "react"

interface DashboardHeaderProps {
  onRefresh: () => void
  isRefreshing: boolean
  lastRefresh: Date
}

export function DashboardHeader({ onRefresh, isRefreshing, lastRefresh }: DashboardHeaderProps) {
  const [systemStatus, setSystemStatus] = useState<"online" | "offline">("online")
  const [time, setTime] = useState<string>("")

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toLocaleTimeString())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch("http://localhost:8000/dashboard/overview")
        setSystemStatus(response.ok ? "online" : "offline")
      } catch {
        setSystemStatus("offline")
      }
    }

    checkStatus()
    const interval = setInterval(checkStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <header className="border-b border-border bg-card">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-foreground">Karl AI Ecosystem</h1>
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-muted">
                <div className={`w-2 h-2 rounded-full ${systemStatus === "online" ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-sm text-muted-foreground capitalize">
                  {systemStatus === "online" ? "En línea" : "Desconectado"}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Última actualización</p>
              <p className="text-sm font-mono text-foreground">{lastRefresh.toLocaleTimeString()}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Hora actual</p>
              <p className="text-sm font-mono text-foreground">{time}</p>
            </div>
            <Button
              onClick={onRefresh}
              disabled={isRefreshing}
              variant="outline"
              size="sm"
              className="gap-2 bg-transparent"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
              Actualizar
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
