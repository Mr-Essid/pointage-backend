from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from env_data import USERNAME_, PASSWORD_, HOSTNAME, DBNAME

engine = create_engine(f"mysql://{USERNAME_}:{PASSWORD_}@{HOSTNAME}:3306/{DBNAME}", echo=True)
base = declarative_base()
