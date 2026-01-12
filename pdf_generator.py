from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

def generate_pdf(result, filename="resume_analysis_report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("<b>Resume Analysis Report</b>", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))

    # ATS Score
    story.append(Paragraph(f"<b>ATS Compatibility Score:</b> {result['ats_score']} / 100", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    def add_section(title, items):
        story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        story.append(
            ListFlowable(
                [ListItem(Paragraph(i, styles["Normal"])) for i in items],
                bulletType="bullet"
            )
        )
        story.append(Spacer(1, 0.25 * inch))

    add_section("Strengths", result["strengths"])
    add_section("Weaknesses", result["weaknesses"])
    add_section("Missing / Suggested Skills", result["missing_skills"])
    add_section("Improved Resume Bullet Points", result["improved_bullets"])
    add_section("Overall Suggestions", result["suggestions"])
    add_section("Skill Improvement Roadmap", result["skill_roadmap"])
    add_section("Project Feedback", result["project_feedback"])
    add_section("Recommended Projects to Add", result["recommended_projects"])

    doc.build(story)
    return filename
