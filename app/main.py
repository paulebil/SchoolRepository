from fastapi import FastAPI


app = FastAPI()

@app.get("/")
async def index():
    return {"message": "School Paper Repository is up and Running. Server Healthy!"}