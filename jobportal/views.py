from django.shortcuts import render

from jobs.data import get_jobs_dataframe, to_job_record


def home(request):
    jobs = get_jobs_dataframe()
    featured = [
        to_job_record(index, row)
        for index, row in jobs.drop_duplicates(subset=["Job Title", "Company"]).head(6).iterrows()
    ]
    work_type_counts = [{"name": name, "count": int(count)} for name, count in jobs["Work Type"].value_counts().head(4).items()]
    popular_roles = [{"name": name, "count": int(count)} for name, count in jobs["Job Title"].value_counts().head(5).items()]
    top_countries = [{"name": name, "count": int(count)} for name, count in jobs["Country"].value_counts().head(5).items()]
    top_companies = [name for name in jobs["Company"].value_counts().head(10).index]
    return render(
        request,
        "home.html",
        {
            "featured_jobs": featured,
            "job_count": len(jobs),
            "country_count": jobs["Country"].nunique(),
            "company_count": jobs["Company"].nunique(),
            "category_count": jobs["Job Title"].nunique(),
            "work_type_counts": work_type_counts,
            "popular_roles": popular_roles,
            "top_countries": top_countries,
            "top_companies": top_companies,
        },
    )
