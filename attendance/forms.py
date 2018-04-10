from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
import re

from .models import *

class TimeInputField(forms.IntegerField):
        default_error_messages = {
                'negative': _('This field must be positive'),
                'tolarge': _('This field must be less than or equal to 240 (4 hours)'),
        }
        def validate(self, value):
                super(TimeInputField, self).validate(value)
                if value <= 0:
                        raise ValidationError(
                                _(self.default_error_messages['negative']),
                                code='negative',
                        )
                if value > 240:
                        raise ValidationError(
                                _(self.default_error_messages['tolarge']),
                                code='tolarge',
                        )

class NameCharField(forms.CharField):
        default_error_messages = {
                'required': _('This field is required'),
                'invalid': _('This field must only include letters, numbers, and underscores'),
        }
        cleanName = re.compile(r'[0-9a-zA-Z_]*')
        def validate(self, value):
                super(NameCharField, self).validate(value)
                #if not self.cleanName.fullmatch(value):
                #        raise ValidationError(
                #                _(self.default_error_messages['invalid']),
                #                code='invalid',
                #        )

class NamesTextarea(forms.CharField):
        default_error_messages = {
                'required': _('This field is required'),
                'invalid': _('Student list must be a newline-separated list')
        }
        widget = forms.Textarea(attrs={'rows':10, 'cols':25})
        cleanName = re.compile(r'[0-9a-zA-Z]*')
        def validate(self, value):
                for name in value.split("\r\n"):
                        super(NamesTextarea, self).validate(name)
                        #if not self.cleanName.fullmatch(name):
                        #        raise ValidationError(
                        #                _(self.default_error_messages['invalid']),
                        #                code='invalid',
                        #        )

class UpdateCourse(forms.Form):
        class Meta:
                widgets = {
                        'text': forms.Textarea(attrs={'rows':-45, 'cols':25}),
                }
        checkinwindow = TimeInputField(label=mark_safe('<p class="formLabel">Sign In Window (minutes)</p>'), label_suffix="", initial={'code': 15})
        students = NamesTextarea(label=mark_safe('<p class="formLabel">Students</p>'), label_suffix="", max_length=15*300, required=False)

class CourseHome(forms.Form):
        time = TimeInputField(label=mark_safe('<p class="formLabel">Sign In Window (minutes)</p>'), label_suffix="", initial={'code': 15})

class AttendanceStatus(forms.ModelForm):
        class Meta:
                model = AttendanceRecord
                fields = ('studentusername','status',)
        studentusername = NameCharField(disabled=True)

class LoginForm(forms.Form):
        username = forms.CharField()
        password = forms.CharField(widget=forms.PasswordInput)

class CodeEntryForm(forms.Form):
    code = forms.CharField(label=mark_safe('<p class="formLabel">Course Code</p>'), label_suffix="", max_length=5)
