import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def performance_monitor(func):
    """Decorator to monitor function execution time"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.info(
                f"Function {func.__name__} executed in {execution_time:.2f}s"
            )
            
            # Log if execution took longer than threshold
            if execution_time > 30:  # More than 30 seconds
                logger.warning(
                    f"Function {func.__name__} took longer than expected: "
                    f"{execution_time:.2f}s"
                )
    
    return wrapper

# Example usage
@performance_monitor
def generate_video_step(step_name: str, data: dict) -> dict:
    """Generate a video step with performance monitoring"""
    # Implementation here
    return data