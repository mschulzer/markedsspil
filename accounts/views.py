from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm, UserUpdateForm
from django.shortcuts import render, redirect
from django.contrib import messages


class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        """ Override. If the form is valid do these extra things before default behavior """
        messages.success(
            self.request, f'Your account was created!')
        
        return super().form_valid(form)
    
