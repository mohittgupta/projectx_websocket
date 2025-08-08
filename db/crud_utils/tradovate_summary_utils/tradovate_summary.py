import asyncio
import os
import zipfile
import pandas as pd
import traceback
from datetime import datetime
from sqlalchemy import text
from config import logger
from db.database import db_session


async def fetch_user_data(from_date: str, to_date: str):
    try:
        from_date = datetime.strptime(from_date, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
        to_date = datetime.strptime(to_date, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")

        query = text("""
        WITH latest_payment AS (
            SELECT 
                user_id, 
                MAX(created) AS last_payment_date,
                MAX(subscription_type) AS last_payment_plan
            FROM payment_history
            GROUP BY user_id
        ), 
        trade_summary AS (
            SELECT 
                user_id, 
                MIN(trade_time) AS first_trade_time, 
                COUNT(trade_time) AS total_trades
            FROM trade_data
            GROUP BY user_id
        ),
        payment_summary AS (
            SELECT 
                user_id, 
                SUM(amount) AS total_payment_amount,
                COUNT(created) AS total_payments_made,
                STRING_AGG(DISTINCT TO_CHAR(created, 'YYYY-MM-DD HH24:MI:SS'), ', ') AS total_payment_dates
            FROM payment_history
            GROUP BY user_id
        )

        SELECT 
            lc.user_name AS "User Email", 
            lc.phone_no AS "Phone Number", 
            lc.source AS "Registration Source",
            lc.created AS "Registration Date",

            CASE 
                WHEN lc.mail_verified THEN 'True' 
                ELSE 'False' 
            END AS "Email Verified",

            lc.demo_expiry AS "Demo Expiry Date",

            CASE 
                WHEN referrer_lc.user_name IS NOT NULL THEN 'Yes' 
                ELSE 'No' 
            END AS "Was Referred?",
            referrer_lc.user_name AS "Referred By (Inviter)",

            STRING_AGG(DISTINCT user_referral_lc.user_name, ', ') AS "Users Referred (Invitees)",
            COUNT(DISTINCT user_referral_lc.user_name) AS "Total Referrals",

            CASE 
                WHEN lc.paid THEN 'True' 
                ELSE 'False' 
            END AS "Is Paid User?", 

            COALESCE(lp.last_payment_plan, 'None') AS "Current Payment Plan",
            lp.last_payment_date AS "Current Payment Date",
            lc.other_referral_code AS "Referral Code Used for Payment",

            COALESCE(ps.total_payment_amount, 0) AS "Total Payment Amount",
            COALESCE(ps.total_payments_made, 0) AS "Total Payments Made",
            COALESCE(ps.total_payment_dates, 'None') AS "Total Payment Dates",

            CASE 
                WHEN COUNT(tc.user_random_id) > 0 THEN 'True' 
                ELSE 'False' 
            END AS "Tradovate Account Linked",

            COUNT(DISTINCT tc.tradovate_account_name) AS "Number of Active Tradovate Accounts",
            STRING_AGG(DISTINCT tc.tradovate_account_name, ', ') AS "Tradovate Account Usernames",

            ts.first_trade_time AS "First Alert Sent",
            ts.total_trades AS "Total Alerts Sent",

            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM multi_accounts mc WHERE mc.user_random_id = lc.id
                ) THEN 'True' 
                ELSE 'False' 
            END AS "Manual Trade Copier Connected",

            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM multi_accounts mc
                    JOIN watch_client_order_id_map wc ON wc.master_token = mc.token
                    WHERE mc.user_random_id = lc.id
                ) THEN 'True' 
                ELSE 'False' 
            END AS "Sent Alert Through Manual Trade Copier"

        FROM login_central lc 

        LEFT JOIN login_central user_referral_lc 
            ON user_referral_lc.other_user_referral_code = lc.my_referral_code
        LEFT JOIN login_central referrer_lc 
            ON lc.other_user_referral_code = referrer_lc.my_referral_code
        LEFT JOIN latest_payment lp 
            ON lp.user_id = lc.id
        LEFT JOIN payment_summary ps 
            ON ps.user_id = lc.id
        LEFT JOIN tradovate_accounts tc 
            ON tc.user_random_id = lc.random_id AND tc.active = TRUE
        LEFT JOIN trade_summary ts 
            ON ts.user_id = lc.random_id  

        WHERE lc.created BETWEEN :from_date AND :to_date

        GROUP BY 
            lc.id, lc.user_name, lc.phone_no, lc.source, lc.created, lc.mail_verified, 
            lc.demo_expiry, lc.paid, lc.other_referral_code, referrer_lc.user_name,
            lp.last_payment_date, lp.last_payment_plan, ts.first_trade_time, ts.total_trades,
            ps.total_payment_amount, ps.total_payments_made, ps.total_payment_dates

        ORDER BY lc.created DESC;
        """)

        result = db_session.execute(query, {"from_date": from_date, "to_date": to_date})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        db_session.close()
        return df

    except Exception as e:
        logger.error(f"Exception in DB rollback start {traceback.format_exc()}")
        db_session.rollback()
        db_session.close()
        return None


def generate_summary(df, from_date, to_date):
    current_date = datetime.today().strftime('%Y-%m-%d')
    summary = {
        "Report Date Range": f"{from_date} to {to_date}",
        "Total Signups": len(df),
        "Total Verified Emails": (df["Email Verified"] == "True").sum(),
        "Total Unverified Emails": (df["Email Verified"] == "False").sum(),
        "Total Referred Users": (df["Was Referred?"] == "Yes").sum(),
        "Total Non-Referred Users": (df["Was Referred?"] == "No").sum(),
        "Total Paid Users": (df["Is Paid User?"] == "True").sum(),
        "Total Unpaid Users": (df["Is Paid User?"] == "False").sum(),
        "Total Active Trial Users (Not Paid)": (
                (df["Is Paid User?"] == "False") & (df["Demo Expiry Date"] >= current_date)
        ).sum(),
        "Total Expired Trial Users (Not Paid)": (
                (df["Is Paid User?"] == "False") & (df["Demo Expiry Date"] < current_date)
        ).sum(),
        "Total Users Who Sent Their First Alert": (df["First Alert Sent"].notna()).sum(),
        "Total Users Who Signed Up but Haven't Sent Their First Alert": (df["First Alert Sent"].isna()).sum(),
        "Total Users with Tradovate Linked Accounts": (df["Tradovate Account Linked"] == "True").sum(),
        "Total Users without Tradovate Linked Accounts": (df["Tradovate Account Linked"] == "False").sum(),
        "Total Users with Manual Trade Copier Linked": (df["Manual Trade Copier Connected"] == "True").sum(),
        "Total Users without Manual Trade Copier Linked": (df["Manual Trade Copier Connected"] == "False").sum(),
        "Total Users Who Sent Alerts via Manual Trade Copier": (
                    df["Sent Alert Through Manual Trade Copier"] == "True").sum(),
        "Total Users Who Did Not Send Alerts via Manual Trade Copier": (
                    df["Sent Alert Through Manual Trade Copier"] == "False").sum(),
        "Total Alerts Sent": df["Total Alerts Sent"].sum(),
        "Total Referrals Made by Users": (df["Was Referred?"] == "Yes").sum(),
        "Total Revenue Collected": df["Total Payment Amount"].sum()
    }

    return pd.DataFrame(summary.items(), columns=["Metric", "Value"])


def categorize_source(source):
    if not isinstance(source, str):  # Handle None or NaN values
        return "Unknown"

    source_lower = source.lower()  # Convert source to lowercase for case-insensitive matching

    # Discord variations
    if "discord" in source_lower or "algopro" in source_lower:
        return "Discord"
    elif source_lower.startswith("friend") or "frend" in source_lower or "mate" in source_lower:
        return "Friend"
    elif "google" in source_lower or "search" in source_lower or "searching" in source_lower:
        return "Google/Search"
    elif "twitter" in source_lower or source_lower == "x":
        return "Twitter/X"
    elif "youtube" in source_lower:
        return "YouTube"
    elif "telegram" in source_lower:
        return "Telegram"
    elif "reddit" in source_lower:
        return "Reddit"
    elif "tradingview" in source_lower or "trading view" in source_lower:
        return "TradingView"
    elif "forum" in source_lower:
        return "Forum"
    elif "ai" in source_lower or "chatgpt" in source_lower or "chatgbt" in source_lower or "grok" in source_lower:
        return "AI/ChatGPT"
    elif "stackoverflow" in source_lower:
        return "Stack Overflow"
    elif "website" in source_lower or "web" in source_lower:
        return "Website"
    elif "instagram" in source_lower:
        return "Instagram"
    elif "referral" in source_lower or "relative" in source_lower or "work associate" in source_lower:
        return "Referral"
    elif "trading" in source_lower or "trading group" in source_lower or "fxc" in source_lower:
        return "Trading Group"
    elif "myself" in source_lower:
        return "Myself"
    elif "nasir" in source_lower or "jonathan garcia" in source_lower:
        return "Individual Referral"
    elif "pornhub" in source_lower:
        return "Other"
    else:
        return source


def generate_source_summary(df):
    df["Categorized Source"] = df["Registration Source"].apply(categorize_source)

    source_summary = df.groupby("Categorized Source").agg(
        Total_Signups=("User Email", "count"),
        Total_Paid_Users=("Is Paid User?", lambda x: (x == "True").sum()),
        Total_Amount=("Total Payment Amount", "sum"),
        Total_Alerts_Sent=("Total Alerts Sent", "sum"),
        Avg_Alerts_Per_User=("Total Alerts Sent", "mean"),
        Total_Referrals=("Total Referrals", "sum"),
        Total_First_Alert_Users=("First Alert Sent", lambda x: x.notna().sum()),
        Total_Manual_Trade_Copier_Connected=("Manual Trade Copier Connected", lambda x: (x == "True").sum()),
        Total_Manual_Trade_Copier_Alerts=("Sent Alert Through Manual Trade Copier", lambda x: (x == "True").sum()),
    ).reset_index()

    if "Categorized Source" in df.columns:
        df.drop(columns=["Categorized Source"], inplace=True)

    return source_summary


def generate_referral_summary(df):
    # Ensure the column name matches exactly
    inviter_column = "Referred By (Inviter)"

    referral_summary = df.groupby(inviter_column).agg(
        Total_Referrals=("User Email", "count"),
        Paid_Referrals=("Is Paid User?", lambda x: (x == 'True').sum()),
        Total_Alerts_By_Referrals=("Total Alerts Sent", "sum"),
        Tradovate_Connected=("Tradovate Account Linked", lambda x: (x == 'True').sum()),
        Total_Amount=("Total Payment Amount", "sum"),
        Total_First_Alert_Users=("First Alert Sent", lambda x: x.notna().sum()),
        Total_Manual_Trade_Copier_Connected=("Manual Trade Copier Connected", lambda x: (x == 'True').sum()),
        Total_Manual_Trade_Copier_Alerts=("Sent Alert Through Manual Trade Copier", lambda x: (x == 'True').sum()),
    ).reset_index()

    return referral_summary


def generate_raw_source_summary(df):
    """Generates summary grouped by raw (original) sources without categorization"""
    source_summary = df.groupby("Registration Source").agg(
        Total_Signups=("User Email", "count"),
        Total_Paid_Users=("Is Paid User?", lambda x: (x == "True").sum()),
        Total_Amount=("Total Payment Amount", "sum"),
        Total_Alerts_Sent=("Total Alerts Sent", "sum"),
        Avg_Alerts_Per_User=("Total Alerts Sent", "mean"),
        Total_Referrals=("Total Referrals", "sum"),
        Total_First_Alert_Users=("First Alert Sent", lambda x: x.notna().sum()),
        Total_Manual_Trade_Copier_Connected=("Manual Trade Copier Connected", lambda x: (x == "True").sum()),
        Total_Manual_Trade_Copier_Alerts=("Sent Alert Through Manual Trade Copier", lambda x: (x == "True").sum()),
    ).reset_index()

    return source_summary


def save_data_to_excel(df, filename, from_date, to_date):
    """Save user data and summaries to an Excel file."""
    summary_df = generate_summary(df, from_date, to_date)
    source_summary_df = generate_source_summary(df)
    referral_summary_df = generate_referral_summary(df)
    detailed_source_summary_df = generate_raw_source_summary(df)

    try:
        with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="User Data", index=False)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            source_summary_df.to_excel(writer, sheet_name="Reg Source Summary", index=False)
            referral_summary_df.to_excel(writer, sheet_name="Referral Summary", index=False)
            detailed_source_summary_df.to_excel(writer, sheet_name="Raw Source Summary", index=False)
        logger.info(f"Excel file saved successfully: {filename}")
    except Exception as e:
        logger.error(f"Error saving Excel file: {e}")
        traceback.print_exc()


def blocking_generate_zip(df, from_date, to_date):
    try:
        path ='/tmp/'
        excel_filename = f"user_data_{from_date}_to_{to_date}.xlsx"
        logger.info(f"os path {os.getcwd()}")
        zip_filename = os.path.join(path, "user_data.zip")
        logger.info(f"zip_filename {zip_filename}  {path}")
        save_data_to_excel(df, excel_filename, from_date, to_date)
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(excel_filename, os.path.basename(excel_filename))
        return zip_filename
    except Exception as e:
        print(f"Error in blocking_generate_zip: {e}")
        raise e

async def save_to_zip(from_date: str, to_date: str):
    df = await fetch_user_data(from_date, to_date)
    if df is None or df.empty:
        return df, None
    zip_file_path = await asyncio.to_thread(blocking_generate_zip, df, from_date, to_date)
    return df, zip_file_path
