import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { api } from '@/services/api';
import { Project } from '@/types';
import { Settings, Sparkles, FileText, Save, AlertCircle, CheckCircle, DollarSign } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { OrchestratorSettings } from '@/components/OrchestratorSettings';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface ProjectSettingsProps {
  project: Project;
}

export function ProjectSettings({ project }: ProjectSettingsProps) {
  const [projectOverview, setProjectOverview] = useState(project.project_overview || '');
  const [initialPrompt, setInitialPrompt] = useState(project.initial_prompt || '');
  const [dartWorkspace, setDartWorkspace] = useState('');
  const [dartDartboard, setDartDartboard] = useState('');
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [lastCostInfo, setLastCostInfo] = useState<any>(null);
  const queryClient = useQueryClient();

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
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', project.id] });
      if (data.cost_info) {
        setLastCostInfo(data.cost_info);
      }
    },
    onError: (error: any) => {
      alert(`Failed to generate plan: ${error.message}`);
    }
  });

  const handleSave = () => {
    setSaveStatus('saving');
    updateProjectMutation.mutate({
      project_overview: projectOverview,
      initial_prompt: initialPrompt
    });
  };

  const handleGeneratePlan = () => {
    if (!projectOverview || !initialPrompt) {
      alert('Please provide both project overview and initial prompt');
      return;
    }
    generatePlanMutation.mutate();
  };

  return (
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
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="plan">Plan</TabsTrigger>
            <TabsTrigger value="api">API Settings</TabsTrigger>
            <TabsTrigger value="integrations">Integrations</TabsTrigger>
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
                  variant="glow"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  {generatePlanMutation.isPending ? 'Generating...' : 'Generate Plan & Tasks'}
                </Button>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="plan" className="space-y-4">
            <div className="space-y-2">
              <Label>Generated Plan</Label>
              {project.plan ? (
                <div className="bg-dark-bg/50 border border-electric-cyan/20 rounded-md p-4">
                  <pre className="whitespace-pre-wrap text-sm">{project.plan}</pre>
                </div>
              ) : (
                <div className="bg-dark-bg/50 border border-electric-cyan/20 rounded-md p-4 text-center text-muted-foreground">
                  <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No plan generated yet. Configure the overview and initial prompt, then click "Generate Plan & Tasks".</p>
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
        </Tabs>
      </CardContent>
    </Card>
  );
}