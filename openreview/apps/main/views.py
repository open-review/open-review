from django.shortcuts import render
from openreview.apps.main.models import Paper
from django.db.models import Count, Q

# Create your views here.
def frontpage(request):
    # Display 3 papers in each column
    paper_count = 3

    return render(request, "main/frontpage.html", {
        "user" : request.user,
        "latest_papers_list" : Paper.latest()[:paper_count],
        "trending_papers_list" : Paper.trending()[:paper_count],
        "controversial_papers_list" : Paper.controversial()[:paper_count]
    })
