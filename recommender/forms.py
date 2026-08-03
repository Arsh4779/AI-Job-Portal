from django import forms


class ResumeUploadForm(forms.Form):
    resume = forms.FileField(
        label="Upload Resume (PDF)",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".pdf",
            }
        )
    )

    def clean_resume(self):
        resume = self.cleaned_data["resume"]

        if not resume.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Only PDF files are allowed.")

        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Resume must be smaller than 5 MB."
            )

        header = resume.read(5)
        resume.seek(0)
        if header != b"%PDF-":
            raise forms.ValidationError("The uploaded file is not a valid PDF.")

        return resume
