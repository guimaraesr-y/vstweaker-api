import os
from django.core.files import File
from ninja import UploadedFile
from manager.models import VSFile, AudioTrack
from manager.domain.vs_file import VSFileEntity
from manager.domain.audio_track import AudioTrackEntity


class VSFileRepository:
    def create(self, name: str, file: UploadedFile) -> VSFileEntity:
        vs = VSFile.objects.create(
            name=name,
            zip_file=file,
        )
        return VSFileEntity(vs.id, vs.name, vs.zip_file.path, vs.extracted_path)

    def add_track(self, vs_id: int, track_name: str, file_path: str):
        with open(file_path, 'rb') as f:
            audio_file = File(f, name=os.path.basename(file_path))
            AudioTrack.objects.create(
                vs_file_id=vs_id,
                name=track_name,
                file=audio_file
            )

    def set_extracted_path(self, entity_id: VSFile, path: str):
        vs = VSFile.objects.get(id=entity_id)
        vs.set_extracted_path(path)

    def list_all(self):
        return VSFile.objects.all()
