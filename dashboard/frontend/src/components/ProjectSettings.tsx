import { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { api } from '@/services/api';
import { Project } from '@/types';
import { Settings, Sparkles, FileText, Save, AlertCircle, CheckCircle, DollarSign, GitBranch, AlertTriangle, Zap, Skull } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { OrchestratorSettings } from '@/components/OrchestratorSettings';
import { MCPDiagnostics } from '@/components/MCPDiagnostics';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { TaskGenerationModal } from '@/components/TaskGenerationModal';

interface ProjectSettingsProps {
  project: Project;
}

export function ProjectSettings({ project }: ProjectSettingsProps) {
  const [projectOverview, setProjectOverview] = useState(project.project_overview || '');
  const [initialPrompt, setInitialPrompt] = useState(project.initial_prompt || '');
  const [plan, setPlan] = useState(project.plan || '');
  const [isEditingPlan, setIsEditingPlan] = useState(false);
  const [dartWorkspace, setDartWorkspace] = useState('');
  const [dartDartboard, setDartDartboard] = useState('');
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [lastCostInfo, setLastCostInfo] = useState<any>(null);
  const [showTaskGenerationModal, setShowTaskGenerationModal] = useState(false);
  const queryClient = useQueryClient();

  // Git status query
  const { data: gitStatus, refetch: refetchGitStatus } = useQuery({
    queryKey: ['git-status', project.id],
    queryFn: () => api.getGitStatus(project.id),
    staleTime: 30000, // 30 seconds
  });

  const updateProjectMutation = useMutation({
    mutationFn: (updates: Partial<Project>) => 
      api.updateProject(project.id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);
    },
    onError: () => {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  });

  const generatePlanMutation = useMutation({
    mutationFn: () => 
      api.generatePlan(project.id, {
        project_overview: projectOverview,
        initial_prompt: initialPrompt,
        dart_workspace: dartWorkspace,
        dart_dartboard: dartDartboard
      }),
    onSuccess: (data) => {
      // Update the cost info first
      if (data.cost_info) {
        setLastCostInfo(data.cost_info);
      }
      
      // Update the specific project in the cache
      queryClient.setQueryData(['projects'], (oldData: any) => {
        if (!oldData || !Array.isArray(oldData)) return oldData;
        return oldData.map((p: any) => 
          p.id === project.id 
            ? { ...p, plan: data.plan, project_overview: projectOverview, initial_prompt: initialPrompt }
            : p
        );
      });
      
      // Then invalidate tasks to refetch the new ones
      queryClient.invalidateQueries({ queryKey: ['tasks', project.id] });
      
      // Also invalidate the single project query if it exists
      queryClient.invalidateQueries({ queryKey: ['project', project.id] });
    },
    onError: (error: any) => {
      alert(`Failed to generate plan: ${error.message}`);
    }
  });

  const generateTaskBreakdownMutation = useMutation({
    mutationFn: () => 
      api.generateTaskBreakdown(project.id, {
        project_overview: projectOverview,
        initial_prompt: initialPrompt
      }),
    onMutate: () => {
      // Show the modal when starting
      setShowTaskGenerationModal(true);
    },
    onSuccess: (data) => {
      // Hide the modal on success
      setShowTaskGenerationModal(false);
      
      // Update the cost info first
      if (data.cost_info) {
        setLastCostInfo(data.cost_info);
      }
      
      // Update the specific project in the cache
      queryClient.setQueryData(['projects'], (oldData: any) => {
        if (!oldData || !Array.isArray(oldData)) return oldData;
        return oldData.map((p: any) => 
          p.id === project.id 
            ? { ...p, plan: data.plan, project_overview: projectOverview, initial_prompt: initialPrompt }
            : p
        );
      });
      
      // Then invalidate tasks to refetch the new ones
      queryClient.invalidateQueries({ queryKey: ['tasks', project.id] });
      
      // Also invalidate the single project query if it exists
      queryClient.invalidateQueries({ queryKey: ['project', project.id] });
      
      alert(`🎉 Task Master AI has successfully generated ${data.tasks_created} structured tasks with custom prompts!`);
    },
    onError: (error: any) => {
      // Hide the modal on error
      setShowTaskGenerationModal(false);
      alert(`Failed to generate task breakdown: ${error.message}`);
    }
  });

  const initGitMutation = useMutation({
    mutationFn: () => api.initGitRepo(project.id),
    onSuccess: () => {
      refetchGitStatus();
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
    onError: (error: any) => {
      alert(`Failed to initialize Git: ${error.message}`);
    }
  });

  const resetProjectMutation = useMutation({
    mutationFn: () => api.resetProject(project.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', project.id] });
      queryClient.invalidateQueries({ queryKey: ['agents', project.id] });
      alert('Project has been reset successfully');
    },
    onError: (error: any) => {
      alert(`Failed to reset project: ${error.message}`);
    }
  });

  const handleSave = () => {
    setSaveStatus('saving');
    updateProjectMutation.mutate({
      project_overview: projectOverview,
      initial_prompt: initialPrompt
    });
  };

  const handleSavePlan = () => {
    setSaveStatus('saving');
    updateProjectMutation.mutate({
      plan: plan
    });
    setIsEditingPlan(false);
  };

  const handleGeneratePlan = () => {
    if (!projectOverview || !initialPrompt) {
      alert('Please provide both project overview and initial prompt');
      return;
    }
    generatePlanMutation.mutate();
  };

  const handleGenerateTaskBreakdown = () => {
    if (!projectOverview || !initialPrompt) {
      alert('Please provide both project overview and initial prompt');
      return;
    }
    generateTaskBreakdownMutation.mutate();
  };

  return (
    <>
      <Card className="bg-deep-indigo/50 border-electric-cyan/20">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Settings className="w-5 h-5" />
          <span>Project Settings</span>
        </CardTitle>
        <CardDescription>
          Configure your project overview and initial prompt for AI orchestration
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-7">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="plan">Plan</TabsTrigger>
            <TabsTrigger value="git">Git</TabsTrigger>
            <TabsTrigger value="api">API Settings</TabsTrigger>
            <TabsTrigger value="integrations">Integrations</TabsTrigger>
            <TabsTrigger value="mcp">MCP Status</TabsTrigger>
            <TabsTrigger value="danger" className="text-yellow-400 bg-black/50 data-[state=active]:bg-black data-[state=active]:text-yellow-300">
              <Skull className="w-4 h-4 mr-1" />
              DANGER
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="project-overview">Project Overview</Label>
              <Textarea
                id="project-overview"
                value={projectOverview}
                onChange={(e) => setProjectOverview(e.target.value)}
                placeholder="Provide a detailed overview of your project, including its purpose, target audience, key features, and any technical requirements..."
                className="min-h-[150px] bg-dark-bg/50 border-electric-cyan/20"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="initial-prompt">Initial Prompt</Label>
              <Textarea
                id="initial-prompt"
                value={initialPrompt}
                onChange={(e) => setInitialPrompt(e.target.value)}
                placeholder="What would you like the AI orchestrator to help you build? Be specific about features, functionality, and any constraints..."
                className="min-h-[100px] bg-dark-bg/50 border-electric-cyan/20"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {saveStatus === 'saved' && (
                  <div className="flex items-center space-x-1 text-green-500">
                    <CheckCircle className="w-4 h-4" />
                    <span className="text-sm">Settings saved</span>
                  </div>
                )}
                {saveStatus === 'error' && (
                  <div className="flex items-center space-x-1 text-red-500">
                    <AlertCircle className="w-4 h-4" />
                    <span className="text-sm">Failed to save</span>
                  </div>
                )}
              </div>
              <div className="flex space-x-2">
                <Button
                  onClick={handleSave}
                  disabled={updateProjectMutation.isPending}
                  variant="outline"
                  className="border-electric-cyan/20"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {updateProjectMutation.isPending ? 'Saving...' : 'Save Settings'}
                </Button>
                
                <Button
                  onClick={handleGeneratePlan}
                  disabled={generatePlanMutation.isPending || !projectOverview || !initialPrompt}
                  variant="outline"
                  className="border-electric-cyan/20"
                  title="Generate a basic plan with simple task list"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  {generatePlanMutation.isPending ? 'Generating...' : 'Basic Plan Generation'}
                </Button>
                
                <Button
                  onClick={handleGenerateTaskBreakdown}
                  disabled={generateTaskBreakdownMutation.isPending || !projectOverview || !initialPrompt}
                  variant="glow"
                  title="Generate comprehensive plan + wave-based tasks with custom AI prompts"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  {generateTaskBreakdownMutation.isPending ? 'Generating...' : '🚀 AI Task Master (Plan + Tasks)'}
                </Button>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="plan" className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Generated Plan</Label>
                <div className="flex items-center space-x-2">
                  {project.plan && (
                    <Button
                      onClick={() => setIsEditingPlan(!isEditingPlan)}
                      variant="outline"
                      size="sm"
                      className="border-electric-cyan/20"
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      {isEditingPlan ? 'Cancel Edit' : 'Edit Plan'}
                    </Button>
                  )}
                </div>
              </div>
              
              {project.plan ? (
                isEditingPlan ? (
                  <div className="space-y-4">
                    <Textarea
                      value={plan}
                      onChange={(e) => setPlan(e.target.value)}
                      className="min-h-[300px] bg-dark-bg/50 border-electric-cyan/20 font-mono text-sm"
                      placeholder="Edit your project plan..."
                    />
                    <div className="flex space-x-2">
                      <Button
                        onClick={handleSavePlan}
                        disabled={updateProjectMutation.isPending}
                        variant="glow"
                      >
                        <Save className="w-4 h-4 mr-2" />
                        {updateProjectMutation.isPending ? 'Saving...' : 'Save Plan'}
                      </Button>
                      <Button
                        onClick={() => {
                          setIsEditingPlan(false);
                          setPlan(project.plan || '');
                        }}
                        variant="outline"
                        className="border-electric-cyan/20"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="bg-dark-bg/50 border border-electric-cyan/20 rounded-md p-4">
                    <pre className="whitespace-pre-wrap text-sm">{project.plan}</pre>
                  </div>
                )
              ) : (
                <div className="bg-dark-bg/50 border border-electric-cyan/20 rounded-md p-4 text-center text-muted-foreground">
                  <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="mb-2">No plan generated yet.</p>
                  <p className="text-sm">
                    Configure the overview and initial prompt in the Overview tab, then use:
                  </p>
                  <div className="mt-3 space-y-2 text-sm">
                    <div className="flex items-center justify-center space-x-2">
                      <Sparkles className="w-4 h-4" />
                      <span><strong>Basic Plan:</strong> Simple plan with basic tasks</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2 text-electric-cyan">
                      <Zap className="w-4 h-4" />
                      <span><strong>AI Task Master:</strong> Comprehensive plan + structured tasks (Recommended)</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {lastCostInfo && (
              <Alert className="border-electric-cyan/20 mt-4">
                <DollarSign className="h-4 w-4" />
                <AlertDescription>
                  <strong>Last generation cost:</strong> ${lastCostInfo.total_cost?.toFixed(4) || '0.0000'}
                  <span className="text-xs text-muted-foreground ml-2">
                    ({lastCostInfo.input_tokens || 0} input + {lastCostInfo.output_tokens || 0} output tokens)
                  </span>
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>
          
          <TabsContent value="git" className="space-y-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold flex items-center space-x-2">
                    <GitBranch className="w-5 h-5" />
                    <span>Git Repository Status</span>
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Manage Git version control for your project
                  </p>
                </div>
              </div>

              {gitStatus && !gitStatus.is_git_repo && (
                <Alert className="border-yellow-500/20 bg-yellow-500/10">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  <AlertDescription className="text-yellow-200">
                    <strong>Not a Git repository</strong>
                    <p className="mt-2">
                      This project directory is not initialized as a Git repository. 
                      Git is required for SplitMind to manage branches and worktrees for AI agents.
                    </p>
                    <Button
                      onClick={() => initGitMutation.mutate()}
                      disabled={initGitMutation.isPending}
                      variant="outline"
                      className="mt-3 border-yellow-500/50 hover:bg-yellow-500/20"
                    >
                      <GitBranch className="w-4 h-4 mr-2" />
                      {initGitMutation.isPending ? 'Initializing...' : 'Initialize Git Repository'}
                    </Button>
                  </AlertDescription>
                </Alert>
              )}

              {gitStatus && gitStatus.is_git_repo && (
                <div className="space-y-4">
                  <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                    <div className="flex items-center space-x-2 text-green-400">
                      <CheckCircle className="w-5 h-5" />
                      <span className="font-medium">Git repository initialized</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-dark-bg/50 border border-electric-cyan/20 rounded-md p-4">
                      <Label className="text-sm text-muted-foreground">Current Branch</Label>
                      <p className="mt-1 font-mono">{gitStatus.current_branch || 'Unknown'}</p>
                    </div>
                    
                    <div className="bg-dark-bg/50 border border-electric-cyan/20 rounded-md p-4">
                      <Label className="text-sm text-muted-foreground">Uncommitted Changes</Label>
                      <p className="mt-1">
                        {gitStatus.has_changes ? (
                          <span className="text-yellow-400">Changes detected</span>
                        ) : (
                          <span className="text-green-400">Working tree clean</span>
                        )}
                      </p>
                    </div>
                  </div>

                  {gitStatus.remote_url && (
                    <div className="bg-dark-bg/50 border border-electric-cyan/20 rounded-md p-4">
                      <Label className="text-sm text-muted-foreground">Remote Repository</Label>
                      <p className="mt-1 font-mono text-sm truncate">{gitStatus.remote_url}</p>
                    </div>
                  )}

                  {gitStatus.error && (
                    <Alert className="border-red-500/20 bg-red-500/10">
                      <AlertCircle className="h-4 w-4 text-red-500" />
                      <AlertDescription className="text-red-200">
                        <strong>Git Error:</strong> {gitStatus.error}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              )}

              <div className="pt-4 border-t border-electric-cyan/10">
                <Button
                  onClick={() => refetchGitStatus()}
                  variant="outline"
                  size="sm"
                  className="border-electric-cyan/20"
                >
                  Refresh Status
                </Button>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="api" className="space-y-4">
            <OrchestratorSettings />
          </TabsContent>
          
          <TabsContent value="integrations" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="dart-workspace">Dart Workspace ID</Label>
              <input
                id="dart-workspace"
                type="text"
                value={dartWorkspace}
                onChange={(e) => setDartWorkspace(e.target.value)}
                placeholder="ws_123456"
                className="w-full px-3 py-2 bg-dark-bg/50 border border-electric-cyan/20 rounded-md"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="dart-dartboard">Dart Dartboard ID</Label>
              <input
                id="dart-dartboard"
                type="text"
                value={dartDartboard}
                onChange={(e) => setDartDartboard(e.target.value)}
                placeholder="db_789012"
                className="w-full px-3 py-2 bg-dark-bg/50 border border-electric-cyan/20 rounded-md"
              />
            </div>
            
            <p className="text-sm text-muted-foreground">
              Configure external integrations like Dart to sync tasks and updates.
            </p>
          </TabsContent>
          
          <TabsContent value="mcp" className="space-y-4">
            <MCPDiagnostics />
          </TabsContent>
          
          <TabsContent value="danger" className="space-y-4">
            <div className="bg-yellow-400/20 border-2 border-yellow-400 p-4 rounded-lg">
              <div className="flex items-center space-x-3 mb-3">
                <div className="flex space-x-1">
                  <div className="w-4 h-16 bg-black"></div>
                  <div className="w-4 h-16 bg-yellow-400"></div>
                  <div className="w-4 h-16 bg-black"></div>
                  <div className="w-4 h-16 bg-yellow-400"></div>
                  <div className="w-4 h-16 bg-black"></div>
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-yellow-400 flex items-center">
                    <Skull className="w-8 h-8 mr-2" />
                    DANGER ZONE - NUCLEAR OPTION
                  </h3>
                  <p className="text-yellow-300 mt-1">
                    WARNING: Destructive operations that cannot be undone!
                  </p>
                </div>
                <div className="flex space-x-1">
                  <div className="w-4 h-16 bg-black"></div>
                  <div className="w-4 h-16 bg-yellow-400"></div>
                  <div className="w-4 h-16 bg-black"></div>
                  <div className="w-4 h-16 bg-yellow-400"></div>
                  <div className="w-4 h-16 bg-black"></div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4 mt-6">
              <Card className="border-4 border-yellow-400/50 bg-black/90 overflow-hidden relative">
                <div className="absolute inset-0 opacity-10">
                  <div className="absolute inset-0" style={{
                    backgroundImage: 'repeating-linear-gradient(45deg, #000 0, #000 10px, #facc15 10px, #facc15 20px)',
                  }}></div>
                </div>
                <CardHeader className="relative">
                  <CardTitle className="text-yellow-400 flex items-center space-x-2 text-xl">
                    <div className="relative">
                      <Zap className="w-8 h-8 absolute animate-pulse" />
                      <Skull className="w-8 h-8 relative" />
                    </div>
                    <span className="font-black uppercase tracking-wider">TOTAL PROJECT RESET</span>
                  </CardTitle>
                  <CardDescription className="text-yellow-300/90 font-semibold">
                    ⚠️ THIS IS THE NUCLEAR OPTION - COMPLETE PROJECT WIPE ⚠️
                  </CardDescription>
                </CardHeader>
                <CardContent className="relative">
                  <div className="space-y-4">
                    <Alert className="border-2 border-yellow-400 bg-black/80">
                      <AlertTriangle className="h-6 w-6 text-yellow-400" />
                      <AlertDescription className="text-yellow-300">
                        <p className="font-bold mb-2">THIS WILL DESTROY:</p>
                        <ul className="list-none space-y-1 ml-6">
                          <li className="flex items-center"><Skull className="w-4 h-4 mr-2" /> ALL tasks will be obliterated</li>
                          <li className="flex items-center"><Skull className="w-4 h-4 mr-2" /> ALL AI agents will be terminated</li>
                          <li className="flex items-center"><Skull className="w-4 h-4 mr-2" /> ALL Git worktrees will be vaporized</li>
                          <li className="flex items-center"><Skull className="w-4 h-4 mr-2" /> ALL branches (except main) will be deleted</li>
                          <li className="flex items-center"><Skull className="w-4 h-4 mr-2" /> ALL temporary files will be purged</li>
                        </ul>
                        <p className="mt-4 font-black text-lg text-center animate-pulse">
                          ☢️ THERE IS NO UNDO! ☢️
                        </p>
                      </AlertDescription>
                    </Alert>
                    
                    <div className="flex justify-center pt-4">
                      <Button
                        onClick={() => {
                          const confirmed = confirm(
                            '⚠️ NUCLEAR OPTION WARNING ⚠️\n\n' +
                            'This will COMPLETELY DESTROY your project state:\n\n' +
                            '💀 ALL tasks will be deleted\n' +
                            '💀 ALL agent sessions will be killed\n' +
                            '💀 ALL worktrees will be removed\n' +
                            '💀 ALL branches will be deleted (except main)\n\n' +
                            '☢️ THIS CANNOT BE UNDONE! ☢️\n\n' +
                            'Type "YES" to confirm you understand the consequences.'
                          );
                          if (confirmed) {
                            const finalConfirm = prompt(
                              '🚨 FINAL WARNING 🚨\n\n' +
                              'This is your LAST CHANCE to cancel.\n\n' +
                              'To proceed with the NUCLEAR RESET, type the project name exactly:\n\n' +
                              `"${project.name}"`
                            );
                            if (finalConfirm === project.name) {
                              resetProjectMutation.mutate();
                            } else if (finalConfirm !== null) {
                              alert('Project name did not match. Reset cancelled.');
                            }
                          }
                        }}
                        disabled={resetProjectMutation.isPending}
                        className="bg-yellow-400 hover:bg-yellow-500 text-black font-black text-lg px-8 py-6 border-4 border-black shadow-[0_0_20px_rgba(250,204,21,0.5)] hover:shadow-[0_0_30px_rgba(250,204,21,0.8)] transition-all"
                      >
                        <div className="flex items-center space-x-3">
                          <Zap className="w-6 h-6 animate-pulse" />
                          <span className="uppercase tracking-wider">
                            {resetProjectMutation.isPending ? 'DETONATING...' : 'INITIATE NUCLEAR RESET'}
                          </span>
                          <Skull className="w-6 h-6 animate-pulse" />
                        </div>
                      </Button>
                    </div>
                    
                    <div className="text-center text-yellow-400/80 text-sm mt-4 font-semibold">
                      ⚡ Use only in extreme emergency situations ⚡
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
    
      {/* Task Generation Modal */}
      <TaskGenerationModal 
        open={showTaskGenerationModal} 
        onOpenChange={setShowTaskGenerationModal}
      />
    </>
  );
}