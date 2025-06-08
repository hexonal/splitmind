import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

interface Agent {
  agent_id: string;
  project_id: string;
  task_id: string;
  branch: string;
  description: string;
  status: string;
  started_at: string;
  last_heartbeat?: string;
  is_alive: boolean;
  todo_count: number;
  completed_todos: number;
  file_locks: string[];
}

interface CoordinationEvent {
  event_type: string;
  project_id: string;
  agent_id: string;
  timestamp: string;
  data: any;
}

interface CoordinationStats {
  project_id: string;
  total_agents: number;
  active_agents: number;
  total_todos: number;
  completed_todos: number;
  todo_completion_rate: number;
  active_file_locks: number;
  agents: Record<string, Agent>;
  file_locks: Record<string, string>;
  communication_graph: Record<string, string[]>;
}

interface AgentCoordinationCenterProps {
  projectId: string;
}

const AgentCoordinationCenter: React.FC<AgentCoordinationCenterProps> = ({ projectId }) => {
  const [stats, setStats] = useState<CoordinationStats | null>(null);
  const [events, setEvents] = useState<CoordinationEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/projects/${projectId}/coordination/live`;
      
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        setIsConnected(true);
        console.log('🔗 Connected to coordination monitoring');
      };
      
      wsRef.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        if (message.type === 'coordination_state' || message.type === 'coordination_update') {
          setStats(message.data);
        } else if (message.type === 'coordination_event') {
          setEvents(prev => [...prev.slice(-49), message.data]);
        }
      };
      
      wsRef.current.onclose = () => {
        setIsConnected(false);
        console.log('🔌 Disconnected from coordination monitoring');
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setIsConnected(false);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [projectId]);

  // Draw live coordination graph
  useEffect(() => {
    if (!stats || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const agents = Object.values(stats.agents);
    if (agents.length === 0) return;

    // Set canvas dimensions
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) * 0.7;

    // Draw agents as nodes in a circle
    agents.forEach((agent, index) => {
      const angle = (index / agents.length) * 2 * Math.PI - Math.PI / 2;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;

      // Agent circle
      ctx.beginPath();
      ctx.arc(x, y, 30, 0, 2 * Math.PI);
      
      // Color based on status
      if (agent.is_alive) {
        ctx.fillStyle = agent.status === 'active' ? '#10b981' : '#f59e0b';
        // Pulsing effect for active agents
        const pulseSize = 30 + Math.sin(Date.now() / 500) * 5;
        ctx.arc(x, y, pulseSize, 0, 2 * Math.PI);
      } else {
        ctx.fillStyle = '#ef4444';
      }
      
      ctx.fill();
      ctx.strokeStyle = '#374151';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Agent label
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(agent.agent_id.split('-')[0], x, y + 4);

      // Todo progress indicator
      if (agent.todo_count > 0) {
        const progress = agent.completed_todos / agent.todo_count;
        const progressY = y + 45;
        
        // Progress bar background
        ctx.fillStyle = '#374151';
        ctx.fillRect(x - 20, progressY, 40, 6);
        
        // Progress bar fill
        ctx.fillStyle = '#10b981';
        ctx.fillRect(x - 20, progressY, 40 * progress, 6);
      }

      // File locks indicator
      if (agent.file_locks.length > 0) {
        ctx.beginPath();
        ctx.arc(x + 20, y - 20, 8, 0, 2 * Math.PI);
        ctx.fillStyle = '#dc2626';
        ctx.fill();
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(agent.file_locks.length.toString(), x + 20, y - 16);
      }

      // Heartbeat indicator
      if (agent.is_alive && agent.last_heartbeat) {
        const timeSinceHeartbeat = Date.now() - new Date(agent.last_heartbeat).getTime();
        if (timeSinceHeartbeat < 5000) { // Show if heartbeat within 5 seconds
          ctx.beginPath();
          ctx.arc(x - 20, y - 20, 5, 0, 2 * Math.PI);
          ctx.fillStyle = '#10b981';
          ctx.fill();
        }
      }
    });

    // Draw communication lines (if any)
    Object.entries(stats.communication_graph).forEach(([sourceAgent, targets]) => {
      const sourceIndex = agents.findIndex(a => a.agent_id === sourceAgent);
      if (sourceIndex === -1) return;

      targets.forEach(targetAgent => {
        const targetIndex = agents.findIndex(a => a.agent_id === targetAgent);
        if (targetIndex === -1) return;

        const sourceAngle = (sourceIndex / agents.length) * 2 * Math.PI - Math.PI / 2;
        const targetAngle = (targetIndex / agents.length) * 2 * Math.PI - Math.PI / 2;
        
        const sourceX = centerX + Math.cos(sourceAngle) * radius;
        const sourceY = centerY + Math.sin(sourceAngle) * radius;
        const targetX = centerX + Math.cos(targetAngle) * radius;
        const targetY = centerY + Math.sin(targetAngle) * radius;

        // Animated communication line
        ctx.beginPath();
        ctx.moveTo(sourceX, sourceY);
        ctx.lineTo(targetX, targetY);
        ctx.strokeStyle = '#8b5cf6';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.lineDashOffset = -Date.now() / 100;
        ctx.stroke();
        ctx.setLineDash([]);
      });
    });

  }, [stats]);

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'agent_registered': return '🤖';
      case 'agent_heartbeat': return '💗';
      case 'todo_created': return '📝';
      case 'todo_completed': return '✅';
      case 'file_locked': return '🔒';
      case 'file_unlocked': return '🔓';
      case 'agent_communication': return '💬';
      case 'task_completed': return '🎉';
      default: return '📡';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (!stats) {
    return (
      <Card className="w-full h-96">
        <CardContent className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-500">Connecting to coordination monitoring...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <div>
                <p className="text-sm font-medium">Active Agents</p>
                <p className="text-2xl font-bold">{stats.active_agents}/{stats.total_agents}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div>
              <p className="text-sm font-medium">Todo Progress</p>
              <p className="text-2xl font-bold">{stats.completed_todos}/{stats.total_todos}</p>
              <p className="text-xs text-gray-500">{stats.todo_completion_rate.toFixed(1)}% complete</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div>
              <p className="text-sm font-medium">File Locks</p>
              <p className="text-2xl font-bold text-red-500">{stats.active_file_locks}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div>
              <p className="text-sm font-medium">Status</p>
              <Badge variant={isConnected ? "default" : "destructive"}>
                {isConnected ? "Live" : "Disconnected"}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard */}
      <Tabs defaultValue="graph" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="graph">🕸️ Live Graph</TabsTrigger>
          <TabsTrigger value="agents">🤖 Agents</TabsTrigger>
          <TabsTrigger value="events">📡 Event Stream</TabsTrigger>
          <TabsTrigger value="files">📁 File Locks</TabsTrigger>
        </TabsList>

        <TabsContent value="graph" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>🎛️ Coordination Command Center</CardTitle>
            </CardHeader>
            <CardContent>
              <canvas
                ref={canvasRef}
                className="w-full h-96 border rounded-lg bg-gray-900"
                style={{ maxWidth: '100%' }}
              />
              <div className="mt-4 text-sm text-gray-500 space-y-1">
                <p>🟢 Active Agent • 🟡 Working • 🔴 Offline</p>
                <p>💗 Recent Heartbeat • 🔴 File Locks • Progress Bars: Todo Completion</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.values(stats.agents).map(agent => (
              <Card key={agent.agent_id} className={`${agent.is_alive ? 'border-green-500' : 'border-red-500'}`}>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center justify-between">
                    <span>🤖 {agent.agent_id}</span>
                    <Badge variant={agent.is_alive ? "default" : "destructive"}>
                      {agent.is_alive ? "Alive" : "Offline"}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-xs space-y-1">
                    <p><strong>Task:</strong> {agent.description}</p>
                    <p><strong>Branch:</strong> {agent.branch}</p>
                    <p><strong>Started:</strong> {new Date(agent.started_at).toLocaleTimeString()}</p>
                    {agent.last_heartbeat && (
                      <p><strong>Last Heartbeat:</strong> {formatTimestamp(agent.last_heartbeat)}</p>
                    )}
                  </div>
                  
                  {/* Todo Progress */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span>Todos</span>
                      <span>{agent.completed_todos}/{agent.todo_count}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full transition-all duration-300" 
                        style={{ 
                          width: agent.todo_count > 0 ? `${(agent.completed_todos / agent.todo_count) * 100}%` : '0%' 
                        }}
                      ></div>
                    </div>
                  </div>

                  {/* File Locks */}
                  {agent.file_locks.length > 0 && (
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-red-600">🔒 File Locks:</p>
                      {agent.file_locks.map(file => (
                        <Badge key={file} variant="destructive" className="text-xs mr-1">
                          {file}
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>📡 Live Event Stream</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-2">
                  {events.slice().reverse().map((event, index) => (
                    <div key={index} className="flex items-start space-x-3 p-2 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
                      <span className="text-lg">{getEventIcon(event.event_type)}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium">{event.agent_id}</span>
                          <span className="text-xs text-gray-500">{formatTimestamp(event.timestamp)}</span>
                        </div>
                        <p className="text-sm text-gray-700 capitalize">{event.event_type.replace('_', ' ')}</p>
                        {event.data && Object.keys(event.data).length > 0 && (
                          <pre className="text-xs text-gray-500 mt-1 font-mono">
                            {JSON.stringify(event.data, null, 2)}
                          </pre>
                        )}
                      </div>
                    </div>
                  ))}
                  {events.length === 0 && (
                    <div className="text-center text-gray-500 py-8">
                      <p>No coordination events yet</p>
                      <p className="text-sm">Events will appear here as agents work</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="files" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>🔒 Active File Locks</CardTitle>
            </CardHeader>
            <CardContent>
              {Object.keys(stats.file_locks).length > 0 ? (
                <div className="space-y-2">
                  {Object.entries(stats.file_locks).map(([file, agent]) => (
                    <div key={file} className="flex items-center justify-between p-3 rounded-lg bg-red-50 border border-red-200">
                      <div className="flex items-center space-x-2">
                        <span className="text-red-500">🔒</span>
                        <span className="font-mono text-sm">{file}</span>
                      </div>
                      <Badge variant="destructive">{agent}</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <span className="text-4xl">🔓</span>
                  <p className="mt-2">No active file locks</p>
                  <p className="text-sm">Files are available for editing</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AgentCoordinationCenter;