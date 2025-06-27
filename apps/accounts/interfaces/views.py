from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return redirect("dashboard")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
            form.add_error(None, "Invalid credentials.")
        return render(request, self.template_name, {"form": form})


class LogoutUserView(LogoutView):
    next_page = reverse_lazy("home")
