import os
from typing import List
from ninja import Router, File
from ninja.files import UploadedFile
from django.conf import settings

from manager.repositories.vs_file_repository import VSFileRepository
from manager.infra.storage import LocalStorage
from manager.services.upload_service import UploadService
from manager.services.extraction_service import ExtractionService

from manager.api.schemas import AudioTrackSchema, VSFileDetailSchema, VSFileOut, VSFileSchema
from manager.models import AudioTrack, VSFile


router = Router()
storage = LocalStorage()
repository = VSFileRepository()
extract_service = ExtractionService(repository, os.path.join(settings.MEDIA_ROOT, "extracted"))
upload_service = UploadService(storage, repository)


def serialize_track(track: AudioTrack) -> AudioTrackSchema:
    return AudioTrackSchema(**track.__dict__)


@router.post("/upload", response=VSFileOut)
def upload_vs(request, file: UploadedFile = File(...)):
    entity = upload_service.upload_vs_file(file)
    extract_service.extract(entity)
    return VSFile.objects.get(id=entity.id)


# ---------------------------------------------
# 1. LISTAR VS
# ---------------------------------------------
@router.get("/", response=List[VSFileSchema])
def list_vs(request):
    return VSFile.objects.all()


# ---------------------------------------------
# 2. LISTAR AUDIO TRACKS DE UM VS
# ---------------------------------------------
@router.get("/{vs_id}/tracks", response=List[AudioTrackSchema])
def list_vs_tracks(request, vs_id: int):
    return AudioTrack.objects.filter(vs_file_id=vs_id)


# ---------------------------------------------
# 3. DETALHES DE UM VS + SUAS TRACKS
# ---------------------------------------------
@router.get("/{vs_id}", response=VSFileDetailSchema)
def get_vs_detail(request, vs_id: int):
    vs = VSFile.objects.get(id=vs_id)
    tracks = AudioTrack.objects.filter(vs_file=vs)

    return {
        "id": vs.id,
        "name": vs.name,
        "created_at": vs.created_at,
        "tracks": tracks
    }


# ---------------------------------------------
# 4. LISTAR TODAS AS TRACKS DO SISTEMA
# ---------------------------------------------
@router.get("/tracks", response=List[AudioTrackSchema])
def list_all_tracks(request):
    return AudioTrack.objects.all()