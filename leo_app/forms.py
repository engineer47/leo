from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.files.images import get_image_dimensions
from django.contrib.auth.models import User
from django import forms
from django.utils.html import strip_tags
from leo_app.models import Ribbit, UserProfile, Sighting
from leo_app.custom_form_fields import SubmitButtonField


class UserCreateForm(UserCreationForm):
    #avatar = forms.ImageField(required=False, widget=forms.widgets.ClearableFileInput(attrs={'placehoder': 'avatar'}))
    email = forms.EmailField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'Last Name'}))
    mobile = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={'placeholder': 'mobile number'}))
    username = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password Confirmation'}))

    def is_valid(self):
        form = super(UserCreateForm, self).is_valid()
        for f, error in self.errors.iteritems():
            if f != '__all_':
                self.fields[f].widget.attrs.update({'class': 'error', 'value': strip_tags(error)})
        return form

    class Meta:
        fields = ['email', 'username', 'first_name', 'last_name', 'password1',
                  'password2']
        profile_fields = ['mobile']
        model = User


class VehicleSightingForm(forms.ModelForm):
    registration = forms.CharField(required=True)
    vehicle_model = forms.CharField(required=True)
    #infridgement = forms.CharField(required=True)
    infridgement_code = forms.IntegerField(required=True)
    # Vehicle, Human or Infrastructure
    sighting = forms.CharField(required=True)
    longitude = forms.DecimalField(decimal_places=4, max_digits=7)
    latitude = forms.DecimalField(decimal_places=4, max_digits=6)

    class Meta:
        model = Sighting


class HumanSightingForm(forms.ModelForm):
    human_name = forms.CharField(required=True)
    human_number = forms.CharField(required=True)
    infridgement_code = forms.IntegerField(required=True)
    sighting = forms.CharField(required=True)
    longitude = forms.DecimalField(decimal_places=4, max_digits=7)
    latitude = forms.DecimalField(decimal_places=4, max_digits=6)

    class Meta:
        model = Sighting


class InfrastructureSightingForm(forms.ModelForm):
    registration = forms.CharField(required=True)
    vehicle_model = forms.CharField(required=True)
    infridgement = forms.CharField(required=True)
    infridgement_code = forms.IntegerField(required=True)
    sighting = forms.CharField(required=True)

    class Meta:
        model = Sighting


class AuthenticateForm(AuthenticationForm):
    username = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password'}))
 
    def is_valid(self):
        form = super(AuthenticateForm, self).is_valid()
        for f, error in self.errors.iteritems():
            if f != '__all__':
                self.fields[f].widget.attrs.update({'class': 'error', 'value': strip_tags(error)})
        return form


class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'Last Name'}))
    mobile = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={'placeholder': 'mobile number'}))
    username = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Username'}))
    submit_button = SubmitButtonField(label='Save', initial="Save")
#     password1 = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password'}))
#     password2 = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password Confirmation'}))

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']

        try:
            w, h = get_image_dimensions(avatar)

            #validate dimensions
            max_width = max_height = 100
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    u'Please use an image that is '
                     '%s x %s pixels or smaller.' % (max_width, max_height))

            #validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, '
                    'GIF or PNG image.')

            #validate file size
            if len(avatar) > (20 * 1024):
                raise forms.ValidationError(
                    u'Avatar file size may not exceed 20k.')

        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass

        return avatar


    class Meta:
        fields = ['email', 'username', 'first_name', 'last_name']
        profile_fields = ['mobile']
        model = UserProfile


class LeoForm(forms.ModelForm):
    content = forms.CharField(required=True, widget=forms.widgets.Textarea(attrs={'class': 'ribbitText'}))
    
    def is_valid(self):
        form = super(LeoForm, self).is_valid()
        for f in self.errors.iterkeys():
            if f != '__all__':
                self.fields[f].widget.attrs.update({'class': 'error ribbitText'})
        return form
 
    class Meta:
        model = Ribbit
        exclude = ('user',)