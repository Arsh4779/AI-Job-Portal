from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from pathlib import Path
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from recommender.utils.pdf_utils import extract_text_from_pdf
from jobs.data import get_jobs_dataframe, to_job_record

from .forms import CVUploadForm, PortalAuthenticationForm, ProfileSetupForm, UserRegisterForm
from .services.cv_parser import extract_cv_details


def extract_profile_from_cv(profile):
    """Read a saved CV and persist the dashboard fields found in it."""
    if not profile.resume:
        return False, "No CV has been uploaded."
    try:
        details = extract_cv_details(extract_text_from_pdf(profile.resume.path))
    except (OSError, ValueError) as error:
        return False, str(error)

    for field, value in details.items():
        if value and not getattr(profile, field):
            setattr(profile, field, value)
    profile.cv_extracted_at = timezone.now()
    profile.save()
    return any(details.values()), None


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account is ready. Please sign in to continue.")
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


def profile_is_complete(profile):
    return all((
        profile.user.email,
        profile.phone,
        profile.linkedin_url,
        profile.github_url,
        profile.skills,
        profile.secondary_school,
        profile.secondary_marks,
        profile.higher_secondary_school,
        profile.higher_secondary_marks,
        profile.university,
        profile.university_marks,
        profile.experience,
    ))


class CVRequiredLoginView(LoginView):
    """Send users without a stored CV to the required upload step."""

    authentication_form = PortalAuthenticationForm

    def get_success_url(self):
        if not profile_is_complete(self.request.user.profile):
            return reverse("profile_setup")
        if not self.request.user.profile.resume:
            return reverse("cv_upload")
        return super().get_success_url()


@login_required
def profile_setup(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileSetupForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved. Now upload your CV.")
            return redirect("cv_upload")
    else:
        form = ProfileSetupForm(instance=profile)
    return render(request, "users/profile_setup.html", {"form": form})


@login_required
def cv_upload(request):
    profile = request.user.profile
    if request.method == "POST":
        form = CVUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            previous_resume_name = profile.resume.name if profile.resume else ""
            profile = form.save()
            extracted, error = extract_profile_from_cv(profile)
            if error:
                profile.resume.delete(save=False)
                profile.resume.name = previous_resume_name
                profile.save(update_fields=["resume"])
                form.add_error("resume", f"We could not read this PDF: {error}")
            else:
                if previous_resume_name and previous_resume_name != profile.resume.name:
                    profile.resume.storage.delete(previous_resume_name)
                if extracted:
                    messages.success(request, "CV saved and dashboard details extracted.")
                else:
                    messages.warning(request, "CV uploaded, but no dashboard details were identified.")
                return redirect("home")
    else:
        form = CVUploadForm(instance=profile)
    return render(
        request,
        "users/cv_upload.html",
        {"form": form, "is_replacement": bool(profile.resume)},
    )


@login_required
def profile(request):
    user_profile = request.user.profile
    if not profile_is_complete(user_profile):
        messages.info(request, "Complete your profile to personalise your dashboard.")
        return redirect("profile_setup")
    if user_profile.resume and not user_profile.cv_extracted_at:
        extracted, error = extract_profile_from_cv(user_profile)
        if error:
            messages.warning(request, "We could not extract data from your CV. Try a text-based PDF.")
        elif extracted:
            messages.success(request, "Your existing CV has been processed and the dashboard updated.")
    skills = [skill.strip() for skill in user_profile.skills.split(",") if skill.strip()]
    profile_fields = (
        user_profile.user.email,
        user_profile.phone,
        user_profile.linkedin_url,
        user_profile.github_url,
        user_profile.skills,
        user_profile.secondary_school,
        user_profile.secondary_marks,
        user_profile.higher_secondary_school,
        user_profile.higher_secondary_marks,
        user_profile.university,
        user_profile.university_marks,
        user_profile.experience,
    )
    completed_fields = sum(bool(field) for field in profile_fields)
    data = get_jobs_dataframe()
    saved_jobs = [to_job_record(item.csv_index, data.loc[item.csv_index]) for item in request.user.saved_jobs.order_by("-saved_at")[:5] if item.csv_index in data.index]
    return render(
        request,
        "users/profile.html",
        {
            "skills": skills,
            "completed_fields": completed_fields,
            "profile_completion": round(completed_fields / len(profile_fields) * 100),
            "cv_filename": Path(user_profile.resume.name).name if user_profile.resume else "",
            "has_extracted_data": bool(user_profile.cv_extracted_at),
            "saved_jobs": saved_jobs,
        },
    )


@login_required
def refresh_cv_data(request):
    if request.method != "POST":
        return redirect("profile")
    extracted, error = extract_profile_from_cv(request.user.profile)
    if error:
        messages.error(request, f"Could not extract CV data: {error}")
    elif extracted:
        messages.success(request, "Dashboard details were refreshed from your CV.")
    else:
        messages.warning(request, "Your CV was read, but no dashboard details were identified.")
    return redirect("profile")
