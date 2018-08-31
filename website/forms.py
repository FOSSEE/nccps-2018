from django import forms

from django.forms import ModelForm, widgets

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MinValueValidator, \
    RegexValidator, URLValidator
from captcha.fields import ReCaptchaField

from website.models import Proposal

MY_CHOICES = (
    ('Beginner', 'Beginner'),
    ('Advanced', 'Advanced'),
)

ws_duration = (
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
)
abs_duration = (
    ('15', '15'),
    ('30', '30'),
)


MY_CHOICES = (
    ('Beginner', 'Beginner'),
    ('Advanced', 'Advanced'),
)
rating = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
)

CHOICES = [('1', 'Yes'),
           ('0', 'No')]


# modal proposal form for cfp
class ProposalForm(forms.ModelForm):

    about_me = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'About Me'}),
                               required=True,
                               error_messages={
                                   'required': 'About me field required.'},
                               )
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),
                                 label='Please upload relevant documents (if any)',
                                 required=False,)
    phone = forms.CharField(min_length=10, max_length=12, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}), required=False, validators=[RegexValidator(regex='^[0-9-_+.]*$', message='Enter a Valid Phone Number',)],
                            # error_messages = {'required':'Title field required.'},
                            )
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
                            required=True,
                            error_messages={
                                'required': 'Title field required.'},
                            )
    abstract = forms.CharField(min_length=300,  widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Abstract', 'onkeyup': 'countChar(this)'}),
                               required=True,
                               label='Abstract (Min. 300 char.)',
                               error_messages={
                                   'required': 'Abstract field required.'},
                               )
    proposal_type = forms.CharField(
        widget=forms.HiddenInput(), label='', initial='ABSTRACT', required=False)

    duration = forms.ChoiceField(
        choices=abs_duration, label='Duration (Mins.)')

    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tags'}),
                           required=False,
                           )
    open_to_share = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), required=True,
                                      label='I am agree to publish my content',)

    class Meta:
        model = Proposal
        exclude = ('user', 'email', 'prerequisite', 'status', 'rate')

    def clean_attachment(self):
        import os
        cleaned_data = self.cleaned_data
        attachment = cleaned_data.get('attachment', None)
        if attachment:
            ext = os.path.splitext(attachment.name)[1]
            valid_extensions = ['.pdf']
            if not ext in valid_extensions:
                raise forms.ValidationError(
                    u'File not supported!  Only .pdf file is accepted')
            if attachment.size > (5*1024*1024):
                raise forms.ValidationError('File size exceeds 5MB')
        return attachment


# modal workshop form for cfw
class WorkshopForm(forms.ModelForm):
    about_me = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'About Me'}),
                               required=True,
                               error_messages={
                                   'required': 'About Me field required.'},
                               )
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),
                                 label='Please upload relevant documents (if any)',
                                 required=False,)
    phone = forms.CharField(min_length=10, max_length=12, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}), required=False, validators=[RegexValidator(regex='^[0-9-_+.]*$', message='Enter a Valid Phone Number',)],
                            )
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
                            required=True,
                            error_messages={
                                'required': 'Title field required.'},
                            )
    abstract = forms.CharField(min_length=300, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Desciption', 'onkeyup': 'countChar(this)'}),
                               required=True,
                               label='Description (Min. 300 char.)',)

    prerequisite = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Prerequisite'}),
                                   label='Prerequisites',
                                   required=False,
                                   )
    proposal_type = forms.CharField(
        widget=forms.HiddenInput(), label='', required=False, initial='WORKSHOP')

    duration = forms.ChoiceField(choices=ws_duration, label='Duration (Hrs.)')

    tags = forms.ChoiceField(choices=MY_CHOICES, label='Level')
    open_to_share = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), required=True,
                                      label='I am agree to publish my content',)

    class Meta:
        model = Proposal
        exclude = ('user', 'email', 'status', 'rate')

    def clean_attachment(self):
        import os
        cleaned_data = self.cleaned_data
        attachment = cleaned_data.get('attachment', None)
        if attachment:
            ext = os.path.splitext(attachment.name)[1]
            valid_extensions = ['.pdf', ]
            if not ext in valid_extensions:
                raise forms.ValidationError(
                    u'File not supported! Only .pdf file is accepted')
            if attachment.size > (5*1024*1024):
                raise forms.ValidationError('File size exceeds 5MB')
        return attachment


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1',
                  'password2')
        first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
                                     label='First Name'
                                     )
        last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
                                    label='Last Name'
                                    )
        email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
                                 required=True,
                                 error_messages={
                                     'required': 'Email field required.'},
                                 label='Email'
                                 )
        username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
                                   required=True,
                                   error_messages={
                                       'required': 'Username field required.'},
                                   label='Username'
                                   )
        password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
                                    required=True,
                                    error_messages={
                                        'required': 'Password field required.'},
                                    label='Password'
                                    )
        password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
                                    required=True,
                                    error_messages={
                                        'required': 'Password Confirm field required.'},
                                    label='Re-enter Password'
                                    )

        def clean_first_name(self):
            return self.cleaned_data["first_name"].title()

        def clean_email(self):
            return self.cleaned_data["email"].lower()

        def clean_last_name(self):
            return self.cleaned_data["last_name"].title()


class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-inline', 'placeholder': 'Username'}),
        label='User Name'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-inline', 'placeholder': 'Password'}),
        label='Password'
    )