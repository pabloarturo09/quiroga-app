from flask import request, jsonify
from app.routes import main_bp
from app.services.user_service import UserService

@main_bp.route('/api/admin/users', methods=['GET'])
def api_get_users():
    """API endpoint to get users with filtering and pagination"""
    try:
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        role = request.args.get('role', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 15))
        
        result = UserService.get_all_users(
            search=search, 
            status=status, 
            role=role, 
            page=page, 
            per_page=per_page
        )

        formatted_users = []
        for user in result['users']:
            formatted_users.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': 'admin' if user['is_admin'] else 'user',
                'role_display': 'Administrador' if user['is_admin'] else 'Usuario',
                'status': 'active' if user['is_active'] else 'inactive',
                'status_display': 'Activo' if user['is_active'] else 'Inactivo',
                'created_at': user['created_at'].strftime('%d-%m-%Y'),
                'avatar_initials': ''.join([name[0].upper() for name in user['full_name'].split()[:2]])
            })
        
        return jsonify({
            'success': True,
            'users': formatted_users,
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
            'message': f'Error al cargar los usuarios: {str(e)}'
        }), 500

@main_bp.route('/api/admin/users', methods=['POST'])
def api_create_user():
    """API endpoint to create new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos.'
            }), 400
        
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Se esperaba el campo: {field}'
                }), 400
    
        if len(data['password']) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }), 400
        
        user, message = UserService.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            is_admin=data.get('role') == 'admin'
        )
        
        if user:
            return jsonify({
                'success': True,
                'message': message,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'role': 'admin' if user['is_admin'] else 'user',
                    'role_display': 'Administrador' if user['is_admin'] else 'Usuario',
                    'status': 'active',
                    'status_display': 'Activo',
                    'created_at': user['created_at'].strftime('%Y-%m-%d'),
                    'avatar_initials': ''.join([name[0].upper() for name in user['full_name'].split()[:2]])
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
            'message': f'Error al crear el usuario: {str(e)}'
        }), 500

@main_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    """API endpoint to update user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos.'
            }), 400
        
        required_fields = ['username', 'email', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Se esperaba el campo: {field}'
                }), 400
        
        user, message = UserService.update_user(
            user_id=user_id,
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            is_admin=data.get('role') == 'admin',
            is_active=data.get('is_active', True)
        )
        
        if user:
            return jsonify({
                'success': True,
                'message': message,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'role': 'admin' if user['is_admin'] else 'user',
                    'role_display': 'Administrador' if user['is_admin'] else 'Usuario',
                    'status': 'active' if user['is_active'] else 'inactive',
                    'status_display': 'Activo' if user['is_active'] else 'Inactivo',
                    'avatar_initials': ''.join([name[0].upper() for name in user['full_name'].split()[:2]])
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
            'message': f'Error al actualizar usuario: {str(e)}'
        }), 500

@main_bp.route('/api/admin/users/<int:user_id>/password', methods=['PUT'])
def api_change_password(user_id):
    """API endpoint to change user password"""
    try:
        data = request.get_json()
        
        if not data or not data.get('new_password'):
            return jsonify({
                'success': False,
                'message': 'Debes enviar una nueva contraseña'
            }), 400
        
        if len(data['new_password']) < 8:
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres'
            }), 400
        
        success, message = UserService.change_password(user_id, data['new_password'])
        
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
            'message': f'Error al cambiar la contraseña: {str(e)}'
        }), 500

@main_bp.route('/api/admin/users/<int:user_id>/status', methods=['PUT'])
def api_toggle_user_status(user_id):
    """API endpoint to toggle user status"""
    try:
        success, message = UserService.toggle_user_status(user_id)
        
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
            'message': f'Error cambiando el estado del usuario: {str(e)}'
        }), 500

@main_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    """API endpoint to delete user"""
    try:
        success, message = UserService.delete_user(user_id)
        
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
            'message': f'Error al eliminar usuario: {str(e)}'
        }), 500