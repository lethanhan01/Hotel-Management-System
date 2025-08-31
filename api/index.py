import os
import sys
from vercel_wsgi import make_app

# Ensure project src/ is on sys.path so `from src.app import app` works during build
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from app import app  # now import directly from src (sys.path adjusted)

# Create WSGI application wrapper for Vercel
application = make_app(app)

# Vercel Python runtime expects an `app` or `handler` symbol. Export `app`.
app = application
