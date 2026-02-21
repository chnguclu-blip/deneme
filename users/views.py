from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserChangeForm, GroupForm

# Check if user is admin
def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Handle groups
            if form.cleaned_data.get('groups'):
                user.groups.set(form.cleaned_data['groups'])
            messages.success(request, f'Kullanıcı {user.username} başarıyla oluşturuldu.')
            return redirect('users:user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Yeni Kullanıcı Ekle'})

@login_required
@user_passes_test(is_admin)
def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
             # Handle groups manually if needed, but ModelMultipleChoiceField handles it often
            if 'groups' in form.cleaned_data:
                 user.groups.set(form.cleaned_data['groups'])
            
            messages.success(request, f'Kullanıcı {user.username} güncellendi.')
            return redirect('users:user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Kullanıcı Düzenle'})

@login_required
@user_passes_test(is_admin)
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Kullanıcı {username} silindi.')
        return redirect('user_list')
    return render(request, 'users/confirm_delete.html', {'object': user, 'type': 'Kullanıcı'})

# --- Group Views ---

@login_required
@user_passes_test(is_admin)
def group_list(request):
    groups = Group.objects.all().order_by('name')
    return render(request, 'users/group_list.html', {'groups': groups})

@login_required
@user_passes_test(is_admin)
def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Grup {group.name} oluşturuldu.')
            return redirect('users:group_list')
    else:
        form = GroupForm()
    return render(request, 'users/group_form.html', {'form': form, 'title': 'Yeni Grup Ekle'})

@login_required
@user_passes_test(is_admin)
def edit_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f'Grup {group.name} güncellendi.')
            return redirect('users:group_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'users/group_form.html', {'form': form, 'title': 'Grup Düzenle'})

@login_required
@user_passes_test(is_admin)
def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        name = group.name
        group.delete()
        messages.success(request, f'Grup {name} silindi.')
        return redirect('group_list')
    return render(request, 'users/confirm_delete.html', {'object': group, 'type': 'Grup'})
