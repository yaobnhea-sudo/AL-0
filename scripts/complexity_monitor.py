#!/usr/bin/env python3
"""
AL-0 Complexity Monitor
Prevents complexity creep during phased development
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ComplexityMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.complexity_thresholds = {
            'dependencies': 25,  # Max dependencies
            'services': 8,       # Max Docker services
            'config_files': 10,  # Max config files
            'documentation_files': 20,  # Max doc files
            'api_endpoints': 50,  # Max API endpoints
            'python_files': 100,  # Max Python files
            'typescript_files': 50,  # Max TypeScript files
            'docker_layers': 20,  # Max Docker layers
        }
        
        self.complexity_scores = {
            'low': 0,
            'medium': 1,
            'high': 2,
            'critical': 3
        }
    
    def check_complexity(self) -> Dict[str, Any]:
        """Check if complexity is within acceptable limits"""
        print("🔍 Checking project complexity...")
        
        current = self.measure_complexity()
        violations = []
        warnings = []
        
        for metric, threshold in self.complexity_thresholds.items():
            current_value = current.get(metric, 0)
            if current_value > threshold:
                violations.append({
                    'metric': metric,
                    'current': current_value,
                    'threshold': threshold,
                    'severity': 'critical'
                })
            elif current_value > threshold * 0.8:
                warnings.append({
                    'metric': metric,
                    'current': current_value,
                    'threshold': threshold,
                    'severity': 'warning'
                })
        
        # Calculate overall complexity score
        complexity_score = self.calculate_complexity_score(current)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': current,
            'violations': violations,
            'warnings': warnings,
            'complexity_score': complexity_score,
            'status': 'PASS' if not violations else 'FAIL'
        }
        
        # Print results
        self.print_results(result)
        
        # Save results
        self.save_results(result)
        
        return result
    
    def measure_complexity(self) -> Dict[str, int]:
        """Measure current project complexity"""
        metrics = {}
        
        # Count dependencies
        metrics['dependencies'] = self.count_dependencies()
        
        # Count Docker services
        metrics['services'] = self.count_docker_services()
        
        # Count config files
        metrics['config_files'] = self.count_config_files()
        
        # Count documentation files
        metrics['documentation_files'] = self.count_doc_files()
        
        # Count API endpoints
        metrics['api_endpoints'] = self.count_api_endpoints()
        
        # Count code files
        metrics['python_files'] = self.count_python_files()
        metrics['typescript_files'] = self.count_typescript_files()
        
        # Count Docker layers
        metrics['docker_layers'] = self.count_docker_layers()
        
        return metrics
    
    def count_dependencies(self) -> int:
        """Count total dependencies across all package files"""
        count = 0
        
        # Python dependencies
        req_files = [
            'backend/requirements.txt',
            'backend/requirements.mvp.txt'
        ]
        
        for req_file in req_files:
            if Path(self.project_root / req_file).exists():
                with open(self.project_root / req_file, 'r') as f:
                    lines = f.readlines()
                    count += len([line for line in lines if line.strip() and not line.startswith('#')])
        
        # Node.js dependencies
        package_files = [
            'frontend/package.json',
            'frontend/package.mvp.json'
        ]
        
        for package_file in package_files:
            if Path(self.project_root / package_file).exists():
                with open(self.project_root / package_file, 'r') as f:
                    data = json.load(f)
                    count += len(data.get('dependencies', {}))
                    count += len(data.get('devDependencies', {}))
        
        return count
    
    def count_docker_services(self) -> int:
        """Count Docker services across all compose files"""
        count = 0
        
        compose_files = [
            'docker-compose.yml',
            'docker-compose.mvp.yml',
            'docker-compose.prod.yml'
        ]
        
        for compose_file in compose_files:
            if Path(self.project_root / compose_file).exists():
                with open(self.project_root / compose_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if 'services' in data:
                        count += len(data['services'])
        
        return count
    
    def count_config_files(self) -> int:
        """Count configuration files"""
        config_patterns = [
            '*.yml', '*.yaml', '*.json', '*.toml', '*.ini',
            'Dockerfile*', '*.conf', '*.cfg'
        ]
        
        count = 0
        for pattern in config_patterns:
            count += len(list(self.project_root.rglob(pattern)))
        
        return count
    
    def count_doc_files(self) -> int:
        """Count documentation files"""
        doc_patterns = ['*.md', '*.rst', '*.txt']
        
        count = 0
        for pattern in doc_patterns:
            count += len(list(self.project_root.rglob(pattern)))
        
        return count
    
    def count_api_endpoints(self) -> int:
        """Count API endpoints in FastAPI files"""
        count = 0
        
        # Count @router.get, @router.post, etc. in Python files
        for py_file in self.project_root.rglob('*.py'):
            if 'api' in str(py_file):
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Count FastAPI route decorators
                    count += content.count('@router.get')
                    count += content.count('@router.post')
                    count += content.count('@router.put')
                    count += content.count('@router.delete')
                    count += content.count('@router.patch')
        
        return count
    
    def count_python_files(self) -> int:
        """Count Python files"""
        return len(list(self.project_root.rglob('*.py')))
    
    def count_typescript_files(self) -> int:
        """Count TypeScript files"""
        return len(list(self.project_root.rglob('*.ts'))) + len(list(self.project_root.rglob('*.tsx')))
    
    def count_docker_layers(self) -> int:
        """Count Docker layers across all Dockerfiles"""
        count = 0
        
        for dockerfile in self.project_root.rglob('Dockerfile*'):
            with open(dockerfile, 'r') as f:
                content = f.read()
                # Count RUN, COPY, ADD commands (approximate layer count)
                count += content.count('RUN ')
                count += content.count('COPY ')
                count += content.count('ADD ')
        
        return count
    
    def calculate_complexity_score(self, metrics: Dict[str, int]) -> str:
        """Calculate overall complexity score"""
        score = 0
        
        for metric, value in metrics.items():
            threshold = self.complexity_thresholds.get(metric, 100)
            ratio = value / threshold
            
            if ratio > 1.0:
                score += 3  # Critical
            elif ratio > 0.8:
                score += 2  # High
            elif ratio > 0.6:
                score += 1  # Medium
            else:
                score += 0  # Low
        
        # Normalize score
        max_score = len(metrics) * 3
        normalized_score = score / max_score
        
        if normalized_score > 0.8:
            return 'critical'
        elif normalized_score > 0.6:
            return 'high'
        elif normalized_score > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def print_results(self, result: Dict[str, Any]):
        """Print complexity check results"""
        print(f"\n📊 Complexity Check Results")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Overall Score: {result['complexity_score'].upper()}")
        print(f"Status: {result['status']}")
        
        print(f"\n📈 Current Metrics:")
        for metric, value in result['current_metrics'].items():
            threshold = self.complexity_thresholds.get(metric, 'N/A')
            print(f"  {metric}: {value} (threshold: {threshold})")
        
        if result['violations']:
            print(f"\n❌ Critical Violations:")
            for violation in result['violations']:
                print(f"  {violation['metric']}: {violation['current']} > {violation['threshold']}")
        
        if result['warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"  {warning['metric']}: {warning['current']} > {warning['threshold'] * 0.8}")
        
        if result['status'] == 'PASS':
            print(f"\n✅ Complexity check passed!")
        else:
            print(f"\n❌ Complexity check failed! Reduce complexity before proceeding.")
    
    def save_results(self, result: Dict[str, Any]):
        """Save results to file"""
        results_dir = self.project_root / 'monitoring' / 'complexity'
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'complexity_check_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Also save latest results
        latest_file = results_dir / 'latest_complexity.json'
        with open(latest_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")

def main():
    """Main function"""
    monitor = ComplexityMonitor()
    result = monitor.check_complexity()
    
    # Exit with error code if complexity check failed
    if result['status'] == 'FAIL':
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
    main()
