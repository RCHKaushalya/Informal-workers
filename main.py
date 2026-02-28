from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database.db import SessionLocal, User
from models import UserCreate

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Hello, Sri Lankan Workers!"}

# Register user endpoint
@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user with the same NIC already exists
    existing_user = db.query(User).filter(User.nic == user.nic).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this NIC already exists")

    # Create new user
    new_user = User(
        nic=user.nic,
        name=user.name,
        phone=user.phone,
        user_type=user.user_type,
        language=user.language,
        location=user.location,
        sms_enabled=user.sms_enabled
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}