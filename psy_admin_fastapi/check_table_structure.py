from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('tests')
print('Tests表结构:')
for col in columns:
    print(f'  {col["name"]}: {col["type"]}')