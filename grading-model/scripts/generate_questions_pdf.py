"""
Generate a PDF of interview questions for the manual grader.
Writes to ~/Desktop/grader-interview.pdf.
"""

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

OUT_PATH = Path.home() / "Desktop" / "grader-interview.pdf"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleBig", parent=styles["Title"], fontSize=20, leading=24,
        spaceAfter=14, textColor=colors.HexColor("#1A3A52"),
    ))
    styles.add(ParagraphStyle(
        name="H1", parent=styles["Heading1"], fontSize=14, leading=17,
        textColor=colors.HexColor("#1A3A52"), spaceBefore=14, spaceAfter=4,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="Q", parent=styles["Normal"], fontSize=10.5, leading=14,
        spaceAfter=5, leftIndent=16, firstLineIndent=-16,
    ))
    return styles


def q(styles, n, text):
    return Paragraph(f"<b>{n}.</b>&nbsp;&nbsp;{text}", styles["Q"])


def build_story(styles):
    story = []

    story.append(Paragraph("Grader Interview", styles["TitleBig"]))

    # === Process ===
    story.append(Paragraph("Process and rubric", styles["H1"]))
    story.append(q(styles, 1, "Walk me through grading one device from the moment you pick it up to the moment you put it down. What do you look at first, in what order, and when do you decide the grade?"))
    story.append(q(styles, 2, "Show me an example of each grade side by side. For each one, point at the specific damage that made it that grade and not a grade above it."))
    story.append(q(styles, 3, "Is there a written rubric or are you doing it by feel and experience? If written, can I have a copy?"))
    story.append(q(styles, 4, "If you had to describe &ldquo;grade B&rdquo; in plain words that a new hire could follow, what would you say? Same for each of the other grades."))
    story.append(q(styles, 5, "How long do you typically spend grading one device? Is it consistent or does it vary?"))
    story.append(q(styles, 6, "Does the rubric differ between iPhones, iPads, and other device types? How?"))
    story.append(q(styles, 7, "Does age or model year matter? Would a new iPhone with the same damage as an old one get a worse grade?"))

    # === What you look at ===
    story.append(Paragraph("Angles and inspection", styles["H1"]))
    story.append(q(styles, 8, "Which angles of the device do you always look at? Front, back, each edge, each corner? In what order?"))
    story.append(q(styles, 9, "Do you flip the device to see the back? Do you tilt it under the light to catch glare?"))
    story.append(q(styles, 10, "Do you use magnification, a loupe, a flashlight at an angle, or anything else to see defects you otherwise miss?"))
    story.append(q(styles, 11, "Do you touch the device or feel for damage with your fingertips, or is it purely visual?"))
    story.append(q(styles, 12, "Is there anything you check that isn&rsquo;t visual? Powering it on, pressing every button, weighing it, listening for rattles, inspecting ports, opening it?"))
    story.append(q(styles, 13, "Which area of the device do you find damage most often? Back? Corners? Edges? Screen?"))
    story.append(q(styles, 14, "Which area matters most for the grade? If front and back had equal damage, which one moves the grade more?"))

    # === Defect taxonomy ===
    story.append(Paragraph("Defects and severity", styles["H1"]))
    story.append(q(styles, 15, "What kinds of defects do you look for? List them. (Scratches, scuffs, dents, chips, cracks, discoloration, wear marks, something else?)"))
    story.append(q(styles, 16, "Which defects are worse than others? If a device has one big dent vs ten small scratches, which gets the worse grade?"))
    story.append(q(styles, 17, "How do you judge the size of a scratch or dent? By eye? Compared to a fingernail or a coin? Using a ruler?"))
    story.append(q(styles, 18, "Does the number of defects matter, or just the worst one? One big scratch vs five small ones?"))
    story.append(q(styles, 19, "Does the location of a defect matter? A scratch on the back vs the same scratch on the front vs on an edge vs on a corner?"))
    story.append(q(styles, 20, "Is there a &ldquo;viewing distance&rdquo; rule? (E.g., defects only count if visible at arm&rsquo;s length, or they always count up close.)"))
    story.append(q(styles, 21, "Are there any instant-disqualifier defects that automatically drop a device to the worst grade? (Cracked glass, bent frame, liquid damage indicator, swollen battery, missing parts, third-party repair, any others?)"))
    story.append(q(styles, 22, "Can you tell when a device has been previously refurbished or had a third-party screen/battery? What gives it away?"))

    # === Edge cases ===
    story.append(Paragraph("Edge cases", styles["H1"]))
    story.append(q(styles, 23, "A device with a pristine front but a heavily scratched back. What grade?"))
    story.append(q(styles, 24, "A device with one dented corner but otherwise perfect. What grade?"))
    story.append(q(styles, 25, "A device with a hairline crack on the back glass that you can only see under angled light. Grade?"))
    story.append(q(styles, 26, "A device with light wear spread everywhere (everything looks a little used) vs a device with one obvious big defect. Which is worse?"))
    story.append(q(styles, 27, "What do you do with a device you genuinely can&rsquo;t decide between two grades?"))
    story.append(q(styles, 28, "When you&rsquo;re unsure between two grades, do you go high or go low? Is there a company policy?"))

    # === Self-consistency ===
    story.append(Paragraph("Consistency and judgment", styles["H1"]))
    story.append(q(styles, 29, "If I handed you the same device twice a week apart, would you give it the same grade every time? On borderline cases, how often would you disagree with yourself?"))
    story.append(q(styles, 30, "Has your personal grading standard changed over time? Are you stricter or looser now than when you started?"))
    story.append(q(styles, 31, "Has the company rubric changed in the last 12 months?"))
    story.append(q(styles, 32, "What&rsquo;s the grade you second-guess yourself on the most?"))
    story.append(q(styles, 33, "What&rsquo;s the hardest thing about grading that would be impossible to teach someone new in a week?"))

    # === Hands-on ===
    story.append(Paragraph("Hands-on", styles["H1"]))
    story.append(q(styles, 34, "Can I watch you grade 10&ndash;20 devices right now and take notes while you do it?"))
    story.append(q(styles, 35, "Can we pull 20 already-graded devices from inventory and re-grade them without looking at the stored label, to see how often you match your own previous call?"))
    story.append(q(styles, 36, "Here are some photos from our POC set &mdash; would you call each one B or C? Can you tell just from the photos, or do you need the device in hand?"))

    return story


def main():
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=LETTER,
        leftMargin=0.8 * inch,
        rightMargin=0.8 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
        title="Grader Interview",
        author="Grading Model POC",
    )
    doc.build(build_story(styles))
    print(f"[written] {OUT_PATH}")


if __name__ == "__main__":
    main()
