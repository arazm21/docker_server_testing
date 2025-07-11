from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:6000"]   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Serve static HTML file
@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    with open("user_simulator.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)
   