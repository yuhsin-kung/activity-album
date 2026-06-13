from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event, EventPhoto, EventDocument


class MemberSignUpForm(UserCreationForm):
    first_name = forms.CharField(label='姓名', max_length=150, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'password1', 'password2']
        labels = {
            'username': '帳號',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.is_staff = False
        if commit:
            user.save()
        return user


class EventForm(forms.ModelForm):
    start_date = forms.DateField(
        label='活動開始日期',
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
    )
    end_date = forms.DateField(
        label='活動結束日期',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        input_formats=['%Y-%m-%d'],
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'start_date', 'end_date', 'location']


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = EventPhoto
        fields = ['image', 'caption']


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = EventDocument
        fields = ['title', 'file']
