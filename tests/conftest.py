import pytest
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def vfs_config():
    return {
        "email": os.getenv("VFS_EMAIL", "{{VFS_EMAIL}}"),
        "password": os.getenv("VFS_PASSWORD", "{{VFS_PASSWORD}}"),
        "phone": os.getenv("VFS_PHONE", "{{VFS_PHONE}}"),
        "api_url": os.getenv("VFS_API_URL", "https://lift-api.vfsglobal.com"),
    }

@pytest.fixture
def mock_browser_page():
    class MockPage:
        async def goto(self, url): return True
        async def fill(self, selector, value): return True
        async def click(self, selector): return True
        async def wait_for_selector(self, selector): return True
        async def screenshot(self, path): return True
    return MockPage()

@pytest.fixture
def sample_account():
    return {
        "email": "{{VFS_EMAIL}}",
        "password": "{{VFS_PASSWORD}}",
        "phone": "{{VFS_PHONE}}"
    }
