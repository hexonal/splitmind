import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { 
  Settings, 
  Key, 
  Brain, 
  Users, 
  AlertCircle,
  CheckCircle2,
  Eye,
  EyeOff,
  Save,
  RefreshCw
} from 'lucide-react';

interface OrchestratorConfig {
  max_concurrent_agents: number;
  auto_merge: boolean;
  merge_strategy: string;
  auto_spawn_interval: number;
  enabled: boolean;
  anthropic_api_key?: string;
  anthropic_model?: string;
}

export function GlobalSettings() {
  const [showApiKey, setShowApiKey] = useState(false);
  const [formData, setFormData] = useState<OrchestratorConfig>({
    max_concurrent_agents: 5,
    auto_merge: false,
    merge_strategy: 'merge',
    auto_spawn_interval: 60,
    enabled: false,
    anthropic_api_key: '',
    anthropic_model: 'claude-3-sonnet-20240229',
  });
  const [hasChanges, setHasChanges] = useState(false);

  const queryClient = useQueryClient();

  // Fetch current configuration
  const { data: config, isLoading, error } = useQuery({
    queryKey: ['orchestrator-config'],
    queryFn: async () => {
      const response = await fetch('/api/orchestrator/config');
      if (!response.ok) throw new Error('Failed to fetch configuration');
      return response.json();
    },
  });

  // Update configuration mutation
  const updateMutation = useMutation({
    mutationFn: async (newConfig: OrchestratorConfig) => {
      const response = await fetch('/api/orchestrator/config', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig),
      });
      if (!response.ok) throw new Error('Failed to update configuration');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orchestrator-config'] });
      setHasChanges(false);
    },
  });

  // Load config data into form when it arrives
  useEffect(() => {
    if (config) {
      setFormData(config);
    }
  }, [config]);

  // Track changes
  useEffect(() => {
    if (config) {
      const changed = JSON.stringify(config) !== JSON.stringify(formData);
      setHasChanges(changed);
    }
  }, [config, formData]);

  const handleInputChange = (field: keyof OrchestratorConfig, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = () => {
    updateMutation.mutate(formData);
  };

  const handleReset = () => {
    if (config) {
      setFormData(config);
    }
  };

  const validateApiKey = (key: string) => {
    return key.startsWith('sk-ant-') && key.length > 20;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-electric-cyan mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading settings...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="border-red-500/20 bg-red-500/5">
        <AlertCircle className="h-4 w-4 text-red-500" />
        <AlertDescription>
          Failed to load configuration settings
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Settings className="w-8 h-8 text-electric-cyan" />
            Global Settings
          </h1>
          <p className="text-muted-foreground mt-1">
            Configure SplitMind orchestrator and API settings
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {hasChanges && (
            <Badge variant="outline" className="text-yellow-400 border-yellow-400/20">
              Unsaved Changes
            </Badge>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
            disabled={!hasChanges}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Reset
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={handleSave}
            disabled={!hasChanges || updateMutation.isPending}
          >
            <Save className="w-4 h-4 mr-2" />
            {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Anthropic API Configuration */}
        <Card className="border-electric-cyan/20 bg-card/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-electric-cyan" />
              Anthropic API
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="api-key">API Key</Label>
              <div className="relative">
                <Input
                  id="api-key"
                  type={showApiKey ? "text" : "password"}
                  value={formData.anthropic_api_key || ''}
                  onChange={(e) => handleInputChange('anthropic_api_key', e.target.value)}
                  placeholder="sk-ant-..."
                  className="pr-20"
                />
                <div className="absolute right-2 top-2.5 flex items-center space-x-1">
                  {formData.anthropic_api_key && validateApiKey(formData.anthropic_api_key) && (
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="h-6 w-6 p-0"
                  >
                    {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
              {formData.anthropic_api_key && !validateApiKey(formData.anthropic_api_key) && (
                <p className="text-xs text-red-400">Invalid API key format</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Select
                value={formData.anthropic_model || 'claude-3-sonnet-20240229'}
                onValueChange={(value) => handleInputChange('anthropic_model', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="claude-3-opus-20240229">Claude 3 Opus</SelectItem>
                  <SelectItem value="claude-3-sonnet-20240229">Claude 3 Sonnet</SelectItem>
                  <SelectItem value="claude-3-haiku-20240307">Claude 3 Haiku</SelectItem>
                  <SelectItem value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Alert className="border-blue-500/20 bg-blue-500/5">
              <Key className="h-4 w-4 text-blue-500" />
              <AlertDescription className="text-xs">
                Your API key is stored securely and used for AI plan generation and task processing.
                Get your key from the <a 
                  href="https://console.anthropic.com/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-electric-cyan hover:underline"
                >
                  Anthropic Console
                </a>
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        {/* Orchestrator Configuration */}
        <Card className="border-electric-cyan/20 bg-card/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-electric-cyan" />
              Orchestrator Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-sm font-medium">Enable Orchestrator</Label>
                <p className="text-xs text-muted-foreground">
                  Automatically spawn and manage AI agents
                </p>
              </div>
              <Switch
                checked={formData.enabled}
                onCheckedChange={(checked) => handleInputChange('enabled', checked)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="max-agents">Max Concurrent Agents</Label>
              <Input
                id="max-agents"
                type="number"
                min="1"
                max="20"
                value={formData.max_concurrent_agents}
                onChange={(e) => handleInputChange('max_concurrent_agents', parseInt(e.target.value) || 1)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="spawn-interval">Auto Spawn Interval (seconds)</Label>
              <Input
                id="spawn-interval"
                type="number"
                min="10"
                max="600"
                value={formData.auto_spawn_interval}
                onChange={(e) => handleInputChange('auto_spawn_interval', parseInt(e.target.value) || 60)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-sm font-medium">Auto Merge</Label>
                <p className="text-xs text-muted-foreground">
                  Automatically merge completed tasks
                </p>
              </div>
              <Switch
                checked={formData.auto_merge}
                onCheckedChange={(checked) => handleInputChange('auto_merge', checked)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="merge-strategy">Merge Strategy</Label>
              <Select
                value={formData.merge_strategy}
                onValueChange={(value) => handleInputChange('merge_strategy', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select strategy" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="merge">Merge (create merge commit)</SelectItem>
                  <SelectItem value="rebase">Rebase (linear history)</SelectItem>
                  <SelectItem value="squash">Squash (single commit)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Status Information */}
      <Card className="border-electric-cyan/20 bg-card/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-electric-cyan" />
            Configuration Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                formData.anthropic_api_key && validateApiKey(formData.anthropic_api_key) 
                  ? 'bg-green-500' 
                  : 'bg-red-500'
              }`}></div>
              <span className="text-sm">API Key {
                formData.anthropic_api_key && validateApiKey(formData.anthropic_api_key) 
                  ? 'Valid' 
                  : 'Invalid'
              }</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                formData.enabled ? 'bg-green-500' : 'bg-gray-500'
              }`}></div>
              <span className="text-sm">Orchestrator {formData.enabled ? 'Enabled' : 'Disabled'}</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                hasChanges ? 'bg-yellow-500' : 'bg-green-500'
              }`}></div>
              <span className="text-sm">{hasChanges ? 'Unsaved Changes' : 'Settings Saved'}</span>
            </div>
          </div>
          
          {hasChanges && (
            <Alert className="border-yellow-500/20 bg-yellow-500/5 mt-4">
              <AlertCircle className="h-4 w-4 text-yellow-500" />
              <AlertDescription className="text-xs">
                You have unsaved changes. Click "Save Settings" to apply them.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
}