def calculate_monthly_savings(
    monthly_income,
    monthly_expenses
):
    """Calculate average monthly savings."""

    return monthly_income - monthly_expenses


def calculate_goal_timeline(
    goal_amount,
    monthly_savings
):
    """
    Estimate how many months are needed
    to reach a financial goal.
    """

    if goal_amount <= 0:
        return 0

    if monthly_savings <= 0:
        return None

    return goal_amount / monthly_savings


def calculate_what_if(
    current_monthly_spending,
    new_monthly_spending,
    current_monthly_savings,
    goal_amount
):
    """
    Calculate the effect of changing a spending category
    on savings and financial-goal timeline.
    """

    monthly_reduction = (
        current_monthly_spending
        - new_monthly_spending
    )

    new_monthly_savings = (
        current_monthly_savings
        + monthly_reduction
    )

    current_timeline = calculate_goal_timeline(
        goal_amount,
        current_monthly_savings
    )

    new_timeline = calculate_goal_timeline(
        goal_amount,
        new_monthly_savings
    )

    months_saved = None

    if (
        current_timeline is not None
        and new_timeline is not None
    ):
        months_saved = (
            current_timeline
            - new_timeline
        )

    return {
        "monthly_reduction": monthly_reduction,
        "new_monthly_savings": new_monthly_savings,
        "current_timeline": current_timeline,
        "new_timeline": new_timeline,
        "months_saved": months_saved
    }