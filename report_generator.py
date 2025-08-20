from typing import Dict, List, Any

import pandas as pd
from openpyxl.styles import Font

import config
import utils

class ReportGenerator:
    """Encapsulates all logic for building and writing report files."""

    def __init__(self, data: Dict[str, Any]):
        """
        Initializes the generator with the report data from the API.

        Args:
            data: The raw JSON from the Feroot API.
        """
        self.data = data
        self.scripts = self.data.get('content', {}).get('scripts', [])
        # Create a lookup map for script details, used by the assets table.
        self._script_lookup = {s['scriptId']: s for s in self.scripts}

    def _build_scripts_df(self, selected_columns: List[str]) -> pd.DataFrame:
        """Builds the main Scripts Details DataFrame based on user selections."""
        headers = [config.COLUMN_MAP[col][0] for col in selected_columns]
        table_data = []
        for script in self.scripts:
            row_data = [script.get(config.COLUMN_MAP[col][1], 'N/A') for col in selected_columns]
            table_data.append(row_data)
        return pd.DataFrame(table_data, columns=headers)

    def _build_headers_df(self) -> pd.DataFrame:
        """Builds the HTTP Headers DataFrame."""
        headers_data = self.data.get('content', {}).get('headers', [])
        if not headers_data:
            return pd.DataFrame()

        df = pd.DataFrame(headers_data)
        return df.rename(columns={'name': 'Header Name', 'value': 'Header Value', 'authorized': 'Authorization Status'})

    def _build_data_assets_df(self) -> pd.DataFrame:
        """Builds the Data Assets DataFrame by cross-referencing scripts."""
        data_assets = self.data.get('content', {}).get('dataAssets', [])
        if not data_assets:
            return pd.DataFrame()

        asset_table_data = []
        for asset in data_assets:
            asset_name = asset.get('name', 'Unknown Asset')
            for script_ref in asset.get('scripts', []):
                script_id = script_ref.get('scriptId')
                details = self._script_lookup.get(script_id, {})
                access_level = "Read" if script_ref.get('read') else "Presence"
                asset_table_data.append({
                    "Data Asset": asset_name,
                    "Script Name": details.get('name', 'Unknown Script'),
                    "Script URL": details.get('url', 'N/A'),
                    "Access Level": access_level,
                })
        return pd.DataFrame(asset_table_data)

    def generate_csv(self, selected_columns: List[str], filename: str) -> None:
        """Generates the report as a single-table CSV file."""
        scripts_df = self._build_scripts_df(selected_columns)
        scripts_df.to_csv(f"{filename}.csv", index=False, encoding='utf-8')
        print(f"\n✅ Success! Your report has been generated: {filename}.csv")

    def generate_excel(self, selected_columns: List[str], filename: str) -> None:
        """Generates a multi-part, formatted Excel report."""
        with pd.ExcelWriter(f"{filename}.xlsx", engine='openpyxl') as writer:
            sheet_name = 'PCI Compliance Report'
            pd.DataFrame([]).to_excel(writer, sheet_name=sheet_name)
            worksheet = writer.sheets[sheet_name]
            bold_font = Font(bold=True, name='Calibri')

            # --- Part 1: Write Custom Header Content ---
            stats = self.data.get('content', {}).get('stats', {})
            total_scripts = stats.get('totalScripts', 0)
            other_scripts = total_scripts - (stats.get('firstPartyScripts', 0) + stats.get('thirdPartyScripts', 0))
            header_content = [
                ("Report Name", self.data.get('title', 'N/A')),
                ("URL of the Webpage", self.data.get('page', {}).get('url', 'N/A')),
                None,
                ("Date", pd.to_datetime("now").strftime("%B %d, %Y")),
                ("Time", pd.to_datetime("now").strftime("%I:%M %p EDT")),
                None,
                ("Total Number of Scripts", stats.get('totalScripts', 'N/A')),
                ("Other Scripts", other_scripts),
                None,
                ("Total Vulnerabilities", stats.get('totalVulnerabilities', 'N/A')),
            ]
            current_row = 1
            for item in header_content:
                if item is None:
                    current_row += 1
                    continue
                label, value = item
                worksheet[f'A{current_row}'].value = f"{label}:"
                worksheet[f'A{current_row}'].font = bold_font
                worksheet[f'B{current_row}'].value = value
                current_row += 1

            next_row = current_row + 2

            # --- Part 2 & Onwards: Write DataFrame Tables ---
            tables = {
                "Scripts Details": self._build_scripts_df(selected_columns),
                "HTTP Headers": self._build_headers_df(),
                "Cardholder Data Asset Access": self._build_data_assets_df(),
            }

            for title, df in tables.items():
                if df.empty:
                    continue
                worksheet[f'A{next_row}'].value = title
                worksheet[f'A{next_row}'].font = bold_font
                df.to_excel(writer, sheet_name=sheet_name, startrow=next_row + 1, index=False)
                utils._adjust_column_widths(worksheet, df, startrow=next_row + 1)
                next_row += len(df) + 4 # Add space for the next table

        print(f"\n✅ Success! Your report has been generated: {filename}.xlsx")
