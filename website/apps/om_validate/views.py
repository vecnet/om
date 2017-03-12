import logging

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from website.apps.om_validate.utils import get_xml_validation_errors

logger = logging.getLogger(__name__)


@csrf_exempt
def validate_view(request):
    logger.info("om_validate service started")
    logger.info("user: %s" % request.user)
    xml = request.read()
    response = validate_scenario(xml)

    return JsonResponse(response, safe=False)


def validate_scenario(xml):
    # Also used in ts_om application
    data = get_xml_validation_errors(xml)
    if data is None:
        response = {"result": 0}
    else:
        response = {"result": -1, "om_output": data}
    logger.debug("validate_scenario: %s" % response)
    return response
