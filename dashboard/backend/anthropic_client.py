"""
Anthropic API Client for SplitMind

This module handles direct API calls to Anthropic for plan generation.
"""
import os
import json
import httpx
from typing import Dict, List, Optional
from pathlib import Path


class AnthropicClient:
    """Client for Anthropic API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1"
        self.default_model = "claude-sonnet-4-20250514"  # Default model
        
        # Pricing per million tokens (as of Jan 2025)
        self.pricing = {
            "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
            "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
            "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
            "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25}
        }
        
    def generate_plan(self, project_info: Dict, model: Optional[str] = None) -> Dict:
        """
        Generate a project plan using Anthropic API
        
        Args:
            project_info: Dictionary containing:
                - project_name: Name of the project
                - project_overview: Detailed project description
                - initial_prompt: User's initial request
                
        Returns:
            Dictionary containing:
                - plan: Generated project plan
                - suggested_tasks: List of tasks with titles and descriptions
                - success: Boolean indicating if the request was successful
                - error: Error message if request failed
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "No Anthropic API key configured. Please add it in Settings.",
                "plan": "",
                "suggested_tasks": []
            }
        
        # Prepare the prompt
        system_prompt = """You are a project planning expert. You analyze project requirements and create comprehensive development plans with actionable tasks.

When creating tasks, you MUST format each one exactly as follows:
- **Task Title** - Brief description | Dependencies: [dep1, dep2] | Priority: X

Where:
- Dependencies are the titles of other tasks that must be completed first (use exact task titles, or "none" if no dependencies)
- Priority is a number from 1-10 where 1 is highest priority, 10 is lowest
- Tasks should follow a logical development order (e.g., setup before implementation, implementation before testing)

Example format:
- **Set up project structure** - Initialize Git repo and create basic folders | Dependencies: [none] | Priority: 1
- **Create database schema** - Design and implement database models | Dependencies: [Set up project structure] | Priority: 2
- **Implement API endpoints** - Create REST API for CRUD operations | Dependencies: [Create database schema] | Priority: 3
- **Write unit tests** - Add comprehensive test coverage | Dependencies: [Implement API endpoints] | Priority: 4

Make sure tasks are specific, have clear dependencies, and follow a logical implementation order."""
        
        user_prompt = f"""Please create a comprehensive project plan for the following project:

Project Name: {project_info.get('project_name', 'Unknown')}

Project Overview:
{project_info.get('project_overview', 'No overview provided')}

Initial Requirements/Prompt:
{project_info.get('initial_prompt', 'No initial prompt provided')}

Please provide:
1. A detailed project plan with:
   - Architecture decisions
   - Technology stack recommendations
   - Development phases with timelines
   - Risk factors and mitigation strategies
   
2. Generate 10-15 specific, actionable tasks with dependencies and priorities:
   - Use the EXACT format: **Task Title** - Brief description | Dependencies: [dep1, dep2] | Priority: X
   - List dependencies by exact task titles or use [none]
   - Assign priorities 1-10 (1=highest, 10=lowest) based on logical order
   - Ensure tasks follow natural development flow (setup → implementation → testing → deployment)

Make the tasks concrete and implementable by AI coding agents."""
        
        try:
            # Make API request
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": model or self.default_model,
                "max_tokens": 4096,
                "temperature": 0.7,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }
            
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    return {
                        "success": False,
                        "error": f"API Error: {error_data.get('error', {}).get('message', 'Unknown error')}",
                        "plan": "",
                        "suggested_tasks": []
                    }
                
                result = response.json()
                content = result.get('content', [{}])[0].get('text', '')
                
                # Calculate cost
                usage = result.get('usage', {})
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)
                
                model_used = model or self.default_model
                cost_info = self._calculate_cost(model_used, input_tokens, output_tokens)
                
                # Parse the response
                parsed = self._parse_response(content)
                parsed['cost_info'] = cost_info
                parsed['usage'] = usage
                
                return parsed
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timed out. Please try again.",
                "plan": "",
                "suggested_tasks": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calling Anthropic API: {str(e)}",
                "plan": "",
                "suggested_tasks": []
            }
    
    def _parse_response(self, content: str) -> Dict:
        """Parse Claude's response to extract plan and tasks with dependencies"""
        lines = content.split('\n')
        
        # Extract tasks
        tasks = []
        for line in lines:
            line = line.strip()
            if line.startswith('- **') and '**' in line[4:]:
                # Pattern: - **Title** - Description | Dependencies: [dep1, dep2] | Priority: X
                parts = line.split('**')
                if len(parts) >= 3:
                    title = parts[1].strip()
                    remaining = parts[2].strip()
                    
                    # Remove leading dash if present
                    if remaining.startswith('-'):
                        remaining = remaining[1:].strip()
                    
                    # Split by pipe to extract description, dependencies, and priority
                    sections = remaining.split('|')
                    description = sections[0].strip() if sections else ""
                    
                    # Default values
                    dependencies = []
                    priority = 5  # Default middle priority
                    
                    # Parse dependencies and priority from remaining sections
                    for section in sections[1:]:
                        section = section.strip()
                        if section.startswith('Dependencies:'):
                            dep_text = section.replace('Dependencies:', '').strip()
                            # Parse dependency list
                            if dep_text.startswith('[') and dep_text.endswith(']'):
                                dep_text = dep_text[1:-1]  # Remove brackets
                                if dep_text.lower() != 'none':
                                    dependencies = [d.strip() for d in dep_text.split(',') if d.strip()]
                        elif section.startswith('Priority:'):
                            try:
                                priority = int(section.replace('Priority:', '').strip())
                            except ValueError:
                                priority = 5
                    
                    tasks.append({
                        "title": title,
                        "description": description,
                        "dependencies": dependencies,
                        "priority": priority
                    })
        
        # If no tasks found in the expected format, try to extract them
        if not tasks:
            in_task_section = False
            for line in lines:
                if 'task' in line.lower() and (':' in line or '-' in line):
                    in_task_section = True
                if in_task_section and line.startswith('-'):
                    task_text = line[1:].strip()
                    if task_text:
                        # Try to split on common delimiters
                        for delimiter in [' - ', ': ', ' — ']:
                            if delimiter in task_text:
                                parts = task_text.split(delimiter, 1)
                                tasks.append({
                                    "title": parts[0].strip(),
                                    "description": parts[1].strip() if len(parts) > 1 else "",
                                    "dependencies": [],
                                    "priority": 5
                                })
                                break
                        else:
                            # No delimiter found, use the whole line as title
                            tasks.append({
                                "title": task_text[:100],  # Limit length
                                "description": "Implement this feature according to project requirements",
                                "dependencies": [],
                                "priority": 5
                            })
        
        return {
            "success": True,
            "plan": content,
            "suggested_tasks": tasks[:15],  # Limit to 15 tasks
            "error": None
        }
    
    def generate_task_breakdown(self, project_info: Dict, model: Optional[str] = None) -> Dict:
        """
        Generate a structured task breakdown using Task Master AI approach
        
        Args:
            project_info: Dictionary containing project details
            model: Model to use (optional)
            
        Returns:
            Dictionary containing plan, task breakdown, and suggested tasks
        """
        print(f"🤖 Starting task breakdown generation for project: {project_info.get('project_name', 'Unknown')}")
        
        if not self.api_key:
            return {
                "success": False,
                "error": "No Anthropic API key configured. Please add it in Settings.",
                "plan": "",
                "task_breakdown": "",
                "suggested_tasks": []
            }
        
        # Optimized Task Master AI System Prompt (reduced tokens)
        system_prompt = """You are a Task Master AI that creates wave-based task breakdowns for AI coding agents.

Rules:
1. Each task: self-contained, 1-4 hours work, executable by single agent
2. Group tasks into waves by dependencies (max 5 agents per wave)
3. Earlier waves: setup/structure. Later waves: features/polish

Task Format:
Wave X: [Name] (Y agents)
Agent N - [Role]
Task: [Title]
[Description with technical specs, files, libraries, configs]
Output: [Deliverables]

Generate a PROJECT PLAN followed by WAVE-BASED TASK BREAKDOWN."""

        user_prompt = f"""Project: {project_info.get('project_name', 'Unknown')}

Overview: {project_info.get('project_overview', 'No overview provided')[:500]}

Requirements: {project_info.get('initial_prompt', 'No initial prompt provided')[:500]}

Create:
1. PROJECT PLAN (architecture, tech stack, phases)
2. WAVE-BASED TASKS (3-5 agents per wave, specific technical details)"""

        try:
            model_to_use = model or self.default_model
            print(f"📡 Using model: {model_to_use}")
            
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01", 
                "content-type": "application/json"
            }
            
            data = {
                "model": model_to_use,
                "max_tokens": 4096,  # Reduced to prevent timeout
                "temperature": 0.5,   # Lower for more structured output
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }
            
            print(f"📤 Sending request to Anthropic API...")
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=data,
                    timeout=120.0  # Increased timeout to 2 minutes
                )
                
                print(f"📥 Response received with status: {response.status_code}")
                
                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    print(f"❌ API Error: {error_msg}")
                    return {
                        "success": False,
                        "error": f"API Error: {error_msg}",
                        "plan": "",
                        "task_breakdown": "",
                        "suggested_tasks": []
                    }
                
                result = response.json()
                content = result.get('content', [{}])[0].get('text', '')
                
                # Calculate cost
                usage = result.get('usage', {})
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)
                
                print(f"✅ Response received: {input_tokens} input tokens, {output_tokens} output tokens")
                
                model_used = model_to_use
                cost_info = self._calculate_cost(model_used, input_tokens, output_tokens)
                
                # Parse the response for both plan and task breakdown
                parsed = self._parse_task_breakdown_response(content)
                parsed['cost_info'] = cost_info
                parsed['usage'] = usage
                
                return parsed
                
        except httpx.TimeoutException:
            print(f"⏱️ Request timed out after 120 seconds")
            return {
                "success": False,
                "error": "Request timed out. Try using a faster model (claude-3-5-haiku) or simplifying your project description.",
                "plan": "",
                "task_breakdown": "",
                "suggested_tasks": []
            }
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Error calling Anthropic API: {str(e)}",
                "plan": "",
                "task_breakdown": "",
                "suggested_tasks": []
            }

    def _parse_task_breakdown_response(self, content: str) -> Dict:
        """Parse the task breakdown response to extract plan, breakdown, and tasks"""
        
        # Split content into plan and task breakdown sections
        sections = content.split('\n')
        
        # Find the task breakdown section
        task_breakdown_start = -1
        for i, line in enumerate(sections):
            if any(keyword in line.lower() for keyword in ['ai-executable', 'task breakdown', 'wave 1:', 'agent 1']):
                task_breakdown_start = i
                break
        
        if task_breakdown_start > 0:
            plan = '\n'.join(sections[:task_breakdown_start]).strip()
            task_breakdown = '\n'.join(sections[task_breakdown_start:]).strip()
        else:
            plan = content
            task_breakdown = ""
        
        # Extract individual tasks for backward compatibility
        tasks = self._extract_tasks_from_breakdown(content)
        
        return {
            "success": True,
            "plan": plan,
            "task_breakdown": task_breakdown,
            "suggested_tasks": tasks,
            "error": None
        }
    
    def _extract_tasks_from_breakdown(self, content: str) -> List[Dict]:
        """Extract individual tasks from the wave-based breakdown"""
        tasks = []
        lines = content.split('\n')
        
        current_wave = 1
        current_agent = 1
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for task definitions
            if line.startswith('Task:'):
                title = line.replace('Task:', '').strip()
                
                # Collect description until we hit Output: or next Task:
                description_lines = []
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith('Output:') or next_line.startswith('Task:') or next_line.startswith('Agent') or next_line.startswith('Wave'):
                        break
                    if next_line:  # Skip empty lines
                        description_lines.append(next_line)
                    i += 1
                
                description = ' '.join(description_lines).strip()
                
                # Basic priority assignment based on wave
                priority = current_wave
                
                tasks.append({
                    "title": title,
                    "description": description,
                    "dependencies": [],  # Dependencies will be implicit in wave structure
                    "priority": min(priority, 10),  # Cap at 10
                    "wave": current_wave,
                    "agent": current_agent
                })
                
                continue
            
            # Track waves and agents for context
            if line.startswith('Wave'):
                try:
                    current_wave = int(line.split(':')[0].replace('Wave', '').strip())
                except:
                    current_wave += 1
                current_agent = 1
            elif line.startswith('Agent'):
                try:
                    current_agent = int(line.split('-')[0].replace('Agent', '').strip())
                except:
                    current_agent += 1
            
            i += 1
        
        return tasks[:20]  # Limit to 20 tasks

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Dict:
        """Calculate the cost of the API call"""
        pricing = self.pricing.get(model, self.pricing[self.default_model])
        
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        total_cost = input_cost + output_cost
        
        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": f"${input_cost:.6f}",
            "output_cost": f"${output_cost:.6f}",
            "total_cost": f"${total_cost:.6f}",
            "pricing_per_million": pricing
        }


# Global instance
anthropic_client = AnthropicClient()