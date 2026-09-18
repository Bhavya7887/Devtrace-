import re
import json
from io import BytesIO

from django.shortcuts import render, get_object_or_404
from django.http import FileResponse

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from config import GITHUB_TOKEN

from github.client import GitHubClient
from analyzer.repository import RepositoryAnalyzer
from analyzer.commits import CommitAnalyzer
from analyzer.files import FileAnalyzer
from analyzer.risk import RiskAnalyzer

from .models import Report


# ============================================================
# ANALYZE GITHUB REPOSITORY
# ============================================================

def analyze(request):

    context = {}

    if request.method == "POST":

        github_url = request.POST.get("github_url", "").strip()

        pattern = r"github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, github_url)

        if not match:
            context["error"] = "Please enter a valid GitHub repository URL."

            return render(
                request,
                "dashboard/analyze.html",
                context
            )

        owner = match.group(1)
        repo = match.group(2).replace(".git", "")

        try:

            github = GitHubClient(GITHUB_TOKEN)

            print(f"[+] Analyzing {owner}/{repo}")

            # GitHub data
            repository = github.get_repository(
                owner,
                repo
            )

            commits = github.get_commits(
                owner,
                repo
            )

            # File analysis
            file_data = FileAnalyzer(
                github
            ).analyze(
                owner,
                repo
            )

            # Repository analysis
            repository_analysis = RepositoryAnalyzer(
                repository
            ).analyze()

            # Commit analysis
            commit_analysis = CommitAnalyzer(
                commits
            ).analyze()

            # Risk analysis
            risk_data = RiskAnalyzer(
                file_data["files"],
                github,
                owner,
                repo
            ).analyze()

            # ------------------------------------------------
            # SAVE REPORT
            # ------------------------------------------------

            report = Report.objects.create(

                repository_name=(
                    repository_analysis.get("full_name")
                    or f"{owner}/{repo}"
                ),

                repository_url=github_url,

                language=repository_analysis.get(
                    "language"
                ),

                stars=repository_analysis.get(
                    "stars"
                ) or 0,

                forks=repository_analysis.get(
                    "forks"
                ) or 0,

                open_issues=repository_analysis.get(
                    "open_issues"
                ) or 0,

                total_commits=commit_analysis.get(
                    "total_commits"
                ) or 0,

                contributors=commit_analysis.get(
                    "contributors"
                ) or 0,

                total_files=file_data.get(
                    "total_files"
                ) or 0,

                total_directories=file_data.get(
                    "total_directories"
                ) or 0,

                repository_data=repository_analysis,

                commit_data=commit_analysis,

                file_data=file_data,

                risk_data=risk_data
            )

            print(
                f"[+] Report saved with ID: {report.id}"
            )

            # ------------------------------------------------
            # RESULT PAGE
            # ------------------------------------------------

            context = {
                "repository": repository_analysis,
                "commits": commit_analysis,
                "files": file_data,
                "risks": risk_data,
                "report_id": report.id,
            }

            return render(
                request,
                "dashboard/result.html",
                context
            )

        except Exception as e:

            print(
                f"[ERROR] {str(e)}"
            )

            context["error"] = (
                f"Analysis failed: {str(e)}"
            )

    return render(
        request,
        "dashboard/analyze.html",
        context
    )


# ============================================================
# REPORT HISTORY
# ============================================================

def report_history(request):

    reports = Report.objects.all()

    return render(
        request,
        "dashboard/report_history.html",
        {
            "reports": reports
        }
    )


# ============================================================
# REPORT DETAIL
# ============================================================

def report_detail(request, report_id):

    report = get_object_or_404(
        Report,
        id=report_id
    )

    return render(
        request,
        "dashboard/report_detail.html",
        {
            "report": report
        }
    )


# ============================================================
# DOWNLOAD PDF
# ============================================================

