import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Project } from '@/types';
import { api } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ProjectSetupWizard } from '@/components/ProjectSetupWizard';
import { 
  FolderOpen, 
  Trash2, 
  Edit2, 
  RotateCcw, 
  Calendar,
  GitBranch,
  Users,
  AlertTriangle,
  RefreshCw,
  Plus
} from 'lucide-react';

interface ProjectManagerProps {
  onSelectProject?: (projectId: string) => void;
}

export function ProjectManager({ onSelectProject }: ProjectManagerProps) {
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [deletingProject, setDeletingProject] = useState<Project | null>(null);
  const [resetingProject, setResetingProject] = useState<Project | null>(null);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [editForm, setEditForm] = useState({ name: '', description: '' });
  const [deleteWithCleanup, setDeleteWithCleanup] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  
  const queryClient = useQueryClient();

  // Fetch all projects
  const { data: projects = [], isLoading, refetch } = useQuery({
    queryKey: ['projects'],
    queryFn: api.getProjects,
  });

  // Update project mutation
  const updateMutation = useMutation({
    mutationFn: async ({ projectId, updates }: { projectId: string; updates: any }) => {
      const response = await fetch(`/api/projects/${projectId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      if (!response.ok) throw new Error('Failed to update project');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setEditingProject(null);
    },
  });

  // Delete project mutation
  const deleteMutation = useMutation({
    mutationFn: async ({ projectId, cleanup }: { projectId: string; cleanup: boolean }) => {
      const params = new URLSearchParams();
      if (cleanup) params.append('cleanup_files', 'true');
      
      const response = await fetch(`/api/projects/${projectId}?${params}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete project');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setDeletingProject(null);
      setDeleteWithCleanup(false);
      setDeleteConfirmText('');
    },
  });

  // Reset project mutation
  const resetMutation = useMutation({
    mutationFn: async (projectId: string) => {
      const response = await fetch(`/api/projects/${projectId}/reset`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to reset project');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setResetingProject(null);
    },
  });

  const handleEdit = (project: Project) => {
    setEditingProject(project);
    setEditForm({
      name: project.name,
      description: project.description || '',
    });
  };

  const handleSaveEdit = () => {
    if (!editingProject) return;
    updateMutation.mutate({
      projectId: editingProject.id,
      updates: editForm,
    });
  };

  const handleDelete = (project: Project) => {
    setDeletingProject(project);
  };

  const confirmDelete = () => {
    if (!deletingProject || deleteConfirmText !== deletingProject.name) return;
    deleteMutation.mutate({
      projectId: deletingProject.id,
      cleanup: deleteWithCleanup,
    });
  };

  const isDeleteConfirmValid = deleteConfirmText === deletingProject?.name;

  const handleReset = (project: Project) => {
    setResetingProject(project);
  };

  const confirmReset = () => {
    if (!resetingProject) return;
    resetMutation.mutate(resetingProject.id);
  };


  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-electric-cyan mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Project Manager</h1>
          <p className="text-muted-foreground mt-1">
            Manage all your SplitMind projects in one place
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            onClick={() => setShowCreateProject(true)}
            className="bg-electric-cyan hover:bg-electric-cyan/90 text-dark-bg font-medium"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create New Project
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Projects Grid */}
      {projects.length === 0 ? (
        <Card className="border-dashed border-2 border-electric-cyan/20">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FolderOpen className="w-12 h-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Projects Yet</h3>
            <p className="text-muted-foreground text-center mb-6">
              Create your first project to get started with SplitMind's AI-powered development workflow
            </p>
            <Button
              onClick={() => setShowCreateProject(true)}
              className="bg-electric-cyan hover:bg-electric-cyan/90 text-dark-bg font-medium"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Project
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="border-electric-cyan/20 bg-card/50 hover:bg-card/70 transition-colors">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg flex items-center gap-2">
                        <FolderOpen className="w-5 h-5 text-electric-cyan" />
                        {project.name}
                      </CardTitle>
                      {project.description && (
                        <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                          {project.description}
                        </p>
                      )}
                    </div>
                    <Badge variant={project.active ? "default" : "secondary"}>
                      {project.active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  {/* Project Details */}
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center text-muted-foreground">
                      <Calendar className="w-4 h-4 mr-2" />
                      Created {formatDate(project.created_at)}
                    </div>
                    
                    {project.is_git_repo && (
                      <div className="flex items-center text-green-400">
                        <GitBranch className="w-4 h-4 mr-2" />
                        Git Repository
                      </div>
                    )}
                    
                    <div className="flex items-center text-muted-foreground">
                      <Users className="w-4 h-4 mr-2" />
                      Max {project.max_agents} agents
                    </div>
                  </div>

                  {/* Project Path */}
                  <div className="bg-dark-bg/30 rounded p-2">
                    <code className="text-xs text-muted-foreground break-all">
                      {project.path}
                    </code>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center justify-between pt-2">
                    <div className="flex items-center space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(project)}
                        title="Edit Project"
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleReset(project)}
                        title="Reset Project"
                        className="text-yellow-400 hover:text-yellow-300"
                      >
                        <RotateCcw className="w-4 h-4" />
                      </Button>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(project)}
                        title="Delete Project"
                        className="text-red-400 hover:text-red-300"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    {onSelectProject && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onSelectProject(project.id)}
                      >
                        Open Project
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Edit Project Dialog */}
      <Dialog open={!!editingProject} onOpenChange={(open) => !open && setEditingProject(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Project</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Project Name</Label>
              <Input
                id="name"
                value={editForm.name}
                onChange={(e) => setEditForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter project name"
              />
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={editForm.description}
                onChange={(e) => setEditForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Enter project description"
                rows={3}
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingProject(null)}>
              Cancel
            </Button>
            <Button 
              onClick={handleSaveEdit}
              disabled={updateMutation.isPending}
            >
              {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog 
        open={!!deletingProject} 
        onOpenChange={(open) => {
          if (!open) {
            setDeletingProject(null);
            setDeleteConfirmText('');
            setDeleteWithCleanup(false);
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              Delete Project
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <Alert className="border-red-500/20 bg-red-500/5">
              <AlertTriangle className="h-4 w-4 text-red-500" />
              <AlertDescription>
                <strong>This action cannot be undone!</strong>
                <br />
                This will permanently delete the project "{deletingProject?.name}" from SplitMind.
                {deleteWithCleanup ? (
                  <span className="block mt-2 text-red-600 font-medium">
                    ⚠️ Complete cleanup will remove: tasks, worktrees, git branches, tmux sessions, and .splitmind directory
                  </span>
                ) : (
                  <span className="block mt-1 text-gray-600">
                    Project files on disk will remain untouched.
                  </span>
                )}
              </AlertDescription>
            </Alert>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="cleanup-files"
                  checked={deleteWithCleanup}
                  onCheckedChange={setDeleteWithCleanup}
                />
                <Label htmlFor="cleanup-files" className="text-sm">
                  <strong>Complete cleanup</strong> - Remove all SplitMind files, tasks, branches, and sessions
                </Label>
              </div>

              <div className="space-y-2">
                <Label htmlFor="delete-confirm" className="text-sm font-medium">
                  To confirm deletion, type the project name: <span className="text-red-400 font-mono">{deletingProject?.name}</span>
                </Label>
                <Input
                  id="delete-confirm"
                  value={deleteConfirmText}
                  onChange={(e) => setDeleteConfirmText(e.target.value)}
                  placeholder="Type project name to confirm"
                  className={`${
                    deleteConfirmText && !isDeleteConfirmValid 
                      ? 'border-red-500 focus:border-red-500' 
                      : isDeleteConfirmValid 
                      ? 'border-green-500 focus:border-green-500' 
                      : ''
                  }`}
                />
                {deleteConfirmText && !isDeleteConfirmValid && (
                  <p className="text-xs text-red-400">Project name doesn't match</p>
                )}
                {isDeleteConfirmValid && (
                  <p className="text-xs text-green-400">✓ Project name confirmed</p>
                )}
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeletingProject(null)}>
              Cancel
            </Button>
            <Button 
              variant="destructive"
              onClick={confirmDelete}
              disabled={deleteMutation.isPending || !isDeleteConfirmValid}
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete Project'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reset Confirmation Dialog */}
      <Dialog open={!!resetingProject} onOpenChange={(open) => !open && setResetingProject(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <RotateCcw className="w-5 h-5 text-yellow-500" />
              Reset Project
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <Alert className="border-yellow-500/20 bg-yellow-500/5">
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
              <AlertDescription>
                <strong>This will clean up all project work!</strong>
                <br />
                This will remove all tasks, kill tmux sessions, remove worktrees, 
                and clean up git branches for "{resetingProject?.name}". 
                The main project files will remain untouched.
              </AlertDescription>
            </Alert>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setResetingProject(null)}>
              Cancel
            </Button>
            <Button 
              variant="outline"
              onClick={confirmReset}
              disabled={resetMutation.isPending}
              className="text-yellow-400 border-yellow-400/20 hover:bg-yellow-400/10"
            >
              {resetMutation.isPending ? 'Resetting...' : 'Reset Project'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Project Wizard */}
      <ProjectSetupWizard
        open={showCreateProject}
        onOpenChange={setShowCreateProject}
      />
    </div>
  );
}