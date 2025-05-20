import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from io import BytesIO
import streamlit_antd_components as sac
import datetime, re
import google.generativeai as genai
import base64

# Configure Gemini API
genai.configure(api_key="AIzaSyCowEfoqnX5RJtIK8dIDkhu1BBqi-Pi6-Y")

def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    pattern = r"^\+?[0-9]{10,14}$"
    return re.match(pattern, phone) is not None

def is_valid_url(url):
    pattern = r"^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$"
    return re.match(pattern, url) is not None

def format_date(date):
    return date.strftime("%Y")

def generate_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.3 * inch,
        bottomMargin=0.3 * inch,
    )
    styles = getSampleStyleSheet()
    story = []

    # Custom styles with reduced spacing
    normal_style = ParagraphStyle(
        name="Normal", parent=styles["Normal"], fontSize=11, spaceAfter=2  # Reduced from 4
    )
    bold_style = ParagraphStyle(
        name="BoldStyle", parent=styles["Normal"], fontSize=12, spaceAfter=2, fontName="Helvetica-Bold"  # Reduced from 4
    )
    course_style = ParagraphStyle(
        name="CourseStyle", parent=styles["Normal"], fontSize=12, spaceAfter=2, fontName="Helvetica-Bold", leading=14  # Reduced from 4
    )
    school_style = ParagraphStyle(
        name="SchoolStyle", parent=styles["Normal"], fontSize=11, spaceAfter=0, leftIndent=0
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=normal_style,
        leftIndent=15,
        spaceAfter=2,  # Reduced from 4
        bulletIndent=5,
        firstLineIndent=-5
    )

    # Title with reduced spacing
    if data["name"]:
        title_style = ParagraphStyle(
            name="Title",
            parent=styles["Heading1"],
            alignment=TA_CENTER,
            fontSize=24,
            spaceAfter=6,  # Reduced from 6
        )
        story.append(Paragraph(f"{data['name']}".upper(), title_style))

    # Contact Info with reduced spacing
    contact_style = ParagraphStyle(
        name="Contact",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        spaceAfter=6,  
    )

    contact_parts = []
    if data["email"]:
        contact_parts.append(data["email"])
    if data["phone"]:
        contact_parts.append(data["phone"])
    if data["linkedin"]:
        contact_parts.append(
            f"<link href='{data['linkedin']}'><font color='blue'><u>{data['linkedin']}</u></font></link>"
        )
    if data["github"]:
        contact_parts.append(
            f"<link href='https://{data['github']}'><font color='blue'><u>{data['github']}</u></font></link>"
        )

    if contact_parts:
        contact_info = " | ".join(contact_parts)
        story.append(Paragraph(contact_info, contact_style))

    story.append(Spacer(1, 1))  # Kept minimal
    story.append(
        HRFlowable(
            width="100%", thickness=0.5, color=colors.grey, spaceBefore=0, spaceAfter=1  # Reduced from spaceAfter=1
        )
    )

    # Sections with reduced spacing
    sections = [
        ("SUMMARY", "summary"),
        ("EDUCATION", "education"),
        ("EXPERIENCE", "experience"),
        ("SKILLS", "skills"),
        ("PROJECTS", "projects"),
        ("ACCOMPLISHMENTS", "accomplishments"),
    ]

    for section_title, section_key in sections:
        if section_key == "education" and data.get("education"):
            story.append(Paragraph(section_title, styles["Heading2"]))
            for edu in data["education"]:
                education_table = Table([
                    [
                        Paragraph(f"{edu['course'].title()}", course_style),
                        Paragraph(f"{format_date(edu['timeline'][0])} - {format_date(edu['timeline'][1])}", 
                                ParagraphStyle(name="RightAlign", alignment=TA_RIGHT, fontSize=10))
                    ] if edu["course"] and edu["timeline"] else [""],
                    [
                        Paragraph(f"{edu['school'].title()}", school_style),
                        Paragraph(f"{edu['grade']}",ParagraphStyle(name="RightAlign", alignment=TA_RIGHT, fontSize=10)) if edu["grade"] else ""
                        ""
                    ] if edu["school"] else [""],
                ], colWidths=[410, 100])
                
                education_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                
                story.append(education_table)
                story.append(Spacer(1, 1))  # Reduced from Spacer(1, 1)

        elif section_key == "experience" and data.get("experience"):
            story.append(Paragraph(section_title, styles["Heading2"]))
            for exp in data["experience"]:
                if exp["company"] and exp["timeline"] and exp["role"]:
                    timeline_str = f"{format_date(exp['timeline'][0])} - {format_date(exp['timeline'][1])}"
                    story.append(
                        Paragraph(
                            f"<b>{exp['company'].title()}, {exp['role'].title()}</b> | <b>{timeline_str}</b>",
                            bold_style,
                        )
                    )
                if exp["experience_summary"]:
                    bullet_points = re.split(
                        r"\s*-\s+", exp["experience_summary"].strip()
                    )
                    for point in bullet_points:
                        if point:
                            story.append(Paragraph(f"\u2022 {point}", normal_style))
                story.append(Spacer(1, 4))  # Reduced from Spacer(1, 8)

        elif section_key == "skills" and (data.get("technical_skills") or data.get("tools") or data.get("other_skills")):
            story.append(Paragraph(section_title, styles["Heading2"]))
            
            skills_content = []
            if data.get("technical_skills"):
                skills_content.append(f"<b>Technical Skills:</b> {data['technical_skills']}")
            if data.get("tools"):
                skills_content.append(f"<b>Tools & Technologies:</b> {data['tools']}")
            if data.get("other_skills"):
                skills_content.append(f"<b>Other Skills:</b> {data['other_skills']}")
            
            story.append(Paragraph("<br/>".join(skills_content), normal_style))
            story.append(Spacer(1, 6))  # Reduced from Spacer(1, 12)
                
        elif section_key == "projects" and data.get("projects"):
            story.append(Paragraph(section_title, styles["Heading2"]))
            for project in data["projects"]:
                if isinstance(project, dict) and project.get("name"):
                    project_name = project['name']
                    if project.get("url"):
                        project_name = f"<link href='{project['url']}' color='black'><u><b>{project_name}</b></u></link>"
                    else:
                        project_name = f"<b>{project_name}</b>"
                        
                    project_table = Table([
                        [
                            Paragraph(project_name, styles["Heading3"]),
                            Paragraph(f"{project.get('year', '')}", 
                                    ParagraphStyle(name="RightAlign", alignment=TA_RIGHT, fontSize=10))
                        ]
                    ], colWidths=[400, 110])
                    
                    project_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    
                    story.append(project_table)
                    
                    if project.get("description"):
                        bullet_points = [p.strip() for p in project["description"].split("\n") if p.strip()]
                        for point in bullet_points:
                            if point.startswith("-"):
                                story.append(Paragraph(point, normal_style))
                            else:
                                story.append(Paragraph(f"• {point}", normal_style))
                    story.append(Spacer(1, 4))  # Reduced from Spacer(1, 6)

        elif section_key == "accomplishments" and data.get("accomplishments"):
            story.append(Paragraph(section_title, styles["Heading2"]))
            for acc in data["accomplishments"]:
                if isinstance(acc, dict) and acc.get("title"):
                    if acc.get("url"):
                        acc_title = f"<link href='{acc['url']}' color='black'><u><b>{acc['title']}</b></u></link>"
                    else:
                        acc_title = f"<b>{acc['title']}</b>"
                    
                    if acc.get("issuer"):
                        acc_title += f" - {acc['issuer']}"
                    if acc.get("year"):
                        acc_title += f" | {acc['year']}"
                    
                    story.append(Paragraph(acc_title, styles["Heading3"]))
                    
                    if acc.get("description"):
                        desc = acc["description"].strip()
                        if desc:
                            story.append(Paragraph(desc, normal_style))
                    story.append(Spacer(1, 4))  # Reduced from Spacer(1, 6)
                
        elif section_key == "summary" and data.get(section_key):
            story.append(Paragraph(section_title, styles["Heading2"]))
            story.append(Paragraph(data[section_key], normal_style))

        # Reduced spacing for horizontal lines between sections
        if ((section_key == "education" and data.get("education")) or
            (section_key == "experience" and data.get("experience")) or
            (section_key == "skills" and (data.get("technical_skills") or data.get("tools") or data.get("other_skills"))) or
            (section_key == "projects" and data.get("projects")) or
            (section_key == "accomplishments" and data.get("accomplishments")) or
            (section_key == "summary" and data.get(section_key))):
            
            story.append(Spacer(1, 4))  # Reduced from Spacer(1, 6)
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=colors.grey,
                    spaceBefore=0,
                    spaceAfter=4,  # Reduced from 6
                )
            )

    doc.build(story)
    buffer.seek(0)
    return buffer

