from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:

    @staticmethod
    def authenticate(username, password):
        """Authenticate user"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, password_hash, is_admin, is_active
                FROM users 
                WHERE username = %s AND is_active = TRUE
            """, (username,))
            
            user = cursor.fetchone()
            if user and check_password_hash(user['password_hash'], password):
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'is_admin': user['is_admin']
                }
            return None
    
    @staticmethod
    def get_all_users(search=None, status=None, role=None, page=1, per_page=15):
        """Get all users with optional filtering and pagination"""
        query = """
            SELECT id, username, email, full_name, is_admin, is_active, created_at
            FROM users 
            WHERE 1=1
        """
        count_query = "SELECT COUNT(*) FROM users WHERE 1=1"
        params = []
        
        if search:
            query += " AND (username ILIKE %s OR email ILIKE %s OR full_name ILIKE %s)"
            count_query += " AND (username ILIKE %s OR email ILIKE %s OR full_name ILIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if status == 'active':
            query += " AND is_active = TRUE"
            count_query += " AND is_active = TRUE"
        elif status == 'inactive':
            query += " AND is_active = FALSE"
            count_query += " AND is_active = FALSE"
        
        if role == 'admin':
            query += " AND is_admin = TRUE"
            count_query += " AND is_admin = TRUE"
        elif role == 'user':
            query += " AND is_admin = FALSE"
            count_query += " AND is_admin = FALSE"
        
        query += " ORDER BY id ASC"
        
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        with db.get_cursor() as cursor:
            cursor.execute(count_query, params[:len(params)-2])  # Exclude LIMIT and OFFSET params
            total_count = cursor.fetchone()[0]

            cursor.execute(query, params)
            users = cursor.fetchall()
            
            return {
                'users': [dict(user) for user in users],
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, is_admin, is_active, created_at
                FROM users 
                WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    @staticmethod
    def create_user(username, email, password, full_name, is_admin=False):
        """Create new user"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT id FROM users WHERE username = %s OR email = %s
            """, (username, email))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return None, "El username o el correo electrónico ya existen"
        
        password_hash = generate_password_hash(password)
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, is_admin)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, username, email, full_name, is_admin, is_active, created_at
            """, (username, email, password_hash, full_name, is_admin))
            
            user = cursor.fetchone()
            return dict(user), "Usuario creado exitosamente"
    
    @staticmethod
    def update_user(user_id, username, email, full_name, is_admin, is_active):
        """Update user information"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT id FROM users 
                WHERE (username = %s OR email = %s) AND id != %s
            """, (username, email, user_id))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return None, "El username o el correo electrónico ya existen"

        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE users 
                SET username = %s, email = %s, full_name = %s, is_admin = %s, is_active = %s
                WHERE id = %s
                RETURNING id, username, email, full_name, is_admin, is_active, created_at
            """, (username, email, full_name, is_admin, is_active, user_id))
            
            user = cursor.fetchone()
            if user:
                return dict(user), "Usuario actualizado exitosamente"
            else:
                return None, "Usuario no encontrado"
    
    @staticmethod
    def change_password(user_id, new_password):
        """Change user password"""
        password_hash = generate_password_hash(new_password)
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s 
                WHERE id = %s
                RETURNING id
            """, (password_hash, user_id))
            
            updated = cursor.fetchone()
            if updated:
                return True, "Contraseña actualizada exitosamente"
            else:
                return False, "Usuario no encontrado"
    
    @staticmethod
    def toggle_user_status(user_id):
        """Toggle user active status"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE users 
                SET is_active = NOT is_active 
                WHERE id = %s
                RETURNING id, is_active
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                new_status = "activado" if result['is_active'] else "desactivado"
                return True, f"Usuario {new_status} exitosamente"
            else:
                return False, "Usuario no encontrado"
    
    @staticmethod
    def delete_user(user_id):
        """Delete user (soft delete)"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE users 
                SET is_active = FALSE 
                WHERE id = %s
                RETURNING id
            """, (user_id,))
            
            deleted = cursor.fetchone()
            if deleted:
                return True, "Usuario desactivado correctamente"
            else:
                return False, "Usuario no encontrado"
            
    @staticmethod
    def get_active_users():
        """Get all active users for dropdowns"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name
                FROM users 
                WHERE is_active = TRUE
                ORDER BY full_name
            """)
            users = cursor.fetchall()
            return [dict(user) for user in users]

    @staticmethod
    def get_total_users_count():
        """Get total number of users"""
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
