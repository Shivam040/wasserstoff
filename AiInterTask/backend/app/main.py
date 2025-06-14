from fastapi import FastAPI
from app.api.routes import router

app = FastAPI()
# Include the router from routes.py so that all defined endpoints are part of the app
app.include_router(router)
