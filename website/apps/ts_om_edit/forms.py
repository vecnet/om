# Copyright (C) 2015, University of Notre Dame
# All rights reserved
import datetime
from xml.etree import ElementTree
from django import forms
from vecnet.openmalaria.scenario.entomology import Vector
from website.apps.ts_om.models import DemographicsSnippet, AnophelesSnippet, InterventionSnippet


class ScenarioMonitoringForm(forms.Form):
    MOS = [('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
           ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11')]
    DIAG_TYPE = [('100', 'RDT (100 parasites per microlitre)'),
                 ('200', 'Microscopy (200)'),
                 ('7', 'PCR (7)'),
                 ('custom', 'Custom')]

    daily_eir = forms.BooleanField(initial=True, required=False,
                                   widget=forms.CheckboxInput(attrs={'disabled': 'disabled', 'checked': 'checked'}))
    nr_per_age_group = forms.BooleanField(initial=True, required=False,
                                          widget=forms.CheckboxInput(attrs={'disabled': 'disabled',
                                                                            'checked': 'checked'}))
    patent_infections = forms.BooleanField(initial=True, required=False)
    uncomplicated_episodes = forms.BooleanField(initial=True, required=False)
    severe_episodes = forms.BooleanField(required=False)
    hospitalizations = forms.BooleanField(required=False)
    direct_deaths = forms.BooleanField(required=False)
    indirect_deaths = forms.BooleanField(required=False)
    itn = forms.BooleanField(required=False)
    irs = forms.BooleanField(required=False)
    mda = forms.BooleanField(required=False)
    msat = forms.BooleanField(required=False)
    vaccine = forms.BooleanField(required=False)
    nr_infections = forms.BooleanField(required=False)
    sim_start_date = forms.CharField(initial=datetime.datetime.now().year,
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    monitor_yrs = forms.CharField(initial='2',
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    monitor_mos = forms.ChoiceField(choices=MOS, initial=MOS[0][0], widget=forms.Select(attrs={'class': 'form-control'}))
    monitor_start_date = forms.CharField(initial=datetime.datetime.now().year,
                                         widget=forms.TextInput(attrs={'class': 'form-control'}))
    measure_outputs = forms.ChoiceField(choices=[('yearly', 'Yearly'), ('monthly', 'Monthly'), ('custom', 'Custom')],
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    parasite_detection_diagnostic_type = forms.ChoiceField(choices=DIAG_TYPE, widget=forms.Select(
        attrs={'class': 'form-control'}))


def get_age_dist():
    test = list(DemographicsSnippet.objects.order_by('title'))
    new_list = []
    for t in test:
        new_list.append((t.name, {
            'name': t.name,
            'title': t.title,
            'xml': t.xml,
            'url': t.url,
            'maximum_age_yrs': t.maximum_age_yrs
        }))

    new_list.append(('custom', {
        'name': 'custom',
        'title': '',
        'xml': '',
        'url': '#',
        'maximum_age_yrs': '0'
    }))

    return new_list


class ScenarioDemographyForm(forms.Form):
    POP_SIZES = [('100', '100'),
                 ('1000', '1000'),
                 ('10000', '10000'),
                 ('100000', '100000')]

    age_dist = forms.ChoiceField(choices=get_age_dist)
    human_pop_size = forms.ChoiceField(choices=POP_SIZES)
    age_dist_name = forms.CharField(widget=forms.HiddenInput())
    age_dist_xml = forms.CharField(widget=forms.HiddenInput())
    maximum_age_yrs = forms.CharField(widget=forms.HiddenInput())


class ScenarioHealthSystemForm(forms.Form):
    FIRST_LINE_DRUG_TYPE = [('ACT', 'Artimisinin combination therapy (ACT)'),
                            ('SP', 'Sulphadoxine-Pyrimethamine (SP)'),
                            ('CQ', 'Chloroquine (CQ)')]

    perc_total_treated = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    perc_formal_care = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_line_drug = forms.ChoiceField(choices=FIRST_LINE_DRUG_TYPE, widget=forms.Select(
        attrs={'class': 'form-control'}))


def get_vectors():
    vectors = list(AnophelesSnippet.objects.all())
    new_list = []
    for vector in vectors:
        v = Vector(ElementTree.fromstring(vector.anopheles))
        new_list.append((vector.name, {
            'extra': {
                'average_eir': v.seasonality.annualEIR,
                'human_blood_index': v.mosq.mosqHumanBloodIndex,
                'monthly_values': v.seasonality.monthlyValues
            }
        }))

    return new_list


class ScenarioEntomologyForm(forms.Form):
    annual_eir = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    vectors = forms.ChoiceField(choices=get_vectors, required=False, widget=forms.Select(
        attrs={'class': 'form-control'}))


class ScenarioEntomologyVectorForm(forms.Form):
    average_eir = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Annual EIR")
    human_blood_index = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    monthly_values = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.HiddenInput())


class ScenarioInterventionsForm(forms.Form):
    interventions = forms.ModelChoiceField(queryset=InterventionSnippet.objects.all(), empty_label=None, required=False)


class ScenarioBaseInterventionForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput())
    disp_name = forms.CharField(widget=forms.HiddenInput(), required=False)


class ScenarioHumanInterventionForm(ScenarioBaseInterventionForm):
    id = forms.CharField(widget=forms.HiddenInput())


class ScenarioGviInterventionForm(ScenarioHumanInterventionForm):
    def __init__(self, *args, **kwargs):
        component = None
        vectors = []

        if 'component' in kwargs:
            component = kwargs.pop('component')

        if 'vectors_iterator' in kwargs:
            try:
                vectors = kwargs.pop('vectors_iterator').next()
            except StopIteration:
                pass
        elif 'vectors' in kwargs:
            vectors = kwargs.pop('vectors')

        super(ScenarioGviInterventionForm, self).__init__(*args, **kwargs)

        self.fields['vector___inner-prefix___mosquito'] = forms.CharField(
            widget=forms.HiddenInput(),
            required=False
        )
        self.fields['vector___inner-prefix___propActive'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control vector-prop-active'}),
            required=False,
            label="Proportion of bites for which IRS acts"
        )
        self.fields['vector___inner-prefix___deterrency'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control vector-deterrency'}),
            required=False,
            label="Relative attractiveness"
        )
        self.fields['vector___inner-prefix___preprandialKillingEffect'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control vector-preprandial-killing-effect'}),
            required=False,
            label="Pre-prandial killing effect"
        )
        self.fields['vector___inner-prefix___postprandialKillingEffect'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control vector-postprandial-killing-effect'}),
            required=False,
            label="Post-prandial killing effect"
        )

        for index, vector in enumerate(vectors):
            self.fields['vector_%s_mosquito' % index] = forms.CharField(
                widget=forms.HiddenInput(),
                initial=vector['mosquito'],
                required=False
            )
            self.fields['vector_%s_propActive' % index] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control vector-prop-active'}),
                initial=vector['propActive'],
                required=False,
                label="Proportion of bites for which IRS acts"
            )
            self.fields['vector_%s_deterrency' % index] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control vector-deterrency'}),
                initial=vector['deterrency'],
                required=False,
                label="Relative attractiveness"
            )
            self.fields['vector_%s_preprandialKillingEffect' % index] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control vector-preprandial-killing-effect'}),
                initial=vector['preprandialKillingEffect'],
                required=False,
                label="Pre-prandial killing effect"
            )
            self.fields['vector_%s_postprandialKillingEffect' % index] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control vector-postprandial-killing-effect'}),
                initial=vector['postprandialKillingEffect'],
                required=False,
                label="Post-prandial killing effect"
            )

        if component is not None:
            self.fields['attrition'].initial = component.decay.L
            self.fields['vector___inner-prefix___mosquito'].initial = component.anophelesParams[0].mosquito
            self.fields['vector___inner-prefix___propActive'].initial = component.anophelesParams[0].propActive
            self.fields['vector___inner-prefix___deterrency'].initial = component.anophelesParams[0].deterrency
            self.fields['vector___inner-prefix___preprandialKillingEffect'].initial = \
                component.anophelesParams[0].preprandialKillingEffect
            self.fields['vector___inner-prefix___postprandialKillingEffect'].initial = \
                component.anophelesParams[0].postprandialKillingEffect

    attrition = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Decay", initial=0.0)


