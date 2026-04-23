import sys
import os

# Add backend to path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the FastAPI app
from api import app

# Make app available at module level for Vercel
__all__ = ["app"]
