from django.shortcuts import render
from openreview.apps.main.models import Paper

# Create your views here.
def frontpage(request):
    # Display 3 papers in each column
    paper_count = 3
    
    # Find new papers
    latest_papers_list = Paper.objects.order_by('-publish_date')[:paper_count]
    
    return render(request, "main/frontpage.html", {
        "user" : request.user,
        "latest_papers_list" : latest_papers_list
    })
