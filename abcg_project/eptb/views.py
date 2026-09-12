from django.shortcuts import render

from .forms import EPTBScreeningForm
from .constants import EPTB_QUESTIONS


def eptb_questions(request):

    form = EPTBScreeningForm()

    context = {
        "form": form,
        "questions": EPTB_QUESTIONS,
    }

    return render( request, "eptb/questions.html", context)