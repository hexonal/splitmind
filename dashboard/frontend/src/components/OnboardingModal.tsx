import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Copy, 
  CheckCircle2, 
  Key, 
  GitBranch, 
  Terminal, 
  Cpu,
  ExternalLink,
  Info,
  AlertCircle,
  ChevronRight,
  Rocket
} from 'lucide-react';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function OnboardingModal({ isOpen, onClose }: OnboardingModalProps) {
  const [activeTab, setActiveTab] = useState('anthropic');
  const [copiedItems, setCopiedItems] = useState<Set<string>>(new Set());
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());

  // Load completed steps from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('onboarding_completed_steps');
    if (saved) {
      setCompletedSteps(new Set(JSON.parse(saved)));
    }
  }, []);

  const copyToClipboard = async (text: string, itemId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedItems(prev => new Set(prev).add(itemId));
      setTimeout(() => {
        setCopiedItems(prev => {
          const next = new Set(prev);
          next.delete(itemId);
          return next;
        });
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const markStepComplete = (step: string) => {
    const newCompleted = new Set(completedSteps).add(step);
    setCompletedSteps(newCompleted);
    localStorage.setItem('onboarding_completed_steps', JSON.stringify(Array.from(newCompleted)));
  };

  const CodeBlock = ({ children, itemId }: { children: string; itemId: string }) => (
    <div className="relative group">
      <pre className="bg-muted/50 border border-border rounded-lg p-4 pr-12 overflow-x-auto">
        <code className="text-sm font-mono text-electric-cyan">{children}</code>
      </pre>
      <Button
        size="sm"
        variant="ghost"
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={() => copyToClipboard(children, itemId)}
      >
        {copiedItems.has(itemId) ? (
          <CheckCircle2 className="h-4 w-4 text-green-500" />
        ) : (
          <Copy className="h-4 w-4" />
        )}
      </Button>
    </div>
  );

  const StepCard = ({ 
    title, 
    description, 
    icon: Icon, 
    children,
    stepId 
  }: { 
    title: string; 
    description: string; 
    icon: any; 
    children: React.ReactNode;
    stepId: string;
  }) => (
    <Card className="border-electric-cyan/20 bg-card/50 backdrop-blur-sm">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-electric-cyan/10 text-electric-cyan">
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-lg">{title}</CardTitle>
              <CardDescription>{description}</CardDescription>
            </div>
          </div>
          {completedSteps.has(stepId) && (
            <Badge variant="secondary" className="bg-green-500/10 text-green-500 border-green-500/20">
              <CheckCircle2 className="h-3 w-3 mr-1" />
              Complete
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {children}
        {!completedSteps.has(stepId) && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => markStepComplete(stepId)}
            className="w-full border-electric-cyan/20 hover:bg-electric-cyan/10"
          >
            Mark as Complete
          </Button>
        )}
      </CardContent>
    </Card>
  );

  const tabs = [
    { id: 'anthropic', label: 'Anthropic API', icon: Key },
    { id: 'git', label: 'Git Setup', icon: GitBranch },
    { id: 'dart', label: 'Dart Integration', icon: Rocket },
    { id: 'mcp', label: 'MCP Tools', icon: Cpu },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] p-0 bg-background border-electric-cyan/20">
        <DialogHeader className="px-6 pt-6 pb-0">
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Terminal className="h-6 w-6 text-electric-cyan" />
            SplitMind Setup Guide
          </DialogTitle>
        </DialogHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1">
          <div className="px-6 pb-4">
            <TabsList className="grid w-full grid-cols-4 bg-muted/50">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isComplete = completedSteps.has(tab.id);
                return (
                  <TabsTrigger 
                    key={tab.id} 
                    value={tab.id}
                    className="data-[state=active]:bg-electric-cyan/20 data-[state=active]:text-electric-cyan"
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {tab.label}
                    {isComplete && (
                      <CheckCircle2 className="h-3 w-3 ml-2 text-green-500" />
                    )}
                  </TabsTrigger>
                );
              })}
            </TabsList>
          </div>

          <ScrollArea className="flex-1 px-6 pb-6" style={{ height: 'calc(90vh - 180px)' }}>
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
              >
                <TabsContent value="anthropic" className="space-y-6 mt-0">
                  <StepCard
                    title="Get Your API Key"
                    description="Create an Anthropic account and generate an API key"
                    icon={Key}
                    stepId="anthropic"
                  >
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          1. Visit the Anthropic Console to create your account:
                        </p>
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full justify-between"
                          onClick={() => window.open('https://console.anthropic.com', '_blank')}
                        >
                          Open Anthropic Console
                          <ExternalLink className="h-4 w-4 ml-2" />
                        </Button>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          2. Navigate to API Keys and create a new key
                        </p>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          3. Set your API key in the Claude CLI:
                        </p>
                        <CodeBlock itemId="claude-api-key">
