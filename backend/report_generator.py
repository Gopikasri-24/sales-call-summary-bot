import os
from datetime import datetime

REPORT_FOLDER = "../reports"


def generate_report(transcript, summary, action_items, sentiment):
    if not os.path.exists(REPORT_FOLDER):
        os.makedirs(REPORT_FOLDER)

    filename = "sales_report_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
    file_path = os.path.join(REPORT_FOLDER, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("SALES CALL SUMMARY REPORT\n")
        file.write("=" * 40 + "\n\n")

        file.write("SUMMARY:\n")
        file.write(summary + "\n\n")

        file.write("SENTIMENT:\n")
        file.write(sentiment + "\n\n")

        file.write("ACTION ITEMS:\n")
        for i, item in enumerate(action_items, start=1):
            file.write(f"{i}. {item}\n")

        file.write("\nORIGINAL TRANSCRIPT:\n")
        file.write(transcript)

    return file_path