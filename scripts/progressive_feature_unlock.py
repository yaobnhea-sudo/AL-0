#!/usr/bin/env python3
"""
AL-0 Progressive Feature Unlock System
Ties new ML models and heavy features to phases to respect memory and startup constraints
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import psutil
import GPUtil

class ProgressiveFeatureUnlock:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / 'config'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.feature_config = self.load_feature_config()
        self.hardware_profile = self.detect_hardware_profile()
        self.current_phase = self.detect_current_phase()
        
        self.unlock_results = {
            'timestamp': datetime.now().isoformat(),
            'current_phase': self.current_phase,
            'hardware_profile': self.hardware_profile,
            'available_features': [],
            'locked_features': [],
            'resource_usage': {},
            'recommendations': []
        }
    
    def load_feature_config(self) -> Dict[str, Any]:
        """Load feature configuration with phase and resource requirements"""
        default_config = {
            'phases': {
                '1': {  # MVP Phase
                    'name': 'MVP Foundation',
                    'max_memory_mb': 2048,
                    'max_startup_time_s': 120,
                    'max_models': 1,
                    'max_services': 3,
                    'features': {
                        'basic_inference': {
                            'enabled': True,
                            'memory_required_mb': 512,
                            'startup_time_s': 30,
                            'models': ['yolov8n'],
                            'services': ['backend', 'frontend', 'redis']
                        },
                        'simple_3d_viewer': {
                            'enabled': True,
                            'memory_required_mb': 256,
                            'startup_time_s': 20,
                            'models': [],
                            'services': ['frontend']
                        },
                        'basic_telemetry': {
                            'enabled': True,
                            'memory_required_mb': 128,
                            'startup_time_s': 10,
                            'models': [],
                            'services': ['backend']
                        }
                    }
                },
                '2': {  # Core Enhancement
                    'name': 'Core Enhancement',
                    'max_memory_mb': 4096,
                    'max_startup_time_s': 180,
                    'max_models': 3,
                    'max_services': 5,
                    'features': {
                        'advanced_inference': {
                            'enabled': True,
                            'memory_required_mb': 1024,
                            'startup_time_s': 60,
                            'models': ['yolov8s', 'deeplab'],
                            'services': ['backend', 'postgres']
                        },
                        'real_time_simulator': {
                            'enabled': True,
                            'memory_required_mb': 512,
                            'startup_time_s': 40,
                            'models': [],
                            'services': ['frontend', 'websocket']
                        },
                        'model_optimization': {
                            'enabled': True,
                            'memory_required_mb': 256,
                            'startup_time_s': 20,
                            'models': [],
                            'services': ['backend']
                        },
                        'advanced_monitoring': {
                            'enabled': True,
                            'memory_required_mb': 128,
                            'startup_time_s': 15,
                            'models': [],
                            'services': ['prometheus', 'grafana']
                        }
                    }
                },
                '3': {  # Production Scale
                    'name': 'Production Scale',
                    'max_memory_mb': 8192,
                    'max_startup_time_s': 300,
                    'max_models': 5,
                    'max_services': 8,
                    'features': {
                        'multi_model_inference': {
                            'enabled': True,
                            'memory_required_mb': 2048,
                            'startup_time_s': 120,
                            'models': ['yolov8m', 'deeplab', 'pointpillars'],
                            'services': ['backend', 'postgres', 'redis']
                        },
                        'advanced_3d_visualization': {
                            'enabled': True,
                            'memory_required_mb': 1024,
                            'startup_time_s': 80,
                            'models': [],
                            'services': ['frontend', 'websocket']
                        },
                        'distributed_processing': {
                            'enabled': True,
                            'memory_required_mb': 512,
                            'startup_time_s': 60,
                            'models': [],
                            'services': ['celery', 'redis']
                        },
                        'comprehensive_monitoring': {
                            'enabled': True,
                            'memory_required_mb': 256,
                            'startup_time_s': 30,
                            'models': [],
                            'services': ['prometheus', 'grafana', 'elasticsearch']
                        },
                        'auto_scaling': {
                            'enabled': True,
                            'memory_required_mb': 128,
                            'startup_time_s': 20,
                            'models': [],
                            'services': ['kubernetes']
                        }
                    }
                },
                '4': {  # Enterprise
                    'name': 'Enterprise',
                    'max_memory_mb': 16384,
                    'max_startup_time_s': 600,
                    'max_models': 10,
                    'max_services': 12,
                    'features': {
                        'enterprise_ml_suite': {
                            'enabled': True,
                            'memory_required_mb': 4096,
                            'startup_time_s': 240,
                            'models': ['yolov8l', 'deeplab', 'pointpillars', 'transformer'],
                            'services': ['backend', 'postgres', 'redis', 'mlflow']
                        },
                        'advanced_analytics': {
                            'enabled': True,
                            'memory_required_mb': 2048,
                            'startup_time_s': 120,
                            'models': [],
                            'services': ['elasticsearch', 'kibana', 'spark']
                        },
                        'multi_tenant_support': {
                            'enabled': True,
                            'memory_required_mb': 1024,
                            'startup_time_s': 60,
                            'models': [],
                            'services': ['keycloak', 'vault']
                        },
                        'enterprise_security': {
                            'enabled': True,
                            'memory_required_mb': 512,
                            'startup_time_s': 30,
                            'models': [],
                            'services': ['vault', 'cert-manager']
                        },
                        'global_deployment': {
                            'enabled': True,
                            'memory_required_mb': 256,
                            'startup_time_s': 20,
                            'models': [],
                            'services': ['istio', 'cert-manager']
                        }
                    }
                }
            },
            'hardware_profiles': {
                'minimal': {
                    'max_memory_mb': 1024,
                    'max_startup_time_s': 60,
                    'gpu_available': False,
                    'cpu_cores': 2,
                    'recommended_phase': '1'
                },
                'standard': {
                    'max_memory_mb': 4096,
                    'max_startup_time_s': 180,
                    'gpu_available': False,
                    'cpu_cores': 4,
                    'recommended_phase': '2'
                },
                'gpu_standard': {
                    'max_memory_mb': 8192,
                    'max_startup_time_s': 300,
                    'gpu_available': True,
                    'gpu_memory_mb': 4096,
                    'cpu_cores': 4,
                    'recommended_phase': '3'
                },
                'enterprise': {
                    'max_memory_mb': 16384,
                    'max_startup_time_s': 600,
                    'gpu_available': True,
                    'gpu_memory_mb': 8192,
                    'cpu_cores': 8,
                    'recommended_phase': '4'
                }
            }
        }
        
        # Try to load from file, fallback to default
        config_file = self.config_dir / 'feature_unlock_config.json'
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Save default config
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def detect_hardware_profile(self) -> str:
        """Detect current hardware profile"""
        # Get system specs
        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_cores = psutil.cpu_count()
        gpu_available = False
        gpu_memory_gb = 0
        
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_available = True
                gpu_memory_gb = gpus[0].memoryTotal / 1024
        except:
            pass
        
        # Determine profile based on specs
        if memory_gb >= 16 and gpu_available and gpu_memory_gb >= 8:
            return 'enterprise'
        elif memory_gb >= 8 and gpu_available and gpu_memory_gb >= 4:
            return 'gpu_standard'
        elif memory_gb >= 4 and cpu_cores >= 4:
            return 'standard'
        else:
            return 'minimal'
    
    def detect_current_phase(self) -> str:
        """Detect current development phase"""
        # Check for phase indicators in the project
        phase_indicators = {
            '1': ['docker-compose.mvp.yml', 'requirements.mvp.txt'],
            '2': ['docker-compose.yml', 'prometheus.yml'],
            '3': ['docker-compose.prod.yml', 'kubernetes'],
            '4': ['enterprise', 'vault', 'keycloak']
        }
        
        for phase, indicators in phase_indicators.items():
            phase_score = 0
            for indicator in indicators:
                if self.project_root.rglob(f'*{indicator}*'):
                    phase_score += 1
            
            if phase_score >= len(indicators) // 2:
                return phase
        
        return '1'  # Default to MVP phase
    
    def analyze_feature_unlock(self) -> Dict[str, Any]:
        """Analyze which features should be unlocked based on current phase and hardware"""
        print(f"🔓 Analyzing feature unlock for Phase {self.current_phase}...")
        
        # Get current phase configuration
        phase_config = self.feature_config['phases'].get(self.current_phase, {})
        hardware_config = self.feature_config['hardware_profiles'].get(self.hardware_profile, {})
        
        # Calculate resource usage
        resource_usage = self.calculate_current_resource_usage()
        
        # Determine available features
        available_features = []
        locked_features = []
        
        for feature_name, feature_config in phase_config.get('features', {}).items():
            if self.can_unlock_feature(feature_name, feature_config, phase_config, hardware_config, resource_usage):
                available_features.append({
                    'name': feature_name,
                    'config': feature_config,
                    'unlock_reason': 'phase_and_resources_available'
                })
            else:
                locked_features.append({
                    'name': feature_name,
                    'config': feature_config,
                    'lock_reason': self.get_lock_reason(feature_name, feature_config, phase_config, hardware_config, resource_usage)
                })
        
        # Generate recommendations
        recommendations = self.generate_unlock_recommendations(available_features, locked_features, phase_config, hardware_config)
        
        self.unlock_results.update({
            'available_features': available_features,
            'locked_features': locked_features,
            'resource_usage': resource_usage,
            'recommendations': recommendations
        })
        
        return self.unlock_results
    
    def calculate_current_resource_usage(self) -> Dict[str, Any]:
        """Calculate current resource usage"""
        resource_usage = {
            'memory_used_mb': 0,
            'startup_time_s': 0,
            'models_loaded': 0,
            'services_running': 0,
            'gpu_memory_used_mb': 0
        }
        
        try:
            # Get memory usage
            memory = psutil.virtual_memory()
            resource_usage['memory_used_mb'] = memory.used / (1024 * 1024)
            
            # Get GPU memory usage
            if self.hardware_profile in ['gpu_standard', 'enterprise']:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        resource_usage['gpu_memory_used_mb'] = gpus[0].memoryUsed
                except:
                    pass
            
            # Count running services (simplified)
            try:
                result = subprocess.run(['docker', 'ps', '--format', 'json'], capture_output=True, text=True)
                if result.returncode == 0:
                    services = [json.loads(line) for line in result.stdout.strip().split('\n') if line]
                    resource_usage['services_running'] = len(services)
            except:
                pass
            
        except Exception as e:
            print(f"⚠️  Error calculating resource usage: {e}")
        
        return resource_usage
    
    def can_unlock_feature(self, feature_name: str, feature_config: Dict, 
                          phase_config: Dict, hardware_config: Dict, 
                          resource_usage: Dict) -> bool:
        """Check if a feature can be unlocked"""
        # Check phase requirements
        if not feature_config.get('enabled', False):
            return False
        
        # Check memory requirements
        required_memory = feature_config.get('memory_required_mb', 0)
        available_memory = hardware_config.get('max_memory_mb', 0) - resource_usage.get('memory_used_mb', 0)
        if required_memory > available_memory:
            return False
        
        # Check startup time requirements
        required_startup = feature_config.get('startup_time_s', 0)
        available_startup = hardware_config.get('max_startup_time_s', 0) - resource_usage.get('startup_time_s', 0)
        if required_startup > available_startup:
            return False
        
        # Check model requirements
        required_models = len(feature_config.get('models', []))
        available_models = phase_config.get('max_models', 0) - resource_usage.get('models_loaded', 0)
        if required_models > available_models:
            return False
        
        # Check service requirements
        required_services = len(feature_config.get('services', []))
        available_services = phase_config.get('max_services', 0) - resource_usage.get('services_running', 0)
        if required_services > available_services:
            return False
        
        # Check GPU requirements
        if feature_config.get('requires_gpu', False) and not hardware_config.get('gpu_available', False):
            return False
        
        return True
    
    def get_lock_reason(self, feature_name: str, feature_config: Dict,
                       phase_config: Dict, hardware_config: Dict,
                       resource_usage: Dict) -> str:
        """Get reason why a feature is locked"""
        # Check memory requirements
        required_memory = feature_config.get('memory_required_mb', 0)
        available_memory = hardware_config.get('max_memory_mb', 0) - resource_usage.get('memory_used_mb', 0)
        if required_memory > available_memory:
            return f"Insufficient memory: requires {required_memory}MB, available {available_memory}MB"
        
        # Check startup time requirements
        required_startup = feature_config.get('startup_time_s', 0)
        available_startup = hardware_config.get('max_startup_time_s', 0) - resource_usage.get('startup_time_s', 0)
        if required_startup > available_startup:
            return f"Startup time too long: requires {required_startup}s, available {available_startup}s"
        
        # Check model requirements
        required_models = len(feature_config.get('models', []))
        available_models = phase_config.get('max_models', 0) - resource_usage.get('models_loaded', 0)
        if required_models > available_models:
            return f"Too many models: requires {required_models}, available {available_models}"
        
        # Check service requirements
        required_services = len(feature_config.get('services', []))
        available_services = phase_config.get('max_services', 0) - resource_usage.get('services_running', 0)
        if required_services > available_services:
            return f"Too many services: requires {required_services}, available {available_services}"
        
        # Check GPU requirements
        if feature_config.get('requires_gpu', False) and not hardware_config.get('gpu_available', False):
            return "GPU required but not available"
        
        return "Feature disabled in current phase"
    
    def generate_unlock_recommendations(self, available_features: List[Dict], 
                                      locked_features: List[Dict],
                                      phase_config: Dict, hardware_config: Dict) -> List[Dict[str, Any]]:
        """Generate recommendations for feature unlock"""
        recommendations = []
        
        # Memory recommendations
        memory_usage = self.unlock_results['resource_usage'].get('memory_used_mb', 0)
        max_memory = hardware_config.get('max_memory_mb', 0)
        memory_utilization = (memory_usage / max_memory) * 100 if max_memory > 0 else 0
        
        if memory_utilization > 80:
            recommendations.append({
                'type': 'memory',
                'priority': 'high',
                'message': f'Memory utilization is {memory_utilization:.1f}%. Consider upgrading hardware or optimizing memory usage.',
                'action': 'Upgrade RAM or optimize existing features to free up memory.'
            })
        
        # Phase progression recommendations
        if len(locked_features) > len(available_features):
            recommendations.append({
                'type': 'phase_progression',
                'priority': 'medium',
                'message': f'{len(locked_features)} features are locked. Consider progressing to next phase.',
                'action': 'Complete current phase requirements and move to next phase.'
            })
        
        # Hardware upgrade recommendations
        if self.hardware_profile == 'minimal' and len(locked_features) > 0:
            recommendations.append({
                'type': 'hardware_upgrade',
                'priority': 'medium',
                'message': 'Current hardware profile is minimal. Many features are locked due to hardware constraints.',
                'action': 'Consider upgrading to standard or GPU-enabled hardware.'
            })
        
        # Feature optimization recommendations
        heavy_features = [f for f in locked_features if f['config'].get('memory_required_mb', 0) > 1000]
        if heavy_features:
            recommendations.append({
                'type': 'optimization',
                'priority': 'low',
                'message': f'{len(heavy_features)} features are memory-intensive. Consider optimizing or using lighter alternatives.',
                'action': 'Optimize feature implementations or use progressive loading.'
            })
        
        return recommendations
    
    def generate_feature_config(self, target_phase: str = None) -> Dict[str, Any]:
        """Generate feature configuration for a specific phase"""
        if target_phase is None:
            target_phase = self.current_phase
        
        phase_config = self.feature_config['phases'].get(target_phase, {})
        hardware_config = self.feature_config['hardware_profiles'].get(self.hardware_profile, {})
        
        # Generate configuration based on available features
        config = {
            'phase': target_phase,
            'hardware_profile': self.hardware_profile,
            'enabled_features': [],
            'disabled_features': [],
            'resource_limits': {
                'max_memory_mb': min(phase_config.get('max_memory_mb', 0), hardware_config.get('max_memory_mb', 0)),
                'max_startup_time_s': min(phase_config.get('max_startup_time_s', 0), hardware_config.get('max_startup_time_s', 0)),
                'max_models': phase_config.get('max_models', 0),
                'max_services': phase_config.get('max_services', 0)
            }
        }
        
        # Analyze which features can be enabled
        resource_usage = self.calculate_current_resource_usage()
        
        for feature_name, feature_config in phase_config.get('features', {}).items():
            if self.can_unlock_feature(feature_name, feature_config, phase_config, hardware_config, resource_usage):
                config['enabled_features'].append(feature_name)
            else:
                config['disabled_features'].append(feature_name)
        
        return config
    
    def save_feature_config(self, config: Dict[str, Any]):
        """Save feature configuration to file"""
        config_file = self.project_root / 'config' / f'feature_config_phase_{config["phase"]}.json'
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"💾 Feature configuration saved to: {config_file}")
    
    def print_summary(self):
        """Print feature unlock summary"""
        print(f"\n🔓 AL-0 Progressive Feature Unlock Summary")
        print(f"Current Phase: {self.current_phase}")
        print(f"Hardware Profile: {self.hardware_profile}")
        
        # Available features
        available = self.unlock_results['available_features']
        print(f"\n✅ Available Features ({len(available)}):")
        for feature in available:
            print(f"  - {feature['name']}")
        
        # Locked features
        locked = self.unlock_results['locked_features']
        print(f"\n🔒 Locked Features ({len(locked)}):")
        for feature in locked:
            print(f"  - {feature['name']}: {feature['lock_reason']}")
        
        # Resource usage
        resource_usage = self.unlock_results['resource_usage']
        print(f"\n📊 Resource Usage:")
        print(f"  Memory: {resource_usage.get('memory_used_mb', 0):.0f} MB")
        print(f"  Services: {resource_usage.get('services_running', 0)}")
        print(f"  Models: {resource_usage.get('models_loaded', 0)}")
        
        # Recommendations
        recommendations = self.unlock_results['recommendations']
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                print(f"  {i}. {priority_icon} {rec['message']}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AL-0 Progressive Feature Unlock System')
    parser.add_argument('--phase', choices=['1', '2', '3', '4'],
                       help='Target phase for feature analysis')
    parser.add_argument('--generate-config', action='store_true',
                       help='Generate feature configuration file')
    parser.add_argument('--save', action='store_true',
                       help='Save analysis results to file')
    
    args = parser.parse_args()
    
    unlock_system = ProgressiveFeatureUnlock()
    
    print("🔓 Starting progressive feature unlock analysis...")
    print(f"Hardware Profile: {unlock_system.hardware_profile}")
    print(f"Current Phase: {unlock_system.current_phase}")
    
    # Run analysis
    results = unlock_system.analyze_feature_unlock()
    
    # Print summary
    unlock_system.print_summary()
    
    # Generate config if requested
    if args.generate_config:
        target_phase = args.phase or unlock_system.current_phase
        config = unlock_system.generate_feature_config(target_phase)
        unlock_system.save_feature_config(config)
    
    # Save results if requested
    if args.save:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = unlock_system.project_root / 'monitoring' / 'feature_unlock' / f'feature_unlock_{timestamp}.json'
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {results_file}")

if __name__ == '__main__':
    main()
