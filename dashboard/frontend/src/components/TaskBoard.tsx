import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Plus, GitBranch, RefreshCw } from 'lucide-react';
import { api } from '@/services/api';
import { Task, TaskStatus } from '@/types';
import { motion } from 'framer-motion';
import { AddTaskDialog } from '@/components/AddTaskDialog';
import { TaskDetailsDialog } from '@/components/TaskDetailsDialog';

interface TaskBoardProps {
  projectId: string;
}

const statusColumns = [
  { id: TaskStatus.UNCLAIMED, title: 'TODO', color: 'bg-gray-500' },
  { id: TaskStatus.CLAIMED, title: 'CLAIMED', color: 'bg-blue-500' },
  { id: TaskStatus.IN_PROGRESS, title: 'WORKING', color: 'bg-yellow-500' },
  { id: TaskStatus.COMPLETED, title: 'DONE', color: 'bg-green-500' },
  { id: TaskStatus.MERGED, title: 'MERGED', color: 'bg-purple-500' },
];

export function TaskBoard({ projectId }: TaskBoardProps) {
  const queryClient = useQueryClient();
  const [isAddingTask, setIsAddingTask] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isTaskDetailsOpen, setIsTaskDetailsOpen] = useState(false);

  // Fetch tasks
  const { data: tasks = [], isLoading, refetch } = useQuery({
    queryKey: ['tasks', projectId],
    queryFn: () => api.getTasks(projectId),
  });

  // Update task mutation
  const updateTaskMutation = useMutation({
    mutationFn: ({ taskId, updates }: { taskId: string; updates: Partial<Task> }) =>
      api.updateTask(projectId, taskId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
    },
  });

  // Group tasks by status
  const tasksByStatus = statusColumns.reduce((acc, column) => {
    acc[column.id] = tasks.filter(task => task.status === column.id);
    return acc;
  }, {} as Record<TaskStatus, Task[]>);

  const handleDragStart = (e: React.DragEvent, taskId: string) => {
    e.dataTransfer.setData('taskId', taskId);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, newStatus: TaskStatus) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('taskId');
    updateTaskMutation.mutate({ taskId, updates: { status: newStatus } });
  };

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setIsTaskDetailsOpen(true);
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">Loading tasks...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-electric-cyan">Task Board</h2>
        <div className="flex items-center space-x-2">
          <Button variant="glow" size="sm" onClick={() => refetch()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="glow" size="sm" onClick={() => setIsAddingTask(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Task
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-4">
        {statusColumns.map((column) => (
          <div
            key={column.id}
            className="space-y-2"
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, column.id)}
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-sm uppercase tracking-wider">
                {column.title}
              </h3>
              <Badge variant="glow" className="text-xs">
                {tasksByStatus[column.id].length}
              </Badge>
            </div>

            <ScrollArea className="h-[600px]">
              <div className="space-y-2 pr-3">
                {tasksByStatus[column.id].map((task, index) => (
                  <motion.div
                    key={task.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <TaskCard
                      task={task}
                      onDragStart={handleDragStart}
                      columnColor={column.color}
                      onClick={() => handleTaskClick(task)}
                    />
                  </motion.div>
                ))}
              </div>
            </ScrollArea>
          </div>
        ))}
      </div>

      <AddTaskDialog
        projectId={projectId}
        open={isAddingTask}
        onOpenChange={setIsAddingTask}
      />

      <TaskDetailsDialog
        projectId={projectId}
        task={selectedTask}
        open={isTaskDetailsOpen}
        onOpenChange={setIsTaskDetailsOpen}
      />
    </div>
  );
}

interface TaskCardProps {
  task: Task;
  onDragStart: (e: React.DragEvent, taskId: string) => void;
  columnColor: string;
  onClick: () => void;
}

function TaskCard({ task, onDragStart, columnColor, onClick }: TaskCardProps) {
  return (
    <Card
      draggable
      onDragStart={(e) => onDragStart(e, task.id)}
      onClick={onClick}
      className="group cursor-move bg-deep-indigo/50 border-electric-cyan/20 hover:border-electric-cyan/50 transition-all hover:shadow-[0_0_20px_rgba(0,255,255,0.2)]"
    >
      <CardHeader className="p-3">
        <CardTitle className="text-sm font-medium line-clamp-2">
          {task.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-3 pt-0 space-y-2">
        <div className="flex items-center space-x-2 text-xs">
          <GitBranch className="w-3 h-3 text-electric-cyan" />
          <span className="text-muted-foreground">{task.branch}</span>
        </div>
        {task.session && (
          <Badge variant="outline" className="text-xs">
            {task.session}
          </Badge>
        )}
        <div className={`h-1 w-full rounded-full ${columnColor} opacity-50`} />
      </CardContent>
    </Card>
  );
}