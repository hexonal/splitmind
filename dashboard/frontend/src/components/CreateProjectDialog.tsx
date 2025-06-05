import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/services/api';
import { Plus, Sparkles, Folder } from 'lucide-react';
import { FolderPicker } from '@/components/FolderPicker';

interface CreateProjectDialogProps {
  trigger?: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function CreateProjectDialog({ trigger, open, onOpenChange }: CreateProjectDialogProps) {
  const [name, setName] = useState('');
  const [path, setPath] = useState('');
  const [description, setDescription] = useState('');
  const [maxAgents, setMaxAgents] = useState(5);
  const [folderPickerOpen, setFolderPickerOpen] = useState(false);
  const queryClient = useQueryClient();

  const createProjectMutation = useMutation({
    mutationFn: () => {
      // Extract folder name from path for ID
      const folderName = path.split('/').pop() || name;
      const projectId = folderName.toLowerCase().replace(/[^a-z0-9-]/g, '-');
      
      return api.createProject({
        id: projectId,
        name,
        path,
        description: description || undefined,
        max_agents: maxAgents,
        active: true,
      });
    },
    onSuccess: () => {
      // Force immediate refetch of projects
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.refetchQueries({ queryKey: ['projects'] });
      
      // Reset form
      setName('');
      setPath('');
      setDescription('');
      setMaxAgents(5);
      
      // Close dialog
      if (onOpenChange) onOpenChange(false);
    },
    onError: (error: any) => {
      console.error('Failed to create project:', error);
      alert(`Failed to create project: ${error.message}`);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name && path) {
      createProjectMutation.mutate();
    }
  };

  const defaultTrigger = (
    <Button variant="glow" size="icon">
      <Plus className="w-4 h-4" />
    </Button>
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        {trigger || defaultTrigger}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[525px] bg-dark-bg/95 border-electric-cyan/20">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle className="text-electric-cyan flex items-center space-x-2">
              <Sparkles className="w-5 h-5" />
              <span>Create New Project</span>
            </DialogTitle>
            <DialogDescription>
              Add a project to manage with SplitMind. The project should be a Git repository.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Name
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="col-span-3 bg-deep-indigo/50 border-electric-cyan/20"
                placeholder="My Awesome Project"
                autoComplete="off"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="path" className="text-right">
                Path
              </Label>
              <div className="col-span-3">
                <div className="flex space-x-2">
                  <Input
                    id="path"
                    value={path}
                    onChange={(e) => setPath(e.target.value)}
                    className="flex-1 bg-deep-indigo/50 border-electric-cyan/20"
                    placeholder="/Users/you/code/my-project"
                    autoComplete="off"
                    required
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={() => setFolderPickerOpen(true)}
                    className="border-electric-cyan/20 hover:border-electric-cyan/50"
                  >
                    <Folder className="w-4 h-4" />
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Select or enter the path to your Git repository
                </p>
              </div>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">
                Description
              </Label>
              <Input
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="col-span-3 bg-deep-indigo/50 border-electric-cyan/20"
                placeholder="Optional project description"
                autoComplete="off"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="maxAgents" className="text-right">
                Max Agents
              </Label>
              <Input
                id="maxAgents"
                type="number"
                value={maxAgents}
                onChange={(e) => setMaxAgents(parseInt(e.target.value) || 5)}
                className="col-span-3 bg-deep-indigo/50 border-electric-cyan/20"
                min="1"
                max="20"
                autoComplete="off"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="submit"
              variant="glow"
              disabled={createProjectMutation.isPending || !name || !path}
            >
              {createProjectMutation.isPending ? 'Creating...' : 'Create Project'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
      
      <FolderPicker
        open={folderPickerOpen}
        onOpenChange={setFolderPickerOpen}
        onSelect={(selectedPath) => {
          setPath(selectedPath);
          // Auto-generate project name from folder name if empty
          if (!name && selectedPath) {
            const folderName = selectedPath.split('/').pop() || '';
            setName(folderName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));
          }
        }}
        currentPath={path}
      />
    </Dialog>
  );
}