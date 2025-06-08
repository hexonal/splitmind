import { Project } from '@/types';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { FolderOpen, Settings } from 'lucide-react';

interface ProjectSelectorProps {
  projects: Project[];
  selectedProjectId: string | null;
  onSelectProject: (projectId: string) => void;
  onOpenProjectManager?: () => void;
}

export function ProjectSelector({
  projects,
  selectedProjectId,
  onSelectProject,
  onOpenProjectManager,
}: ProjectSelectorProps) {
  
  return (
    <div className="flex items-center space-x-2">
      <Select value={selectedProjectId || ''} onValueChange={onSelectProject}>
        <SelectTrigger className="w-[200px] bg-deep-indigo/50 border-electric-cyan/20">
          <SelectValue placeholder="Select a project">
            {selectedProjectId && (
              <div className="flex items-center space-x-2">
                <FolderOpen className="w-4 h-4 text-electric-cyan" />
                <span>
                  {projects.find(p => p.id === selectedProjectId)?.name}
                </span>
              </div>
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {projects.map(project => (
            <SelectItem key={project.id} value={project.id}>
              <div className="flex items-center space-x-2">
                <FolderOpen className="w-4 h-4" />
                <span>{project.name}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      {onOpenProjectManager && (
        <Button 
          variant="outline" 
          size="sm"
          onClick={onOpenProjectManager}
          className="text-muted-foreground hover:text-white hover:bg-electric-cyan/10"
          title="Project Manager"
        >
          <Settings className="w-4 h-4 mr-2" />
          Projects
        </Button>
      )}
    </div>
  );
}