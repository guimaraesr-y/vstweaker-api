from django.db import models
from django.conf import settings
import uuid
import os

def mix_output_path(instance, filename):
    return os.path.join("vs_mixes", str(instance.id), filename)


class MixJob(models.Model):
    """
    Representa um job de mixagem enfileirado/executado.
    """
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_ERROR = "error"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_DONE, "Done"),
        (STATUS_ERROR, "Error"),
    ]

    vs_file = models.ForeignKey("VSFile", on_delete=models.CASCADE, related_name="mix_jobs")
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    output_file = models.FileField(upload_to=mix_output_path, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"MixJob {self.id} - {self.name} - {self.status}"


class MixTrackSetting(models.Model):
    """
    Configuração por faixa: volume (dB) e pan (-1.0 left .. 1.0 right)
    """
    mix_job = models.ForeignKey(MixJob, on_delete=models.CASCADE, related_name="track_settings")
    audio_track = models.ForeignKey("AudioTrack", on_delete=models.CASCADE, related_name="+")
    # volume in dB. 0 = original, negative reduce, positive increase
    volume_db = models.FloatField(default=0.0)
    # pan -1.0 (full left) .. 1.0 (full right)
    pan = models.FloatField(default=0.0)

    class Meta:
        unique_together = (("mix_job", "audio_track"),)

    def __str__(self):
        return f"{self.audio_track.name} ({self.volume_db} dB, pan {self.pan})"
