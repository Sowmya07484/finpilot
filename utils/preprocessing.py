import pandas as pd


def load_transactions(file_source):
    """
    Load transaction data from CSV, Excel,
    file path, or Streamlit UploadedFile.
    """

    file_name = getattr(file_source, "name", str(file_source))

    if file_name.lower().endswith(".csv"):
        df = pd.read_csv(file_source)

    elif file_name.lower().endswith(".xlsx"):
        df = pd.read_excel(file_source)

    else:
        raise ValueError("Unsupported file format.")

    return clean_transactions(df)


def clean_transactions(df):
    """
    Clean and standardize transaction data.
    """

    df = df.copy()

    df.columns = df.columns.str.strip()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

    if "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(
            df["Amount"],
            errors="coerce"
        )

    df = df.dropna(
        subset=["Date", "Amount"]
    )

    if "Transaction Type" in df.columns:
        df["Transaction Type"] = (
            df["Transaction Type"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    df["Month"] = (
        df["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df