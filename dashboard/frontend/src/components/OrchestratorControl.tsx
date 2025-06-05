import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { api } from '@/services/api';
import { Play, Square, Settings } from 'lucide-react';
import { motion } from 'framer-motion';

interface OrchestratorControlProps {
  projectId: string;
}

export function OrchestratorControl({ projectId }: OrchestratorControlProps) {
  const [isConfigOpen, setIsConfigOpen] = useState(false);

  // Fetch orchestrator status
  const { data: status, refetch: refetchStatus } = useQuery({
    queryKey: ['orchestrator-status'],
    queryFn: api.getOrchestratorStatus,
    refetchInterval: 2000,
  });

  // Fetch orchestrator config
  const { data: config, refetch: refetchConfig } = useQuery({
    queryKey: ['orchestrator-config'],
    queryFn: api.getOrchestratorConfig,
  });

  // Start orchestrator
  const startMutation = useMutation({
    mutationFn: () => api.startOrchestrator(projectId),
    onSuccess: () => refetchStatus(),
  });

  // Stop orchestrator
  const stopMutation = useMutation({
    mutationFn: api.stopOrchestrator,
    onSuccess: () => refetchStatus(),
  });

  // Update config
  const updateConfigMutation = useMutation({
    mutationFn: api.updateOrchestratorConfig,
    onSuccess: () => refetchConfig(),
  });

  const isRunning = status?.running && status?.current_project === projectId;

  return (
    <Card className="bg-deep-indigo/50 border-electric-cyan/20 hover:border-electric-cyan/40 transition-all">
      <CardHeader>
        <CardTitle className="text-electric-cyan flex items-center justify-between">
          Orchestrator
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsConfigOpen(!isConfigOpen)}
          >
            <Settings className="w-4 h-4" />
          </Button>
        </CardTitle>
        <CardDescription>AI Agent Control System</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col space-y-4">
          {isRunning ? (
            <Button
              variant="destructive"
              className="w-full"
              onClick={() => stopMutation.mutate()}
              disabled={stopMutation.isPending}
            >
              <Square className="w-4 h-4 mr-2" />
              Stop Orchestrator
            </Button>
          ) : (
            <Button
              variant="glow"
              className="w-full"
              onClick={() => startMutation.mutate()}
              disabled={startMutation.isPending}
            >
              <Play className="w-4 h-4 mr-2" />
              Launch Orchestrator
            </Button>
          )}

          <div className="flex items-center justify-center">
            <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
            <span className="ml-2 text-sm">
              {isRunning ? 'Running' : 'Stopped'}
            </span>
          </div>
        </div>

        {isConfigOpen && config && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-4 pt-4 border-t border-electric-cyan/20"
          >
            <div className="space-y-2">
              <Label htmlFor="max-agents">Max Agents</Label>
              <Input
                id="max-agents"
                type="number"
                value={config.max_concurrent_agents}
                onChange={(e) => updateConfigMutation.mutate({
                  ...config,
                  max_concurrent_agents: parseInt(e.target.value) || 5,
                })}
                className="bg-dark-bg/50 border-electric-cyan/20"
              />
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="auto-merge"
                checked={config.auto_merge}
                onCheckedChange={(checked) => updateConfigMutation.mutate({
                  ...config,
                  auto_merge: checked,
                })}
              />
              <Label htmlFor="auto-merge">Auto-merge completed work</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="enabled"
                checked={config.enabled}
                onCheckedChange={(checked) => updateConfigMutation.mutate({
                  ...config,
                  enabled: checked,
                })}
              />
              <Label htmlFor="enabled">Enable auto-spawning</Label>
            </div>
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
}