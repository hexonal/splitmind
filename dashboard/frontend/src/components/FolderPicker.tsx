import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { 
  Folder, 
  FolderOpen, 
  Home, 
  ChevronUp, 
  GitBranch,
  HardDrive,
  Check,
  FolderPlus
} from 'lucide-react';
import { motion } from 'framer-motion';

interface FolderPickerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelect: (path: string) => void;
  currentPath?: string;
}

interface DirectoryItem {
  name: string;
  path: string;
  is_git_repo: boolean;
}

interface FilesystemData {
  current_path: string;
  parent_path: string | null;
  directories: DirectoryItem[];
  quick_access: { name: string; path: string }[];
  platform: string;
}

export function FolderPicker({ open, onOpenChange, onSelect, currentPath }: FolderPickerProps) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<FilesystemData | null>(null);
  const [selectedPath, setSelectedPath] = useState(currentPath || '');
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [createError, setCreateError] = useState('');

  const fetchDirectory = async (path?: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (path) params.append('path', path);
      
      const response = await fetch(`/api/filesystem/browse?${params}`);
      const result = await response.json();
      setData(result);
      setSelectedPath(result.current_path);
    } catch (error) {
      console.error('Failed to browse filesystem:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      fetchDirectory(currentPath);
    }
  }, [open, currentPath]);

  const handleSelect = () => {
    onSelect(selectedPath);
    onOpenChange(false);
  };

  const navigateTo = (path: string) => {
    fetchDirectory(path);
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) {
      setCreateError('Folder name is required');
      return;
    }

    try {
      const response = await fetch('/api/filesystem/create-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_path: data?.current_path || selectedPath,
          folder_name: newFolderName.trim()
        })
      });

      if (!response.ok) {
        const error = await response.json();
        setCreateError(error.detail || 'Failed to create folder');
        return;
      }

      const result = await response.json();
      
      // Refresh the current directory
      await fetchDirectory(data?.current_path);
      
      // Select the new folder
      setSelectedPath(result.path);
      
      // Reset form
      setShowCreateFolder(false);
      setNewFolderName('');
      setCreateError('');
    } catch (error) {
      setCreateError('Failed to create folder');
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] bg-dark-bg/95 border-electric-cyan/20">
        <DialogHeader>
          <DialogTitle className="text-electric-cyan flex items-center space-x-2">
            <FolderOpen className="w-5 h-5" />
            <span>Select Project Folder</span>
          </DialogTitle>
          <DialogDescription>
            Choose a Git repository folder for your project
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Current Path */}
          <div className="flex items-center space-x-2 p-2 bg-deep-indigo/30 rounded-md">
            <HardDrive className="w-4 h-4 text-electric-cyan" />
            <span className="text-sm font-mono flex-1 truncate">{data?.current_path || selectedPath}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowCreateFolder(!showCreateFolder)}
              title="Create new folder"
              className="hover:bg-electric-cyan/20"
            >
              <FolderPlus className="w-4 h-4" />
            </Button>
            {data?.parent_path && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigateTo(data.parent_path!)}
                title="Go to parent folder"
              >
                <ChevronUp className="w-4 h-4" />
              </Button>
            )}
          </div>

          {/* Create Folder Form */}
          {showCreateFolder && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-2 p-3 bg-deep-indigo/30 rounded-md border border-electric-cyan/20"
            >
              <Label htmlFor="new-folder" className="text-sm">New Folder Name</Label>
              <div className="flex space-x-2">
                <Input
                  id="new-folder"
                  value={newFolderName}
                  onChange={(e) => {
                    setNewFolderName(e.target.value);
                    setCreateError('');
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleCreateFolder();
                    }
                  }}
                  placeholder="my-new-project"
                  className="flex-1 bg-dark-bg/50 border-electric-cyan/20 text-sm"
                />
                <Button
                  variant="glow"
                  size="sm"
                  onClick={handleCreateFolder}
                >
                  Create
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setShowCreateFolder(false);
                    setNewFolderName('');
                    setCreateError('');
                  }}
                >
                  Cancel
                </Button>
              </div>
              {createError && (
                <p className="text-xs text-red-500">{createError}</p>
              )}
            </motion.div>
          )}

          {/* Quick Access */}
          {data?.quick_access && data.quick_access.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-muted-foreground">Quick Access</h4>
              <div className="flex flex-wrap gap-2">
                {data.quick_access.map((item) => (
                  <Button
                    key={item.path}
                    variant="outline"
                    size="sm"
                    onClick={() => navigateTo(item.path)}
                    className="border-electric-cyan/20 hover:border-electric-cyan/50"
                  >
                    <Home className="w-4 h-4 mr-2" />
                    {item.name}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Directory List */}
          <ScrollArea className="h-[300px] w-full rounded-md border border-electric-cyan/20 bg-deep-indigo/20 p-4">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-muted-foreground">Loading...</div>
              </div>
            ) : (
              <div className="space-y-1">
                {data?.directories.map((dir, index) => (
                  <motion.div
                    key={dir.path}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.02 }}
                  >
                    <button
                      className={`w-full flex items-center justify-between p-2 rounded-md hover:bg-electric-cyan/10 transition-colors ${
                        selectedPath === dir.path ? 'bg-electric-cyan/20' : ''
                      }`}
                      onDoubleClick={() => navigateTo(dir.path)}
                      onClick={() => setSelectedPath(dir.path)}
                    >
                      <div className="flex items-center space-x-2">
                        <Folder className="w-4 h-4 text-electric-cyan" />
                        <span className="text-sm">{dir.name}</span>
                      </div>
                      {dir.is_git_repo && (
                        <Badge variant="glow" className="text-xs">
                          <GitBranch className="w-3 h-3 mr-1" />
                          Git
                        </Badge>
                      )}
                    </button>
                  </motion.div>
                ))}
                {data?.directories.length === 0 && (
                  <div className="text-center text-muted-foreground py-8">
                    No subdirectories found
                  </div>
                )}
              </div>
            )}
          </ScrollArea>

          <div className="text-xs text-muted-foreground">
            <p>• Single click to select, double click to open folder</p>
            <p>• Look for folders with the Git badge</p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button 
            variant="glow" 
            onClick={handleSelect}
            disabled={!selectedPath}
          >
            <Check className="w-4 h-4 mr-2" />
            Select Folder
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}