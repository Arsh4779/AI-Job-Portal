from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs.update({"autocomplete": "username"})
        self.fields["password1"].widget.attrs.update({"autocomplete": "new-password"})
        self.fields["password2"].widget.attrs.update({"autocomplete": "new-password"})


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "skills", "education", "experience", "resume", "profile_picture"]


class ProfileSetupForm(forms.ModelForm):
    """Required profile details collected before a user uploads a CV."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"})
    )

    class Meta:
        model = Profile
        fields = ["phone", "linkedin_url", "github_url", "skills", "secondary_school", "secondary_marks", "higher_secondary_school", "higher_secondary_marks", "university", "university_marks", "experience"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 98765 43210"}),
            "skills": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Python, Django, SQL, communication"}),
            "secondary_school": forms.TextInput(attrs={"class": "form-control", "placeholder": "Secondary school name"}),
            "secondary_marks": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 88% or 8.8 CGPA"}),
            "higher_secondary_school": forms.TextInput(attrs={"class": "form-control", "placeholder": "Higher secondary school name"}),
            "higher_secondary_marks": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 85% or 8.5 CGPA"}),
            "university": forms.TextInput(attrs={"class": "form-control", "placeholder": "University / college and degree"}),
            "university_marks": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 8.2 CGPA or 76%"}),
            "experience": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Briefly describe your work experience or projects"}),
            "linkedin_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://www.linkedin.com/in/your-name"}),
            "github_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://github.com/your-name"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
        if self.instance and self.instance.user_id:
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.email = self.cleaned_data["email"]
        if commit:
            profile.user.save(update_fields=["email"])
            profile.save()
        return profile


class CVUploadForm(forms.ModelForm):
    """A small, validated form used to complete a new login."""

    class Meta:
        model = Profile
        fields = ["resume"]
        widgets = {
            "resume": forms.ClearableFileInput(
                attrs={"accept": ".pdf,application/pdf"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resume"].required = True

    def clean_resume(self):
        resume = self.files.get("resume")
        if not resume:
            raise forms.ValidationError("Please choose a new CV file.")
        if not resume.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Please upload your CV as a PDF file.")
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Your CV must be smaller than 5 MB.")
        if resume.read(5) != b"%PDF-":
            raise forms.ValidationError("The uploaded file is not a valid PDF.")
        resume.seek(0)
        return resume


class PortalAuthenticationForm(AuthenticationForm):
    """Authentication form with the portal's input styling and browser hints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "username"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "current-password"}
        )
