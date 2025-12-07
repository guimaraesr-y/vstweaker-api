import os
from ninja import Router, Schema
from ninja.files import UploadedFile, File
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import FileResponse, Http404
from vsmanager.repositories.vs_file_repository import VSFileRepository
from vsmanager.models import VSFile, AudioTrack, MixJob, MixTrackSetting
from .schemas import VSFileOut
from .controller_upload import upload_service, extract_service  # se separados
from vsmanager.tasks import run_mix_job

router = Router()

# Schemas
class TrackSettingIn(Schema):
    audio_track_id: int
    volume_db: float = 0.0
    pan: float = 0.0

class CreateMixIn(Schema):
    vs_file_id: int
    name: Optional[str] = None
    tracks: List[TrackSettingIn]

class MixJobOut(Schema):
    id: int
    name: str
    status: str
    created_at: str
    output_url: Optional[str] = None
    error_message: Optional[str] = None

# Create mix job and enqueue
@router.post("/mix/create", response=MixJobOut)
def create_mix_job(request, payload: CreateMixIn):
    vs = get_object_or_404(VSFile, id=payload.vs_file_id)
    name = payload.name or f"Mix of {vs.name}"
    mix_job = MixJob.objects.create(vs_file=vs, name=name)

    # create track settings
    for t in payload.tracks:
        track = get_object_or_404(AudioTrack, id=t.audio_track_id, vs_file=vs)
        MixTrackSetting.objects.create(
            mix_job=mix_job,
            audio_track=track,
            volume_db=float(t.volume_db),
            pan=float(t.pan)
        )

    # enqueue celery task
    run_mix_job.delay(mix_job.id)

    return _mixjob_to_out(mix_job, request)

@router.get("/mix/{mix_job_id}", response=MixJobOut)
def get_mix_job(request, mix_job_id: int):
    mix_job = get_object_or_404(MixJob, id=mix_job_id)
    return _mixjob_to_out(mix_job, request)

@router.get("/mix/{mix_job_id}/download")
def download_mix(request, mix_job_id: int):
    mix_job = get_object_or_404(MixJob, id=mix_job_id)
    if mix_job.status != MixJob.STATUS_DONE or not mix_job.output_file:
        raise Http404("Mix not ready")
    # serve file
    fp = mix_job.output_file.path
    return FileResponse(open(fp, "rb"), as_attachment=True, filename=os.path.basename(fp))

def _mixjob_to_out(mix_job: MixJob, request):
    out = {
        "id": mix_job.id,
        "name": mix_job.name,
        "status": mix_job.status,
        "created_at": mix_job.created_at.isoformat(),
        "output_url": None,
        "error_message": mix_job.error_message,
    }
    if mix_job.status == MixJob.STATUS_DONE and mix_job.output_file:
        # URL building — adjust MEDIA_URL and your host as needed
        out["output_url"] = request.build_absolute_uri(f"/media/{mix_job.output_file.name}")
    return out
