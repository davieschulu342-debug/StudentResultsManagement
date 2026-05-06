# myapp/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class AdminAccessOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated or not request.user.is_staff:
                return redirect(reverse('admin:login'))  # Django admin login
        return self.get_response(request)
