import random
import requests

from django.http import HttpResponse
from django.template import RequestContext
from django.template.context_processors import csrf
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login
from api.models import ClientUser as User
from ussdframework.core import UssdRequest

from ussd.views import USSDGateWayOukitel
from .forms import DialForm, InputForm


class UssdSimulatorView(View):
    """
    View for creating ussd simulators.
    """

    # In the view class that inherits this view,
    # set standalone_ussd_simulator = True
    # if that simulator is going to be a standalone simulator,
    # ie (one that is not coupled with the ussd app)
    standalone_ussd_simulator = False
    ussd_view_url_name = 'gateway'
    initial_input = ''
    ussd_view = USSDGateWayOukitel
    http_method = 'post'
    initial_input = '*200#'

    def __init__(self, **kwargs):
        super(UssdSimulatorView, self).__init__(**kwargs)
        self.login_required = getattr(self, 'login_required', True)
        if self.standalone_ussd_simulator:
            self.ussd_view_url = self.ussd_view_url_name
        else:
            self.ussd_view_url = reverse(self.ussd_view_url_name)

    def dispatch(self, request, *args, **kwargs):
        return super(UssdSimulatorView, self).dispatch(
            request, *args, **kwargs)

    @classmethod
    def as_view(cls, **initkwargs):
        """
        Store the original class on the view function.

        This allows us to discover information about the view when we do URL
        reverse lookups.  Used for breadcrumb generation.
        """
        view = super(UssdSimulatorView, cls).as_view(**initkwargs)
        view.cls = cls
        return view

    def post(self, request):
        # if its a login form process the authentification
        if request.POST.get('password', False):
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                return self.get(request)

        # if login is required make sure the user is logged in
        if self.login_required and not request.user.is_authenticated:
            return self.get(request)

        # Process ussd transactions
        if not request.session.get('phone_number', False):
            return self.initiate(request)
        return self.interact(request)

    def get(self, request):
        if self.login_required and not request.user.is_authenticated:
            # if user is not logged in redirect to login form
            return render(request, 'login.html')

        # each time you do a get the session is cleared
        authenticated_user = request.session.get('_auth_user_id')
        authentication_backend = request.session.get('_auth_user_backend')
        request.session.clear()
        request.session['_auth_user_id'] = authenticated_user
        request.session['_auth_user_backend'] = authentication_backend

        # this hack forces the session not to logout
        login(
            request,
            User.objects.get(pk=authenticated_user),
            backend=authentication_backend
        )

        if self.standalone_ussd_simulator:
            absolute_url = self.ussd_view_url_name
        else:
            absolute_url = request.build_absolute_uri(
                reverse(self.ussd_view_url_name)
            )
        dial_form = DialForm(initial={'service_url': absolute_url})
        if hasattr(self, 'language_choices'):
            dial_form.fields['language'].widget.choices = self.language_choices
        return render(
            request, 'initiate.html',
            context={'form': dial_form},
        )

    def initiate(self, request):
        """Request user's phone number. This would ordinarily be provided
        by the mobile operator; we need it to correctly simulate
        interaction ."""
        data = {}
        data.update(csrf(request))

        form = DialForm(request.POST)
        if form.is_valid():
            request.session['phone_number'] = form.cleaned_data['phone_number']
            request.session['service_url'] = form.cleaned_data['service_url']
            request.session['language'] = form.cleaned_data['language']
            request.session['session_id'] = str(random.randint(0, 10000)) + \
                                            '-sim-' + \
                                            '{0}'.format(getattr(settings, 'STAGE', 'environment_not_set'))
            return self.post(request)
        return self.get(request)

    def interact(self, request):
        """Accept input from user and display menus from the application"""
        data = {}
        data.update(csrf(request))

        if self.standalone_ussd_simulator:
            user_input = self.initial_input
        else:
            user_input = self.initial_input

        form = InputForm(request.POST)
        if form.is_valid():
            user_input = form.cleaned_data['input']

        # Always create a new unbound form (so that previous inputs don't
        # show up in current form fields)
        form = InputForm()
        try:
            # enable the simulator to create ussd request
            if getattr(self, 'request_handler', False):
                response = UssdRequest(
                    phoneNumber=request.session['phone_number'],
                    sessionId=request.session.get('session_id'),
                    input=user_input,
                    serviceCode="ussdSimulator",
                    language=request.session.get('language', 'en'),
                    ussd_url=request.session['service_url'],
                    request=request
                )

            else:
                # get the data used to create ussd request
                phone_number = getattr(self, 'phoneNumber', 'phoneNumber')
                session_id = getattr(self, 'session_id', 'sessionId')
                input = getattr(self, 'input', 'text')
                language = getattr(self, 'language', 'language')
                extra_args = getattr(self, 'extra_args', {})

                data = {
                    phone_number: request.session['phone_number'],
                    session_id: request.session.get('session_id'),
                    input: user_input,
                    'serviceCode': self.initial_input,
                    language: request.session.get('language', 'en')
                }
                data.update(extra_args)

                if hasattr(self.ussd_view, 'get'):
                    response = requests.get(
                        request.session['service_url'],
                        params=data, verify=False
                    )
                else:
                    response = requests.post(
                        request.session['service_url'],
                        data=data, verify=False
                    )

            if response.status_code == 500:
                return HttpResponse(response)
            status, message = self.response_handler(response)

            # status should be a boolean
            data['status'] = status
            data['message'] = message
        except ValueError:
            data['message'] = '<Invalid response from app>'
        data['form'] = form
        data['request_url'] = request.session['service_url']
        data['post_data'] = request.session.load()
        return render(request, 'interact.html', data)

    def response_handler(self, response):
        """
        manipulates http response and returns message and status of session
        in the response
        :param response:
        :return:
        """
        return True if response.headers.get('status') == 'CON' else False, response.text
