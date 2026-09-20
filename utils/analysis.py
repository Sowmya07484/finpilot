import pandas as pd


def get_income(df):
    """Calculate total recorded income."""

    return df[
        df["Transaction Type"] == "credit"
    ]["Amount"].sum()


def get_expenses(df):
    """Calculate total recorded expenses."""

    return df[
        df["Transaction Type"] == "debit"
    ]["Amount"].sum()


def get_net_cash_flow(df):
    """Calculate income minus expenses."""

    return get_income(df) - get_expenses(df)


def get_category_spending(df):
    """Return spending totals by category."""

    expenses = df[
        df["Transaction Type"] == "debit"
    ]

    return (
        expenses
        .groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


def get_monthly_summary(df):
    """Return monthly income and expense totals."""

    summary = (
        df.groupby(
            ["Month", "Transaction Type"]
        )["Amount"]
        .sum()
        .reset_index()
    )

    return summary


def get_monthly_expenses(df):
    """Return total expenses for each month."""

    expenses = df[
        df["Transaction Type"] == "debit"
    ]

    return (
        expenses
        .groupby("Month")["Amount"]
        .sum()
        .reset_index(name="Expenses")
    )


def get_monthly_comparison(df):
    """Compare spending with the previous month."""

    monthly = get_monthly_expenses(df)

    monthly["Change"] = (
        monthly["Expenses"].diff()
    )

    monthly["Change_%"] = (
        monthly["Expenses"]
        .pct_change()
        .mul(100)
    )

    return monthly


def get_recurring_expenses(
    df,
    minimum_months=3
):
    """
    Identify expenses appearing
    across multiple months.
    """

    expenses = df[
        df["Transaction Type"] == "debit"
    ].copy()

    recurring = (
        expenses
        .groupby("Description")
        .agg(
            Months=("Month", "nunique"),
            Transactions=("Description", "count"),
            Average_Amount=("Amount", "mean"),
            Total_Spent=("Amount", "sum")
        )
        .reset_index()
    )

    recurring = recurring[
        recurring["Months"] >= minimum_months
    ]

    return recurring.sort_values(
        ["Months", "Average_Amount"],
        ascending=[False, False]
    )


def get_upcoming_obligations(df):
    """
    Estimate recurring financial obligations
    using the most recent transaction patterns.
    """

    recurring = get_recurring_expenses(df)

    if recurring.empty:
        return recurring

    obligations = recurring[
        [
            "Description",
            "Average_Amount",
            "Months"
        ]
    ].copy()

    obligations["Average_Amount"] = (
        obligations["Average_Amount"].round(2)
    )

    return obligations


def detect_unusual_spending(
    df,
    threshold=2.0
):
    """
    Detect unusually large transactions using
    category-level mean and standard deviation.
    """

    expenses = df[
        df["Transaction Type"] == "debit"
    ].copy()

    if expenses.empty:
        return expenses

    category_stats = (
        expenses
        .groupby("Category")["Amount"]
        .agg(["mean", "std"])
        .reset_index()
    )

    expenses = expenses.merge(
        category_stats,
        on="Category",
        how="left"
    )

    expenses["Z_Score"] = (
        (expenses["Amount"] - expenses["mean"])
        / expenses["std"].replace(0, pd.NA)
    )

    unusual = expenses[
        expenses["Z_Score"].abs() >= threshold
    ].copy()

    return unusual.sort_values(
        "Z_Score",
        ascending=False
    )


def get_budget_status(
    df,
    monthly_budget
):
    """Compare latest month's spending with budget."""

    if monthly_budget <= 0:
        return {
            "budget": monthly_budget,
            "spent": 0,
            "remaining": 0,
            "percentage_used": 0
        }

    latest_month = df["Month"].max()

    spent = df[
        (df["Month"] == latest_month)
        & (df["Transaction Type"] == "debit")
    ]["Amount"].sum()

    remaining = monthly_budget - spent

    percentage_used = (
        spent / monthly_budget
    ) * 100

    return {
        "budget": monthly_budget,
        "spent": spent,
        "remaining": remaining,
        "percentage_used": percentage_used
    }
def generate_financial_insights(df, monthly_budget=None):
    """Generate personalized observations from transaction data."""

    insights = []

    category_data = get_category_spending(df)

    if not category_data.empty:
        top = category_data.iloc[0]

        insights.append(
            f"Your highest spending category is "
            f"{top['Category']} at ${top['Amount']:,.2f}."
        )

    comparison = get_monthly_comparison(df)

    if len(comparison) >= 2:
        latest = comparison.iloc[-1]

        if not pd.isna(latest["Change_%"]):
            if latest["Change"] > 0:
                insights.append(
                    f"Spending increased by "
                    f"${latest['Change']:,.2f} "
                    f"({latest['Change_%']:.1f}%) "
                    f"compared with the previous month."
                )
            elif latest["Change"] < 0:
                insights.append(
                    f"Spending decreased by "
                    f"${abs(latest['Change']):,.2f} "
                    f"({abs(latest['Change_%']):.1f}%) "
                    f"compared with the previous month."
                )

    recurring = get_recurring_expenses(df)

    if not recurring.empty:
        recurring_total = recurring["Average_Amount"].sum()

        insights.append(
            f"Detected recurring expenses average "
            f"${recurring_total:,.2f} per month."
        )

    if monthly_budget is not None:
        budget = get_budget_status(
            df,
            monthly_budget
        )

        if budget["remaining"] < 0:
            insights.append(
                "Your latest month's spending "
                "has exceeded the budget."
            )
        else:
            insights.append(
                f"You have ${budget['remaining']:,.2f} "
                "remaining in the current budget."
            )

    return insights
def generate_financial_insights(df, monthly_budget=None):
    """Generate personalized observations from transaction data."""

    insights = []

    category_data = get_category_spending(df)

    if not category_data.empty:
        top = category_data.iloc[0]

        insights.append(
            f"Your highest spending category is "
            f"{top['Category']} at ${top['Amount']:,.2f}."
        )

    comparison = get_monthly_comparison(df)

    if len(comparison) >= 2:
        latest = comparison.iloc[-1]

        if not pd.isna(latest["Change_%"]):

            if latest["Change"] > 0:
                insights.append(
                    f"Spending increased by "
                    f"${latest['Change']:,.2f} "
                    f"({latest['Change_%']:.1f}%) "
                    f"compared with the previous month."
                )

            elif latest["Change"] < 0:
                insights.append(
                    f"Spending decreased by "
                    f"${abs(latest['Change']):,.2f} "
                    f"({abs(latest['Change_%']):.1f}%) "
                    f"compared with the previous month."
                )

    recurring = get_recurring_expenses(df)

    if not recurring.empty:
        recurring_total = recurring["Average_Amount"].sum()

        insights.append(
            f"Detected recurring expenses average "
            f"${recurring_total:,.2f} per month."
        )

    if monthly_budget is not None:

        budget = get_budget_status(
            df,
            monthly_budget
        )

        if budget["remaining"] < 0:
            insights.append(
                "Your latest month's spending "
                "has exceeded the budget."
            )
        else:
            insights.append(
                f"You have ${budget['remaining']:,.2f} "
                "remaining in the current budget."
            )

    return insights