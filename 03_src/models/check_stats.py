import pandas as pd
test_data_path = r"C:\Users\Lenovo\Desktop\DAP391_project\01_data\train_test\test_data.csv"
df = pd.read_csv(test_data_path)
print(df[['Recency', 'Frequency', 'Monetary']].describe())