class ScenarioLarvicidingInterventionForm(ScenarioBaseInterventionForm):
    def __init__(self, *args, **kwargs):
        intervention = None
        vectors = []

        if 'intervention' in kwargs:
            intervention = kwargs.pop('intervention')

        if 'vectors_iterator' in kwargs:
            try:
                vectors = kwargs.pop('vectors_iterator').next()
            except StopIteration:
                pass
        elif 'vectors' in kwargs:
            vectors = kwargs.pop('vectors')

        super(ScenarioLarvicidingInterventionForm, self).__init__(*args, **kwargs)

        self.fields['vector___inner-prefix___mosquito'] = forms.CharField(
            widget=forms.HiddenInput(),
            required=False
        )
        self.fields['vector___inner-prefix___seekingDeathRateIncrease'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            label="Proportional increase in deaths while host searching",
        )
        self.fields['vector___inner-prefix___probDeathOvipositing'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            label="Proportion ovipositing mosquitoes killed"
        )
        self.fields['vector___inner-prefix___emergenceReduction'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            label="Proportion of emerging pupa killed"
        )

        for index, vector in enumerate(vectors):
            self.fields['vector_%s_mosquito' % index] = forms.CharField(
                widget=forms.HiddenInput(),
                initial=vector['mosquito'],
                required=False
            )
            self.fields['vector_%s_seekingDeathRateIncrease' % index] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                initial=vector['seekingDeathRateIncrease'],
                required=False,
                label="Proportional increase in deaths while host searching",
            )
            self.fields['vector_%s_probDeathOvipositing' % index] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                initial=vector['probDeathOvipositing'],
                required=False,
                label="Proportion ovipositing mosquitoes killed"
            )
            self.fields['vector_%s_emergenceReduction' % index] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                initial=vector['emergenceReduction'],
                required=False,
                label="Proportion of emerging pupa killed"
            )

        if intervention is not None:
            emergence_reduction = intervention.anopheles[0].emergenceReduction
            if emergence_reduction is not None:
                self.fields['emergence_reduction'].initial = emergence_reduction
                self.fields['vector___inner-prefix___emergenceReduction'].initial = emergence_reduction
            else:
                self.fields['emergence_reduction'].initial = 0.0
                self.fields['vector___inner-prefix___emergenceReduction'].initial = 0.0

            self.fields['vector___inner-prefix___mosquito'].initial = intervention.anopheles[0].mosquito

            if intervention.anopheles[0].seekingDeathRateIncrease is not None:
                self.fields['vector___inner-prefix___seekingDeathRateIncrease'].initial = \
                    intervention.anopheles[0].seekingDeathRateIncrease
            else:
                self.fields['vector___inner-prefix___seekingDeathRateIncrease'].initial = 0.0

            if intervention.anopheles[0].probDeathOvipositing is not None:
                self.fields['vector___inner-prefix___probDeathOvipositing'].initial = \
                    intervention.anopheles[0].probDeathOvipositing
            else:
                self.fields['vector___inner-prefix___probDeathOvipositing'].initial = 0.0

    emergence_reduction = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                          label="Initial proportion for emergence reduction", initial=0.0)
    deploy = forms.BooleanField(required=False)
    timesteps = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Timesteps",
                                required=False)


