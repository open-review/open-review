from django import forms
from django.forms import widgets
from django.core.exceptions import ObjectDoesNotExist
from openreview.apps.main.models import Author, Keyword

from openreview.apps.main.models.review import Review
from openreview.apps.main.models.paper import Paper


class ReviewForm(forms.ModelForm):
    def __init__(self, user, paper=None, **kwargs):
        super(ReviewForm, self).__init__(**kwargs)
        self.user = user
        self.paper = paper

    def save(self, commit=True, **kwargs):
        review = super(ReviewForm, self).save(commit=False, **kwargs)
        review.poster = self.user

        if self.paper is not None:
            review.paper = self.paper

        if commit:
            review.save()
        return review

    class Meta:
        model = Review
        fields = ['text']


class PaperForm(forms.ModelForm):
    type_choices = [('',"Select an item"),
                    ('doi',"Digital object identifier"),
                    ('arxiv',"arXiv identifier"),
                    ('manually',"Manually")]

    type = forms.ChoiceField(choices=type_choices, help_text="Select an option")
    authors = forms.CharField(widget=widgets.Textarea(), help_text="Authors of this paper, separated with a newline.")
    keywords = forms.CharField(widget=widgets.Textarea(), help_text="Keywords, separated with a comma.", required=False)

    def __init__(self, *args, **kwargs):
        super(PaperForm, self).__init__(*args, **kwargs)

        # Fields are defined as TextFields in Paper model as we don't want to
        # restrict sizes (they would be completely arbitrary and don't offer
        # improved performance).

        self.fields["title"].widget = widgets.TextInput()
        self.fields["doc_id"].widget = widgets.TextInput()
        self.fields["publisher"].widget = widgets.TextInput()
        self.fields["keywords"].widget = widgets.TextInput()

    # TODO: clean_{authors,keywords} use the same algorithm. Generalise?
    def clean_authors(self):
        authors = [a.strip() for a in self.cleaned_data["authors"].split("\n") if a.strip()]
        authors_models = {a.name: a for a in Author.objects.filter(name__in=authors)}
        authors = [authors_models.get(a, Author(name=a)) for a in authors]
        self.cleaned_data["authors"] = authors
        return authors

    def clean_keywords(self):
        keywords = [k.strip() for k in self.cleaned_data["keywords"].split(",") if k.strip()]
        keywords_models = {k.label: k for k in Keyword.objects.filter(label__in=keywords)}
        keywords = [keywords_models.get(k, Keyword(label=k)) for k in keywords]
        self.cleaned_data["keywords"] = keywords
        return keywords       

    def save(self, commit=True, **kwargs):
        """
        Beware: saving with commit=False will result in any newly created authors to not
        be created also.
        """
        try:
            return Paper.objects.get(doc_id=self.cleaned_data.get("doc_id"))
        except Paper.DoesNotExist:
            paper = super(PaperForm, self).save(commit=False, **kwargs)

            if commit:
                paper.save()
                # TODO: More efficient implementation. This calls the database N times, which is
                # TODO: stupid. We can use use Postgres RETURNING ID as used in the following manner:
                # TODO: https://github.com/amcat/amcat/blob/master/amcat/models/coding/codedarticle.py#L130
                for author in self.cleaned_data["authors"]:
                    if author.id is None:
                        author.save()
                paper.authors.add(*self.cleaned_data["authors"])

                for keyword in self.cleaned_data["keywords"]:
                    if keyword.id is None:
                        keyword.save()
                paper.keywords.add(*self.cleaned_data["keywords"])
                
                paper.categories.add(*self.cleaned_data["categories"])                

                print(paper.categories.all())
            return paper

    class Meta:
        model = Paper
        fields = [
            'type', 'title', 'doc_id', 'authors', 'abstract', 'keywords',
            'publisher', 'publish_date', 'urls', 'categories'
        ]