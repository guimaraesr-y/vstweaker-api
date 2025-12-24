from .stats_service import StatsService
from .library_service import LibraryService

class DashboardService:
    @staticmethod
    def get_dashboard_data():
        return {
            "stats": StatsService.get_stats(),
            "recent_vs": LibraryService.get_recent_vs()
        }
