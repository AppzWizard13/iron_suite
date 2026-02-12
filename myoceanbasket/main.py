import os
import sys

def main():
    """Run administrative tasks."""
    # Use DJANGO_SETTINGS_MODULE environment variable
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
    if not settings_module:
        print(
            'Error: The DJANGO_SETTINGS_MODULE environment variable is not set.\n'
            'Set it to "settings.development" or "settings.production" as per your environment.'
        )
        sys.exit(1)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
