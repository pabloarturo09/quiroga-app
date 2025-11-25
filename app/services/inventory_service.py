from app.database import db

class InventoryService:
    
    @staticmethod
    @staticmethod
    def get_all_items(page=1, per_page=15, search=None, item_type=None, status=None):
        """Get all inventory items with pagination and filtering"""
        query = "SELECT * FROM inventory_items WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM inventory_items WHERE 1=1"
        params = []
        
        if search:
            query += " AND identificador ILIKE %s"
            count_query += " AND identificador ILIKE %s"
            params.append(f"%{search}%")
        
        if item_type:
            query += " AND item_type = %s"
            count_query += " AND item_type = %s"
            params.append(item_type)
        
        if status:
            query += " AND status = %s"
            count_query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        with db.get_cursor() as cursor:
            cursor.execute(count_query, params[:len(params)-2])
            total_count = cursor.fetchone()[0]
            
            cursor.execute(query, params)
            items = cursor.fetchall()
            
            return {
                'items': [dict(item) for item in items],
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }
    
    @staticmethod
    def get_item_by_id(item_id):
        """Get inventory item by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM inventory_items WHERE id = %s
            """, (item_id,))
            item = cursor.fetchone()
            return dict(item) if item else None
    
    @staticmethod
    def create_item(identificador, item_type, brand=None, model=None, status='available'):
        """Create new inventory item"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO inventory_items (identificador, item_type, brand, model, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """, (identificador, item_type, brand, model, status))
            item = cursor.fetchone()
            return dict(item) if item else None
    
    @staticmethod
    def update_item(item_id, **kwargs):
        """Update inventory item"""
        allowed_fields = ['identificador', 'item_type', 'brand', 'model', 'status']
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f"{field} = %s")
                params.append(value)
        
        if not updates:
            return None
        
        params.append(item_id)
        
        with db.get_cursor() as cursor:
            cursor.execute(f"""
                UPDATE inventory_items 
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING *
            """, params)
            item = cursor.fetchone()
            return dict(item) if item else None
    
    @staticmethod
    def delete_item(item_id):
        """Delete inventory item"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                DELETE FROM inventory_items 
                WHERE id = %s
                RETURNING id
            """, (item_id,))
            deleted = cursor.fetchone()
            return bool(deleted)
    
    @staticmethod
    def get_items_by_type(item_type, page=1, per_page=15):
        """Get inventory items by type with pagination"""
        return InventoryService.get_all_items(page=page, per_page=per_page, item_type=item_type)

    @staticmethod
    def get_items_by_status(status, page=1, per_page=15):
        """Get inventory items by status with pagination"""
        return InventoryService.get_all_items(page=page, per_page=per_page, status=status)

    @staticmethod
    def get_available_items(page=1, per_page=15):
        """Get all available inventory items with pagination"""
        return InventoryService.get_all_items(page=page, per_page=per_page, status='available')
    
    @staticmethod
    def get_item_types_count():
        """Get count of items by type"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT item_type, COUNT(*) as count
                FROM inventory_items
                GROUP BY item_type
            """)
            result = cursor.fetchall()
            return {row['item_type']: row['count'] for row in result}
    
    @staticmethod
    def get_status_count():
        """Get count of items by status"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM inventory_items
                GROUP BY status
            """)
            result = cursor.fetchall()
            return {row['status']: row['count'] for row in result}
