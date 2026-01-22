from sqlalchemy import Column, Integer, String
from database import Base

# ------------------ MISSIONS TABLE ------------------
# Skill model is already defined in models.py
# Do NOT redefine Skill here (it breaks SQLAlchemy)

class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)       # <-- fixed here
    description = Column(String, nullable=True)
    difficulty = Column(String, nullable=False)
