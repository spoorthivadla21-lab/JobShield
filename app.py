
import streamlit as st
import pandas as pd
import sqlite3
import json
import re
import requests
from datetime import datetime


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="JobShield | Job Safety Analyzer",
    page_icon="🔰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# LOGIN SESSION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

DB = "jobshield_history.db"

# =========================================================
# DATABASE
# =========================================================

def db():
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analyzed_at TEXT,
            analysis_type TEXT,
            title TEXT,
            company TEXT,
            salary TEXT,
            experience TEXT,
            location TEXT,
            email TEXT,
            url TEXT,
            source TEXT,
            platform TEXT,
            content TEXT,
            risk_score INTEGER,
            risk_level TEXT,
            findings TEXT,
            recommendations TEXT
        )
    """)
    con.commit()
    return con

db().close()

def save_history(kind, data, score, level, findings, recs):
    con = db()
    con.execute("""
        INSERT INTO history
        (analyzed_at,analysis_type,title,company,salary,experience,
        location,email,url,source,platform,content,risk_score,
        risk_level,findings,recommendations)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        datetime.now().strftime("%d %b %Y, %I:%M %p"),
        kind,
        data.get("title",""),
        data.get("company",""),
        data.get("salary",""),
        data.get("experience",""),
        data.get("location",""),
        data.get("email",""),
        data.get("url",""),
        data.get("source",""),
        data.get("platform",""),
        data.get("description",data.get("message","")),
        score,
        level,
        json.dumps(findings),
        json.dumps(recs)
    ))
    con.commit()
    con.close()

def get_history():
    con = db()
    df = pd.read_sql_query(
        "SELECT * FROM history ORDER BY id DESC", con
    )
    con.close()
    return df

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

*{
    font-family:Inter,sans-serif
}

