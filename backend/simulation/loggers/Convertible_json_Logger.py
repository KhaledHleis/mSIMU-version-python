import threading
import queue
import json
import time
from typing import Any
from datetime import datetime
import os
import copy

class LoggerThread:
    """
    Daemon thread that logs StringConvertible objects to JSON files.
    Uses a queue to handle logging requests asynchronously.
    """
    
    def __init__(self, log_dir: str = "logs", batch_size: int = 1):
        """
        Args:
            log_dir: Directory where log files will be saved
            batch_size: Number of items to accumulate before writing (default: 1 for immediate write)
        """
        self.log_dir = log_dir
        self.batch_size = batch_size
        self.queue = queue.Queue()
        self.running = True
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Start the daemon thread
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
    
    def log(self, obj: Any, filename: str = None) -> None:
        """
        Queue an object for logging.
        
        Args:
            obj: Object with to_json() method (StringConvertible)
            filename: Optional custom filename (default: auto-generated with timestamp)
        """
        self._wait_if_queue_full()
        # Create a deep snapshot of the data at this moment
        obj_snapshot = copy.deepcopy(obj.to_dict())
        self.queue.put((obj_snapshot, filename))
    
    def _worker(self) -> None:
        """Worker thread that processes the queue."""
        while self.running:
            try:
                # Wait for items with timeout to allow checking self.running
                obj_data, filename = self.queue.get(timeout=1)
                
                # Generate filename if not provided
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    # Extract class name from dict if available, otherwise use generic name
                    class_name = obj_data.get('name', 'object') if isinstance(obj_data, dict) else 'object'
                    filename = f"{class_name}_{timestamp}.json"
                
                # Full path
                filepath = os.path.join(self.log_dir, filename)
                
                # Save to file
                try:
                    with open(filepath, 'w') as f:
                        json.dump(obj_data, f, indent=2)
                    print(f"[Logger] Saved {filepath}")
                except Exception as e:
                    print(f"[Logger] Error saving {filepath}: {e}")
                
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Logger] Worker error: {e}")
    
    def stop(self) -> None:
        """Stop the logger thread gracefully."""
        print("[Logger] Stopping logger...")
        self.running = False
        self.thread.join(timeout=5)
    
    def wait_until_complete(self) -> None:
        """Block until all queued items are processed."""
        self.queue.join()
    
    def get_queue_size(self) -> int:
        """Return the number of items waiting to be logged."""
        return self.queue.qsize()

    def _wait_if_queue_full(self) -> None:
        """
        Block if queue has batch_size or more elements.
        Waits until queue is empty before returning.
        """
        if self.queue.qsize() >= self.batch_size:
            print(f"[Logger] Queue full ({self.queue.qsize()} items), waiting for queue to empty...")
            self.queue.join()
            print("[Logger] Queue emptied, resuming...")


class BatchLoggerThread(LoggerThread):
    """
    Logger that batches multiple objects into a single JSON file.
    Useful for high-frequency logging scenarios.
    """
    
    def __init__(self, log_dir: str = "logs", batch_size: int = 10, flush_interval: float = 1):
        """
        Args:
            log_dir: Directory where log files will be saved
            batch_size: Number of items to accumulate before writing
            flush_interval: Seconds to wait before flushing incomplete batch
        """
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
        super().__init__(log_dir, batch_size)
    
    def log(self, obj: Any, filename: str = None) -> None:
        """
        Queue an object for logging.
        
        Args:
            obj: Object with to_json() method (StringConvertible)
            filename: Optional custom filename (ignored in batch mode)
        """
        self._wait_if_queue_full()
        # Create a deep snapshot of the data at this moment
        obj_snapshot = copy.deepcopy(obj.to_dict())
        self.queue.put((obj_snapshot, filename))
    
    def _worker(self) -> None:
        """Worker thread that batches and processes the queue."""
        while self.running:
            try:
                # Check if we should flush based on time
                if self.batch and (time.time() - self.last_flush) >= self.flush_interval:
                    self._flush_batch()
                
                # Try to get an item
                try:
                    obj_data, filename = self.queue.get(timeout=0.5)
                    self.batch.append(obj_data)
                    self.queue.task_done()
                    
                    # Flush if batch is full
                    if len(self.batch) >= self.batch_size:
                        self._flush_batch()
                        
                except queue.Empty:
                    continue
                    
            except Exception as e:
                print(f"[BatchLogger] Worker error: {e}")
        
        # Flush remaining items on shutdown
        if self.batch:
            self._flush_batch()
    
    def _flush_batch(self) -> None:
        """Write the current batch to a file."""
        if not self.batch:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_{timestamp}.json"
        filepath = os.path.join(self.log_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.batch, f, indent=2)
            print(f"[BatchLogger] Saved batch with {len(self.batch)} items to {filepath}")
        except Exception as e:
            print(f"[BatchLogger] Error saving batch: {e}")
        
        self.batch = []
        self.last_flush = time.time()