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
import { api } from '@/services/api';
import { Plus } from 'lucide-react';

interface AddTaskDialogProps {
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AddTaskDialog({ projectId, open, onOpenChange }: AddTaskDialogProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const queryClient = useQueryClient();

  const createTaskMutation = useMutation({
    mutationFn: () => api.createTask(projectId, title, description || undefined),
    onSuccess: () => {
      // Invalidate and refetch tasks
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
      
      // Reset form
      setTitle('');
      setDescription('');
      
      // Close dialog
      onOpenChange(false);
    },
    onError: (error: any) => {
      console.error('Failed to create task:', error);
      alert(`Failed to create task: ${error.message}`);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      createTaskMutation.mutate();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[525px] bg-dark-bg/95 border-electric-cyan/20">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle className="text-electric-cyan flex items-center space-x-2">
              <Plus className="w-5 h-5" />
              <span>Add New Task</span>
            </DialogTitle>
            <DialogDescription>
              Create a new task for AI agents to work on. Be specific and include acceptance criteria.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="title">Task Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Implement user authentication"
                className="bg-deep-indigo/50 border-electric-cyan/20"
                autoComplete="off"
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Detailed description, acceptance criteria, technical requirements..."
                className="min-h-[100px] bg-deep-indigo/50 border-electric-cyan/20"
                autoComplete="off"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="border-electric-cyan/20"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="glow"
              disabled={createTaskMutation.isPending || !title.trim()}
            >
              {createTaskMutation.isPending ? 'Creating...' : 'Create Task'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}