from django.utils import timezone
from datetime import timedelta
from manager.models import VSFile
from mixer.models import MixJob

class StatsService:
    @staticmethod
    def get_stats():
        now = timezone.now()
        last_month = now - timedelta(days=30)

        # Total VS Files
        total_vs = VSFile.objects.count()
        prev_total_vs = VSFile.objects.filter(created_at__lt=last_month).count()
        vs_change = StatsService._calculate_change(total_vs, prev_total_vs)

        # Active Mixes (Total projects)
        active_mixes = MixJob.objects.count()
        prev_active_mixes = MixJob.objects.filter(created_at__lt=last_month).count()
        mixes_change = StatsService._calculate_change(active_mixes, prev_active_mixes)

        # Processing
        processing = MixJob.objects.filter(status=MixJob.STATUS_PROCESSING).count()
        prev_processing = MixJob.objects.filter(status=MixJob.STATUS_PROCESSING, created_at__lt=last_month).count()
        processing_change = StatsService._calculate_change(processing, prev_processing)

        # Success Rate
        done_mixes = MixJob.objects.filter(status=MixJob.STATUS_DONE).count()
        total_finished = MixJob.objects.filter(status__in=[MixJob.STATUS_DONE, MixJob.STATUS_ERROR]).count()
        
        success_rate = (done_mixes / total_finished * 100) if total_finished > 0 else 100.0
        
        prev_done = MixJob.objects.filter(status=MixJob.STATUS_DONE, created_at__lt=last_month).count()
        prev_finished = MixJob.objects.filter(status__in=[MixJob.STATUS_DONE, MixJob.STATUS_ERROR], created_at__lt=last_month).count()
        prev_success_rate = (prev_done / prev_finished * 100) if prev_finished > 0 else 100.0
        success_change = success_rate - prev_success_rate

        return {
            "total_vs_files": {
                "label": "Total VS Files",
                "value": total_vs,
                "change_percentage": vs_change,
                "trend": "up" if vs_change > 0 else "down" if vs_change < 0 else "neutral"
            },
            "active_mixes": {
                "label": "Active Mixes",
                "value": active_mixes,
                "change_percentage": mixes_change,
                "trend": "up" if mixes_change > 0 else "down" if mixes_change < 0 else "neutral"
            },
            "success_rate": {
                "label": "Success Rate",
                "value": f"{int(success_rate)}%",
                "change_percentage": success_change,
                "trend": "up" if success_change > 0 else "down" if success_change < 0 else "neutral"
            },
            "processing": {
                "label": "Processing",
                "value": processing,
                "change_percentage": processing_change,
                "trend": "up" if processing_change > 0 else "down" if processing_change < 0 else "neutral"
            }
        }

    @staticmethod
    def _calculate_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100.0
