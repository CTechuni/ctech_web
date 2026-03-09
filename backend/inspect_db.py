
from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('events')
with open('db_columns.txt', 'w') as f:
    for column in columns:
        f.write(f"Column: {column['name']}, Type: {column['type']}\n")
