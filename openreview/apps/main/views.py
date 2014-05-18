from django.db import transaction
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from openreview.apps.main.models import Paper
from openreview.apps.main.models import Review
from openreview.apps.main.forms import ReviewForm, PaperForm
from openreview.apps.papers import scrapers

def landing_page(request):
    paper_count = 5

    return render(request, "main/landing_page.html", {
      "trending_papers": Paper.trending(top=paper_count),
      "new_papers": Paper.latest()[:paper_count]
    })

@login_required
def dashboard(request):
    paper_count = 5

    return render(request, "main/dashboard.html", {
        "user": request.user,
        "new_papers": Paper.latest()[:paper_count],
        "controversial_papers": Paper.controversial()[:paper_count],
        "trending_papers": Paper.trending(top=paper_count)
    })