def download_report(request, report_id):

    report = get_object_or_404(
        Report,
        id=report_id
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=45,
        bottomMargin=45,

        title=f"DevTrace Report - {report.repository_name}",

        author="DevTrace Frontier Intelligence"
    )

    styles = getSampleStyleSheet()

    # ========================================================
    # COLORS
    # ========================================================

    paper_light = colors.HexColor("#FFF8E7")
    brown_dark = colors.HexColor("#281A14")
    red = colors.HexColor("#8D1F1F")
    gold = colors.HexColor("#B88A35")
    ink = colors.HexColor("#2D2119")
    muted = colors.HexColor("#6D5947")
    green = colors.HexColor("#3E593B")
    danger = colors.HexColor("#7D2020")

    # ========================================================
    # STYLES
    # ========================================================

    title_style = ParagraphStyle(
        "ReportTitle",

        parent=styles["Title"],

        fontName="Helvetica-Bold",

        fontSize=25,

        leading=30,

        alignment=TA_CENTER,

        textColor=paper_light,

        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",

        parent=styles["Normal"],

        fontSize=10,

        leading=14,

        alignment=TA_CENTER,

        textColor=colors.HexColor("#E7D5AD"),

        spaceAfter=5
    )

    section_style = ParagraphStyle(
        "Section",

        parent=styles["Heading2"],

        fontName="Helvetica-Bold",

        fontSize=15,

        leading=19,

        textColor=brown_dark,

        spaceBefore=14,

        spaceAfter=8
    )

    repo_style = ParagraphStyle(
        "Repository",

        parent=styles["Normal"],

        fontName="Helvetica-Bold",

        fontSize=17,

        leading=22,

        textColor=red,

        alignment=TA_CENTER,

        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalCustom",

        parent=styles["Normal"],

        fontSize=9.5,

        leading=14,

        textColor=ink
    )

    small_style = ParagraphStyle(
        "Small",

        parent=styles["Normal"],

        fontSize=8,

        leading=11,

        textColor=muted
    )

    white_style = ParagraphStyle(
        "White",

        parent=styles["Normal"],

        fontSize=9,

        leading=13,

        textColor=colors.white
    )

    risk_style = ParagraphStyle(
        "Risk",

        parent=styles["Normal"],

        fontSize=9,

        leading=13,

        textColor=danger
    )

    # ========================================================
    # HEADER / FOOTER
    # ========================================================

    def draw_header_footer(canvas, doc):

        canvas.saveState()

        width, height = A4

        # Header

        canvas.setFillColor(
            brown_dark
        )

        canvas.rect(
            0,
            height - 70,
            width,
            70,
            fill=1,
            stroke=0
        )

        canvas.setFillColor(
            gold
        )

        canvas.setFont(
            "Helvetica-Bold",
            9
        )

        canvas.drawString(
            40,
            height - 28,
            "DEVTRACE"
        )

        canvas.setFillColor(
            colors.HexColor("#E7D5AD")
        )

        canvas.setFont(
            "Helvetica",
            7
        )

        canvas.drawString(
            40,
            height - 42,
            "FRONTIER INTELLIGENCE"
        )

        # Footer

        canvas.setStrokeColor(
            gold
        )

        canvas.setLineWidth(
            0.6
        )

        canvas.line(
            40,
            32,
            width - 40,
            32
        )

        canvas.setFillColor(
            muted
        )

        canvas.setFont(
            "Helvetica",
            7
        )

        canvas.drawString(
            40,
            20,
            "Generated by DevTrace"
        )

        canvas.drawRightString(
            width - 40,
            20,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    # ========================================================
    # PDF STORY
    # ========================================================

    story = []

    # ========================================================
    # COVER
    # ========================================================

    cover_data = [

        [
            Paragraph(
                "DEVTRACE",
                title_style
            )
        ],

        [
            Paragraph(
                "FRONTIER INTELLIGENCE",
                subtitle_style
            )
        ],

        [
            Paragraph(
                "REPOSITORY INVESTIGATION REPORT",
                subtitle_style
            )
        ]
    ]

    cover_table = Table(
        cover_data,

        colWidths=[
            7.0 * inch
        ],

        rowHeights=[
            0.55 * inch,
            0.3 * inch,
            0.3 * inch
        ]
    )

    cover_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                brown_dark
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                2,
                gold
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                15
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                15
            )
        ])
    )

    story.append(
        Spacer(
            1,
            0.45 * inch
        )
    )

    story.append(
        cover_table
    )

    story.append(
        Spacer(
            1,
            0.35 * inch
        )
    )

    story.append(
        Paragraph(
            report.repository_name,
            repo_style
        )
    )

    story.append(
        Paragraph(
            report.repository_url,
            small_style
        )
    )

    story.append(
        Spacer(
            1,
            0.3 * inch
        )
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    summary_data = [

        [
            Paragraph(
                "<b>LANGUAGE</b>",
                normal_style
            ),

            Paragraph(
                str(
                    report.language
                    or
                    "Not detected"
                ),
                normal_style
            ),

            Paragraph(
                "<b>STARS</b>",
                normal_style
            ),

            Paragraph(
                str(report.stars),
                normal_style
            )
        ],

        [
            Paragraph(
                "<b>FORKS</b>",
                normal_style
            ),

            Paragraph(
                str(report.forks),
                normal_style
            ),

            Paragraph(
                "<b>OPEN ISSUES</b>",
                normal_style
            ),

            Paragraph(
                str(report.open_issues),
                normal_style
            )
        ],

        [
            Paragraph(
                "<b>COMMITS</b>",
                normal_style
            ),

            Paragraph(
                str(report.total_commits),
                normal_style
            ),

            Paragraph(
                "<b>CONTRIBUTORS</b>",
                normal_style
            ),

            Paragraph(
                str(report.contributors),
                normal_style
            )
        ],

        [
            Paragraph(
                "<b>FILES</b>",
                normal_style
            ),

            Paragraph(
                str(report.total_files),
                normal_style
            ),

            Paragraph(
                "<b>DIRECTORIES</b>",
                normal_style
            ),

            Paragraph(
                str(report.total_directories),
                normal_style
            )
        ]
    ]

    summary_table = Table(
        summary_data,

        colWidths=[
            1.35 * inch,
            2.05 * inch,
            1.35 * inch,
            2.05 * inch
        ]
    )

    summary_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                paper_light
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.7,
                colors.HexColor("#B99A67")
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    story.append(
        Paragraph(
            "REPOSITORY SUMMARY",
            section_style
        )
    )

    story.append(
        summary_table
    )

    # ========================================================
    # GENERIC DATA TABLE FUNCTION
    # ========================================================

    def create_data_table(data):

        rows = []

        for key, value in data.items():

            if isinstance(
                value,
                (dict, list)
            ):

                if isinstance(
                    value,
                    list
                ):

                    value = (
                        f"{len(value)} items detected"
                    )

                else:

                    value = json.dumps(
                        value,
                        indent=2,
                        default=str
                    )[:2000]

            rows.append(
                [
                    Paragraph(
                        str(key)
                        .replace("_", " ")
                        .title(),

                        normal_style
                    ),

                    Paragraph(
                        str(value),

                        small_style
                    )
                ]
            )

        if not rows:
            return None

        table = Table(
            rows,

            colWidths=[
                1.8 * inch,
                5.0 * inch
            ]
        )

        table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#E5C98F")
                ),

                (
                    "BACKGROUND",
                    (1, 0),
                    (1, -1),
                    paper_light
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#B99A67")
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ])
        )

        return table

    # ========================================================
    # REPOSITORY INTELLIGENCE
    # ========================================================

    story.append(
        Paragraph(
            "REPOSITORY INTELLIGENCE",
            section_style
        )
    )

    repository_table = create_data_table(
        report.repository_data or {}
    )

    if repository_table:
        story.append(
            repository_table
        )

    # ========================================================
    # COMMIT INTELLIGENCE
    # ========================================================

    story.append(
        Paragraph(
            "COMMIT INTELLIGENCE",
            section_style
        )
    )

    commit_table = create_data_table(
        report.commit_data or {}
    )

    if commit_table:
        story.append(
            commit_table
        )

    # ========================================================
    # FILE INTELLIGENCE
    # ========================================================

    story.append(
        Paragraph(
            "FILE SYSTEM INTELLIGENCE",
            section_style
        )
    )

    file_table = create_data_table(
        report.file_data or {}
    )

    if file_table:
        story.append(
            file_table
        )

    # ========================================================
    # RISK ANALYSIS
    # ========================================================

    story.append(
        Paragraph(
            "RISK INVESTIGATION",
            section_style
        )
    )

    risks = report.risk_data or []

    if risks:

        risk_rows = [

            [
                Paragraph(
                    "<b>RISK / FINDING</b>",
                    white_style
                )
            ]
        ]

        for risk in risks:

            if isinstance(
                risk,
                dict
            ):

                risk_text = json.dumps(
                    risk,
                    indent=2,
                    default=str
                )

            else:

                risk_text = str(risk)

            risk_rows.append(
                [
                    Paragraph(
                        risk_text,
                        risk_style
                    )
                ]
            )

        risk_table = Table(
            risk_rows,

            colWidths=[
                6.8 * inch
            ]
        )

        risk_table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    danger
                ),

                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.HexColor("#F7E4D6")
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    danger
                ),

                (
                    "INNERGRID",
                    (0, 1),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D3A18D")
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story.append(
            risk_table
        )

    else:

        safe_table = Table(
            [
                [
                    Paragraph(
                        "No significant risks were detected.",
                        normal_style
                    )
                ]
            ],

            colWidths=[
                6.8 * inch
            ]
        )

        safe_table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#E6EAD9")
                ),

                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    green
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                )
            ])
        )

        story.append(
            safe_table
        )

    # ========================================================
    # FINAL
    # ========================================================

    story.append(
        Spacer(
            1,
            0.3 * inch
        )
    )

    final_table = Table(
        [
            [
                Paragraph(
                    "CASE FILE CLOSED",
                    title_style
                )
            ],

            [
                Paragraph(
                    "Generated by DevTrace Frontier Intelligence",
                    subtitle_style
                )
            ]
        ],

        colWidths=[
            7.0 * inch
        ],

        rowHeights=[
            0.55 * inch,
            0.35 * inch
        ]
    )

    final_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                brown_dark
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                2,
                gold
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            )
        ])
    )

    story.append(
        final_table
    )

    # ========================================================
    # BUILD
    # ========================================================

    document.build(
        story,
        onFirstPage=draw_header_footer,
        onLaterPages=draw_header_footer
    )

    buffer.seek(0)

    filename = (
        report.repository_name
        .replace("/", "-")
        .replace(" ", "_")
        + "_DevTrace_Report.pdf"
    )

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf"
    )