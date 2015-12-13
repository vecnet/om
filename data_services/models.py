########################################################################################################################
# VECNet CI - Prototype
# Date: 4/5/2013
# Institution: University of Notre Dame
# Primary Authors:
#   Lawrence Selvy <Lawrence.Selvy.1@nd.edu>
#   Zachary Torstrick <Zachary.R.Torstrick.1@nd.edu>
########################################################################################################################
import datetime
import logging
import tempfile
from wsgiref.util import FileWrapper
import zipfile
from django.core.exceptions import ObjectDoesNotExist

from django.db import models
from jsonfield import JSONField
from vecnet.simulation import sim_model, sim_status

from .sim_file_server.conf import get_active_server

logger = logging.getLogger('prod_logger')


def make_choices_tuple(choices, get_display_name):
    """
    Make a tuple for the choices parameter for a data model field.

    :param choices: sequence of valid values for the model field
    :param get_display_name: callable that returns the human-readable name for a choice

    :return: A tuple of 2-tuples (choice, display_name) suitable for the choices parameter
    """
    assert callable(get_display_name)
    return tuple((x, get_display_name(x)) for x in choices)


class DimUser(models.Model):
    def __str__(self):
        return self.username
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    organization = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(null=True)

    class Meta:
        db_table = 'dim_user'


class SimulationGroup(models.Model):
    """
    Represents a group of simulations submitted for execution at the same time.
    """
    submitted_by = models.ForeignKey(DimUser,
                                     help_text='who submitted the group for execution')
    submitted_when = models.DateTimeField(help_text='when was the group submitted',
                                          null=True, blank=True)  # Assigned by job services

    def __str__(self):
        return "%s" % self.id

    def create_om_zip_file(self, name):
        # s = StringIO.StringIO()

        temp = tempfile.TemporaryFile()
        with zipfile.ZipFile(temp, 'w') as sim_file:
            for sim in Simulation.objects.filter(group=self):
                assert sim.model == sim_model.OPEN_MALARIA

                try:
                    input_file = sim.input_files.get(name="scenario.xml")
                    file_name = input_file.metadata.get("filename", "scenario%s.xml" % input_file.id)
                    sim_file.writestr(file_name, input_file.get_contents())
                except ObjectDoesNotExist:
                    raise RuntimeError("Scenario.xml does not exist in simulation #%s" % sim.id)
                try:
                    output_file = sim.simulationoutputfile_set.get(name="output.txt")
                    sim_file.writestr(file_name.replace(".xml", "_output.txt"), output_file.get_contents())
                except ObjectDoesNotExist:
                    pass
                try:
                    continuous_file = sim.simulationoutputfile_set.get(name="ctsout.txt")
                    sim_file.writestr(file_name.replace(".xml", "_ctsout.txt"), continuous_file.get_contents())
                except ObjectDoesNotExist:
                    pass

        wrapper = FileWrapper(temp)
        temp_len = temp.tell()
        temp.seek(0)

        return wrapper, temp_len


class Simulation(models.Model):
    """
    Represents a single execution of a simulation model.  Contains sufficient information about the particular
    simulation model that was run and the input data so that the output data can be reproduced.
    """
    group = models.ForeignKey(SimulationGroup, related_name='simulations')
    model = models.CharField(help_text='simulation model ID',
                             choices=make_choices_tuple(sim_model.ALL, sim_model.get_name),
                             max_length=sim_model.MAX_LENGTH)
    version = models.CharField(help_text='version of simulation model',
                               max_length=20)
                               #  Format varies from model to model; i.e., it's model specific
    cmd_line_args = models.CharField(help_text='additional command line arguments passed to the model',
                                     max_length=100,
                                     blank=True)
    status = models.CharField(help_text='status of the simulation',
                              choices=make_choices_tuple(sim_status.ALL, sim_status.get_description),
                              max_length=sim_status.MAX_LENGTH)
    started_when = models.DateTimeField(help_text='when was the simulation started',
                                        null=True, blank=True)  # Collected on the cluster
    duration = models.BigIntegerField(help_text='how long the simulation ran (in seconds)',
                                      null=True, blank=True)  # Collected on the cluster

    @property
    def duration_as_timedelta(self):
        """
        Get the simulation's duration as a Python timedelta object.
        """
        if self.duration is None:
            return None
        return datetime.timedelta(seconds=self.duration)

    @property
    def ended_when(self):
        """
        When did the simulation end (either successfully or due to error).

        :return datetime: Date and time when the simulation stopped, or None if it has not yet started or is still
                          running.
        """
        if self.started_when is None or self.duration is None:
            return None
        return self.started_when + self.duration_as_timedelta

    def copy(self, include_output=False, should_link_files=False):
        simulation_group = SimulationGroup(submitted_by=self.group.submitted_by)
        simulation_group.save()

        new_simulation = Simulation.objects.create(
            group=simulation_group,
            model=self.model,
            version=self.version,
            status=sim_status.READY_TO_RUN
        )

        # Add simulation input files to the new simulation
        for input_file in self.input_files.all():
            if should_link_files:
                new_simulation.input_files.add(input_file)
            else:
                new_simulation.input_files.add(input_file.copy())

        if include_output:
            # Add simulation output files to the new simulation
            for output_file in self.output_files.all():
                new_simulation.output_files.add(output_file.copy())

        return new_simulation

    def __str__(self):
        return "%s (%s v%s) - %s" % (self.id, self.model, self.version, self.status)


