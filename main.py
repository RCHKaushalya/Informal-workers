from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database.db import SessionLocal, User, Job
from models import UserCreate, JobCreate

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
@app.post("/register/")
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

# Post job endpoint
@app.post("/post-job/")
def post_job(job: JobCreate, db: Session = Depends(get_db)):
    # Check if the poster exists
    poster = db.query(User).filter(User.id == job.posted_by).first()
    if not poster:
        raise HTTPException(status_code=404, detail="Poster user not found")

    # Create new job
    new_job = Job(
        title=job.title,
        description=job.description,
        posted_by=job.posted_by,
        location=job.location,
        status="posted"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {"message": "Job posted successfully", "job_id": new_job.id}

# endpoint to list available jobs
@app.get("/jobs/")
def list_jobs(location: str = None, db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.status == "posted")
    if location:
        jobs = jobs.filter(Job.location == location)
    jobs = jobs.all()
    return {"jobs": jobs}