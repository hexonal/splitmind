import { useState } from 'react';
import { Project } from '@/types';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { OrchestratorControl } from '@/components/OrchestratorControl';
import { TaskBoard } from '@/components/TaskBoard';
import { AgentMonitor } from '@/components/AgentMonitor';
import { ProjectStats } from '@/components/ProjectStats';
import { ProjectSettings } from '@/components/ProjectSettings';
import { AgentCoordination } from '@/components/AgentCoordination';
import AgentCoordinationCenter from '@/components/AgentCoordinationCenter';
import { motion } from 'framer-motion';
import { LayoutGrid, Cpu, BarChart3, Settings, Network } from 'lucide-react';

interface CommandCenterProps {
  project: Project;
}

export function CommandCenter({ project }: CommandCenterProps) {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="grid grid-cols-12 gap-6">
        {/* Left Column - Orchestrator Control & Coordination */}
        <div className="col-span-3 space-y-6">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <OrchestratorControl projectId={project.id} />
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <AgentCoordination projectId={project.id} />
          </motion.div>
        </div>

        {/* Main Content Area */}
        <motion.div 
          className="col-span-9"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className="bg-deep-indigo/50 border border-electric-cyan/20">
              <TabsTrigger value="dashboard" className="data-[state=active]:bg-electric-cyan/20">
                <LayoutGrid className="w-4 h-4 mr-2" />
                Dashboard
              </TabsTrigger>
              <TabsTrigger value="agents" className="data-[state=active]:bg-electric-cyan/20">
                <Cpu className="w-4 h-4 mr-2" />
                Agents
              </TabsTrigger>
              <TabsTrigger value="coordination" className="data-[state=active]:bg-electric-cyan/20">
                <Network className="w-4 h-4 mr-2" />
                Coordination
              </TabsTrigger>
              <TabsTrigger value="stats" className="data-[state=active]:bg-electric-cyan/20">
                <BarChart3 className="w-4 h-4 mr-2" />
                Statistics
              </TabsTrigger>
              <TabsTrigger value="settings" className="data-[state=active]:bg-electric-cyan/20">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </TabsTrigger>
            </TabsList>

            <TabsContent value="dashboard" className="space-y-6">
              <TaskBoard projectId={project.id} />
            </TabsContent>

            <TabsContent value="agents" className="space-y-6">
              <AgentMonitor projectId={project.id} />
            </TabsContent>

            <TabsContent value="coordination" className="space-y-6">
              <AgentCoordinationCenter projectId={project.id} />
            </TabsContent>

            <TabsContent value="stats" className="space-y-6">
              <ProjectStats projectId={project.id} />
            </TabsContent>

            <TabsContent value="settings" className="space-y-6">
              <ProjectSettings project={project} />
            </TabsContent>
          </Tabs>
        </motion.div>
      </div>
    </div>
  );
}