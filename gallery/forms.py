from django import forms
from .models import Event, Photo

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'is_published']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'caption', 'is_featured']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Add a caption (optional)'}),
        }

class PhotoUploadForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.all(), widget=forms.HiddenInput())
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}),
        required=True,
        label='Select photos'
    )
    captions = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label='Captions (one per line, matching photo order)',
        help_text="Enter one caption per line. They will be matched to the uploaded photos in order."
    )

    def __init__(self, *args, **kwargs):
        event_instance = kwargs.pop('event_instance', None)
        super().__init__(*args, **kwargs)
        if event_instance:
            self.fields['event'].initial = event_instance
        # Add the multiple attribute back in the __init__ if removing attrs works
        # self.fields['images'].widget.attrs.update({'multiple': True})