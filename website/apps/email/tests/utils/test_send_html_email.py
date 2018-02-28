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

from smtplib import SMTPConnectError

from django.conf import settings
from django.test import TestCase, override_settings
from mock import patch
from website.apps.email.models import DoNotSendEmailList, Email

from website.apps.email.utils.send_html_email import send_html_email


class SendHtmlEmailTest(TestCase):
    @patch("website.apps.email.models.send_mail")
    @patch("website.apps.email.utils.send_html_email.mail_managers")
    def test_success(self, mail_managers, send_mail):
        result, message = send_html_email(
            "alex@example.com",
            "Subject",
            "Test",
            "base.html")
        self.assertTrue(send_mail.called)
        self.assertFalse(mail_managers.called)
        self.assertEqual(send_mail.call_args[0][2], settings.DEFAULT_FROM_EMAIL)
        self.assertTrue(result)
        self.assertIsNone(message)

        self.assertEqual(Email.objects.count(), 1)
        email_object = Email.objects.all()[0]
        self.assertEqual(email_object.email_recipient, "alex@example.com")
        self.assertEqual(email_object.email_subject, "Subject")
        self.assertEqual(email_object.from_address, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(email_object.last_error_message, None)

    @patch("website.apps.email.models.send_mail")
    @patch("website.apps.email.utils.send_html_email.mail_managers")
    def test_send_mail_fails(self, mail_managers, send_mail):
        send_mail.side_effect = SMTPConnectError(10, msg="Can't connect")
        result, message = send_html_email(
            "avyushko@nd.edu",
            "Subject",
            "Test",
            "base.html")
        self.assertTrue(send_mail.called)
        self.assertFalse(mail_managers.called)
        self.assertEqual(send_mail.call_args[0][2], settings.DEFAULT_FROM_EMAIL)
        self.assertFalse(result)
        self.assertEqual(message, "(10, \"Can't connect\")")

    @patch("website.apps.email.models.send_mail")
    def test_smoke_test(self, send_mail):
        send_html_email("avyushko@nd.edu",
                        "Subject",
                        "Test",
                        "base.html")
        self.assertTrue(send_mail.called)
        self.assertEqual(send_mail.call_args[0][2], settings.DEFAULT_FROM_EMAIL)

    @patch("website.apps.email.models.send_mail")
    def test_recipients_none(self, send_mail):
        result, message = send_html_email(
            None,
            "Subject",
            "Test",
            "base.html")
        self.assertFalse(send_mail.called)
        self.assertTrue(result)
        self.assertIsNone(message)
        self.assertEqual(Email.objects.count(), 0)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
    @patch("website.apps.email.models.send_mail")
    def test_from_email(self, send_mail):
        send_html_email("avyushko@nd.edu",
                        "Subject",
                        "Test",
                        "base.html",
                        from_email="test@gmail.com")
        self.assertTrue(send_mail.called)
        self.assertEqual(send_mail.call_args[0][2], "test@gmail.com")
        self.assertEqual(Email.objects.count(), 1)

        email_object = Email.objects.all()[0]
        self.assertEqual(email_object.email_recipient, "avyushko@nd.edu")
        self.assertEqual(email_object.email_subject, "Subject")
        self.assertEqual(email_object.from_address, "test@gmail.com")

    @override_settings(EMAIL_HOST="no.server")
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
    def test_wrong_mail_server(self):
        # To trigger "socket error" branch
        result, message = send_html_email(
            "avyushko@nd.edu",
            "Subject",
            "Test",
            "base.html",
            from_email="test@gmail.com")
        self.assertFalse(result)
        # self.assertIn("[Errno 11001] getaddrinfo failed", message)
        self.assertEqual(Email.objects.count(), 1)
        email_object = Email.objects.all()[0]
        self.assertEqual(email_object.email_recipient, "avyushko@nd.edu")
        self.assertEqual(email_object.email_subject, "Subject")
        self.assertEqual(email_object.from_address, "test@gmail.com")
        self.assertNotEqual(email_object.last_error_message, "")

    @override_settings(EMAIL_HOST="no.server")
    @override_settings(EMAIL_BACKEND="wrong.EmailBackend")
    def test_wrong_mail_backend(self):
        # To trigger "Server Error" branch in send_html_email
        result, message = send_html_email(
            "avyushko@nd.edu",
            "Subject",
            "Test",
            "base.html",
            from_email="test@gmail.com")
        self.assertFalse(result)
        self.assertIn("No module named 'wrong'", message)

    @patch("website.apps.email.models.send_mail")
    @override_settings(SEND_HTML_EMAIL_ADDRESS="123@example.com")
    def test_send_html_email_option(self, send_mail):
        result, message = send_html_email(
            "alex@example.com",
            "Subject",
            "Test",
            "base.html",
            from_email="test@gmail.com")
        self.assertTrue(result)
        self.assertEqual(send_mail.call_args[0][3], ["123@example.com"])
        self.assertEqual(Email.objects.count(), 1)

        email_object = Email.objects.all()[0]
        self.assertEqual(email_object.email_recipient, "alex@example.com")
        self.assertEqual(email_object.email_subject, "Subject")
        self.assertEqual(email_object.from_address, "test@gmail.com")

    @patch("website.apps.email.models.send_mail")
    def test_do_not_send_list_1(self, send_mail):
        DoNotSendEmailList.objects.create(email="alex@example.com")
        result, message = send_html_email(
            "alex@example.com",
            "Subject",
            "Test",
            "base.html",
            from_email="test@gmail.com")
        self.assertFalse(result)
        self.assertIn("Email opted out from the research", message)
        self.assertFalse(send_mail.called)
        self.assertEqual(Email.objects.count(), 0)

    @patch("website.apps.email.models.send_mail")
    def test_do_not_send_list_2(self, send_mail):
        DoNotSendEmailList.objects.create(email="ALEX@example.com")
        result, message = send_html_email(
            "alex@example.com",
            "Subject",
            "Test",
            "base.html",
            from_email="test@gmail.com")
        self.assertFalse(result)
        self.assertIn("Email opted out from the research", message)
        self.assertFalse(send_mail.called)
        self.assertEqual(Email.objects.count(), 0)

    @patch("website.apps.email.models.send_mail")
    def test_do_not_send_list_3(self, send_mail):
        DoNotSendEmailList.objects.create(email="ALEX@example.com")
        DoNotSendEmailList.objects.create(email="alex1@example.com")
        result, message = send_html_email(
            ["alex@example.com", "alex1@example.com"],
            "Subject",
            "Test",
            "base.html",
            from_email="test@gmail.com")
        self.assertFalse(result)
        self.assertIn("Email opted out from the research", message)
        self.assertFalse(send_mail.called)
        self.assertEqual(Email.objects.count(), 0)

    @patch("website.apps.email.models.send_mail")
    def test_do_not_send_list_4(self, send_mail):
        DoNotSendEmailList.objects.create(email="ALEX@example.com")
        result, message = send_html_email(
            ["alex@example.com", "alex1@example.com"],
            "Subject",
            "Test",
            "base.html",
            from_email="test@gmail.com")
        self.assertTrue(result)
        self.assertTrue(send_mail.called)

        # One email will be created since we tried two users, and only one was opted out
        self.assertEqual(Email.objects.count(), 1)
        email_object = Email.objects.all()[0]
        self.assertEqual(email_object.email_recipient, "alex1@example.com")
        self.assertEqual(email_object.email_subject, "Subject")
        self.assertEqual(email_object.from_address, "test@gmail.com")
        self.assertEqual(email_object.last_error_message, None)

    @patch("website.apps.email.utils.send_html_email.mail_managers")
    def test_send_managers(self, mail_managers):
        result, message = send_html_email(
            None,
            "Subject",
            "Test",
            "base.html",
            send_to_managers=True,
            from_email="test@gmail.com")
        self.assertTrue(result)
        self.assertTrue(mail_managers.called)
        self.assertEqual(Email.objects.count(), 0)
