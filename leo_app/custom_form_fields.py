from django import forms
from django.utils import html


class SubmitButtonWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        print '{} {}'.format(name,value)
        return '<input type="submit" name="%s" value="%s">' % (html.escape(name), html.escape(value))


class SubmitButtonField(forms.Field):
    def __init__(self, *args, **kwargs):
        if not kwargs:
            kwargs = {}
        kwargs["widget"] = SubmitButtonWidget

        super(SubmitButtonField, self).__init__(*args, **kwargs)

    def clean(self, value):
        return value