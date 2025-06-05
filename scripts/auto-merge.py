#!/usr/bin/env python3
"""
Auto-merge Git worktrees for SplitMind

This script provides safe, automated merging of worktree branches back to main.
Designed to work standalone or be called by Claude orchestrator.
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


class WorktreeMerger:
    def __init__(self, branch=None, strategy='merge', dry_run=False):
        self.branch = branch
        self.strategy = strategy
        self.dry_run = dry_run
        self.original_branch = self.get_current_branch()
    
    def run_command(self, cmd, capture=True):
        """Run a shell command and return output"""
        if self.dry_run and any(word in cmd for word in ['merge', 'push', 'delete']):
            print(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return ""
        
        try:
            result = subprocess.run(cmd, capture_output=capture, text=True, check=True)
            return result.stdout.strip() if capture else None
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            sys.exit(1)
    
    def get_current_branch(self):
        """Get the current branch name"""
        return self.run_command(['git', 'branch', '--show-current'])
    
    def get_worktree_branches(self):
        """Get all worktree branches"""
        worktrees = self.run_command(['git', 'worktree', 'list', '--porcelain'])
        branches = []
        
        for line in worktrees.split('\n'):
            if line.startswith('branch'):
                branch = line.split()[1].replace('refs/heads/', '')
                if branch != 'main' and branch != self.original_branch:
                    branches.append(branch)
        
        return branches
    
    def check_branch_status(self, branch):
        """Check if branch has unpushed commits or uncommitted changes"""
        # Switch to branch
        self.run_command(['git', 'checkout', branch])
        
        # Check for uncommitted changes
        status = self.run_command(['git', 'status', '--porcelain'])
        if status:
            return {'clean': False, 'reason': 'uncommitted changes'}
        
        # Check if branch is ahead of origin
        ahead = self.run_command(['git', 'rev-list', '--count', f'origin/{branch}..{branch}'])
        if ahead and ahead != '0':
            return {'clean': False, 'reason': f'{ahead} unpushed commits'}
        
        # Check if branch is behind main
        self.run_command(['git', 'fetch', 'origin', 'main'])
        behind = self.run_command(['git', 'rev-list', '--count', f'{branch}..origin/main'])
        
        return {
            'clean': True,
            'behind': int(behind) if behind else 0,
            'commits': self.get_branch_commits(branch)
        }
    
    def get_branch_commits(self, branch):
        """Get commits that will be merged"""
        commits = self.run_command([
            'git', 'log', '--oneline', 
            f'origin/main..{branch}', 
            '--format=%h %s'
        ])
        return commits.split('\n') if commits else []
    
    def merge_branch(self, branch):
        """Merge a branch into main"""
        print(f"\n{'='*60}")
        print(f"Processing branch: {branch}")
        print(f"{'='*60}")
        
        # Check branch status
        status = self.check_branch_status(branch)
        
        if not status['clean']:
            print(f"❌ Cannot merge: {status['reason']}")
            return False
        
        if not status['commits']:
            print(f"ℹ️  No new commits to merge")
            return True
        
        print(f"\n📋 Commits to merge:")
        for commit in status['commits']:
            print(f"  - {commit}")
        
        # Switch to main
        self.run_command(['git', 'checkout', 'main'])
        self.run_command(['git', 'pull', 'origin', 'main'])
        
        # Perform merge based on strategy
        print(f"\n🔄 Merging with strategy: {self.strategy}")
        
        if self.strategy == 'squash':
            self.run_command(['git', 'merge', '--squash', branch])
            commit_msg = f"Merge branch '{branch}' (squashed)\n\nSquashed commits:\n"
            commit_msg += '\n'.join(f"- {c}" for c in status['commits'])
            self.run_command(['git', 'commit', '-m', commit_msg])
        
        elif self.strategy == 'ff':
            try:
                self.run_command(['git', 'merge', '--ff-only', branch])
            except:
                print("❌ Cannot fast-forward, falling back to regular merge")
                self.run_command(['git', 'merge', '--no-ff', branch, '-m', 
                                f"Merge branch '{branch}'"])
        
        else:  # default merge
            self.run_command(['git', 'merge', '--no-ff', branch, '-m', 
                            f"Merge branch '{branch}'"])
        
        # Push to origin
        print(f"\n📤 Pushing to origin/main")
        self.run_command(['git', 'push', 'origin', 'main'])
        
        # Delete remote branch
        print(f"\n🗑️  Deleting remote branch")
        self.run_command(['git', 'push', 'origin', '--delete', branch])
        
        # Remove worktree
        worktree_path = Path('worktrees') / branch
        if worktree_path.exists():
            print(f"\n🧹 Removing worktree")
            self.run_command(['git', 'worktree', 'remove', str(worktree_path)])
        
        # Delete local branch
        self.run_command(['git', 'branch', '-d', branch])
        
        print(f"\n✅ Successfully merged and cleaned up: {branch}")
        return True
    
    def merge_all(self):
        """Merge all eligible worktree branches"""
        branches = self.get_worktree_branches()
        
        if not branches:
            print("No worktree branches found")
            return
        
        print(f"Found {len(branches)} worktree branches: {', '.join(branches)}")
        
        results = {
            'merged': [],
            'failed': []
        }
        
        for branch in branches:
            try:
                if self.merge_branch(branch):
                    results['merged'].append(branch)
                else:
                    results['failed'].append(branch)
            except Exception as e:
                print(f"Error merging {branch}: {e}")
                results['failed'].append(branch)
        
        # Return to original branch
        self.run_command(['git', 'checkout', self.original_branch])
        
        # Print summary
        print(f"\n{'='*60}")
        print("MERGE SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Merged: {len(results['merged'])} branches")
        if results['merged']:
            for branch in results['merged']:
                print(f"   - {branch}")
        
        if results['failed']:
            print(f"\n❌ Failed: {len(results['failed'])} branches")
            for branch in results['failed']:
                print(f"   - {branch}")
        
        # Output JSON for Claude
        if '--json' in sys.argv:
            print(f"\n{json.dumps(results, indent=2)}")
        
        return results


def main():
    parser = argparse.ArgumentParser(description='Auto-merge Git worktrees')
    parser.add_argument('branch', nargs='?', help='Specific branch to merge')
    parser.add_argument('--all', action='store_true', help='Merge all worktree branches')
    parser.add_argument('--strategy', choices=['merge', 'squash', 'ff'], 
                       default='merge', help='Merge strategy (default: merge)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    merger = WorktreeMerger(
        branch=args.branch,
        strategy=args.strategy,
        dry_run=args.dry_run
    )
    
    if args.all:
        merger.merge_all()
    elif args.branch:
        merger.merge_branch(args.branch)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()