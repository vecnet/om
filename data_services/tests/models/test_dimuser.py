# Copyright (C) 2016, University of Notre Dame
# All rights reserved
from django.test.testcases import TestCase

from data_services.models import DimUser


class DimUserModelTest(TestCase):
    def test(self):
        dim_user = DimUser.objects.create(
            username="user"
        )
        self.assertEqual(str(dim_user), "user")
        self.assertIsNone(dim_user.date_joined)
