import pandas as pd


def detect_intent(question):
    question = question.lower().strip()

    if "spent the most" in question or "spend the most" in question:
        return "top_category"

    if "subscription" in question or "recurring" in question:
        return "recurring"

    if (
        "increased" in question
        or "increase" in question
        or "decreased" in question
        or "decrease" in question
        or "compared with last month" in question
        or "compared to last month" in question
    ):
        return "monthly_comparison"

    if "budget" in question or "committed" in question:
        return "budget"

    if "income" in question or "salary" in question:
        return "income"

    if "cash flow" in question or "cashflow" in question:
        return "cash_flow"

    if "expense" in question or "expenses" in question:
        return "expenses"

    if "unusual" in question or "abnormal" in question:
        return "unusual"

    if "goal" in question or "save" in question:
        return "goal"

    return "unknown"


def answer_question(question, df, analysis_functions):
    intent = detect_intent(question)

    # 1. TOP SPENDING
    if intent == "top_category":
        working_df = df.copy()

        if "this month" in question or "this month's" in question:
            latest_month = working_df["Month"].max()
            working_df = working_df[
                working_df["Month"] == latest_month
            ]

        category_data = analysis_functions["get_category_spending"](
            working_df
        )

        if category_data.empty:
            return "I couldn't find any expense data."

        top = category_data.iloc[0]

        if "this month" in question or "this month's" in question:
            return (
                f"In {top.get('Month', working_df['Month'].max())}, "
                f"your highest spending category was "
                f"{top['Category']} with "
                f"${top['Amount']:,.2f} spent."
            )

        return (
            f"Your highest spending category is "
            f"{top['Category']} with "
            f"${top['Amount']:,.2f} spent."
        )

    # 2. RECURRING / SUBSCRIPTIONS
    if intent == "recurring":
        recurring = analysis_functions["get_recurring_expenses"](df)

        if recurring.empty:
            return "I couldn't detect any recurring expenses."

        rows = recurring.head(8)

        response = "I found these recurring expenses:\n"

        for _, row in rows.iterrows():
            response += (
                f"• {row['Description']} — "
                f"average ${row['Average_Amount']:,.2f}\n"
            )

        return response

    # 3. MONTHLY COMPARISON
    if intent == "monthly_comparison":
        comparison = analysis_functions["get_monthly_comparison"](df)

        if len(comparison) < 2:
            return "There isn't enough monthly data for a comparison."

        latest = comparison.iloc[-1]

        if pd.isna(latest["Change_%"]):
            return "There isn't enough data for a comparison."

        if latest["Change"] > 0:
            return (
                f"Your spending increased by "
                f"${latest['Change']:,.2f} "
                f"({latest['Change_%']:.1f}%) "
                f"compared with the previous month."
            )

        if latest["Change"] < 0:
            return (
                f"Your spending decreased by "
                f"${abs(latest['Change']):,.2f} "
                f"({abs(latest['Change_%']):.1f}%) "
                f"compared with the previous month."
            )

        return "Your spending was unchanged compared with the previous month."

    # 4. INCOME
    if intent == "income":
        income = analysis_functions["get_income"](df)
        return f"Your recorded income is ${income:,.2f}."

    # 5. EXPENSES
    if intent == "expenses":
        expenses = analysis_functions["get_expenses"](df)
        return f"Your recorded expenses are ${expenses:,.2f}."

    # 6. CASH FLOW
    if intent == "cash_flow":
        cash_flow = analysis_functions["get_net_cash_flow"](df)

        if cash_flow > 0:
            return (
                f"Your net cash flow is ${cash_flow:,.2f}. "
                "Your recorded income is higher than your expenses."
            )

        if cash_flow < 0:
            return (
                f"Your net cash flow is -${abs(cash_flow):,.2f}. "
                "Your recorded expenses are higher than your income."
            )

        return "Your net cash flow is $0.00."

    # 7. UNUSUAL SPENDING
    if intent == "unusual":
        unusual = analysis_functions["detect_unusual_spending"](df)

        if unusual.empty:
            return "I didn't detect any unusually large transactions."

        rows = unusual.head(5)

        response = "I found some unusual spending:\n"

        for _, row in rows.iterrows():
            response += (
                f"• {row['Description']} — "
                f"${row['Amount']:,.2f} "
                f"({row['Category']})\n"
            )

        return response

    # 8. BUDGET
    if intent == "budget":
        return (
            "Your budget status is available in the "
            "Budget & Financial Goal section below. "
            "Set your monthly budget there to see how much "
            "you have spent, remaining budget, and percentage used."
        )

    # 9. GOAL
    if intent == "goal":
        savings = analysis_functions["get_net_cash_flow"](df)

        if savings <= 0:
            return (
                "Based on the recorded transactions, "
                "your current net cash flow is not positive, "
                "so a savings timeline cannot be estimated yet."
            )

        return (
            f"Your recorded net cash flow is ${savings:,.2f}. "
            "Use the Financial Goal and What-If Simulator sections "
            "to test how changes in spending could affect your goal."
        )

    # FALLBACK
    return (
        "I can help you analyze your spending, income, cash flow, "
        "recurring expenses, monthly changes, unusual spending, "
        "budgets, and financial goals."
    )