class ScenarioMdaInterventionForm(ScenarioHumanInterventionForm):
    def __init__(self, *args, **kwargs):
        options = []

        if 'options_iterator' in kwargs:
            try:
                options = kwargs.pop('options_iterator').next()
            except StopIteration:
                pass
        elif 'options' in kwargs:
            options = kwargs.pop('options')

        super(ScenarioMdaInterventionForm, self).__init__(*args, **kwargs)

        self.fields['option___inner-prefix___name'] = forms.CharField(
            widget=forms.HiddenInput(),
            required=False
        )
        self.fields['option___inner-prefix___pSelection'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            label="Probability of selection"
        )
        self.fields['option___inner-prefix___deploy___inner-option-prefix___maxAge'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            label="Maximum age of eligible humans"
        )
        self.fields['option___inner-prefix___deploy___inner-option-prefix___minAge'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            label="Minimum age of eligible humans"
        )
        self.fields['option___inner-prefix___deploy___inner-option-prefix___p'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            label="Probability of delivery to eligible humans"
        )
        self.fields['option___inner-prefix___deploy___inner-option-prefix___components'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            label="Components deployed to eligible humans"
        )
        self.fields['option___inner-prefix___clearInfection___inner-option-prefix___stage'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            label="Target stage"
        )
        self.fields['option___inner-prefix___clearInfection___inner-option-prefix___timesteps'] = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            required=False,
            label="Length of effect"
        )

        for index, option in enumerate(options):
            self.fields['option_%s_name' % index] = forms.CharField(
                widget=forms.HiddenInput(),
                initial=option['name'],
                required=False
            )
            self.fields['option_%s_pSelection' % index] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                initial=option['pSelection'],
                required=False,
                label="Probability of selection"
            )

            if "deploys" in option:
                for inner_index, deploy in option['deploys']:
                    self.fields['option_%s_deploy_%s_maxAge' % (index, inner_index)] = forms.CharField(
                        widget=forms.TextInput(attrs={'class': 'form-control'}),
                        initial=deploy.maxAge,
                        required=False,
                        label="Maximum age of eligible humans"
                    )
                    self.fields['option_%s_deploy_%s_minAge' % (index, inner_index)] = forms.CharField(
                        widget=forms.TextInput(attrs={'class': 'form-control'}),
                        initial=deploy.minAge,
                        required=False,
                        label="Minimum age of eligible humans"
                    )
                    self.fields['option_%s_deploy_%s_p' % (index, inner_index)] = forms.CharField(
                        widget=forms.TextInput(attrs={'class': 'form-control'}),
                        initial=deploy.p,
                        required=False,
                        label="Probability of delivery to eligible humans"
                    )
                    self.fields['option_%s_deploy_%s_components' % (index, inner_index)] = forms.CharField(
                        widget=forms.TextInput(attrs={'class': 'form-control'}),
                        initial=deploy.components,
                        required=False,
                        label="Components deployed to eligible humans"
                    )

            if "clearInfections" in option:
                for inner_index, clear_infection in enumerate(option['clearInfections']):
                    self.fields['option_%s_clearInfection_%s_stage' % (index, inner_index)] = \
                        forms.CharField(
                            widget=forms.TextInput(attrs={'class': 'form-control'}),
                            initial=clear_infection['stage'],
                            required=False,
                            label="Target stage"
                        )
                    self.fields['option_%s_clearInfection_%s_timesteps' % (index, inner_index)] = \
                        forms.CharField(
                            widget=forms.TextInput(attrs={'class': 'form-control'}),
                            initial=clear_infection['timesteps'],
                            required=False,
                            label="Length of effect"
                        )


