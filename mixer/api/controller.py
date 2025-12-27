# mixer/api/controller.py
from typing import List
from ninja import Router
from ninja.responses import Response
from django.shortcuts import get_object_or_404
from manager.api.controller import serialize_track
from manager.models import VSFile, AudioTrack
from mixer.models import MixJob, MixTrackConfig
from mixer.tasks import process_mix_job
from .schemas import CreateMixIn, MixJobOut


router = Router()


def serialize_mix(mix: MixJob, request, include_mix_track_configs=False):
    output_url = None
    status = mix.status

    if mix.output_file and mix.status == MixJob.STATUS_DONE:
        if mix.output_file.storage.exists(mix.output_file.name):
            output_url = request.build_absolute_uri("/media/" + mix.output_file.name)
        else:
            status = MixJob.STATUS_EXPIRED

    data = {
        "id": mix.id,
        "name": mix.name,
        "status": status,
        "output_url": output_url,
        "error_message": mix.error_message,
        "last_downloaded_at": mix.last_downloaded_at,
    }

    if include_mix_track_configs:
        data["mix_track_configs"] = [
            {
                "id": t.audio_track_id,
                "volume_db": t.volume_db,
                "pan": t.pan,
                "track": serialize_track(t.audio_track)
            }
            for t in mix.tracks.all().select_related("audio_track")
        ]

    return data


@router.get("", response=List[MixJobOut])
def list_mixes(request):
    return [
        serialize_mix(mix, request, include_mix_track_configs=True)
        for mix in MixJob.objects.all().select_related(
            'vs_file',
        ).prefetch_related('tracks__audio_track')
    ]


@router.get("/{mix_id}", response=MixJobOut)
def get_status(request, mix_id: int):
    mix = get_object_or_404(MixJob, id=mix_id)
    return serialize_mix(mix, request, include_mix_track_configs=True)


@router.get("/vs/{vs_id}", response=List[MixJobOut])
def list_mixes_by_vs(request, vs_id):
    return [
        serialize_mix(mix, request, include_mix_track_configs=True)
        for mix in MixJob.objects.filter(vs_file_id=vs_id).select_related(
            'vs_file',
        ).prefetch_related('tracks__audio_track')
    ]


@router.post("", response=MixJobOut)
def create_mix(request, payload: CreateMixIn):
    vs = get_object_or_404(VSFile, id=payload.id)

    mix = MixJob.objects.create(
        vs_file=vs,
        name=payload.name
    )

    for t in payload.tracks:
        track = get_object_or_404(AudioTrack, id=t.id)
        MixTrackConfig.objects.create(
            mix_job=mix,
            audio_track=track,
            volume_db=t.volume_db,
            pan=t.pan
        )

    process_mix_job.delay(mix.id)

    return serialize_mix(mix, request, include_mix_track_configs=True)

@router.patch("/{mix_id}", response=MixJobOut)
def update_mix(request, mix_id: int, payload: CreateMixIn):
    mix = get_object_or_404(MixJob, id=mix_id)

    for t in payload.tracks:
        track = get_object_or_404(AudioTrack, id=t.audio_track_id)
        MixTrackConfig.objects.update_or_create(
            mix_job=mix,
            audio_track=track,
            volume_db=t.volume_db,
            pan=t.pan
        )

    mix.name = payload.name
    mix.save(update_fields=["name"])

    return serialize_mix(mix, request, include_mix_track_configs=True)


@router.delete("/{mix_id}")
def delete_mix(request, mix_id: int):
    mix = get_object_or_404(MixJob, id=mix_id)
    mix.delete()

    return Response(data=None, status=204)


@router.get("/{mix_id}/reexport", response=MixJobOut)
def reexport(request, mix_id: int):
    mix = get_object_or_404(MixJob, id=mix_id)

    mix.status = MixJob.STATUS_PENDING
    mix.output_file.delete(save=True)

    process_mix_job.delay(mix.id)

    return serialize_mix(mix, request, include_mix_track_configs=True)


@router.get("/{mix_id}/download")
def download_mix(request, mix_id: int):
    mix = get_object_or_404(MixJob, id=mix_id)
    
    # If explicitly expired or file missing on disk
    is_missing = not mix.output_file or not mix.output_file.storage.exists(mix.output_file.name)
    
    if mix.status == MixJob.STATUS_EXPIRED or is_missing:
        # File is missing or expired, regeneration needed
        mix.status = MixJob.STATUS_PENDING
        mix.save(update_fields=["status"])
        process_mix_job.delay(mix.id)
        return {"detail": "File is being regenerated", "status": mix.status}

    mix.mark_downloaded()
    return {"url": request.build_absolute_uri("/media/" + mix.output_file.name)}
