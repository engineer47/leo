import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.http import Http404
from leo_app.forms import (AuthenticateForm, UserCreateForm, LeoForm, UserProfileForm, VehicleSightingForm,
                           HumanSightingForm, InfrastructureSightingForm)
from leo_app.models import Ribbit, UserProfile, Vehicle, Infridgement, Sighting, Notification

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
            user_profile = UserProfile.objects.get(user=request.user)
            updated_user_values = {}
            updated_profile_values = {}
            for fld in UserProfileForm.Meta.fields:
                updated_user_values[fld] = form.cleaned_data.get(fld)
            for fld in UserProfileForm.Meta.profile_fields:
                updated_profile_values[fld] = form.cleaned_data.get(fld)
            User.objects.filter(id=request.user.id).update(**updated_user_values)
            UserProfile.objects.filter(user=request.user).update(**updated_profile_values)
            # TODO: search cars by registration not model name.
            updated_vehicles = []
            for key, value in request.POST.iteritems():
                if key.find('car') != -1:
                    updated_vehicles.append(value)
            # release all vehicles previously attached to this profile
            Vehicle.objects.filter(owner=user_profile).update(owner=None)
            # attach the updated list of vehicles to this profile
            Vehicle.objects.filter(model__in=updated_vehicles).update(owner=user_profile)

            # TODO: search People by omang-ID not firstname and lastname.
            updated_people = []
            for key, value in request.POST.iteritems():
                if key.find('per') != -1:
                    updated_people.append(value)
            # release all other users previously linked to this profile
            UserProfile.linked_to.through.objects.filter(user__username=request.user.username).delete()
            # link the updated list of users to this profile
            for name in updated_people:
                first_name, surname = name.split('.')
                named_user = UserProfile.objects.get(user__firstname=first_name, user__surname=surname)
                user_profile.linked_to.add(named_user)
            return HttpResponseRedirect('/user_profile/{}/'.format(form.cleaned_data.get('username')))
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
                   'vehicles': Vehicle.objects.all(),
                   'my_vehicles': Vehicle.objects.filter(owner=user_profile),
                   'people': UserProfile.objects.all().exclude(user__username=request.user.username),
                   'my_people': UserProfile.linked_to.through.objects.all(),
                   'username': request.user.username, })


def vehicle_lov(request):
    return render(request, 
                  'vehicle_lov.html',
                  {'vehicles': Vehicle.objects.all()})


def infridgement_lov(request):
    return render(request, 
                  'infridgement_lov.html',
                  {'infridgements': Infridgement.objects.all()})


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
        model = ''
        registration = ''
        ribbits_self = Ribbit.objects.filter(user=user.id)
        my_notifications = None
        my_vehicles = []
        #ribbits_buddies = Ribbit.objects.filter(user__userprofile__in=user.profile.follows.all)
        #ribbits = ribbits_self | ribbits_buddies
        my_vehicles = Vehicle.objects.filter(owner__user__username=request.user.username)
        my_notifications = Notification.objects.filter(Q(sighting__human__user__username=request.user.username) |
                                                           Q(sighting__vehicle__in=my_vehicles))
        if request.method == 'POST':
            # All POST data will contain a value for sighting
            sighting_type = request.POST.get('sighting')
            if sighting_type == 'vehicle':
                form = VehicleSightingForm(request.POST)
            elif sighting_type == 'human':
                form = HumanSightingForm(request.POST)
            elif sighting_type == 'infrastructure':
                form = InfrastructureSightingForm(request.POST)
            else:
                sighting_type = '------'
            # check whether it's valid:
            if form.is_valid():
                car = Vehicle.objects.get(registration=form.cleaned_data.get('registration'))
                infridgement = Infridgement.objects.get(code=form.cleaned_data.get('infridgement_code'))
                longitude = form.cleaned_data.get('longitude')
                latitude = form.cleaned_data.get('latitude')
                Sighting.objects.create(vehicle=car, infridgement=infridgement, longitude=longitude,
                                        latitude=latitude, sighting_datetime=datetime.now())
                msg = "Sucessfully registered a sighting agains vehicle registered {}".format(car.registration)
                messages.add_message(request, messages.INFO, msg)
        # What if the method is a get?
        else:
            sighting_type = '------'
        return render(request,
                      'buddies.html',
                      {'ribbit_form': ribbit_form, 'user': user,
                       #'ribbits': ribbits,
                       'model': model,
                       'registration': registration,
                       'sighting_type': sighting_type,
                       'notifications': my_notifications,
                       'public_notifications': [],
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
def footprint(request):
    username = request.GET.get('username')
    sightings = None
    sightings_tuple = []
    data = {'values':[]}
    if request.method == 'GET':
        my_sightings = Sighting.objects.filter(human__user__username=username)
        sightings = my_sightings
    else:
        sighting_type = request.POST.get('type')
        if sighting_type == 'vehicle':
            sightings = Sighting.objects.filter(vehicle__registration=request.POST.get('registration'))
            for st in sightings:
                sightings_tuple.append((st.sighting_datetime.strftime('%d/%b/%Y'),
                                        st.infridgement.short_description))
            sightings = sightings.values('year_month_slug').annotate(dcount=Count('year_month_slug'))
            for index in sightings:
                index['X'] = index.pop('year_month_slug')
                index['Y'] = index.pop('dcount')
            data['values'] = sightings
        elif sighting_type == 'human':
            pass
        elif sighting_type == 'infrastructure':
            pass
        else:
            sighting_type = '------'
        print str(data)
    return render(request,
                   'footprint.html',
                   {'username': request.user.username,
                    'sightings_tuple': sightings_tuple,
                    'graph_data': str(data).replace('u\'', '\'').replace('\'', '"')
                    })

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