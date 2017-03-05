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

import factory
import os

from django.contrib.auth.models import User

from website.apps.ts_om import models


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def get_xml(filename="default.xml"):
    with open(os.path.join(DATA_DIR, filename)) as fp:
        xml = fp.read()
    return xml


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    # http://stackoverflow.com/questions/15616277/how-can-you-create-an-admin-user-with-factory-boy
    password = factory.PostGenerationMethodCall('set_password', '1')
    is_staff = False
    is_superuser = False
    is_active = True


class ScenarioFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Scenario

    user = factory.SubFactory(UserFactory)
    xml = get_xml()
    description = factory.Sequence(lambda n: 'description_{0}'.format(n))

