from flask import request, jsonify
from app.routes import main_bp
from app.services.reservation_service import ReservationService
from app.services.user_service import UserService

@main_bp.route('/api/admin/reservations', methods=['GET'])
def api_get_reservations():
    """API endpoint to get reservations with filtering and pagination"""
    try:
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        date_filter = request.args.get('date', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 15))
        
        result = ReservationService.get_all_reservations(
            search=search, 
            status=status, 
            date_filter=date_filter,
            page=page, 
            per_page=per_page
        )

        status_match = {
            "pending": "Pendiente",
            "cancelled": "Cancelada",
            "confirmed": "Confirmada"
        }
        
        formatted_reservations = []
        for reservation in result['reservations']:
            formatted_reservations.append({
                'id': reservation['id'],
                'user_id': reservation['user_id'],
                'user_name': reservation['full_name'],
                'user_email': reservation['email'],
                'user_username': reservation['username'],
                'reservation_date': reservation['reservation_date'].strftime('%d-%m-%Y'),
                'start_time': reservation['start_time'].strftime('%H:%M'),
                'end_time': reservation['end_time'].strftime('%H:%M'),
                'status': reservation['status'],
                'status_display': status_match[reservation['status']],
                'created_at': reservation['created_at'].strftime('%d-%m-%Y'),
                'avatar_initials': ''.join([name[0].upper() for name in reservation['full_name'].split()[:2]])
            })
        
        return jsonify({
            'success': True,
            'reservations': formatted_reservations,
            'pagination': {
                'page': result['page'],
                'per_page': result['per_page'],
                'total_count': result['total_count'],
                'total_pages': result['total_pages']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar las reservaciones: {str(e)}'
        }), 500

@main_bp.route('/api/admin/reservations', methods=['POST'])
def api_create_reservation():
    """API endpoint to create new reservation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se enviaron los datos necesarios'
            }), 400
        
        required_fields = ['user_id', 'reservation_date', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'No se envío el campo: {field}'
                }), 400
        
        reservation, message = ReservationService.create_reservation(
            user_id=data['user_id'],
            reservation_date=data['reservation_date'],
            start_time=data['start_time'],
            end_time=data['end_time']
        )
        
        if reservation:
            user = UserService.get_user_by_id(data['user_id'])
            return jsonify({
                'success': True,
                'message': message,
                'reservation': {
                    'id': reservation['id'],
                    'user_id': reservation['user_id'],
                    'user_name': user['full_name'] if user else 'Unknown',
                    'user_email': user['email'] if user else '',
                    'reservation_date': reservation['reservation_date'].strftime('%Y-%m-%d'),
                    'start_time': reservation['start_time'].strftime('%H:%M'),
                    'end_time': reservation['end_time'].strftime('%H:%M'),
                    'status': reservation['status'],
                    'status_display': reservation['status'].capitalize(),
                    'created_at': reservation['created_at'].strftime('%Y-%m-%d %H:%M'),
                    'avatar_initials': ''.join([name[0].upper() for name in user['full_name'].split()[:2]]) if user else 'U'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear la reservación: {str(e)}'
        }), 500

@main_bp.route('/api/admin/reservations/<int:reservation_id>', methods=['PUT'])
def api_update_reservation(reservation_id):
    """API endpoint to update reservation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se enviaron los datos necesarios'
            }), 400
        
        required_fields = ['reservation_date', 'start_time', 'end_time', 'status']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'No se envío el campo: {field}'
                }), 400
        
        reservation, message = ReservationService.update_reservation(
            reservation_id=reservation_id,
            reservation_date=data['reservation_date'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            status=data['status']
        )
        
        if reservation:
            user = UserService.get_user_by_id(reservation['user_id'])
            return jsonify({
                'success': True,
                'message': message,
                'reservation': {
                    'id': reservation['id'],
                    'user_id': reservation['user_id'],
                    'user_name': user['full_name'] if user else 'Unknown',
                    'user_email': user['email'] if user else '',
                    'reservation_date': reservation['reservation_date'].strftime('%Y-%m-%d'),
                    'start_time': reservation['start_time'].strftime('%H:%M'),
                    'end_time': reservation['end_time'].strftime('%H:%M'),
                    'status': reservation['status'],
                    'status_display': reservation['status'].capitalize(),
                    'avatar_initials': ''.join([name[0].upper() for name in user['full_name'].split()[:2]]) if user else 'U'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar la reservación: {str(e)}'
        }), 500

@main_bp.route('/api/admin/reservations/<int:reservation_id>/cancel', methods=['PUT'])
def api_cancel_reservation(reservation_id):
    """API endpoint to cancel reservation"""
    try:
        success, message = ReservationService.cancel_reservation(reservation_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cancelar la reservación: {str(e)}'
        }), 500

@main_bp.route('/api/admin/reservations/<int:reservation_id>', methods=['DELETE'])
def api_delete_reservation(reservation_id):
    """API endpoint to delete reservation"""
    try:
        success, message = ReservationService.cancel_reservation(reservation_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar la reservación: {str(e)}'
        }), 500

@main_bp.route('/api/admin/reservations/users/active', methods=['GET'])
def api_get_active_users():
    """API endpoint to get active users for dropdown"""
    try:
        users = UserService.get_active_users()
        formatted_users = [{
            'id': user['id'],
            'name': user['full_name'],
            'email': user['email'],
            'username': user['username']
        } for user in users]
        
        return jsonify({
            'success': True,
            'users': formatted_users
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar los usuarios: {str(e)}'
        }), 500
