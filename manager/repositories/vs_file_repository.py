from manager.models import VSFile, AudioTrack
from manager.domain.vs_file import VSFileEntity
from manager.domain.audio_track import AudioTrackEntity


class VSFileRepository:
    def create(self, name: str, original_filename: str, stored_path: str) -> VSFileEntity:
        vs = VSFile.objects.create(
            name=name,
            original_filename=original_filename,
            stored_path=stored_path
        )
        return VSFileEntity(vs.id, vs.name, vs.original_filename, vs.stored_path)

    def add_track(self, vs_id: int, track_name: str, file_path: str):
        AudioTrack.objects.create(
            vs_file_id=vs_id,
            name=track_name,
            file_path=file_path
        )

    def list_all(self):
        return VSFile.objects.all()
