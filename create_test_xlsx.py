import pandas as pd
from datetime import date

df = pd.DataFrame([
    {
        'date': '2026-05-29',
        'channel': '이랜드리테일',
        'store': '테스트점',
        'brand': '위라이크패션',
        'sales_amount': 123456,
    }
])
df.to_excel('test_upload.xlsx', index=False)
print('Wrote test_upload.xlsx')
