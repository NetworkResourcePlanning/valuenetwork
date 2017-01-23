import sys
import datetime
from decimal import *
from collections import OrderedDict

import bleach
from captcha.fields import CaptchaField

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from valuenetwork.valueaccounting.models import *
from work.models import *
from valuenetwork.valueaccounting.forms import *


class ProjectAgentCreateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'required-field input-xlarge',}))
    nick = forms.CharField(
        label="ID",
        help_text="Must be unique, and no more than 32 characters",
        widget=forms.TextInput(attrs={'class': 'nick required-field',}))
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'class': 'email input-xxlarge',}))
    #address = forms.CharField(
    #    required=False,
    #    label="Work location",
    #    help_text="Enter address for a new work location. Otherwise, select existing location on map.",
    #    widget=forms.TextInput(attrs={'class': 'input-xxlarge',}))
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'input-xxlarge',}))
    agent_type = forms.ModelChoiceField(
        queryset=AgentType.objects.all(),
        empty_label=None,
        widget=forms.Select(
        attrs={'class': 'chzn-select'}))
    #is_context = forms.BooleanField(
    #    required=False,
    #    label="Is a context agent",
    #    widget=forms.CheckboxInput())
    password = forms.CharField(label=_("Password"),
        help_text=_("Login password"),
        widget=forms.PasswordInput(attrs={'class': 'password',}))

    class Meta:
        model = EconomicAgent
        #removed address and is_context
        fields = ('name', 'nick', 'agent_type', 'description', 'url', 'email')


class UploadAgentForm(forms.ModelForm):
    photo_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))

    class Meta:
        model = EconomicAgent
        fields = ('photo', 'photo_url')


class SkillSuggestionForm(forms.ModelForm):
    skill = forms.CharField(
        label = "Other",
        help_text = _("Your skill suggestions will be sent to Freedom Coop Admins"),
        )

    class Meta:
        model = SkillSuggestion
        fields = ('skill',)


class MembershipRequestForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = MembershipRequest
        exclude = ('agent',)

    def clean(self):
        #import pdb; pdb.set_trace()
        data = super(MembershipRequestForm, self).clean()
        type_of_membership = data["type_of_membership"]
        number_of_shares = data["number_of_shares"]
        if type_of_membership == "collective":
            if int(number_of_shares) < 2:
                msg = "Number of shares must be at least 2 for a collective."
                self.add_error('number_of_shares', msg)

    def _clean_fields(self):
        super(MembershipRequestForm, self)._clean_fields()
        for name, value in self.cleaned_data.items():
            self.cleaned_data[name] = bleach.clean(value)


class WorkProjectSelectionFormOptional(forms.Form):
    context_agent = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))

    def __init__(self, context_agents, *args, **kwargs):
        super(WorkProjectSelectionFormOptional, self).__init__(*args, **kwargs)
        self.fields["context_agent"].choices = [('', '--All My Projects--')] + [(proj.id, proj.name) for proj in context_agents]

class WorkTodoForm(forms.ModelForm):
    from_agent = forms.ModelChoiceField(
        required=False,
        #queryset=EconomicAgent.objects.individuals(),
        queryset=EconomicAgent.objects.with_user(),
        label="Assigned to",
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.filter(behavior="work"),
        label="Type of work",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.context_agents(),
        label=_("Context"),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    due_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'todo-description input-xlarge',}))
    url = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': 'url input-xlarge',}))

    class Meta:
        model = Commitment
        fields = ('from_agent', 'context_agent', 'resource_type', 'due_date', 'description', 'url')

    def __init__(self, agent, pattern=None, *args, **kwargs): #agent is posting agent
        super(WorkTodoForm, self).__init__(*args, **kwargs)
        contexts = agent.related_contexts()
        self.fields["context_agent"].choices = list(set([(ct.id, ct) for ct in contexts]))
        peeps = [agent,]
        from_agent_choices = [('', 'Unassigned'), (agent.id, agent),]
        #import pdb; pdb.set_trace()
        for context in contexts:
            if agent.is_manager_of(context):
                peeps.extend(context.task_assignment_candidates())
        if len(peeps) > 1:
            peeps = list(OrderedDict.fromkeys(peeps))
        from_agent_choices = [('', 'Unassigned')] + [(peep.id, peep) for peep in peeps]

        self.fields["from_agent"].choices = from_agent_choices
        #import pdb; pdb.set_trace()
        if pattern:
            self.pattern = pattern
            #self.fields["resource_type"].choices = [(rt.id, rt) for rt in pattern.todo_resource_types()]
            self.fields["resource_type"].queryset = pattern.todo_resource_types()


