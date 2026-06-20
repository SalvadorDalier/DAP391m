import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

tpl = r'C:\Users\Lenovo\Downloads\Report Templates-20260603\AI_AuditLog_Template_DAP391m.xlsx'
current = r'C:\Users\Lenovo\Desktop\DAP391_project\07_audit_log\Audit_log.xlsx'

print("--- Template Sheet 1 (Row 1-5) ---")
df1 = pd.read_excel(tpl, sheet_name='1. Metadata & Summary', header=None)
print(df1.head(10))

print("\n--- Template Sheet 2 (Header at row index 1) ---")
df2 = pd.read_excel(tpl, sheet_name='2. Detailed Audit Log', header=1)
print(df2.columns.tolist())

print("\n--- Template Sheet 3 (Header at row index 1) ---")
df3 = pd.read_excel(tpl, sheet_name='3. Hallucination Detection', header=1)
print(df3.columns.tolist())

print("\n--- Template Sheet 4 (Header at row index 1) ---")
df4 = pd.read_excel(tpl, sheet_name='4. Self-Assessment Checklist', header=1)
print(df4.columns.tolist())

print("\n--- Current Data ---")
xl = pd.ExcelFile(current)
for sheet in xl.sheet_names:
    print(f"Sheet: {sheet}")
    df_c = pd.read_excel(current, sheet_name=sheet)
    print("Columns:", df_c.columns.tolist())
    print("Data rows:", len(df_c))
    if len(df_c) > 0:
        print(df_c.iloc[0].to_dict())