class ScenarioVaccineInterventionForm(ScenarioHumanInterventionForm):
    attrition = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Decay", initial=0.0)
    efficacy_b = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 label="Measure of variation in vaccine efficacy", initial=0.0)
    initial_efficacy = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                                       label="Mean efficacy values before decay", initial=0.0)


class ScenarioImportedInfectionsForm(forms.Form):
    period = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),
                             label="Period of repetition", initial=0)
    timesteps = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), initial=0)
    values = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), initial=0)
    name = forms.CharField(widget=forms.HiddenInput(), required=False)


class ScenarioDeploymentsForm(forms.Form):
    pass


class ScenarioDeploymentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        components = []

        if 'components' in kwargs:
            components = kwargs.pop('components')

        super(ScenarioDeploymentForm, self).__init__(*args, **kwargs)

        if len(components) > 0:
            self.fields['components'] = forms.MultipleChoiceField(widget=forms.SelectMultiple({'size': '8'}),
                                                                  choices=components, initial=components[0])
        else:
            self.fields['components'] = forms.MultipleChoiceField(widget=forms.SelectMultiple({'size': '8'}))

    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Description of deployment'}), required=False)
    timesteps = forms.CharField(initial=0)
    coverages = forms.CharField(widget=forms.TextInput(attrs={'class': 'coverages'}), initial=0.0)

    def clean_coverages(self):
        coverages = self.cleaned_data["coverages"]

        for coverage_string in coverages.split(','):
            coverage = float(coverage_string)
            if float(coverage) < 0.0 or float(coverage) > 1.0:
                raise forms.ValidationError("Coverages must be specified as comma-separated values "
                                            "in the range [0.0, 1.0].")

        return coverages