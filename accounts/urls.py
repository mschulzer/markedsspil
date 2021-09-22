from .views import SignupPageView
from django.urls import path
#from .views import signup

# urlpatterns = [
#     path('signup/', signup, name='signup'),
# ]

urlpatterns = [
    path('signup/', SignupPageView.as_view(), name='signup'),
]
