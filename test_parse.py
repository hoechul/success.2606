import sys
sys.path.insert(0, 'c:/Users/admin/Desktop/welike')

from sales_data import read_sales_excel
from io import BytesIO

try:
    df = read_sales_excel('C:/Users/admin/Desktop/test.xlsx')
    print("=== 파싱 성공 ===")
    print(f"총 행: {len(df)}")
    print(f"\n데이터 샘플 (처음 5행):")
    print(df.head(5))
    print(f"\n컬럼: {list(df.columns)}")
except Exception as e:
    print(f"=== 파싱 실패 ===")
    print(f"오류: {e}")
