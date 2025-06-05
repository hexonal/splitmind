import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Rocket, Code2, GitBranch, Cpu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { CreateProjectDialog } from '@/components/CreateProjectDialog';

export function WelcomeScreen() {
  const [dialogOpen, setDialogOpen] = useState(false);

  const features = [
    { icon: <Code2 className="w-8 h-8" />, title: 'AI-Powered Development', desc: 'Spawn multiple AI agents to work on tasks' },
    { icon: <GitBranch className="w-8 h-8" />, title: 'Git Worktree Isolation', desc: 'Each agent works in its own branch' },
    { icon: <Cpu className="w-8 h-8" />, title: 'Parallel Execution', desc: 'Run multiple agents simultaneously' },
  ];

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
      <motion.div 
        className="text-center max-w-2xl mx-auto p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, type: "spring" }}
          className="mb-8"
        >
          <div className="relative inline-block">
            <div className="absolute inset-0 bg-electric-cyan/20 blur-3xl animate-pulse" />
            <Sparkles className="w-24 h-24 text-electric-cyan relative" />
          </div>
        </motion.div>

        <motion.h1 
          className="text-4xl font-bold mb-4 bg-gradient-to-r from-electric-cyan to-accent bg-clip-text text-transparent"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Hey! Looks Like You're Just Getting Started!
        </motion.h1>
        
        <motion.p 
          className="text-xl text-muted-foreground mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          Welcome to SplitMind Command Center
        </motion.p>

        <motion.div 
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="p-4 rounded-lg bg-deep-indigo/30 border border-electric-cyan/20"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              whileHover={{ scale: 1.05, borderColor: 'rgba(0, 255, 255, 0.5)' }}
            >
              <div className="text-electric-cyan mb-2">{feature.icon}</div>
              <h3 className="font-semibold mb-1">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">{feature.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <CreateProjectDialog 
            open={dialogOpen} 
            onOpenChange={setDialogOpen}
            trigger={
              <Button 
                variant="glow" 
                size="lg"
                className="group"
              >
                <Rocket className="w-5 h-5 mr-2 group-hover:animate-bounce" />
                Start Your First Project
              </Button>
            }
          />
        </motion.div>
      </motion.div>
    </div>
  );
}