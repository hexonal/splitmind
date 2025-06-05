import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '@/services/api';
import { useWebSocket } from '@/hooks/useWebSocket';
import { WebSocketMessage } from '@/types';
import { CommandCenter } from '@/components/CommandCenter';
import { ProjectSelector } from '@/components/ProjectSelector';
import { Logo } from '@/components/Logo';
import { WelcomeScreen } from '@/components/WelcomeScreen';

function App() {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  // Fetch projects
  const { data: projects = [], refetch: refetchProjects, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: api.getProjects,
  });

  console.log('Query state:', { projects, isLoading, error });

  // Handle WebSocket messages
  useWebSocket((message: WebSocketMessage) => {
    console.log('WebSocket message:', message);
    
    // Refetch data based on message type
    if (message.type.includes('task') || message.type.includes('agent') || message.type.includes('project') || message.type === 'plan_generated') {
      refetchProjects();
    }
  });

  // Select first project by default
  useEffect(() => {
    if (projects.length > 0 && !selectedProjectId) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

  const selectedProject = projects.find(p => p.id === selectedProjectId);

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Background Grid Pattern */}
      <div className="fixed inset-0 bg-grid-pattern bg-[length:40px_40px] opacity-5" />
      
      {/* Header */}
      <header className="relative z-10 border-b border-electric-cyan/20 bg-dark-bg/80 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <Logo />
              {projects.length > 0 && (
                <ProjectSelector
                  projects={projects}
                  selectedProjectId={selectedProjectId}
                  onSelectProject={setSelectedProjectId}
                />
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10">
        {selectedProject ? (
          <motion.div
            key={selectedProject.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <CommandCenter project={selectedProject} />
          </motion.div>
        ) : (
          <WelcomeScreen />
        )}
      </main>
    </div>
  );
}

export default App;