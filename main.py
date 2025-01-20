from fastapi import FastAPI

from migration_0001 import run_migration

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.get("/migrate")
async def migrate():
    run_migration()
    return {"message": "Migration complete! Ran migration_0001.py"}