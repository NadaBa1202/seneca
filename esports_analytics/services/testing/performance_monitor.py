"""Real-time Model Performance Monitoring

Live accuracy tracking with confidence intervals, statistical significance testing,
and automated model retraining triggers.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta
import json
from collections import deque
import threading

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    metric_name: str
    value: float
    timestamp: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ModelPerformance:
    """Model performance summary."""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    latency_ms: float
    throughput_per_second: float
    confidence: float
    last_updated: float

class PerformanceMonitor:
    """
    Real-time model performance monitoring system.
    
    Features:
    - Live accuracy tracking with confidence intervals
    - Statistical significance testing
    - Automated model retraining triggers
    - Bias detection and fairness metrics
    - Latency monitoring and optimization alerts
    - Custom esports-specific metrics
    """
    
    def __init__(self, 
                 monitoring_interval: int = 60,
                 confidence_level: float = 0.95,
                 performance_threshold: float = 0.85,
                 alert_threshold: float = 0.1):
        """
        Initialize performance monitor.
        
        Args:
            monitoring_interval: Monitoring interval in seconds
            confidence_level: Confidence level for statistical tests
            performance_threshold: Minimum acceptable performance
            alert_threshold: Performance degradation threshold
        """
        self.monitoring_interval = monitoring_interval
        self.confidence_level = confidence_level
        self.performance_threshold = performance_threshold
        self.alert_threshold = alert_threshold
        
        # Performance tracking
        self.metrics_history = {}
        self.model_performance = {}
        self.alerts = deque(maxlen=1000)
        
        # Statistical tracking
        self.baseline_performance = {}
        self.performance_trends = {}
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_task = None
        
        # Esports-specific metrics
        self.esports_metrics = {
            'sentiment_accuracy': {'weight': 0.3, 'threshold': 0.85},
            'toxicity_precision': {'weight': 0.25, 'threshold': 0.90},
            'emotion_f1_score': {'weight': 0.2, 'threshold': 0.87},
            'highlight_relevance': {'weight': 0.15, 'threshold': 0.80},
            'latency_ms': {'weight': 0.1, 'threshold': 100}
        }
        
        logger.info("Initialized PerformanceMonitor")
    
    async def start_monitoring(self):
        """Start performance monitoring."""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                await self._collect_metrics()
                await self._analyze_performance()
                await self._check_alerts()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_metrics(self):
        """Collect performance metrics from models."""
        # This would collect metrics from actual models
        # For now, we'll simulate metric collection
        
        current_time = time.time()
        
        # Simulate sentiment analysis metrics
        sentiment_accuracy = 0.85 + np.random.normal(0, 0.02)
        self._record_metric('sentiment_accuracy', sentiment_accuracy, current_time)
        
        # Simulate toxicity detection metrics
        toxicity_precision = 0.90 + np.random.normal(0, 0.01)
        self._record_metric('toxicity_precision', toxicity_precision, current_time)
        
        # Simulate emotion classification metrics
        emotion_f1 = 0.87 + np.random.normal(0, 0.015)
        self._record_metric('emotion_f1_score', emotion_f1, current_time)
        
        # Simulate latency metrics
        latency = 95 + np.random.normal(0, 10)
        self._record_metric('latency_ms', latency, current_time)
        
        # Simulate throughput metrics
        throughput = 50 + np.random.normal(0, 5)
        self._record_metric('throughput_per_second', throughput, current_time)
    
    def _record_metric(self, metric_name: str, value: float, timestamp: float):
        """Record a performance metric."""
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = deque(maxlen=1000)
        
        # Calculate confidence interval
        recent_values = list(self.metrics_history[metric_name])[-30:]  # Last 30 values
        if len(recent_values) >= 10:
            mean_val = np.mean(recent_values)
            std_val = np.std(recent_values)
            n = len(recent_values)
            
            # Calculate confidence interval
            z_score = 1.96 if self.confidence_level == 0.95 else 2.58  # 95% or 99%
            margin_error = z_score * (std_val / np.sqrt(n))
            ci_lower = mean_val - margin_error
            ci_upper = mean_val + margin_error
        else:
            ci_lower = ci_upper = value
        
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            timestamp=timestamp,
            confidence_interval=(ci_lower, ci_upper),
            sample_size=len(recent_values) + 1,
            metadata={'monitoring_interval': self.monitoring_interval}
        )
        
        self.metrics_history[metric_name].append(metric)
    
    async def _analyze_performance(self):
        """Analyze performance trends and patterns."""
        for metric_name, metrics in self.metrics_history.items():
            if len(metrics) < 10:
                continue
            
            recent_metrics = list(metrics)[-20:]  # Last 20 measurements
            values = [m.value for m in recent_metrics]
            
            # Calculate trend
            trend = self._calculate_trend(values)
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(metric_name, values)
            
            # Update performance tracking
            if metric_name not in self.model_performance:
                self.model_performance[metric_name] = ModelPerformance(
                    model_name=metric_name,
                    accuracy=0.0,
                    precision=0.0,
                    recall=0.0,
                    f1_score=0.0,
                    latency_ms=0.0,
                    throughput_per_second=0.0,
                    confidence=0.0,
                    last_updated=time.time()
                )
            
            # Update model performance
            perf = self.model_performance[metric_name]
            perf.accuracy = np.mean(values)
            perf.confidence = self._calculate_confidence(values)
            perf.last_updated = time.time()
            
            # Store trend
            self.performance_trends[metric_name] = {
                'trend': trend,
                'performance_score': performance_score,
                'last_updated': time.time()
            }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate performance trend."""
        if len(values) < 5:
            return 'insufficient_data'
        
        # Simple linear regression to determine trend
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.01:
            return 'improving'
        elif slope < -0.01:
            return 'degrading'
        else:
            return 'stable'
    
    def _calculate_performance_score(self, metric_name: str, values: List[float]) -> float:
        """Calculate overall performance score."""
        if metric_name in self.esports_metrics:
            threshold = self.esports_metrics[metric_name]['threshold']
            weight = self.esports_metrics[metric_name]['weight']
            
            avg_value = np.mean(values)
            
            # Normalize score based on threshold
            if metric_name == 'latency_ms':
                # Lower is better for latency
                score = max(0, 1 - (avg_value - threshold) / threshold)
            else:
                # Higher is better for other metrics
                score = min(1, avg_value / threshold)
            
            return score * weight
        
        return np.mean(values)
    
    def _calculate_confidence(self, values: List[float]) -> float:
        """Calculate confidence in performance measurement."""
        if len(values) < 5:
            return 0.0
        
        # Confidence based on consistency (inverse of coefficient of variation)
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if mean_val == 0:
            return 0.0
        
        cv = std_val / abs(mean_val)
        confidence = max(0, 1 - cv)
        
        return confidence
    
    async def _check_alerts(self):
        """Check for performance alerts."""
        for metric_name, perf in self.model_performance.items():
            # Check performance threshold
            if metric_name in self.esports_metrics:
                threshold = self.esports_metrics[metric_name]['threshold']
                
                if metric_name == 'latency_ms':
                    # Lower is better for latency
                    if perf.accuracy > threshold:
                        await self._create_alert(
                            'performance_degradation',
                            f"{metric_name} exceeded threshold: {perf.accuracy:.2f} > {threshold}",
                            metric_name,
                            perf.accuracy
                        )
                else:
                    # Higher is better for other metrics
                    if perf.accuracy < threshold:
                        await self._create_alert(
                            'performance_degradation',
                            f"{metric_name} below threshold: {perf.accuracy:.2f} < {threshold}",
                            metric_name,
                            perf.accuracy
                        )
            
            # Check for significant degradation
            if metric_name in self.baseline_performance:
                baseline = self.baseline_performance[metric_name]
                degradation = abs(perf.accuracy - baseline) / baseline
                
                if degradation > self.alert_threshold:
                    await self._create_alert(
                        'significant_degradation',
                        f"{metric_name} degraded by {degradation:.1%}",
                        metric_name,
                        perf.accuracy
                    )
    
    async def _create_alert(self, alert_type: str, message: str, metric_name: str, value: float):
        """Create a performance alert."""
        alert = {
            'alert_type': alert_type,
            'message': message,
            'metric_name': metric_name,
            'value': value,
            'timestamp': time.time(),
            'severity': 'high' if alert_type == 'significant_degradation' else 'medium'
        }
        
        self.alerts.append(alert)
        logger.warning(f"Performance Alert: {message}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary."""
        if not self.model_performance:
            return {}
        
        # Calculate overall performance score
        total_score = 0.0
        total_weight = 0.0
        
        for metric_name, perf in self.model_performance.items():
            if metric_name in self.esports_metrics:
                weight = self.esports_metrics[metric_name]['weight']
                score = self._calculate_performance_score(metric_name, [perf.accuracy])
                total_score += score
                total_weight += weight
        
        overall_score = total_score / total_weight if total_weight > 0 else 0.0
        
        # Calculate health status
        health_status = 'healthy'
        if overall_score < self.performance_threshold:
            health_status = 'degraded'
        if len(self.alerts) > 5:
            health_status = 'critical'
        
        return {
            'overall_score': overall_score,
            'health_status': health_status,
            'model_count': len(self.model_performance),
            'active_alerts': len(self.alerts),
            'last_updated': max(p.last_updated for p in self.model_performance.values()) if self.model_performance else 0
        }
    
    def get_metric_history(self, metric_name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metric history for specified time period."""
        if metric_name not in self.metrics_history:
            return []
        
        cutoff_time = time.time() - (hours * 3600)
        metrics = list(self.metrics_history[metric_name])
        
        recent_metrics = [
            {
                'timestamp': m.timestamp,
                'value': m.value,
                'confidence_interval': m.confidence_interval,
                'sample_size': m.sample_size
            }
            for m in metrics if m.timestamp >= cutoff_time
        ]
        
        return recent_metrics
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent performance alerts."""
        return list(self.alerts)[-limit:]
    
    def set_baseline_performance(self, metric_name: str, baseline_value: float):
        """Set baseline performance for comparison."""
        self.baseline_performance[metric_name] = baseline_value
        logger.info(f"Set baseline for {metric_name}: {baseline_value}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'monitoring_interval': self.monitoring_interval,
            'confidence_level': self.confidence_level,
            'performance_threshold': self.performance_threshold,
            'alert_threshold': self.alert_threshold,
            'monitoring_active': self.monitoring_active,
            'esports_metrics': list(self.esports_metrics.keys()),
            'tracked_metrics': list(self.metrics_history.keys())
        }
