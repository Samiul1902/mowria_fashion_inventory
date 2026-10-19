"""
Cross-Platform WSGI Server for Mowria Inventory Manage.
Works on BOTH Windows (via waitress) and Linux/Cloud (via gunicorn).
"""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mowria_Inventory_Manage.settings')
    port = int(os.environ.get('PORT', 8000))
    host = '0.0.0.0'

    if sys.platform == 'win32':
        # Windows: Use Waitress production WSGI server (fcntl does not exist on Windows)
        try:
            from waitress import serve
            from Mowria_Inventory_Manage.wsgi import application
            print(f"Starting Waitress production WSGI server on http://127.0.0.1:{port} ...")
            serve(application, host=host, port=port)
        except ImportError:
            # Fallback to Django manage.py runserver if waitress not installed
            from django.core.management import execute_from_command_line
            execute_from_command_line([sys.argv[0], 'runserver', f'{host}:{port}'])
    else:
        # Linux / Cloud (Render, Heroku, Docker): Use Gunicorn
        import subprocess
        cmd = [
            'gunicorn',
            '--bind', f'{host}:{port}',
            '--workers', '2',
            'Mowria_Inventory_Manage.wsgi:application'
        ]
        sys.exit(subprocess.call(cmd))

if __name__ == '__main__':
    main()
