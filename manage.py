#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mowria_Inventory_Manage.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # Check if project virtual environment exists and auto-re-execute
        base_dir = os.path.dirname(os.path.abspath(__file__))
        venv_python = os.path.join(base_dir, 'venv', 'Scripts', 'python.exe')
        if os.path.exists(venv_python) and sys.executable.lower() != venv_python.lower():
            import subprocess
            sys.exit(subprocess.call([venv_python] + sys.argv))
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
