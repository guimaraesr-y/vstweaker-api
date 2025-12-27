from datetime import datetime
from ninja import Schema
from typing import List


class AudioTrackSchema(Schema):
    id: int
    name: str
    file: str


class VSFileSchema(Schema):
    id: int
    name: str
    tracks_count: int
    created_at: datetime


class VSFileDetailSchema(Schema):
    id: int
    name: str
    zip_file: str
    tracks: List[AudioTrackSchema]
    tracks_count: int
    created_at: datetime


class VSFileOut(Schema):
    id: int
    name: str
    zip_file: str
    extracted_path: str
    tracks_count: int
    created_at: datetime
