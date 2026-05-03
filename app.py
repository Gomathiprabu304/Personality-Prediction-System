import streamlit as st
import pdfplumber
import docx
import re

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Personality Prediction from CV",
    page_icon="🧠",
    layout="centered"
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 28px;
        font-weight: 700;
        color: #4A4AE8;
        text-align: center;
        margin-bottom: 4px;
    }
    .sub-title {
        font-size: 14px;
        color: #888;
        text-align: center;
        margin-bottom: 30px;
    }
    .trait-card {
        background: #f9f9ff;
        border-left: 5px solid;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    .trait-name {
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 2px;
    }
    .trait-meaning {
        font-size: 13px;
        color: #666;
        margin-bottom: 10px;
    }
    .score-number {
        font-size: 32px;
        font-weight: 800;
    }
    .tip-box {
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        margin-top: 10px;
        line-height: 1.6;
    }
    .career-box {
        background: #f0f4ff;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
    .career-chip {
        display: inline-block;
        background: #4A4AE8;
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 13px;
        margin: 4px;
    }
    .verdict-box {
        background: #fff8e1;
        border-left: 5px solid #FFC107;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 20px;
        font-size: 14px;
        line-height: 1.8;
    }
    .section-head {
        font-size: 18px;
        font-weight: 700;
        color: #333;
        margin: 30px 0 12px;
        border-bottom: 2px solid #eee;
        padding-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TRAIT CONFIG
# ─────────────────────────────────────────────
TRAITS = {
    "Openness": {
        "emoji": "🎨",
        "color": "#7C3AED",
        "meaning": "How creative and curious you are",
        "keywords": [
            "creative", "innovative", "design", "explore", "research",
            "curious", "art", "idea", "invention", "experiment",
            "learning", "develop", "build", "imagine", "vision"
        ],
        "improve": [
            "📚 Read books or watch videos on new topics every week.",
            "🎯 Try one new skill every month — coding, design, music, anything.",
            "💡 Add personal projects or side work to your CV.",
            "🌍 Travel or explore new places to expand your thinking.",
        ],
        "strength": [
            "✅ Highlight creative projects prominently in your CV.",
            "✅ Apply for roles in tech, design, research, or startups.",
            "✅ Mention any new tools or skills you have learned recently.",
        ]
    },
    "Conscientiousness": {
        "emoji": "📋",
        "color": "#059669",
        "meaning": "How organised and hardworking you are",
        "keywords": [
            "organised", "deadline", "managed", "planned", "achieved",
            "delivered", "completed", "responsible", "systematic", "goal",
            "schedule", "efficient", "disciplined", "accurate", "detail"
        ],
        "improve": [
            "📝 Use a daily to-do list app like Notion or Todoist.",
            "🎯 Set weekly goals and track them every Sunday.",
            "🏆 Add exact numbers in CV — 'completed 5 projects on time'.",
            "👥 Take leadership roles in college or internship projects.",
        ],
        "strength": [
            "✅ You are reliable — mention this clearly in your CV.",
            "✅ Apply for roles like Project Manager, Team Lead, or Analyst.",
            "✅ Show your achievements with numbers and results.",
        ]
    },
    "Extraversion": {
        "emoji": "🗣️",
        "color": "#2563EB",
        "meaning": "How social and outgoing you are",
        "keywords": [
            "led", "presented", "communicated", "team", "event",
            "leadership", "coordinated", "organized", "spoke", "conference",
            "group", "public", "networking", "community", "club"
        ],
        "improve": [
            "🪞 Practice speaking in front of a mirror for 5 minutes daily.",
            "🎤 Join a college club or public speaking group.",
            "💬 Prepare 3 short stories about yourself before interviews.",
            "👋 Try to start one new conversation every day.",
        ],
        "strength": [
            "✅ Apply for sales, HR, marketing, or client-facing roles.",
            "✅ Mention teamwork, events organized, or people managed.",
            "✅ Your social skills are an advantage — show them in interviews.",
        ]
    },
    "Agreeableness": {
        "emoji": "🤝",
        "color": "#D97706",
        "meaning": "How kind and cooperative you are",
        "keywords": [
            "helped", "collaborated", "supported", "volunteer", "mentored",
            "assisted", "cooperated", "team player", "empathy", "care",
            "contributed", "shared", "listened", "guided", "taught"
        ],
        "improve": [
            "👂 Practice active listening — focus fully when others speak.",
            "🙌 Volunteer to help teammates or juniors with their work.",
            "📖 Add group projects and collaborations to your CV.",
            "😊 Be the person who resolves conflicts calmly in a team.",
        ],
        "strength": [
            "✅ You are a natural team player — highlight group achievements.",
            "✅ Roles in HR, counselling, teaching, and management suit you.",
            "✅ Mention volunteer work or community service in your CV.",
        ]
    },
    "Emotional Stability": {
        "emoji": "🧘",
        "color": "#B45309",
        "meaning": "How calm you are under pressure",
        "keywords": [
            "calm", "handled", "resolved", "adapted", "stable",
            "pressure", "challenge", "overcome", "resilient", "patient",
            "balanced", "focused", "composed", "steady", "managed stress"
        ],
        "improve": [
            "🚶 Take a 10-minute walk every day — it reduces stress naturally.",
            "📓 Write your feelings in a diary — it clears your mind.",
            "😴 Sleep 7 to 8 hours daily — poor sleep causes stress at work.",
            "🧠 When facing a problem, break it into 3 small steps and solve one at a time.",
        ],
        "strength": [
            "✅ You handle pressure well — mention challenging situations you overcame.",
            "✅ Apply for high-pressure roles like doctor, engineer, or manager.",
            "✅ Your calmness makes you a reliable team member during tough times.",
        ]
    }
}

CAREER_MAP = {
    ("Openness", "Conscientiousness"): ["Software Developer", "Data Scientist", "Research Analyst", "Product Manager"],
    ("Openness", "Extraversion"):      ["UX Designer", "Marketing Manager", "Content Strategist", "Entrepreneur"],
    ("Conscientiousness", "Agreeableness"): ["HR Manager", "Teacher", "Social Worker", "Operations Manager"],
    ("Extraversion", "Agreeableness"):  ["Sales Executive", "Public Relations", "Event Manager", "Counsellor"],
    ("Emotional Stability", "Conscientiousness"): ["Financial Analyst", "Doctor", "Engineer", "Project Manager"],
}

# ─────────────────────────────────────────────
#  FUNCTIONS
# ─────────────────────────────────────────────
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + " "
    return text

def read_docx(file):
    doc = docx.Document(file)
    return " ".join([p.text for p in doc.paragraphs])

def get_scores(text):
    text_lower = text.lower()
    scores = {}
    for trait, data in TRAITS.items():
        found = sum(1 for w in data["keywords"] if w in text_lower)
        raw = (found / len(data["keywords"])) * 100
        # Scale so even 4-5 keyword hits = good score
        scaled = min(int(raw * 4.5 + 30), 98)
        scores[trait] = scaled
    return scores

def get_careers(scores):
    top2 = sorted(scores, key=scores.get, reverse=True)[:2]
    key = tuple(sorted(top2))
    for k, careers in CAREER_MAP.items():
        if set(k) == set(key):
            return careers
    return ["Data Analyst", "Business Analyst", "Project Coordinator", "Team Lead"]

def score_color(score):
    if score >= 75:
        return "#059669", "🟢 Strong"
    elif score >= 55:
        return "#D97706", "🟡 Average"
    else:
        return "#DC2626", "🔴 Needs Work"

# ─────────────────────────────────────────────
#  UI
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">🧠 Personality Prediction System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Upload your CV — get personality scores, improvement tips & career suggestions</div>', unsafe_allow_html=True)

uploaded = st.file_uploader("📄 Upload your CV (PDF or Word)", type=["pdf", "docx"])

if uploaded:
    with st.spinner("Reading your CV..."):
        if uploaded.name.endswith(".pdf"):
            text = read_pdf(uploaded)
        else:
            text = read_docx(uploaded)

    if not text.strip():
        st.error("Could not read text from the file. Please try a different CV.")
        st.stop()

    scores = get_scores(text)
    careers = get_careers(scores)

    st.markdown('<div class="section-head">📊 Your Personality Scores</div>', unsafe_allow_html=True)

    for trait, score in scores.items():
        data = TRAITS[trait]
        bar_color = data["color"]
        level_color, level_label = score_color(score)

        st.markdown(f"""
        <div class="trait-card" style="border-color:{bar_color}">
            <div class="trait-name" style="color:{bar_color}">{data['emoji']} {trait}</div>
            <div class="trait-meaning">{data['meaning']}</div>
            <div class="score-number" style="color:{bar_color}">{score}%</div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(score / 100)
        st.caption(f"Status: {level_label}")

    st.markdown('<div class="section-head">💡 What to Improve</div>', unsafe_allow_html=True)

    weak = {t: s for t, s in scores.items() if s < 65}
    strong = {t: s for t, s in scores.items() if s >= 75}

    if weak:
        for trait, score in weak.items():
            data = TRAITS[trait]
            tips = "\n".join(data["improve"])
            st.markdown(f"""
            <div class="tip-box" style="background:#fff0f0;border-left:4px solid #DC2626;">
                <b style="color:#DC2626">{data['emoji']} {trait} ({score}%) — Needs Improvement</b><br><br>
                {"<br>".join(data['improve'])}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("All traits are at a good level! Keep growing.")

    st.markdown('<div class="section-head">💪 Your Strengths</div>', unsafe_allow_html=True)

    if strong:
        for trait, score in strong.items():
            data = TRAITS[trait]
            st.markdown(f"""
            <div class="tip-box" style="background:#f0fff4;border-left:4px solid #059669;">
                <b style="color:#059669">{data['emoji']} {trait} ({score}%) — Strong Trait</b><br><br>
                {"<br>".join(data['strength'])}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Keep working on all traits to build strong strengths.")

    st.markdown('<div class="section-head">🚀 Best Career Matches for You</div>', unsafe_allow_html=True)

    chips = "".join([f'<span class="career-chip">{c}</span>' for c in careers])
    st.markdown(f'<div class="career-box">{chips}</div>', unsafe_allow_html=True)

    top_trait = max(scores, key=scores.get)
    weak_trait = min(scores, key=scores.get)

    st.markdown(f"""
    <div class="verdict-box">
        <b>Overall Verdict</b><br><br>
        Your biggest strength is <b>{top_trait}</b> ({scores[top_trait]}%) — use this to stand out in interviews.<br>
        Your focus area is <b>{weak_trait}</b> ({scores[weak_trait]}%) — work on this and you will grow much faster.<br><br>
        With consistent effort, you are well suited for roles like <b>{careers[0]}</b> or <b>{careers[1]}</b>.
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("👆 Upload your CV above to get started.")
    st.markdown("""
    **What this app does:**
    - Reads your CV (PDF or Word)
    - Predicts your Big Five personality traits
    - Shows your score for each trait
    - Gives improvement tips for weak areas
    - Suggests best career paths for you
    """)
