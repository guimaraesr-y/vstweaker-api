# mixer/api/controller.py
from ninja import Router
from django.shortcuts import get_object_or_404
from manager.models import VSFile, AudioTrack
from mixer.models import MixJob, MixTrackConfig
from mixer.tasks import process_mix_job
from .schemas import CreateMixIn, MixJobOut


router = Router()


def serialize_mix(mix: MixJob, request):
    return {
        "id": mix.id,
        "name": mix.name,
        "status": mix.status,
        "output_url": request.build_absolute_uri("/media/" + mix.output_file.name) if mix.output_file else None,
        "error_message": mix.error_message,
    }


@router.post("/create", response=MixJobOut)
def create_mix(request, payload: CreateMixIn):
    vs = get_object_or_404(VSFile, id=payload.vs_file_id)

    mix = MixJob.objects.create(
        vs_file=vs,
        name=payload.name
    )

    for t in payload.tracks:
        track = get_object_or_404(AudioTrack, id=t.audio_track_id)
        MixTrackConfig.objects.create(
            mix_job=mix,
            audio_track=track,
            volume_db=t.volume_db,
            pan=t.pan
        )

    process_mix_job.delay(mix.id)

    return serialize_mix(mix, request)


@router.get("/{mix_id}", response=MixJobOut)
def get_status(request, mix_id: int):
    mix = get_object_or_404(MixJob, id=mix_id)
    return serialize_mix(mix, request)


@router.get("/{mix_id}/reexport", response=MixJobOut)
def reexport(request, mix_id: int):
    mix = get_object_or_404(MixJob, id=mix_id)

    mix.status = MixJob.STATUS_PENDING
    mix.output_file.delete(save=True)

    process_mix_job.delay(mix.id)

    return serialize_mix(mix, request)
