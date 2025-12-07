class UploadService:
    def __init__(self, storage, repository):
        self.storage = storage
        self.repository = repository

    def upload_vs_file(self, file):
        stored_path = self.storage.save(file.name, file)
        entity = self.repository.create(
            name=file.name.split(".")[0],
            original_filename=file.name,
            stored_path=stored_path
        )
        return entity
