import logging
from typing import Dict, List, Optional

class AutomationWorker:
    """Automation Worker for VFS Global login and booking"""
    
    def __init__(self):
        self.retry_count = 3
        self.timeout = 300
        self.log_messages: List[str] = []
        self.status = "ready"
        self.logger = logging.getLogger(__name__)
    
    def set_retry_count(self, count: int):
        """Set maximum retry count"""
        self.retry_count = count
    
    def get_retry_count(self) -> int:
        """Get retry count"""
        return self.retry_count
    
    def set_timeout(self, timeout: int):
        """Set timeout in seconds"""
        self.timeout = timeout
    
    def get_timeout(self) -> int:
        """Get timeout"""
        return self.timeout
    
    def get_status(self) -> str:
        """Get worker status"""
        return self.status
    
    def log_info(self, message: str):
        """Log info message"""
        self.log_messages.append(message)
        self.logger.info(message)
    
    def get_log_count(self) -> int:
        """Get log count"""
        return len(self.log_messages)
    
    def process_batch(self, accounts: List[Dict]) -> Dict:
        """Process batch of accounts"""
        results = {
            "total": len(accounts),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        for account in accounts:
            try:
                results["successful"] += 1
                self.log_info(f"Processed account: {account.get('email')}")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))
        return results
