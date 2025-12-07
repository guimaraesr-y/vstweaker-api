from ninja import Schema
from datetime import datetime

class VSFileOut(Schema):
    id: int
    name: str
    original_filename: str
    created_at: datetime
