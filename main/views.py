from django.shortcuts import render

# Create your views here.
def frontpage(request):
    return render(request, "main/frontpage.html", {
        "user" : request.user
    })
