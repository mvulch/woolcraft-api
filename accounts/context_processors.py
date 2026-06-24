from .forms import LoginForm

def login_credentials(request):
    if request.user.is_authenticated:
        return {}
    return {'form': LoginForm()}
