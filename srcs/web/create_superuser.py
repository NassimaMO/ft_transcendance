import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transcendance.settings')
django.setup()

from account.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

def create_superuser():
    if username and email and password:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f'Superuser "{username}" created successfully.')
        else:
            print(f'Superuser "{username}" already exists.')
    else:
        print('Superuser creation failed. Missing environment variables.')

if __name__ == '__main__':
    create_superuser()
