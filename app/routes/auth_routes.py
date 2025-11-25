from flask import render_template, request, redirect, url_for, session, flash
from app.routes import main_bp
from app.services.user_service import UserService

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = UserService.authenticate(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            flash(f'Iniciaste sesión como {user["full_name"]}', 'success')
            redirect_url = 'main.admin_dashboard' if user['is_admin'] else 'main.user_dashboard'
            return redirect(url_for(redirect_url))
        else:
            flash('Usuario o contraseña inválidos', 'error')

    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('main.login'))
