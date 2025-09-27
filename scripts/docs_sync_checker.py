#!/usr/bin/env python3
"""
AL-0 Documentation Sync Checker
Ensures documentation stays in sync with configuration changes
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib

class DocsSyncChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_files = [
            'docker-compose.yml',
            'docker-compose.mvp.yml',
            'docker-compose.prod.yml',
            'monitoring/prometheus.yml',
            'monitoring/prometheus.mvp.yml',
            'monitoring/alert_rules.yml',
            'backend/app/core/config.py',
            'backend/app/core/config_mvp.py',
            'frontend/package.json',
            'frontend/package.mvp.json',
            'backend/requirements.txt',
            'backend/requirements.mvp.txt',
        ]
        
        self.doc_files = [
            'README.md',
            'API.md',
            'DEPLOYMENT.md',
            'PERFORMANCE_OPTIMIZATION.md',
            'OPERATIONAL_EXCELLENCE_PLAN.md',
            'MVP_IMPLEMENTATION_PLAN.md',
            'RISK_ASSESSMENT_AND_MITIGATION.md',
            'TECHNOLOGY_STACK.md',
            'PROJECT_RENAME_SUMMARY.md',
            'OPTIMIZATION_SUMMARY.md',
        ]
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'config_files': {},
            'doc_files': {},
            'sync_status': 'PASS',
            'out_of_sync': [],
            'missing_docs': [],
            'stale_docs': []
        }
    
    def check_docs_sync(self) -> Dict[str, Any]:
        """Check if documentation is in sync with configurations"""
        print("📚 Checking documentation sync...")
        
        # Check each config file
        for config_file in self.config_files:
            self.check_config_file(config_file)
        
        # Check each documentation file
        for doc_file in self.doc_files:
            self.check_doc_file(doc_file)
        
        # Check for missing documentation
        self.check_missing_docs()
        
        # Check for stale documentation
        self.check_stale_docs()
        
        # Determine overall sync status
        self.results['sync_status'] = self.determine_sync_status()
        
        # Print results
        self.print_results()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def check_config_file(self, config_file: str):
        """Check if a config file has corresponding documentation"""
        config_path = self.project_root / config_file
        
        if not config_path.exists():
            self.results['config_files'][config_file] = {
                'status': 'MISSING',
                'last_modified': None,
                'has_docs': False
            }
            return
        
        # Get file modification time
        last_modified = datetime.fromtimestamp(config_path.stat().st_mtime)
        
        # Check if there's corresponding documentation
        has_docs = self.has_corresponding_docs(config_file)
        
        # Check if docs are up to date
        docs_up_to_date = self.are_docs_up_to_date(config_file, last_modified)
        
        self.results['config_files'][config_file] = {
            'status': 'OK' if has_docs and docs_up_to_date else 'OUT_OF_SYNC',
            'last_modified': last_modified.isoformat(),
            'has_docs': has_docs,
            'docs_up_to_date': docs_up_to_date
        }
        
        if not has_docs or not docs_up_to_date:
            self.results['out_of_sync'].append(config_file)
    
    def check_doc_file(self, doc_file: str):
        """Check if a documentation file is up to date"""
        doc_path = self.project_root / doc_file
        
        if not doc_path.exists():
            self.results['doc_files'][doc_file] = {
                'status': 'MISSING',
                'last_modified': None,
                'references_configs': False
            }
            return
        
        # Get file modification time
        last_modified = datetime.fromtimestamp(doc_path.stat().st_mtime)
        
        # Check if doc references configs
        references_configs = self.doc_references_configs(doc_file)
        
        # Check if doc is stale (older than 7 days)
        is_stale = (datetime.now() - last_modified).days > 7
        
        self.results['doc_files'][doc_file] = {
            'status': 'STALE' if is_stale else 'OK',
            'last_modified': last_modified.isoformat(),
            'references_configs': references_configs,
            'is_stale': is_stale
        }
        
        if is_stale:
            self.results['stale_docs'].append(doc_file)
    
    def has_corresponding_docs(self, config_file: str) -> bool:
        """Check if a config file has corresponding documentation"""
        # Map config files to their documentation
        config_doc_map = {
            'docker-compose.yml': ['DEPLOYMENT.md', 'README.md'],
            'docker-compose.mvp.yml': ['MVP_IMPLEMENTATION_PLAN.md', 'DEPLOYMENT.md'],
            'docker-compose.prod.yml': ['DEPLOYMENT.md', 'OPERATIONAL_EXCELLENCE_PLAN.md'],
            'monitoring/prometheus.yml': ['OPERATIONAL_EXCELLENCE_PLAN.md', 'PERFORMANCE_OPTIMIZATION.md'],
            'monitoring/prometheus.mvp.yml': ['MVP_IMPLEMENTATION_PLAN.md'],
            'monitoring/alert_rules.yml': ['OPERATIONAL_EXCELLENCE_PLAN.md'],
            'backend/app/core/config.py': ['API.md', 'TECHNOLOGY_STACK.md'],
            'backend/app/core/config_mvp.py': ['MVP_IMPLEMENTATION_PLAN.md'],
            'frontend/package.json': ['TECHNOLOGY_STACK.md', 'README.md'],
            'frontend/package.mvp.json': ['MVP_IMPLEMENTATION_PLAN.md'],
            'backend/requirements.txt': ['TECHNOLOGY_STACK.md', 'README.md'],
            'backend/requirements.mvp.txt': ['MVP_IMPLEMENTATION_PLAN.md'],
        }
        
        expected_docs = config_doc_map.get(config_file, [])
        
        # Check if any of the expected docs exist and reference this config
        for doc in expected_docs:
            doc_path = self.project_root / doc
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if config_file in content or self.get_config_name(config_file) in content:
                        return True
        
        return False
    
    def are_docs_up_to_date(self, config_file: str, config_modified: datetime) -> bool:
        """Check if documentation is up to date with config file"""
        config_doc_map = {
            'docker-compose.yml': ['DEPLOYMENT.md', 'README.md'],
            'docker-compose.mvp.yml': ['MVP_IMPLEMENTATION_PLAN.md', 'DEPLOYMENT.md'],
            'docker-compose.prod.yml': ['DEPLOYMENT.md', 'OPERATIONAL_EXCELLENCE_PLAN.md'],
            'monitoring/prometheus.yml': ['OPERATIONAL_EXCELLENCE_PLAN.md', 'PERFORMANCE_OPTIMIZATION.md'],
            'monitoring/prometheus.mvp.yml': ['MVP_IMPLEMENTATION_PLAN.md'],
            'monitoring/alert_rules.yml': ['OPERATIONAL_EXCELLENCE_PLAN.md'],
            'backend/app/core/config.py': ['API.md', 'TECHNOLOGY_STACK.md'],
            'backend/app/core/config_mvp.py': ['MVP_IMPLEMENTATION_PLAN.md'],
            'frontend/package.json': ['TECHNOLOGY_STACK.md', 'README.md'],
            'frontend/package.mvp.json': ['MVP_IMPLEMENTATION_PLAN.md'],
            'backend/requirements.txt': ['TECHNOLOGY_STACK.md', 'README.md'],
            'backend/requirements.mvp.txt': ['MVP_IMPLEMENTATION_PLAN.md'],
        }
        
        expected_docs = config_doc_map.get(config_file, [])
        
        # Check if any of the expected docs are newer than the config
        for doc in expected_docs:
            doc_path = self.project_root / doc
            if doc_path.exists():
                doc_modified = datetime.fromtimestamp(doc_path.stat().st_mtime)
                if doc_modified >= config_modified:
                    return True
        
        return False
    
    def doc_references_configs(self, doc_file: str) -> bool:
        """Check if a documentation file references configuration files"""
        doc_path = self.project_root / doc_file
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for references to config files
            for config_file in self.config_files:
                if config_file in content or self.get_config_name(config_file) in content:
                    return True
        
        return False
    
    def get_config_name(self, config_file: str) -> str:
        """Get a human-readable name for a config file"""
        name_map = {
            'docker-compose.yml': 'Docker Compose',
            'docker-compose.mvp.yml': 'Docker Compose MVP',
            'docker-compose.prod.yml': 'Docker Compose Production',
            'monitoring/prometheus.yml': 'Prometheus Configuration',
            'monitoring/prometheus.mvp.yml': 'Prometheus MVP Configuration',
            'monitoring/alert_rules.yml': 'Alert Rules',
            'backend/app/core/config.py': 'Backend Configuration',
            'backend/app/core/config_mvp.py': 'Backend MVP Configuration',
            'frontend/package.json': 'Frontend Dependencies',
            'frontend/package.mvp.json': 'Frontend MVP Dependencies',
            'backend/requirements.txt': 'Backend Dependencies',
            'backend/requirements.mvp.txt': 'Backend MVP Dependencies',
        }
        return name_map.get(config_file, config_file)
    
    def check_missing_docs(self):
        """Check for missing documentation files"""
        for doc_file in self.doc_files:
            doc_path = self.project_root / doc_file
            if not doc_path.exists():
                self.results['missing_docs'].append(doc_file)
    
    def check_stale_docs(self):
        """Check for stale documentation files"""
        for doc_file in self.doc_files:
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                last_modified = datetime.fromtimestamp(doc_path.stat().st_mtime)
                if (datetime.now() - last_modified).days > 7:
                    self.results['stale_docs'].append(doc_file)
    
    def determine_sync_status(self) -> str:
        """Determine overall documentation sync status"""
        if (self.results['out_of_sync'] or 
            self.results['missing_docs'] or 
            self.results['stale_docs']):
            return 'FAIL'
        return 'PASS'
    
    def print_results(self):
        """Print documentation sync results"""
        print(f"\n📚 Documentation Sync Check Results")
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Overall Status: {self.results['sync_status']}")
        
        if self.results['out_of_sync']:
            print(f"\n⚠️  Out of Sync Config Files:")
            for config_file in self.results['out_of_sync']:
                print(f"  - {config_file}")
        
        if self.results['missing_docs']:
            print(f"\n❌ Missing Documentation Files:")
            for doc_file in self.results['missing_docs']:
                print(f"  - {doc_file}")
        
        if self.results['stale_docs']:
            print(f"\n🕐 Stale Documentation Files:")
            for doc_file in self.results['stale_docs']:
                print(f"  - {doc_file}")
        
        print(f"\n📊 Config Files Status:")
        for config_file, data in self.results['config_files'].items():
            status_icon = "✅" if data['status'] == 'OK' else "❌"
            print(f"  {status_icon} {config_file}: {data['status']}")
        
        print(f"\n📊 Documentation Files Status:")
        for doc_file, data in self.results['doc_files'].items():
            status_icon = "✅" if data['status'] == 'OK' else "❌"
            print(f"  {status_icon} {doc_file}: {data['status']}")
        
        if self.results['sync_status'] == 'PASS':
            print(f"\n🎉 Documentation is in sync!")
        else:
            print(f"\n❌ Documentation sync issues found! Update documentation.")
    
    def save_results(self):
        """Save results to file"""
        results_dir = self.project_root / 'monitoring' / 'docs_sync'
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'docs_sync_check_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Also save latest results
        latest_file = results_dir / 'latest_docs_sync.json'
        with open(latest_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")

def main():
    """Main function"""
    checker = DocsSyncChecker()
    result = checker.check_docs_sync()
    
    # Exit with error code if sync check failed
    if result['sync_status'] == 'FAIL':
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
    main()
