from django.views.generic import TemplateView
from openreview.apps.main.models import Paper
from django.shortcuts import render, HttpResponse


class PaperWithReviewsView(TemplateView):
    template_name = "papers/paper-with-reviews.html"

    def get(self, request, id):
        return render(request, "papers/paper-with-reviews.html", {
            "paper": Paper.objects.get(pk=id)
        })


def doi_scraper(request,id):
    return HttpResponse("Scrapen van DOI {id} mislukt.".format(id=id))


def arxiv_scraper(request, id):
    return HttpResponse("Scrapen van Arxiv {id} mislukt.".format(id=id))

