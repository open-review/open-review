from django.shortcuts import render
from openreview.apps.main.forms import ReviewForm

# Create your views here.
def frontpage(request):
    return render(request, "main/frontpage.html", {
        "user" : request.user
    })

def addreview(request):
	data = request.POST if "addreview" in request.POST else None

	return render(request, "main/addreview.html", {
		"user" : request.user,
		"addreview_form" : ReviewForm(data=data)
	})
