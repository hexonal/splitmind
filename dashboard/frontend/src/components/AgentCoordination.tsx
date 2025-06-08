import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Users, 
  MessageSquare, 
  Lock, 
  GitBranch,
  CheckCircle2,
  Clock,
  AlertCircle,
  Info,
  Network
} from 'lucide-react';

interface CoordinationStats {
  enabled: boolean;
  active_agents: number;
  total_todos: number;
  completed_todos: number;
  completion_rate: number;
  shared_interfaces: number;
  recent_changes: number;
  agents?: Record<string, any>;
  interfaces?: string[];
  error?: string;
  message?: string;
}

interface AgentCoordinationProps {
  projectId: string;
}

export function AgentCoordination({ projectId }: AgentCoordinationProps) {
  const { data: stats, isLoading, error } = useQuery<CoordinationStats>({
    queryKey: ['coordination-stats', projectId],
    queryFn: async () => {
      const response = await fetch(`/api/projects/${projectId}/coordination-stats`);
      if (!response.ok) throw new Error('Failed to fetch coordination stats');
      return response.json();
    },
    refetchInterval: 5000, // Refetch every 5 seconds
    enabled: !!projectId,
  });

  if (isLoading) {
    return (
      <Card className="border-electric-cyan/20 bg-card/50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Network className="w-5 h-5 text-electric-cyan" />
            Agent Coordination
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-pulse text-muted-foreground">Loading coordination data...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !stats) {
    return (
      <Card className="border-electric-cyan/20 bg-card/50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Network className="w-5 h-5 text-electric-cyan" />
            Agent Coordination
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert className="border-red-500/20 bg-red-500/5">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <AlertDescription>
              Failed to load coordination data
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!stats.enabled) {
    return (
      <Card className="border-electric-cyan/20 bg-card/50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Network className="w-5 h-5 text-electric-cyan" />
            Agent Coordination
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert className="border-yellow-500/20 bg-yellow-500/5">
            <Info className="h-4 w-4 text-yellow-500" />
            <AlertDescription>
              <strong>A2AMCP coordination not available</strong>
              <p className="text-sm mt-1">
                {stats.message || 'Install and run A2AMCP for enhanced agent coordination'}
              </p>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-electric-cyan/20 bg-card/50">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Network className="w-5 h-5 text-electric-cyan animate-pulse" />
          Agent Coordination
          <Badge variant="secondary" className="ml-auto bg-green-500/10 text-green-500">
            Active
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Active Agents */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm">Active Agents</span>
          </div>
          <Badge variant={stats.active_agents > 0 ? "default" : "secondary"}>
            {stats.active_agents}
          </Badge>
        </div>

        {/* Task Progress */}
        {stats.total_todos > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-muted-foreground" />
                Task Progress
              </span>
              <span className="text-muted-foreground">
                {stats.completed_todos} / {stats.total_todos}
              </span>
            </div>
            <Progress value={stats.completion_rate} className="h-2" />
            <p className="text-xs text-muted-foreground text-right">
              {stats.completion_rate.toFixed(0)}% complete
            </p>
          </div>
        )}

        {/* Shared Interfaces */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm">Shared Interfaces</span>
          </div>
          <Badge variant="outline">{stats.shared_interfaces}</Badge>
        </div>

        {/* Recent Changes */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm">Recent Changes</span>
          </div>
          <Badge variant="outline">{stats.recent_changes}</Badge>
        </div>

        {/* Active Agent List */}
        {stats.agents && Object.keys(stats.agents).length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-muted-foreground" />
              Coordinating Agents
            </h4>
            <div className="space-y-1">
              {Object.entries(stats.agents).map(([name, agent]: [string, any]) => (
                <div key={name} className="flex items-center justify-between text-xs">
                  <span className="font-mono truncate">{name}</span>
                  <Badge variant="secondary" className="text-xs">
                    {agent.task_id}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Shared Interfaces List */}
        {stats.interfaces && stats.interfaces.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium flex items-center gap-2">
              <Lock className="w-4 h-4 text-muted-foreground" />
              Shared Types
            </h4>
            <div className="flex flex-wrap gap-1">
              {stats.interfaces.map((interfaceName) => (
                <Badge key={interfaceName} variant="outline" className="text-xs">
                  {interfaceName}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Error Display */}
        {stats.error && (
          <Alert className="border-yellow-500/20 bg-yellow-500/5">
            <AlertCircle className="h-4 w-4 text-yellow-500" />
            <AlertDescription className="text-xs">
              {stats.error}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}