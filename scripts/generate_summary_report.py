#!/usr/bin/env python3
"""
AL-0 Operational Excellence Summary Report Generator
Generates comprehensive reports from all operational checks
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class SummaryReportGenerator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.monitoring_dir = self.project_root / 'monitoring'
        self.summary_dir = self.monitoring_dir / 'summary'
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'overall_status': 'PASS',
            'recommendations': [],
            'metrics': {}
        }
    
    def generate_summary(self):
        """Generate comprehensive operational excellence summary"""
        print("📊 Generating Operational Excellence Summary Report...")
        
        # Collect results from all checks
        self.collect_complexity_results()
        self.collect_docs_sync_results()
        self.collect_phase_gate_results()
        self.collect_automated_metrics_results()
        self.collect_test_coverage_quality_results()
        self.collect_progressive_feature_unlock_results()
        self.collect_security_results()
        
        # Calculate overall metrics
        self.calculate_metrics()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Determine overall status
        self.determine_overall_status()
        
        # Generate reports
        self.generate_markdown_report()
        self.generate_json_report()
        self.generate_dashboard_data()
        
        # Print summary
        self.print_summary()
    
    def collect_complexity_results(self):
        """Collect complexity monitoring results"""
        complexity_dir = self.monitoring_dir / 'complexity'
        
        if complexity_dir.exists():
            latest_file = complexity_dir / 'latest_complexity.json'
            if latest_file.exists():
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    self.report['checks']['complexity'] = {
                        'status': data.get('status', 'UNKNOWN'),
                        'score': data.get('complexity_score', 'unknown'),
                        'violations': len(data.get('violations', [])),
                        'warnings': len(data.get('warnings', [])),
                        'metrics': data.get('current_metrics', {})
                    }
            else:
                self.report['checks']['complexity'] = {
                    'status': 'NO_DATA',
                    'message': 'No complexity data available'
                }
        else:
            self.report['checks']['complexity'] = {
                'status': 'NO_DATA',
                'message': 'Complexity monitoring not set up'
            }
    
    def collect_docs_sync_results(self):
        """Collect documentation sync results"""
        docs_sync_dir = self.monitoring_dir / 'docs_sync'
        
        if docs_sync_dir.exists():
            latest_file = docs_sync_dir / 'latest_docs_sync.json'
            if latest_file.exists():
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    self.report['checks']['docs_sync'] = {
                        'status': data.get('sync_status', 'UNKNOWN'),
                        'out_of_sync': len(data.get('out_of_sync', [])),
                        'missing_docs': len(data.get('missing_docs', [])),
                        'stale_docs': len(data.get('stale_docs', []))
                    }
            else:
                self.report['checks']['docs_sync'] = {
                    'status': 'NO_DATA',
                    'message': 'No docs sync data available'
                }
        else:
            self.report['checks']['docs_sync'] = {
                'status': 'NO_DATA',
                'message': 'Docs sync monitoring not set up'
            }
    
    def collect_phase_gate_results(self):
        """Collect phase gate results"""
        phase_gates_dir = self.monitoring_dir / 'phase_gates'
        
        if phase_gates_dir.exists():
            # Find latest phase gate results
            phase_files = list(phase_gates_dir.glob('phase_*_gate_latest.json'))
            if phase_files:
                latest_phase_file = max(phase_files, key=lambda x: x.stat().st_mtime)
                with open(latest_phase_file, 'r') as f:
                    data = json.load(f)
                    self.report['checks']['phase_gate'] = {
                        'phase': data.get('phase', 'unknown'),
                        'status': data.get('overall_status', 'UNKNOWN'),
                        'criteria_passed': sum(1 for c in data.get('criteria', {}).values() if c.get('status') == 'PASS'),
                        'criteria_total': len(data.get('criteria', {})),
                        'blockers': len(data.get('blockers', []))
                    }
            else:
                self.report['checks']['phase_gate'] = {
                    'status': 'NO_DATA',
                    'message': 'No phase gate data available'
                }
        else:
            self.report['checks']['phase_gate'] = {
                'status': 'NO_DATA',
                'message': 'Phase gate monitoring not set up'
            }
    
    def collect_automated_metrics_results(self):
        """Collect automated metrics tracking results"""
        metrics_dir = self.monitoring_dir / 'metrics'
        
        if metrics_dir.exists():
            latest_file = metrics_dir / 'latest_metrics.json'
            if latest_file.exists():
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    summary = data.get('summary', {})
                    self.report['checks']['automated_metrics'] = {
                        'status': summary.get('overall_status', 'UNKNOWN'),
                        'performance_score': summary.get('performance_score', 0),
                        'efficiency_score': summary.get('efficiency_score', 0),
                        'hardware_type': data.get('hardware', {}).get('ml_acceleration', 'unknown'),
                        'startup_time': data.get('startup_metrics', {}).get('total_time', 0),
                        'memory_usage': data.get('memory_metrics', {}).get('total_memory_usage', 0)
                    }
            else:
                self.report['checks']['automated_metrics'] = {
                    'status': 'NO_DATA',
                    'message': 'No automated metrics data available'
                }
        else:
            self.report['checks']['automated_metrics'] = {
                'status': 'NO_DATA',
                'message': 'Automated metrics monitoring not set up'
            }
    
    def collect_test_coverage_quality_results(self):
        """Collect test coverage quality analysis results"""
        coverage_dir = self.monitoring_dir / 'test_coverage'
        
        if coverage_dir.exists():
            latest_file = coverage_dir / 'latest_coverage_analysis.json'
            if latest_file.exists():
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    self.report['checks']['test_coverage_quality'] = {
                        'status': 'PASS' if data.get('overall_score', 0) >= 70 else 'FAIL',
                        'overall_score': data.get('overall_score', 0),
                        'ml_functions_covered': data.get('ml_functionality_coverage', {}).get('critical_functions_covered', 0),
                        'ml_functions_total': data.get('ml_functionality_coverage', {}).get('critical_functions_total', 0),
                        'edge_cases_covered': data.get('edge_case_coverage', {}).get('edge_cases_covered', 0),
                        'integration_points_covered': data.get('integration_coverage', {}).get('integration_points_covered', 0)
                    }
            else:
                self.report['checks']['test_coverage_quality'] = {
                    'status': 'NO_DATA',
                    'message': 'No test coverage quality data available'
                }
        else:
            self.report['checks']['test_coverage_quality'] = {
                'status': 'NO_DATA',
                'message': 'Test coverage quality monitoring not set up'
            }
    
    def collect_progressive_feature_unlock_results(self):
        """Collect progressive feature unlock analysis results"""
        feature_unlock_dir = self.monitoring_dir / 'feature_unlock'
        
        if feature_unlock_dir.exists():
            # Find latest feature unlock results
            unlock_files = list(feature_unlock_dir.glob('feature_unlock_*.json'))
            if unlock_files:
                latest_file = max(unlock_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                    self.report['checks']['progressive_feature_unlock'] = {
                        'status': 'PASS' if len(data.get('available_features', [])) > 0 else 'WARNING',
                        'current_phase': data.get('current_phase', 'unknown'),
                        'hardware_profile': data.get('hardware_profile', 'unknown'),
                        'available_features': len(data.get('available_features', [])),
                        'locked_features': len(data.get('locked_features', [])),
                        'memory_usage': data.get('resource_usage', {}).get('memory_used_mb', 0)
                    }
            else:
                self.report['checks']['progressive_feature_unlock'] = {
                    'status': 'NO_DATA',
                    'message': 'No feature unlock data available'
                }
        else:
            self.report['checks']['progressive_feature_unlock'] = {
                'status': 'NO_DATA',
                'message': 'Progressive feature unlock monitoring not set up'
            }
    
    def collect_security_results(self):
        """Collect security check results"""
        security_dir = self.monitoring_dir / 'security'
        
        if security_dir.exists():
            # Look for security test results
            security_files = list(security_dir.glob('*.json'))
            if security_files:
                latest_security_file = max(security_files, key=lambda x: x.stat().st_mtime)
                with open(latest_security_file, 'r') as f:
                    data = json.load(f)
                    self.report['checks']['security'] = {
                        'status': data.get('status', 'UNKNOWN'),
                        'vulnerabilities': data.get('vulnerabilities', 0),
                        'high_severity': data.get('high_severity', 0),
                        'medium_severity': data.get('medium_severity', 0),
                        'low_severity': data.get('low_severity', 0)
                    }
            else:
                self.report['checks']['security'] = {
                    'status': 'NO_DATA',
                    'message': 'No security data available'
                }
        else:
            self.report['checks']['security'] = {
                'status': 'NO_DATA',
                'message': 'Security monitoring not set up'
            }
    
    def calculate_metrics(self):
        """Calculate overall operational metrics"""
        metrics = {}
        
        # Complexity metrics
        if 'complexity' in self.report['checks']:
            complexity = self.report['checks']['complexity']
            if 'metrics' in complexity:
                metrics['total_dependencies'] = complexity['metrics'].get('dependencies', 0)
                metrics['total_services'] = complexity['metrics'].get('services', 0)
                metrics['total_config_files'] = complexity['metrics'].get('config_files', 0)
                metrics['total_doc_files'] = complexity['metrics'].get('documentation_files', 0)
                metrics['total_api_endpoints'] = complexity['metrics'].get('api_endpoints', 0)
        
        # Documentation metrics
        if 'docs_sync' in self.report['checks']:
            docs_sync = self.report['checks']['docs_sync']
            metrics['docs_out_of_sync'] = docs_sync.get('out_of_sync', 0)
            metrics['docs_missing'] = docs_sync.get('missing_docs', 0)
            metrics['docs_stale'] = docs_sync.get('stale_docs', 0)
        
        # Performance metrics
        if 'performance' in self.report['checks']:
            performance = self.report['checks']['performance']
            metrics['avg_response_time'] = performance.get('response_time', 0)
            metrics['throughput'] = performance.get('throughput', 0)
            metrics['error_rate'] = performance.get('error_rate', 0)
        
        # Security metrics
        if 'security' in self.report['checks']:
            security = self.report['checks']['security']
            metrics['total_vulnerabilities'] = security.get('vulnerabilities', 0)
            metrics['high_severity_vulns'] = security.get('high_severity', 0)
        
        self.report['metrics'] = metrics
    
    def generate_recommendations(self):
        """Generate recommendations based on check results"""
        recommendations = []
        
        # Complexity recommendations
        if 'complexity' in self.report['checks']:
            complexity = self.report['checks']['complexity']
            if complexity.get('status') == 'FAIL':
                recommendations.append({
                    'category': 'Complexity',
                    'priority': 'HIGH',
                    'message': 'Project complexity exceeds thresholds. Consider simplifying the stack or breaking into smaller components.',
                    'action': 'Review and reduce dependencies, services, or configuration files.'
                })
            elif complexity.get('score') == 'high':
                recommendations.append({
                    'category': 'Complexity',
                    'priority': 'MEDIUM',
                    'message': 'Project complexity is approaching thresholds. Monitor closely.',
                    'action': 'Consider refactoring or documentation improvements.'
                })
        
        # Documentation recommendations
        if 'docs_sync' in self.report['checks']:
            docs_sync = self.report['checks']['docs_sync']
            if docs_sync.get('out_of_sync', 0) > 0:
                recommendations.append({
                    'category': 'Documentation',
                    'priority': 'HIGH',
                    'message': f"{docs_sync.get('out_of_sync', 0)} configuration files are out of sync with documentation.",
                    'action': 'Update documentation to reflect configuration changes.'
                })
            if docs_sync.get('missing_docs', 0) > 0:
                recommendations.append({
                    'category': 'Documentation',
                    'priority': 'MEDIUM',
                    'message': f"{docs_sync.get('missing_docs', 0)} documentation files are missing.",
                    'action': 'Create missing documentation files.'
                })
            if docs_sync.get('stale_docs', 0) > 0:
                recommendations.append({
                    'category': 'Documentation',
                    'priority': 'LOW',
                    'message': f"{docs_sync.get('stale_docs', 0)} documentation files are stale.",
                    'action': 'Review and update stale documentation.'
                })
        
        # Performance recommendations
        if 'performance' in self.report['checks']:
            performance = self.report['checks']['performance']
            if performance.get('response_time', 0) > 500:
                recommendations.append({
                    'category': 'Performance',
                    'priority': 'HIGH',
                    'message': f"Average response time ({performance.get('response_time', 0)}ms) exceeds acceptable limits.",
                    'action': 'Optimize API endpoints and database queries.'
                })
            if performance.get('error_rate', 0) > 5:
                recommendations.append({
                    'category': 'Performance',
                    'priority': 'HIGH',
                    'message': f"Error rate ({performance.get('error_rate', 0)}%) is too high.",
                    'action': 'Investigate and fix error sources.'
                })
        
        # Security recommendations
        if 'security' in self.report['checks']:
            security = self.report['checks']['security']
            if security.get('high_severity', 0) > 0:
                recommendations.append({
                    'category': 'Security',
                    'priority': 'CRITICAL',
                    'message': f"{security.get('high_severity', 0)} high-severity vulnerabilities found.",
                    'action': 'Immediately patch or mitigate high-severity vulnerabilities.'
                })
            if security.get('vulnerabilities', 0) > 10:
                recommendations.append({
                    'category': 'Security',
                    'priority': 'MEDIUM',
                    'message': f"Total vulnerabilities ({security.get('vulnerabilities', 0)}) is high.",
                    'action': 'Review and address security vulnerabilities.'
                })
        
        self.report['recommendations'] = recommendations
    
    def determine_overall_status(self):
        """Determine overall operational excellence status"""
        failed_checks = 0
        total_checks = 0
        
        for check_name, check_data in self.report['checks'].items():
            total_checks += 1
            if check_data.get('status') == 'FAIL':
                failed_checks += 1
        
        if failed_checks == 0:
            self.report['overall_status'] = 'PASS'
        elif failed_checks <= total_checks * 0.2:  # Less than 20% failed
            self.report['overall_status'] = 'WARNING'
        else:
            self.report['overall_status'] = 'FAIL'
    
    def generate_markdown_report(self):
        """Generate markdown report"""
        report_file = self.summary_dir / 'operational_excellence_report.md'
        
        with open(report_file, 'w') as f:
            f.write(f"# AL-0 Operational Excellence Report\n\n")
            f.write(f"**Generated:** {self.report['timestamp']}\n")
            f.write(f"**Overall Status:** {self.report['overall_status']}\n\n")
            
            # Check results
            f.write("## Check Results\n\n")
            for check_name, check_data in self.report['checks'].items():
                status_icon = "✅" if check_data.get('status') == 'PASS' else "❌"
                f.write(f"### {check_name.replace('_', ' ').title()}\n")
                f.write(f"**Status:** {status_icon} {check_data.get('status', 'UNKNOWN')}\n\n")
                
                # Add specific details for each check
                if check_name == 'complexity':
                    f.write(f"- **Complexity Score:** {check_data.get('score', 'unknown')}\n")
                    f.write(f"- **Violations:** {check_data.get('violations', 0)}\n")
                    f.write(f"- **Warnings:** {check_data.get('warnings', 0)}\n")
                elif check_name == 'docs_sync':
                    f.write(f"- **Out of Sync:** {check_data.get('out_of_sync', 0)}\n")
                    f.write(f"- **Missing Docs:** {check_data.get('missing_docs', 0)}\n")
                    f.write(f"- **Stale Docs:** {check_data.get('stale_docs', 0)}\n")
                elif check_name == 'phase_gate':
                    f.write(f"- **Phase:** {check_data.get('phase', 'unknown')}\n")
                    f.write(f"- **Criteria Passed:** {check_data.get('criteria_passed', 0)}/{check_data.get('criteria_total', 0)}\n")
                    f.write(f"- **Blockers:** {check_data.get('blockers', 0)}\n")
                elif check_name == 'performance':
                    f.write(f"- **Response Time:** {check_data.get('response_time', 0)}ms\n")
                    f.write(f"- **Throughput:** {check_data.get('throughput', 0)} req/s\n")
                    f.write(f"- **Error Rate:** {check_data.get('error_rate', 0)}%\n")
                elif check_name == 'security':
                    f.write(f"- **Total Vulnerabilities:** {check_data.get('vulnerabilities', 0)}\n")
                    f.write(f"- **High Severity:** {check_data.get('high_severity', 0)}\n")
                    f.write(f"- **Medium Severity:** {check_data.get('medium_severity', 0)}\n")
                    f.write(f"- **Low Severity:** {check_data.get('low_severity', 0)}\n")
                
                f.write("\n")
            
            # Metrics
            f.write("## Metrics\n\n")
            for metric_name, metric_value in self.report['metrics'].items():
                f.write(f"- **{metric_name.replace('_', ' ').title()}:** {metric_value}\n")
            f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            if self.report['recommendations']:
                for i, rec in enumerate(self.report['recommendations'], 1):
                    priority_icon = "🔴" if rec['priority'] == 'CRITICAL' else "🟡" if rec['priority'] == 'HIGH' else "🟠" if rec['priority'] == 'MEDIUM' else "🟢"
                    f.write(f"### {i}. {priority_icon} {rec['category']} - {rec['priority']}\n")
                    f.write(f"**Issue:** {rec['message']}\n\n")
                    f.write(f"**Action:** {rec['action']}\n\n")
            else:
                f.write("No recommendations at this time.\n")
    
    def generate_json_report(self):
        """Generate JSON report"""
        report_file = self.summary_dir / 'operational_excellence_report.json'
        
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2)
    
    def generate_dashboard_data(self):
        """Generate dashboard data for visualization"""
        dashboard_data = {
            'timestamp': self.report['timestamp'],
            'overall_status': self.report['overall_status'],
            'check_statuses': {
                check_name: check_data.get('status', 'UNKNOWN')
                for check_name, check_data in self.report['checks'].items()
            },
            'metrics': self.report['metrics'],
            'recommendations_count': len(self.report['recommendations']),
            'critical_recommendations': len([
                r for r in self.report['recommendations'] 
                if r['priority'] == 'CRITICAL'
            ])
        }
        
        dashboard_file = self.summary_dir / 'dashboard_data.json'
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
    
    def print_summary(self):
        """Print summary to console"""
        print(f"\n📊 AL-0 Operational Excellence Summary")
        print(f"Timestamp: {self.report['timestamp']}")
        print(f"Overall Status: {self.report['overall_status']}")
        
        print(f"\n📋 Check Results:")
        for check_name, check_data in self.report['checks'].items():
            status_icon = "✅" if check_data.get('status') == 'PASS' else "❌"
            print(f"  {status_icon} {check_name.replace('_', ' ').title()}: {check_data.get('status', 'UNKNOWN')}")
        
        print(f"\n📈 Key Metrics:")
        for metric_name, metric_value in self.report['metrics'].items():
            print(f"  {metric_name.replace('_', ' ').title()}: {metric_value}")
        
        print(f"\n💡 Recommendations: {len(self.report['recommendations'])}")
        for rec in self.report['recommendations'][:3]:  # Show top 3
            priority_icon = "🔴" if rec['priority'] == 'CRITICAL' else "🟡" if rec['priority'] == 'HIGH' else "🟠"
            print(f"  {priority_icon} {rec['category']}: {rec['message']}")
        
        if len(self.report['recommendations']) > 3:
            print(f"  ... and {len(self.report['recommendations']) - 3} more")

def main():
    """Main function"""
    generator = SummaryReportGenerator()
    generator.generate_summary()

if __name__ == '__main__':
    main()
