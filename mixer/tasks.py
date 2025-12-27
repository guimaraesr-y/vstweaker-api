# mixer/tasks.py
from celery import shared_task
from django.core.files import File
import shutil
import os
from datetime import timedelta
from django.utils import timezone

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
        result = service.mix(settings, name=mix.name)

        with open(result.output_path, "rb") as f:
            mix.output_file.save(os.path.basename(result.output_path), File(f), save=True)

        mix.mark_done()

        shutil.rmtree(os.path.dirname(result.output_path), ignore_errors=True)

    except Exception as e:
        mix.mark_error(str(e))
        raise e

@shared_task
def cleanup_inactive_mix_files():
    """Delete mix files inactive for more than 12 hours."""
    threshold = timezone.now() - timedelta(hours=12)
    
    # Files never downloaded: check created_at
    mixes_never_downloaded = MixJob.objects.filter(
        status=MixJob.STATUS_DONE,
        last_downloaded_at__isnull=True,
        finished_at__lt=threshold
    )
    
    # Files downloaded long ago
    mixes_inactive = MixJob.objects.filter(
        status=MixJob.STATUS_DONE,
        last_downloaded_at__lt=threshold
    )
    
    affected = 0
    for mix in (mixes_never_downloaded | mixes_inactive).distinct():
        if mix.output_file:
            mix.output_file.delete(save=False)
            mix.status = MixJob.STATUS_EXPIRED
            mix.save(update_fields=["status"])
            affected += 1
    
    return f"Cleaned up {affected} inactive mix files"

@shared_task
def cleanup_inactive_vs_tracks():
    """Delete extracted tracks for VS files with no mixes in the last 24 hours."""
    from manager.models import VSFile
    threshold = timezone.now() - timedelta(hours=24)
    
    # VS files older than 24h
    vs_files = VSFile.objects.filter(created_at__lt=threshold, extracted_path__isnull=False)
    
    affected = 0
    for vs in vs_files:
        if not vs.has_recent_mixes(hours=24):
            vs.cleanup_tracks()
            affected += 1
            
    return f"Cleaned up tracks for {affected} VS files"
