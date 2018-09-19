from django import forms

from django.forms import ModelForm, widgets

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MinValueValidator, \
    RegexValidator, URLValidator
from captcha.fields import ReCaptchaField
from string import punctuation, digits
try:
    from string import letters
except ImportError:
    from string import ascii_letters as letters

from website.models import Proposal
from website.send_mails import generate_activation_key
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from website.models import (
    Profile, User
)

UNAME_CHARS = letters + "._" + digits
PWD_CHARS = letters + punctuation + digits

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

position_choices = (
    ("student", "Student"),
    ("faculty", "Faculty"),
    ("industry_people", "Industry People"),
)

source = (
    ("FOSSEE website", "FOSSEE website"),
    ("Google", "Google"),
    ("Social Media", "Social Media"),
    ("From other College", "From other College"),
)

title = (
    ("Mr", "Mr."),
    ("Miss", "Ms."),
    ("Professor", "Prof."),
    ("Doctor", "Dr."),
)
states = (
    ("IN-AP",    "Andhra Pradesh"),
    ("IN-AR",    "Arunachal Pradesh"),
    ("IN-AS",    "Assam"),
    ("IN-BR",    "Bihar"),
    ("IN-CT",    "Chhattisgarh"),
    ("IN-GA",    "Goa"),
    ("IN-GJ",    "Gujarat"),
    ("IN-HR",    "Haryana"),
    ("IN-HP",    "Himachal Pradesh"),
    ("IN-JK",    "Jammu and Kashmir"),
    ("IN-JH",    "Jharkhand"),
    ("IN-KA",    "Karnataka"),
    ("IN-KL",    "Kerala"),
    ("IN-MP",    "Madhya Pradesh"),
    ("IN-MH",    "Maharashtra"),
    ("IN-MN",    "Manipur"),
    ("IN-ML",    "Meghalaya"),
    ("IN-MZ",    "Mizoram"),
    ("IN-NL",    "Nagaland"),
    ("IN-OR",    "Odisha"),
    ("IN-PB",    "Punjab"),
    ("IN-RJ",    "Rajasthan"),
    ("IN-SK",    "Sikkim"),
    ("IN-TN",    "Tamil Nadu"),
    ("IN-TG",    "Telangana"),
    ("IN-TR",    "Tripura"),
    ("IN-UT",    "Uttarakhand"),
    ("IN-UP",    "Uttar Pradesh"),
    ("IN-WB",    "West Bengal"),
    ("IN-AN",    "Andaman and Nicobar Islands"),
    ("IN-CH",    "Chandigarh"),
    ("IN-DN",    "Dadra and Nagar Haveli"),
    ("IN-DD",    "Daman and Diu"),
    ("IN-DL",    "Delhi"),
    ("IN-LD",    "Lakshadweep"),
    ("IN-PY",    "Puducherry")
)


# modal proposal form for cfp
class ProposalForm(forms.ModelForm):
    name_of_authors = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Author, Second Author, Third Author'}),
                            required=True,
                            error_messages={
                                'required': 'Name of authors field required.'},
                            )
    about_the_authors = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'About the author(s)'}),
                               required=True,
                               error_messages={
                                   'required': 'About the field required.'},
                               )
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),
                                 label='Please upload relevant documents (if any)',
                                 required=True,)
    phone = forms.CharField(min_length=10, max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your valid contact number'}), required=False, validators=[RegexValidator(regex='^[0-9-_+.]*$', message='Enter a Valid Phone Number',)],
                            # error_messages = {'required':'Title field required.'},
                            )
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the title of your paper'}),
                            required=True,
                            error_messages={
                                'required': 'Title field required.'},
                            )
    abstract = forms.CharField(widget= forms.HiddenInput(),required=False, label='')
    proposal_type = forms.CharField(
        widget=forms.HiddenInput(), label='', initial='ABSTRACT', required=False)

    duration = forms.ChoiceField(widget=forms.Select(attrs={'readonly': True}), choices=abs_duration, required=True)
    #duration = forms.ChoiceField(choices=abs_duration, widget=forms.ChoiceField(attrs={'readonly': True}),
    # label='Duration (Mins.)')

    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tags'}),
                           required=False,
                           )
    open_to_share = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(), required=True,
                                      label='I agree to publish my content',)
    terms_and_conditions = forms.BooleanField(widget=forms.CheckboxInput(), required=True, label='I agree to the terms and conditions')

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
            if attachment.size > (10*1024*1024):
                raise forms.ValidationError('File size exceeds 10MB')
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

    #duration = forms.ChoiceField(choices=ws_duration, label='Duration (Hrs.)')

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


