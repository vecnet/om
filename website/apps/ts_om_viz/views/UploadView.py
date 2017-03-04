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

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.generic import TemplateView
from website.apps.ts_om_viz.forms import DocumentForm
from website.notification import set_notification
from data_services.models import *
from website.apps.ts_om.models import Scenario
from vecnet.openmalaria import get_schema_version_from_xml
from django.utils.datastructures import MultiValueDictKeyError


class UploadView(TemplateView):
    template_name = 'ts_om_viz/upload.html'

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)
        context['form'] = DocumentForm(prefix='uploadForm')

        return context

    def post(self, request, **kwargs):
        # Handle file upload
        """
        :type request: django.http.HttpRequest!
        """
        form = DocumentForm(request.POST, request.FILES, prefix='uploadForm')
        # For additional details about handling uploaded files in Django please refer to
        # https://docs.djangoproject.com/en/dev/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile

        if form.is_valid():
            # create simulation group and simulation itself
            if request.user.is_anonymous():
                # Use "Test" DimUser if user is not authenticated
                username = "Test"
            else:
                # Current user will be an owner of newly created simulation group
                username = request.user.get_username()

            # Handle uploaded files
            try:
                # Continuous output is optional.
                # If it is not in request.FILES, MultiValueDictKeyError will be raised
                output = request.FILES['uploadForm-outputfile']
                output_contents = output.read()
            except MultiValueDictKeyError:
                output_contents = output = None

            try:
                # Survey output is optional.
                # If it is not in request.FILES, MultiValueDictKeyError will be raised
                ctsoutput = request.FILES['uploadForm-ctsoutputfile'].read()
            except MultiValueDictKeyError:
                ctsoutput = None

            # xml file is required, so user can't get past form validation
            # (and if they do, they can enjoy internal server error)
            xml = request.FILES['uploadForm-xmlfile'].read()

            # Creation data_services.models.Simulation object - for visualization
            sim_group = SimulationGroup(submitted_by_user=request.user)
            sim_group.save()

            om_version = get_schema_version_from_xml(xml)
            simulation = Simulation(group=sim_group,
                                    model=sim_model.OPEN_MALARIA,
                                    version=om_version,
                                    status=sim_status.SCRIPT_DONE)
            simulation.save()

            # store scenario.xml to database
            # metadata = "{\"filename\":\"%s\"}" % request.FILES['uploadForm-xmlfile'].name
            scenario_file = SimulationInputFile.objects.create_file(contents=xml, name="scenario.xml")
            scenario_file.metadata["filename"] = request.FILES['uploadForm-xmlfile'].name
            scenario_file.save()
            simulation.input_files.add(scenario_file)

            # store output.txt to database
            if output is not None:
                #metadata = "{\"filename\":\"%s\"}" % output.name
                SimulationOutputFile.objects.create_file(contents=output_contents,
                                                         name="output.txt",
                                                         simulation=simulation)

            # store ctsout.txt to database
            if ctsoutput is not None:
                SimulationOutputFile.objects.create_file(contents=ctsoutput,
                                                         name="ctsout.txt",
                                                         metadata="{}",
                                                         simulation=simulation)

            if form.cleaned_data['save_to'] is True:
                try:
                    scenario = Scenario.objects.create(xml=xml,
                                                       user=self.request.user)
                    if ctsoutput is not None or output is not None:
                        # If we have at least one output file, associate it with data_services.models.Simulation object
                        # Otherwise, create Scenario without output
                        scenario.simulation = simulation
                    if form.cleaned_data['scenario_label']:
                        scenario.name = form.cleaned_data['scenario_label']
                    scenario.save()
                    set_notification(self.request,
                                     'Scenario %s (%s) has been created successfully' % (scenario.id, scenario.name),
                                     'alert-success')
                except Exception:
                    set_notification(self.request, "Scenario creation failed", 'alert-error')

            return redirect('/ts_om_viz/sim/' + str(simulation.id))

        else:
            # Render list page with the documents and the form
            return render_to_response(
                'ts_om_viz/pageerror.html',
                {'form': form},
                context_instance=RequestContext(request))

    def invalid_notification(self, err):
        set_notification(self.request, '<strong>Error! %s</strong>' % str(err.__str__()), 'alert-error')

