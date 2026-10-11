
from src.database import Base, engine
from src import db_models  # Register the table definitions

def main():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    main()
