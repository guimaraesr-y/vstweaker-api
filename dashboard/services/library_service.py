from manager.models import VSFile
from django.db.models import Count


class LibraryService:
    @staticmethod
    def get_recent_vs(limit=5):
        return VSFile.objects.all().annotate(
            tracks_count=Count("tracks")
        ).order_by("-created_at")[:limit]
