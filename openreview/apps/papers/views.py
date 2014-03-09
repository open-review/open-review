from django.views.generic import TemplateView

class PaperWithReviewsView(TemplateView):
    template_name = "papers/paper-with-reviews.html"
