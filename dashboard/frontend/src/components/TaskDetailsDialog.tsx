import { useState, useEffect } from 'react';
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
import { Edit3, Trash2, RotateCcw, GitMerge } from 'lucide-react';

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
  const [prompt, setPrompt] = useState('');
  const [branch, setBranch] = useState('');
  const [status, setStatus] = useState<TaskStatus>(TaskStatus.UNCLAIMED);
  const queryClient = useQueryClient();

  // Generate the full prompt that would be sent to Claude
  const generateFullPrompt = (task: Task, customPrompt?: string) => {
    if (customPrompt) {
      // Use custom prompt with task context
      let fullPrompt = customPrompt;
      fullPrompt += `\n\nTask: ${task.title}`;
      if (task.description) {
        fullPrompt += `\nDescription: ${task.description}`;
      }
      return fullPrompt;
    } else {
      // Use default prompt
      let fullPrompt = `Create a plan, review your plan and choose the best option, then accomplish the following task and commit the changes: ${task.title}`;
      if (task.description) {
        fullPrompt += `\n\nDescription: ${task.description}`;
      }
      return fullPrompt;
    }
  };

  // Initialize form when task changes
  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || '');
      // Show the full prompt that would be sent to Claude
      setPrompt(generateFullPrompt(task, task.prompt));
      setBranch(task.branch);
      setStatus(task.status);
      setIsEditing(false);
    }
  }, [task]);

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

  const mergeTaskMutation = useMutation({
    mutationFn: () => api.mergeTask(projectId, task!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
      onOpenChange(false);
    },
    onError: (error: any) => {
      console.error('Failed to merge task:', error);
      alert(`Failed to merge task: ${error.message}`);
    }
  });

  const handleSave = () => {
    if (!task) return;
    
    const updates: Partial<Task> = {};
    if (title !== task.title) updates.title = title;
    if (description !== task.description) updates.description = description || undefined;
    
    // Extract custom prompt by removing the default structure
    const defaultPrompt = generateFullPrompt({ ...task, title, description: description || task.description }, undefined);
    let customPrompt = prompt;
    
    // If the prompt matches the default structure, don't save a custom prompt
    if (prompt === defaultPrompt) {
      customPrompt = '';
    } else {
      // Try to extract just the custom part if user edited the full prompt
      const taskSection = `\n\nTask: ${title}`;
      const descSection = (description || task.description) ? `\nDescription: ${description || task.description}` : '';
      const contextSuffix = taskSection + descSection;
      
      if (prompt.endsWith(contextSuffix)) {
        customPrompt = prompt.replace(contextSuffix, '');
      }
    }
    
    if (customPrompt !== (task.prompt || '')) updates.prompt = customPrompt || undefined;
    if (branch !== task.branch) updates.branch = branch;
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

  const handleReset = () => {
    if (!task) return;
    
    if (confirm('Are you sure you want to reset this task? This will set it back to unclaimed and clear the session.')) {
      updateTaskMutation.mutate({
        status: TaskStatus.UNCLAIMED,
        session: undefined
      });
    }
  };

  const handleMerge = () => {
    if (!task) return;
    
    if (confirm('Are you sure you want to merge this task? This will merge the changes to the main branch.')) {
      mergeTaskMutation.mutate();
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
              {(task.status === TaskStatus.UP_NEXT || task.status === TaskStatus.IN_PROGRESS) && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleReset}
                  className="h-8 w-8 text-yellow-500 hover:text-yellow-600"
                  disabled={updateTaskMutation.isPending}
                  title="Reset task to unclaimed"
                >
                  <RotateCcw className="w-4 h-4" />
                </Button>
              )}
              {task.status === TaskStatus.COMPLETED && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleMerge}
                  className="h-8 w-8 text-green-500 hover:text-green-600"
                  disabled={mergeTaskMutation.isPending}
                  title="Merge task to main branch"
                >
                  <GitMerge className="w-4 h-4" />
                </Button>
              )}
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
            <Label htmlFor="task-prompt">Agent Prompt (Full Prompt Sent to Claude)</Label>
            {isEditing ? (
              <div className="space-y-2">
                <Textarea
                  id="task-prompt"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="min-h-[200px] bg-deep-indigo/50 border-electric-cyan/20 font-mono text-sm"
                  placeholder="Edit the full prompt that will be sent to Claude..."
                  autoComplete="off"
                />
                <div className="text-xs text-muted-foreground">
                  💡 This is the complete prompt that will be sent to Claude. You can edit it directly or it will use the default structure.
                </div>
              </div>
            ) : (
              <div className="bg-dark-bg/50 border border-electric-cyan/20 rounded-md p-4">
                <pre className="text-sm text-muted-foreground whitespace-pre-wrap font-mono">
                  {generateFullPrompt(task, task.prompt)}
                </pre>
                <div className="mt-2 text-xs text-muted-foreground">
                  {task.prompt ? '✨ Using custom prompt' : '🔧 Using default prompt structure'}
                </div>
              </div>
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
                  <SelectItem value={TaskStatus.UP_NEXT}>Up Next</SelectItem>
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
            <Label>Task ID</Label>
            <p className="text-sm font-mono">{task.task_id || 'Not assigned'}</p>
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="task-branch">Branch</Label>
            {isEditing ? (
              <div className="space-y-1">
                <Input
                  id="task-branch"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  className="bg-deep-indigo/50 border-electric-cyan/20 font-mono"
                  placeholder="Git branch name"
                  autoComplete="off"
                />
                <p className="text-xs text-muted-foreground">
                  ⚠️ Avoid special characters like / & \ in branch names
                </p>
              </div>
            ) : (
              <p className="text-sm font-mono">{task.branch}</p>
            )}
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