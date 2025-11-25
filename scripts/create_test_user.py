import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.user_service import UserService

def main():
    """Create test user and tables if they don't exist"""
    try:
        print("Creating test user...")
        user, message = UserService.create_user(
            username='admin',
            email='moa02724@docente.ujat.mx',
            password='sala-rv-ra',
            full_name='Dra. María de los Ángeles Olán Acosta',
            is_admin=True
        )

        if user:
            print(f"User created successfully: {user}")
            
            test_user = UserService.authenticate('admin', 'sala-rv-ra')
            if test_user:
                print("Authentication works correctly")
                print(f"Authenticated user: {test_user['full_name']}")
            else:
                print("Authentication error")
        else:
            print(f"Error creating user: {message}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
