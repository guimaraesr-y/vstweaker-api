import os
from ninja import Router, File
from ninja.files import UploadedFile
from django.conf import settings

from manager.repositories.vs_file_repository import VSFileRepository
from manager.infra.storage import LocalStorage
from manager.services.upload_service import UploadService
from manager.services.extraction_service import ExtractionService

from manager.api.schemas import VSFileOut
from manager.models import VSFile


router = Router()
storage = LocalStorage()
repository = VSFileRepository()
extract_service = ExtractionService(repository, os.path.join(settings.MEDIA_ROOT, "extracted"))
upload_service = UploadService(storage, repository)


@router.post("/upload", response=VSFileOut)
def upload_vs(request, file: UploadedFile = File(...)):
    entity = upload_service.upload_vs_file(file)
    extract_service.extract(entity)
    return VSFile.objects.get(id=entity.id)


@router.get("/list", response=list[VSFileOut])
def list_vs_files(request):
    return VSFile.objects.all()
