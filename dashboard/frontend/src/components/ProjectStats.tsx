import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/services/api';
// ProjectStats type imported from '@/types'
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  GitBranch, 
  CheckCircle2, 
  Circle, 
  Clock, 
  Cpu,
  TrendingUp,
  Activity
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  // Legend - not used currently
} from 'recharts';

interface ProjectStatsProps {
  projectId: string;
}

export function ProjectStats({ projectId }: ProjectStatsProps) {
  // Fetch project stats
  const { data: stats, isLoading } = useQuery({
    queryKey: ['project-stats', projectId],
    queryFn: () => api.getProjectStats(projectId),
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  if (isLoading || !stats) {
    return <div className="flex items-center justify-center h-96">Loading statistics...</div>;
  }

  // Prepare data for charts
  const taskDistribution = [
    { name: 'Unclaimed', value: stats.unclaimed_tasks, color: '#6b7280' },
    { name: 'Claimed', value: stats.claimed_tasks, color: '#3b82f6' },
    { name: 'In Progress', value: stats.in_progress_tasks, color: '#eab308' },
    { name: 'Completed', value: stats.completed_tasks, color: '#22c55e' },
    { name: 'Merged', value: stats.merged_tasks, color: '#a855f7' },
  ].filter(item => item.value > 0);

  const progressData = [
    { name: 'TODO', value: stats.unclaimed_tasks },
    { name: 'WIP', value: stats.claimed_tasks + stats.in_progress_tasks },
    { name: 'Done', value: stats.completed_tasks + stats.merged_tasks },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-electric-cyan mb-6">Project Statistics</h2>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={<Circle className="w-5 h-5" />}
          title="Total Tasks"
          value={stats.total_tasks}
          delay={0}
        />
        <StatCard
          icon={<Cpu className="w-5 h-5" />}
          title="Active Agents"
          value={stats.active_agents}
          delay={0.1}
          accent
        />
        <StatCard
          icon={<CheckCircle2 className="w-5 h-5" />}
          title="Completed"
          value={stats.completed_tasks + stats.merged_tasks}
          delay={0.2}
        />
        <StatCard
          icon={<Clock className="w-5 h-5" />}
          title="In Progress"
          value={stats.in_progress_tasks}
          delay={0.3}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Task Distribution Pie Chart */}
        <Card className="bg-deep-indigo/50 border-electric-cyan/20">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-electric-cyan" />
              <span>Task Distribution</span>
            </CardTitle>
            <CardDescription>Current status of all tasks</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={taskDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {taskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Progress Bar Chart */}
        <Card className="bg-deep-indigo/50 border-electric-cyan/20">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-electric-cyan" />
              <span>Progress Overview</span>
            </CardTitle>
            <CardDescription>Task completion progress</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={progressData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1f3a" />
                <XAxis dataKey="name" stroke="#00ffff" />
                <YAxis stroke="#00ffff" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1a1f3a', 
                    border: '1px solid #00ffff',
                    borderRadius: '8px'
                  }} 
                />
                <Bar dataKey="value" fill="#00ffff" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Activity Timeline */}
      <Card className="bg-deep-indigo/50 border-electric-cyan/20">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-electric-cyan" />
            <span>Activity Summary</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg/50">
              <div className="flex items-center space-x-3">
                <GitBranch className="w-5 h-5 text-electric-cyan" />
                <span>Total Agents Run</span>
              </div>
              <span className="text-2xl font-bold">{stats.total_agents_run}</span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-lg bg-dark-bg/50">
                <div className="text-sm text-muted-foreground">Success Rate</div>
                <div className="text-xl font-bold text-green-500">
                  {stats.total_tasks > 0 
                    ? Math.round(((stats.completed_tasks + stats.merged_tasks) / stats.total_tasks) * 100)
                    : 0}%
                </div>
              </div>
              <div className="p-3 rounded-lg bg-dark-bg/50">
                <div className="text-sm text-muted-foreground">Throughput</div>
                <div className="text-xl font-bold text-electric-cyan">
                  {stats.active_agents} / {stats.total_tasks}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: number;
  delay?: number;
  accent?: boolean;
}

function StatCard({ icon, title, value, delay = 0, accent = false }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
    >
      <Card className={`bg-deep-indigo/50 border-electric-cyan/20 hover:border-electric-cyan/40 transition-all ${
        accent ? 'hover:shadow-[0_0_30px_rgba(0,255,255,0.5)]' : ''
      }`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">{title}</p>
              <p className={`text-3xl font-bold ${accent ? 'text-electric-cyan' : ''}`}>
                {value}
              </p>
            </div>
            <div className={`p-3 rounded-full ${accent ? 'bg-electric-cyan/20' : 'bg-secondary'}`}>
              {icon}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}