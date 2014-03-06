from django.shortcuts import render
from openreview.apps.main.models import Paper
from django.db.models import Count, Q

# Create your views here.
def frontpage(request):
    # Display 3 papers in each column
    paper_count = 3
    
    # Find trending papers
    # A paper is trending if it has many reviews in the last 7 days
    trending_papers_list = Paper.objects.extra(select = {
        "num_reviews" : """
            SELECT COUNT(*) FROM main_review
            WHERE main_review.paper_id = main_paper.id
            AND main_review.parent_id IS NULL
            AND main_review.timestamp >= NOW() - interval '7 days'"""
    }).order_by('-num_reviews')[:paper_count]
    
    # Find new papers
    latest_papers_list = Paper.objects.order_by('-publish_date')[:paper_count]
    
    # Find controversial papers
    # A paper is controversial if the votes about its reviews have a large variation - i.e. people don't agree about its reviews
    controversial_papers_list = Paper.objects.extra(select = {
        "controversiality" : """
            SELECT COUNT(*) - SUM(vote) FROM main_vote
            WHERE main_vote.review_id IN (
                SELECT main_review.id FROM main_review
                WHERE main_review.paper_id = main_paper.id
            )"""
    }).order_by('-controversiality')[:paper_count]
    
    return render(request, "main/frontpage.html", {
        "user" : request.user,
        "latest_papers_list" : latest_papers_list,
        "trending_papers_list" : trending_papers_list,
        "controversial_papers_list" : controversial_papers_list
    })
