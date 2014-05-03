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
    # Display 3 papers in each column
    paper_count = 3

    return render(request, "main/dashboard.html", {
        "user": request.user,
        "latest_papers_list": Paper.latest()[:paper_count],
        "trending_papers_list": Paper.trending(top=paper_count),
        "controversial_papers_list": Paper.controversial()[:paper_count]
    })


@login_required
def add_review(request):
    data = request.POST if "add_review" in request.POST else None

    review_form = ReviewForm(data=data, user=request.user)

    if data and data.get('type') == 'arxiv':
        #TODO potentially unsave?
        scraper = scrapers.Controller(scrapers.ArXivScraper).run(data.get('doc_id'))
        scraper.update({"type": 'arxiv', "doc_id": data.get('doc_id')})
        scraper.update({"authors": "\n".join(scraper['authors'])})

        paper_form = PaperForm(data=scraper)
    else:
        paper_form = PaperForm(data=data)

    with transaction.atomic():
        if paper_form.is_valid() and review_form.is_valid():
            paper = paper_form.save()
            review = review_form.save(commit=False)
            review.paper = paper
            review.save()

            #return redirect(reverse("paper", args=(paper.id,)), parmanent=False)
            return redirect(reverse("dashboard"), parmanent=False)

    return render(request, "main/add_review.html", {
        "user": request.user,
        "add_review_form": review_form,
        "add_paper_form": paper_form
    })