.stApp{
    background:
    radial-gradient(circle at 5% 5%,#c9fff8,transparent 25%),
    radial-gradient(circle at 95% 5%,#cce7ff,transparent 28%),
    linear-gradient(135deg,#f5fdff,#eaf8ff,#f8fcff);
}

/* =========================================================
   DARK MODE TEXT VISIBILITY
   ========================================================= */

[data-theme="dark"] .stApp{
    color:#f5f7ff !important;
}

[data-theme="dark"] .stApp p,
[data-theme="dark"] .stApp span,
[data-theme="dark"] .stApp label,
[data-theme="dark"] .stApp h1,
[data-theme="dark"] .stApp h2,
[data-theme="dark"] .stApp h3,
[data-theme="dark"] .stApp h4,
[data-theme="dark"] .stApp h5,
[data-theme="dark"] .stApp h6{
    color:#f5f7ff !important;
}

[data-theme="dark"] [data-testid="stMarkdownContainer"] p,
[data-theme="dark"] [data-testid="stMarkdownContainer"] li{
    color:#e8ecf7 !important;
}

[data-theme="dark"] .feature-text{
    color:#d9e3ed !important;
}

[data-theme="dark"] .footer{
    color:#d0dbe5 !important;
}

[data-theme="dark"] .card,
[data-theme="dark"] .feature,
[data-theme="dark"] .history,
[data-theme="dark"] .risk{
    color:#f5f7ff !important;
}

[data-theme="dark"] .card p,
[data-theme="dark"] .feature p,
[data-theme="dark"] .risk p{
    color:#e8ecf7 !important;
}

[data-theme="dark"] input,
[data-theme="dark"] textarea{
    color:#ffffff !important;
    background-color:#172b3b !important;
}

[data-theme="dark"] input::placeholder,
[data-theme="dark"] textarea::placeholder{
    color:#b8c5d3 !important;
}

[data-theme="dark"] [data-baseweb="select"] *{
    color:#ffffff !important;
}

[data-theme="dark"] [data-testid="stMetricLabel"],
[data-theme="dark"] [data-testid="stMetricValue"],
[data-theme="dark"] [data-testid="stMetricDelta"]{
    color:#f5f7ff !important;
}

[data-theme="dark"] [data-testid="stExpander"]{
    color:#f5f7ff !important;
}

[data-theme="dark"] [data-testid="stExpander"] summary{
    color:#f5f7ff !important;
}

[data-theme="dark"] .stDataFrame{
    color:#ffffff !important;
}

[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#032f42,#075a70,#06394f);
}

[data-testid="stSidebar"] *{
    color:white!important
}

.logo{
    text-align:center;
    padding:10px 0 25px;
}

.logo-mark{
    width:75px;
    height:75px;
    margin:auto;
    border-radius:24px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:34px;
    font-weight:800;
    color:white;
    background:linear-gradient(145deg,#8affed,#20bcd1,#2477b9);
    box-shadow:0 15px 35px #20bcd155;
}

.logo-name{
    font-size:27px;
    font-weight:800;
    margin-top:10px;
}

.logo-sub{
    font-size:9px;
    letter-spacing:2px;
    opacity:.7;
}

.hero{
    padding:42px;
    border-radius:30px;
    color:white;
    background:linear-gradient(135deg,#04384c,#087f91,#08a8b8);
    box-shadow:0 20px 50px #06485c33;
    margin-bottom:25px;
}

.hero h1{
    font-size:42px;
    font-weight:800;
    margin:12px 0;
}

.hero p{
    max-width:850px;
    line-height:1.7;
    opacity:.9;
}

.badge{
    padding:8px 14px;
    border-radius:20px;
    background:#ffffff22;
    border:1px solid #ffffff33;
    font-size:11px;
}

.card,.feature,.history{
    background:#ffffffc9;
    border:1px solid #ffffff;
    border-radius:22px;
    padding:22px;
    box-shadow:0 12px 35px #07506412;
    backdrop-filter:blur(14px);
}

.feature{
    min-height:165px;
    margin-bottom:15px;
}

.feature-icon{
    font-size:30px
}

.feature-title{
    font-weight:800;
    font-size:17px;
    margin:9px 0;
}

.feature-text{
    color:#617984;
    font-size:13px;
    line-height:1.5;
}

.risk{
    text-align:center;
    padding:28px;
    border-radius:24px;
    background:#ffffffdd;
    box-shadow:0 15px 40px #00000012;
}

.score{
    font-size:64px;
    font-weight:800;
}

.stButton>button{
    border-radius:13px!important;
    min-height:44px!important;
    font-weight:700!important;
}

div[data-testid="stMetric"]{
    background:#ffffffb8;
    border-radius:17px;
    padding:14px;
}

.footer{
    text-align:center;
    padding:30px;
    color:#718993;
    font-size:12px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# ANALYSIS ENGINE
# =========================================================

def level(score):
    if score >= 70:
        return "HIGH RISK"
    if score >= 40:
        return "MEDIUM RISK"
    return "LOW RISK"

def add(findings, category, severity, evidence, why):
    findings.append({
        "Category":category,
        "Severity":severity,
        "Evidence":evidence,
        "Explanation":why
    })

def analyze(data):
    text = " ".join(str(data.get(x,"")) for x in [
        "title","company","salary","experience","location",
        "email","url","source","description","message"
    ]).lower()

    findings=[]
    score=0

    rules=[
        (r"registration fee|processing fee|application fee|joining fee|security deposit|training fee",
         "Payment Request","Critical",28,
         "Legitimate recruitment normally should not require candidates to pay money."),

        (r"upi|paytm|phonepe|google pay|gpay|bank transfer|crypto",
         "Payment Method","High",16,
         "Payment instructions should be independently verified."),

        (r"guaranteed job|guaranteed selection|100% selection|100% placement",
         "Guaranteed Promise","High",14,
         "Guaranteed selection claims can be used to pressure applicants."),

        (r"urgent hiring|apply immediately|limited vacancies|act now|today only|last chance",
         "Urgency","Medium",10,
         "Artificial urgency can pressure applicants into rushed decisions."),

        (r"easy money|get rich|earn.*huge|earn.*per day|work 1.?2 hours",
         "Unrealistic Promise","High",13,
         "Easy-money and unusually high-income claims need verification."),

        (r"otp|one time password|cvv|pin|atm pin|banking password|net banking password",
         "Sensitive Information","Critical",25,
         "Never share OTPs, PINs, CVVs or banking passwords."),

        (r"whatsapp only|telegram only|contact only on whatsapp|contact only on telegram",
         "Unusual Communication","Medium",9,
         "Exclusive informal communication deserves additional verification."),

        (r"aadhaar.*fee|pan.*fee|document.*fee",
         "Document Fee","High",15,
         "Charging candidates for document processing can be suspicious.")
    ]

    for pattern,cat,sev,points,why in rules:
        m=re.search(pattern,text)
        if m:
            add(findings,cat,sev,m.group(0),why)
            score+=points

    # EMAIL CHECK
    email=str(data.get("email","")).strip()

    if email and "@" in email:
        domain=email.split("@")[-1].lower()

        free={
            "gmail.com","yahoo.com","outlook.com",
            "hotmail.com","proton.me","protonmail.com"
        }

        if domain in free:
            add(
                findings,
                "Free Email Domain",
                "Medium",
                domain,
                "A free email domain does not prove fraud, but the employer should be verified."
            )
            score+=6

        company=str(data.get("company","")).lower()
        words=[
            x for x in re.findall(r"[a-zA-Z0-9]+",company)
            if len(x)>=4
        ]

        if words and not any(x in domain for x in words):
            add(
                findings,
                "Company / Email Mismatch",
                "Medium",
                email,
                "The email domain does not obviously match the stated company."
            )
            score+=8

    elif not email:
        add(
            findings,
            "Missing Recruiter Email",
            "Low",
            "Not provided",
            "Missing recruiter identity makes verification harder."
        )
        score+=3

    # URL CHECK
    url=str(data.get("url","")).strip()

    if url:
        if re.match(r"^https?://",url):
            try:
                r=requests.get(
                    url,
                    timeout=4,
                    allow_redirects=True,
                    headers={"User-Agent":"JobShield"}
                )

                if r.status_code>=400:
                    add(
                        findings,
                        "URL Check",
                        "Medium",
                        f"HTTP {r.status_code}",
                        "The supplied URL returned an error response."
                    )
                    score+=5
                else:
                    add(
                        findings,
                        "URL Check",
                        "Info",
                        f"HTTP {r.status_code}",
                        "The website responded, but reachability does not prove legitimacy."
                    )
            except:
                add(
                    findings,
                    "URL Check",
                    "Medium",
                    "Unable to connect",
                    "The URL could not be checked."
                )
                score+=4
        else:
            add(
                findings,
                "Invalid URL",
                "Medium",
                url,
                "The URL does not begin with HTTP or HTTPS."
            )
            score+=3

    # COMPANY
    if not str(data.get("company","")).strip():
        add(
            findings,
            "Missing Company",
            "Medium",
            "Company not provided",
            "A missing company identity makes verification difficult."
        )
        score+=7

    # DESCRIPTION
    desc=str(data.get("description","")).strip()

    if desc and len(desc)<80:
        add(
            findings,
            "Short Description",
            "Low",
            f"{len(desc)} characters",
            "Limited information makes verification harder."
        )
        score+=4

    # ROLE MISMATCH
    title=str(data.get("title","")).lower()
    exp=str(data.get("experience","")).lower()

    if any(x in title for x in ["senior","lead","manager","architect"]):
        if "fresher" in exp or "0 year" in exp or exp=="0":
            add(
                findings,
                "Role / Experience Mismatch",
                "Medium",
                f"{title} + {exp}",
                "The role level appears inconsistent with the experience requirement."
            )
            score+=8

    score=min(100,max(0,int(score)))
    risk=level(score)

    if risk=="HIGH RISK":
        recs=[
            "Do not pay registration, processing or training fees.",
            "Never share OTP, PIN, CVV or banking passwords.",
            "Verify the company using its official website.",
            "Independently verify the recruiter.",
            "Do not let urgency pressure you."
        ]
    elif risk=="MEDIUM RISK":
        recs=[
            "Verify the employer independently.",
            "Check the official careers page.",
            "Avoid sending money to recruiters.",
            "Do not share sensitive banking information."
        ]
    else:
        recs=[
            "Continue normal job-search precautions.",
            "Verify the employer before accepting an offer.",
            "Never share OTPs, PINs, CVVs or banking passwords."
        ]

    return score,risk,findings,recs

# =========================================================
# RESULT
# =========================================================

def show_result(score,risk,findings,recs):
    icon="🔴" if risk=="HIGH RISK" else "🟡" if risk=="MEDIUM RISK" else "🟢"

    st.markdown("## 🧠 JobShield Analysis")

    c1,c2,c3=st.columns([1,1,1.6])

    with c1:
        st.markdown(f"""
        <div class="risk">
            <div style="font-size:38px">{icon}</div>
            <div class="score">{score}</div>
            <div>out of 100</div>
            <h3>{risk}</h3>
        </div>
        """,unsafe_allow_html=True)

    with c2:
        st.metric("🚨 Warning Signals",len(findings))
        st.metric(
            "🛡️ Status",
            "Review Carefully" if score>=40 else "Lower Apparent Risk"
        )

    with c3:
        if score>=70:
            st.error("🚨 HIGH RISK\n\nMultiple suspicious indicators detected.")
        elif score>=40:
            st.warning("⚠️ MEDIUM RISK\n\nAdditional verification recommended.")
        else:
            st.success("✅ LOWER APPARENT RISK\n\nNo major warning pattern detected.")

    st.markdown("### 📊 Risk Signal Breakdown")

    if findings:
        chart=pd.Series([x["Category"] for x in findings]).value_counts()
        st.bar_chart(chart)
    else:
        st.info("No warning signals detected.")

    st.markdown("### 🔎 Why Was This Flagged?")

    for i,f in enumerate(findings,1):
        ic={
            "Critical":"🚨",
            "High":"🔴",
            "Medium":"🟡",
            "Low":"🟢",
            "Info":"ℹ️"
        }.get(f["Severity"],"⚠️")

        with st.expander(
            f"{ic} {i}. {f['Category']} — {f['Severity']}"
        ):
            st.write("**Evidence:**",f["Evidence"])
            st.write("**Why it matters:**",f["Explanation"])

    st.markdown("### 💡 Safety Recommendations")

    for r in recs:
        st.markdown(f"✅ {r}")

    report={
        "generated_at":datetime.now().isoformat(),
        "risk_score":score,
        "risk_level":risk,
        "warning_signals":findings,
        "recommendations":recs
    }

    st.download_button(
        "📥 Download Full Analysis Report",
        json.dumps(report,indent=4),
        "jobshield_report.json",
        "application/json",
        use_container_width=True
    )
# =======================================================
  # ADD HERE — LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:


    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 🔐 Login")

        username = st.text_input(
            "👤 Username",
            placeholder="Enter your username"
        )

        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="Enter your password"
        )

        if st.button("🔐 LOGIN", use_container_width=True):

            if username.strip() and password.strip():
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.success("✅ Login successful!")
                st.rerun()

            else:
                st.error("⚠️ Please enter a username and password.")

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("""
    <div class="logo">
        <div class="logo-mark">JS</div>
        <div class="logo-name">JobShield</div>
        <div class="logo-sub">JOB SAFETY ANALYZER</div>
    </div>
    """,unsafe_allow_html=True)

    st.divider()

    page=st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🔍 Analyze a Job",
            "💬 Recruiter Message",
            "📜 Analysis History",
            "⚙️ How It Works",
            "ℹ️ About & Limitations"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("🔰 Verify before you trust.")
    st.caption("Risk assessment is not a guarantee.")
# =====================================================
    # 🔴 ADD HERE — LOGOUT
    # =====================================================

    st.divider()

    st.write(
        f"👤 Logged in as: **{st.session_state.username}**"
    )

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
# =========================================================
# DASHBOARD
# =========================================================

if page=="🏠 Dashboard":

    st.markdown("""
    <div class="hero">
        <span class="badge">AI-ASSISTED • SCAM DETECTION • JOB SAFETY</span>
        <h1>Verify Before You Apply.</h1>
        <p>
        JobShield analyzes job postings and recruiter messages
        for suspicious patterns including payment requests,
        urgency, unrealistic promises, sensitive information,
        email mismatches and suspicious communication.
        </p>
    </div>
    """,unsafe_allow_html=True)

    history=get_history()

    a,b,c,d=st.columns(4)

    a.metric("🔎 Total Analyses",len(history))

    b.metric(
        "🔴 High Risk",
        int((history["risk_level"]=="HIGH RISK").sum())
        if not history.empty else 0
    )

    c.metric(
        "🟡 Medium Risk",
        int((history["risk_level"]=="MEDIUM RISK").sum())
        if not history.empty else 0
    )

    d.metric(
        "🟢 Low Risk",
        int((history["risk_level"]=="LOW RISK").sum())
        if not history.empty else 0
    )

    st.markdown("### ✨ JobShield Features")

    features=[
        ("🔰","Smart Risk Score","Transparent 0–100 risk scoring."),
        ("🚨","Scam Detection","Detect fees, urgency and suspicious promises."),
        ("🧠","Explainable Analysis","Shows exactly why something was flagged."),
        ("📜","Detailed History","Stores every analysis and its complete details."),
        ("📧","Email Check","Checks free domains and company mismatch."),
        ("🔗","URL Check","Performs basic website reachability checking."),
        ("🇮🇳","India Scam Signals","Detects UPI and common payment indicators."),
        ("📥","Reports","Download analysis reports.")
    ]

    cols=st.columns(4)

    for col,(ic,title,desc) in zip(cols,features):
        with col:
            st.markdown(f"""
            <div class="feature">
                <div class="feature-icon">{ic}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-text">{desc}</div>
            </div>
            """,unsafe_allow_html=True)

    if not history.empty:
        st.markdown("### 🕘 Recent Activity")
        st.dataframe(
            history[
                ["analyzed_at","title","company",
                 "analysis_type","risk_score","risk_level"]
            ].head(5),
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# JOB ANALYSIS
# =========================================================

elif page=="🔍 Analyze a Job":

    st.markdown("## 🔍 Analyze a Job Posting")
    st.caption("Enter as much information as possible for a stronger analysis.")

    with st.form("job_form"):

        c1,c2=st.columns(2)

        with c1:
            title=st.text_input("💼 Job Title")
            company=st.text_input("🏢 Company")
            salary=st.text_input("💰 Salary")
            experience=st.text_input("🎓 Experience")

        with c2:
            location=st.text_input("📍 Location")
            email=st.text_input("📧 Recruiter Email")
            url=st.text_input("🔗 Job URL")
            source=st.selectbox(
                "🌐 Job Source",
                ["LinkedIn","Naukri","Indeed",
                 "Company Website","WhatsApp",
                 "Telegram","Other"]
            )

        description=st.text_area(
            "📝 Full Job Description",
            height=220
        )

        submit=st.form_submit_button(
            "🛡️ ANALYZE JOB NOW",
            use_container_width=True
        )

    if submit:
        if not title and not description:
            st.warning("Please enter a job title or description.")
        else:
            data={
                "title":title,
                "company":company,
                "salary":salary,
                "experience":experience,
                "location":location,
                "email":email,
                "url":url,
                "source":source,
                "description":description
            }

            score,risk,findings,recs=analyze(data)

            save_history(
                "Job Posting",
                data,
                score,
                risk,
                findings,
                recs
            )

            st.toast(
                f"Analysis complete: {score}/100",
                icon="🔰"
            )

            show_result(score,risk,findings,recs)

# =========================================================
# MESSAGE ANALYSIS
# =========================================================

elif page=="💬 Recruiter Message":

    st.markdown("## 💬 Recruiter Message Analyzer")
    st.caption("Check a recruiter message before replying or sharing information.")

    platform=st.selectbox(
        "📱 Where did you receive it?",
        ["WhatsApp","Telegram","Email",
         "SMS","LinkedIn","Other"]
    )

    message=st.text_area(
        "💬 Paste Recruiter Message",
        height=280,
        placeholder="Paste the complete message here..."
    )

    if st.button(
        "🔎 ANALYZE MESSAGE",
        use_container_width=True
    ):

        if not message.strip():
            st.warning("Please paste a message first.")
        else:
            data={
                "title":"Recruiter Message",
                "source":platform,
                "platform":platform,
                "description":message
            }

            score,risk,findings,recs=analyze(data)

            save_history(
                "Recruiter Message",
                data,
                score,
                risk,
                findings,
                recs
            )

            st.toast(
                f"Message analyzed: {score}/100",
                icon="💬"
            )

            show_result(score,risk,findings,recs)

# =========================================================
# HISTORY
# =========================================================

elif page=="📜 Analysis History":

    st.markdown("## 📜 Analysis History")
    st.caption("Every previous analysis is stored with its complete details.")

    history=get_history()

    if history.empty:
        st.info("📭 No analysis history yet.")
    else:

        a,b,c,d=st.columns(4)

        a.metric("🔎 Total",len(history))
        b.metric("🔴 High",int((history.risk_level=="HIGH RISK").sum()))
        c.metric("🟡 Medium",int((history.risk_level=="MEDIUM RISK").sum()))
        d.metric("🟢 Low",int((history.risk_level=="LOW RISK").sum()))

        st.divider()

        search=st.text_input(
            "🔎 Search",
            placeholder="Search title, company, email or content..."
        )

        risk_filter=st.selectbox(
            "🎯 Risk Filter",
            ["All","HIGH RISK","MEDIUM RISK","LOW RISK"]
        )

        filtered=history.copy()

        if search:
            mask=False

            for col in ["title","company","email","content"]:
                mask=mask|filtered[col].fillna("").str.contains(
                    search,case=False,na=False
                )

            filtered=filtered[mask]

        if risk_filter!="All":
            filtered=filtered[
                filtered.risk_level==risk_filter
            ]

        st.write(f"**{len(filtered)} record(s) found**")

        for _,row in filtered.iterrows():

            icon="🔴" if row.risk_level=="HIGH RISK" else \
                 "🟡" if row.risk_level=="MEDIUM RISK" else "🟢"

            name=row.title or "Untitled Analysis"

            with st.expander(
                f"{icon} {name}  |  {row.risk_score}/100  |  {row.analyzed_at}"
            ):

                a,b,c=st.columns(3)

                a.metric("Risk Score",f"{row.risk_score}/100")
                b.metric("Risk Level",row.risk_level)
                c.metric("Type",row.analysis_type)

                st.markdown("### 📌 Complete Details")

                details=pd.DataFrame([
                    ["Job Title",row.title],
                    ["Company",row.company],
                    ["Salary",row.salary],
                    ["Experience",row.experience],
                    ["Location",row.location],
                    ["Recruiter Email",row.email],
                    ["Job URL",row.url],
                    ["Source",row.source],
                    ["Platform",row.platform],
                    ["Analysis Date",row.analyzed_at]
                ],columns=["Field","Information"])

                st.dataframe(
                    details,
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("### 📝 Original Job / Message")

                st.text_area(
                    "Original Content",
                    row.content or "",
                    height=180,
                    disabled=True,
                    key=f"content_{row.id}",
                    label_visibility="collapsed"
                )

                findings=json.loads(row.findings or "[]")
                recs=json.loads(row.recommendations or "[]")

                st.markdown("### 🚨 Warning Signals")

                if findings:
                    st.dataframe(
                        pd.DataFrame(findings),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.success("No warning signals detected.")

                st.markdown("### 💡 Recommendations")

                for r in recs:
                    st.markdown(f"✅ {r}")

                if st.button(
                    "🗑️ Delete This Analysis",
                    key=f"delete_{row.id}"
                ):
                    con=db()
                    con.execute(
                        "DELETE FROM history WHERE id=?",
                        (int(row.id),)
                    )
                    con.commit()
                    con.close()
                    st.rerun()

        st.divider()

        if st.button(
            "🗑️ CLEAR ALL HISTORY",
            use_container_width=True
        ):
            con=db()
            con.execute("DELETE FROM history")
            con.commit()
            con.close()
            st.success("All history cleared.")
            st.rerun()

# =========================================================
# HOW IT WORKS
# =========================================================

elif page=="⚙️ How It Works":

    st.markdown("## ⚙️ How JobShield Works")

    steps=[
        ("01","📥 INPUT","User enters a job posting or recruiter message."),
        ("02","🧹 TEXT ANALYSIS","JobShield examines the supplied information."),
        ("03","🔎 SIGNAL DETECTION","Suspicious patterns are identified."),
        ("04","📊 RISK SCORING","Signals are converted into a 0–100 score."),
        ("05","🧠 EXPLANATION","The system explains every warning."),
        ("06","🛡️ RECOMMENDATION","Safety actions are provided.")
    ]

    for no,title,desc in steps:
        st.markdown(f"""
        <div class="card" style="margin-bottom:12px">
            <b style="font-size:24px;color:#079aaa">{no}</b>
            <span style="font-size:18px;font-weight:800;margin-left:20px">
                {title}
            </span>
            <p style="color:#607b85;margin-left:50px">{desc}</p>
        </div>
        """,unsafe_allow_html=True)

    st.markdown("### 🔎 Detection Categories")

    detection=[
        "Payment Requests",
        "UPI / Payment Apps",
        "Urgency",
        "Guaranteed Selection",
        "Unrealistic Income",
        "OTP / PIN / CVV Requests",
        "Email Domain",
        "Company / Email Mismatch",
        "URL Reachability",
        "Indian Scam Indicators",
        "Role / Experience Contradictions"
    ]

    cols=st.columns(3)

    for i,item in enumerate(detection):
        cols[i%3].success("✓ "+item)

# =========================================================
# ABOUT
# =========================================================

else:

    st.markdown("## ℹ️ About & Limitations")

    st.markdown("""
    <div class="card">
        <h2>🔰 JobShield</h2>
        <p>
        JobShield is a job-safety analysis system designed to
        help job seekers identify suspicious patterns in job
        postings and recruiter messages.
        </p>
        <p>
        It combines text pattern detection, contextual checks,
        risk scoring, explanations and safety recommendations.
        </p>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("### 🚀 Main Features")

    features=[
        "Job posting analysis",
        "Recruiter message analysis",
        "0–100 risk scoring",
        "Explainable warning signals",
        "Detailed persistent history",
        "Search and risk filtering",
        "Email analysis",
        "URL checking",
        "Indian scam indicators",
        "Downloadable reports",
        "SQLite database"
    ]

    for x in features:
        st.markdown("✅ "+x)

    st.markdown("### ⚠️ Limitations")

    limits=[
        "A high score is not absolute proof of fraud.",
        "A low score does not guarantee a genuine job.",
        "A reachable website does not prove legitimacy.",
        "A free email address does not automatically mean fraud.",
        "Sophisticated scams may not be detected.",
        "Users should independently verify companies and recruiters."
    ]

    for x in limits:
        st.markdown("• "+x)

    st.warning(
        "🔐 Never share OTPs, PINs, CVVs or banking passwords with recruiters."
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
🔰 JobShield — Job Safety Analyzer<br>
Verify before you trust • Stay alert • Stay safe
</div>
""",unsafe_allow_html=True)
