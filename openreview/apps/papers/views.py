from django.views.generic import TemplateView
from openreview.apps.main.models import Paper
from django.shortcuts import render, HttpResponse
import json

from .scrapers import ArXivScraper

class PaperWithReviewsView(TemplateView):
    template_name = "papers/paper-with-reviews.html"

    def get(self, request, id):
        return render(request, "papers/paper-with-reviews.html", {
            "paper": Paper.objects.get(pk=id)
        })


def doi_scraper(request,id):
    return HttpResponse(json.JSONEncoder().encode({"error": "Invalid document identifier"}), content_type="application/json")


def arxiv_scraper(request, id):
    try:
        tempres = ArXivScraper().parse(id)
        return HttpResponse(json.JSONEncoder().encode(tempres.get_results()), content_type="application/json")
    except Exception:
        return HttpResponse(json.JSONEncoder().encode({"error": "Invalid document identifier"}), content_type="application/json")




