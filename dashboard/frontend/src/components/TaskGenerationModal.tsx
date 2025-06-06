import { useEffect, useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Loader2, Zap, CheckCircle, Sparkles, Code, Cpu, BrainCircuit } from 'lucide-react';

interface TaskGenerationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const loadingMessages = [
  { icon: BrainCircuit, text: "🧠 Task Master AI is analyzing your project..." },
  { icon: Zap, text: "⚡ Breaking down requirements into executable tasks..." },
  { icon: Code, text: "💻 Structuring wave-based development phases..." },
  { icon: Cpu, text: "🤖 Assigning AI agents to parallel workflows..." },
  { icon: Sparkles, text: "✨ Crafting custom prompts for each task..." },
  { icon: CheckCircle, text: "📋 Finalizing your task breakdown..." }
];

export function TaskGenerationModal({ open, onOpenChange }: TaskGenerationModalProps) {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!open) {
      setCurrentMessageIndex(0);
      setProgress(0);
      return;
    }

    // Progress animation
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) return 95; // Don't complete until actually done
        return prev + Math.random() * 3;
      });
    }, 500);

    // Message rotation
    const messageInterval = setInterval(() => {
      setCurrentMessageIndex(prev => (prev + 1) % loadingMessages.length);
    }, 3000);

    return () => {
      clearInterval(progressInterval);
      clearInterval(messageInterval);
    };
  }, [open]);

  const currentMessage = loadingMessages[currentMessageIndex];
  const Icon = currentMessage.icon;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] bg-dark-bg/95 border-electric-cyan/20">
        <DialogHeader>
          <DialogTitle className="text-electric-cyan flex items-center space-x-2">
            <Zap className="w-5 h-5 animate-pulse" />
            <span>Task Master AI at Work</span>
          </DialogTitle>
          <DialogDescription>
            Creating your perfect development roadmap...
          </DialogDescription>
        </DialogHeader>
        
        <div className="py-8 space-y-6">
          {/* Animated Icon */}
          <div className="flex justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-electric-cyan/20 rounded-full blur-xl animate-pulse" />
              <div className="relative bg-deep-indigo/50 p-6 rounded-full border-2 border-electric-cyan/40">
                <Icon className="w-16 h-16 text-electric-cyan animate-pulse" />
              </div>
            </div>
          </div>

          {/* Loading Message */}
          <div className="text-center space-y-2">
            <p className="text-lg font-medium text-electric-cyan">
              {currentMessage.text}
            </p>
            <p className="text-sm text-muted-foreground">
              This may take up to 60 seconds for complex projects
            </p>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <Progress value={progress} className="h-2" />
            <p className="text-xs text-center text-muted-foreground">
              {Math.round(progress)}% Complete
            </p>
          </div>

          {/* Loading Spinner */}
          <div className="flex justify-center">
            <Loader2 className="w-8 h-8 text-electric-cyan animate-spin" />
          </div>

          {/* Fun Facts */}
          <div className="bg-electric-cyan/5 border border-electric-cyan/20 rounded-lg p-4">
            <p className="text-xs text-center text-muted-foreground">
              <span className="font-semibold">Did you know?</span> Task Master AI can generate
              up to 20 parallel tasks organized into development waves, each with custom prompts
              tailored for AI agents.
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}