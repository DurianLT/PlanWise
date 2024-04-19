from django import forms
from catch_date.models import Event


class EventForm(forms.ModelForm):

    # 使用 DateTimeField 和适当的小部件，必须填写
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=True  # 确保这个字段是必填的
    )
    event = forms.CharField(
        max_length=255,
        required=True  # 确保事件字段是必填的
    )

    class Meta:
        model = Event
        fields = ['date', 'address', 'event', 'comment']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Optional', 'required': False}),
            'comment': forms.Textarea(attrs={'placeholder': 'Optional', 'required': False})
        }
