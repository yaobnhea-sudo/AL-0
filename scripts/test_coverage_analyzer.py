#!/usr/bin/env python3
"""
AL-0 Test Coverage Quality Analyzer
Ensures tests cover critical ML functionality, edge cases, and integration points
"""

import os
import json
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
import re

class TestCoverageAnalyzer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend'
        self.tests_dir = self.project_root / 'tests'
        
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'coverage_quality': {},
            'ml_functionality_coverage': {},
            'edge_case_coverage': {},
            'integration_coverage': {},
            'critical_paths': {},
            'recommendations': [],
            'overall_score': 0
        }
        
        # Define critical ML functionality that must be tested
        self.critical_ml_functions = [
            'model_inference',
            'preprocess_image',
            'postprocess_predictions',
            'load_model',
            'optimize_model',
            'quantize_model',
            'validate_input',
            'handle_errors'
        ]
        
        # Define edge cases that should be tested
        self.edge_cases = [
            'empty_input',
            'invalid_format',
            'oversized_input',
            'malformed_data',
            'network_timeout',
            'memory_overflow',
            'gpu_unavailable',
            'model_not_found'
        ]
        
        # Define integration points
        self.integration_points = [
            'api_endpoints',
            'websocket_connections',
            'database_operations',
            'file_uploads',
            'model_serving',
            'telemetry_streaming',
            'authentication',
            'rate_limiting'
        ]
    
    def analyze_test_coverage_quality(self) -> Dict[str, Any]:
        """Analyze the quality of test coverage beyond just percentages"""
        print("🧪 Analyzing test coverage quality...")
        
        # Run coverage analysis
        coverage_data = self.run_coverage_analysis()
        
        # Analyze ML functionality coverage
        ml_coverage = self.analyze_ml_functionality_coverage()
        
        # Analyze edge case coverage
        edge_coverage = self.analyze_edge_case_coverage()
        
        # Analyze integration coverage
        integration_coverage = self.analyze_integration_coverage()
        
        # Analyze critical paths
        critical_paths = self.analyze_critical_paths()
        
        # Calculate overall quality score
        quality_score = self.calculate_quality_score(
            coverage_data, ml_coverage, edge_coverage, 
            integration_coverage, critical_paths
        )
        
        # Generate recommendations
        recommendations = self.generate_coverage_recommendations(
            coverage_data, ml_coverage, edge_coverage, 
            integration_coverage, critical_paths
        )
        
        self.analysis_results.update({
            'coverage_quality': coverage_data,
            'ml_functionality_coverage': ml_coverage,
            'edge_case_coverage': edge_coverage,
            'integration_coverage': integration_coverage,
            'critical_paths': critical_paths,
            'overall_score': quality_score,
            'recommendations': recommendations
        })
        
        return self.analysis_results
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """Run coverage analysis and extract detailed metrics"""
        print("📊 Running coverage analysis...")
        
        coverage_data = {
            'overall_percentage': 0,
            'file_coverage': {},
            'function_coverage': {},
            'line_coverage': {},
            'branch_coverage': {},
            'missing_lines': {},
            'uncovered_functions': []
        }
        
        try:
            # Run pytest with coverage
            result = subprocess.run([
                'python', '-m', 'pytest', '--cov=backend', '--cov-report=json', '--cov-report=term-missing'
            ], cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            # Parse coverage.json
            coverage_file = self.project_root / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    cov_data = json.load(f)
                    
                    coverage_data['overall_percentage'] = cov_data['totals']['percent_covered']
                    
                    # Analyze file coverage
                    for file_path, file_data in cov_data['files'].items():
                        if 'backend' in file_path:
                            rel_path = file_path.replace(str(self.project_root) + '/', '')
                            coverage_data['file_coverage'][rel_path] = {
                                'percentage': file_data['summary']['percent_covered'],
                                'lines_covered': file_data['summary']['covered_lines'],
                                'lines_total': file_data['summary']['num_statements'],
                                'missing_lines': file_data.get('missing_lines', []),
                                'excluded_lines': file_data.get('excluded_lines', [])
                            }
                            
                            # Track missing lines
                            if file_data.get('missing_lines'):
                                coverage_data['missing_lines'][rel_path] = file_data['missing_lines']
            
            # Extract uncovered functions from terminal output
            if result.stdout:
                uncovered_functions = self.extract_uncovered_functions(result.stdout)
                coverage_data['uncovered_functions'] = uncovered_functions
            
        except subprocess.TimeoutExpired:
            coverage_data['error'] = "Coverage analysis timed out"
        except Exception as e:
            coverage_data['error'] = f"Coverage analysis failed: {e}"
        
        return coverage_data
    
    def analyze_ml_functionality_coverage(self) -> Dict[str, Any]:
        """Analyze coverage of critical ML functionality"""
        print("🤖 Analyzing ML functionality coverage...")
        
        ml_coverage = {
            'critical_functions_covered': 0,
            'critical_functions_total': len(self.critical_ml_functions),
            'coverage_details': {},
            'missing_tests': [],
            'test_quality_score': 0
        }
        
        # Find ML-related files
        ml_files = self.find_ml_files()
        
        for file_path in ml_files:
            file_coverage = self.analyze_file_ml_coverage(file_path)
            ml_coverage['coverage_details'][file_path] = file_coverage
            
            # Check if critical functions are tested
            for func in self.critical_ml_functions:
                if func in file_coverage.get('functions_tested', []):
                    ml_coverage['critical_functions_covered'] += 1
                else:
                    ml_coverage['missing_tests'].append(f"{file_path}:{func}")
        
        # Calculate test quality score
        ml_coverage['test_quality_score'] = self.calculate_ml_test_quality(ml_coverage['coverage_details'])
        
        return ml_coverage
    
    def analyze_edge_case_coverage(self) -> Dict[str, Any]:
        """Analyze coverage of edge cases and error conditions"""
        print("⚠️  Analyzing edge case coverage...")
        
        edge_coverage = {
            'edge_cases_covered': 0,
            'edge_cases_total': len(self.edge_cases),
            'error_handling_tests': 0,
            'boundary_tests': 0,
            'negative_tests': 0,
            'coverage_details': {}
        }
        
        # Find test files
        test_files = self.find_test_files()
        
        for test_file in test_files:
            file_edge_coverage = self.analyze_file_edge_coverage(test_file)
            edge_coverage['coverage_details'][test_file] = file_edge_coverage
            
            # Count edge cases covered
            for edge_case in self.edge_cases:
                if edge_case in file_edge_coverage.get('edge_cases_tested', []):
                    edge_coverage['edge_cases_covered'] += 1
            
            # Count test types
            edge_coverage['error_handling_tests'] += file_edge_coverage.get('error_handling_tests', 0)
            edge_coverage['boundary_tests'] += file_edge_coverage.get('boundary_tests', 0)
            edge_coverage['negative_tests'] += file_edge_coverage.get('negative_tests', 0)
        
        return edge_coverage
    
    def analyze_integration_coverage(self) -> Dict[str, Any]:
        """Analyze coverage of integration points"""
        print("🔗 Analyzing integration coverage...")
        
        integration_coverage = {
            'integration_points_covered': 0,
            'integration_points_total': len(self.integration_points),
            'api_endpoint_tests': 0,
            'database_tests': 0,
            'websocket_tests': 0,
            'file_upload_tests': 0,
            'coverage_details': {}
        }
        
        # Find integration test files
        integration_test_files = self.find_integration_test_files()
        
        for test_file in integration_test_files:
            file_integration_coverage = self.analyze_file_integration_coverage(test_file)
            integration_coverage['coverage_details'][test_file] = file_integration_coverage
            
            # Count integration points covered
            for integration_point in self.integration_points:
                if integration_point in file_integration_coverage.get('integration_points_tested', []):
                    integration_coverage['integration_points_covered'] += 1
            
            # Count specific test types
            integration_coverage['api_endpoint_tests'] += file_integration_coverage.get('api_endpoint_tests', 0)
            integration_coverage['database_tests'] += file_integration_coverage.get('database_tests', 0)
            integration_coverage['websocket_tests'] += file_integration_coverage.get('websocket_tests', 0)
            integration_coverage['file_upload_tests'] += file_integration_coverage.get('file_upload_tests', 0)
        
        return integration_coverage
    
    def analyze_critical_paths(self) -> Dict[str, Any]:
        """Analyze coverage of critical business paths"""
        print("🎯 Analyzing critical path coverage...")
        
        critical_paths = {
            'user_flows_covered': 0,
            'user_flows_total': 0,
            'critical_scenarios': [],
            'coverage_details': {}
        }
        
        # Define critical user flows
        critical_scenarios = [
            'user_uploads_image',
            'user_uploads_video',
            'user_views_simulator',
            'user_views_telemetry',
            'admin_manages_models',
            'system_handles_errors',
            'system_scales_automatically'
        ]
        
        critical_paths['critical_scenarios'] = critical_scenarios
        critical_paths['user_flows_total'] = len(critical_scenarios)
        
        # Find end-to-end test files
        e2e_test_files = self.find_e2e_test_files()
        
        for test_file in e2e_test_files:
            file_critical_coverage = self.analyze_file_critical_coverage(test_file)
            critical_paths['coverage_details'][test_file] = file_critical_coverage
            
            # Count critical scenarios covered
            for scenario in critical_scenarios:
                if scenario in file_critical_coverage.get('scenarios_tested', []):
                    critical_paths['user_flows_covered'] += 1
        
        return critical_paths
    
    def find_ml_files(self) -> List[str]:
        """Find ML-related Python files"""
        ml_files = []
        
        for py_file in self.backend_dir.rglob('*.py'):
            if any(keyword in str(py_file).lower() for keyword in ['model', 'inference', 'ml', 'ai', 'neural', 'pytorch', 'tensorflow']):
                ml_files.append(str(py_file.relative_to(self.project_root)))
        
        return ml_files
    
    def find_test_files(self) -> List[str]:
        """Find test files"""
        test_files = []
        
        for test_file in self.project_root.rglob('test_*.py'):
            test_files.append(str(test_file.relative_to(self.project_root)))
        
        for test_file in self.project_root.rglob('*_test.py'):
            test_files.append(str(test_file.relative_to(self.project_root)))
        
        return test_files
    
    def find_integration_test_files(self) -> List[str]:
        """Find integration test files"""
        integration_files = []
        
        for test_file in self.project_root.rglob('*integration*.py'):
            integration_files.append(str(test_file.relative_to(self.project_root)))
        
        for test_file in self.project_root.rglob('*e2e*.py'):
            integration_files.append(str(test_file.relative_to(self.project_root)))
        
        return integration_files
    
    def find_e2e_test_files(self) -> List[str]:
        """Find end-to-end test files"""
        e2e_files = []
        
        for test_file in self.project_root.rglob('*e2e*.py'):
            e2e_files.append(str(test_file.relative_to(self.project_root)))
        
        return e2e_files
    
    def analyze_file_ml_coverage(self, file_path: str) -> Dict[str, Any]:
        """Analyze ML coverage for a specific file"""
        file_coverage = {
            'functions_tested': [],
            'test_quality': 'unknown',
            'error_handling_tested': False,
            'performance_tested': False
        }
        
        try:
            # Read the file and find ML functions
            full_path = self.project_root / file_path
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Parse AST to find functions
            tree = ast.parse(content)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            # Check if functions are tested
            test_file = self.find_test_file_for_source(file_path)
            if test_file:
                with open(self.project_root / test_file, 'r') as f:
                    test_content = f.read()
                
                for func in functions:
                    if func in test_content:
                        file_coverage['functions_tested'].append(func)
                
                # Check test quality indicators
                if 'pytest.raises' in test_content or 'assertRaises' in test_content:
                    file_coverage['error_handling_tested'] = True
                
                if 'time' in test_content or 'performance' in test_content.lower():
                    file_coverage['performance_tested'] = True
                
                # Determine test quality
                if file_coverage['error_handling_tested'] and file_coverage['performance_tested']:
                    file_coverage['test_quality'] = 'excellent'
                elif file_coverage['error_handling_tested'] or file_coverage['performance_tested']:
                    file_coverage['test_quality'] = 'good'
                else:
                    file_coverage['test_quality'] = 'basic'
        
        except Exception as e:
            file_coverage['error'] = str(e)
        
        return file_coverage
    
    def analyze_file_edge_coverage(self, test_file: str) -> Dict[str, Any]:
        """Analyze edge case coverage for a test file"""
        file_coverage = {
            'edge_cases_tested': [],
            'error_handling_tests': 0,
            'boundary_tests': 0,
            'negative_tests': 0
        }
        
        try:
            full_path = self.project_root / test_file
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Check for edge case patterns
            edge_patterns = {
                'empty_input': ['empty', 'null', 'none', '""', "''"],
                'invalid_format': ['invalid', 'malformed', 'wrong format'],
                'oversized_input': ['large', 'big', 'huge', 'oversized'],
                'malformed_data': ['malformed', 'corrupt', 'invalid data'],
                'network_timeout': ['timeout', 'network', 'connection'],
                'memory_overflow': ['memory', 'overflow', 'oom'],
                'gpu_unavailable': ['gpu', 'cuda', 'device'],
                'model_not_found': ['model not found', 'missing model']
            }
            
            for edge_case, patterns in edge_patterns.items():
                if any(pattern in content.lower() for pattern in patterns):
                    file_coverage['edge_cases_tested'].append(edge_case)
            
            # Count test types
            file_coverage['error_handling_tests'] = content.count('pytest.raises') + content.count('assertRaises')
            file_coverage['boundary_tests'] = content.count('boundary') + content.count('edge case')
            file_coverage['negative_tests'] = content.count('should fail') + content.count('should raise')
        
        except Exception as e:
            file_coverage['error'] = str(e)
        
        return file_coverage
    
    def analyze_file_integration_coverage(self, test_file: str) -> Dict[str, Any]:
        """Analyze integration coverage for a test file"""
        file_coverage = {
            'integration_points_tested': [],
            'api_endpoint_tests': 0,
            'database_tests': 0,
            'websocket_tests': 0,
            'file_upload_tests': 0
        }
        
        try:
            full_path = self.project_root / test_file
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Check for integration patterns
            integration_patterns = {
                'api_endpoints': ['test_client', 'response.status_code', 'api/', 'endpoint'],
                'websocket_connections': ['websocket', 'ws://', 'socket'],
                'database_operations': ['database', 'db', 'sql', 'query'],
                'file_uploads': ['upload', 'file', 'multipart'],
                'model_serving': ['model', 'inference', 'predict'],
                'telemetry_streaming': ['telemetry', 'stream', 'real-time'],
                'authentication': ['auth', 'login', 'token', 'jwt'],
                'rate_limiting': ['rate limit', 'throttle', 'limit']
            }
            
            for integration_point, patterns in integration_patterns.items():
                if any(pattern in content.lower() for pattern in patterns):
                    file_coverage['integration_points_tested'].append(integration_point)
            
            # Count specific test types
            file_coverage['api_endpoint_tests'] = content.count('test_client') + content.count('response.status_code')
            file_coverage['database_tests'] = content.count('database') + content.count('db.')
            file_coverage['websocket_tests'] = content.count('websocket')
            file_coverage['file_upload_tests'] = content.count('upload') + content.count('multipart')
        
        except Exception as e:
            file_coverage['error'] = str(e)
        
        return file_coverage
    
    def analyze_file_critical_coverage(self, test_file: str) -> Dict[str, Any]:
        """Analyze critical path coverage for a test file"""
        file_coverage = {
            'scenarios_tested': [],
            'user_flow_tests': 0,
            'business_logic_tests': 0
        }
        
        try:
            full_path = self.project_root / test_file
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Check for critical scenario patterns
            scenario_patterns = {
                'user_uploads_image': ['upload image', 'image upload', 'file upload'],
                'user_uploads_video': ['upload video', 'video upload'],
                'user_views_simulator': ['simulator', '3d', 'visualization'],
                'user_views_telemetry': ['telemetry', 'dashboard', 'monitoring'],
                'admin_manages_models': ['admin', 'manage model', 'model management'],
                'system_handles_errors': ['error handling', 'exception', 'fail'],
                'system_scales_automatically': ['scale', 'auto', 'load']
            }
            
            for scenario, patterns in scenario_patterns.items():
                if any(pattern in content.lower() for pattern in patterns):
                    file_coverage['scenarios_tested'].append(scenario)
            
            # Count test types
            file_coverage['user_flow_tests'] = content.count('user') + content.count('flow')
            file_coverage['business_logic_tests'] = content.count('business') + content.count('logic')
        
        except Exception as e:
            file_coverage['error'] = str(e)
        
        return file_coverage
    
    def find_test_file_for_source(self, source_file: str) -> Optional[str]:
        """Find corresponding test file for a source file"""
        # Convert source file to test file name
        source_name = Path(source_file).stem
        test_name = f"test_{source_name}.py"
        
        # Look for test file
        test_file = self.project_root / 'tests' / test_name
        if test_file.exists():
            return str(test_file.relative_to(self.project_root))
        
        # Look in same directory
        test_file = self.project_root / source_file.replace('.py', f'_test.py')
        if test_file.exists():
            return str(test_file.relative_to(self.project_root))
        
        return None
    
    def extract_uncovered_functions(self, coverage_output: str) -> List[str]:
        """Extract uncovered functions from coverage output"""
        uncovered = []
        
        # Look for function names in coverage output
        lines = coverage_output.split('\n')
        for line in lines:
            if 'def ' in line and '->' in line:
                # Extract function name
                match = re.search(r'def\s+(\w+)', line)
                if match:
                    uncovered.append(match.group(1))
        
        return uncovered
    
    def calculate_ml_test_quality(self, coverage_details: Dict[str, Any]) -> float:
        """Calculate ML test quality score"""
        if not coverage_details:
            return 0.0
        
        total_score = 0
        file_count = 0
        
        for file_path, details in coverage_details.items():
            if 'error' not in details:
                file_count += 1
                score = 0
                
                # Base score for having tests
                if details.get('functions_tested'):
                    score += 30
                
                # Quality bonuses
                if details.get('error_handling_tested'):
                    score += 30
                
                if details.get('performance_tested'):
                    score += 20
                
                if details.get('test_quality') == 'excellent':
                    score += 20
                elif details.get('test_quality') == 'good':
                    score += 10
                
                total_score += min(score, 100)  # Cap at 100
        
        return total_score / file_count if file_count > 0 else 0.0
    
    def calculate_quality_score(self, coverage_data: Dict, ml_coverage: Dict, 
                              edge_coverage: Dict, integration_coverage: Dict, 
                              critical_paths: Dict) -> float:
        """Calculate overall test coverage quality score"""
        scores = []
        
        # Coverage percentage score (30% weight)
        coverage_percentage = coverage_data.get('overall_percentage', 0)
        scores.append(('coverage_percentage', coverage_percentage, 0.3))
        
        # ML functionality score (25% weight)
        ml_score = (ml_coverage.get('critical_functions_covered', 0) / 
                   max(ml_coverage.get('critical_functions_total', 1), 1)) * 100
        ml_quality = ml_coverage.get('test_quality_score', 0)
        ml_combined = (ml_score + ml_quality) / 2
        scores.append(('ml_functionality', ml_combined, 0.25))
        
        # Edge case score (20% weight)
        edge_score = (edge_coverage.get('edge_cases_covered', 0) / 
                     max(edge_coverage.get('edge_cases_total', 1), 1)) * 100
        scores.append(('edge_cases', edge_score, 0.2))
        
        # Integration score (15% weight)
        integration_score = (integration_coverage.get('integration_points_covered', 0) / 
                           max(integration_coverage.get('integration_points_total', 1), 1)) * 100
        scores.append(('integration', integration_score, 0.15))
        
        # Critical paths score (10% weight)
        critical_score = (critical_paths.get('user_flows_covered', 0) / 
                         max(critical_paths.get('user_flows_total', 1), 1)) * 100
        scores.append(('critical_paths', critical_score, 0.1))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        return round(total_score, 2)
    
    def generate_coverage_recommendations(self, coverage_data: Dict, ml_coverage: Dict,
                                        edge_coverage: Dict, integration_coverage: Dict,
                                        critical_paths: Dict) -> List[Dict[str, Any]]:
        """Generate recommendations for improving test coverage quality"""
        recommendations = []
        
        # Coverage percentage recommendations
        coverage_percentage = coverage_data.get('overall_percentage', 0)
        if coverage_percentage < 80:
            recommendations.append({
                'type': 'coverage',
                'priority': 'high',
                'message': f'Overall coverage is {coverage_percentage}%. Aim for at least 80%.',
                'action': 'Add more test cases to increase coverage percentage.'
            })
        
        # ML functionality recommendations
        ml_covered = ml_coverage.get('critical_functions_covered', 0)
        ml_total = ml_coverage.get('critical_functions_total', 0)
        if ml_covered < ml_total:
            missing = ml_total - ml_covered
            recommendations.append({
                'type': 'ml_functionality',
                'priority': 'high',
                'message': f'{missing} critical ML functions are not tested.',
                'action': f'Add tests for: {", ".join(ml_coverage.get("missing_tests", [])[:5])}'
            })
        
        # Edge case recommendations
        edge_covered = edge_coverage.get('edge_cases_covered', 0)
        edge_total = edge_coverage.get('edge_cases_total', 0)
        if edge_covered < edge_total:
            missing = edge_total - edge_covered
            recommendations.append({
                'type': 'edge_cases',
                'priority': 'medium',
                'message': f'{missing} edge cases are not tested.',
                'action': 'Add tests for error conditions, boundary values, and negative scenarios.'
            })
        
        # Integration recommendations
        integration_covered = integration_coverage.get('integration_points_covered', 0)
        integration_total = integration_coverage.get('integration_points_total', 0)
        if integration_covered < integration_total:
            missing = integration_total - integration_covered
            recommendations.append({
                'type': 'integration',
                'priority': 'medium',
                'message': f'{missing} integration points are not tested.',
                'action': 'Add integration tests for API endpoints, database operations, and external services.'
            })
        
        # Critical paths recommendations
        critical_covered = critical_paths.get('user_flows_covered', 0)
        critical_total = critical_paths.get('user_flows_total', 0)
        if critical_covered < critical_total:
            missing = critical_total - critical_covered
            recommendations.append({
                'type': 'critical_paths',
                'priority': 'high',
                'message': f'{missing} critical user flows are not tested.',
                'action': 'Add end-to-end tests for critical business scenarios.'
            })
        
        return recommendations
    
    def save_analysis(self):
        """Save analysis results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        analysis_file = self.project_root / 'monitoring' / 'test_coverage' / f'coverage_analysis_{timestamp}.json'
        analysis_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(analysis_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        # Also save latest analysis
        latest_file = self.project_root / 'monitoring' / 'test_coverage' / 'latest_coverage_analysis.json'
        with open(latest_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        print(f"💾 Analysis saved to: {analysis_file}")
    
    def print_summary(self):
        """Print analysis summary"""
        print(f"\n🧪 AL-0 Test Coverage Quality Analysis")
        print(f"Overall Score: {self.analysis_results['overall_score']}/100")
        
        # Coverage quality
        coverage = self.analysis_results['coverage_quality']
        print(f"\n📊 Coverage Quality:")
        print(f"  Overall Percentage: {coverage.get('overall_percentage', 0)}%")
        print(f"  Files Analyzed: {len(coverage.get('file_coverage', {}))}")
        
        # ML functionality
        ml = self.analysis_results['ml_functionality_coverage']
        print(f"\n🤖 ML Functionality Coverage:")
        print(f"  Critical Functions: {ml.get('critical_functions_covered', 0)}/{ml.get('critical_functions_total', 0)}")
        print(f"  Test Quality Score: {ml.get('test_quality_score', 0)}/100")
        
        # Edge cases
        edge = self.analysis_results['edge_case_coverage']
        print(f"\n⚠️  Edge Case Coverage:")
        print(f"  Edge Cases: {edge.get('edge_cases_covered', 0)}/{edge.get('edge_cases_total', 0)}")
        print(f"  Error Handling Tests: {edge.get('error_handling_tests', 0)}")
        
        # Integration
        integration = self.analysis_results['integration_coverage']
        print(f"\n🔗 Integration Coverage:")
        print(f"  Integration Points: {integration.get('integration_points_covered', 0)}/{integration.get('integration_points_total', 0)}")
        print(f"  API Endpoint Tests: {integration.get('api_endpoint_tests', 0)}")
        
        # Critical paths
        critical = self.analysis_results['critical_paths']
        print(f"\n🎯 Critical Path Coverage:")
        print(f"  User Flows: {critical.get('user_flows_covered', 0)}/{critical.get('user_flows_total', 0)}")
        
        # Recommendations
        recommendations = self.analysis_results['recommendations']
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                print(f"  {i}. {priority_icon} {rec['message']}")

def main():
    """Main function"""
    analyzer = TestCoverageAnalyzer()
    
    print("🧪 Starting test coverage quality analysis...")
    
    # Run analysis
    results = analyzer.analyze_test_coverage_quality()
    
    # Print summary
    analyzer.print_summary()
    
    # Save results
    analyzer.save_analysis()
    
    # Exit with error code if quality is low
    if results['overall_score'] < 70:
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
    main()