def display_pdf(file_bytes: bytes, file_name: str):
    base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
    pdf_display = f"""
    <iframe
        src="data:application/pdf;base64,{base64_pdf}"
        width="100%"
        height="506px"
        type="application/pdf"
    >
    </iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)

# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = {
        "name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "summary": "",
        "education": [],
        "experience": [],
        "technical_skills": "",
        "tools": "",
        "other_skills": "",
        "projects": [],
        "accomplishments": [],
    }

# Initialize skill categories
if 'skill_categories' not in st.session_state:
    st.session_state.skill_categories = {
        "Technical Skills": st.session_state.data.get("technical_skills", ""),
        "Tools & Technologies": st.session_state.data.get("tools", ""),
        "Other Skills": st.session_state.data.get("other_skills", "")
    }

# UI Layout
col1, col2, col3, col4, col5 = st.columns([0.2, 0.1, 0.1, 0.1, 0.5], gap="small")
with col1:
    st.image("./Static/logo.svg", width=140)
with col2:
    st.page_link("views/welcome.py", label="Home")
with col3:
    st.page_link("views/app.py", label="Builder")
with col4:
    st.page_link("views/ai.py", label="Enhancer")

builder, previewer = st.columns([0.6, 0.4], gap="large")

with builder:
    st.title("Builder")

    with st.container(border=True):
        current_step = sac.steps(
            items=[
                sac.StepsItem(title="Basic Info"),
                sac.StepsItem(title="Education"),
                sac.StepsItem(title="Experience"),
                sac.StepsItem(title="Skills & Projects"),
                sac.StepsItem(title="Generate PDF"),
            ],
            size="xs",
            return_index=True,
        )

    if current_step == 0:
        with st.form("basic_info_form"):
            st.subheader(":material/info: Basic Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("Full Name", st.session_state.data["name"])
            with col2:
                email = st.text_input("Email", st.session_state.data["email"])
            with col3:
                phone = st.text_input("Phone", st.session_state.data["phone"])

            col4, col5 = st.columns(2)
            with col4:
                linkedin = st.text_input("LinkedIn Link", st.session_state.data["linkedin"])
            with col5:
                github = st.text_input("GitHub Link", st.session_state.data["github"])

            summary = st.text_area("Personal Summary", st.session_state.data["summary"])
            
            st.subheader(":material/auto_awesome: AI-Generated Targeted Summary")
            job_description = st.text_area("Paste the job description here to generate a targeted summary", 
                                        placeholder="Paste the job description you're applying for...")
            
            col6, col7 = st.columns(2)
            with col6:
                generate_ai_summary = st.form_submit_button("Generate AI Summary")
            with col7:
                save_info = st.form_submit_button("Save & Continue")

            if generate_ai_summary and job_description:
                try:
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    prompt = f"""
                    Create a professional summary for a resume based on the following information:
                     
                    Job Description:
                    {job_description}
                    
                    Create a concise, targeted professional summary (3-4 sentences) that highlights the most relevant 
                    qualifications and experiences for this specific job. Focus on matching keywords and requirements 
                    from the job description.
                    """
                    response = model.generate_content(prompt)
                    ai_summary = response.text
                    st.session_state.data["ai_summary"] = ai_summary
                    st.toast("AI summary generated successfully!", icon="✨")
                except Exception as e:
                    st.error(f"Failed to generate AI summary: {str(e)}")
            
            if "ai_summary" in st.session_state.data:
                st.text_area("AI-Generated Summary", 
                            value=st.session_state.data["ai_summary"], 
                            key="ai_summary_display",height=300)

            if save_info:
                error = False
                if not name:
                    st.toast(":red-badge[:material/error: Please enter your full name.]")
                    error = True
                if not is_valid_email(email):
                    st.toast(":red-badge[:material/error: Please enter a valid email address.]")
                    error = True
                if not is_valid_phone(phone):
                    st.toast(":red-badge[:material/error: Please enter a valid phone number.]")
                    error = True
                if linkedin and not is_valid_url(linkedin):
                    st.toast(":red-badge[:material/error: Please enter a valid LinkedIn URL.]")
                    error = True
                if github and not is_valid_url(github):
                    st.toast(":red-badge[:material/error: Please enter a valid GitHub URL.]")
                    error = True

                if not error:
                    st.session_state.data.update({
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "linkedin": linkedin,
                        "github": github,
                        "summary": summary,
                    })
                    st.toast(":green-badge[:material/check: Basic information saved successfully!]")
                
    elif current_step == 1:
        st.subheader(":material/school: Education")
        
        for i, edu in enumerate(st.session_state.data["education"]):
            with st.expander(f"Education Entry {i+1}: {edu['school']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("School Name", value=edu["school"], key=f"school_{i}", disabled=True)
                    st.date_input(
                        "Start Date",
                        value=edu["timeline"][0],
                        key=f"start_date_{i}",
                        disabled=True
                    )
                with col2:
                    st.text_input("Course Name", value=edu["course"], key=f"course_{i}", disabled=True)
                    st.date_input(
                        "End Date",
                        value=edu["timeline"][1],
                        key=f"end_date_{i}",
                        disabled=True
                    )
                st.text_input("Grade point", value=edu["grade"], key=f"grade_{i}", disabled=True)
                
                if st.button("Delete Entry", key=f"delete_edu_{i}"):
                    st.session_state.data["education"].pop(i)
                    st.rerun()

        with st.form("education_form"):
            st.write("Add New Education Entry")
            col1, col2 = st.columns(2)
            with col1:
                school = st.text_input("School Name", key="new_school")
                start_date = st.date_input(
                    "Start Date",
                    min_value=datetime.date(1900, 1, 1),
                    max_value=datetime.date.today(),
                    key="new_start_date"
                )
            with col2:
                course = st.text_input("Course Name", key="new_course")
                end_date = st.date_input(
                    "End Date",
                    min_value=datetime.date(1900, 1, 1),
                    max_value=datetime.date(2100, 1, 1),
                    key="new_end_date"
                )
            grade = st.text_input("Grade (%)", key="new_grade")
            submit = st.form_submit_button("Add Education Entry")

            if submit:
                error = False
                if not school:
                    st.error("Please enter the school name.")
                    error = True
                if not course:
                    st.error("Please enter the course name.")
                    error = True
                if isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date):
                    if start_date >= end_date:
                        st.error("End date must be after start date.")
                        error = True
                if not grade:
                    st.error("Please enter a grade.")
                    error = True

                if not error:
                    new_edu = {
                        "school": school,
                        "course": course,
                        "timeline": (start_date, end_date),
                        "grade": grade,
                    }
                    st.session_state.data["education"].append(new_edu)
                    st.success("Education entry added successfully!")
                    st.rerun()

        if st.button("Continue Without Adding Education", use_container_width=True):
            st.toast("Continuing without education entries")

    elif current_step == 2:
        st.subheader(":material/work: Work Experience (Optional)")
        
        for i, exp in enumerate(st.session_state.data["experience"]):
            with st.expander(f"Experience Entry {i+1}: {exp['company']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Company Name", value=exp["company"], key=f"company_{i}", disabled=True)
                    st.date_input(
                        "Start Date",
                        value=exp["timeline"][0],
                        key=f"exp_start_date_{i}",
                        disabled=True
                    )
                with col2:
                    st.text_input("Role", value=exp["role"], key=f"role_{i}", disabled=True)
                    st.date_input(
                        "End Date",
                        value=exp["timeline"][1],
                        key=f"exp_end_date_{i}",
                        disabled=True
                    )
                st.text_area("Experience Summary", value=exp["experience_summary"], key=f"exp_summary_{i}", disabled=True)
                
                if st.button("Delete Entry", key=f"delete_exp_{i}"):
                    st.session_state.data["experience"].pop(i)
                    st.rerun()

        with st.form("experience_form"):
            st.write("Add New Experience Entry (Optional)")
            col1, col2 = st.columns(2)
            with col1:
                company = st.text_input("Company Name", key="new_company")
                start_date_c = st.date_input(
                    "Start Date",
                    min_value=datetime.date(1900, 1, 1),
                    max_value=datetime.date.today(),
                    key="new_exp_start_date"
                )
            with col2:
                role = st.text_input("Role", key="new_role")
                end_date_c = st.date_input(
                    "End Date",
                    min_value=datetime.date(1900, 1, 1),
                    max_value=datetime.date(2100, 1, 1),
                    key="new_exp_end_date"
                )
            experience_summary = st.text_area("Experience Summary (bullet points separated by new lines)", key="new_exp_summary")
            submit = st.form_submit_button("Add Experience Entry")

            if submit:
                error = False
                if company or role or experience_summary:
                    if not company:
                        st.error("Please enter the company name.")
                        error = True
                    if not role:
                        st.error("Please enter the role name.")
                        error = True
                    if isinstance(start_date_c, datetime.date) and isinstance(end_date_c, datetime.date):
                        if start_date_c >= end_date_c:
                            st.error("End date must be after start date.")
                            error = True
                    if not experience_summary:
                        st.error("Please add a summary (bullet points separated by new lines)")
                        error = True

                    if not error:
                        new_exp = {
                            "company": company,
                            "role": role,
                            "timeline": (start_date_c, end_date_c),
                            "experience_summary": experience_summary,
                        }
                        st.session_state.data["experience"].append(new_exp)
                        st.success("Experience entry added successfully!")
                        st.rerun()
                else:
                    st.toast("No experience added - continuing")

        if st.button("Continue Without Adding Experience", use_container_width=True):
            st.toast("Continuing without experience entries")

    elif current_step == 3:
        with st.expander("📝 Job Description (Required for AI Recommendations)", expanded=True):
            job_description = st.text_area(
                "Paste the job description here (this will be used for all AI recommendations)",
                value=st.session_state.get("job_description", ""),
                height=150,
                placeholder="Paste the complete job description here..."
            )
            if st.button("Save Job Description"):
                st.session_state.job_description = job_description
                st.toast("Job description saved!", icon="✅")

        st.subheader(":material/badge: Skills & Projects")
        st.write("### :material/auto_awesome: Skills")

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("#### Technical Skills")
            st.markdown("#### Tools & Technologies")
            st.markdown("#### Other Skills")

        with col2:
            technical_skills = st.text_area(
                "Programming languages, frameworks, etc.",
                value=st.session_state.skill_categories["Technical Skills"],
                height=100,
                placeholder="Python (pandas, NumPy), Java, JavaScript (React)",
                label_visibility="collapsed"
            )
            
            tools = st.text_area(
                "Software, tools, platforms",
                value=st.session_state.skill_categories["Tools & Technologies"],
                height=100,
                placeholder="Git, Docker, Tableau, AWS",
                label_visibility="collapsed"
            )
            
            other_skills = st.text_area(
                "Other relevant skills",
                value=st.session_state.skill_categories["Other Skills"],
                height=100,
                placeholder="Project Management, Agile Methodologies",
                label_visibility="collapsed"
            )

        if st.button("💾 Save All Skills"):
            st.session_state.skill_categories = {
                "Technical Skills": technical_skills,
                "Tools & Technologies": tools,
                "Other Skills": other_skills
            }
            st.session_state.data.update({
                "technical_skills": technical_skills,
                "tools": tools,
                "other_skills": other_skills
            })
            st.toast("Skills saved successfully!", icon="✅")

        with st.expander("🔍 AI Skill Recommendations (Based on Job Description)"):
            if st.button("Generate AI Recommendations"):
                if "job_description" in st.session_state and st.session_state.job_description:
                    try:
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        categories = {
                            "Technical Skills": "programming languages, frameworks, libraries, and technical competencies",
                            "Tools & Technologies": "software tools, platforms, and technologies",
                            "Other Skills": "soft skills, methodologies, and other relevant non-technical skills"
                        }
                        ai_recommendations = {}
                        for category, description in categories.items():
                            prompt = f"""
                            Based on this job description:
                            {st.session_state.job_description}
                            
                            Suggest specific {description} the candidate should highlight for the {category} section.
                            
                            Return only a bulleted list of the most relevant items, with no additional text.
                            Each item should be concise (3-5 words max).
                            """
                            response = model.generate_content(prompt)
                            ai_recommendations[category] = response.text
                        st.session_state.ai_skills = ai_recommendations
                        st.toast("AI skill recommendations generated!", icon="✨")
                    except Exception as e:
                        st.error(f"Error generating skills: {str(e)}")
                else:
                    st.warning("Please add and save a job description first")
            
            if "ai_skills" in st.session_state:
                st.write("#### Technical Skills Recommendations")
                st.text_area(
                    "Technical Skills AI Suggestions",
                    value=st.session_state.ai_skills.get("Technical Skills", ""),
                    height=100,
                    disabled=True,
                    label_visibility="collapsed"
                )
                
                st.write("#### Tools & Technologies Recommendations")
                st.text_area(
                    "Tools AI Suggestions",
                    value=st.session_state.ai_skills.get("Tools & Technologies", ""),
                    height=100,
                    disabled=True,
                    label_visibility="collapsed"
                )
                
                st.write("#### Other Skills Recommendations")
                st.text_area(
                    "Other Skills AI Suggestions",
                    value=st.session_state.ai_skills.get("Other Skills", ""),
                    height=100,
                    disabled=True,
                    label_visibility="collapsed"
                )
                
                if st.button("Apply All AI Recommendations"):
                    st.session_state.skill_categories = {
                        "Technical Skills": st.session_state.ai_skills.get("Technical Skills", ""),
                        "Tools & Technologies": st.session_state.ai_skills.get("Tools & Technologies", ""),
                        "Other Skills": st.session_state.ai_skills.get("Other Skills", "")
                    }
                    st.rerun()

        st.write("### :material/rocket: Projects")

        # Display existing projects
        for i, project in enumerate(st.session_state.data["projects"]):
            # Ensure each project is a dictionary
            if not isinstance(project, dict):
                st.session_state.data["projects"][i] = {"name": str(project)}
            
            with st.expander(f"Project {i+1}: {st.session_state.data['projects'][i].get('name', 'Untitled')}"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input(
                        "Project Name", 
                        value=st.session_state.data["projects"][i].get("name", ""), 
                        key=f"project_name_{i}"
                    )
                    year = st.text_input(
                        "Year", 
                        value=st.session_state.data["projects"][i].get("year", ""), 
                        key=f"project_year_{i}"
                    )
                with col2:
                    url = st.text_input(
                        "Project URL", 
                        value=st.session_state.data["projects"][i].get("url", ""), 
                        key=f"project_url_{i}"
                    )
                
                # AI description generation section
                if st.button("✨ Get AI Suggestions", key=f"ai_suggest_{i}"):
                    if name and "job_description" in st.session_state and st.session_state.job_description:
                        try:
                            model = genai.GenerativeModel('gemini-2.0-flash')
                            prompt = f"""
                            Based on this job description:
                            {st.session_state.job_description}
                            
                            Suggest 3 professional bullet points for a project called "{name}" that would be impressive for this role.
                            
                            Requirements:
                            - Each bullet point should start with a hyphen (-)
                            - First highlight technical aspects (languages, frameworks, tools used)
                            - Then mention business impact (performance improvements, cost savings, etc.)
                            - Keep each point under 2 lines
                            - Use action verbs (developed, implemented, optimized, etc.)
                            - Include metrics where possible
                            
                            Example format:
                            - Developed X using Y, resulting in Z% improvement
                            - Implemented A which reduced B by C%
                            - Optimized D process saving E hours per week
                            """
                            response = model.generate_content(prompt)
                            st.session_state[f"ai_suggestions_{i}"] = response.text
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating suggestions: {str(e)}")
                    else:
                        st.warning("Please enter a project name and save a job description first")
                
                # Display AI suggestions if available
                if f"ai_suggestions_{i}" in st.session_state:
                    st.subheader("AI Suggestions")
                    st.code(st.session_state[f"ai_suggestions_{i}"], language="text")
                    
                    if st.button("✅ Use These Suggestions", key=f"use_suggestions_{i}"):
                        st.session_state.data["projects"][i]["description"] = st.session_state[f"ai_suggestions_{i}"]
                        del st.session_state[f"ai_suggestions_{i}"]
                        st.rerun()
                    
                    if st.button("🗑️ Discard Suggestions", key=f"discard_suggestions_{i}"):
                        del st.session_state[f"ai_suggestions_{i}"]
                        st.rerun()
                
                description = st.text_area(
                    "Project Description (bullet points separated by new lines)", 
                    value=st.session_state.data["projects"][i].get("description", ""),
                    height=150,
                    key=f"project_desc_{i}",
                    help="Start each bullet point with '-' for proper formatting"
                )
                
                # Update the project data
                st.session_state.data["projects"][i] = {
                    "name": name,
                    "year": year,
                    "url": url,
                    "description": description
                }
                
                if st.button("Delete Project", key=f"delete_project_{i}"):
                    st.session_state.data["projects"].pop(i)
                    st.rerun()

        # Form for adding new project
        with st.form("project_form"):
            st.write("Add New Project")
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Project Name", key="new_project_name")
                new_year = st.text_input("Year", key="new_project_year")
            with col2:
                new_url = st.text_input("Project URL", key="new_project_url")
            new_description = st.text_area(
                "Project Description (bullet points separated by new lines)", 
                height=150,
                key="new_project_desc",
                help="Start each bullet point with '-' for proper formatting"
            )
            
            if st.form_submit_button("Add Project"):
                if new_name:
                    new_project = {
                        "name": new_name,
                        "year": new_year,
                        "url": new_url,
                        "description": new_description
                    }
                    st.session_state.data["projects"].append(new_project)
                    st.success("Project added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a project name")

        st.write("### :material/star: Accomplishments (Optional)")

        # Display existing accomplishments
        for i, acc in enumerate(st.session_state.data["accomplishments"]):
            # Ensure each accomplishment is a dictionary
            if not isinstance(acc, dict):
                st.session_state.data["accomplishments"][i] = {"title": str(acc)}
            
            with st.expander(f"{st.session_state.data['accomplishments'][i].get('title', 'Untitled')}"):
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input(
                        "Title", 
                        value=st.session_state.data["accomplishments"][i].get("title", ""), 
                        key=f"acc_title_{i}"
                    )
                    issuer = st.text_input(
                        "Issuer (for certifications)", 
                        value=st.session_state.data["accomplishments"][i].get("issuer", ""), 
                        key=f"acc_issuer_{i}"
                    )
                with col2:
                    url = st.text_input(
                        "URL", 
                        value=st.session_state.data["accomplishments"][i].get("url", ""), 
                        key=f"acc_url_{i}"
                    )
                    year = st.text_input(
                        "Year", 
                        value=st.session_state.data["accomplishments"][i].get("year", ""), 
                        key=f"acc_year_{i}"
                    )
                description = st.text_area(
                    "Description", 
                    value=st.session_state.data["accomplishments"][i].get("description", ""),
                    height=100,
                    key=f"acc_desc_{i}"
                )
                
                # Update the accomplishment data
                st.session_state.data["accomplishments"][i] = {
                    "title": title,
                    "issuer": issuer,
                    "url": url,
                    "year": year,
                    "description": description
                }
                
                if st.button("Delete", key=f"delete_acc_{i}"):
                    st.session_state.data["accomplishments"].pop(i)
                    st.rerun()

        # Form for adding new accomplishment/certification
        with st.form("accomplishment_form"):
            st.write("Add New Accomplishment/Certification (Optional)")
            col1, col2 = st.columns(2)
            with col1:
                new_title = st.text_input("Title", key="new_acc_title")
                new_issuer = st.text_input("Issuer (for certifications)", key="new_acc_issuer")
            with col2:
                new_url = st.text_input("URL", key="new_acc_url")
                new_year = st.text_input("Year", key="new_acc_year")
            new_description = st.text_area(
                "Description", 
                height=100,
                key="new_acc_desc"
            )
            
            if st.form_submit_button("Add"):
                if new_title:
                    new_acc = {
                        "title": new_title,
                        "issuer": new_issuer,
                        "url": new_url,
                        "year": new_year,
                        "description": new_description
                    }
                    st.session_state.data["accomplishments"].append(new_acc)
                    st.success("Added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a title")

    elif current_step == 4:
        st.subheader(":material/docs: Generate Resume PDF")
        if st.button(":material/docs: Generate PDF", key="generate_pdf_button", use_container_width=True):
            if not st.session_state.data["name"]:
                st.error("Please complete Basic Information first")
            else:
                with st.spinner("Generating PDF..."):
                    try:
                        pdf = generate_pdf(st.session_state.data)
                        st.download_button(
                            label=":material/download: Download PDF",
                            data=pdf,
                            file_name=f"{st.session_state.data['name']}_Resume.pdf",
                            mime="application/pdf",
                            key="download_pdf_button",
                            use_container_width=True,
                        )
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")

with previewer:
    st.title("Resume Preview")
    with st.container(border=True):
        if st.session_state.data.get("name"):
            try:
                pdf_buffer = generate_pdf(st.session_state.data)
                display_pdf(
                    pdf_buffer.getvalue(),
                    f"{st.session_state.data['name']}_Resume.pdf"
                )
            except Exception as e:
                st.warning("PDF preview unavailable. Please complete more fields.")