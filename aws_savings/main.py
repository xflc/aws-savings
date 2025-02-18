from fastapi import FastAPI
from aws_savings.models.savings_request import SavingsRequest, SavingsResponse, OptimalSavingsRequest
from aws_savings.services.savings_calculator import SavingsCalculator
import pandas as pd

app = FastAPI()

@app.post("/calculate-savings", response_model=SavingsResponse)
async def calculate_savings(request: SavingsRequest) -> SavingsResponse:
    start_date = pd.to_datetime(request.start_date, utc=True)
    end_date = pd.to_datetime(request.end_date, utc=True)
    calculator = SavingsCalculator(start_date, end_date)
    
    results = calculator.calculate_savings(
        start_date,
        end_date,
        request.commitment_amount
    )
    
    return SavingsResponse(**results)

@app.post("/find-optimal-savings", response_model=SavingsResponse)
async def find_optimal_savings(request: OptimalSavingsRequest) -> SavingsResponse:
    start_date = pd.to_datetime(request.start_date, utc=True)
    end_date = pd.to_datetime(request.end_date, utc=True)
    calculator = SavingsCalculator(start_date, end_date)
    
    results = calculator.find_optimal_commitment(tolerance=request.tolerance)
    return SavingsResponse(**results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)