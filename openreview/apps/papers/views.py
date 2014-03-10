from django.views.generic import TemplateView
from openreview.apps.main.models import Paper
from django.shortcuts import render

class PaperWithReviewsView(TemplateView):
    template_name = "papers/paper-with-reviews.html"


    def get(self, request, id):
      return render(request, "papers/paper-with-reviews.html", {
          "paper": Paper.objects.get(pk=id)
      })
