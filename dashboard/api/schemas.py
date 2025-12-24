from typing import List, Union
from ninja import Schema
from manager.api.schemas import VSFileSchema

class StatItem(Schema):
    label: str
    value: Union[int, float, str]
    change_percentage: float
    trend: str  # 'up', 'down', 'neutral'

class DashboardStats(Schema):
    total_vs_files: StatItem
    active_mixes: StatItem
    success_rate: StatItem
    processing: StatItem

class DashboardOut(Schema):
    stats: DashboardStats
    recent_vs: List[VSFileSchema]
