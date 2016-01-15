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


class StandaloneSubmitForm(forms.Form):
    name = forms.CharField(required=False)
    xml = forms.CharField(widget=forms.Textarea)
    desc = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Description', 'rows': '3'}), required=False)
    model_version = forms.ChoiceField(choices=[("30", "30"), ("32", "32"), ("33", "33")])


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
