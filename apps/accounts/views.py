from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to SMS & Email Guard, {user.username}!")
            return redirect('dashboard:home')
        else:
            messages.error(request, "Please correct the registration errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Logged in successfully as {user.username}.")
            next_url = request.GET.get('next') or 'dashboard:home'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('accounts:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    submitted_count = request.user.submitted_messages.count()

    context = {
        'form': form,
        'submitted_count': submitted_count,
    }
    return render(request, 'accounts/profile.html', context)
