from django.db import models


class VSFile(models.Model):
    """
    Representa um arquivo VS enviado pelo usuário (ZIP/RAR).
    """
    name = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    stored_path = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class AudioTrack(models.Model):
    """
    Após a extração do VS, cada faixa separada é registrada aqui.
    """
    vs_file = models.ForeignKey(VSFile, on_delete=models.CASCADE, related_name="tracks")
    name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.vs_file.name} - {self.name}"


