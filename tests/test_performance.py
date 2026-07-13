import pytest
from unittest.mock import patch, MagicMock

def test_performance_monitor_decorator():
    """Test the performance monitoring decorator"""
    
    # Import our decorated function
    from src.performance_monitor import performance_monitor
    
    @performance_monitor
    def slow_function():
        # Simulate a function that takes time
        import time
        time.sleep(0.1)
        return "done"
    
    # Test that it executes without error
    result = slow_function()
    assert result == "done"

def test_performance_monitor_with_long_execution():
    """Test performance monitoring with longer execution"""
    
    from src.performance_monitor import performance_monitor
    
    @performance_monitor
    def very_slow_function():
        # Simulate a long-running function
        import time
        time.sleep(0.2)
        return "completed"
    
    # Test that it executes without error
    result = very_slow_function()
    assert result == "completed"