class ProjectCreateForm(AgentCreateForm):
    # override fields for EconomicAgent model
    agent_type = forms.ModelChoiceField(
        queryset=AgentType.objects.filter(is_context=True),
        empty_label=None,
        widget=forms.Select(
        attrs={'class': 'chzn-select'}))

    is_context = None # projects are always context_agents, hide the field

    # fields for Project model
    joining_style = forms.ChoiceField()
    visibility = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(ProjectCreateForm, self).__init__(*args, **kwargs)
        self.fields["joining_style"].choices = [(js[0], js[1]) for js in JOINING_STYLE_CHOICES]
        self.fields["visibility"].choices = [(vi[0], vi[1]) for vi in VISIBILITY_CHOICES]

    def clean(self):
        #import pdb; pdb.set_trace()
        data = super(ProjectCreateForm, self).clean()
        url = data["url"]
        if not url[0:3] == "http":
          data["url"] = "http://" + url
        #if type_of_user == "collective":
            #if int(number_of_shares) < 2:
            #    msg = "Number of shares must be at least 2 for a collective."
            #    self.add_error('number_of_shares', msg)

    def _clean_fields(self):
        super(ProjectCreateForm, self)._clean_fields()
        for name, value in self.cleaned_data.items():
            self.cleaned_data[name] = bleach.clean(value)

    class Meta: #(AgentCreateForm.Meta):
        model = Project #EconomicAgent
        #removed address and is_context
        fields = ('name', 'nick', 'agent_type', 'description', 'url', 'email', 'joining_style', 'visibility', 'fobi_slug')
        #exclude = ('is_context',)


class WorkAgentCreateForm(AgentCreateForm):
    # override fields for EconomicAgent model
    agent_type = forms.ModelChoiceField(
        queryset=AgentType.objects.all(), #filter(is_context=True),
        empty_label=None,
        widget=forms.Select(
        attrs={'class': 'chzn-select'}))

    is_context = None # projects are always context_agents, hide the field
    nick = None
    # fields for Project model
    #joining_style = forms.ChoiceField()
    #visibility = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(WorkAgentCreateForm, self).__init__(*args, **kwargs)
        #self.fields["joining_style"].choices = [(js[0], js[1]) for js in JOINING_STYLE_CHOICES]
        #self.fields["visibility"].choices = [(vi[0], vi[1]) for vi in VISIBILITY_CHOICES]


    class Meta: #(AgentCreateForm.Meta):
        model = EconomicAgent
        #removed address and is_context
        fields = ('name', 'agent_type', 'description', 'url', 'email', 'address', 'phone_primary',)
        #exclude = ('is_context',)


class WorkCasualTimeContributionForm(forms.ModelForm):
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.filter(behavior="work"),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    context_agent = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.open_projects(),
        label=_("Context"),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'chzn-select'}))
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'item-date date-entry',}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'item-description',}))
    url = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': 'url',}))
    quantity = forms.DecimalField(required=False,
        widget=DecimalDurationWidget,
        help_text="hrs, mins")

    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'resource_type', 'context_agent', 'quantity', 'is_contribution', 'url', 'description')


# public join form
class JoinRequestForm(forms.ModelForm):
    captcha = CaptchaField()

    project = None
    '''forms.ModelChoiceField(
        queryset=Project.objects.filter(joining_style='moderated', visibility='public'),
        empty_label=None,
        widget=forms.Select(
        attrs={'class': 'chzn-select'}))'''

    class Meta:
        model = JoinRequest
        exclude = ('agent', 'project', 'fobi_data',)

    def clean(self):
        #import pdb; pdb.set_trace()
        data = super(JoinRequestForm, self).clean()
        type_of_user = data["type_of_user"]
        #number_of_shares = data["number_of_shares"]
        #if type_of_user == "collective":
            #if int(number_of_shares) < 2:
            #    msg = "Number of shares must be at least 2 for a collective."
            #    self.add_error('number_of_shares', msg)

    def _clean_fields(self):
        super(JoinRequestForm, self)._clean_fields()
        for name, value in self.cleaned_data.items():
            self.cleaned_data[name] = bleach.clean(value)


class JoinRequestInternalForm(forms.ModelForm):
    captcha = None #CaptchaField()

    project = None
    '''forms.ModelChoiceField(
        queryset=Project.objects.filter(joining_style='moderated', visibility='public'),
        empty_label=None,
        widget=forms.Select(
        attrs={'class': 'chzn-select'}))'''

    class Meta:
        model = JoinRequest
        exclude = ('agent', 'project', 'fobi_data', 'type_of_user', 'name', 'surname', 'requested_username', 'email_address', 'phone_number', 'address',)

    def clean(self):
        #import pdb; pdb.set_trace()
        data = super(JoinRequestInternalForm, self).clean()
        #type_of_user = data["type_of_user"]
        #number_of_shares = data["number_of_shares"]
        #if type_of_user == "collective":
            #if int(number_of_shares) < 2:
            #    msg = "Number of shares must be at least 2 for a collective."
            #    self.add_error('number_of_shares', msg)

    def _clean_fields(self):
        super(JoinRequestInternalForm, self)._clean_fields()
        for name, value in self.cleaned_data.items():
            self.cleaned_data[name] = bleach.clean(value)


