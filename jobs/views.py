from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .data import get_jobs_dataframe, to_job_record
from .models import SavedJob


def _options(dataframe, column):
    return sorted(value for value in dataframe[column].dropna().unique() if value)


def job_list(request):
    all_jobs = get_jobs_dataframe()
    jobs = all_jobs
    query = request.GET.get("q", "").strip()
    country = request.GET.get("country", "").strip()
    job_type = request.GET.get("job_type", "").strip()
    experience_years = request.GET.get("experience_years", "").strip()

    if query:
        title_match = jobs["Job Title"].str.contains(query, case=False, na=False)
        skill_match = jobs["skills"].str.contains(query, case=False, na=False)
        jobs = jobs[title_match | skill_match]
    if country:
        jobs = jobs[jobs["Country"] == country]
    if job_type:
        jobs = jobs[jobs["Work Type"] == job_type]
    if experience_years:
        minimum_years = jobs["Experience"].str.extract(r"^(\d+)")[0].astype(int)
        try:
            jobs = jobs[minimum_years <= int(experience_years)]
        except ValueError:
            experience_years = ""

    records = [to_job_record(index, row) for index, row in jobs.head(1000).iterrows()]
    saved_ids = set(request.user.saved_jobs.values_list("csv_index", flat=True)) if request.user.is_authenticated else set()
    for record in records:
        record["is_saved"] = record["id"] in saved_ids
    return render(
        request,
        "jobs/job_list.html",
        {
            "jobs": records,
            "total_matches": len(jobs),
            "showing_count": len(records),
            "query": query,
            "country": country,
            "job_type": job_type,
            "experience_years": experience_years,
            "countries": _options(all_jobs, "Country"),
            "job_types": _options(all_jobs, "Work Type"),
            "experience_options": range(16),
        },
    )


def job_detail(request, pk):
    jobs = get_jobs_dataframe()
    if pk not in jobs.index:
        raise Http404("Job not found")
    job = to_job_record(pk, jobs.loc[pk])
    job["is_saved"] = request.user.is_authenticated and request.user.saved_jobs.filter(csv_index=pk).exists()
    return render(request, "jobs/job_detail.html", {"job": job})


@login_required
def toggle_saved_job(request, pk):
    if request.method == "POST":
        if pk not in get_jobs_dataframe().index:
            raise Http404("Job not found")
        saved_job, created = SavedJob.objects.get_or_create(user=request.user, csv_index=pk)
        if not created:
            saved_job.delete()
    return redirect(request.POST.get("next") or "job_list")
