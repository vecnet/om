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

import logging
import socket
from smtplib import SMTPException

import html2text
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.utils.timezone import now


logger = logging.getLogger(__name__)


class DoNotSendEmailList(models.Model):
    """
    List of people who opted out of the research. No invitation emails should be sent to those people.
    """
    email = models.TextField(default=None)  # email is required and can't be None
    notes = models.TextField(blank=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)  # Auto saves on create
    last_modified_timestamp = models.DateTimeField(auto_now=True)  # Auto updates on save

    def __str__(self):
        return "%s" % self.email

    class Meta:
        get_latest_by = 'last_modified_timestamp'
        managed = True  # Django manages the database table's lifecycle.
        ordering = ['last_modified_timestamp', ]


class Email(models.Model):
    UNSENT = "Unsent"
    FAILED = "Failed"
    SENT = "Sent"

    STATUSES = (UNSENT, FAILED, SENT)

    email_recipient = models.TextField(default=None)  # email_address is required
    from_address = models.TextField(default=None)
    # Email subject line
    email_subject = models.TextField(default=None)
    # Email body
    email_body = models.TextField(default=None)
    # Tracking code used in this email (optional)
    tracking_code = models.TextField(null=True, blank=True, default=None)
    # Email status - unsent, failed, sent
    # You should use CharField instead TextField to get select menu - TextField rendered always as TextArea
    status = models.CharField(choices=zip(STATUSES, STATUSES), default=UNSENT, max_length=30)

    sent_timestamp = models.DateTimeField(null=True, blank=True, default=None)
    last_error_message = models.TextField(null=True, blank=True)

    creation_timestamp = models.DateTimeField(auto_now_add=True)  # Auto saves on create
    last_modified_timestamp = models.DateTimeField(auto_now=True)  # Auto updates on save

    class Meta:
        managed = True
        db_table = "email"
        verbose_name = "Email"
        verbose_name_plural = "Emails"

    def __str__(self):
        return self.email_recipient

    def send(self):
        """  Attempt to send this email
        If email is accepted for the delivery, sent_timestamp is set to now
        If error happens (email server is down etc), last_error_message is set
        :return: True or False
        """
        if DoNotSendEmailList.objects.filter(email__iexact=self.email_recipient).first():
            # Prevent from sending emails to people who opted out from research
            error_message = "Email %s is on do not send list" % self.email_recipient
            logger.error(error_message)
            self.last_error_message = error_message
            self.status = Email.FAILED
            self.save()

            return False

        # Override recipient list - for debugging purpose
        recipients = [self.email_recipient]
        if hasattr(settings, "SEND_HTML_EMAIL_ADDRESS"):
            recipients = settings.SEND_HTML_EMAIL_ADDRESS

            if not isinstance(recipients, list):
                if recipients is not None:
                    recipients = [recipients]

        try:
            send_mail(self.email_subject,
                      html2text.html2text(self.email_body),
                      self.from_address,
                      recipients,
                      html_message=self.email_body,
                      fail_silently=False)
        except SMTPException as e:
                error_message = "Can't send email to %s: %s" % (self.email_recipient, e)
                logger.error(error_message)
                self.last_error_message = str(e)
                self.status = Email.FAILED
                self.save()
                return False
        except socket.error as e:
            # For some reason, socket exceptions are raised even when fail_silently is set to True
            error_message = "Can't connect to mail server to send email. Socket error: %s" % e
            logger.error(error_message)
            self.last_error_message = error_message
            self.status = Email.FAILED
            self.save()
            return False
        except Exception as e:
            # This shouldn't happen, but just in case
            error_message = "Exception in send_mail. Stacktrace is below for your convenience"
            logger.critical(error_message)
            logger.exception(e)
            self.last_error_message = "Server error: %s" % e
            self.status = Email.FAILED
            self.save()
            return False

        logger.debug("Successfully sent email to %s" % self.email_recipient)

        self.sent_timestamp = now()
        self.last_error_message = None
        self.status = Email.SENT
        self.save()

        return True
