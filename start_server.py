"""
Production server startup script
"""
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "attendance_api:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )

