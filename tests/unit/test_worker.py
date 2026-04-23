import pytest
from src.modules.worker import AutomationWorker

@pytest.mark.unit
def test_worker_initialization():
    """Test Automation Worker initialization"""
    worker = AutomationWorker()
    assert worker is not None

@pytest.mark.unit
def test_worker_batch_processing():
    """Test batch account processing"""
    worker = AutomationWorker()
    accounts = [
        {"email": "{{VFS_EMAIL}}", "phone": "{{VFS_PHONE}}"}
    ]
    result = worker.process_batch(accounts)
    assert result is not None

@pytest.mark.unit
def test_worker_status_report():
    """Test worker status reporting"""
    worker = AutomationWorker()
    status = worker.get_status()
    assert status is not None

@pytest.mark.unit
def test_worker_retry_mechanism():
    """Test worker retry mechanism"""
    worker = AutomationWorker()
    worker.set_retry_count(3)
    assert worker.get_retry_count() == 3

@pytest.mark.unit
def test_worker_logging():
    """Test worker logging mechanism"""
    worker = AutomationWorker()
    worker.log_info("Test log message")
    assert worker.get_log_count() >= 1
