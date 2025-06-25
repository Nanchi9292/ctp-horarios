from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Class:
    group_name: str
    day: str
    time_slot: str
    subject: str
    teacher: str
    classroom: str
    created_by: Optional[str] = None
    last_modified: Optional[datetime] = None

@dataclass
class User:
    username: str
    password_hash: str
    role: str  # 'admin', 'teacher', 'student'
    full_name: str = ""
    email: str = ""
