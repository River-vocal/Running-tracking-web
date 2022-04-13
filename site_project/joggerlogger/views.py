from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, resolve
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings
from django.utils import timezone

from django.http import HttpResponse, Http404, HttpResponseRedirect

from joggerlogger.forms import RegisterForm, LoginForm, RunForm, PictureForm, GoalForm
from joggerlogger.models import Account, Run, Team, Goal
from joggerlogger.utils import *

import json


# Create your views here.

# Api views

@login_required
def api_runs(request):
    #
    # GET requests
    #
    if request.method == "GET":
        username = request.GET.get('user', '')
        user = User.objects.filter(username__exact=username).first()
        if user == None:
            return HttpResponse(404)

        runs = user.account.first().runs.all()
        response_data = []
        for run in runs:
            extendedProps = {
                "title": run.title,
                "description": run.description,
                "distance": run.distance,
                "duration": run.duration
            }
            run_item = {
                'id': run.id,
                'title': "{} mi, {} min".format(run.distance, run.duration),
                'start': str(run.date),
                'end': str(run.date),
                'editable': False,
                'extendedProps': extendedProps
            }
            response_data.append(run_item)
        response_json = json.dumps(response_data)
        return HttpResponse(response_json, content_type='application/json', status=200)
    #
    # Post Requests
    #
    if request.method == "POST" and not 'id' in request.POST:
        user = request.user
        account = user.account.first()
        form = RunForm(request.POST)
        if not form.is_valid():
            return render(request, "joggerlogger/error.html", {'error': 'Error creating run'})

        if form.cleaned_data['runid'] == -1:
            run = Run(
                runner=account,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                distance=form.cleaned_data['distance'],
                duration=form.cleaned_data['duration'],
                date=form.cleaned_data['date'],
                is_at_meet=False,
                created_by=user,
                created_at=timezone.now()
            )
            run.save()
        else:
            run = Run.objects.filter(id__exact=form.cleaned_data['runid']).first()
            run.title = form.cleaned_data['title']
            run.description = form.cleaned_data['description']
            run.distance = form.cleaned_data['distance']
            run.duration = form.cleaned_data['duration']
            run.date = form.cleaned_data['date']
            created_at = timezone.now()
            run.save()
        return redirect("/?user={}".format(request.user.username))
    #
    # DELETE requests
    #
    if request.method == "DELETE":
        id = request.GET.get('id')
        run = Run.objects.filter(id__exact=id).first()
        if run.runner != request.user.account.first():
            return HttpResponse('Unauthorized', status=401)
        else:
            run.delete()
            return HttpResponse(status=200)


# Page views

@login_required
def index(request):
    context = {}
    username = request.GET.get("user", "")
    if username == "":
        return redirect("/?user={}".format(request.user.username))
    profile_user = User.objects.filter(username__exact=username).first()
    if profile_user is None:
        return render(request, 'joggerlogger/error.html', {'error': 'User not found'})
    context = {'username': username, 'first': profile_user.first_name, 'last': profile_user.last_name}
    context['own_page'] = username == request.user.username
    return render(request, 'joggerlogger/index.html', context)


def login_page(request):
    context = {}
    if request.method == "GET":
        return render(request, 'joggerlogger/login.html', context)

    form = LoginForm(request.POST)

    if not form.is_valid():
        context['message'] = form.message
        return render(request, 'joggerlogger/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    login(request, new_user)
    return redirect(reverse("index_page"))


def register_page(request):
    context = {}
    if request.method == "GET":
        return render(request, 'joggerlogger/register.html', context)

    form = RegisterForm(request.POST)

    if not form.is_valid():
        context['message'] = form.message
        return render(request, 'joggerlogger/register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        email=form.cleaned_data['email'])

    new_user_profile = Account(bio="Talk about yourself here!", goal="Has yet to be decided",
                               user=new_user, picture="default.png", content_type="image/png")

    new_user_profile.save()

    new_user.account.set([new_user_profile])

    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])

    # send a confirmation email to the user upon registration
    subject = "Welcome to Jogger Logger"
    message = "Thank you for registering for Jogger Logger. Your account is now activated. Enjoy!"
    from_email = settings.EMAIL_HOST_USER
    to_list = [new_user.email]
    send_mail(subject, message, from_email, to_list)

    return redirect(reverse(login_page))


def logout_action(request):
    logout(request)
    return redirect(reverse('login_page'))


# https://docs.djangoproject.com/en/3.2/topics/db/queries/#querying-jsonfield
def del_run_logging(request):
    profile_user = User.objects.filter(username__exact=request.POST['user']).first()
    # user_cur = Account.objects.get(user=profile_user)
    run_id = int(request.POST['run_id'])
    existing_run = profile_user.account.first().runs.all()[run_id]
    existing_run.lat_longs.remove([request.POST['lat'], request.POST['lng']])
    existing_run.save()
    return HttpResponseRedirect(reverse("run_logging", args=(run_id,)));


