import zipfile
import rarfile
import os

from manager.domain.vs_file import VSFileEntity
from manager.repositories.vs_file_repository import VSFileRepository


class ExtractionService:
    def __init__(self, repository: VSFileRepository, base_extract_path: str):
        self.repository = repository
        self.base_extract_path = base_extract_path

    def extract(self, vs_file_entity: VSFileEntity):
        extract_dir = os.path.join(self.base_extract_path, str(vs_file_entity.id))
        os.makedirs(extract_dir, exist_ok=True)

        if vs_file_entity.zip_file.endswith(".zip"):
            with zipfile.ZipFile(vs_file_entity.zip_file, 'r') as z:
                z.extractall(extract_dir)

        elif vs_file_entity.zip_file.endswith(".rar"):
            with rarfile.RarFile(vs_file_entity.zip_file) as r:
                r.extractall(extract_dir)

        # registra faixas
        for root, _, files in os.walk(extract_dir):
            for f in files:
                if f.lower().endswith((".wav", ".mp3")):
                    self.repository.add_track(
                        vs_file_entity.id,
                        f,
                        os.path.join(root, f)
                    )

        vs_file_entity
        self.repository.set_extracted_path(
            entity_id=vs_file_entity.id,
            path=extract_dir
        )
