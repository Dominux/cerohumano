from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define a Pydantic model to validate incoming data
class User(BaseModel):
    username: str
    email: str
    is_active: bool = True

# A simple GET endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI application!"}

# A GET endpoint with path parameters
@app.get("/users/{user_id}")
def get_user(user_id: int, status: str | None = None):
    return {"user_id": user_id, "status": status}

# A POST endpoint to receive and validate data
@app.post("/users/")
def create_user(user: User):
    return {"message": "User created successfully", "data": user}
