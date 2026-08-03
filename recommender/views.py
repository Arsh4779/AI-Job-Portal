import tempfile
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ResumeUploadForm
from .ml.recommender import recommend_jobs
from .utils.pdf_utils import extract_text_from_pdf


def _recommend_from_uploaded_file(uploaded_file):
    """Extract a temporary upload and return matches without persisting the file."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temporary_file:
        temporary_path = Path(temporary_file.name)
        for chunk in uploaded_file.chunks():
            temporary_file.write(chunk)
    try:
        return recommend_jobs(extract_text_from_pdf(temporary_path))
    finally:
        temporary_path.unlink(missing_ok=True)


def _filter_recommendations(jobs, params):
    country = params.get("country", "").strip()
    work_type = params.get("work_type", "").strip()
    title = params.get("title", "").strip()
    if country:
        jobs = [job for job in jobs if job["country"] == country]
    if work_type:
        jobs = [job for job in jobs if job["work_type"] == work_type]
    if title:
        jobs = [job for job in jobs if title.casefold() in job["title"].casefold()]
    return jobs, {
        "country": country,
        "work_type": work_type,
        "title": title,
    }


def _result_context(jobs, resume_name, using_saved_cv, form, params):
    countries = sorted({job["country"] for job in jobs if job["country"]})
    work_types = sorted({job["work_type"] for job in jobs if job["work_type"]})
    filtered_jobs, selected_filters = _filter_recommendations(jobs, params)
    return {
        "jobs": filtered_jobs,
        "resume_name": resume_name,
        "using_saved_cv": using_saved_cv,
        "form": form,
        "countries": countries,
        "work_types": work_types,
        **selected_filters,
    }


@login_required
def home(request):
    """Recommend from the saved profile CV, or one temporary comparison CV."""
    profile = request.user.profile
    if not profile.resume:
        messages.info(request, "Upload your CV before viewing recommendations.")
        return redirect("cv_upload")

    form = ResumeUploadForm()
    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                jobs = _recommend_from_uploaded_file(form.cleaned_data["resume"])
            except Exception as error:
                form.add_error("resume", f"Could not process this CV: {error}")
            else:
                return render(
                    request,
                    "recommender/results.html",
                    _result_context(jobs, form.cleaned_data["resume"].name, False, ResumeUploadForm(), request.GET),
                )

    if request.method == "GET":
        try:
            jobs = recommend_jobs(extract_text_from_pdf(profile.resume.path), top_k=100)
        except Exception as error:
            messages.error(request, f"Could not process your saved CV: {error}")
        else:
            return render(
                request,
                "recommender/results.html",
                _result_context(jobs, Path(profile.resume.name).name, True, form, request.GET),
            )

    return render(request, "recommender/index.html", {"form": form})
