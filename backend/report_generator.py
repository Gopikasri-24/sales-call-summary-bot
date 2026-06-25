import os
from datetime import datetime

# ----------------------------------------
# Reports Folder
# ----------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPORT_FOLDER = os.path.join(BASE_DIR, "..", "reports")


# ----------------------------------------
# Generate Sales Call Report
# ----------------------------------------

def generate_report(
    transcript,
    summary,
    sentiment,
    action_items,
    customer_needs
):
    # Create reports folder if it doesn't exist
    os.makedirs(REPORT_FOLDER, exist_ok=True)

    filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    report_path = os.path.join(REPORT_FOLDER, filename)

    with open(report_path, "w", encoding="utf-8") as file:

        file.write("=" * 60 + "\n")
        file.write("           SALES CALL SUMMARY REPORT\n")
        file.write("=" * 60 + "\n\n")

        file.write(f"Generated On : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n\n")

        # --------------------------------
        # Sentiment
        # --------------------------------
        file.write("SENTIMENT\n")
        file.write("-" * 60 + "\n")
        file.write(f"{sentiment}\n\n")

        # --------------------------------
        # AI Summary
        # --------------------------------
        file.write("AI SUMMARY\n")
        file.write("-" * 60 + "\n")
        file.write(summary + "\n\n")

        # --------------------------------
        # Customer Needs
        # --------------------------------
        file.write("CUSTOMER NEEDS\n")
        file.write("-" * 60 + "\n")

        if customer_needs:
            for i, need in enumerate(customer_needs, start=1):
                file.write(f"{i}. {need}\n")
        else:
            file.write("No customer needs identified.\n")

        file.write("\n")

        # --------------------------------
        # Action Items
        # --------------------------------
        file.write("ACTION ITEMS\n")
        file.write("-" * 60 + "\n")

        if action_items:
            for i, item in enumerate(action_items, start=1):
                file.write(f"{i}. {item}\n")
        else:
            file.write("No action items found.\n")

        file.write("\n")

        # --------------------------------
        # Transcript
        # --------------------------------
        file.write("ORIGINAL TRANSCRIPT\n")
        file.write("-" * 60 + "\n")
        file.write(transcript)

        file.write("\n\n")
        file.write("=" * 60 + "\n")
        file.write("End of Report\n")
        file.write("=" * 60 + "\n")

    return report_path