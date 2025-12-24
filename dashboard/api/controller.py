from ninja import Router
from dashboard.api.schemas import DashboardOut
from dashboard.services import DashboardService

router = Router()

@router.get("/", response=DashboardOut)
def get_dashboard_data(request):
    return DashboardService.get_dashboard_data()
