import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Terminal, Cpu, Clock, GitBranch, ExternalLink } from 'lucide-react';
import { api } from '@/services/api';
import { Agent } from '@/types';
import { motion } from 'framer-motion';
// Remove date-fns import - using custom function instead

interface AgentMonitorProps {
  projectId: string;
}

export function AgentMonitor({ projectId }: AgentMonitorProps) {
  // Fetch agents
  const { data: agents = [], isLoading } = useQuery({
    queryKey: ['agents', projectId],
    queryFn: () => api.getAgents(projectId),
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  const handleLaunchITerm = async (agentId: string) => {
    try {
      await api.launchITerm(projectId, agentId);
    } catch (error) {
      console.error('Failed to launch iTerm:', error);
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
        <Badge variant="glow" className="text-lg px-4 py-1">
          {agents.filter(a => a.status === 'running').length} Active
        </Badge>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {agents.map((agent, index) => (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <AgentCard agent={agent} onLaunchITerm={handleLaunchITerm} />
          </motion.div>
        ))}
      </div>
    </div>
  );
}

interface AgentCardProps {
  agent: Agent;
  onLaunchITerm: (agentId: string) => void;
}

function AgentCard({ agent, onLaunchITerm }: AgentCardProps) {
  const isRunning = agent.status === 'running';

  return (
    <Card className="bg-deep-indigo/50 border-electric-cyan/20 hover:border-electric-cyan/40 transition-all hover:shadow-[0_0_30px_rgba(0,255,255,0.3)]">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-500' : 'bg-yellow-500'} animate-pulse`} />
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
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <GitBranch className="w-4 h-4 text-electric-cyan" />
            <span className="text-muted-foreground">Branch:</span>
            <span className="font-mono">{agent.branch}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-electric-cyan" />
            <span className="text-muted-foreground">Started:</span>
            <span>{formatDistanceToNow(new Date(agent.started_at), { addSuffix: true })}</span>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="text-electric-cyan">{agent.progress}%</span>
          </div>
          <Progress value={agent.progress} className="h-2" />
        </div>

        <div className="flex items-center space-x-2 text-sm">
          <Badge variant={isRunning ? 'default' : 'secondary'}>
            {agent.status}
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

// Helper function for date formatting
function formatDistanceToNow(date: Date, options?: { addSuffix?: boolean }): string {
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInMinutes = Math.floor(diffInMs / 60000);
  
  if (diffInMinutes < 1) return 'just now';
  if (diffInMinutes < 60) return `${diffInMinutes}m${options?.addSuffix ? ' ago' : ''}`;
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h${options?.addSuffix ? ' ago' : ''}`;
  
  const diffInDays = Math.floor(diffInHours / 24);
  return `${diffInDays}d${options?.addSuffix ? ' ago' : ''}`;
}