from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse


from openreview.apps.main.forms import ReviewForm
from openreview.apps.main.models.author import Author


# Create your views here.
def frontpage(request):
    return render(request, "main/frontpage.html", {
        "user" : request.user
    })

def addreview(request):
	data = request.POST.copy() if "addreview" in request.POST else None
	f = ReviewForm(data=data)

	if f.is_valid():
		f.save()
		return redirect(reverse("frontpage"), parmanent=False)
	else:
		return render(request, "main/addreview.html", {
		"user" : request.user,
		"addreview_form" : ReviewForm(data=data)
		})
