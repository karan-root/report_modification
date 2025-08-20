from typing import List, Optional, Dict, Tuple, Any

import requests
import questionary
import pandas as pd
from openpyxl.styles import Alignment

import config

# --- Helper & Utility Functions ---

def _adjust_column_widths(worksheet, df: pd.DataFrame, startrow: int) -> None:
    """Helper to set column widths with wrapping."""
    wrap_alignment = Alignment(wrap_text=True, vertical='top')
    MAX_WIDTH = 60
    for i, col_name in enumerate(df.columns, 1):
        column_letter = chr(64 + i)
        max_len = max(df[col_name].astype(str).map(len).max(), len(col_name)) + 3
        worksheet.column_dimensions[column_letter].width = min(max_len, MAX_WIDTH)
        for row_idx in range(startrow + 1, startrow + 1 + len(df)):
            worksheet.cell(row=row_idx, column=i).alignment = wrap_alignment

def get_report_data(api_key: str, report_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a specific report from the Feroot API."""
    try:
        url = f"{config.REPORTS_API_URL}{report_id}"
        response = requests.get(url, headers={"X-Api-Key": api_key})
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {e}")
        return None

def prompt_for_preferences() -> Tuple[Optional[List[str]], Optional[str], Optional[str]]:
    """Prompts the user for report columns, file type, and filename."""
    column_display_names = [details[0] for details in config.COLUMN_MAP.values()]
    selected_display = questionary.checkbox("Select columns for the report:", choices=column_display_names).ask()
    if selected_display is None: return None, None, None

    reverse_map = {v[0]: k for k, v in config.COLUMN_MAP.items()}
    selected_keys = [reverse_map[name] for name in selected_display]

    file_type = questionary.select("Select the output file type:", choices=["Excel (.xlsx)", "CSV (.csv)"]).ask()
    if file_type is None: return None, None, None
    file_type_key = 'excel' if 'Excel' in file_type else 'csv'

    filename = questionary.text("Enter the desired filename (without extension):", default="report").ask()
    if filename is None: return None, None, None

    return selected_keys, file_type_key, filename
