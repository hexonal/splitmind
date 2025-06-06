import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Terminal, Cpu, Clock, GitBranch, ExternalLink, RotateCcw, CheckCircle, XCircle, CircleDot, Monitor } from 'lucide-react';
import { api } from '@/services/api';
import { Agent } from '@/types';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

interface AgentMonitorProps {
  projectId: string;
}

export function AgentMonitor({ projectId }: AgentMonitorProps) {
  const queryClient = useQueryClient();
  const [currentTime, setCurrentTime] = useState(new Date());
  
  // Update time every second for live duration counter
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);
  
  // Fetch agents
  const { data: agents = [], isLoading } = useQuery({
    queryKey: ['agents', projectId],
    queryFn: () => api.getAgents(projectId),
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  const resetTasksMutation = useMutation({
    mutationFn: () => api.resetAgentTasks(projectId),
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['agents', projectId] });
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
    },
  });

  const handleLaunchITerm = async (agentId: string) => {
    try {
      await api.launchITerm(projectId, agentId);
    } catch (error) {
      console.error('Failed to launch iTerm:', error);
    }
  };

  const handleResetAll = () => {
    if (confirm('This will kill all agent sessions and reset their tasks to unclaimed. Are you sure?')) {
      resetTasksMutation.mutate();
    }
  };

  const handleLaunchMonitor = async () => {
    try {
      await api.launchAgentMonitor(projectId);
    } catch (error) {
      console.error('Failed to launch monitor:', error);
      alert('Failed to launch monitor: ' + (error as Error).message);
    }
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">Loading agents...</div>;
  }

  if (agents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <Cpu className="w-16 h-16 text-electric-cyan/50" />
        <h3 className="text-xl font-semibold">No Active Agents</h3>
        <p className="text-muted-foreground">Agents will appear here when spawned</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-electric-cyan">Agent Monitor</h2>
        <div className="flex items-center space-x-4">
          {agents.length > 0 && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLaunchMonitor}
                className="border-electric-cyan/50 text-electric-cyan hover:bg-electric-cyan/10"
              >
                <Monitor className="w-4 h-4 mr-2" />
                Split View
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleResetAll}
                disabled={resetTasksMutation.isPending}
                className="border-red-500/50 text-red-500 hover:bg-red-500/10"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset All Agents
              </Button>
            </>
          )}
          <Badge variant="glow" className="text-lg px-4 py-1">
            {agents.filter(a => a.status === 'running').length} Active
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {agents.map((agent, index) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <AgentCard agent={agent} onLaunchITerm={handleLaunchITerm} currentTime={currentTime} />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

interface AgentCardProps {
  agent: Agent;
  onLaunchITerm: (agentId: string) => void;
  currentTime: Date;
}

function AgentCard({ agent, onLaunchITerm, currentTime }: AgentCardProps) {

  const getStatusColor = () => {
    switch (agent.status) {
      case 'running':
        return 'bg-green-500';
      case 'completed':
        return 'bg-blue-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = () => {
    switch (agent.status) {
      case 'running':
        return <Cpu className="w-4 h-4 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'failed':
        return <XCircle className="w-4 h-4" />;
      default:
        return <CircleDot className="w-4 h-4" />;
    }
  };

  return (
    <Card className="bg-deep-indigo/50 border-electric-cyan/20 hover:border-electric-cyan/40 transition-all hover:shadow-[0_0_30px_rgba(0,255,255,0.3)]">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${getStatusColor()} ${agent.status === 'running' ? 'animate-pulse' : ''}`} />
            <CardTitle className="text-lg">{agent.task_title}</CardTitle>
          </div>
          <Button
            variant="glow"
            size="sm"
            onClick={() => onLaunchITerm(agent.id)}
            className="group"
          >
            <Terminal className="w-4 h-4 mr-2" />
            iTerm
            <ExternalLink className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 gap-3 text-sm">
          <div className="flex items-center space-x-2">
            <GitBranch className="w-4 h-4 text-electric-cyan" />
            <span className="text-muted-foreground">Branch:</span>
            <span className="font-mono">{agent.branch}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-electric-cyan" />
            <span className="text-muted-foreground">Started:</span>
            <span className="font-mono">{formatStartTime(new Date(agent.started_at))}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-yellow-400" />
            <span className="text-muted-foreground">Running:</span>
            <span className="font-mono text-yellow-400">{formatRunningDuration(new Date(agent.started_at), currentTime)}</span>
          </div>
        </div>
        
        {agent.status === 'running' && (
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Cpu className="w-4 h-4 animate-pulse text-green-500" />
            <span>Agent is actively working...</span>
          </div>
        )}
        
        {agent.status === 'completed' && (
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <CheckCircle className="w-4 h-4 text-blue-500" />
            <span>Task completed, waiting for merge</span>
          </div>
        )}

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="text-electric-cyan">{agent.progress}%</span>
          </div>
          <Progress value={agent.progress} className="h-2" />
        </div>

        <div className="flex items-center space-x-2 text-sm">
          <Badge 
            variant={agent.status === 'running' ? 'default' : agent.status === 'completed' ? 'success' : 'destructive'}
            className="flex items-center space-x-1"
          >
            {getStatusIcon()}
            <span className="capitalize">{agent.status}</span>
          </Badge>
          <Badge variant="outline" className="font-mono text-xs">
            {agent.session_name}
          </Badge>
        </div>

        {agent.logs.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-semibold mb-2">Recent Logs</h4>
            <ScrollArea className="h-24 w-full rounded-md border border-electric-cyan/20 bg-dark-bg/50 p-2">
              <div className="space-y-1">
                {agent.logs.slice(-5).map((log, i) => (
                  <p key={i} className="text-xs font-mono text-muted-foreground">
                    {log}
                  </p>
                ))}
              </div>
            </ScrollArea>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Helper functions for date formatting
function formatStartTime(date: Date): string {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit',
    hour12: false 
  });
}

function formatRunningDuration(startTime: Date, currentTime: Date): string {
  const diffInMs = currentTime.getTime() - startTime.getTime();
  const diffInSeconds = Math.floor(diffInMs / 1000);
  
  const hours = Math.floor(diffInSeconds / 3600);
  const minutes = Math.floor((diffInSeconds % 3600) / 60);
  const seconds = diffInSeconds % 60;
  
  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  } else {
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }
}