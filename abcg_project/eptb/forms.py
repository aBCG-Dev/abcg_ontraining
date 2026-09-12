from django import forms
from .constants import EPTB_QUESTIONS


YES_NO = (

    ("Yes", "Yes"),

    ("No", "No")

)


class EPTBScreeningForm(forms.Form):

    doctor_history = forms.ChoiceField(

        label="Has any doctor diagnosed, suspected, or advised investigations for TB outside the lungs in the past 3 months?",
        choices=YES_NO,
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for key, label in EPTB_QUESTIONS:

            self.fields[key] = forms.ChoiceField(
                label=label,
                choices=YES_NO,
                widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
                required=False
            )

            self.fields[f"{key}_details"] = forms.CharField(

                required=False,

                widget=forms.Textarea(

                    attrs={
                        "rows": 2,
                        "class": "form-control",
                        "placeholder": f"Enter details about {label}"
                    }
                )
            )