from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [

    # Home / Analyze
    path(
        "",
        views.analyze,
        name="analyze"
    ),

    # Report History
    path(
        "reports/",
        views.report_history,
        name="report_history"
    ),

    # Report Detail
    path(
        "report/<int:report_id>/",
        views.report_detail,
        name="report_detail"
    ),

    # Download PDF
    path(
        "report/<int:report_id>/download/",
        views.download_report,
        name="download_report"
    ),
]