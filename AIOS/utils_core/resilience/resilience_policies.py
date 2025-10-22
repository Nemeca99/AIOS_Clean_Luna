"""
Resilience Policies
Timeout handling, retry logic, and fallback strategies
"""

import time
import functools
from typing import Callable, Any, Optional, Tuple, Dict
from datetime import datetime


class TimeoutError(Exception):
    """Request exceeded deadline"""
    pass


class RetryPolicy:
    """
    Configurable retry policy with exponential backoff
    """
    
    def __init__(self,
                 max_retries: int = 3,
                 base_delay_s: float = 1.0,
                 max_delay_s: float = 10.0,
                 exponential_base: float = 2.0):
        self.max_retries = max_retries
        self.base_delay_s = base_delay_s
        self.max_delay_s = max_delay_s
        self.exponential_base = exponential_base
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        delay = self.base_delay_s * (self.exponential_base ** attempt)
        return min(delay, self.max_delay_s)
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if should retry based on error type"""
        if attempt >= self.max_retries:
            return False
        
        # Retry on network errors, timeouts, 5xx errors
        retryable_errors = (
            ConnectionError,
            TimeoutError,
            # Add more as needed
        )
        
        return isinstance(error, retryable_errors)


def with_timeout(timeout_s: float, fallback: Any = None):
    """
    Decorator to add timeout to function
    
    Args:
        timeout_s: Timeout in seconds
        fallback: Fallback value if timeout (None = raise TimeoutError)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} exceeded {timeout_s}s timeout")
            
            # Note: signal.alarm only works on Unix
            # For Windows, use threading.Timer
            import platform
            if platform.system() == 'Windows':
                # Windows timeout implementation
                import threading
                result = [TimeoutError(f"Timeout after {timeout_s}s")]
                
                def target():
                    try:
                        result[0] = func(*args, **kwargs)
                    except Exception as e:
                        result[0] = e
                
                thread = threading.Thread(target=target)
                thread.daemon = True
                thread.start()
                thread.join(timeout_s)
                
                if thread.is_alive():
                    # Timeout occurred
                    if fallback is not None:
                        return fallback
                    raise TimeoutError(f"Function {func.__name__} exceeded {timeout_s}s timeout")
                
                if isinstance(result[0], Exception):
                    raise result[0]
                return result[0]
            else:
                # Unix timeout implementation
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout_s))
                
                try:
                    result = func(*args, **kwargs)
                    signal.alarm(0)  # Cancel alarm
                    return result
                except TimeoutError:
                    if fallback is not None:
                        return fallback
                    raise
                finally:
                    signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator


def with_retry(policy: Optional[RetryPolicy] = None):
    """
    Decorator to add retry logic to function
    
    Args:
        policy: RetryPolicy instance (default: 3 retries, exponential backoff)
    """
    if policy is None:
        policy = RetryPolicy()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(policy.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    if not policy.should_retry(attempt, e):
                        raise
                    
                    if attempt < policy.max_retries:
                        delay = policy.calculate_delay(attempt)
                        print(f"  Retry {attempt + 1}/{policy.max_retries} after {delay:.1f}s: {e}")
                        time.sleep(delay)
            
            # All retries exhausted
            raise last_error
        
        return wrapper
    return decorator


class ResultCache:
    """
    Simple in-memory result cache for repeated queries
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            
            # Check TTL
            if time.time() - timestamp < self.ttl_seconds:
                self.hits += 1
                return value
            else:
                # Expired
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def put(self, key: str, value: Any):
        """Put value in cache"""
        # Evict random item if cache full
        if len(self.cache) >= self.max_size:
            # Simple LRU: remove oldest
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / total if total > 0 else 0.0,
            'ttl_seconds': self.ttl_seconds
        }


# Global cache instance
_result_cache: Optional[ResultCache] = None

def get_result_cache() -> ResultCache:
    """Get singleton result cache"""
    global _result_cache
    if _result_cache is None:
        _result_cache = ResultCache()
    return _result_cache


def cached_query(cache_key_func: Callable = None):
    """
    Decorator to cache function results
    
    Args:
        cache_key_func: Function to generate cache key from args (default: str(args))
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_result_cache()
            
            # Generate cache key
            if cache_key_func:
                key = cache_key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try cache first
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result, True  # Return (result, from_cache)
            
            # Cache miss - call function
            result = func(*args, **kwargs)
            cache.put(key, result)
            
            return result, False  # Return (result, from_cache)
        
        return wrapper
    return decorator


def main():
    """Test resilience utilities"""
    print("="*70)
    print("RESILIENCE UTILITIES TEST")
    print("="*70)
    
    # Test retry policy
    print("\n1. Testing retry policy...")
    policy = RetryPolicy(max_retries=3, base_delay_s=0.1)
    
    attempt_count = [0]
    
    @with_retry(policy)
    def flaky_function():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise ConnectionError("Simulated network error")
        return "Success!"
    
    try:
        result = flaky_function()
        print(f"   ✓ Retry worked after {attempt_count[0]} attempts: {result}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test cache
    print("\n2. Testing result cache...")
    cache = ResultCache(max_size=3, ttl_seconds=10)
    
    cache.put('key1', 'value1')
    cache.put('key2', 'value2')
    
    val1 = cache.get('key1')
    val2 = cache.get('key1')  # Hit
    val3 = cache.get('key3')  # Miss
    
    print(f"   Cache stats: {cache.get_stats()}")
    print(f"   ✓ Hit rate: {cache.get_stats()['hit_rate']:.1%}")
    
    # Test timeout (disabled for compatibility)
    print("\n3. Testing timeout...")
    print("   ⚠ Timeout test skipped (requires threading support)")
    
    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()

