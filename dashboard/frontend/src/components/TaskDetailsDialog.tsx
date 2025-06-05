import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { api } from '@/services/api';
import { Task, TaskStatus } from '@/types';
import { Edit3, Trash2 } from 'lucide-react';

interface TaskDetailsDialogProps {
  projectId: string;
  task: Task | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TaskDetailsDialog({ projectId, task, open, onOpenChange }: TaskDetailsDialogProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<TaskStatus>(TaskStatus.UNCLAIMED);
  const queryClient = useQueryClient();

  // Initialize form when task changes
  useState(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || '');
      setStatus(task.status);
      setIsEditing(false);
    }
  });

  const updateTaskMutation = useMutation({
    mutationFn: (updates: Partial<Task>) => 
      api.updateTask(projectId, task!.id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
      setIsEditing(false);
    },
    onError: (error: any) => {
      console.error('Failed to update task:', error);
      alert(`Failed to update task: ${error.message}`);
    }
  });

  const deleteTaskMutation = useMutation({
    mutationFn: () => api.deleteTask(projectId, task!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
      onOpenChange(false);
    },
    onError: (error: any) => {
      console.error('Failed to delete task:', error);
      alert(`Failed to delete task: ${error.message}`);
    }
  });

  const handleSave = () => {
    if (!task) return;
    
    const updates: Partial<Task> = {};
    if (title !== task.title) updates.title = title;
    if (description !== task.description) updates.description = description || undefined;
    if (status !== task.status) updates.status = status;
    
    if (Object.keys(updates).length > 0) {
      updateTaskMutation.mutate(updates);
    } else {
      setIsEditing(false);
    }
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this task?')) {
      deleteTaskMutation.mutate();
    }
  };

  if (!task) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[525px] bg-dark-bg/95 border-electric-cyan/20">
        <DialogHeader>
          <DialogTitle className="text-electric-cyan flex items-center justify-between">
            <span>Task Details</span>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsEditing(!isEditing)}
                className="h-8 w-8"
              >
                <Edit3 className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleDelete}
                className="h-8 w-8 text-red-500 hover:text-red-600"
                disabled={deleteTaskMutation.isPending}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </DialogTitle>
          <DialogDescription>
            {isEditing ? 'Edit task details' : 'View task information'}
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="task-title">Title</Label>
            {isEditing ? (
              <Input
                id="task-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="bg-deep-indigo/50 border-electric-cyan/20"
                autoComplete="off"
              />
            ) : (
              <p className="text-sm">{task.title}</p>
            )}
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="task-description">Description</Label>
            {isEditing ? (
              <Textarea
                id="task-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="min-h-[100px] bg-deep-indigo/50 border-electric-cyan/20"
                autoComplete="off"
              />
            ) : (
              <p className="text-sm text-muted-foreground">
                {task.description || 'No description provided'}
              </p>
            )}
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="task-status">Status</Label>
            {isEditing ? (
              <Select value={status} onValueChange={(value) => setStatus(value as TaskStatus)}>
                <SelectTrigger className="bg-deep-indigo/50 border-electric-cyan/20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={TaskStatus.UNCLAIMED}>Unclaimed</SelectItem>
                  <SelectItem value={TaskStatus.CLAIMED}>Claimed</SelectItem>
                  <SelectItem value={TaskStatus.IN_PROGRESS}>In Progress</SelectItem>
                  <SelectItem value={TaskStatus.COMPLETED}>Completed</SelectItem>
                  <SelectItem value={TaskStatus.MERGED}>Merged</SelectItem>
                </SelectContent>
              </Select>
            ) : (
              <p className="text-sm capitalize">{task.status.replace('_', ' ')}</p>
            )}
          </div>
          
          <div className="grid gap-2">
            <Label>Branch</Label>
            <p className="text-sm font-mono">{task.branch}</p>
          </div>
          
          {task.session && (
            <div className="grid gap-2">
              <Label>Session</Label>
              <p className="text-sm font-mono">{task.session}</p>
            </div>
          )}
          
          <div className="grid gap-2">
            <Label>Created</Label>
            <p className="text-sm text-muted-foreground">
              {new Date(task.created_at).toLocaleString()}
            </p>
          </div>
        </div>
        
        <DialogFooter>
          {isEditing ? (
            <>
              <Button
                variant="outline"
                onClick={() => setIsEditing(false)}
                className="border-electric-cyan/20"
              >
                Cancel
              </Button>
              <Button
                variant="glow"
                onClick={handleSave}
                disabled={updateTaskMutation.isPending}
              >
                {updateTaskMutation.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
            </>
          ) : (
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="border-electric-cyan/20"
            >
              Close
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}