# mixer/api/schemas.py
from ninja import Schema
from typing import List


class TrackConfigIn(Schema):
    audio_track_id: int
    volume_db: float = 0.0
    pan: float = 0.0


class CreateMixIn(Schema):
    vs_file_id: int
    name: str
    tracks: List[TrackConfigIn]


class MixJobOut(Schema):
    id: int
    name: str
    status: str
    output_url: str | None = None
    error_message: str | None = None
    tracks: List[TrackConfigIn]
