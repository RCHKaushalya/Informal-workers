from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database.db import SessionLocal, User, Job, JobApplication
from models import UserCreate, JobCreate, JobResponse
from sms_utils import send_sms, receive_sms
from language_messages import MESSAGES
from ranking import calculate_score
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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

# Worker Responds to Job (API Endpoint)
@app.post("/respond-job/")
def respond_job(response: JobResponse, db: Session = Depends(get_db)):
    # Check if the job exists
    job = db.query(Job).filter(Job.id == response.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if the worker exists
    worker = db.query(User).filter(User.id == response.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Create or update job application
    job_application = db.query(JobApplication).filter(
        JobApplication.job_id == response.job_id,
        JobApplication.worker_id == response.worker_id
    ).first()

    if job_application:
        job_application.response = response.response
    else:
        job_application = JobApplication(
            job_id=response.job_id,
            worker_id=response.worker_id,
            response=response.response
        )
        db.add(job_application)

    db.commit()
    db.refresh(job_application)
    return {"message": f"Job response recorded: {job_application.response}"}

# API Endpoint to List Interested Workers for a Job
@app.get("/job/{job_id}/applicants/")
def get_applicants(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    applications = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.response == "liked"
    ).all()

    applicants = []
    for app in applications:
        worker = db.query(User).filter(User.id == app.worker_id).first()
                
        if worker:
            score = calculate_score(worker)
            applicants.append({
                "worker_id": worker.id,
                "name": worker.name,
                "phone": worker.phone,
                "language": worker.language,
                "location": worker.location,
                "score": score
            })
    
    applicants.sort(key=lambda x: x['score'], reverse=True)  # Sort by score descending

    return {"applicants": applicants}

# API Endpoint to send SMS to worker
@app.post("/notify-worker/{job_id}")
def notify_worker(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    workers =  db.query(User).filter(
        User.sms_enabled == True,
        User.location == job.location,
        User.user_type == "worker"
    ).all()

    for worker in workers:
        lang = worker.language
        message = MESSAGES['job_alert'][lang].format(title=job.title)
        send_sms(worker.phone, message)
    
    return {"message": f"Notifications sent to {len(workers)} workers"}

# API Endpoint to receive SMS responses from workers
@app.post("/process-sms/")
def process_sms(db: Session = Depends(get_db)):
    job_id, worker_id, response = receive_sms()

    # Check if the job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if the worker exists
    worker = db.query(User).filter(User.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    # Create or update job application
    job_application = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.worker_id == worker_id
    ).first()

    if job_application:
        job_application.response = response
    else:
        job_application = JobApplication(
            job_id=job_id,
            worker_id=worker_id,
            response=response
        )
        db.add(job_application)

    db.commit()
    db.refresh(job_application)
    return {"message": f"SMS response recorded: {response}"}

# Endpoint to assign job to worker
@app.post("/assign-job/")
def assign_job(job_id: int, worker_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    worker = db.query(User).filter(User.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    job_application = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.worker_id == worker_id
    ).first()

    if not job_application or job_application.response != "liked":
        raise HTTPException(status_code=400, detail="Worker did not like this job")

    job_application.assigned = True
    job.status = "assigned"
    db.commit()

    return {"message": f"Worker {worker.name} assigned to job"}

@app.get('/admin')
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})