claude set api-key sk-ant-api03-xxxxx</CodeBlock>
                      </div>

                      <Alert className="border-electric-cyan/20 bg-electric-cyan/5">
                        <Info className="h-4 w-4 text-electric-cyan" />
                        <AlertDescription>
                          <strong>Pricing:</strong> Claude uses a pay-per-token model. Claude 3.5 Sonnet costs $3 per million input tokens and $15 per million output tokens.
                        </AlertDescription>
                      </Alert>
                    </div>
                  </StepCard>
                </TabsContent>

                <TabsContent value="git" className="space-y-6 mt-0">
                  <StepCard
                    title="Initialize Git Repository"
                    description="Set up version control for your project"
                    icon={GitBranch}
                    stepId="git"
                  >
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          1. Initialize a new Git repository:
                        </p>
                        <CodeBlock itemId="git-init">git init</CodeBlock>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          2. Create a GitHub repository:
                        </p>
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full justify-between"
                          onClick={() => window.open('https://github.com/new', '_blank')}
                        >
                          Create New Repository
                          <ExternalLink className="h-4 w-4 ml-2" />
                        </Button>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          3. Connect your local repo to GitHub:
                        </p>
                        <CodeBlock itemId="git-remote">git remote add origin https://github.com/yourusername/your-repo.git
