import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { 
  Cpu, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  RefreshCw, 
  Download,
  Terminal,
  Loader2,
  Copy,
  ExternalLink
} from 'lucide-react';


export function MCPDiagnostics() {
  const [isInstalling, setIsInstalling] = useState<string | null>(null);
  const [copiedCommand, setCopiedCommand] = useState<string | null>(null);

  // Check Claude CLI status
  const { data: cliStatus, isLoading: cliLoading, refetch: refetchCLI } = useQuery({
    queryKey: ['claude-cli'],
    queryFn: api.checkClaudeCLI,
    staleTime: 30000, // 30 seconds
  });

  // List MCPs
  const { data: mcpList, isLoading: mcpLoading, refetch: refetchMCPs } = useQuery({
    queryKey: ['mcp-list'],
    queryFn: api.listMCPs,
    enabled: cliStatus?.installed === true,
    staleTime: 30000,
  });

  const copyToClipboard = async (text: string, commandId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedCommand(commandId);
      setTimeout(() => setCopiedCommand(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const installMCP = async (name: string, command?: string) => {
    setIsInstalling(name);
    try {
      const result = await api.installMCP(name, command);
      if (result.success) {
        await refetchMCPs();
      } else {
        console.error('Failed to install MCP:', result.error);
      }
    } catch (error) {
      console.error('Error installing MCP:', error);
    } finally {
      setIsInstalling(null);
    }
  };

  const recommendedMCPs = [
    {
      name: 'dart',
      description: 'AI-native project management integration',
      command: '{"command":"npx","args":["-y","dart-mcp-server"],"env":{"DART_TOKEN":"your-token-here"}}',
      needsToken: true,
    },
    {
      name: 'context7',
      description: 'Context storage and retrieval for better AI memory',
      command: null,
      transport: 'sse',
    },
    {
      name: 'playwright',
      description: 'Browser automation and testing',
      command: '{"command":"npx","args":["@playwright/mcp"]}',
    },
    {
      name: 'browsermcp',
      description: 'Web browsing capabilities',
      command: '{"command":"npx","args":["@browsermcp/mcp@latest"]}',
    },
  ];

  const isInstalled = (mcpName: string) => {
    return mcpList?.mcps?.some(mcp => mcp.name === mcpName) || false;
  };

  if (cliLoading || mcpLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-electric-cyan" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Claude CLI Status */}
      <Card className="border-electric-cyan/20">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Terminal className="h-5 w-5 text-electric-cyan" />
              <CardTitle>Claude CLI Status</CardTitle>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => refetchCLI()}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {cliStatus?.installed ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                <span className="font-medium">Claude CLI is installed</span>
              </div>
              {cliStatus.version && (
                <div className="text-sm text-muted-foreground">
                  Version: {cliStatus.version}
                </div>
              )}
              {cliStatus.path && (
                <div className="text-sm text-muted-foreground">
                  Path: <code className="bg-muted px-1 rounded">{cliStatus.path}</code>
                </div>
              )}
            </div>
          ) : (
            <Alert className="border-red-500/20 bg-red-500/5">
              <XCircle className="h-4 w-4 text-red-500" />
              <AlertTitle>Claude CLI Not Found</AlertTitle>
              <AlertDescription className="space-y-3">
                <p>The Claude CLI is not installed on your system.</p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open('https://docs.anthropic.com/en/docs/claude-cli', '_blank')}
                  >
                    Installation Guide
                    <ExternalLink className="h-3 w-3 ml-1" />
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* MCP Status */}
      {cliStatus?.installed && (
        <>
          <Card className="border-electric-cyan/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="h-5 w-5 text-electric-cyan" />
                    Installed MCPs
                  </CardTitle>
                  <CardDescription>
                    Model Context Protocol tools extend Claude's capabilities
                  </CardDescription>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => refetchMCPs()}
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {mcpList?.success === false ? (
                <Alert className="border-yellow-500/20 bg-yellow-500/5">
                  <AlertCircle className="h-4 w-4 text-yellow-500" />
                  <AlertTitle>Error Loading MCPs</AlertTitle>
                  <AlertDescription>{mcpList.error}</AlertDescription>
                </Alert>
              ) : mcpList?.mcps && mcpList.mcps.length > 0 ? (
                <div className="space-y-3">
                  {mcpList.mcps.map((mcp) => (
                    <motion.div
                      key={mcp.name}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center justify-between p-3 rounded-lg bg-muted/50 border border-border"
                    >
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                        <div>
                          <div className="font-medium">{mcp.name}</div>
                          <div className="text-sm text-muted-foreground">
                            Transport: {mcp.transport}
                          </div>
                        </div>
                      </div>
                      {mcp.global && (
                        <Badge variant="secondary" className="text-xs">
                          Global
                        </Badge>
                      )}
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Cpu className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No MCPs installed yet</p>
                  <p className="text-sm mt-1">Install recommended MCPs below to get started</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recommended MCPs */}
          <Card className="border-electric-cyan/20">
            <CardHeader>
              <CardTitle>Recommended MCPs</CardTitle>
              <CardDescription>
                Install these tools to enhance Claude's capabilities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recommendedMCPs.map((mcp) => {
                  const installed = isInstalled(mcp.name);
                  const commandId = `mcp-${mcp.name}`;
                  
                  return (
                    <div
                      key={mcp.name}
                      className="border border-border rounded-lg p-4 space-y-3"
                    >
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-medium">{mcp.name}</h4>
                            {installed && (
                              <Badge variant="secondary" className="bg-green-500/10 text-green-500 border-green-500/20">
                                <CheckCircle2 className="h-3 w-3 mr-1" />
                                Installed
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {mcp.description}
                          </p>
                        </div>
                        {!installed && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => installMCP(mcp.name, mcp.command || undefined)}
                            disabled={isInstalling !== null || mcp.needsToken}
                          >
                            {isInstalling === mcp.name ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Installing...
                              </>
                            ) : (
                              <>
                                <Download className="h-4 w-4 mr-2" />
                                Install
                              </>
                            )}
                          </Button>
                        )}
                      </div>
                      
                      {/* Installation command */}
                      {!installed && (
                        <div className="space-y-2">
                          <p className="text-xs text-muted-foreground">Installation command:</p>
                          <div className="relative group">
                            <pre className="bg-muted/50 border border-border rounded p-3 pr-12 overflow-x-auto">
                              <code className="text-xs font-mono text-electric-cyan">
                                {mcp.name === 'dart' 
                                  ? `claude mcp add-json dart '${mcp.command}'`
                                  : mcp.name === 'context7'
                                  ? 'claude mcp add --transport sse context7 https://mcp.context7.com/sse'
                                  : mcp.command
                                  ? `claude mcp add-json ${mcp.name} '${mcp.command}'`
                                  : `claude mcp add -g ${mcp.name}`
                                }
                              </code>
                            </pre>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                              onClick={() => copyToClipboard(
                                mcp.name === 'dart' 
                                  ? `claude mcp add-json dart '${mcp.command}'`
                                  : mcp.name === 'context7'
                                  ? 'claude mcp add --transport sse context7 https://mcp.context7.com/sse'
                                  : mcp.command
                                  ? `claude mcp add-json ${mcp.name} '${mcp.command}'`
                                  : `claude mcp add -g ${mcp.name}`,
                                commandId
                              )}
                            >
                              {copiedCommand === commandId ? (
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                              ) : (
                                <Copy className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                          {mcp.needsToken && (
                            <Alert className="border-yellow-500/20 bg-yellow-500/5">
                              <AlertCircle className="h-4 w-4 text-yellow-500" />
                              <AlertDescription className="text-xs">
                                Replace "your-token-here" with your actual Dart API token
                              </AlertDescription>
                            </Alert>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              
              {/* Copy from Claude Desktop */}
              <div className="mt-6 pt-6 border-t border-border">
                <h4 className="font-medium mb-2">Copy MCPs from Claude Desktop</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  If you have MCPs configured in Claude Desktop, you can copy them all at once:
                </p>
                <div className="relative group">
                  <pre className="bg-muted/50 border border-border rounded p-3 pr-12">
                    <code className="text-sm font-mono text-electric-cyan">
                      claude mcp add-from-claude-desktop
                    </code>
                  </pre>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => copyToClipboard('claude mcp add-from-claude-desktop', 'copy-desktop')}
                  >
                    {copiedCommand === 'copy-desktop' ? (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}