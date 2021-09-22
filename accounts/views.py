from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm


class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

# def signup(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             new_user = form.save()
#             messages.info(
#                 request, "Thanks for registering. You are now logged in.")
#             new_user = authenticate(username=form.cleaned_data['username'],
#                                     password=form.cleaned_data['password1'],
#                                     )
#             login(request, new_user)
#             return HttpResponseRedirect("/")
#     else:
#         form = CustomUserCreationForm()

#     return render(request, "registration/signup.html", {'form': form})
