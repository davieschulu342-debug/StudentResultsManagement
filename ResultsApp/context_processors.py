from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

def staff_users(request):
    if request.user.is_authenticated:
        users = User.objects.filter(
            is_active=True
        ).filter(
            Q(is_staff=True) | Q(teacherprofile__isnull=False)  # <-- change here
        ).exclude(id=request.user.id)
        return {'staff_users': users}
    return {}
