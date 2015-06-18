from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.http import Http404
from leo_app.forms import AuthenticateForm, UserCreateForm, LeoForm, UserProfileForm
from leo_app.models import Ribbit, UserProfile, Vehicle

def get_latest(user):
    try:
        return user.ribbit_set.order_by('-id')[0]
    except IndexError:
        return ""
 
@login_required
def follow(request):
    if request.method == "POST":
        follow_id = request.POST.get('follow', False)
        if follow_id:
            try:
                user = User.objects.get(id=follow_id)
                request.user.profile.follows.add(user.profile)
            except ObjectDoesNotExist:
                return redirect('/users/')
    return redirect('/users/')

@login_required
def users(request, username="", ribbit_form=None):
    if username:
        # Show a profile
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        ribbits = Ribbit.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username):
            # Self Profile or buddies' profile
            return render(request, 'user.html', {'user': user, 'ribbits': ribbits, })
        return render(request, 'user.html', {'user': user, 'ribbits': ribbits, 'follow': True, })
    users = User.objects.all().annotate(ribbit_count=Count('ribbit'))
    ribbits = map(get_latest, users)
    obj = zip(users, ribbits)
    ribbit_form = ribbit_form or LeoForm()
    return render(request,
                  'profiles.html',
                  {'obj': obj, 'next_url': '/users/',
                   'ribbit_form': ribbit_form,
                   'username': request.user.username, })

@login_required
def user_profile(request, username=None):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserProfileForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            updated_user_values = {}
            updated_profile_values = {}
            for fld in UserProfileForm.Meta.fields:
                updated_user_values[fld] = form.cleaned_data.get(fld)
            for fld in UserProfileForm.Meta.profile_fields:
                updated_profile_values[fld] = form.cleaned_data.get(fld)
            User.objects.filter(id=request.user.id).update(**updated_user_values)
            UserProfile.objects.filter(user=request.user).update(**updated_profile_values)
            return HttpResponseRedirect('/user_profile/{}/'.format(form.cleaned_data.get('username')))

    # if a GET (or any other method) we'll create a blank form
    else:
        #user = request.GET.get('username')
        print request.GET
        user_profile = UserProfile.objects.get(user__username=username)
        form_values = {}
        for fld in UserProfileForm.Meta.fields:
            form_values[fld] = user_profile.user.__dict__[fld]
        for fld in UserProfileForm.Meta.profile_fields:
            form_values[fld] = user_profile.__dict__[fld]
        form = UserProfileForm(form_values)

    return render(request, 
                  'profiles.html', 
                  {'form': form,
                   'vehicles': Vehicle.objects.all().exclude(owner=request.user),
                   'my_vehicles': Vehicle.objects.filter(owner=request.user),
                   'username': request.user.username, })

@login_required
def vehicle_owner(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_vehicles')
        reg = request.POST.get('add_car')
    return render(request, 
                  'profiles.html', 
                  {'form': form,
                   'vehicles': Vehicle.objects.all().exclude(owner=request.user),
                   'my_vehicles': Vehicle.objects.filter(owner=request.user),
                   'username': request.user.username, })
    
def index(request, auth_form=None, user_form=None):
    # User is logged in
    if request.user.is_authenticated():
        ribbit_form = LeoForm()
        user = request.user
        ribbits_self = Ribbit.objects.filter(user=user.id)
        #ribbits_buddies = Ribbit.objects.filter(user__userprofile__in=user.profile.follows.all)
        #ribbits = ribbits_self | ribbits_buddies

        if request.POST.get('sighting'):
            sighting_type = request.POST.get('sighting')
        else:
            sighting_type = '------'
        return render(request,
                      'buddies.html',
                      {'ribbit_form': ribbit_form, 'user': user,
                       #'ribbits': ribbits,
                       'sighting_type': sighting_type,
                       'notifications': [1, 2, 3],
                       'public_notifications': [1, 2, 3],
                       'next_url': '/',
                       'username': request.user.username,  })
    else:
        # User is not logged in
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()
 
        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Success
            return redirect('/')
        else:
            # Failure
            return index(request, auth_form=form)
    return redirect('/')
 
 
def logout_view(request):
    logout(request)
    return redirect('/')

def signup(request):
    user_form = UserCreateForm(data=request.POST)
    if request.method == 'POST':
        if user_form.is_valid():
            username = user_form.clean_username()
            password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            form_values = {}
            for fld in UserCreateForm.Meta.profile_fields:
                form_values[fld] = user_form.cleaned_data[fld]
            form_values['user'] = user
            UserProfile.objects.create(**form_values)
            return redirect('/')
        else:
            return index(request, user_form=user_form)
    return redirect('/')

@login_required
def public(request, ribbit_form=None):
    ribbit_form = ribbit_form or LeoForm()
    ribbits = Ribbit.objects.reverse()[:10]
    return render(request,
                   'public.html',
                   {'ribbit_form': ribbit_form, 'next_url': '/ribbits',
                    'ribbits': ribbits, 'username': request.user.username})
 
@login_required
def submit(request):
    if request.method == "POST":
        ribbit_form = LeoForm(data=request.POST)
        next_url = request.POST.get("next_url", "/")
        if ribbit_form.is_valid():
            ribbit = ribbit_form.save(commit=False)
            ribbit.user = request.user
            ribbit.save()
            return redirect(next_url)
        else:
            return public(request, ribbit_form)
    return redirect('/')