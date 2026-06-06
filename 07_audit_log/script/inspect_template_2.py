import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
tpl = r'C:\Users\Lenovo\Downloads\Report Templates-20260603\AI_AuditLog_Template_DAP391m.xlsx'

xl = pd.ExcelFile(tpl)
for sheet in xl.sheet_names:
    print(f"\n--- Sheet: {sheet} ---")
    df = pd.read_excel(tpl, sheet_name=sheet, header=None)
    for i in range(min(5, len(df))):
        row = df.iloc[i].tolist()
        # Drop nan to see what the row actually contains
        row_clean = [str(x) for x in row if pd.notna(x)]
        if row_clean:
            print(f"Row {i}: {row_clean}")
