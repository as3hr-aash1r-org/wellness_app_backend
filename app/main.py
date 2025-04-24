from fastapi import FastAPI

from app.routes import user

app = FastAPI()



app.include_router(user.router)