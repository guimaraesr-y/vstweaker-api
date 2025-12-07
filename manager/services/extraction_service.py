import zipfile
import rarfile
import os


class ExtractionService:
    def __init__(self, repository, base_extract_path):
        self.repository = repository
        self.base_extract_path = base_extract_path

    def extract(self, vs_file_entity):
        extract_dir = os.path.join(self.base_extract_path, str(vs_file_entity.id))
        os.makedirs(extract_dir, exist_ok=True)

        if vs_file_entity.original_filename.endswith(".zip"):
            with zipfile.ZipFile(vs_file_entity.stored_path, 'r') as z:
                z.extractall(extract_dir)

        elif vs_file_entity.original_filename.endswith(".rar"):
            with rarfile.RarFile(vs_file_entity.stored_path) as r:
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
