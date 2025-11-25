from app.database import db
from datetime import date

class ReservationService:
    
    @staticmethod
    def get_all_reservations(search=None, status=None, date_filter=None, page=1, per_page=15):
        """Get all reservations with optional filtering and pagination"""
        query = """
            SELECT r.id, r.user_id, r.reservation_date, r.start_time, r.end_time, r.status, r.created_at,
                   u.username, u.full_name, u.email
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            WHERE 1=1
        """
        count_query = """
            SELECT COUNT(*)
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (u.username ILIKE %s OR u.full_name ILIKE %s OR u.email ILIKE %s)"
            count_query += " AND (u.username ILIKE %s OR u.full_name ILIKE %s OR u.email ILIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if status and status != 'all':
            query += " AND r.status = %s"
            count_query += " AND r.status = %s"
            params.append(status)
        
        if date_filter:
            query += " AND r.reservation_date = %s"
            count_query += " AND r.reservation_date = %s"
            params.append(date_filter)
        
        query += " ORDER BY r.reservation_date, r.start_time"
        
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        with db.get_cursor() as cursor:
            cursor.execute(count_query, params[:len(params)-2])
            total_count = cursor.fetchone()[0]
            
            cursor.execute(query, params)
            reservations = cursor.fetchall()
            
            return {
                'reservations': [dict(reservation) for reservation in reservations],
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }
    
    @staticmethod
    def create_reservation(user_id, reservation_date, start_time, end_time):
        """Create new reservation"""
        conflict = ReservationService._check_time_conflict(reservation_date, start_time, end_time)
        if conflict:
            return None, "Conflicto de horario: Ya existe una reserva en este horario."
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO reservations (user_id, reservation_date, start_time, end_time, status)
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING id, user_id, reservation_date, start_time, end_time, status, created_at
            """, (user_id, reservation_date, start_time, end_time))
            
            reservation = cursor.fetchone()
            return dict(reservation), "Reservación creada exitosamente"
    
    @staticmethod
    def update_reservation(reservation_id, reservation_date, start_time, end_time, status):
        """Update reservation"""
        conflict = ReservationService._check_time_conflict(reservation_date, start_time, end_time, reservation_id)
        if conflict:
            return None, "Conflicto de horario: Ya existe una reserva en este horario."
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE reservations 
                SET reservation_date = %s, start_time = %s, end_time = %s, status = %s
                WHERE id = %s
                RETURNING id, user_id, reservation_date, start_time, end_time, status, created_at
            """, (reservation_date, start_time, end_time, status, reservation_id))
            
            reservation = cursor.fetchone()
            if reservation:
                return dict(reservation), "Reservación actualizada correctamente"
            else:
                return None, "Reservación no encontrada"
    
    @staticmethod
    def cancel_reservation(reservation_id):
        """Cancel reservation"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE reservations 
                SET status = 'cancelled'
                WHERE id = %s
                RETURNING id
            """, (reservation_id,))
            
            cancelled = cursor.fetchone()
            if cancelled:
                return True, "Reservación cancelada correctamente"
            else:
                return False, "Reservación no encontrada"
    
    @staticmethod
    def _check_time_conflict(reservation_date, start_time, end_time, exclude_reservation_id=None):
        """Check if there's a time conflict with existing reservations"""
        query = """
            SELECT COUNT(*) as conflicts
            FROM reservations
            WHERE reservation_date = %s 
            AND (status = 'confirmed' OR status = 'pending')
            AND (
                (start_time <= %s AND end_time > %s) OR
                (start_time < %s AND end_time >= %s) OR
                (start_time >= %s AND end_time <= %s)
            )
        """
        params = [reservation_date, start_time, start_time, end_time, end_time, start_time, end_time]
        
        if exclude_reservation_id:
            query += " AND id != %s"
            params.append(exclude_reservation_id)
        
        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['conflicts'] > 0
    
    @staticmethod
    def get_reservation_by_id(reservation_id):
        """Get reservation by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.id, r.user_id, r.reservation_date, r.start_time, r.end_time, r.status, r.created_at,
                       u.username, u.full_name, u.email
                FROM reservations r
                JOIN users u ON r.user_id = u.id
                WHERE r.id = %s
            """, (reservation_id,))
            reservation = cursor.fetchone()
            return dict(reservation) if reservation else None
    
    @staticmethod
    def get_todays_reservations():
        """Get today's reservations"""
        today = date.today()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.id, r.user_id, r.reservation_date, r.start_time, r.end_time, r.status,
                       u.full_name
                FROM reservations r
                JOIN users u ON r.user_id = u.id
                WHERE r.reservation_date = %s AND r.status = 'confirmed'
                ORDER BY r.start_time
            """, (today,))
            reservations = cursor.fetchall()
            return [dict(reservation) for reservation in reservations]
        
    @staticmethod
    def get_user_reservations(user_id, page=1, per_page=15, status=None, date_filter=None):
        """Get reservations for a specific user with pagination"""
        query = """
            SELECT r.id, r.user_id, r.reservation_date, r.start_time, r.end_time, r.status, r.created_at,
                u.username, u.full_name, u.email
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            WHERE r.user_id = %s
        """
        count_query = "SELECT COUNT(*) FROM reservations WHERE user_id = %s"
        params = [user_id]
        count_params = [user_id]
        
        if status and status != 'all':
            query += " AND r.status = %s"
            count_query += " AND status = %s"
            params.append(status)
            count_params.append(status)
        
        if date_filter:
            query += " AND r.reservation_date = %s"
            count_query += " AND reservation_date = %s"
            params.append(date_filter)
            count_params.append(date_filter)
        
        query += " ORDER BY r.reservation_date, r.start_time"
        
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        with db.get_cursor() as cursor:
            cursor.execute(count_query, count_params)
            total_count = cursor.fetchone()[0]
            
            cursor.execute(query, params)
            reservations = cursor.fetchall()
            
            return {
                'reservations': [dict(reservation) for reservation in reservations],
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }

    @staticmethod
    def get_user_upcoming_reservations(user_id, limit=5):
        """Get upcoming reservations for a user"""
        today = date.today()
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.id, r.reservation_date, r.start_time, r.end_time, r.status
                FROM reservations r
                WHERE r.user_id = %s 
                AND r.reservation_date >= %s 
                AND (r.status = 'confirmed' OR r.status = 'pending')
                ORDER BY r.reservation_date ASC, r.start_time ASC
                LIMIT %s
            """, (user_id, today, limit))
            
            reservations = cursor.fetchall()
            return [dict(reservation) for reservation in reservations]

    @staticmethod
    def cancel_user_reservation(reservation_id, user_id):
        """Cancel a reservation if it belongs to the user"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE reservations 
                SET status = 'cancelled'
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (reservation_id, user_id))
            
            cancelled = cursor.fetchone()
            if cancelled:
                return True, "Reservación cancelada exitosamente"
            else:
                return False, "Reservación no encontrada"

    @staticmethod
    def confirm_reservation_usage(reservation_id, user_id):
        """Confirm that a reservation was actually used"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE reservations 
                SET status = 'confirmed'
                WHERE id = %s AND user_id = %s AND status = 'pending'
                RETURNING id
            """, (reservation_id, user_id))
            
            confirmed = cursor.fetchone()
            if confirmed:
                return True, "Reservación confirmada exitosamente"
            else:
                return False, "Reservación no encontrada o ya no está pendiente"

    @staticmethod
    def get_total_reservations_count():
        """Get total number of reservations"""
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM reservations")
            return cursor.fetchone()[0]

    @staticmethod
    def get_pending_reservations_count():
        """Get count of pending reservations"""
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM reservations WHERE status = 'pending'")
            return cursor.fetchone()[0]

    @staticmethod
    def get_recent_reservations(limit=5):
        """Get recent reservations with user info"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT r.id, r.reservation_date, r.start_time, r.end_time, r.status, r.created_at,
                    u.username, u.full_name
                FROM reservations r
                JOIN users u ON r.user_id = u.id
                ORDER BY r.created_at DESC
                LIMIT %s
            """, (limit,))
            reservations = cursor.fetchall()
            return [dict(reservation) for reservation in reservations]
