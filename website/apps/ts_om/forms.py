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

from django import forms

from django.forms import ModelForm

from .models import ExperimentFile
from .models import BaselineScenario


class ScenarioSummaryForm(forms.Form):
    xml = forms.CharField(widget=forms.Textarea)
    desc = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Description', 'rows': '3'}), required=False)
    simulation_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    submit_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name'}), required=True)


class ScenarioStartForm(forms.Form):
    CHOICES = [('build', 'Build new simulation'),
               ('list', 'Choose existing simulation from a list'),
               ('upload', 'Upload existing XML file')]

    choice = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), initial=CHOICES[0][0])
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name', 'class': 'form-control'}),
                           required=True)
    desc = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Description', 'rows': '3', 'class': 'form-control'}), required=False)
    list = forms.ModelChoiceField(queryset=BaselineScenario.objects.all(),
                                  widget=forms.Select(attrs={'class': 'form-control'}),
                                  empty_label=None,
                                  required=False)
    xml_file = forms.FileField(required=False)

    def clean(self):
        clean_data = super(ScenarioStartForm, self).clean()

        choice = clean_data.get("choice")

        if choice == "upload":
            xml_file = clean_data.get("xml_file")

            if not xml_file:
                raise forms.ValidationError("No scenario xml file chosen for upload.")


class ExperimentUploadForm(ModelForm):
    class Meta:
        model = ExperimentFile
        fields = ['name', 'file']

    def __init__(self, *args, **kwargs):
        super(ExperimentUploadForm, self).__init__(*args, **kwargs)

        self.fields["name"].widget.attrs["class"] = "form-control"