class JoinAgentSelectionForm(forms.Form):
    created_agent = AgentModelChoiceField(
        queryset=EconomicAgent.objects.without_join_request(),
        required=False)


class ProjectSelectionFilteredForm(forms.Form):
    context_agent = forms.ChoiceField()

    def __init__(self, agent, *args, **kwargs):
        super(ProjectSelectionFilteredForm, self).__init__(*args, **kwargs)
        projects = agent.managed_projects()
        if projects:
            self.fields["context_agent"].choices = [(proj.id, proj.name) for proj in projects]


class OrderSelectionFilteredForm(forms.Form):
    demand = forms.ModelChoiceField(
        queryset=Order.objects.exclude(order_type="holder"),
        label="Add to an existing order (optional)",
        required=False)

    def __init__(self, provider=None, *args, **kwargs):
        super(OrderSelectionFilteredForm, self).__init__(*args, **kwargs)
        if provider:
            self.fields["demand"].queryset = provider.sales_orders.all()



from general.models import Record_Type
from mptt.forms import TreeNodeChoiceField

class ExchangeNavForm(forms.Form):
    #get_et = False
    used_exchange_type = forms.ModelChoiceField(
          queryset=ExchangeType.objects.none(),  #ExchangeType.objects.all(),
          empty_label='. . .',
          #level_indicator='. ',
          required=False,
          widget=forms.Select(
              attrs={'class': 'exchange-selector chzn-select'}
          )
    )
    exchange_type = TreeNodeChoiceField( #forms.ModelChoiceField(
          queryset=Ocp_Record_Type.objects.none(),  #ExchangeType.objects.all(),
          empty_label=None, #'. . .',
          level_indicator='. ',
          required=False,
          widget=forms.Select(
              attrs={'class': 'chzn-select',
                     'multiple':'',
                     'data-placeholder':_("search Exchange type...")}
          )
    )

    resource_type = TreeNodeChoiceField(
        queryset=Ocp_Artwork_Type.objects.all(),
        empty_label=None,
        level_indicator='. ',
        required=False,
        widget=forms.Select(
          attrs={'class': 'chzn-select',
                     'multiple':'',
                     'data-placeholder':_("search Resource type...")}
        )
    )
    skill_type = TreeNodeChoiceField(
        queryset=Ocp_Skill_Type.objects.all(),
        empty_label=None,
        level_indicator='. ',
        required=False,
        widget=forms.Select(
          attrs={'class': 'chzn-select',
                     'multiple':'',
                     'data-placeholder':_("search Skill type...")}
        )
    )

    def __init__(self, agent=None, *args, **kwargs):
        super(ExchangeNavForm, self).__init__(*args, **kwargs)
        try:
            gen_et = Ocp_Record_Type.objects.get(clas='ocp_exchange')
            if agent:
                context_ids = [c.id for c in agent.related_all_agents()]
                if not agent.id in context_ids:
                    context_ids.append(agent.id)
                if gen_et:
                    self.fields["exchange_type"].label = 'Contexts: '+str(agent.related_all_agents())
                    self.fields["exchange_type"].queryset = Ocp_Record_Type.objects.filter(lft__gt=gen_et.lft, rght__lt=gen_et.rght, tree_id=gen_et.tree_id).exclude( Q(exchange_type__isnull=False), ~Q(exchange_type__context_agent__id__in=context_ids) )

                    self.fields["resource_type"].queryset = Ocp_Artwork_Type.objects.all().exclude( Q(resource_type__isnull=False), Q(resource_type__context_agent__isnull=False), ~Q(resource_type__context_agent__id__in=context_ids) ) #| Q(resource_type__context_agent__isnull=True) )
                    self.fields["skill_type"].queryset = Ocp_Skill_Type.objects.all().exclude( Q(resource_type__isnull=False), Q(resource_type__context_agent__isnull=False), ~Q(resource_type__context_agent__id__in=context_ids) ) #| Q(resource_type__context_agent__isnull=True) )

                exchanges = Exchange.objects.filter(context_agent=agent)
                ex_types = [ex.exchange_type.id for ex in exchanges]
                self.fields["used_exchange_type"].queryset = ExchangeType.objects.filter(id__in=ex_types)

        except:
            #pass
            self.fields["exchange_type"].label = 'ERROR! contexts: '+str(agent.related_all_agents())
            self.fields["exchange_type"].queryset = Ocp_Record_Type.objects.none() #all()


