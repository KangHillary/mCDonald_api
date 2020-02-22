import os

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from structlog import get_logger
from ussdframework.core import UssdView, UssdRequest


class USSDGateWayOukitel(UssdView):
    logger = get_logger(__name__).bind(action="ussd_request")
    customer_journey_namespace = "Oukitel"
    path = os.path.dirname(os.path.abspath(__file__))
    customer_journey_conf = path + "/mc_donald_ussd_journey.yml"

    def post(self, req):
        list_of_inputs = req.data['text'].split("*")
        text = "*" if len(list_of_inputs) >= 2 and list_of_inputs[-1] == "" and list_of_inputs[-2] == "" else \
        list_of_inputs[
            -1]

        ussd_request = UssdRequest(
            phone_number=req.data['phoneNumber'].strip('+'),
            session_id=req.data['sessionId'],
            ussd_input=text,
            service_code=req.data['serviceCode'],
            language=req.data.get('language', 'en')
        )

        return ussd_request

    def ussd_response_handler(self, ussd_response):
        if self.request.data.get('serviceCode') == 'test':
            return super(). \
                ussd_response_handler(ussd_response)
        if ussd_response.status:
            res = 'CON' + ' ' + str(ussd_response)
            response = HttpResponse(res)
        else:
            res = 'END' + ' ' + str(ussd_response)
            response = HttpResponse(res)
        return response
