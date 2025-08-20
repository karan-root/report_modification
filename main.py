"""
A command-line tool to generate PCI compliance reports from the Feroot API.

This script prompts the user for their API key and report preferences,
fetches the data, and generates a report in either CSV or a multi-part
Excel format.
"""
import questionary

import utils
from report_generator import ReportGenerator

# --- Main Execution ---
def main():
    """Main function to run the report generation tool."""
    print("--- Feroot PCI Report Generator ---")
    try:
        api_key = questionary.password("Please enter your Feroot API Key:").ask()
        if not api_key:
            print("API Key is required. Exiting. 👋")
            return

        report_id = questionary.text("Please enter the Report ID (from the URL):").ask()
        if not report_id:
            print("Report ID is required. Exiting. 👋")
            return

        selected_columns, file_type, filename = utils.prompt_for_preferences()
        if not all([selected_columns, file_type, filename]):
            print("Report generation cancelled. Exiting. 👋")
            return

        print(f"\nFetching report data for ID: {report_id}...")
        report_data = utils.get_report_data(api_key, report_id)

        if report_data:
            generator = ReportGenerator(report_data)
            if file_type == 'excel':
                generator.generate_excel(selected_columns, filename)
            elif file_type == 'csv':
                generator.generate_csv(selected_columns, filename)

    except (KeyboardInterrupt, TypeError): # TypeError catches Ctrl+C in questionary password
        print("\n\nOperation cancelled by user. Exiting. 👋")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