def add_run_logging(request):
    profile_user = User.objects.filter(username__exact=request.POST['user']).first()
    # user_cur = Account.objects.get(user=profile_user)
    run_id = int(request.POST['run_id'])
    existing_run = profile_user.account.first().runs.all()[run_id]
    existing_run.lat_longs.append([request.POST['lat'], request.POST['lng']])
    existing_run.save()
    return HttpResponseRedirect(reverse("run_logging", args=(run_id,)));


@login_required
def run_logging(request, run_id):
    if request.method == "GET":
        user_cur = Account.objects.get(user=request.user)

        if run_id >= user_cur.runs.all().count() and user_cur.runs.all().count() != 0:
            run_id = user_cur.runs.all().count() - 1

        if run_id < 0 and user_cur.runs.all().count() != 0:
            run_id = 0

        context = {}
        context['left'] = True
        context['right'] = True
        context['user_cur'] = request.user.username
        context['no_runs'] = False

        # api_file = open('joggerlogger/static/joggerlogger/api_key.txt', 'r')
        api_file = open("/home/ubuntu/s21_team_41/site_project/joggerlogger/static/joggerlogger/api_key.txt", 'r')
        api_key = api_file.readline()

        context['api_key'] = api_key
        if user_cur.runs.all().count() == 0:
            context['no_runs'] = True
        elif user_cur.runs.all().count() == 1:

            runs_user = (user_cur.runs.all().order_by("-date"))[run_id]
            context['left'] = False
            context['right'] = False
            context['run_id'] = run_id
            context['run_u'] = runs_user
            context['lat_long_json'] = user_cur.runs.all()[run_id].lat_longs
        elif run_id == 0:
            runs_user = (user_cur.runs.all().order_by("-date"))[run_id]
            context['prev_run'] = 0
            context['run_id'] = run_id
            context['next_run'] = run_id + 1
            context['next_run_date'] = user_cur.runs.all().order_by("-date")[run_id + 1].date
            context['left'] = False
            context['run_u'] = runs_user
            context['lat_long_json'] = user_cur.runs.all()[run_id].lat_longs

        elif run_id + 1 >= user_cur.runs.all().count():
            runs_user = (user_cur.runs.all().order_by("-date"))[run_id]
            context['next_run'] = user_cur.runs.all().count()
            context['prev_run'] = run_id - 1
            context['run_id'] = run_id
            context['prev_run_date'] = user_cur.runs.all().order_by("-date")[run_id - 1].date
            context['right'] = False
            context['run_u'] = runs_user
            context['lat_long_json'] = user_cur.runs.all()[run_id].lat_longs
        else:
            runs_user = (user_cur.runs.all().order_by("-date"))[run_id]
            context['prev_run'] = run_id - 1
            context['run_id'] = run_id
            context['prev_run_date'] = user_cur.runs.all().order_by("-date")[run_id - 1].date
            context['next_run'] = run_id + 1
            context['next_run_date'] = user_cur.runs.all().order_by("-date")[run_id + 1].date
            context['run_u'] = runs_user
            context['lat_long_json'] = user_cur.runs.all()[run_id].lat_longs
        return render(request, 'joggerlogger/run_logging.html', context)


# Helper function
def find_in_query_set(run, runs):
    for i in range(0, runs.count()):
        if runs[i] == run:
            return i
    return -1


@login_required
def run_search_action(request):
    if request.method != "GET":
        raise Http404

    context = {}
    if 'search' in request.GET:
        search_text = request.GET['search']
        runs_user = Account.objects.get(user=request.user).runs.all()
        context['search'] = search_text
        selected_runs = set()
        for run in runs_user.filter(description__icontains=search_text):
            index = find_in_query_set(run, runs_user)
            selected_runs.add((run, index))
        for run in runs_user.filter(title__icontains=search_text):
            index = find_in_query_set(run, runs_user)
            selected_runs.add((run, index))
        context['selected_runs'] = selected_runs
    return render(request, "joggerlogger/run_search.html", context)


# Team hall view: a list of teams to join

@login_required
def team_hall(request):
    teams = Team.objects.all().order_by('-id')
    context = {'teams': teams}
    return render(request, 'joggerlogger/team_hall.html', context)


# Team details view

