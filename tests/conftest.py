import pytest
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def vfs_config():
    return {
        "email": os.getenv("VFS_EMAIL", "mustafa.eke@live.com"),
        "password": os.getenv("VFS_PASSWORD", "Vfsglobal!5561!"),
        "phone": os.getenv("VFS_PHONE", "5468224662"),
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
        "email": "mustafa.eke@live.com",
        "password": "Vfsglobal!5561!",
        "phone": "5468224662"
    }
