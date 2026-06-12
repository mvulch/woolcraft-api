from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        UserModel = get_user_model()
        if username is None or password is None:
            return None
        try:
            # iexact - search both normal and capital letters
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            return None
        #if not user.email_verified:
            #return None
        if self.user_can_authenticate(user) and user.check_password(password) :
            return user
        return None
