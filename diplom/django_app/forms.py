from django import forms
from .models import Comment, Vacancy, Review, Work


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


from .models import BusinessProject


class BusinessIdeaForm(forms.ModelForm):
    class Meta:
        model = BusinessProject
        fields = ['title', 'description']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 2:
            raise forms.ValidationError("Название должно содержать не менее 2 символов.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise forms.ValidationError("Описание должно содержать не менее 10 символов.")
        return description


from django import forms


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['vacancy', 'full_name','city', 'experience', 'last_experience', 'about',
                  'phone_number', 'age', 'face_photo']
        face_photo = forms.ImageField(required=False)



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class WorkForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ['title', 'description', 'requirements', 'contacts']





class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


class ProductUploadForm(forms.Form):
    file = forms.FileField()