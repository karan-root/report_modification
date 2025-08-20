# config.py
import os
from typing import Dict, Tuple

# --- Core API Configuration ---
# API key is passed via environment variable: FEROOT_API_KEY="XYZ" python main.py OR prompted for
API_KEY = os.getenv("FEROOT_API_KEY", "your-api-key-here")
COLUMN_MAP: Dict[str, Tuple[str, str]] = {
    'name': ('Script Name', 'name'),
    'url': ('URL of the Script', 'url'),
    'origin': ('Script Origin', 'origin'),
    'scan': ('Vulnerability Scan', 'vulnerabilityScanResult'),
    'auth': ('Authorization Status', 'authorization'),
    'purpose': ('Justification of Purpose', 'justificationOfPurpose'),
}
REPORTS_API_URL = "https://app.feroot.com/api/v1/platform/compliance/reports/"
