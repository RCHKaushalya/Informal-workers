from pydantic import BaseModel

class UserCreate(BaseModel):
    nic: str
    name: str
    phone: str
    user_type: str
    language: str
    location: str
    sms_enabled: bool = False

class JobCreate(BaseModel):
    title: str
    description: str
    posted_by: int  # User ID of the poster
    location: str

class JobResponse(BaseModel):
    job_id: int
    worker_id: int
    response: str # 'liked' / 'rejected'