from datetime import datetime
from pydantic import BaseModel

class SavingsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    commitment_amount: float

class SavingsResponse(BaseModel):
    used_committed_budget_percentage: float
    extra_on_demand_cost: float
    total_cost: float
    cost_without_discount: float
    savings_percentage: float
    optimal_commitment: float 

class OptimalSavingsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    tolerance: float = 0.01