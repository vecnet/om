# Create your views here.
# PEP 0263
# -*- coding: utf-8 -*-
########################################################################################################################
# VECNet CI - Prototype
# Date: 8/1/2014
# Institution: University of Notre Dame
# Primary Authors:
#   Nicolas Reed <Nicolas.Reed.102@nd.edu>
########################################################################################################################
import zipfile

from django.views.generic import FormView

from website.apps.ts_om.forms import ExperimentUploadForm


class ExperimentUploadView(FormView):
    template_name = "ts_om_experiment/upload.html"
    form_class = ExperimentUploadForm
    success_url = "/ts_om/experiment/validate/"

    def get_context_data(self, **kwargs):
        context = super(ExperimentUploadView, self).get_context_data(**kwargs)

        if "upload_error" in self.kwargs:
            context["upload_error"] = self.kwargs["upload_error"]

        return context

    def form_valid(self, form):
        name = form.cleaned_data['name']

        experiment = form.save(commit=False)

        if not zipfile.is_zipfile(experiment.file) and not experiment.file.url.endswith(".xml"):
            self.kwargs["upload_error"] = 'Error: Invalid openmalaria experiment uploaded.'

            return super(ExperimentUploadView, self).form_invalid(form)

        experiment.user = self.request.user

        experiment.save()

        self.request.session['name'] = name
        self.request.session['experiment_id'] = experiment.id

        return super(ExperimentUploadView, self).form_valid(form)
