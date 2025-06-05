import { Project, Task, Agent, ProjectStats, OrchestratorConfig } from '@/types';

const API_BASE = '/api';

class ApiService {
  private async request<T>(url: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    const text = await response.text();
    try {
      return JSON.parse(text);
    } catch (e) {
      console.error('Failed to parse response:', text);
      throw new Error('Invalid JSON response from server');
    }
  }

  // Projects
  getProjects = async (): Promise<Project[]> => {
    console.log('Fetching projects from API...');
    const projects = await this.request<Project[]>('/projects');
    console.log('Projects received:', projects);
    return projects;
  }

  getProject = async (id: string): Promise<Project> => {
    return this.request(`/projects/${id}`);
  }

  createProject = async (project: Partial<Project>): Promise<Project> => {
    console.log('Creating project:', project);
    return this.request('/projects', {
      method: 'POST',
      body: JSON.stringify(project),
    });
  }

  updateProject = async (id: string, updates: Partial<Project>): Promise<Project> => {
    return this.request(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  deleteProject = async (id: string): Promise<void> => {
    await this.request(`/projects/${id}`, { method: 'DELETE' });
  }

  getProjectStats = async (id: string): Promise<ProjectStats> => {
    return this.request(`/projects/${id}/stats`);
  }

  // Tasks
  getTasks = async (projectId: string): Promise<Task[]> => {
    return this.request(`/projects/${projectId}/tasks`);
  }

  createTask = async (projectId: string, title: string, description?: string): Promise<Task> => {
    const params = new URLSearchParams({ title });
    if (description) params.append('description', description);
    
    return this.request(`/projects/${projectId}/tasks?${params}`, {
      method: 'POST',
    });
  }

  updateTask = async (projectId: string, taskId: string, updates: Partial<Task>): Promise<Task> => {
    return this.request(`/projects/${projectId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  deleteTask = async (projectId: string, taskId: string): Promise<void> => {
    await this.request(`/projects/${projectId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  // Agents
  getAgents = async (projectId: string): Promise<Agent[]> => {
    return this.request(`/projects/${projectId}/agents`);
  }

  launchITerm = async (projectId: string, agentId: string): Promise<void> => {
    await this.request(`/projects/${projectId}/agents/${agentId}/launch-iterm`, {
      method: 'POST',
    });
  }

  // Orchestrator
  getOrchestratorConfig = async (): Promise<OrchestratorConfig> => {
    return this.request('/orchestrator/config');
  }

  updateOrchestratorConfig = async (config: OrchestratorConfig): Promise<OrchestratorConfig> => {
    return this.request('/orchestrator/config', {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  startOrchestrator = async (projectId: string): Promise<void> => {
    await this.request(`/orchestrator/start?project_id=${projectId}`, {
      method: 'POST',
    });
  }

  stopOrchestrator = async (): Promise<void> => {
    await this.request('/orchestrator/stop', {
      method: 'POST',
    });
  }

  getOrchestratorStatus = async (): Promise<{ running: boolean; current_project?: string }> => {
    return this.request('/orchestrator/status');
  }

  // Plan Generation
  generatePlan = async (projectId: string, data: {
    project_overview: string;
    initial_prompt: string;
    dart_workspace?: string;
    dart_dartboard?: string;
  }): Promise<{ plan: string; tasks_created: number; message: string; cost_info?: any; usage?: any }> => {
    return this.request(`/projects/${projectId}/generate-plan`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const api = new ApiService();