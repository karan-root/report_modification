# Overview

Simple script to remove column indicating PASS/FAIL in Feroot PCI Reports

# Dependencies
- Built using Python 3.13.5
- openpyxl

## Installation

1. Clone the repo
```bash
git clone https://github.com/karan-root/report_modification.git
cd report_modification
```

2. Create Virtual Env (optional), then install dependencies
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

## Run Script -- Ex for deleting Vuln Scan Result col from report
`python report_modification.py [PATH_FOR_DOWNLOADED_REPORT] [NEW_FILE_NAME] "Vulnerability Scan Result"`

If using `python3`:
`python3 report_modification.py [PATH_FOR_DOWNLOADED_REPORT] [NEW_FILE_NAME] "Vulnerability Scan Result"`

### Note
The last part of the command must exactly match the column string to be removed