@login_required
def team_detail(request, team_id):
    team = Team.objects.get(id=team_id)
    if (team_id < 0 or team_id > Team.objects.all().count()):
        return HttpResponseRedirect(reverse("team_hall"))
    context = {'team': team}
    this_account = Account.objects.get(user=request.user)
    if this_account == team.coach:
        return render(request, 'joggerlogger/team_detail_coach.html', context)
    else:
        context['account'] = this_account
        return render(request, 'joggerlogger/team_detail_member.html', context)


# Create a new team

@login_required
def team_creation(request):
    if request.method == 'POST':
        if not "name" in request.POST:
            context = {'message': "Please fill the form completely!"}
            return render(request, 'joggerlogger/team_creation.html', context)
        else:
            this_user = request.user
            this_account = Account.objects.get(user=this_user)
            new_team = Team(name=request.POST['name'], slogan=request.POST['slogan'],
                            coach=this_account, created_by=request.user, goal=request.POST['goal'])
            new_team.save()
            teams = Team.objects.all().order_by('-id')
            context = {'teams': teams}
            return render(request, 'joggerlogger/team_hall.html', context)
    else:
        return render(request, 'joggerlogger/team_creation.html', {})


# Only allowed for coach, modify the profile of the team

@login_required
def set_team_profile(request, team_id):
    if request.method == 'GET':
        raise Http404
    this_team = Team.objects.get(id=team_id)
    this_team.slogan = request.POST['slogan']
    this_team.goal = request.POST['team_goal']
    this_team.name = request.POST['name']
    this_team.save()
    context = {"team": this_team}
    return render(request, 'joggerlogger/team_detail_coach.html', context)


# Only allowed for coach, modify the goal for each runner

@login_required
def set_member_goal(request, runner_id):
    if request.method == 'GET':
        raise Http404
    this_account = Account.objects.get(id=runner_id)
    # this_account.goal = request.POST['runner_goal']
    this_account.save()
    this_team = Team.objects.get(id=request.POST['team_id'])
    context = {"team": this_team}

    new_goal = Goal(runner=this_account, team=this_team, goal=request.POST['runner_goal'])
    new_goal.save()

    return render(request, 'joggerlogger/team_detail_coach.html', context)


@login_required
def add(request):
    if request.method == "GET":
        raise Http404

    context = {}
    if not request.POST["email"] or not request.POST['team_id']:  # missing email field or team_id field
        # need to do error checking on this so that the website does not crash
        pass
    else:
        email = request.POST["email"]
        this_team = Team.objects.get(id=request.POST['team_id'])
        try:  # make sure the email is valid
            validate_email(email)
        except ValidationError as e1:
            context = {"team": this_team}
            return render(request, "joggerlogger/error.html", {'error': 'Not a valid email address'})

        # check if the user is in the database
        try:
            added_user = User.objects.get(email=email)
        except:
            # error message if the user does not have an account
            context["message"] = "The user you are trying to add does not have an account yet"
            context["team"] = this_team
            return render(request, 'joggerlogger/team_detail_coach.html', context)

        added_account = Account.objects.get(user=added_user)

        # error checking
        if added_account == this_team.coach or added_account in this_team.runners.all():
            context = {"message": "This runner is in this team.", "team": this_team}
            return render(request, 'joggerlogger/team_detail_coach.html', context)

        # the added user has an account 
        # send a notification email to the added user
        subject = "You Have Been Added To A Team"
        message = "You have been added to team " + this_team.name + " by " + request.user.first_name + " " + request.user.last_name
        from_email = settings.EMAIL_HOST_USER
        to_list = [email]
        send_mail(subject, message, from_email, to_list)

        # add the person to the team in the database
        this_team.runners.add(added_account)
        context = {"team": this_team}

        # add a dummy goal placeholder for the new member
        new_goal = Goal(runner=added_account, team=this_team, goal="not yet set by the coach")
        new_goal.save()

        return render(request, 'joggerlogger/team_detail_coach.html', context)

    this_team = Team.objects.get(id=request.POST['team_id'])
    context = {"team": this_team}
    return render(request, 'joggerlogger/team_detail_coach.html', context)


@login_required
def join(request, team_id):
    if (team_id < 0 or team_id > Team.objects.all().count()):
        return HttpResponseRedirect(reverse("team_hall"))
    this_user = request.user
    this_account = Account.objects.get(user=this_user)
    this_team = Team.objects.get(id=team_id)
    if this_account == this_team.coach or this_account in this_team.runners.all():
        return team_detail(request, team_id)
    else:
        this_team.runners.add(this_account)
        # add a dummy goal placeholder for the new member
        new_goal = Goal(runner=this_account, team=this_team, goal="not yet set by the coach")
        new_goal.save()
        return team_detail(request, team_id)


