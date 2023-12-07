from .models import ManagerProfile

def access_middleware(get_response):
    def middleware(request):
        try:
            if request.user.is_authenticated:
                try:
                    if ManagerProfile.objects.filter(user_id=request.user).exists():
                        role = 'manager'
                    else:
                        role = 'employee'
                    request.user_role = role
                except ManagerProfile.DoesNotExist:
                    request.user_role = 'employee'
        except Exception as e:
            print(e)
        return get_response(request)
    return middleware