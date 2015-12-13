# -*- coding: utf-8 -*-
from django import forms

class DocumentForm(forms.Form):
    xmlfile = forms.FileField(label='Select the input xml file (scenario.xml)')
    outputfile = forms.FileField(label='Select the survery output file (output.txt) if available', required=False)
    ctsoutputfile = forms.FileField(label='Select the continuous file (ctsout.txt) if available', required=False)
    save_to = forms.BooleanField(initial=False, label='Save to My Scenarios', required=False)
    scenario_label = forms.CharField(label="Scenario name (optional)", required=False)