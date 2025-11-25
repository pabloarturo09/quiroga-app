from flask import render_template
from app.routes import main_bp
from app.services.user_service import UserService
from app.services.reservation_service import ReservationService

@main_bp.route('/admin/dashboard')
def admin_dashboard():
    """Render admin dashboard with simplified data"""
    try:
        total_users = UserService.get_total_users_count()
        total_reservations = ReservationService.get_total_reservations_count()
        pending_reservations = ReservationService.get_pending_reservations_count()
        recent_reservations = ReservationService.get_recent_reservations(limit=5)
        recent_reservations_formatted = [format_reservation_display(r) for r in recent_reservations]
        
        return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_reservations=total_reservations,
                           pending_reservations=pending_reservations,
                           recent_reservations=recent_reservations_formatted)
                           
    except Exception as e:
        return render_template('admin/dashboard.html',
                           total_users=0,
                           total_reservations=0,
                           pending_reservations=0,
                           recent_reservations=[])

@main_bp.route('/admin/users')
def admin_users():
    return render_template('admin/users.html')

@main_bp.route('/admin/reservations')
def admin_reservations():
    return render_template('admin/reservations.html')

@main_bp.route('/admin/inventory')
def admin_inventory():
    return render_template('admin/inventory.html')

@main_bp.route('/admin/ai-assistant')
def admin_ai():
    return render_template('admin/ai_assistant.html')

@main_bp.route('/admin/about')
def about_admin():
    return render_template('admin/about.html')

def format_reservation_display(reservation):
    reservation_date = reservation['reservation_date']
    
    return {
        'id': reservation['id'],
        'date': reservation_date.strftime('%Y-%m-%d'),
        'date_display': reservation_date.strftime('%d/%m/%Y'),
        'start_time': reservation['start_time'].strftime('%H:%M'),
        'end_time': reservation['end_time'].strftime('%H:%M'),
        'status': reservation['status'],
        'status_display': 'Confirmada' if reservation['status'] == 'confirmed' else 
                        'Pendiente' if reservation['status'] == 'pending' else 'Cancelada',
        'user_name': reservation.get('full_name', reservation.get('username', 'Usuario')),
        'created_display': reservation['created_at'].strftime('%d/%m %H:%M')
    }