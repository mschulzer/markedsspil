from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    The user model we use for host accounts. 
    It is considered best practice to make it an extension of the default user model, as
    we might want to customize it later on (by adding fields and so on). 
    """
    pass