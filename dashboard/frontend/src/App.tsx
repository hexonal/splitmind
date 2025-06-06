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
import { OnboardingModal } from '@/components/OnboardingModal';
import { HelpCenter } from '@/components/HelpCenter';
import { Button } from '@/components/ui/button';
import { HelpCircle } from 'lucide-react';

function App() {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showHelpCenter, setShowHelpCenter] = useState(false);

  // Fetch projects
  const { data: projects = [], refetch: refetchProjects, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: api.getProjects,
    staleTime: 5000, // Consider data fresh for 5 seconds
    gcTime: 10 * 60 * 1000, // Keep in cache for 10 minutes (v5 uses gcTime instead of cacheTime)
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

  // Show loading state only on initial load
  const showLoading = isLoading && projects.length === 0;
  
  const selectedProject = projects.find(p => p.id === selectedProjectId);

  // Check if onboarding should be shown on first visit
  useEffect(() => {
    const hasSeenOnboarding = localStorage.getItem('has_seen_onboarding');
    if (!hasSeenOnboarding && !showLoading) {
      setShowOnboarding(true);
      localStorage.setItem('has_seen_onboarding', 'true');
    }
  }, [showLoading]);

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
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowHelpCenter(true)}
              className="text-muted-foreground hover:text-white hover:bg-electric-cyan/10"
              title="Help Center"
            >
              <HelpCircle className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10">
        {showLoading ? (
          <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-electric-cyan mx-auto mb-4"></div>
              <p className="text-muted-foreground">Loading projects...</p>
            </div>
          </div>
        ) : selectedProject ? (
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

      {/* Onboarding Modal */}
      <OnboardingModal 
        isOpen={showOnboarding} 
        onClose={() => setShowOnboarding(false)} 
      />

      {/* Help Center Modal */}
      <HelpCenter 
        isOpen={showHelpCenter} 
        onClose={() => setShowHelpCenter(false)} 
      />
    </div>
  );
}

export default App;