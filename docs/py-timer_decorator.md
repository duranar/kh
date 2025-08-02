---
title: Python Timer Decorator for Performance Logging
description: ""
---
# **Python Decorator Timer Template**

A reusable Python [decorator](https://peps.python.org/pep-0318/) to measure and log the execution time of functions and class methods. Does not meddle with the actual function it measures.

### Timer Decorator Template
```python
import logging
import time
import functools

# Configure a basic logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_timing(func):
    """
    A decorator that logs the execution time of a function.
    If the function is a method of a class, it includes the class name.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        log_prefix = func.__name__
        if args and hasattr(args[0], '__class__') and hasattr(args[0], func.__name__):
            class_name = args[0].__class__.__name__
            log_prefix = f"{class_name}.{func.__name__}"
        
        logging.info(f"(decorator) Starting '{log_prefix}'...")
        start_timer = time.perf_counter()
        result = func(*args, **kwargs)
        end_timer = time.perf_counter()
        duration = end_timer - start_timer
        logging.info(f"(decorator) Finished '{log_prefix}' in {duration:.4f} seconds.")
        return result
    return wrapper
```


### Usage Example

```python
# 1. A standalone function
@log_timing
def standalone_function(duration):
    logging.info(f"--> Standalone function is doing some work for {duration}s...")
    time.sleep(duration)

@log_timing
def worker_task(name):
    logging.info(f"--> Task {name} is doing some work.")
    time.sleep(1)
    
# 2. A class with decorated methods
class SomeClass:
    def __init__(self, source):
        self.source = source

    @log_timing
    def fetch_data(self):
        logging.info(f"--> Fetching data from {self.source}...")
        time.sleep(1.2)
        return "fetch_data complete"
    
    @log_timing
    def analyze_data(self, model_name):
        logging.info(f"--> Analyzing data with model '{model_name}'...")
        time.sleep(0.8)
        return "analyze_data complete"

if __name__ == "__main__":
    standalone_function(0.5)
    
    import threading
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker_task, args=(f"T-{i}",), name=f"Thread-{i}")
        t.start()

    sc = SomeClass(source="database")
    sc.fetch_data()
    sc.analyze_data(model_name="some_model")
```