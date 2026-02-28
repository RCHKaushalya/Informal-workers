from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create SQLite database file
DATABASE_URL = "sqlite:///./informal_workers.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nic = Column(String, unique=True, index=True)
    name = Column(String)
    phone = Column(String)
    user_type = Column(String)  # 'worker' / 'seeker' / 'admin' / 'volunteer'
    language = Column(String)
    location = Column(String)
    sms_enabled = Column(Boolean, default=False)

# Job Table
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    posted_by = Column(Integer)  # User ID of the poster, FK to User.id
    location = Column(String)
    status = Column(String)  # 'posted' / 'assigned' / 'completed'

# Job Application Table
class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer)  # FK to Job.id
    worker_id = Column(Integer)  # FK to User.id
    response = Column(String, default="pending") # 'pending' / 'accepted' / 'rejected'
    assigned = Column(Boolean, default=False)

# Create the database tables
Base.metadata.create_all(bind=engine)
