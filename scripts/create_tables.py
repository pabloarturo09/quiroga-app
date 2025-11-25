import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.models.user import User
from app.models.reservation import Reservation
from app.models.item import InventoryItem

def main():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        User.create_table()
        print("User table created successfully.")
        Reservation.create_table()
        print("Reservation table created successfully.")
        InventoryItem.create_table()
        print("InventoryItem table created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
