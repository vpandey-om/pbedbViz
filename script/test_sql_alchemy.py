import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

POSTGRES = {
    'user': 'vpandey',
    'pw': 'om16042020',
    'db': 'pbe_db',
    'host': 'localhost',
    'port': '5432',
}

DATABASE_URI='postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
# engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine(DATABASE_URI)
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("/Users/vikash/git-hub/Programming with python and Javascript/SQL/src3/flights.csv")
    reader = csv.reader(f)
    for origin, destination, duration in reader:
        db.execute("INSERT INTO flights (origin, destination, duration) VALUES (:origin, :destination, :duration)",
                    {"origin": origin, "destination": destination, "duration": duration})
        print(f"Added flight from {origin} to {destination} lasting {duration} minutes.")
    db.commit()

if __name__ == "__main__":
    main()
