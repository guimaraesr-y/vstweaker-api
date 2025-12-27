from datetime import timedelta
from django.db import models
from django.utils import timezone

class VSFile(models.Model):
    """
    Representa um arquivo VS enviado pelo usuário (ZIP/RAR).
    """
    name = models.CharField(max_length=255)
    zip_file = models.FileField(upload_to="vs_files/", null=True)
    extracted_path = models.CharField(max_length=512, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def set_extracted_path(self, path):
        self.extracted_path = path
        self.save(update_fields=["extracted_path"])

    def has_recent_mixes(self, hours=24):
        from mixer.models import MixJob
        threshold = timezone.now() - timedelta(hours=hours)
        return MixJob.objects.filter(vs_file=self, created_at__gt=threshold).exists()

    def cleanup_tracks(self):
        """Remove extracted track files from disk and records from DB."""
        for track in self.tracks.all():
            if track.file:
                track.file.delete(save=False)
            track.delete()
        self.extracted_path = None
        self.save(update_fields=["extracted_path"])


class AudioTrack(models.Model):
    """
    Após a extração do VS, cada faixa separada é registrada aqui.
    """
    vs_file = models.ForeignKey(VSFile, related_name="tracks", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="audio_tracks/", null=True)

    def __str__(self):
        return f"{self.vs_file.name} - {self.name}"
