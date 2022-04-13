from django import forms

from django.contrib.auth.forms import User
from django.contrib.auth import authenticate
from joggerlogger.models import Account

class LoginForm(forms.Form):
    username = forms.CharField(max_length = 20)
    password = forms.CharField(max_length = 200, widget = forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            self.message = "Invalid username/password"
            raise forms.ValidationError(self.message)

        return cleaned_data

class RegisterForm(forms.Form):
    username   = forms.CharField(max_length = 20)
    password1  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    password2  = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    email = forms.CharField(max_length=25, widget = forms.EmailInput())

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.message = "Passwords did not match."
            raise forms.ValidationError(self.message)
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            self.message = "Username is already taken."
            raise forms.ValidationError(self.message)
        return username

class RunForm(forms.Form):
    runid = forms.IntegerField()
    title = forms.CharField(max_length=200)
    description = forms.CharField(max_length=400)
    distance = forms.FloatField()
    duration = forms.FloatField() # Duration in minutes
    date = forms.DateField()
    def clean(self):
        cleaned_data = super().clean()
        runid = cleaned_data.get('runid')

class MeetingForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(max_length=400)
    duration = forms.FloatField()  # Duration in minutes
    post_time = forms.DateField()

class PictureForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            'picture',
        )
        widgets = {
            "picture":forms.FileInput(),
        }
        def clean_picture(self):
            picture = self.cleaned_data['picture']
            if not picture or not hasattr(picture, 'content_type'):
                raise forms.ValidationError('You must upload a picture')
            if not picture.content_type or not picture.content_type.startswith('image'):
                raise forms.ValidationError('File type is not image')
            MAX_UPLOAD_SIZE = 2500000
            if picture.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
            return picture

class GoalForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            "goal",
        )

        def clean_goal(self):
            goal = self.cleaned_data.get('goal')
            return goal
