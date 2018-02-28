# -*- coding: utf-8 -*-
#
# This file is part of the VecNet OpenMalaria Portal.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/om
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0.  If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

from website.apps.email.models import DoNotSendEmailList, Email

from django.core.mail import mail_managers
from django.template.loader import get_template
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_html_email(recipients,
                    subject,
                    text,
                    template_path,
                    send_to_managers=False,
                    from_email=None,
                    tracking_code=None,
                    **kwargs):
    """ Send email in html format to a list of users.
    If interview object is provided, should_send_emails attribute will be checked first and no emails will
    be sent if it is False.

    :param recipients: list of email addresses.
    :param subject: Email subject
    :param text: Text message (for email clients with no MIME support)
    :param template_path: Django template - will be used as email template
    :param send_to_managers: Send this email to all managers
    :param from_email: FROM field in email header
    :param kwargs: Context variable for email template
    :return: None if should_send_emails is False
             True if completed successfully
             False if couldn't deliver email(s)
    """

    if not isinstance(recipients, list):
        if recipients is not None:
            recipients = [recipients]

    # Do not send list
    if recipients:
        filtered_recipients = []

        for recipient in recipients:
            if not DoNotSendEmailList.objects.filter(email__iexact=recipient).exists():
                filtered_recipients.append(recipient)
            else:
                logger.info("%s is on do not send list, skipping" % recipient)

        if not filtered_recipients:
            return False, "Email opted out from the research"

        recipients = filtered_recipients

    template = get_template(template_path)
    context_variables = dict(list(kwargs.items()))
    html_code = template.render(context_variables)

    return send_html_email_by_html(
        recipients=recipients, subject=subject, text=text, html_code=html_code, send_to_managers=send_to_managers,
        from_email=from_email, tracking_code=tracking_code
    )


def send_html_email_by_html(recipients, subject, text, html_code, send_to_managers, from_email, tracking_code):
    if send_to_managers:
        # mail_managers does not return error message even if fails
        mail_managers(subject, message=text, html_message=html_code, fail_silently=True)

    last_error_message = None

    if recipients is not None:
        # We should probably refactor Email model to accept multiple email addresses someday
        for recipient in recipients:
            email_object = Email.objects.create(
                email_recipient=recipient,
                from_address=from_email or settings.DEFAULT_FROM_EMAIL,
                email_subject=subject,
                email_body=html_code,
                tracking_code=tracking_code
            )

            if not email_object.send():
                last_error_message = email_object.last_error_message

    result = True

    if last_error_message:
        result = False

    return result, last_error_message