git branch -M main
git push -u origin main</CodeBlock>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          4. Create the worktrees directory for SplitMind:
                        </p>
                        <CodeBlock itemId="worktrees">mkdir worktrees</CodeBlock>
                      </div>

                      <Alert className="border-yellow-500/20 bg-yellow-500/5">
                        <AlertCircle className="h-4 w-4 text-yellow-500" />
                        <AlertDescription>
                          Make sure you commit your initial changes before starting the orchestrator to avoid conflicts.
                        </AlertDescription>
                      </Alert>
                    </div>
                  </StepCard>
                </TabsContent>

                <TabsContent value="dart" className="space-y-6 mt-0">
                  <StepCard
                    title="Connect Dart Project Management"
                    description="Sync your tasks with Dart for advanced project tracking"
                    icon={Rocket}
                    stepId="dart"
                  >
                    <div className="space-y-4">
                      <Alert className="border-electric-cyan/20 bg-electric-cyan/5">
                        <Info className="h-4 w-4 text-electric-cyan" />
                        <AlertDescription>
                          Dart is an AI-native project management tool that integrates seamlessly with SplitMind for advanced task tracking and analytics.
                        </AlertDescription>
                      </Alert>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          1. Create a Dart account:
                        </p>
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full justify-between"
                          onClick={() => window.open('https://itsdart.com', '_blank')}
                        >
                          Visit Dart Website
                          <ExternalLink className="h-4 w-4 ml-2" />
                        </Button>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          2. Create a new workspace and dartboard for your project
                        </p>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          3. Find your Workspace and Dartboard IDs in the URL:
                        </p>
                        <div className="bg-muted/50 border border-border rounded-lg p-4">
                          <code className="text-sm text-muted-foreground">
                            https://app.itsdart.com/workspace/<span className="text-electric-cyan">workspace-id</span>/dartboard/<span className="text-electric-cyan">dartboard-id</span>
                          </code>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          4. Add these IDs to your project settings in SplitMind
                        </p>
                      </div>
                    </div>
                  </StepCard>
                </TabsContent>

                <TabsContent value="mcp" className="space-y-6 mt-0">
                  <StepCard
                    title="Install MCP Tools"
                    description="Add Model Context Protocol tools to enhance Claude's capabilities"
                    icon={Cpu}
                    stepId="mcp"
                  >
                    <div className="space-y-4">
                      <Alert className="border-electric-cyan/20 bg-electric-cyan/5">
                        <Info className="h-4 w-4 text-electric-cyan" />
                        <AlertDescription>
                          MCPs (Model Context Protocol) are tools that extend Claude's abilities with web search, file operations, and more.
                        </AlertDescription>
                      </Alert>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          1. Install popular MCP tools:
                        </p>
                        
                        {/* Dart MCP */}
                        <div className="space-y-2">
                          <p className="text-sm font-medium">Dart (Project Management):</p>
                          <CodeBlock itemId="mcp-dart">{`claude mcp add-json dart '{"command":"npx","args":["-y","dart-mcp-server"],"env":{"DART_TOKEN":"dsa_9aa6........."}}'`}</CodeBlock>
                          <p className="text-xs text-muted-foreground italic">Replace the token with your actual Dart API token</p>
                        </div>
                        
                        {/* Context7 MCP */}
                        <div className="space-y-2">
                          <p className="text-sm font-medium">Context7 (Memory & Context):</p>
                          <CodeBlock itemId="mcp-context7">claude mcp add --transport sse context7 https://mcp.context7.com/sse</CodeBlock>
                        </div>
                        
                        {/* Playwright MCP */}
                        <div className="space-y-2">
                          <p className="text-sm font-medium">Playwright (Browser Automation):</p>
                          <CodeBlock itemId="mcp-playwright">mcp add playwright --command "npx" --args "@playwright/mcp"</CodeBlock>
                        </div>
                        
                        {/* BrowserMCP */}
                        <div className="space-y-2">
                          <p className="text-sm font-medium">BrowserMCP (Web Browsing):</p>
                          <CodeBlock itemId="mcp-browsermcp">mcp add browsermcp --command "npx" --args "@browsermcp/mcp@latest"</CodeBlock>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          2. Copy MCPs from Claude Desktop (if you have them configured there):
                        </p>
                        <CodeBlock itemId="mcp-copy-desktop">claude mcp add-from-claude-desktop</CodeBlock>
                      </div>
                      
                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          3. List installed MCPs:
                        </p>
                        <CodeBlock itemId="mcp-list">claude mcp list</CodeBlock>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                          4. Check MCP status in SplitMind:
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Navigate to the Settings tab → MCP Diagnostics to see installed MCPs and troubleshoot issues.
                        </p>
                      </div>

                      <div className="rounded-lg border border-border bg-muted/30 p-4 space-y-3">
                        <h4 className="font-medium text-sm flex items-center gap-2">
                          <Cpu className="h-4 w-4 text-electric-cyan" />
                          MCP Benefits
                        </h4>
                        <div className="space-y-2">
                          <div className="flex items-start gap-2 text-sm">
                            <span className="text-electric-cyan">•</span>
                            <div>
                              <span className="font-medium">Dart:</span>
                              <span className="text-muted-foreground ml-1">Sync tasks with external project management</span>
                            </div>
                          </div>
                          <div className="flex items-start gap-2 text-sm">
                            <span className="text-electric-cyan">•</span>
                            <div>
                              <span className="font-medium">Context7:</span>
                              <span className="text-muted-foreground ml-1">Persistent memory across sessions</span>
                            </div>
                          </div>
                          <div className="flex items-start gap-2 text-sm">
                            <span className="text-electric-cyan">•</span>
                            <div>
                              <span className="font-medium">Playwright:</span>
                              <span className="text-muted-foreground ml-1">Automated browser testing</span>
                            </div>
                          </div>
                          <div className="flex items-start gap-2 text-sm">
                            <span className="text-electric-cyan">•</span>
                            <div>
                              <span className="font-medium">BrowserMCP:</span>
                              <span className="text-muted-foreground ml-1">Web research and navigation</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </StepCard>
                </TabsContent>
              </motion.div>
            </AnimatePresence>
          </ScrollArea>

          <div className="px-6 py-4 border-t border-border flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CheckCircle2 className="h-4 w-4" />
              {completedSteps.size} of {tabs.length} steps completed
            </div>
            <div className="flex items-center gap-2">
              {activeTab !== 'anthropic' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    const currentIndex = tabs.findIndex(t => t.id === activeTab);
                    if (currentIndex > 0) {
                      setActiveTab(tabs[currentIndex - 1].id);
                    }
                  }}
                >
                  Previous
                </Button>
              )}
              {activeTab !== 'mcp' ? (
                <Button
                  size="sm"
                  onClick={() => {
                    const currentIndex = tabs.findIndex(t => t.id === activeTab);
                    if (currentIndex < tabs.length - 1) {
                      setActiveTab(tabs[currentIndex + 1].id);
                    }
                  }}
                  className="bg-electric-cyan hover:bg-electric-cyan/80 text-dark-bg"
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              ) : (
                <Button
                  size="sm"
                  onClick={onClose}
                  className="bg-electric-cyan hover:bg-electric-cyan/80 text-dark-bg"
                >
                  Get Started
                </Button>
              )}
            </div>
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}