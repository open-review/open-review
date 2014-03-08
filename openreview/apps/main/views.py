from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from openreview.apps.main.forms import ReviewForm

def frontpage(request):
    return render(request, "main/frontpage.html", {
        "user": request.user
    })


@login_required
def add_review(request):
    data = request.POST.copy() if "add_review" in request.POST else None
    f = ReviewForm(data=data, user=request.user)

    if f.is_valid() and f.save():
        return redirect(reverse("frontpage"), parmanent=False)

    return render(request, "main/add_review.html", {
        "user": request.user,
        "add_review_form": f
    })

