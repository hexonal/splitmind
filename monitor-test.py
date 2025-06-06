#!/usr/bin/env python3
"""
Monitor test project execution for SplitMind coordination testing
"""
import time
import subprocess
import json
from datetime import datetime
from pathlib import Path
import sys

class TestMonitor:
    def __init__(self, project_id="hello-splitmind"):
        self.project_id = project_id
        self.start_time = datetime.now()
        self.events = []
        self.api_base = "http://localhost:8000/api"
        
    def log_event(self, event_type, data):
        timestamp = (datetime.now() - self.start_time).total_seconds()
        self.events.append({
            "time": timestamp,
            "type": event_type,
            "data": data
        })
        
        # Color codes for different event types
        colors = {
            "SPAWN": "\033[92m",    # Green
            "COMPLETE": "\033[94m",  # Blue
            "MERGE": "\033[95m",     # Purple
            "CONFLICT": "\033[91m",  # Red
            "STATS": "\033[93m",     # Yellow
            "AGENTS": "\033[96m",    # Cyan
        }
        color = colors.get(event_type.split("_")[0], "\033[0m")
        reset = "\033[0m"
        
        print(f"[{timestamp:6.1f}s] {color}{event_type:15}{reset} {data}")
    
    def api_call(self, endpoint):
        """Make API call and return JSON response"""
        try:
            result = subprocess.run([
                "curl", "-s", 
                f"{self.api_base}{endpoint}"
            ], capture_output=True, text=True)
            return json.loads(result.stdout)
        except:
            return None
    
    def check_status(self):
        """Get project statistics"""
        return self.api_call(f"/projects/{self.project_id}/stats")
    
    def check_tasks(self):
        """Get task list"""
        return self.api_call(f"/projects/{self.project_id}/tasks")
    
    def check_agents(self):
        """Get running agents"""
        return self.api_call(f"/projects/{self.project_id}/agents")
    
    def check_conflicts(self):
        """Check for merge conflicts in git"""
        project_path = f"/Users/jasonbrashear/code/{self.project_id}"
        result = subprocess.run(
            ["git", "-C", project_path, "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        conflicts = [line for line in result.stdout.split('\n') if line.startswith('UU ')]
        return conflicts
    
    def monitor(self):
        print(f"🔍 Starting test monitor for project: {self.project_id}")
        print("=" * 80)
        print("Time    Event            Details")
        print("=" * 80)
        
        last_stats = None
        last_agents = []
        task_start_times = {}
        
        while True:
            try:
                # Check current status
                stats = self.check_status()
                tasks = self.check_tasks()
                agents = self.check_agents()
                conflicts = self.check_conflicts()
                
                if not stats:
                    print("⚠️  Unable to connect to API. Is the server running?")
                    time.sleep(5)
                    continue
                
                # Track task state changes
                if tasks:
                    for task in tasks:
                        task_id = task['id']
                        status = task['status']
                        
                        # Track when tasks start
                        if status in ['claimed', 'in_progress'] and task_id not in task_start_times:
                            task_start_times[task_id] = datetime.now()
                            self.log_event("SPAWN", f"{task['title']} -> {status}")
                        
                        # Track when tasks complete
                        elif status == 'completed' and task_id in task_start_times:
                            duration = (datetime.now() - task_start_times[task_id]).total_seconds()
                            self.log_event("COMPLETE", f"{task['title']} (took {duration:.1f}s)")
                        
                        # Track merges
                        elif status == 'merged':
                            self.log_event("MERGE", f"{task['title']} merged successfully")
                
                # Log stats changes
                if last_stats != stats:
                    self.log_event("STATS", {
                        "unclaimed": stats.get("unclaimed_tasks", 0),
                        "active": stats.get("claimed_tasks", 0) + stats.get("in_progress_tasks", 0),
                        "completed": stats.get("completed_tasks", 0),
                        "merged": stats.get("merged_tasks", 0),
                    })
                    last_stats = stats
                
                # Log agent changes
                current_agent_ids = [a['id'] for a in agents] if agents else []
                if current_agent_ids != last_agents:
                    if agents:
                        agent_info = [f"{a['task_title']}" for a in agents]
                        self.log_event("AGENTS", f"Running: {', '.join(agent_info)}")
                    last_agents = current_agent_ids
                
                # Check for conflicts
                if conflicts:
                    self.log_event("CONFLICT", f"Merge conflicts: {', '.join(conflicts)}")
                
                # Check for completion
                if stats and stats.get("total_tasks", 0) > 0:
                    if stats.get("merged_tasks", 0) == stats["total_tasks"]:
                        self.log_event("TEST_COMPLETE", {
                            "total_time": (datetime.now() - self.start_time).total_seconds(),
                            "total_tasks": stats["total_tasks"]
                        })
                        break
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                time.sleep(5)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        print("\n" + "=" * 80)
        print("📊 TEST REPORT")
        print("=" * 80)
        
        if not self.events:
            print("No events recorded")
            return
        
        # Calculate metrics
        total_time = self.events[-1]["time"]
        spawn_events = [e for e in self.events if e["type"] == "SPAWN"]
        complete_events = [e for e in self.events if e["type"] == "COMPLETE"]
        merge_events = [e for e in self.events if e["type"] == "MERGE"]
        conflict_events = [e for e in self.events if e["type"] == "CONFLICT"]
        
        # Find max concurrent agents
        stats_events = [e for e in self.events if e["type"] == "STATS"]
        max_concurrent = max((e["data"].get("active", 0) for e in stats_events), default=0)
        
        print(f"⏱️  Total Time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        print(f"📦 Total Tasks: {len(spawn_events)}")
        print(f"✅ Completed: {len(complete_events)}")
        print(f"🔀 Merged: {len(merge_events)}")
        print(f"⚡ Max Concurrent Agents: {max_concurrent}")
        print(f"⚠️  Conflicts: {len(conflict_events)}")
        
        # Task timing analysis
        if complete_events:
            print("\n📈 Task Completion Times:")
            for event in complete_events:
                print(f"   {event['data']}")
        
        # Save detailed log
        report_file = f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump({
                "project_id": self.project_id,
                "start_time": self.start_time.isoformat(),
                "total_time": total_time,
                "max_concurrent": max_concurrent,
                "total_tasks": len(spawn_events),
                "completed_tasks": len(complete_events),
                "merged_tasks": len(merge_events),
                "conflicts": len(conflict_events),
                "events": self.events
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        # Success/Failure determination
        if len(merge_events) == len(spawn_events) and len(conflict_events) == 0:
            print("\n✅ TEST PASSED: All tasks completed and merged without conflicts!")
        else:
            print("\n❌ TEST FAILED: Some tasks did not complete or had conflicts")

if __name__ == "__main__":
    project_id = sys.argv[1] if len(sys.argv) > 1 else "hello-splitmind"
    monitor = TestMonitor(project_id)
    monitor.monitor()