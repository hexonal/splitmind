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

When creating tasks, format each one exactly as:
- **Task Title** - Brief description of what needs to be done

Make sure tasks are specific, self-contained, and suitable for AI agents to implement independently."""
        
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
   
2. Generate 10-15 specific, actionable tasks formatted as:
   - **Task Title** - Brief description

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
        """Parse Claude's response to extract plan and tasks"""
        lines = content.split('\n')
        
        # Extract tasks
        tasks = []
        for line in lines:
            line = line.strip()
            if line.startswith('- **') and '**' in line[4:]:
                # Pattern: - **Title** - Description
                parts = line.split('**')
                if len(parts) >= 3:
                    title = parts[1].strip()
                    desc_part = parts[2].strip()
                    if desc_part.startswith('-'):
                        desc_part = desc_part[1:].strip()
                    tasks.append({
                        "title": title,
                        "description": desc_part
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
                                    "description": parts[1].strip() if len(parts) > 1 else ""
                                })
                                break
                        else:
                            # No delimiter found, use the whole line as title
                            tasks.append({
                                "title": task_text[:100],  # Limit length
                                "description": "Implement this feature according to project requirements"
                            })
        
        return {
            "success": True,
            "plan": content,
            "suggested_tasks": tasks[:15],  # Limit to 15 tasks
            "error": None
        }
    
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