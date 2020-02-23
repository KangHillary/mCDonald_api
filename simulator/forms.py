from django import forms


class InputForm(forms.Form):
    input = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': 'autofocus'}),
        max_length=160, initial=''
    )


class DialForm(forms.Form):
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': 'autofocus'}),
        max_length=160, initial=''
    )
    language = forms.CharField(
        widget=forms.Select(
            choices=(
                ('en', 'en'),
            ), attrs={'class': 'form-control'}
        ),
        max_length=16, initial='en'
    )
    service_url = forms.URLField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
