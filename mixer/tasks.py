from celery import shared_task
from django.utils import timezone
from django.core.files import File
import os
from .models import MixJob, MixTrackSetting
from .services.mixing_service import MixingService, TrackSetting as TS
import shutil

@shared_task(bind=True)
def run_mix_job(self, mix_job_id: int):
    try:
        mix_job = MixJob.objects.select_related("vs_file").get(id=mix_job_id)
    except MixJob.DoesNotExist:
        return {"error": "MixJob not found"}

    mix_job.status = MixJob.STATUS_PROCESSING
    mix_job.started_at = timezone.now()
    mix_job.save(update_fields=["status", "started_at"])

    try:
        # collect track settings
        settings_qs = mix_job.track_settings.select_related("audio_track").all()
        track_settings = []
        for s in settings_qs:
            audio_path = s.audio_track.file_path  # path in disk from extraction
            track_settings.append(TS(path=audio_path, volume_db=s.volume_db, pan=s.pan))

        if not track_settings:
            raise Exception("No tracks configured for this mix job")

        mixing_service = MixingService()
        result = mixing_service.mix(track_settings)

        # move result to Django FileField storage
        with open(result.output_path, "rb") as f:
            django_file = File(f)
            # define filename in storage
            filename = os.path.basename(result.output_path)
            mix_job.output_file.save(filename, django_file, save=False)

        mix_job.status = MixJob.STATUS_DONE
        mix_job.finished_at = timezone.now()
        mix_job.save(update_fields=["output_file", "status", "finished_at"])

        # cleanup temp dir (result.output_path inside temp dir). Remove temp dir.
        try:
            temp_dir = os.path.dirname(result.output_path)
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        return {"status": "ok", "mix_job_id": mix_job.id}

    except Exception as e:
        mix_job.status = MixJob.STATUS_ERROR
        mix_job.error_message = str(e)
        mix_job.finished_at = timezone.now()
        mix_job.save(update_fields=["status", "error_message", "finished_at"])
        raise  # re-raise so Celery marks the task as failed