class ExchangeContextForm(forms.ModelForm):
    start_date = forms.DateField(required=True,
        label=_("Date"),
        widget=forms.TextInput(attrs={'class': 'item-date date-entry',}))
    notes = forms.CharField(required=False,
        label=_("Comments"),
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    url = forms.CharField(required=False,
        label=_("Link to receipt(s)"),
        widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}))

    class Meta:
        model = Exchange
        fields = ('start_date', 'url', 'notes')


class InvoiceNumberForm(forms.ModelForm):
    member = forms.ModelChoiceField(
        queryset=EconomicAgent.objects.none(),
        label=_("for Freedom Coop Member:"),
        empty_label=None,
        )

    class Meta:
        model = InvoiceNumber
        fields = ('member', 'description', )

    def __init__(self, agent, *args, **kwargs):
        super(InvoiceNumberForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        self.fields["member"].queryset = agent.invoicing_candidates()


class WorkEventContextAgentForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    resource_type = WorkModelChoiceField(
        queryset=EconomicResourceType.objects.filter(behavior="work"),
        label="Type of work done",
        #empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    quantity = forms.DecimalField(required=True,
        label="Hours, up to 2 decimal places",
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    from_agent = forms.ModelChoiceField(
        required=True,
        queryset=EconomicAgent.objects.all(),
        label="Work done by",
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    is_contribution = forms.BooleanField(
        required=False,
        initial=True,
        label="Can be used in a value equation",
        widget=forms.CheckboxInput())

    class Meta:
        model = EconomicEvent
        fields = ('event_date', 'resource_type','quantity', 'description', 'from_agent', 'is_contribution')

    def __init__(self, context_agent=None, *args, **kwargs):
        super(WorkEventContextAgentForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if context_agent:
            self.context_agent = context_agent
            self.fields["from_agent"].queryset = context_agent.related_all_agents_queryset()


from general.models import Material_Type, Nonmaterial_Type, Artwork_Type
from work.utils import *

class ContextTransferForm(forms.Form):
    event_date = forms.DateField(required=True,
        widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    to_agent = forms.ModelChoiceField(
        required=False,
        queryset=EconomicAgent.objects.all(),
        label="Transferred to",
        empty_label=_('. . .'), #None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    from_agent = forms.ModelChoiceField(
        required=False,
        queryset=EconomicAgent.objects.all(),
        label="Transferred from",
        empty_label=_('. . .'), #None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    quantity = forms.DecimalField(
        label="Quantity transferred",
        initial=1,
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))

    ocp_resource_type = TreeNodeChoiceField( #forms.ModelChoiceField(
        queryset=Ocp_Artwork_Type.objects.none(), #filter(lft__gt=gen_et.lft, rght__lt=gen_et.rght, tree_id=gen_et.tree_id),
        empty_label=_('. . .'),
        level_indicator='. ',
        widget=forms.Select(
            attrs={'class': 'ocp-resource-type-for-resource input-xlarge chzn-select'})
    )

    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.all(),
        label="Facets:",
        #empty_label=None,
        required=False,
        widget=forms.Select(
            attrs={'class': 'resource-type-for-resource chzn-select'})
    )

    resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.none(),
        label="Resource transferred (optional if not inventoried)",
        required=False,
        empty_label=_('. . .'),
        widget=forms.Select(attrs={'class': 'resource input-xlarge chzn-select',}))
    from_resource = ResourceModelChoiceField(
        queryset=EconomicResource.objects.none(),
        label="Resource transferred from (optional if not inventoried)",
        required=False,
        empty_label=_('. . .'),
        widget=forms.Select(attrs={'class': 'resource input-xlarge chzn-select',}))
    value = forms.DecimalField(
        label="Value (total, not per unit)",
        initial=0,
        required=False,
        widget=forms.TextInput(attrs={'class': 'quantity value input-small',}))
    unit_of_value = forms.ModelChoiceField(
        empty_label=_('. . .'), #None,
        required=False,
        queryset=Unit.objects.filter(unit_type='value'),
        widget=forms.Select(attrs={'class': 'chzn-select',}))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    is_contribution = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput())
    is_to_distribute = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput())
    event_reference = forms.CharField(
        required=False,
        label="Reference",
        widget=forms.TextInput(attrs={'class': 'input-xlarge',}))
    identifier = forms.CharField(
        required=False,
        label="<b>Create the resource:</b><br><br>Identifier",
        help_text="For example, lot number or serial number.",
        widget=forms.TextInput(attrs={'class': 'item-name',}))
    url = forms.URLField(
        required=False,
        label="URL",
        widget=forms.TextInput(attrs={'class': 'url input-xlarge',}))
    photo_url = forms.URLField(
        required=False,
        label="Photo URL",
        widget=forms.TextInput(attrs={'class': 'url input-xlarge',}))
    current_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        empty_label=_('. . .'),
        label=_("Current Resource Location"),
        widget=forms.Select(attrs={'class': 'input-medium chzn-select',}))
    notes = forms.CharField(
        required=False,
        label="Resource Notes",
        widget=forms.Textarea(attrs={'class': 'item-description',}))
    access_rules = forms.CharField(
        required=False,
        label="Resource Access Rules",
        widget=forms.Textarea(attrs={'class': 'item-description',}))


    def __init__(self, transfer_type=None, context_agent=None, resource_type=None, ocp_resource_type=None, posting=False, *args, **kwargs):
        super(ContextTransferForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()

        if transfer_type:
            rts = transfer_type.get_resource_types()
            if resource_type:
              self.fields["resource_type"].queryset = EconomicResourceType.objects.filter(id=resource_type.id)
            else:
              self.fields["resource_type"].queryset = rts
            if posting:
                self.fields["resource"].queryset = EconomicResource.objects.all()
                self.fields["from_resource"].queryset = EconomicResource.objects.all()
            else:
                if rts:
                    if resource_type:
                        self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=resource_type)
                        self.fields["from_resource"].queryset = EconomicResource.objects.filter(resource_type=resource_type)
                    else:
                        self.fields["resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])
                        self.fields["from_resource"].queryset = EconomicResource.objects.filter(resource_type=rts[0])
            if context_agent:
                self.fields["to_agent"].queryset = transfer_type.to_context_agents(context_agent)
                self.fields["from_agent"].queryset = transfer_type.from_context_agents(context_agent)

            facetvalues = [ttfv.facet_value.value for ttfv in transfer_type.facet_values.all()]
            self.fields["ocp_resource_type"].label = "(Facets: "+', '.join(facetvalues)+")"

            #self.fields["ocp_resource_type"].label += init_resource_types()

            for fv in facetvalues:
                #self.fields["ocp_resource_type"].label += " FV:"+fv
                try:
                    gtyp = Ocp_Artwork_Type.objects.get(facet_value__value=fv)
                    self.fields["ocp_resource_type"].label += " R:"+str(gtyp.name)
                except:
                    pass
                #self.fields["ocp_resource_type"].label += " FV:"+fv

                try:
                    gtyp = Ocp_Skill_Type.objects.get(facet_value__value=fv)
                    self.fields["ocp_resource_type"].label += " S:"+str(gtyp.name)
                except:
                    pass


            for facet in transfer_type.facets():
                if facet.clas == "Material_Type":
                    #gen_mts = Material_Type.objects.all()
                    #ocp_mts =  Ocp_Material_Type.objects.all()
                    #if not gen_mts.count() == ocp_mts.count():
                    #  self.fields["ocp_resource_type"].label += " !Needs Update! (ocpMT:"+str(ocp_mts.count())+" gen:"+str(gen_mts.count())+")"
                    #  update = update_from_general(facet.clas)
                    #  self.fields["ocp_resource_type"].label += "UPDATE: "+str(update)

                    if resource_type:
                       try:
                          self.fields["ocp_resource_type"].initial = Ocp_Artwork_Type.objects.get(resource_type=resource_type)
                       except:
                          self.fields["ocp_resource_type"].label += " INITIAL? "+str(self.fields["ocp_resource_type"].initial)


                elif facet.clas == "Nonmaterial_Type":
                    #gen_nts = Nonmaterial_Type.objects.all()
                    #ocp_nts =  Ocp_Nonmaterial_Type.objects.all()
                    #if not gen_nts.count() == ocp_nts.count():
                    #   self.fields["ocp_resource_type"].label += " !Needs Update! (ocpMT:"+str(ocp_nts.count())+" gen:"+str(gen_nts.count())+")"
                    #   update = update_from_general(facet.clas)
                    #   self.fields["ocp_resource_type"].label += " UPDATE: "+str(update)

                    if resource_type:
                       try:
                          self.fields["ocp_resource_type"].initial = Ocp_Artwork_Type.objects.get(resource_type=resource_type)
                       except:
                          self.fields["ocp_resource_type"].label += " INITIAL? "+str(self.fields["ocp_resource_type"].initial)

                elif facet.clas == "Skill_Type":
                    #gen_sts = Job.objects.all()
                    #ocp_sts =  Ocp_Skill_Type.objects.all()
                    #if not gen_sts.count() == ocp_sts.count():
                    #   self.fields["ocp_resource_type"].label += " !Needs Update! (ocpST:"+str(ocp_sts.count())+" gen:"+str(gen_sts.count())+")"
                    #   update = update_from_general(facet.clas)
                    #   self.fields["ocp_resource_type"].label += " UPDATE: "+str(update)

                    if resource_type:
                       try:
                          self.fields["ocp_resource_type"].initial = Ocp_Skill_Type.objects.get(resource_type=resource_type)
                       except:
                          self.fields["ocp_resource_type"].label += " INITIAL? "+str(self.fields["ocp_resource_type"].initial)

                else:
                  pass

            try:
              self.fields["ocp_resource_type"].queryset = transfer_type.exchange_type.ocp_record_type.get_ocp_resource_types(transfer_type=transfer_type)
            except:
              self.fields["ocp_resource_type"].label = "  Sorry, this exchange type is not yet related to any resource types..."

        else: # no transfer type, rise error TODO
          pass

    def clean(self):
        data = super(ContextTransferForm, self).clean()
        ocp_rt = data["ocp_resource_type"]
        ini_rt = data["resource_type"]
        if ocp_rt:
          if not ini_rt:
            rt = get_rt_from_ocp_rt(ocp_rt)
            if rt:
              data["resource_type"] = rt
            else:
              self.add_error('ocp_resource_type', "This type is too general, try a more specific")
        else:
          self.add_error('ocp_resource_type', "There is a problem with this ocp_resource_type!")
        return data



class ContextTransferCommitmentForm(forms.Form):
    commitment_date = forms.DateField(required=True,
        widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    due_date = forms.DateField(required=True,
        widget=forms.TextInput(attrs={'class': 'input-small date-entry',}))
    to_agent = forms.ModelChoiceField(
        required=False,
        queryset=EconomicAgent.objects.all(),
        label="Transfer to",
        empty_label=_('. . .'),
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    from_agent = forms.ModelChoiceField(
        required=False,
        queryset=EconomicAgent.objects.all(),
        label="Transfer from",
        empty_label=_('. . .'),
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    quantity = forms.DecimalField(
        label="Quantity",
        initial=1,
        widget=forms.TextInput(attrs={'class': 'quantity input-small',}))

    ocp_resource_type = TreeNodeChoiceField( #forms.ModelChoiceField(
        queryset=Ocp_Artwork_Type.objects.none(), #filter(lft__gt=gen_et.lft, rght__lt=gen_et.rght, tree_id=gen_et.tree_id),
        empty_label=_('. . .'),
        level_indicator='. ',
        widget=forms.Select(
            attrs={'class': 'ocp-resource-type-for-resource input-xlarge chzn-select'})
    )

    resource_type = forms.ModelChoiceField(
        queryset=EconomicResourceType.objects.all(),
        empty_label=_('. . .'),
        required=False,
        widget=forms.Select(
            attrs={'class': 'resource-type-for-resource chzn-select'}))
    value = forms.DecimalField(
        label="Value (total, not per unit)",
        initial=0,
        required=False,
        widget=forms.TextInput(attrs={'class': 'value quantity input-small',}))
    unit_of_value = forms.ModelChoiceField(
        required=False,
        empty_label=_('. . .'),
        queryset=Unit.objects.filter(unit_type='value'),
        widget=forms.Select(
            attrs={'class': 'chzn-select'}))
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'item-description',}))

    def __init__(self, transfer_type=None, context_agent=None, resource_type=None, ocp_resource_type=None, posting=False, *args, **kwargs):
        super(ContextTransferCommitmentForm, self).__init__(*args, **kwargs)
        #import pdb; pdb.set_trace()
        if transfer_type:
            self.fields["resource_type"].queryset = transfer_type.get_resource_types()
            if context_agent:
                self.fields["to_agent"].queryset = transfer_type.to_context_agents(context_agent)
                self.fields["from_agent"].queryset = transfer_type.from_context_agents(context_agent)

            facetvalues = [ttfv.facet_value.value for ttfv in transfer_type.facet_values.all()]
            if facetvalues:
              self.fields["ocp_resource_type"].label = "(Facets: "+', '.join(facetvalues)+")"

            for facet in transfer_type.facets():
                if facet.clas == "Material_Type":
                    #gen_mts = Material_Type.objects.all()
                    #ocp_mts =  Ocp_Material_Type.objects.all()
                    #if not gen_mts.count() == ocp_mts.count():
                    #   self.fields["ocp_resource_type"].label += " !Needs Update! (ocpMT:"+str(ocp_mts.count())+" gen:"+str(gen_mts.count())+")"
                    #   update = update_from_general(facet.clas)
                    #   self.fields["ocp_resource_type"].label += "UPDATE: "+str(update)

                    if resource_type:
                       try:
                          self.fields["ocp_resource_type"].initial = Ocp_Artwork_Type.objects.get(resource_type=resource_type)
                       except:
                          self.fields["ocp_resource_type"].label += " INITIAL? "+str(self.fields["ocp_resource_type"].initial)
                    #else:
                       #self.fields["ocp_resource_type"].label += " FALTA RT! "+str(resource_type)

                elif facet.clas == "Nonmaterial_Type":
                    #gen_nts = Nonmaterial_Type.objects.all()
                    #ocp_nts =  Ocp_Nonmaterial_Type.objects.all()
                    #if not gen_nts.count() == ocp_nts.count():
                    #   self.fields["ocp_resource_type"].label += " !Needs Update! (ocpMT:"+str(ocp_nts.count())+" gen:"+str(gen_nts.count())+")"
                    #   update = update_from_general(facet.clas)
                    #   self.fields["ocp_resource_type"].label += " UPDATE: "+str(update)

                    if resource_type:
                       try:
                          self.fields["ocp_resource_type"].initial = Ocp_Artwork_Type.objects.get(resource_type=resource_type)
                       except:
                          self.fields["ocp_resource_type"].label += " INITIAL? "+str(self.fields["ocp_resource_type"].initial)
                    #else:
                       #self.fields["ocp_resource_type"].label += " FALTA RT! "+str(resource_type)
                else:
                  pass

            try:
              self.fields["ocp_resource_type"].queryset = transfer_type.exchange_type.ocp_record_type.get_ocp_resource_types(transfer_type=transfer_type)
            except:
              self.fields["ocp_resource_type"].label = "  Sorry, this exchange type is not yet related to any resource types..."

            #import pdb; pdb.set_trace()

    def clean(self):
        data = super(ContextTransferCommitmentForm, self).clean()
        ocp_rt = data["ocp_resource_type"]
        ini_rt = data["resource_type"]
        if ocp_rt:
          if not ini_rt:
            rt = get_rt_from_ocp_rt(ocp_rt)
            if rt:
              data["resource_type"] = rt
            else:
              self.add_error('ocp_resource_type', "This type is too general, try a more specific")
        else:
          self.add_error('ocp_resource_type', "There is a problem with this ocp_resource_type!")
        return data


class ResourceRoleContextAgentForm(forms.ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    role = forms.ModelChoiceField(
        queryset=AgentResourceRoleType.objects.all(),
        required=False,
        empty_label=_('. . .'),
        widget=forms.Select(
            attrs={'class': 'select-role chzn-select'}))
    agent = AgentModelChoiceField(
        queryset=EconomicAgent.objects.resource_role_agents(),
        required=False,
        empty_label=_('. . .'),
        widget=forms.Select(
            attrs={'class': 'select-agent chzn-select'}))
    is_contact = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput())

    class Meta:
        model = AgentResourceRole
        fields = ('id', 'role', 'agent', 'is_contact')

    def __init__(self, context_agent=None, *args, **kwargs):
        super(ResourceRoleContextAgentForm, self).__init__(*args, **kwargs)
        if context_agent:
          context_agents = context_agent.related_all_agents_queryset() # EconomicAgent.objects.context_agents() #
          self.fields["agent"].queryset = context_agents


class NewContextExchangeTypeForm(forms.Form):  # still not used !
    parent_exchange_type = TreeNodeChoiceField(
        queryset=Ocp_Record_Type.objects.all(),
        empty_label=None,
        level_indicator='. ',
        required=False,
        widget=forms.Select(
          attrs={'class': 'chzn-select',
                     'multiple':'',
                     'data-placeholder':_("search Exchange type...")}
        )
    )
    resource_type = TreeNodeChoiceField(
        queryset=Ocp_Artwork_Type.objects.all(),
        empty_label=None,
        level_indicator='. ',
        required=False,
        widget=forms.Select(
          attrs={'class': 'chzn-select',
                     'multiple':'',
                     'data-placeholder':_("search Resource type...")}
        )
    )
    skill_type = TreeNodeChoiceField(
        queryset=Ocp_Skill_Type.objects.all(),
        empty_label=None,
        level_indicator='. ',
        required=False,
        widget=forms.Select(
          attrs={'class': 'chzn-select',
                     'multiple':'',
                     'data-placeholder':_("search Skill type...")}
        )
    )

    '''
    use_case = forms.ModelChoiceField(
        queryset=UseCase.objects.exchange_use_cases(),
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'use-case chzn-select'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input-xlarge',})) # not required now, to be set in the next page
    '''

    class Meta:
        fields = ('resource_type', 'skill_type')

    def __init__(self, agent=None, *args, **kwargs):
        super(NewContextExchangeTypeForm, self).__init__(*args, **kwargs)
        try:
            gen_et = Ocp_Record_Type.objects.get(clas='ocp_exchange')
            if agent:
                context_ids = [c.id for c in agent.related_all_agents()]
                if not agent.id in context_ids:
                    context_ids.append(agent.id)
                if gen_et:
                    self.fields["parent_exchange_type"].label = 'Contexts: '+str(agent.related_all_agents())
                    self.fields["parent_exchange_type"].queryset = Ocp_Record_Type.objects.filter(lft__gt=gen_et.lft, rght__lt=gen_et.rght, tree_id=gen_et.tree_id).exclude( Q(exchange_type__isnull=False), ~Q(exchange_type__context_agent__id__in=context_ids) )

                    self.fields["resource_type"].queryset = Ocp_Artwork_Type.objects.all().exclude( Q(resource_type__isnull=False), ~Q(resource_type__context_agent__id__in=context_ids) | Q(resource_type__context_agent__isnull=True) )
                    self.fields["skill_type"].queryset = Ocp_Skill_Type.objects.all().exclude( Q(resource_type__isnull=False), ~Q(resource_type__context_agent__id__in=context_ids) | Q(resource_type__context_agent__isnull=True) )

                exchanges = Exchange.objects.filter(context_agent=agent)
                ex_types = [ex.exchange_type.id for ex in exchanges]
                #self.fields["used_exchange_type"].queryset = ExchangeType.objects.filter(id__in=ex_types)

        except:
            #pass
            self.fields["parent_exchange_type"].label = 'ERROR! contexts: '+str(agent.related_all_agents())
            self.fields["parent_exchange_type"].queryset = Ocp_Record_Type.objects.none() #all()


class NewResourceTypeForm(forms.Form):
    name = forms.CharField(
        label=_("Name of the new Resource Type"),
        widget=forms.TextInput(attrs={'class': 'unique-name input-xxlarge',}),
    )
    parent_type = TreeNodeChoiceField( #forms.ModelChoiceField(
        queryset=Ocp_Artwork_Type.objects.all(), #none(), #filter(lft__gt=gen_et.lft, rght__lt=gen_et.rght, tree_id=gen_et.tree_id),
        empty_label=_('. . .'),
        level_indicator='. ',
        label=_("Parent resource type"),
        widget=forms.Select(
            attrs={'class': 'ocp-resource-type input-xlarge chzn-select'}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'item-description input-xxlarge', 'rows': 5,})
    )
    context_agent = forms.ModelChoiceField(
        empty_label=None,
        queryset=EconomicAgent.objects.none(),
        help_text=_('If the resource type can be useful for other projects, choose a broader context here.'),
        widget=forms.Select(
            attrs={'class': 'chzn-select'}),
    )
    substitutable = forms.BooleanField(
        required=False,
        help_text=_('Check this if any resource of this type can be substituted for any other resource of this same type.'),
        widget=forms.CheckboxInput()
    )
    related_type = TreeNodeChoiceField( #forms.ModelChoiceField(
        queryset=Ocp_Artwork_Type.objects.all(), #none(), #filter(lft__gt=gen_et.lft, rght__lt=gen_et.rght, tree_id=gen_et.tree_id),
        empty_label=_('. . .'),
        level_indicator='. ',
        label=_("Main related resource type"),
        help_text=_('If this resource type is mainly related another resource type, choose it here.'),
        widget=forms.Select(
            attrs={'class': 'ocp-resource-type input-xlarge chzn-select'}),
    )
    parent = forms.ModelChoiceField(
        empty_label=_('. . .'),
        queryset=EconomicResourceType.objects.none(),
        label=_("Inherit a Recipe from another resource type"),
        help_text=_('If the resource type must inherit a Recipe from another resource type, choose it here.'),
        widget=forms.Select(
            attrs={'class': 'chzn-select'}),
    )
    url = forms.CharField(
        required=False,
        label=_("Any related URL for the type?"),
        widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}),
    )
    photo_url = forms.CharField(
        required=False,
        label=_("Photo URL of the resource type"),
        widget=forms.TextInput(attrs={'class': 'url input-xxlarge',}),
    )
    '''unit = forms.ModelChoiceField(
        empty_label=_('. . .'),
        queryset=Unit.objects.all(),
        widget=forms.Select(
            attrs={'class': 'chzn-select'}),
    )
    price_per_unit = forms.DecimalField(
        max_digits=8, decimal_places=2,
        widget=forms.TextInput(attrs={'value': '0.0', 'class': 'price'}),
        label=_("Price per unit (in Faircoin)"),
    )'''

    def __init__(self, agent=None, *args, **kwargs):
        super(NewResourceTypeForm, self).__init__(*args, **kwargs)
        self.fields["substitutable"].initial = settings.SUBSTITUTABLE_DEFAULT
        self.fields["parent"].queryset = possible_parent_resource_types()
        if agent:
            self.fields["context_agent"].queryset = agent.related_all_contexts_queryset(agent)
            self.fields["context_agent"].initial = agent



class AssociationForm(forms.Form):
    member = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'chzn-select input-xlarge'}))
    new_association_type = forms.ModelChoiceField(
        queryset=AgentAssociationType.objects.member_types(),
        label=_("Choose a new relationship"),
        empty_label=None,
        widget=forms.Select(
            attrs={'class': 'chzn-select'}),
    )

    def __init__(self, agent, *args, **kwargs):
        super(AssociationForm, self).__init__(*args, **kwargs)
        self.fields["member"].choices = [(assoc.id, assoc.is_associate.name + ' - ' + assoc.association_type.name) for assoc in agent.member_associations()]

