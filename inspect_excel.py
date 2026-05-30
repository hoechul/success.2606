import pandas as pd

df = pd.read_excel('C:/Users/admin/Desktop/test.xlsx', sheet_name=0)
print("=== 컬럼명 ===")
print(list(df.columns))
print("\n=== 첫 3개 행 ===")
print(df.head(3))
print("\n=== 각 컬럼의 정규화 후 이름 ===")
for col in df.columns:
    norm = str(col).strip().lower().replace(' ', '').replace('_', '').replace('-', '')
    print(f"{col:20} -> {norm}")