class SimulationFile(models.Model):
    """
    Base class for a simulation's data file (input files and output files).
    """
    class Meta:
        abstract = True

    class MetadataKeys:
        CHECKSUM = 'checksum'  # For verifying downloads of the file and accidental corruption on file server
        CHECKSUM_ALGORITHM = 'checksum_alg'

    class ChecksumAlgorithms:
        MD5 = 'MD5'

    name = models.TextField(help_text="file's name (e.g., 'ctsout.txt', 'config.json')")
                            # Within a single simulation, a data file's name is unique.  No two input files share the
                            # the same name, nor do any two output files.
    uri = models.TextField(help_text="where the file's contents are stored")
                          # In the long term, this points to a file storage service/server (e.g., WebDAV, MongoDB, ...)
                          # As short-term approach, the contents can be stored in this field using the "data:" scheme
                          #    http://en.wikipedia.org/wiki/Data_URI_scheme
    metadata = JSONField(help_text="additional info about the file, e.g., its data format")
                         # If we discover that a particular metadata field is queried a lot, we can optimize the queries
                         # in several ways (explicit indexes in another table; moved the field into its own model field,
                         # etc).

    def get_contents(self):
        """
        Read all the bytes in the file.

        :returns str: The file's contents
        """
        with self.open_for_reading() as f:
            contents = f.read()
        return contents

    def open_for_reading(self):
        """
        Opens the file so its contents can be read in binary mode.

        :returns: A file-like object with at least a read() method.  It's also a context manager so it can be used in a
                  "with" statement.
        """
        file_server = get_active_server()
        file_like_obj = file_server.open_for_reading(self.uri)
        return file_like_obj

    def _set_contents(self, contents, is_binary=True):
        file_server = get_active_server()
        (self.uri, md5_hash) = file_server.store_file(contents)
        self.metadata = {
            self.MetadataKeys.CHECKSUM: md5_hash,
            self.MetadataKeys.CHECKSUM_ALGORITHM: 'MD5',
        }
        self.save()

    def copy(self):
        if isinstance(self, SimulationInputFile):
            new_simulation_file = SimulationInputFile.objects.create_file(
                contents=self.get_contents(),
                name=self.name,
                metadata=self.metadata,
                created_by=self.created_by
            )
        elif isinstance(self, SimulationOutputFile):
            new_simulation_file = SimulationOutputFile.objects.create_file(
                contents=self.get_contents(),
                name=self.name,
                metadata=self.metadata,
            )
        else:
            raise Exception("SimulationFile is not of type SimulationInputFile nor SimulationOutputFile")

        return new_simulation_file

    def __str__(self):
        return "%s - %s" % (self.id, self.name)


class SimulationFileModelManager(models.Manager):
    """
    Custom model manager for the data models representing simulation files.
    """

    def create_file(self, contents, **kwargs):
        sim_file = self.create(**kwargs)
        sim_file._set_contents(contents)
        return sim_file


class SimulationInputFile(SimulationFile):
    """
    An input file for a simulation.  An input file can be shared among multiple simulations.  An input file is
    immutable since it represents all or some of the data fed into a particular execution of the simulation model.  If
    it is altered, then it's no longer possible to reproduce the output from the simulation.

    An input file at this conceptual level is different than the concept at the user's perspective.  From her viewpoint,
    an input file is mutable.  For example, an OpenMalaria user can create a scenario file and then run a simulation
    with it.  After examining the simulation's output, she makes some changes in the scenario and re-runs it.  From her
    perspective, the two simulations were run with different versions of a single scenario file.  Those two versions
    of that scenario file would be represented by two instances of this class.  Their relationship as snapshots of the
    same scenario file would be stored in another data model.
    """
    simulations = models.ManyToManyField(Simulation,
                                         help_text='the simulations that used this file as input',
                                         related_name='input_files')
    created_by = models.ForeignKey(DimUser,
                                   help_text='who created the file')
    created_when = models.DateTimeField(help_text='when was the file created',
                                        auto_now_add=True)

    objects = SimulationFileModelManager()

    def set_contents(self, contents):
        simulations = self.simulations.all()

        if len(simulations) > 1:
            raise RuntimeError("File is shared by multiple simulations.")

        if len(simulations) == 0 or simulations[0].status == sim_status.READY_TO_RUN:
            self._set_contents(contents)
        else:
            raise RuntimeError("Simulation is not ready to run.")


class SimulationOutputFile(SimulationFile):
    """
    An output file produced by a simulation.
    """
    simulation = models.ForeignKey(Simulation,
                                   null=True,
                                   blank=True,
                                   help_text='the simulation that produced this file')

    objects = SimulationFileModelManager()


