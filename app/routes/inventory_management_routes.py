from flask import request, jsonify
from app.services.inventory_service import InventoryService
from app.routes import main_bp

@main_bp.route('/api/inventory/items', methods=['GET'])
def api_get_inventory_items():
    """API endpoint to get all inventory items"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 15))
        search = request.args.get('search', '')
        item_type = request.args.get('type', '')
        status = request.args.get('status', '')
        
        result = InventoryService.get_all_items(
            page=page,
            per_page=per_page,
            search=search,
            item_type=item_type,
            status=status
        )
        
        return jsonify({
            'success': True,
            'items': result['items'],
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
            'message': f'Error al cargar inventario: {str(e)}'
        }), 500

@main_bp.route('/api/inventory/items', methods=['POST'])
def api_create_inventory_item():
    """API endpoint to create new inventory item"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos'
            }), 400
        
        required_fields = ['identificador', 'item_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido faltante: {field}'
                }), 400
        
        item = InventoryService.create_item(
            identificador=data['identificador'],
            item_type=data['item_type'],
            brand=data.get('brand'),
            model=data.get('model'),
            status=data.get('status', 'available')
        )
        
        if item:
            return jsonify({
                'success': True,
                'message': 'Item creado exitosamente',
                'item': item
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al crear item'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear item: {str(e)}'
        }), 500

@main_bp.route('/api/inventory/items/<int:item_id>', methods=['GET'])
def api_get_inventory_item(item_id):
    """API endpoint to get specific inventory item"""
    try:
        item = InventoryService.get_item_by_id(item_id)
        
        if item:
            return jsonify({
                'success': True,
                'item': item
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Item no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar item: {str(e)}'
        }), 500

@main_bp.route('/api/inventory/items/<int:item_id>', methods=['PUT'])
def api_update_inventory_item(item_id):
    """API endpoint to update inventory item"""
    try:
        data = request.get_json()
        del data["item_id"]
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron datos'
            }), 400
        
        item = InventoryService.update_item(item_id, **data)
        
        if item:
            return jsonify({
                'success': True,
                'message': 'Item actualizado exitosamente',
                'item': item
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Item no encontrado o error al actualizar'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar item: {str(e)}'
        }), 500

@main_bp.route('/api/inventory/items/<int:item_id>', methods=['DELETE'])
def api_delete_inventory_item(item_id):
    """API endpoint to delete inventory item"""
    try:
        success = InventoryService.delete_item(item_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Item eliminado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Item no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar item: {str(e)}'
        }), 500

@main_bp.route('/api/inventory/stats', methods=['GET'])
def api_get_inventory_stats():
    """API endpoint to get inventory statistics"""
    try:
        type_counts = InventoryService.get_item_types_count()
        status_counts = InventoryService.get_status_count()
        
        return jsonify({
            'success': True,
            'stats': {
                'by_type': type_counts,
                'by_status': status_counts
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar estadísticas: {str(e)}'
        }), 500

@main_bp.route('/api/inventory/types', methods=['GET'])
def api_get_item_types():
    """API endpoint to get available item types"""
    try:
        item_types = [
            {'value': 'computadora', 'label': 'Computadora'},
            {'value': 'pantalla', 'label': 'Pantalla'},
            {'value': 'lentes_vr', 'label': 'Lentes VR'}
        ]
        
        return jsonify({
            'success': True,
            'types': item_types
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar tipos: {str(e)}'
        }), 500

@main_bp.route('/api/inventory/statuses', methods=['GET'])
def api_get_statuses():
    """API endpoint to get available statuses"""
    try:
        statuses = [
            {'value': 'available', 'label': 'Disponible'},
            {'value': 'maintenance', 'label': 'En Mantenimiento'},
            {'value': 'broken', 'label': 'Dañado'}
        ]
        
        return jsonify({
            'success': True,
            'statuses': statuses
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar estados: {str(e)}'
        }), 500
