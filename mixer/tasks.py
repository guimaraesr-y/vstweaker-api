# mixer/tasks.py
from celery import shared_task
from django.core.files import File
import shutil
import os

from mixer.models import MixJob, MixTrackConfig
from mixer.services.mixing_service import MixingService, TrackSetting


@shared_task(bind=True)
def process_mix_job(self, mix_job_id):
    try:
        mix = MixJob.objects.get(id=mix_job_id)
    except MixJob.DoesNotExist:
        return

    if mix.status not in [MixJob.STATUS_PENDING, MixJob.STATUS_ERROR]:
        return

    mix.mark_processing()

    try:
        settings = []
        for cfg in mix.tracks.all():
            audio_file_path = cfg.audio_track.file.path
            settings.append(
                TrackSetting(
                    file_path=audio_file_path,
                    volume_db=cfg.volume_db,
                    pan=cfg.pan
                )
            )

        service = MixingService()
        result = service.mix(settings)

        with open(result.output_path, "rb") as f:
            mix.output_file.save(os.path.basename(result.output_path), File(f), save=True)

        mix.mark_done()

        shutil.rmtree(os.path.dirname(result.output_path), ignore_errors=True)

    except Exception as e:
        mix.mark_error(str(e))
        raise e
