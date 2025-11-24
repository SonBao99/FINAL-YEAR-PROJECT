"""
Vercel serverless function entry point
This wraps FastAPI app for Vercel deployment
"""
from attendance_api import app

# Export the FastAPI app for Vercel
handler = app