@login_required
def leave(request, team_id):
    if (team_id < 0 or team_id > Team.objects.all().count()):
        return HttpResponseRedirect(reverse("team_hall"))
    this_user = request.user
    this_account = Account.objects.get(user=this_user)
    this_team = Team.objects.get(id=team_id)
    if this_account not in this_team.runners.all():
        return team_detail(request, team_id)
    else:
        this_team.runners.remove(this_account)
        return team_detail(request, team_id)


@login_required
def search_action(request):
    if request.method == "GET":
        raise Http404
    if not request.POST["last"] or not request.POST['team_id']:
        return team_hall(request)
    prefix = request.POST["last"]
    this_team = Team.objects.get(id=request.POST['team_id'])
    results = User.objects.filter(last_name__istartswith=prefix)
    if results.count() == 0:
        message = 'No runners with last name = "{0}"'.format(prefix)
        context = {'team': this_team, 'message': message}
        return render(request, 'joggerlogger/team_detail_coach.html', context)
    if results.count() >= 1:
        context = {'team': this_team, 'results': results.order_by('last_name', 'first_name')}
        return render(request, 'joggerlogger/team_detail_coach.html', context)
    return team_hall(request)


@login_required
def profile(request, username):
    if request.method == "GET":
        if (not User.objects.filter(username=username)):
            return render(request, "joggerlogger/error.html", {'error': 'User Does Not Exist'})
        user = get_object_or_404(User, username=username)
        account = get_object_or_404(Account, user=user)
        # list goals set by others
        goals = Goal.objects.filter(runner=account)

        # my teams
        my_teams = Team.objects.filter(coach=account)

        if username == request.user.username:  # logged-in user's profile
            picture_form = PictureForm(instance=account)
            goal_form = GoalForm(instance=account)
            stats = get_stats(user)
            context = {"name": request.user.first_name + " " + request.user.last_name,
                       "picture_form": picture_form, "goal_form": goal_form,
                       "goals": goals, "my_teams": my_teams, "stats0": stats[0], "stats1": stats[1], "stats2": stats[2]}
            return render(request, 'joggerlogger/profile.html', context)
        else:  # other people's profile
            stats = get_stats(user)
            context = {"name": user.first_name + " " + user.last_name, "account": account,
                       "goals": goals, "my_teams": my_teams, "stats0": stats[0], "stats1": stats[1], "stats2": stats[2]}
            return render(request, 'joggerlogger/others_profile.html', context)
    else:
        raise Http404


@login_required
def get_photo(request, username):
    if (not User.objects.filter(username=username)):
        return render(request, "joggerlogger/error.html", {'error': 'User Does Not Exist'})
    user = get_object_or_404(User, username=username)
    account = get_object_or_404(Account, user=user)
    if not account.picture:
        raise Http404

    return HttpResponse(account.picture, content_type=account.content_type)


@login_required
def set_picture(request, username):
    if (not User.objects.filter(username=username)):
        return render(request, "joggerlogger/error.html", {'error': 'User Does Not Exist'})
    new_picture_form = PictureForm(request.POST, request.FILES)
    user = get_object_or_404(User, username=username)
    account = get_object_or_404(Account, user=user)
    if not new_picture_form.is_valid():
        # if the form is invalid, just render the page again
        return HttpResponseRedirect(reverse("profile", args=(username,)))
    else:
        pic = new_picture_form.cleaned_data['picture']
        if pic is not None:
            account.picture = pic
            account.content_type = pic.content_type
            account.save()

        return HttpResponseRedirect(reverse("profile", args=(username,)))


@login_required
def set_personal_goal(request, username):
    if (not User.objects.filter(username=username)):
        return render(request, "joggerlogger/error.html", {'error': 'User Does Not Exist'})
    new_goal_form = GoalForm(request.POST)
    user = get_object_or_404(User, username=username)
    account = get_object_or_404(Account, user=user)

    if not new_goal_form.is_valid():
        # if the form is invalid, just render the page again
        return HttpResponseRedirect(reverse("profile", args=(username,)))

    goal = new_goal_form.cleaned_data['goal']
    if goal is not None:
        account.goal = goal
        account.save()
        return HttpResponseRedirect(reverse("profile", args=(username,)))


@login_required
def account_search(request):
    if request.method != "GET":
        raise Http404

    context = {}
    if 'search' in request.GET:
        search_text = request.GET['search']
        users = set()
        for p in User.objects.filter(first_name__icontains=search_text):
            users.add((p, p.account.first()))
        for p in User.objects.filter(last_name__icontains=search_text):
            users.add((p, p.account.first()))
        for p in User.objects.filter(username__icontains=search_text):
            users.add((p, p.account.first()))
        context['results'] = users
    return render(request, "joggerlogger/user_search.html", context)
