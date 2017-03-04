import StringIO
from django.core.files.base import ContentFile, File
from django.test.testcases import TestCase

from website.apps.ts_om.models import Simulation


class Test(TestCase):
    def test(self):
        simulation = Simulation.objects.create()
        f = ContentFile("123456")
        fp = File(open("LICENSE.txt"))
        simulation.input_file.save("1234.txt", fp)

        print simulation
        print simulation.input_file.name

        sim = Simulation.objects.get(pk=simulation.pk)
        print sim
        print sim.input_file.name

