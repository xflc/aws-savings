import numpy as np
import pandas as pd
OUTSIDE_BUDGET = "outside_budget"
WITHIN_BUDGET = "within_budget"

def get_within_and_outside_budget_expenses(df_, commitment_amount):
    """Calculate the cost for all instances within and outside the budget."""
    df_with_budget = df_.assign(
        discount_price_cumulative=lambda df: (df.rate * df.usageamount).cumsum(),
        od_price=lambda df: df.ondemandrate * df.usageamount,
        is_within_dicount_budget=lambda df: df.discount_price_cumulative <= commitment_amount,
    )

    def determine_cost_based_on_budget(df):
        """Get discount price or On Demand price depending on the budget at each row."""
        return df.discount_price_cumulative.max() if df.is_within_dicount_budget.any() else df.od_price.sum()

    cost_within_without_discount = df_with_budget.groupby("is_within_dicount_budget").apply(
        lambda df: determine_cost_based_on_budget(df)
    )
    cost_within_without_discount.index = [WITHIN_BUDGET if x else OUTSIDE_BUDGET for x in cost_within_without_discount.index]
    if OUTSIDE_BUDGET in cost_within_without_discount.index and pd.notna(cost_within_without_discount[OUTSIDE_BUDGET]):
        missing_to_budget = (
            commitment_amount - cost_within_without_discount[WITHIN_BUDGET]
            if WITHIN_BUDGET in cost_within_without_discount.index
            else commitment_amount
        )
        to_move_fom_outside_to_within = np.min([missing_to_budget, cost_within_without_discount[OUTSIDE_BUDGET]])

        cost_within_without_discount[WITHIN_BUDGET] = (
            cost_within_without_discount[WITHIN_BUDGET] + to_move_fom_outside_to_within
            if WITHIN_BUDGET in cost_within_without_discount.index
            else to_move_fom_outside_to_within
        )
        cost_within_without_discount[OUTSIDE_BUDGET] -= to_move_fom_outside_to_within

    
    cost_within_without_discount["price_without_discount"] = df_with_budget.od_price.sum()
    return cost_within_without_discount