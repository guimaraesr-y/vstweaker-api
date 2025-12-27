import os
from django.conf import settings


class FileStorage:
    def save(self, filename: str, content) -> str:
        raise NotImplementedError


class LocalStorage(FileStorage):
    def __init__(self, base_path=None):
        self.base_path = base_path or os.path.join(settings.MEDIA_ROOT, "vs_files")
        os.makedirs(self.base_path, exist_ok=True)

    def save(self, filename: str, content) -> str:
        path = os.path.join(self.base_path, filename)
        with open(path, "wb") as f:
            for chunk in content.chunks():
                f.write(chunk)
        return path
