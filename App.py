import streamlit as st
import nltk
import spacy
nltk.download('stopwords')
spacy.load('en_core_web_sm')

import pandas as pd
import base64, random
import time, datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io, random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import pafy
import plotly.express as px
import youtube_dl

def fetch_yt_video(link):
    video = pafy.new(link)
    return video.title


def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


connection = pymysql.connect(
    host='localhost',
    user='root',
    password='sowmya123',   # ✅ correct
    database='sra'
)
cursor = connection.cursor()


def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills,
                courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (
    name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills,
    courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon='./Logo/bee_logo.png',
)

st.markdown("""
<style>

/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #1A1A1A;  /* dark but softer than black */
}

/* Sidebar text */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    color: #FFFFFF !important;
}

/* Selectbox */
section[data-testid="stSidebar"] .stSelectbox div {
    background-color: #FFF3CC !important;
    color: black !important;
    border-radius: 8px;
}

/* Dropdown text */
section[data-testid="stSidebar"] .stSelectbox span {
    color: black !important;
}

/* Hover fix */
section[data-testid="stSidebar"] .stSelectbox div:hover {
    background-color: #FFE08A !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #FFF9E6;
}

/* Title */
h1, h2, h3 {
    color: #222222;
    text-align: center;
}

/* Buttons */
.stButton>button {
    background-color: #FFC83D;
    color: black;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
}
.stButton>button:hover {
    background-color: #ffb700;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #222222;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Selectbox */
.stSelectbox div {
    background-color: #FFF3CC !important;
}

/* Cards effect */
.block-container {
    padding: 2rem;
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)
# Place this immediately after st.set_page_config()
from PIL import Image
import streamlit as st

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf(data, filename="resume_report.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Smart Resume Analysis Report 🐝", styles['Title']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Name: {data['name']}", styles['Normal']))
    content.append(Paragraph(f"Email: {data['email']}", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Resume Score: {data['score']}", styles['Normal']))
    content.append(Paragraph(f"ATS Score: {data['ats']}", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Skills:", styles['Heading2']))
    content.append(Paragraph(data['skills'], styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Missing Skills:", styles['Heading2']))
    content.append(Paragraph(data['missing'], styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Sections Found:", styles['Heading2']))
    content.append(Paragraph(data['sections_found'], styles['Normal']))

    content.append(Paragraph("Sections Missing:", styles['Heading2']))
    content.append(Paragraph(data['sections_missing'], styles['Normal']))

    doc.build(content)

    return filename
def run():
    st.markdown(
    "<h1>🐝 <span style='color:#FFC83D;'>Smart Resume</span> Analyzer</h1>",
    unsafe_allow_html=True
    )

    

    img = Image.open('Logo/bee_logo.png')
    st.image(img, width=200)

    st.markdown(
    """
    <div style="background-color:#FFF3CC; padding:15px; border-radius:10px;">
        <h3 style="color:#222;">Upload your resume and get smart insights 🚀</h3>
    </div>
    """,
    unsafe_allow_html=True
    )
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
   # img = Image.open('./Logo/SRA_Logo.jpg')
    img = img.resize((250, 250))
    #st.image(img)
    

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    cursor.execute(db_sql)
    connection.select_db("sra")

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(100) NOT NULL,
                     Email_ID VARCHAR(50) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field VARCHAR(25) NOT NULL,
                     User_level VARCHAR(30) NOT NULL,
                     Actual_skills VARCHAR(300) NOT NULL,
                     Recommended_skills VARCHAR(300) NOT NULL,
                     Recommended_courses VARCHAR(600) NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    if choice == 'Normal User':
        # st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Upload your resume, and get smart recommendation based on it."</h4>''',
        #             unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            # with st.spinner('Uploading your Resume....'):
            #     time.sleep(4)
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            import re

            resume_text = pdf_reader(save_image_path)
            resume_text = pdf_reader(save_image_path)

            # 👇 ADD HERE
            lines = resume_text.strip().split('\n')

            for line in lines:
                line = line.strip()

                if len(line) < 3:
                    continue
                if "@" in line:
                    continue
                if any(word in line.lower() for word in [
                    "data scientist", "developer", "engineer", "resume", "cv", "profile"
                ]):
                    continue
                
                words=line.split()
                if 1 <=len(words) <= 3 and all(word.isalpha() for word in words):
                    resume_data['name'] = line
                    break
            import re

            # -------- FIX EMAIL --------
            email_match = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text)
            if email_match:
                resume_data['email'] = email_match[0]
            else:
                resume_data['email'] = "Not Found"

            # -------- FIX NAME --------
            if not resume_data.get('name') or resume_data['name'] == "Email":
                lines = resume_text.strip().split('\n')
            for line in lines:
                if len(line.strip()) > 2:
                    resume_data['name'] = line.strip()
                    break
            # Fix email
            email_match = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text)
            if email_match:
                resume_data['email'] = email_match[0]

            # Fix name (basic fallback)
            if not resume_data.get('name'):
                resume_data['name'] = resume_text.split('\n')[0]
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)
                st.subheader("📑 Resume Section Analysis")

                sections = ["objective", "skills", "education", "projects", "experience"]

                found_sections = []
                missing_sections = []

                for sec in sections:
                    if sec in resume_text.lower():
                        found_sections.append(sec.capitalize())
                    else:
                        missing_sections.append(sec.capitalize())

                st.success(f"✅ Found Sections: {', '.join(found_sections)}")

                if missing_sections:
                    st.warning(f"❌ Missing Sections: {', '.join(missing_sections)}")
                st.subheader("📄 Job Description")
                job_desc = st.text_area("Paste Job Description here")
                ats_score = "N/A"
                missing_skills = []
                from sklearn.feature_extraction.text import CountVectorizer
                from sklearn.metrics.pairwise import cosine_similarity

                def calculate_ats(resume_text, job_desc):
                    text = [resume_text, job_desc]
                    cv = CountVectorizer().fit_transform(text)
                    score = cosine_similarity(cv)[0][1]
                    return round(score * 100, 2)
                
                if job_desc:
                    ats_score = calculate_ats(resume_text, job_desc)

                    st.subheader("📊 ATS Match Score")
                    st.progress(int(ats_score))
                    st.success(f"Your resume matches {ats_score}% with the job description")
                    # -------- SKILL GAP ANALYSIS --------
                    resume_words = set(resume_text.lower().split())
                    job_words = set(job_desc.lower().split())

                    # Common tech skills list (you can expand later)
                    skills_list = [
                        "python", "sql", "machine learning", "aws", "tensorflow",
                        "pytorch", "data analysis", "excel", "power bi", "tableau",
                        "java", "c++", "javascript", "react", "node", "django"
                    ]

                    missing_skills = []

                    for skill in skills_list:
                        if skill in job_words and skill not in resume_words:
                            missing_skills.append(skill)
                    st.subheader("❌ Skill Gap Analysis")

                    if missing_skills:
                        st.warning(f"You are missing: {', '.join(missing_skills)}")
                    else:
                        st.success("✅ Your resume matches most required skills!")
                import spacy

                nlp = spacy.load("en_core_web_sm")
                doc = nlp(resume_text)

                name_found = None

                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        name_found = ent.text
                        break

                if name_found:
                    resume_data['name'] = name_found

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',
                                unsafe_allow_html=True)

                st.subheader("**Skills Recommendation💡**")
                ## Skill shows
                keywords = st_tags(label='### Skills that you have',
                                   text='See our skills recommendation',
                                   value=resume_data['skills'], key='1')

                ##  recommendation
                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask',
                              'streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                                'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro',
                                'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                                'user research', 'user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                ## Courses recommendation
                for i in resume_data['skills']:
                    ## Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                              'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                              'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                                              'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                              'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='2')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                              'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='3')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                              'Kivy', 'GIT', 'SDK', 'SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='4')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                              'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                              'Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='5')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    ## Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq',
                                              'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing',
                                              'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe',
                                              'Solid', 'Grasp', 'User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                       text='Recommended skills generated from System',
                                                       value=recommended_skills, key='6')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                #
                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                ### Resume writing recommendation
                st.subheader("**Resume Tips & Ideas💡**")
                resume_score = 0

                sections = {
                "Objective": 15,
                "Declaration": 10,
                "Hobbies": 10,
                "Achievements": 15,
                "Projects": 20,
                "Skills": 15,
                "Education": 15
                }

                missing_sections = []

                for section, marks in sections.items():
                    if section.lower() in resume_text.lower():
                        resume_score += marks
                    else:
                        missing_sections.append(section)

                # Show feedback
                if missing_sections:
                    st.warning(f"Add these sections to improve your resume: {', '.join(missing_sections)}")
                else:
                    st.success("Great! Your resume covers all key sections.")

                
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('** Your Resume Writing Score: ' + str(score) + '**')
                st.warning(
                    "** Note: This score is calculated based on the content that you have added in your Resume. **")
                st.balloons()

                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                            str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                            str(recommended_skills), str(rec_course))

                ## Resume writing video
                #st.header("**Bonus Video for Resume Writing Tips💡**")
                #resume_vid = random.choice(resume_videos)
                #res_vid_title = fetch_yt_video(resume_vid)
                #st.subheader("✅ **" + res_vid_title + "**")
                #st.video(resume_vid)

                ## Interview Preparation Video
                #st.header("**Bonus Video for Interview👨‍💼 Tips💡**")
                #interview_vid = random.choice(interview_videos)
                #int_vid_title = fetch_yt_video(interview_vid)
                #st.subheader("✅ **" + int_vid_title + "**")
                #st.video(interview_vid)

                connection.commit()
                # -------- SAFE DEFAULTS --------
                ats_score = ats_score if 'ats_score' in locals() else "N/A"
                missing_skills = missing_skills if 'missing_skills' in locals() else []
                skills = resume_data.get('skills', [])
                found_sections = found_sections if 'found_sections' in locals() else []
                missing_sections = missing_sections if 'missing_sections' in locals() else []

                # -------- REPORT --------
                report = f"""
                Resume Analysis Report

                Name: {resume_data.get('name', 'N/A')}
                Email: {resume_data.get('email', 'N/A')}

                Resume Score: {resume_score}
                ATS Score: {ats_score}

                Skills:
                {', '.join(skills) if skills else 'None'}

                Missing Skills:
                {', '.join(missing_skills) if missing_skills else 'None'}

                Sections Found:
                {', '.join(found_sections) if found_sections else 'None'}

                Sections Missing:
                {', '.join(missing_sections) if missing_sections else 'None'}
                """

                # -------- DOWNLOAD BUTTON --------
                st.subheader("📥 Download Your Report")

                # 🟢 Prepare data for PDF
            data = {
                "name": resume_data.get('name', 'N/A'),
                "email": resume_data.get('email', 'N/A'),
                "score": str(resume_score),
                "ats": str(ats_score),
                "skills": ", ".join(skills) if skills else "None",
                "missing": ", ".join(missing_skills) if missing_skills else "None",
                "sections_found": ", ".join(found_sections) if found_sections else "None",
                "sections_missing": ", ".join(missing_sections) if missing_sections else "None"
            }

            # 🟢 PDF Download Button
            if st.button("📄 Generate PDF Report"):
                file_path = create_pdf(data)

                with open(file_path, "rb") as f:
                    st.download_button(
                    label="⬇️ Download PDF",
                    data=f,
                    file_name="resume_report.pdf",
                    mime="application/pdf"
                    )
            
    else:
        ## Admin Side
        st.success('Welcome to Admin Side')
        # st.sidebar.subheader('**ID / Password Required!**')

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'sowmyasai' and ad_password == 'sowmya123':
                st.success(f"Welcome {ad_user}")
                # Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's👨‍💻 Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)

                ## Pie chart for predicted field recommendations
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader("📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                ### Pie chart for User's👨‍💻 Experienced Level
                labels = plot_data.User_level.unique()
                values = plot_data.User_level.value_counts()
                st.subheader("📈 ** Pie-Chart for User's👨‍💻 Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)


            else:
                st.error("Wrong ID & Password Provided")

run()
