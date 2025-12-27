# mixer/models.py
from django.db import models
from django.utils import timezone
from manager.models import AudioTrack, VSFile


def mix_output_path(instance, filename):
    return f"vs_mixes/{instance.id}/{filename}"


class MixJob(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_ERROR = "error"
    STATUS_EXPIRED = "expired"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_DONE, "Done"),
        (STATUS_ERROR, "Error"),
        (STATUS_EXPIRED, "Expired"),
    ]

    vs_file = models.ForeignKey(VSFile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    output_file = models.FileField(upload_to=mix_output_path, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)

    def mark_processing(self):
        self.status = self.STATUS_PROCESSING
        self.error_message = None
        self.started_at = timezone.now()
        self.save(update_fields=["status", "error_message", "started_at"])

    def mark_done(self):
        self.status = self.STATUS_DONE
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "finished_at"])

    def mark_error(self, msg):
        self.status = self.STATUS_ERROR
        self.error_message = msg
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "error_message", "finished_at"])

    def mark_downloaded(self):
        self.last_downloaded_at = timezone.now()
        self.save(update_fields=["last_downloaded_at"])

    def delete(self, *args, **kwargs):
        if self.status == self.STATUS_PROCESSING:
            raise RuntimeError("Cannot delete a mix that is currently being processed.")
            
        if self.output_file:
            self.output_file.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"MixJob({self.id}) - {self.name}"


class MixTrackConfig(models.Model):
    mix_job = models.ForeignKey(MixJob, related_name="tracks", on_delete=models.CASCADE)
    audio_track = models.ForeignKey(AudioTrack, on_delete=models.CASCADE)

    volume_db = models.FloatField(default=0.0)
    pan = models.FloatField(default=0.0)  # -1.0 (esq) a +1.0 (dir)

    class Meta:
        unique_together = ("mix_job", "audio_track")

    def __str__(self):
        return f"TrackConfig({self.audio_track.id}) vol={self.volume_db} pan={self.pan}"
