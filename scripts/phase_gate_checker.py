#!/usr/bin/env python3
"""
AL-0 Phase Gate Checker
Enforces strict phase gate criteria to prevent complexity creep
"""

import os
import json
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import argparse

class PhaseGateChecker:
    def __init__(self, phase: str = "1"):
        self.project_root = Path(__file__).parent.parent
        self.phase = phase
        self.phase_criteria = self.get_phase_criteria()
        self.results = {
            'phase': phase,
            'timestamp': datetime.now().isoformat(),
            'criteria': {},
            'overall_status': 'PASS',
            'blockers': []
        }
    
    def get_phase_criteria(self) -> Dict[str, Any]:
        """Get phase-specific criteria"""
        criteria = {
            "1": {  # MVP Foundation
                'startup_time_max': 120,  # seconds
                'memory_usage_max': 2048,  # MB
                'test_coverage_min': 80,  # percent
                'api_response_max': 500,  # ms
                'ml_inference_max': 2000,  # ms
                'required_services': ['frontend', 'backend', 'redis'],
                'required_endpoints': ['/health', '/api/models', '/api/infer/image'],
                'required_docs': ['README.md', 'API.md', 'DEPLOYMENT.md'],
                'security_checks': ['jwt_auth', 'rate_limiting', 'input_validation']
            },
            "2": {  # Core Enhancement
                'startup_time_max': 180,  # seconds
                'memory_usage_max': 4096,  # MB
                'test_coverage_min': 85,  # percent
                'api_response_max': 300,  # ms
                'ml_inference_max': 1500,  # ms
                'required_services': ['frontend', 'backend', 'redis', 'postgres', 'prometheus'],
                'required_endpoints': ['/health', '/api/models', '/api/infer/image', '/api/telemetry', '/api/monitoring'],
                'required_docs': ['README.md', 'API.md', 'DEPLOYMENT.md', 'PERFORMANCE_OPTIMIZATION.md'],
                'security_checks': ['jwt_auth', 'rate_limiting', 'input_validation', 'rbac']
            },
            "3": {  # Production Scale
                'startup_time_max': 300,  # seconds
                'memory_usage_max': 8192,  # MB
                'test_coverage_min': 90,  # percent
                'api_response_max': 200,  # ms
                'ml_inference_max': 1000,  # ms
                'required_services': ['frontend', 'backend', 'redis', 'postgres', 'prometheus', 'grafana', 'elasticsearch'],
                'required_endpoints': ['/health', '/api/models', '/api/infer/image', '/api/telemetry', '/api/monitoring', '/api/optimization'],
                'required_docs': ['README.md', 'API.md', 'DEPLOYMENT.md', 'PERFORMANCE_OPTIMIZATION.md', 'OPERATIONAL_EXCELLENCE_PLAN.md'],
                'security_checks': ['jwt_auth', 'rate_limiting', 'input_validation', 'rbac', 'secrets_management']
            },
            "4": {  # Enterprise
                'startup_time_max': 600,  # seconds
                'memory_usage_max': 16384,  # MB
                'test_coverage_min': 95,  # percent
                'api_response_max': 100,  # ms
                'ml_inference_max': 500,  # ms
                'required_services': ['frontend', 'backend', 'redis', 'postgres', 'prometheus', 'grafana', 'elasticsearch', 'vault', 'keycloak'],
                'required_endpoints': ['/health', '/api/models', '/api/infer/image', '/api/telemetry', '/api/monitoring', '/api/optimization', '/api/security'],
                'required_docs': ['README.md', 'API.md', 'DEPLOYMENT.md', 'PERFORMANCE_OPTIMIZATION.md', 'OPERATIONAL_EXCELLENCE_PLAN.md', 'ENTERPRISE_GUIDE.md'],
                'security_checks': ['jwt_auth', 'rate_limiting', 'input_validation', 'rbac', 'secrets_management', 'mfa', 'audit_logging']
            }
        }
        return criteria.get(self.phase, criteria["1"])
    
    def check_phase_gate(self) -> Dict[str, Any]:
        """Check all phase gate criteria"""
        print(f"🚪 Checking Phase {self.phase} Gate Criteria...")
        
        # Check each criterion
        self.check_startup_time()
        self.check_memory_usage()
        self.check_test_coverage()
        self.check_api_performance()
        self.check_ml_performance()
        self.check_services()
        self.check_endpoints()
        self.check_documentation()
        self.check_security()
        
        # Determine overall status
        self.results['overall_status'] = self.determine_overall_status()
        
        # Print results
        self.print_results()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def check_startup_time(self):
        """Check application startup time"""
        print("⏱️  Checking startup time...")
        
        try:
            start_time = time.time()
            
            # Start services
            subprocess.run([
                'docker-compose', '-f', 'docker-compose.mvp.yml', 'up', '-d'
            ], cwd=self.project_root, check=True, timeout=300)
            
            # Wait for services to be ready
            self.wait_for_services()
            
            startup_time = time.time() - start_time
            max_time = self.phase_criteria['startup_time_max']
            
            self.results['criteria']['startup_time'] = {
                'actual': startup_time,
                'max_allowed': max_time,
                'status': 'PASS' if startup_time <= max_time else 'FAIL'
            }
            
        except Exception as e:
            self.results['criteria']['startup_time'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            self.results['blockers'].append(f"Startup time check failed: {e}")
    
    def check_memory_usage(self):
        """Check memory usage"""
        print("💾 Checking memory usage...")
        
        try:
            # Get memory usage from Docker stats
            result = subprocess.run([
                'docker', 'stats', '--no-stream', '--format', 'table {{.MemUsage}}'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            # Parse memory usage (simplified)
            total_memory = 0
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    # Extract memory usage (e.g., "123.4MiB" -> 123.4)
                    memory_str = line.split()[0]
                    if 'MiB' in memory_str:
                        memory_mb = float(memory_str.replace('MiB', ''))
                        total_memory += memory_mb
            
            max_memory = self.phase_criteria['memory_usage_max']
            
            self.results['criteria']['memory_usage'] = {
                'actual': total_memory,
                'max_allowed': max_memory,
                'status': 'PASS' if total_memory <= max_memory else 'FAIL'
            }
            
        except Exception as e:
            self.results['criteria']['memory_usage'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            self.results['blockers'].append(f"Memory usage check failed: {e}")
    
    def check_test_coverage(self):
        """Check test coverage"""
        print("🧪 Checking test coverage...")
        
        try:
            # Run tests and get coverage
            result = subprocess.run([
                'python', '-m', 'pytest', '--cov=backend', '--cov-report=json'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            # Parse coverage from JSON report
            coverage_file = self.project_root / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    coverage_percent = coverage_data['totals']['percent_covered']
            else:
                coverage_percent = 0
            
            min_coverage = self.phase_criteria['test_coverage_min']
            
            self.results['criteria']['test_coverage'] = {
                'actual': coverage_percent,
                'min_required': min_coverage,
                'status': 'PASS' if coverage_percent >= min_coverage else 'FAIL'
            }
            
        except Exception as e:
            self.results['criteria']['test_coverage'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            self.results['blockers'].append(f"Test coverage check failed: {e}")
    
    def check_api_performance(self):
        """Check API response times"""
        print("🚀 Checking API performance...")
        
        try:
            # Test API endpoints
            base_url = "http://localhost:8000"
            endpoints = ['/health', '/api/models']
            
            max_response_time = 0
            for endpoint in endpoints:
                start_time = time.time()
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                max_response_time = max(max_response_time, response_time)
            
            max_allowed = self.phase_criteria['api_response_max']
            
            self.results['criteria']['api_performance'] = {
                'actual': max_response_time,
                'max_allowed': max_allowed,
                'status': 'PASS' if max_response_time <= max_allowed else 'FAIL'
            }
            
        except Exception as e:
            self.results['criteria']['api_performance'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            self.results['blockers'].append(f"API performance check failed: {e}")
    
    def check_ml_performance(self):
        """Check ML inference performance"""
        print("🤖 Checking ML performance...")
        
        try:
            # Test ML inference endpoint
            base_url = "http://localhost:8000"
            
            # Create a simple test image (1x1 pixel)
            import io
            from PIL import Image
            
            img = Image.new('RGB', (1, 1), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/infer/image",
                files={'file': ('test.png', img_bytes, 'image/png')},
                timeout=30
            )
            inference_time = (time.time() - start_time) * 1000  # Convert to ms
            
            max_allowed = self.phase_criteria['ml_inference_max']
            
            self.results['criteria']['ml_performance'] = {
                'actual': inference_time,
                'max_allowed': max_allowed,
                'status': 'PASS' if inference_time <= max_allowed else 'FAIL'
            }
            
        except Exception as e:
            self.results['criteria']['ml_performance'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            self.results['blockers'].append(f"ML performance check failed: {e}")
    
    def check_services(self):
        """Check required services are running"""
        print("🐳 Checking services...")
        
        try:
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.mvp.yml', 'ps', '--services'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            running_services = result.stdout.strip().split('\n')
            required_services = self.phase_criteria['required_services']
            
            missing_services = set(required_services) - set(running_services)
            
            self.results['criteria']['services'] = {
                'running': running_services,
                'required': required_services,
                'missing': list(missing_services),
                'status': 'PASS' if not missing_services else 'FAIL'
            }
            
        except Exception as e:
            self.results['criteria']['services'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            self.results['blockers'].append(f"Services check failed: {e}")
    
    def check_endpoints(self):
        """Check required API endpoints are available"""
        print("🔗 Checking endpoints...")
        
        try:
            base_url = "http://localhost:8000"
            required_endpoints = self.phase_criteria['required_endpoints']
            
            available_endpoints = []
            missing_endpoints = []
            
            for endpoint in required_endpoints:
                try:
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                    if response.status_code < 500:  # Not a server error
                        available_endpoints.append(endpoint)
                    else:
                        missing_endpoints.append(endpoint)
                except:
                    missing_endpoints.append(endpoint)
            
            self.results['criteria']['endpoints'] = {
                'available': available_endpoints,
                'required': required_endpoints,
                'missing': missing_endpoints,
                'status': 'PASS' if not missing_endpoints else 'FAIL'
            }
            
        except Exception as e:
            self.results['criteria']['endpoints'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            self.results['blockers'].append(f"Endpoints check failed: {e}")
    
    def check_documentation(self):
        """Check required documentation exists"""
        print("📚 Checking documentation...")
        
        try:
            required_docs = self.phase_criteria['required_docs']
            existing_docs = []
            missing_docs = []
            
            for doc in required_docs:
                doc_path = self.project_root / doc
                if doc_path.exists():
                    existing_docs.append(doc)
                else:
                    missing_docs.append(doc)
            
            self.results['criteria']['documentation'] = {
                'existing': existing_docs,
                'required': required_docs,
                'missing': missing_docs,
                'status': 'PASS' if not missing_docs else 'FAIL'
            }
            
        except Exception as e:
            self.results['criteria']['documentation'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            self.results['blockers'].append(f"Documentation check failed: {e}")
    
    def check_security(self):
        """Check security requirements"""
        print("🔒 Checking security...")
        
        try:
            required_checks = self.phase_criteria['security_checks']
            passed_checks = []
            failed_checks = []
            
            # Basic security checks (simplified)
            for check in required_checks:
                if check == 'jwt_auth':
                    # Check if JWT is implemented
                    if self.check_jwt_implementation():
                        passed_checks.append(check)
                    else:
                        failed_checks.append(check)
                elif check == 'rate_limiting':
                    # Check if rate limiting is implemented
                    if self.check_rate_limiting():
                        passed_checks.append(check)
                    else:
                        failed_checks.append(check)
                # Add more security checks as needed
            
            self.results['criteria']['security'] = {
                'passed': passed_checks,
                'required': required_checks,
                'failed': failed_checks,
                'status': 'PASS' if not failed_checks else 'FAIL'
            }
            
        except Exception as e:
            self.results['criteria']['security'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            self.results['blockers'].append(f"Security check failed: {e}")
    
    def check_jwt_implementation(self) -> bool:
        """Check if JWT authentication is implemented"""
        # Look for JWT-related code in backend
        jwt_files = list(self.project_root.rglob('*.py'))
        for file_path in jwt_files:
            if 'jwt' in str(file_path).lower() or 'auth' in str(file_path).lower():
                with open(file_path, 'r') as f:
                    content = f.read()
                    if 'jwt' in content.lower() or 'token' in content.lower():
                        return True
        return False
    
    def check_rate_limiting(self) -> bool:
        """Check if rate limiting is implemented"""
        # Look for rate limiting code
        rate_limit_files = list(self.project_root.rglob('*.py'))
        for file_path in rate_limit_files:
            with open(file_path, 'r') as f:
                content = f.read()
                if 'rate_limit' in content.lower() or 'throttle' in content.lower():
                    return True
        return False
    
    def wait_for_services(self, timeout: int = 60):
        """Wait for services to be ready"""
        base_url = "http://localhost:8000"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                if response.status_code == 200:
                    return True
            except:
                pass
            time.sleep(2)
        
        return False
    
    def determine_overall_status(self) -> str:
        """Determine overall phase gate status"""
        for criterion, data in self.results['criteria'].items():
            if data.get('status') == 'FAIL':
                return 'FAIL'
        return 'PASS'
    
    def print_results(self):
        """Print phase gate results"""
        print(f"\n🚪 Phase {self.phase} Gate Results")
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Overall Status: {self.results['overall_status']}")
        
        print(f"\n📊 Criteria Results:")
        for criterion, data in self.results['criteria'].items():
            status_icon = "✅" if data.get('status') == 'PASS' else "❌"
            print(f"  {status_icon} {criterion}: {data.get('status', 'UNKNOWN')}")
            
            if 'error' in data:
                print(f"    Error: {data['error']}")
        
        if self.results['blockers']:
            print(f"\n🚫 Blockers:")
            for blocker in self.results['blockers']:
                print(f"  - {blocker}")
        
        if self.results['overall_status'] == 'PASS':
            print(f"\n🎉 Phase {self.phase} gate passed! Ready to proceed to next phase.")
        else:
            print(f"\n❌ Phase {self.phase} gate failed! Fix issues before proceeding.")
    
    def save_results(self):
        """Save results to file"""
        results_dir = self.project_root / 'monitoring' / 'phase_gates'
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'phase_{self.phase}_gate_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Also save latest results
        latest_file = results_dir / f'phase_{self.phase}_gate_latest.json'
        with open(latest_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Check AL-0 phase gate criteria')
    parser.add_argument('--phase', default='1', choices=['1', '2', '3', '4'],
                       help='Phase to check (default: 1)')
    
    args = parser.parse_args()
    
    checker = PhaseGateChecker(phase=args.phase)
    result = checker.check_phase_gate()
    
    # Exit with error code if phase gate failed
    if result['overall_status'] == 'FAIL':
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
    main()
