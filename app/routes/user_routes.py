from flask import request, jsonify, session, render_template, redirect, url_for
from app.services.reservation_service import ReservationService
from app.routes import main_bp
from datetime import date
from app.services.chat_service import ChatService

@main_bp.route('/user/dashboard')
def user_dashboard():
    """Render user dashboard with all data"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('main.login'))
        
        upcoming_reservations = ReservationService.get_user_upcoming_reservations(user_id, limit=5)
        all_reservations_data = ReservationService.get_user_reservations(
            user_id=user_id, 
            page=1, 
            per_page=1000
        )
        all_reservations = all_reservations_data['reservations']
        today = date.today().isoformat()
        
        upcoming_count = len([r for r in all_reservations 
                            if r['reservation_date'].isoformat() >= today 
                            and r['status'] in ['confirmed', 'pending']])
        
        total_count = len(all_reservations)
        cancelled_count = len([r for r in all_reservations if r['status'] == 'cancelled'])
        
        def format_reservation_display(reservation):
            reservation_date = reservation['reservation_date']
            is_today = reservation_date.isoformat() == today
            
            return {
                'id': reservation['id'],
                'date': reservation_date.strftime('%Y-%m-%d'),
                'date_display': reservation_date.strftime('%d/%m/%Y'),
                'start_time': reservation['start_time'].strftime('%H:%M'),
                'end_time': reservation['end_time'].strftime('%H:%M'),
                'status': reservation['status'],
                'status_display': 'Confirmada' if reservation['status'] == 'confirmed' else 'Pendiente'
            }
        
        upcoming_reservations_formatted = [format_reservation_display(r) for r in upcoming_reservations]
        
        return render_template('user/dashboard.html',
                           upcoming_count=upcoming_count,
                           total_count=total_count,
                           cancelled_count=cancelled_count,
                           upcoming_reservations=upcoming_reservations_formatted)
                           
    except Exception as e:
        return render_template('user/dashboard.html',
                           upcoming_count=0,
                           total_count=0,
                           cancelled_count=0,
                           upcoming_reservations=[])

@main_bp.route('/user/reservations')
def user_reservations():
    return render_template('user/reservations.html')

@main_bp.route('/user/reservations/new')
def user_new_reservation():
    return render_template('user/new_reservation.html')

@main_bp.route('/user/ai-chat')
def user_ai_chat():
    """Render AI chat page"""
    return render_template('user/ai_chat.html')

@main_bp.route('/user/about')
def about():
    return render_template('user/about.html')

@main_bp.route('/api/user/reservations', methods=['POST'])
def api_create_user_reservation():
    """API endpoint for user to create reservation"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Usuario no autenticado'
            }), 401
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos'
            }), 400
        
        required_fields = ['reservation_date', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido faltante: {field}'
                }), 400
        
        reservation, message = ReservationService.create_reservation(
            user_id=user_id,
            reservation_date=data['reservation_date'],
            start_time=data['start_time'],
            end_time=data['end_time']
        )
        
        if reservation:
            return jsonify({
                'success': True,
                'message': 'Reservación creada exitosamente',
                'reservation': {
                    'id': reservation['id'],
                    'reservation_date': reservation['reservation_date'].strftime('%Y-%m-%d'),
                    'start_time': reservation['start_time'].strftime('%H:%M'),
                    'end_time': reservation['end_time'].strftime('%H:%M'),
                    'status': reservation['status'],
                    'status_display': 'Pendiente'
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
            'message': f'Error al crear reservación: {str(e)}'
        }), 500

@main_bp.route('/api/user/reservations', methods=['GET'])
def api_get_user_reservations():
    """API endpoint to get user's reservations"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Usuario no autenticado'
            }), 401
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 15))
        status = request.args.get('status', '')
        date_filter = request.args.get('date', '')
        
        result = ReservationService.get_user_reservations(
            user_id=user_id,
            page=page,
            per_page=per_page,
            status=status,
            date_filter=date_filter
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
                'reservation_date': reservation['reservation_date'].strftime('%d-%m-%Y'),
                'start_time': reservation['start_time'].strftime('%H:%M'),
                'end_time': reservation['end_time'].strftime('%H:%M'),
                'status': reservation['status'],
                'status_display': status_match[reservation['status']],
                'created_at': reservation['created_at'].strftime('%d-%m-%Y')
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
            'message': f'Error al cargar reservaciones: {str(e)}'
        }), 500

@main_bp.route('/api/user/reservations/upcoming', methods=['GET'])
def api_get_user_upcoming_reservations():
    """API endpoint to get user's upcoming reservations"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Usuario no autenticado'
            }), 401
        
        limit = int(request.args.get('limit', 5))
        reservations = ReservationService.get_user_upcoming_reservations(user_id, limit)
        
        formatted_reservations = []
        for reservation in reservations:
            formatted_reservations.append({
                'id': reservation['id'],
                'reservation_date': reservation['reservation_date'].strftime('%Y-%m-%d'),
                'start_time': reservation['start_time'].strftime('%H:%M'),
                'end_time': reservation['end_time'].strftime('%H:%M'),
                'status': reservation['status']
            })
        
        return jsonify({
            'success': True,
            'reservations': formatted_reservations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar próximas reservaciones: {str(e)}'
        }), 500

@main_bp.route('/api/user/reservations/<int:reservation_id>/cancel', methods=['PUT'])
def api_cancel_user_reservation(reservation_id):
    """API endpoint for user to cancel their reservation"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Usuario no autenticado'
            }), 401
        
        success, message = ReservationService.cancel_user_reservation(reservation_id, user_id)
        
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
            'message': f'Error al cancelar reservación: {str(e)}'
        }), 500
    
@main_bp.route('/api/user/reservations/<int:reservation_id>/confirm', methods=['PUT'])
def api_confirm_user_reservation(reservation_id):
    """API endpoint for user to confirm they used the reservation"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Usuario no autenticado'
            }), 401
        
        success, message = ReservationService.confirm_reservation_usage(reservation_id, user_id)
        
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
            'message': f'Error al confirmar reservación: {str(e)}'
        }), 500

@main_bp.route('/api/chat/message', methods=['POST'])
def api_chat_message():
    """API endpoint to send message to AI chat"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Usuario no autenticado'
            }), 401
        
        data = request.get_json()
        if not data or not data.get('message'):
            return jsonify({
                'success': False,
                'message': 'El mensaje no puede estar vacío'
            }), 400
        
        user_message = data['message'].strip()
        result = ChatService.send_message(user_id, user_message)
        
        if result['success']:
            return jsonify({
                'success': True,
                'response': result['response'],
                'context_length': result.get('context_length', 0)
            })
        else:
            return jsonify({
                'success': False,
                'message': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en el chat: {str(e)}'
        }), 500

@main_bp.route('/api/chat/clear', methods=['POST'])
def api_clear_chat():
    """API endpoint to clear conversation context"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Usuario no autenticado'
            }), 401
        
        ChatService.clear_user_context(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Conversación reiniciada'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al reiniciar conversación: {str(e)}'
        }), 500

@main_bp.route('/api/chat/context', methods=['GET'])
def api_get_chat_context():
    """API endpoint to get current conversation context (for debugging)"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Usuario no autenticado'
            }), 401
        
        context = ChatService.get_user_context(user_id)
        
        return jsonify({
            'success': True,
            'context': context,
            'context_length': len(context) if context else 0
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener contexto: {str(e)}'
        }), 500
