"""
Converts Google service account JSON to valid Streamlit TOML secrets.
Writes to ~/Desktop/streamlit_secrets.toml — open it, select all, copy, paste.
Usage:  python3 make_secrets.py ~/Downloads/scalper-dashboard-628a9803f53b.json
"""
import json, sys
from pathlib import Path

path = sys.argv[1] if len(sys.argv) > 1 else \
       "/Users/melfranklin/Downloads/scalper-dashboard-628a9803f53b.json"

with open(path) as f:
    creds = json.load(f)

out = Path.home() / "Desktop" / "streamlit_secrets.toml"

with open(out, "w") as f:
    f.write("[gcp_service_account]\n")
    for k, v in creds.items():
        if k == "private_key":
            # Use triple-quoted TOML string so real newlines are preserved cleanly
            f.write(f'private_key = """{v}"""\n')
        elif isinstance(v, str):
            escaped = v.replace('"', '\\"')
            f.write(f'{k} = "{escaped}"\n')
        else:
            f.write(f'{k} = {json.dumps(v)}\n')
    f.write("\n[google_sheets]\n")
    f.write('spreadsheet_id = "1mc7i0K6bUHgIv7zC4thqAMAwQr_BJcw4ugaBx0E6zRE"\n')

print(f"✅ Written to: {out}")
print("Next: open that file, Select All, Copy, paste into Streamlit secrets box.")
