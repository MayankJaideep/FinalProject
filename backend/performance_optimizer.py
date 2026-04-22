#!/usr/bin/env python3

import time
import os
from typing import Dict, Any

try:
    import streamlit as st
    _HAS_STREAMLIT = True
except ImportError:
    _HAS_STREAMLIT = False

class PerformanceMonitor:
    """Monitor and optimize app performance"""
    
    def __init__(self):
        self.start_time = None
        self.metrics = {
            "api_calls": 0,
            "vector_searches": 0,
            "ml_predictions": 0,
            "response_times": []
        }
    
    def start_timer(self):
        self.start_time = time.process_time()
    
    def end_timer(self, operation: str):
        if self.start_time:
            elapsed = time.process_time() - self.start_time
            self.metrics["response_times"].append(elapsed)
            self.metrics[operation] = self.metrics.get(operation, 0) + 1
            return elapsed
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        if self.metrics["response_times"]:
            avg_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
        else:
            avg_time = 0
        
        return {
            "avg_response_time": f"{avg_time:.2f}s",
            "total_operations": sum(self.metrics["response_times"]),
            "api_calls": self.metrics.get("api_calls", 0),
            "vector_searches": self.metrics.get("vector_searches", 0),
            "ml_predictions": self.metrics.get("ml_predictions", 0)
        }

# Global performance monitor
perf_monitor = PerformanceMonitor()

def display_performance_stats():
    """Display performance metrics in the app"""
    if not _HAS_STREAMLIT:
        return
    stats = perf_monitor.get_stats()
    
    with st.expander("📊 Performance Stats", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Response Time", stats["avg_response_time"])
        with col2:
            st.metric("API Calls", stats["api_calls"])
        with col3:
            st.metric("ML Predictions", stats["ml_predictions"])
        
        st.write(f"Vector Searches: {stats['vector_searches']}")
        st.write(f"Total Operations: {stats['total_operations']}")

def optimize_api_calls():
    """Optimize API call patterns"""
    if not _HAS_STREAMLIT:
        return {}
    # Cache API responses
    if "api_cache" not in st.session_state:
        st.session_state.api_cache = {}
    
    return st.session_state.api_cache

def cached_api_call(api_func, cache_key: str, *args, **kwargs):
    """Cache API calls to improve performance"""
    cache = optimize_api_calls()
    
    if cache_key in cache:
        perf_monitor.end_timer("api_calls")
        return cache[cache_key]
    
    result = api_func(*args, **kwargs)
    cache[cache_key] = result
    perf_monitor.metrics["api_calls"] += 1
    
    return result
