import json
import os
from datetime import date, datetime
from pathlib import Path

import plotly.graph_objects as go
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# create basic / endpoint

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

# run 

# /get_response endpoint
@app.get("/get_response")
def get_response():
    return {"response": "This is a response!"}

# generate MidJourney image
@app.get("/mid_journey")
def mid_journey():
    pass

@app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)