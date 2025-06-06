import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  HelpCircle, Rocket, GitBranch, Key, Bot, 
  AlertCircle, CheckCircle, Database,
  Zap, DollarSign, BookOpen
} from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

const Sparkles = Zap; // Using Zap as Sparkles

interface HelpTopic {
  id: string;
  title: string;
  icon: React.ReactNode;
  category: 'getting-started' | 'features' | 'troubleshooting' | 'advanced';
  content: React.ReactNode;
  keywords: string[];
}

const helpTopics: HelpTopic[] = [
  {
    id: 'getting-started',
    title: 'Getting Started with SplitMind',
    icon: <Rocket className="w-5 h-5" />,
    category: 'getting-started',
    keywords: ['start', 'begin', 'setup', 'first', 'new'],
    content: (
      <div className="space-y-4">
        <p>Welcome to SplitMind! Here's how to get started:</p>
        <ol className="list-decimal list-inside space-y-2">
          <li>Create your first project by clicking the "+" button</li>
          <li>Set up your Anthropic API key in Project Settings → API Settings</li>
          <li>Generate a plan using AI in Project Settings → Overview</li>
          <li>Launch the orchestrator to spawn AI agents for your tasks</li>
        </ol>
        <div className="bg-electric-cyan/10 p-4 rounded-lg">
          <p className="text-sm">💡 Tip: Make sure your project is a Git repository for agents to work properly!</p>
        </div>
      </div>
    )
  },
  {
    id: 'api-setup',
    title: 'Setting up Anthropic API',
    icon: <Key className="w-5 h-5" />,
    category: 'getting-started',
    keywords: ['api', 'key', 'anthropic', 'claude', 'token'],
    content: (
      <div className="space-y-4">
        <h4 className="font-semibold">How to get your Anthropic API key:</h4>
        <ol className="list-decimal list-inside space-y-2">
          <li>Visit <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer" className="text-electric-cyan hover:underline">console.anthropic.com</a></li>
          <li>Sign up or log in to your account</li>
          <li>Navigate to API Keys section</li>
          <li>Create a new API key</li>
          <li>Copy and paste it in Project Settings → API Settings</li>
        </ol>
        <div className="bg-deep-indigo/50 p-4 rounded-lg space-y-2">
          <h5 className="font-semibold flex items-center gap-2">
            <DollarSign className="w-4 h-4" /> Pricing
          </h5>
          <ul className="text-sm space-y-1">
            <li>• Claude Sonnet 4: $3/$15 per million tokens</li>
            <li>• Claude Opus 4: $15/$75 per million tokens</li>
            <li>• Average plan generation: ~$0.02-0.08</li>
          </ul>
        </div>
      </div>
    )
  },
  {
    id: 'git-setup',
    title: 'Git Repository Setup',
    icon: <GitBranch className="w-5 h-5" />,
    category: 'getting-started',
    keywords: ['git', 'github', 'repository', 'version', 'control'],
    content: (
      <div className="space-y-4">
        <h4 className="font-semibold">Setting up Git for your project:</h4>
        <div className="space-y-3">
          <div className="bg-dark-bg/50 p-3 rounded-lg">
            <p className="text-sm font-mono mb-2">Initialize Git repository:</p>
            <code className="text-electric-cyan">git init</code>
          </div>
          <div className="bg-dark-bg/50 p-3 rounded-lg">
            <p className="text-sm font-mono mb-2">Add remote GitHub repository:</p>
            <code className="text-electric-cyan">git remote add origin https://github.com/your-username/your-repo.git</code>
          </div>
          <div className="bg-dark-bg/50 p-3 rounded-lg">
            <p className="text-sm font-mono mb-2">First commit:</p>
            <code className="text-electric-cyan">git add . && git commit -m "Initial commit"</code>
          </div>
        </div>
        <Alert className="border-electric-cyan/20">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            SplitMind agents require Git to create branches for their work. You can initialize Git from the Project Settings → Git tab.
          </AlertDescription>
        </Alert>
      </div>
    )
  },
  {
    id: 'mcp-setup',
    title: 'Installing MCPs (Model Context Protocol)',
    icon: <Bot className="w-5 h-5" />,
    category: 'advanced',
    keywords: ['mcp', 'model', 'context', 'protocol', 'claude', 'tools'],
    content: (
      <div className="space-y-4">
        <p>MCPs extend Claude's capabilities. Here are essential MCPs for SplitMind:</p>
        <div className="space-y-3">
          <div className="bg-dark-bg/50 p-3 rounded-lg">
            <p className="text-sm font-semibold mb-1">Dart (Task Management)</p>
            <code className="text-xs text-electric-cyan break-all">
              {`claude mcp add-json dart '{"command":"npx","args":["-y","dart-mcp-server"],"env":{"DART_TOKEN":"your-token"}}'`}
            </code>
          </div>
          <div className="bg-dark-bg/50 p-3 rounded-lg">
            <p className="text-sm font-semibold mb-1">Playwright (Browser Automation)</p>
            <code className="text-xs text-electric-cyan">
              mcp add playwright --command "npx" --args "@playwright/mcp"
            </code>
          </div>
          <div className="bg-dark-bg/50 p-3 rounded-lg">
            <p className="text-sm font-semibold mb-1">BrowserMCP (Web Browsing)</p>
            <code className="text-xs text-electric-cyan">
              mcp add browsermcp --command "npx" --args "@browsermcp/mcp@latest"
            </code>
          </div>
          <div className="bg-dark-bg/50 p-3 rounded-lg">
            <p className="text-sm font-semibold mb-1">Copy from Claude Desktop</p>
            <code className="text-xs text-electric-cyan">
              claude mcp add-from-claude-desktop
            </code>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          Check MCP status in Project Settings → MCP Status
        </p>
      </div>
    )
  },
  {
    id: 'plan-generation',
    title: 'Generating Project Plans',
    icon: <Sparkles className="w-5 h-5" />,
    category: 'features',
    keywords: ['plan', 'generate', 'ai', 'tasks', 'overview'],
    content: (
      <div className="space-y-4">
        <h4 className="font-semibold">How to generate an AI project plan:</h4>
        <ol className="list-decimal list-inside space-y-2">
          <li>Go to Project Settings → Overview tab</li>
          <li>Fill in the Project Overview with details about your project</li>
          <li>Add an Initial Prompt describing what you want to build</li>
          <li>Click "Generate Plan & Tasks"</li>
          <li>AI will create a comprehensive plan and break it into tasks</li>
        </ol>
        <div className="bg-electric-cyan/10 p-4 rounded-lg">
          <p className="text-sm">💡 The more detailed your overview and prompt, the better the plan!</p>
        </div>
      </div>
    )
  },
  {
    id: 'orchestrator',
    title: 'Using the Orchestrator',
    icon: <Zap className="w-5 h-5" />,
    category: 'features',
    keywords: ['orchestrator', 'agents', 'spawn', 'launch', 'ai'],
    content: (
      <div className="space-y-4">
        <h4 className="font-semibold">The Orchestrator manages AI agents:</h4>
        <ul className="list-disc list-inside space-y-2">
          <li>Automatically spawns Claude agents for unclaimed tasks</li>
          <li>Manages concurrent agents based on your settings</li>
          <li>Creates separate Git branches for each agent</li>
          <li>Monitors agent progress in real-time</li>
        </ul>
        <div className="bg-deep-indigo/50 p-4 rounded-lg">
          <h5 className="font-semibold mb-2">To start orchestrating:</h5>
          <ol className="list-decimal list-inside space-y-1 text-sm">
            <li>Ensure you have tasks in your project</li>
            <li>Set max concurrent agents in settings</li>
            <li>Click "Launch Orchestrator"</li>
            <li>Watch agents work on your tasks!</li>
          </ol>
        </div>
      </div>
    )
  },
  {
    id: 'task-management',
    title: 'Managing Tasks',
    icon: <CheckCircle className="w-5 h-5" />,
    category: 'features',
    keywords: ['task', 'todo', 'manage', 'create', 'edit'],
    content: (
      <div className="space-y-4">
        <h4 className="font-semibold">Task Management in SplitMind:</h4>
        <ul className="list-disc list-inside space-y-2">
          <li><strong>Add Task:</strong> Click the "+" button in the Task Board</li>
          <li><strong>Edit Task:</strong> Click on any task to view/edit details</li>
          <li><strong>Task States:</strong> Unclaimed → In Progress → Completed</li>
          <li><strong>Delete Task:</strong> Open task details and click delete</li>
        </ul>
        <div className="bg-dark-bg/50 p-4 rounded-lg">
          <p className="text-sm mb-2">Tasks are automatically created when you generate a plan, but you can also add them manually.</p>
          <p className="text-sm text-muted-foreground">Each task gets its own Git branch when an agent claims it.</p>
        </div>
      </div>
    )
  },
  {
    id: 'troubleshooting-blank',
    title: 'Blank Screen Issues',
    icon: <AlertCircle className="w-5 h-5" />,
    category: 'troubleshooting',
    keywords: ['blank', 'screen', 'empty', 'not', 'loading', 'white'],
    content: (
      <div className="space-y-4">
        <h4 className="font-semibold">If you see a blank screen:</h4>
        <ol className="list-decimal list-inside space-y-2">
          <li>Refresh the page (Cmd/Ctrl + R)</li>
          <li>Check the browser console for errors (F12)</li>
          <li>Ensure the backend is running:
            <code className="block mt-1 text-sm bg-dark-bg/50 p-2 rounded">
              python launch-dashboard.py
            </code>
          </li>
          <li>Clear browser cache and cookies</li>
          <li>Try a different browser</li>
        </ol>
      </div>
    )
  },
  {
    id: 'troubleshooting-api',
    title: 'API Connection Issues',
    icon: <AlertCircle className="w-5 h-5" />,
    category: 'troubleshooting',
    keywords: ['api', 'error', 'connection', 'failed', '401', '403'],
    content: (
      <div className="space-y-4">
        <h4 className="font-semibold">Common API issues and solutions:</h4>
        <div className="space-y-3">
          <div className="bg-dark-bg/50 p-3 rounded-lg">
            <p className="font-semibold text-sm">401 Unauthorized</p>
            <p className="text-sm">Check your API key is correct and has not expired</p>
          </div>
          <div className="bg-dark-bg/50 p-3 rounded-lg">
            <p className="font-semibold text-sm">Rate Limit Exceeded</p>
            <p className="text-sm">Wait a few minutes or upgrade your Anthropic plan</p>
          </div>
          <div className="bg-dark-bg/50 p-3 rounded-lg">
            <p className="font-semibold text-sm">Network Error</p>
            <p className="text-sm">Check your internet connection and firewall settings</p>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 'dart-integration',
    title: 'Dart Task Management',
    icon: <Database className="w-5 h-5" />,
    category: 'advanced',
    keywords: ['dart', 'integration', 'workspace', 'dartboard', 'sync'],
    content: (
      <div className="space-y-4">
        <h4 className="font-semibold">Integrating with Dart:</h4>
        <ol className="list-decimal list-inside space-y-2">
          <li>Get your Dart API token from dart.dev</li>
          <li>Find your workspace ID (format: ws_123456)</li>
          <li>Find your dartboard ID (format: db_789012)</li>
          <li>Add these in Project Settings → Integrations</li>
          <li>Install Dart MCP for Claude integration</li>
        </ol>
        <div className="bg-electric-cyan/10 p-4 rounded-lg">
          <p className="text-sm">Dart syncs tasks between SplitMind and your team's workflow.</p>
        </div>
      </div>
    )
  }
];

const categoryLabels = {
  'getting-started': { label: 'Getting Started', color: 'text-green-400' },
  'features': { label: 'Features', color: 'text-blue-400' },
  'troubleshooting': { label: 'Troubleshooting', color: 'text-yellow-400' },
  'advanced': { label: 'Advanced', color: 'text-purple-400' }
};

interface HelpCenterProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HelpCenter({ isOpen, onClose }: HelpCenterProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTopic, setSelectedTopic] = useState<HelpTopic | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const filteredTopics = helpTopics.filter(topic => {
    const matchesSearch = searchQuery === '' || 
      topic.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      topic.keywords.some(keyword => keyword.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = !selectedCategory || topic.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });


  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl h-[80vh] bg-dark-bg border-electric-cyan/20">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <HelpCircle className="w-6 h-6 text-electric-cyan" />
              <span>Help Center</span>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="flex gap-4 h-full">
          {/* Sidebar */}
          <div className="w-80 border-r border-electric-cyan/20 pr-4">
            <div className="space-y-4">
              {/* Search */}
              <div className="relative">
                <Input
                  type="text"
                  placeholder="Search help topics..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-deep-indigo/30 border-electric-cyan/20"
                />
                <HelpCircle className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              </div>

              {/* Category Filter */}
              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  variant={selectedCategory === null ? "default" : "outline"}
                  onClick={() => setSelectedCategory(null)}
                  className="text-xs"
                >
                  All
                </Button>
                {Object.entries(categoryLabels).map(([key, { label }]) => (
                  <Button
                    key={key}
                    size="sm"
                    variant={selectedCategory === key ? "default" : "outline"}
                    onClick={() => setSelectedCategory(key)}
                    className="text-xs"
                  >
                    {label}
                  </Button>
                ))}
              </div>

              {/* Topics List */}
              <ScrollArea className="h-[calc(100vh-320px)]">
                <div className="space-y-2">
                  {filteredTopics.map((topic) => (
                    <motion.div
                      key={topic.id}
                      whileHover={{ x: 4 }}
                      onClick={() => setSelectedTopic(topic)}
                      className={`
                        p-3 rounded-lg cursor-pointer transition-all
                        ${selectedTopic?.id === topic.id 
                          ? 'bg-electric-cyan/20 border border-electric-cyan/40' 
                          : 'bg-deep-indigo/30 hover:bg-deep-indigo/50 border border-transparent'
                        }
                      `}
                    >
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5">{topic.icon}</div>
                        <div className="flex-1">
                          <h4 className="font-medium text-sm">{topic.title}</h4>
                          <Badge 
                            variant="outline" 
                            className={`mt-1 text-xs ${categoryLabels[topic.category].color}`}
                          >
                            {categoryLabels[topic.category].label}
                          </Badge>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          </div>

          {/* Content Area */}
          <div className="flex-1 pl-4">
            <ScrollArea className="h-[calc(100vh-240px)]">
              {selectedTopic ? (
                <AnimatePresence mode="wait">
                  <motion.div
                    key={selectedTopic.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="space-y-4"
                  >
                    <div className="flex items-center gap-3 mb-6">
                      {selectedTopic.icon}
                      <h2 className="text-2xl font-semibold">{selectedTopic.title}</h2>
                    </div>
                    <div className="prose prose-invert max-w-none">
                      {selectedTopic.content}
                    </div>
                  </motion.div>
                </AnimatePresence>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <BookOpen className="w-12 h-12 text-electric-cyan/30 mb-4" />
                  <p className="text-lg text-muted-foreground">
                    Select a topic from the left to view help content
                  </p>
                </div>
              )}
            </ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}