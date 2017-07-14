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

import socket
from smtplib import SMTPException

from django.test.testcases import TestCase
from django.test.utils import override_settings
from mock.mock import patch
from website.apps.email.models import Email, DoNotSendEmailList


class EmailTest(TestCase):
    def test_str(self):
        email_object = Email.objects.create(
            email_recipient="12345@example.com",
            from_address="123@example.com",
            email_subject="hi",
            email_body="hello",
        )
        self.assertEqual(str(email_object), "12345@example.com")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
    def test(self):
        email_object = Email.objects.create(
            email_recipient="123@example.com",
            from_address="123@example.com",
            email_subject="hi",
            email_body="hello",
        )
        self.assertIsNone(email_object.sent_timestamp)

        result = email_object.send()

        self.assertEqual(result, True)
        self.assertEqual(email_object.last_error_message, None)
        self.assertIsNotNone(email_object.sent_timestamp)
        email_object.refresh_from_db()
        self.assertEqual(email_object.last_error_message, None)
        self.assertIsNotNone(email_object.sent_timestamp)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
    def test_do_not_send_list(self):
        DoNotSendEmailList.objects.create(email="123@Example.com")
        email_object = Email.objects.create(
            email_recipient="123@example.com",
            from_address="123@example.com",
            email_subject="hi",
            email_body="hello",
        )
        self.assertIsNone(email_object.sent_timestamp)

        result = email_object.send()

        self.assertEqual(result, False)
        self.assertEqual(email_object.last_error_message, "Email 123@example.com is on do not send list")
        self.assertIsNone(email_object.sent_timestamp)
        email_object.refresh_from_db()
        self.assertEqual(email_object.last_error_message, "Email 123@example.com is on do not send list")
        self.assertIsNone(email_object.sent_timestamp)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
    @patch("website.apps.email.models.send_mail")
    def test_send_mail_fails(self, send_mail_func):
        email_object = Email.objects.create(
            email_recipient="123@example.com",
            from_address="123@example.com",
            email_subject="hi",
            email_body="hello",
        )
        self.assertIsNone(email_object.sent_timestamp)
        send_mail_func.side_effect = SMTPException("Test exception")

        result = email_object.send()

        self.assertEqual(result, False)
        self.assertEqual(email_object.last_error_message, "Test exception")
        self.assertIsNone(email_object.sent_timestamp)
        email_object.refresh_from_db()
        self.assertEqual(email_object.last_error_message, "Test exception")
        self.assertIsNone(email_object.sent_timestamp)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
    @patch("website.apps.email.models.send_mail")
    def test_send_exception_in_send_mail(self, send_mail_func):
        email_object = Email.objects.create(
            email_recipient="123@example.com",
            from_address="123@example.com",
            email_subject="hi",
            email_body="hello",
        )
        self.assertIsNone(email_object.sent_timestamp)
        send_mail_func.side_effect = Exception("Boom!")

        result = email_object.send()

        self.assertEqual(result, False)
        self.assertEqual(email_object.last_error_message, "Server error: Boom!")
        self.assertIsNone(email_object.sent_timestamp)
        email_object.refresh_from_db()
        self.assertEqual(email_object.last_error_message, "Server error: Boom!")
        self.assertIsNone(email_object.sent_timestamp)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
    @patch("website.apps.email.models.send_mail")
    def test_send_socket_exception_in_send_mail(self, send_mail_func):
        email_object = Email.objects.create(
            email_recipient="123@example.com",
            from_address="123@example.com",
            email_subject="hi",
            email_body="hello",
        )
        self.assertIsNone(email_object.sent_timestamp)
        send_mail_func.side_effect = socket.error("Boom!")

        result = email_object.send()

        self.assertEqual(result, False)
        self.assertEqual(
            email_object.last_error_message,
            "Can't connect to mail server to send email. Socket error: Boom!"
        )
        self.assertIsNone(email_object.sent_timestamp)
        email_object.refresh_from_db()
        self.assertEqual(
            email_object.last_error_message,
            "Can't connect to mail server to send email. Socket error: Boom!"
        )
        self.assertIsNone(email_object.sent_timestamp)
