from .models import Beaver

def getBeaverInstance(request):
    user = request.user
    return Beaver.objects.get(user = user)