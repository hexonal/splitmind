import { useState } from 'react';
import { Project } from '@/types';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { FolderOpen, Plus } from 'lucide-react';
import { ProjectSetupWizard } from '@/components/ProjectSetupWizard';

interface ProjectSelectorProps {
  projects: Project[];
  selectedProjectId: string | null;
  onSelectProject: (projectId: string) => void;
}

export function ProjectSelector({
  projects,
  selectedProjectId,
  onSelectProject,
}: ProjectSelectorProps) {
  const [wizardOpen, setWizardOpen] = useState(false);
  
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
      
      <Button 
        variant="glow" 
        size="icon"
        onClick={() => setWizardOpen(true)}
        title="Add New Project"
      >
        <Plus className="w-4 h-4" />
      </Button>
      
      <ProjectSetupWizard 
        open={wizardOpen} 
        onOpenChange={setWizardOpen}
      />
    </div>
  );
}