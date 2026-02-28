from pydantic import BaseModel

class UserCreate(BaseModel):
    nic: str
    name: str
    phone: str
    user_type: str
    language: str
    location: str
    sms_enabled: bool = False