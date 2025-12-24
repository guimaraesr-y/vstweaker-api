from manager.models import VSFile

class LibraryService:
    @staticmethod
    def get_recent_vs(limit=5):
        return VSFile.objects.all().order_by("-created_at")[:limit]
