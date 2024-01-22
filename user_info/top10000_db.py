from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.types import Integer, VARCHAR, CHAR, DECIMAL, BIGINT
import pandas as pd

password = ''
db_ip = 'localhost'

db_path = f'sof:{password}@{db_ip}:3306/sof'

engine = create_engine(f'mysql://{db_path}')


try:
    # 연결 시도
    with engine.connect():
        print("Database connection successful.")
except OperationalError as e:
    print(f"Database connection failed. Error: {e}")
    
df = pd.read_parquet('./data/24011822_user_info.parquet')
df = df[df.notnull().all(axis=1)]

# price는 'BP'라고 들어간 것이 있어서 VARCHAR로
dtype = {
    'rankNo' : Integer(),
    'LV' : Integer(),
    'nickName' : VARCHAR(20),
    'rankScore' : DECIMAL,
    'tier' : CHAR(6),
    'korRankTier' : VARCHAR(7),
    'price' : VARCHAR(20),
    'ouid' : CHAR(32)
}

df.to_sql(name='top10000', con=engine, index=False, dtype=dtype, if_exists='replace')
print('Data loading completed..')