class UserRegistrationForm(forms.Form):
    """A Class to create new form for User's Registration.
    It has the various fields and functions required to register
    a new user to the system"""
    required_css_class = 'required'
    errorlist_css_class = 'errorlist'
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter user name'}), max_length=32, help_text='''Letters, digits,
                               period and underscore only.''',)
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'placeholder': 'Enter valid email id'}))
    password = forms.CharField(max_length=32, widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=32, widget=forms.PasswordInput())
    title = forms.ChoiceField(choices=title)
    first_name = forms.CharField(max_length=32, label='First name', widget=forms.TextInput(
        attrs={'placeholder': 'Enter first name'}))
    last_name = forms.CharField(max_length=32, label='Last name', widget=forms.TextInput(
        attrs={'placeholder': 'Enter last name'},))
    phone_number = forms.RegexField(regex=r'^.{10}$',
                                    error_messages={'invalid': "Phone number must be entered \
                                                  in the format: '9999999999'.\
                                                 Up to 10 digits allowed."}, label='Phone/Mobile', widget=forms.TextInput(attrs={'placeholder': 'Enter valid contact number'},))
    institute = forms.CharField(max_length=32, 
        label='Institute/Organization/Company', widget=forms.TextInput())
    # department = forms.ChoiceField(help_text='Department you work/study',
    #             choices=department_choices)
    #location = forms.CharField(max_length=255, help_text="Place/City")
    #state = forms.ChoiceField(choices=states)
    how_did_you_hear_about_us = forms.ChoiceField(
        choices=source, label='How did you hear about us?')

    def clean_username(self):
        u_name = self.cleaned_data["username"]
        if u_name.strip(UNAME_CHARS):
            msg = "Only letters, digits, period  are"\
                  " allowed in username"
            raise forms.ValidationError(msg)
        try:
            User.objects.get(username__exact=u_name)
            raise forms.ValidationError("Username already exists.")
        except User.DoesNotExist:
            return u_name

    def clean_password(self):
        pwd = self.cleaned_data['password']
        if pwd.strip(PWD_CHARS):
            raise forms.ValidationError("Only letters, digits and punctuation\
                                        are allowed in password")
        return pwd

    def clean_confirm_password(self):
        c_pwd = self.cleaned_data['confirm_password']
        pwd = self.data['password']
        if c_pwd != pwd:
            raise forms.ValidationError("Passwords do not match")

        return c_pwd

    def clean_email(self):
        user_email = self.cleaned_data['email']
        if User.objects.filter(email=user_email).exists():
            raise forms.ValidationError("This email already exists")
        return user_email

    def save(self):
        u_name = self.cleaned_data["username"]
        u_name = u_name.lower()
        pwd = self.cleaned_data["password"]
        email = self.cleaned_data["email"]
        new_user = User.objects.create_user(u_name, email, pwd)
        new_user.first_name = self.cleaned_data["first_name"]
        new_user.last_name = self.cleaned_data["last_name"]
        new_user.save()

        cleaned_data = self.cleaned_data
        new_profile = Profile(user=new_user)
        new_profile.institute = cleaned_data["institute"]
        #new_profile.department = cleaned_data["department"]
        #new_profile.position = cleaned_data["position"]
        new_profile.phone_number = cleaned_data["phone_number"]
        #new_profile.location = cleaned_data["location"]
        new_profile.title = cleaned_data["title"]
        #new_profile.state = cleaned_data["state"]
        new_profile.how_did_you_hear_about_us = cleaned_data["how_did_you_hear_about_us"]
        new_profile.activation_key = generate_activation_key(new_user.username)
        new_profile.key_expiry_time = timezone.now() + \
            timezone.timedelta(days=1)
        new_profile.save()
        key = Profile.objects.get(user=new_user).activation_key
        return u_name, pwd, key