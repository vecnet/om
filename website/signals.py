# Copyright (C) 2015, University of Notre Dame
# All rights reserved

from django.core.signals import request_finished
from django.dispatch import receiver
from registration.signals import user_activated


import logging
logger = logging.getLogger(__name__)


@receiver(request_finished)
def my_callback(sender, **kwargs):
    """Called after every request"""
    logger.debug("Request finished!")


@receiver(user_activated)
def user_activated_callback(sender, **kwargs):
    """ Called when new users confirms their email
    :param sender:
    :param kwargs:
    :return:
    """
    logger.debug("%s - New user has been activated", sender)
    # Send email to admins

