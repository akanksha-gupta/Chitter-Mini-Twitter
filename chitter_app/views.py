from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth.models import User
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from chitter_app.forms import AuthenticateForm, UserCreateForm, chitterForm
from chitter_app.models import chitter


def index(request, auth_form=None, user_form=None):
    # User is logged in
    if request.user.is_authenticated():
        chitter_form = chitterForm()
        user = request.user
        chitters_self = chitter.objects.filter(user=user.id)
        chitters_buddies = chitter.objects.filter(user__userprofile__in=user.profile.follows.all)
        chitters = chitters_self | chitters_buddies

        return render(request,
                      'buddies.html',
                      {'chitter_form': chitter_form, 'user': user,
                       'chitters': chitters,
                       'next_url': '/', })
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
            return redirect('/')
        else:
            return index(request, user_form=user_form)
    return redirect('/')


@login_required
def public(request, chitter_form=None):
    chitter_form = chitter_form or chitterForm()
    chitters = chitter.objects.reverse()[:10]
    return render(request,
                  'public.html',
                  {'chitter_form': chitter_form, 'next_url': '/chitters',
                   'chitters': chitters, 'username': request.user.username})


@login_required
def submit(request):
    if request.method == "POST":
        chitter_form = chitterForm(data=request.POST)
        next_url = request.POST.get("next_url", "/")
        if chitter_form.is_valid():
            chitter = chitter_form.save(commit=False)
            chitter.user = request.user
            chitter.save()
            return redirect(next_url)
        else:
            return public(request, chitter_form)
    return redirect('/')


def get_latest(user):
    try:
        return user.chitter_set.order_by('id').reverse()[0]
    except IndexError:
        return ""


@login_required
def users(request, username="", chitter_form=None):
    if username:
        # Show a profile
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        chitters = chitter.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username):
            # Self Profile
            return render(request, 'user.html', {'user': user, 'chitters': chitters, })
        return render(request, 'user.html', {'user': user, 'chitters': chitters, 'follow': True, })
    users = User.objects.all().annotate(chitter_count=Count('chitter'))
    chitters = map(get_latest, users)
    obj = zip(users, chitters)
    chitter_form = chitter_form or chitterForm()
    return render(request,
                  'profiles.html',
                  {'obj': obj, 'next_url': '/users/',
                   'chitter_form': chitter_form,
                   'username': request.user.username, })


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
