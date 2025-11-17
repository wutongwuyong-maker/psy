import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info", reload=False, access_log=False)