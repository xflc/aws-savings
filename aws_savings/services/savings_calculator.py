import pandas as pd
from pathlib import Path
from aws_savings.utils.utils import get_within_and_outside_budget_expenses

class SavingsCalculator:
    def __init__(self, start_date: pd.Timestamp, end_date: pd.Timestamp):
        data_dir = Path("aws_savings/data")
        self.saving_plans = self._load_saving_plans(data_dir / "savingsplanrates.csv")
        self.curr_ec2 = self._load_current_usage(data_dir / "currfile.csv")
        self.start_date = start_date
        self.end_date = end_date
        # Pre-filter usage data to improve performance in subsequent calculations
        self.usage_df = self.curr_ec2.query("start_time >= @start_date and end_time <= @end_date")

    def _load_saving_plans(self, file_path):
        saving_plans = pd.read_csv(file_path).drop(
            [
                "purchaseoption", "plantype", "sku", "ratecode", "unit",
                "contractlength", "rate_type", "discountedsku", "servicecode"
            ],
            axis=1,
        )
        # Filter for EC2 instances. I believe these are the correct operations, but i might be wrong here
        # This should include both regular and dedicated host instances (:0002)
        return saving_plans.query(
            "operation in ['RunInstances','RunInstances:0002', 'Hourly']"
        )

    def _load_current_usage(self, file_path):
        curr = pd.read_csv(file_path, sep="|").drop(["lineitem/lineitemdescription", "lineitem/productcode"], axis=1)
        curr.columns = [
            "operation", "usagetype", "timeinterval",
            "usageamount", "ondemandrate"
        ]
        
        # Filter for EC2 instances. I believe these are the correct operations, but i might be wrong here
        # This should include both regular and dedicated host instances (:0002)
        curr_ec2 = curr.query("operation in ['RunInstances','RunInstances:0002', 'Hourly']")
        # TODO: Confirm  if UTC timezone is the correct choice for this data
        curr_ec2[["start_time", "end_time"]] = curr_ec2.timeinterval.str.split("/", expand=True)
        curr_ec2["start_time"] = pd.to_datetime(curr_ec2.start_time, utc=True)
        curr_ec2["end_time"] = pd.to_datetime(curr_ec2.end_time, utc=True)
        return curr_ec2

    def calculate_savings(self, start_date: pd.Timestamp, end_date: pd.Timestamp, commitment_amount: float):
        ec2_calculated_spenditure = (
            self.usage_df.merge(self.saving_plans, on=["operation", "usagetype"], how="left")
            # Sort by time and savings percentage to prioritize best savings
            .sort_values(["end_time", "perc_savings"], ascending=[True, False])
            .assign(discount_price_cumulative=lambda df: (df.rate * df.usageamount).cumsum())
            .assign(haswithin_dicount_budget=lambda df: df.discount_price_cumulative <= commitment_amount)
        )

        # Calculate costs for instances within and outside budget for each hour
        within_outside_budget = ec2_calculated_spenditure.groupby("start_time").apply(
            get_within_and_outside_budget_expenses, commitment_amount=commitment_amount
        )

        # Calculate total hours in the period for budget calculations
        all_possible_hours = (end_date - start_date).total_seconds() / 3600
        total_commited_budget_in_all_hours = commitment_amount * all_possible_hours
        
        with_discount_spent = within_outside_budget.within_budget.sum()
        without_discount_spent = within_outside_budget.outside_budget.sum()
        equivalent_without_discount = within_outside_budget.price_without_discount.sum()

        used_commited_budget_perc = with_discount_spent * 100 / total_commited_budget_in_all_hours
        savings = 100 * (1 - (total_commited_budget_in_all_hours + without_discount_spent) / equivalent_without_discount)

        return {
            "used_committed_budget_percentage": used_commited_budget_perc,
            "extra_on_demand_cost": without_discount_spent,
            "total_cost": total_commited_budget_in_all_hours + without_discount_spent,
            "cost_without_discount": equivalent_without_discount,
            "savings_percentage": savings
        }

    def find_optimal_commitment(self, tolerance: float = 0.5) -> dict:
        """
        Find the optimal commitment amount using binary search for the initialized date range.
        Returns the commitment amount that provides the best balance of savings and utilization.
        
        Args:
            tolerance: The minimum difference between max and min commitment to continue searching
        """
        max_commitment = (self.usage_df.usageamount * self.usage_df.ondemandrate).max()
        min_commitment = 0.0
        
        # Binary search for optimal commitment amount
        while (max_commitment - min_commitment) > tolerance:
            mid_commitment = (min_commitment + max_commitment) / 2
            result = self.calculate_savings(self.start_date, self.end_date, mid_commitment)
            
            # Adjust search range based on budget utilization
            # Target is ~95% utilization for optimal efficiency
            if result['used_committed_budget_percentage'] < 95:
                max_commitment = mid_commitment
            else:
                min_commitment = mid_commitment

            # Early exit if we're very close to 100% utilization
            if abs(result['used_committed_budget_percentage'] - 100) < 1:
                break

        final_result = self.calculate_savings(self.start_date, self.end_date, mid_commitment)
        return {
            'optimal_commitment': mid_commitment,
            **final_result
        }
