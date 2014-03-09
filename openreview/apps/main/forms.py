from django import forms
from django.utils.translation import ugettext_lazy as _

from openreview.apps.main.models.review import Review
from openreview.apps.main.models.paper import Paper
import re

class ReviewForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.user = user

    text = forms.CharField(label=_("Contents"),
                           widget=forms.Textarea,
                           help_text=_("Enter the text of the review."))

    def set_paper(self, paper):
      if(paper != None):
        self.paper=paper
        return True
      return False
    
    def save(self, commit=True, **kwargs):
        user = super(ReviewForm, self).save(commit=False, **kwargs)
        user.poster = self.user
        user.paper = self.paper
        if commit:
            user.save()
        return user

    class Meta:
        model = Review
        fields = ['text']

class PaperForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(PaperForm, self).__init__(*args, **kwargs)
        self.user = user
        
    #todo: search in existing paper database, select if already in there
    title = forms.RegexField(label=_("Title"),
                             regex=r'^.+$',                                
                             error_messages={ 'invalid': _("This value may contain only letters, numbers and "
                                                 "@/./+/-/_ characters.")})
    #todo: DocID recognizion, auto-fill form                                                   
    doc_id = forms.RegexField(label=_("Document Identifier"),
                              regex=re.compile(r'^((\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b)|([0-9]{4}\.[0-9]{4})(v[0-9])?)$',re.IGNORECASE),
                              help_text=_("Identifier: can either be a DOI or a domain-specific one. For example: 1403.0438 (arXiv)."),
                              required=False,
                              error_messages={
                                    'invalid': _("The format is not recognized. Use a correct DOI or arXiv identifier.")})
    #todo: put in database, multiple authors                                        
    authors = forms.RegexField(label=_("Author"),
                              regex=r'^([ \u00c0-\u01ffa-zA-Z\'\-\.])+$',
                              required=False,                                
                              error_messages={
                                    'invalid': _("This value may contain only letters, spaces and "
                                                 "-/'/. characters.")})     
    abstract = forms.CharField(widget=forms.Textarea, 
                               required=False)
    publisher = forms.RegexField(label=_("Publisher name"),
                                 required=False,
                                 regex=r'^[\w.@+\'& -]*$',                               
                                 error_messages={
                                    'invalid': _("This value may contain only letters, numbers, spaces and "
                                                 "@/./+/-/_/\'/& characters.")})
    #todo: change date (YYYY-MM-DD) into year (YYYY)?                                                 
    publish_date = forms.CharField(label=_("Publish date"),                                
                                   required=False,             
                                   help_text=_("Use input format YYYY-MM-DD"),                    
                                   widget=forms.DateInput(format='%Y-%m-%d'),
                                   error_messages={
                                    'invalid': _("This date is invalid.")})                                                                                                         
    urls = forms.URLField(label=_("URL"),  
                          required=False,
                          error_messages={                                    
                              'invalid': _("This url seems to be invalid.")})   
                                                
    def clean(self):
        cleaned_data = super(PaperForm, self).clean()
        if not cleaned_data['publish_date']:
            cleaned_data['publish_date'] = None
        return cleaned_data
                                                         
    def save(self, commit=True, **kwargs):
        user = super(PaperForm, self).save(commit=False, **kwargs)
        user.poster = self.user
        if commit:
            user.save()          
        return user

    class Meta:
        model = Paper
        fields = ['title','doc_id','authors','abstract','publisher','publish_date','urls']