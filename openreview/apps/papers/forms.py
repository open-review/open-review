from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from openreview.apps.main.models import Paper, Author
from openreview.apps.papers import scrapers


class PaperForm(forms.ModelForm):

    title = forms.CharField()
    authors = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Seperated by commas, for example: Tony Cai, Xiaodong Li"}))
    publisher = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "For example: Elsevier"}))
    publish_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    doc_id = forms.CharField(label="Document identifier")
    urls = forms.CharField(label="URL", widget=forms.TextInput(attrs={'placeholder': "For example: http://www.sciencedirect.com/science/article/pii/S0004370201001667"}))

    # TODO: clean_{authors,keywords} use the same algorithm. Generalise?
    def clean_authors(self):
        authors = [a.strip() for a in self.cleaned_data["authors"].split("\n") if a.strip()]
        authors_models = {a.name: a for a in Author.objects.filter(name__in=authors)}
        authors = [authors_models.get(a, Author(name=a)) for a in authors]
        self.cleaned_data["authors"] = authors
        return authors

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

            return paper

    class Meta:
        model = Paper
        fields = ['title', 'authors', 'abstract', 'publish_date', 'publisher', 'urls', 'doc_id']
        widgets = {
            'abstract': forms.Textarea(attrs={'placeholder': "May contain $\LaTeX$ and *Markdown*"})
        }


class ArXivForm(forms.Form):
    arxiv_id = forms.CharField(label='Arxiv ID', widget=forms.TextInput(attrs={'placeholder': "For example: 1401.0003"}))

    def clean_arxiv_id(self):
        arid = self.cleaned_data['arxiv_id']
        try:
            scrapers.Controller(scrapers.ArXivScraper).run(arid)
            return arid
        except scrapers.ScraperError:
            raise ValidationError("Invalid ArXiv identifier")

    def save(self, commit=True):
        if not commit:
            raise ValueError("commit=True mandatory")

        data = scrapers.Controller(scrapers.ArXivScraper).run(self.cleaned_data['arxiv_id'])
        authors = data.pop('authors')
        categories = data.pop('categories')
        with transaction.atomic():
            paper = Paper.objects.create(**data)
            for a in authors:
                author, _ = Author.objects.get_or_create(name=a)
                paper.authors.add(author)

            for c in categories:
                paper.categories.add(c)

            paper.save()

        return paper
