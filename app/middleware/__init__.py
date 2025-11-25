from flask import request, session, redirect, url_for
from app.services.user_service import UserService

def init_app(app):
    
    @app.before_request
    def load_authenticated_user():
        """Load user on each request and redirect to login if not authenticated"""
        if request.endpoint in ['main.login', 'static', 'main.manifest', 'main.service_worker']:
            request.user = None
            return
        
        user_id = session.get('user_id')
        
        if user_id:
            user = UserService.get_user_by_id(user_id)
            if user:
                request.user = user
                return
            else:
                session.clear()
        
        request.user = None
        return redirect(url_for('main.login'))
    
    @app.context_processor
    def inject_user():
        """Inject user into all templates"""
        return dict(current_user=getattr(request, 'user', None))