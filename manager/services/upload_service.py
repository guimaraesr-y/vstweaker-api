from manager.domain.vs_file import VSFileEntity
from manager.infra.storage import FileStorage
from manager.repositories.vs_file_repository import VSFileRepository


# TODO: Create routine to clear local extracted if using S3
class UploadService:

    def __init__(self, storage: FileStorage, repository: VSFileRepository):
        self.storage = storage
        self.repository = repository

    def upload_vs_file(self, file) -> VSFileEntity:
        return self.repository.create(
            name=file.name.split(".")[0],
            file=file,
        )
