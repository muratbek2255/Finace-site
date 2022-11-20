from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, phone_number: str, password, **extra_fields):
        if phone_number is None:
            raise TypeError('Users should have a username')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(phone_number, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
