import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { api } from '@/services/api';
import { OrchestratorConfig } from '@/types';
import { Key, Brain, Save, AlertCircle, CheckCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const AVAILABLE_MODELS = [
  { id: 'claude-sonnet-4-20250514', name: 'Claude Sonnet 4 (Latest)', pricing: '$3/$15' },
  { id: 'claude-opus-4-20250514', name: 'Claude Opus 4', pricing: '$15/$75' },
  { id: 'claude-3-5-sonnet-20241022', name: 'Claude 3.5 Sonnet', pricing: '$3/$15' },
  { id: 'claude-3-5-haiku-20241022', name: 'Claude 3.5 Haiku', pricing: '$0.80/$4' },
  { id: 'claude-3-opus-20240229', name: 'Claude 3 Opus', pricing: '$15/$75' },
  { id: 'claude-3-haiku-20240307', name: 'Claude 3 Haiku', pricing: '$0.25/$1.25' },
];

export function OrchestratorSettings() {
  const [apiKey, setApiKey] = useState('');
  const [selectedModel, setSelectedModel] = useState('claude-sonnet-4-20250514');
  const [showApiKey, setShowApiKey] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const queryClient = useQueryClient();

  // Fetch current config
  const { data: config } = useQuery({
    queryKey: ['orchestrator-config'],
    queryFn: api.getOrchestratorConfig,
  });

  // Update state when config loads
  useEffect(() => {
    if (config) {
      setApiKey(config.anthropic_api_key || '');
      setSelectedModel(config.anthropic_model || 'claude-sonnet-4-20250514');
    }
  }, [config]);

  const updateConfigMutation = useMutation({
    mutationFn: (updates: Partial<OrchestratorConfig>) => 
      api.updateOrchestratorConfig({ ...config!, ...updates }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orchestrator-config'] });
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);
    },
    onError: () => {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  });

  const handleSave = () => {
    setSaveStatus('saving');
    updateConfigMutation.mutate({
      anthropic_api_key: apiKey,
      anthropic_model: selectedModel
    });
  };

  const selectedModelInfo = AVAILABLE_MODELS.find(m => m.id === selectedModel);

  return (
    <Card className="bg-deep-indigo/50 border-electric-cyan/20">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Key className="w-5 h-5" />
          <span>API Configuration</span>
        </CardTitle>
        <CardDescription>
          Configure your Anthropic API key and model preferences for plan generation
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="api-key">Anthropic API Key</Label>
          <div className="flex space-x-2">
            <Input
              id="api-key"
              type={showApiKey ? "text" : "password"}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-ant-..."
              className="bg-dark-bg/50 border-electric-cyan/20"
              autoComplete="off"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowApiKey(!showApiKey)}
              className="border-electric-cyan/20"
            >
              {showApiKey ? 'Hide' : 'Show'}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            Your API key is stored locally and used only for plan generation.
            Get one at <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer" className="text-electric-cyan hover:underline">console.anthropic.com</a>
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="model">Model</Label>
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="bg-dark-bg/50 border-electric-cyan/20">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {AVAILABLE_MODELS.map(model => (
                <SelectItem key={model.id} value={model.id}>
                  <div className="flex items-center justify-between w-full">
                    <span>{model.name}</span>
                    <span className="text-xs text-muted-foreground ml-2">
                      {model.pricing} per MTok
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground">
            Pricing: Input/Output per million tokens. 
            <a href="https://docs.anthropic.com/en/docs/about-claude/pricing" target="_blank" rel="noopener noreferrer" className="text-electric-cyan hover:underline ml-1">
              View details
            </a>
          </p>
        </div>

        {selectedModelInfo && (
          <Alert className="border-electric-cyan/20">
            <Brain className="h-4 w-4" />
            <AlertDescription>
              <strong>{selectedModelInfo.name}</strong> costs {selectedModelInfo.pricing} per million tokens (input/output).
              Plan generation typically uses ~2-3k input and ~2-4k output tokens.
              Estimated cost per plan: ~$0.02-0.08
            </AlertDescription>
          </Alert>
        )}

        <div className="flex items-center justify-between pt-4">
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
          <Button
            onClick={handleSave}
            disabled={updateConfigMutation.isPending || !apiKey}
            variant="glow"
          >
            <Save className="w-4 h-4 mr-2" />
            {updateConfigMutation.isPending ? 'Saving...' : 'Save API Settings'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}