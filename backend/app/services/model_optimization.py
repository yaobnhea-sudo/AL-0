import onnx
import onnxruntime as ort
import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import json
import time

logger = logging.getLogger(__name__)


class ModelOptimizer:
    """Handles ONNX model optimization and quantization"""
    
    def __init__(self):
        self.optimization_configs = {
            'basic': {
                'enable_constant_folding': True,
                'enable_eliminate_common_subexpression': True,
                'enable_eliminate_dead_code': True,
                'enable_fuse_bn_into_conv': True,
                'enable_fuse_consecutive_concats': True,
                'enable_fuse_consecutive_log_softmax': True,
                'enable_fuse_consecutive_reduce_unsqueeze': True,
                'enable_fuse_consecutive_squeezes': True,
                'enable_fuse_consecutive_transposes': True,
                'enable_fuse_matmul_add_bias_into_gemm': True,
                'enable_fuse_pad_into_conv': True,
                'enable_fuse_transpose_into_gemm': True,
                'enable_optimization': True,
                'enable_remove_invalid_nodes': True,
                'enable_shape_inference': True,
                'enable_simplify_ternary': True,
                'enable_split_predict': True,
                'enable_unsqueeze_elimination': True,
            },
            'aggressive': {
                'enable_constant_folding': True,
                'enable_eliminate_common_subexpression': True,
                'enable_eliminate_dead_code': True,
                'enable_fuse_bn_into_conv': True,
                'enable_fuse_consecutive_concats': True,
                'enable_fuse_consecutive_log_softmax': True,
                'enable_fuse_consecutive_reduce_unsqueeze': True,
                'enable_fuse_consecutive_squeezes': True,
                'enable_fuse_consecutive_transposes': True,
                'enable_fuse_matmul_add_bias_into_gemm': True,
                'enable_fuse_pad_into_conv': True,
                'enable_fuse_transpose_into_gemm': True,
                'enable_optimization': True,
                'enable_remove_invalid_nodes': True,
                'enable_shape_inference': True,
                'enable_simplify_ternary': True,
                'enable_split_predict': True,
                'enable_unsqueeze_elimination': True,
                'enable_quantization': True,
                'quantization_mode': 'static',
                'quantization_precision': 'int8',
            }
        }
    
    def optimize_model(self, model_path: str, optimization_level: str = 'basic') -> str:
        """Optimize an ONNX model"""
        try:
            # Load the model
            model = onnx.load(model_path)
            
            # Get optimization config
            config = self.optimization_configs.get(optimization_level, self.optimization_configs['basic'])
            
            # Optimize the model
            optimized_model = onnx.optimizer.optimize(model, config)
            
            # Save optimized model
            optimized_path = model_path.replace('.onnx', f'_optimized_{optimization_level}.onnx')
            onnx.save(optimized_model, optimized_path)
            
            logger.info(f"Model optimized and saved to {optimized_path}")
            return optimized_path
            
        except Exception as e:
            logger.error(f"Error optimizing model {model_path}: {e}")
            raise
    
    def quantize_model(self, model_path: str, quantization_type: str = 'dynamic') -> str:
        """Quantize an ONNX model for edge deployment"""
        try:
            from onnxruntime.quantization import quantize_dynamic, quantize_static, CalibrationDataReader
            
            # Create output path
            quantized_path = model_path.replace('.onnx', f'_quantized_{quantization_type}.onnx')
            
            if quantization_type == 'dynamic':
                # Dynamic quantization
                quantize_dynamic(
                    model_path,
                    quantized_path,
                    weight_type=ort.quantization.QuantType.QUInt8
                )
            elif quantization_type == 'static':
                # Static quantization requires calibration data
                class DummyDataReader(CalibrationDataReader):
                    def __init__(self, model_path: str):
                        self.model_path = model_path
                        self.data_loaded = False
                    
                    def get_next(self):
                        if not self.data_loaded:
                            # Generate dummy calibration data
                            # In production, use real calibration data
                            self.data_loaded = True
                            return {
                                'input': np.random.randn(1, 3, 640, 640).astype(np.float32)
                            }
                        return None
                
                quantize_static(
                    model_path,
                    quantized_path,
                    DummyDataReader(model_path),
                    weight_type=ort.quantization.QuantType.QUInt8,
                    activation_type=ort.quantization.QuantType.QUInt8
                )
            
            logger.info(f"Model quantized and saved to {quantized_path}")
            return quantized_path
            
        except Exception as e:
            logger.error(f"Error quantizing model {model_path}: {e}")
            raise
    
    def benchmark_model(self, model_path: str, input_shape: Tuple[int, ...], num_runs: int = 100) -> Dict[str, Any]:
        """Benchmark model performance"""
        try:
            # Create ONNX Runtime session
            session = ort.InferenceSession(model_path)
            
            # Get input details
            input_name = session.get_inputs()[0].name
            input_shape = (1,) + input_shape  # Add batch dimension
            
            # Warmup runs
            for _ in range(10):
                dummy_input = np.random.randn(*input_shape).astype(np.float32)
                session.run(None, {input_name: dummy_input})
            
            # Benchmark runs
            times = []
            for _ in range(num_runs):
                dummy_input = np.random.randn(*input_shape).astype(np.float32)
                start_time = time.time()
                session.run(None, {input_name: dummy_input})
                end_time = time.time()
                times.append((end_time - start_time) * 1000)  # Convert to milliseconds
            
            # Calculate statistics
            times = np.array(times)
            stats = {
                'mean_latency_ms': float(np.mean(times)),
                'median_latency_ms': float(np.median(times)),
                'p95_latency_ms': float(np.percentile(times, 95)),
                'p99_latency_ms': float(np.percentile(times, 99)),
                'min_latency_ms': float(np.min(times)),
                'max_latency_ms': float(np.max(times)),
                'std_latency_ms': float(np.std(times)),
                'throughput_fps': 1000.0 / float(np.mean(times)),
                'model_size_mb': Path(model_path).stat().st_size / (1024 * 1024),
                'input_shape': input_shape,
                'num_runs': num_runs
            }
            
            logger.info(f"Model benchmark completed: {stats['mean_latency_ms']:.2f}ms mean latency")
            return stats
            
        except Exception as e:
            logger.error(f"Error benchmarking model {model_path}: {e}")
            raise
    
    def compare_models(self, original_path: str, optimized_path: str, input_shape: Tuple[int, ...]) -> Dict[str, Any]:
        """Compare original and optimized model performance"""
        try:
            # Benchmark both models
            original_stats = self.benchmark_model(original_path, input_shape)
            optimized_stats = self.benchmark_model(optimized_path, input_shape)
            
            # Calculate improvements
            latency_improvement = ((original_stats['mean_latency_ms'] - optimized_stats['mean_latency_ms']) / 
                                 original_stats['mean_latency_ms']) * 100
            
            size_improvement = ((original_stats['model_size_mb'] - optimized_stats['model_size_mb']) / 
                              original_stats['model_size_mb']) * 100
            
            throughput_improvement = ((optimized_stats['throughput_fps'] - original_stats['throughput_fps']) / 
                                    original_stats['throughput_fps']) * 100
            
            comparison = {
                'original': original_stats,
                'optimized': optimized_stats,
                'improvements': {
                    'latency_improvement_percent': latency_improvement,
                    'size_improvement_percent': size_improvement,
                    'throughput_improvement_percent': throughput_improvement,
                    'latency_speedup': original_stats['mean_latency_ms'] / optimized_stats['mean_latency_ms'],
                    'size_reduction': original_stats['model_size_mb'] / optimized_stats['model_size_mb'],
                    'throughput_increase': optimized_stats['throughput_fps'] / original_stats['throughput_fps']
                }
            }
            
            logger.info(f"Model comparison completed: {latency_improvement:.1f}% latency improvement")
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            raise
    
    def get_model_info(self, model_path: str) -> Dict[str, Any]:
        """Get detailed information about an ONNX model"""
        try:
            model = onnx.load(model_path)
            
            # Get model metadata
            info = {
                'model_path': model_path,
                'model_size_mb': Path(model_path).stat().st_size / (1024 * 1024),
                'opset_version': model.opset_import[0].version if model.opset_import else None,
                'producer_name': model.producer_name,
                'producer_version': model.producer_version,
                'domain': model.domain,
                'model_version': model.model_version,
                'doc_string': model.doc_string,
                'inputs': [],
                'outputs': [],
                'nodes': len(model.graph.node),
                'initializers': len(model.graph.initializer)
            }
            
            # Get input information
            for input_tensor in model.graph.input:
                input_info = {
                    'name': input_tensor.name,
                    'type': str(input_tensor.type.tensor_type.elem_type),
                    'shape': [dim.dim_value for dim in input_tensor.type.tensor_type.shape.dim]
                }
                info['inputs'].append(input_info)
            
            # Get output information
            for output_tensor in model.graph.output:
                output_info = {
                    'name': output_tensor.name,
                    'type': str(output_tensor.type.tensor_type.elem_type),
                    'shape': [dim.dim_value for dim in output_tensor.type.tensor_type.shape.dim]
                }
                info['outputs'].append(output_info)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting model info for {model_path}: {e}")
            raise
    
    def validate_model(self, model_path: str) -> Dict[str, Any]:
        """Validate an ONNX model"""
        try:
            # Load and check model
            model = onnx.load(model_path)
            onnx.checker.check_model(model)
            
            # Test inference
            session = ort.InferenceSession(model_path)
            
            # Create dummy input
            input_name = session.get_inputs()[0].name
            input_shape = [1, 3, 640, 640]  # Default shape for most models
            dummy_input = np.random.randn(*input_shape).astype(np.float32)
            
            # Run inference
            start_time = time.time()
            outputs = session.run(None, {input_name: dummy_input})
            inference_time = (time.time() - start_time) * 1000
            
            validation_result = {
                'is_valid': True,
                'inference_time_ms': inference_time,
                'num_outputs': len(outputs),
                'output_shapes': [output.shape for output in outputs],
                'errors': []
            }
            
            logger.info(f"Model validation successful: {inference_time:.2f}ms inference time")
            return validation_result
            
        except Exception as e:
            logger.error(f"Model validation failed for {model_path}: {e}")
            return {
                'is_valid': False,
                'inference_time_ms': None,
                'num_outputs': 0,
                'output_shapes': [],
                'errors': [str(e)]
            }
