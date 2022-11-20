from core.settings import ADMINS
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            for user in ADMINS:
                phone_number = user[0]
                username = user[1]
                email = user[2]
                first_name = user[3]
                last_name = user[4]
                password = user[-1]
                print('Creating account for %s (%s)' % (phone_number, password))
                admin = User.objects.create_superuser(
                    phone_number=phone_number, username=username, email=email,
                    first_name=first_name, last_name=last_name, password=password)
                admin.is_active = True
                admin.is_admin = True
                admin.save()
        except:
            pass
