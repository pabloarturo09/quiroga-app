from app.database import db

class InventoryItem:
    
    @staticmethod
    def create_table():
        """Create inventory_items table if it doesn't exist"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_items (
                    id SERIAL PRIMARY KEY,
                    identificador TEXT NOT NULL,
                    item_type VARCHAR(50) NOT NULL,
                    brand VARCHAR(100),
                    model VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)