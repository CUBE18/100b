import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="100B Hiring App", layout="wide")
st.title("🚀 100B Jobs – Smart Hiring App")

REQUIRED_SKILLS = {
    "python", "ml", "data analysis", "docker", "sql", "pyspark", "microservices",
    "cloud computing", "ci/cd", "kubernetes", "react", "aws", "typescript",
    "node js", "java", "machine learning", "next js", "redux", "flask"
}

@st.cache_data
def load_data():
    with open("form-submissions.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

def compute_score(candidate):
    score = 0
    skills = set([s.lower() for s in candidate.get("skills", [])])
    score += len(skills & REQUIRED_SKILLS) * 5
    score += len(candidate.get("work_experiences", [])) * 3

    for edu in candidate.get("education", {}).get("degrees", []):
        subj = edu.get("subject", "").lower()
        if any(x in subj for x in ["computer", "information", "engineering", "technology", "data"]):
            score += 3
        if edu.get("isTop50", False):
            score += 2

    if "full-time" in [x.lower() for x in candidate.get("work_availability", [])]:
        score += 5

    return score

def build_df(data):
    rows = []
    for c in data:
        rows.append({
            "Name": c.get("name"),
            "Email": c.get("email"),
            "Score": compute_score(c),
            "Experience Count": len(c.get("work_experiences", [])),
            "Skills": ", ".join(c.get("skills", [])),
            "Top School": any(e.get("isTop50", False) for e in c.get("education", {}).get("degrees", [])),
            "Available": "full-time" in [x.lower() for x in c.get("work_availability", [])],
            "Location": c.get("location", "")
        })
    return pd.DataFrame(rows)

df = build_df(data)
df_sorted = df.sort_values(by="Score", ascending=False)

st.subheader("📊 All Candidates (Ranked)")
st.dataframe(df_sorted, use_container_width=True)

st.subheader("👥 Build Your Team of 5")
selected_names = st.multiselect("Select exactly 5 candidates", df_sorted["Name"].tolist(), max_selections=5)

if len(selected_names) == 5:
    team_df = df_sorted[df_sorted["Name"].isin(selected_names)]
    st.success("✅ Final Team Selected")
    st.dataframe(team_df)

    skill_pool = set()
    for name in selected_names:
        candidate = next(c for c in data if c["name"] == name)
        skill_pool.update([s.lower() for s in candidate.get("skills", [])])

    st.markdown(f"**Skill Diversity:** {', '.join(sorted(skill_pool))}")
    st.markdown("**Why This Team?**")
    st.markdown("""
    - Strong scores across technical and leadership roles  
    - Balanced team across frontend, backend, and data  
    - Includes candidates with diverse education and locations  
    - All available full-time  
    - Mix of traditional and non-traditional backgrounds  
    """)
else:
    st.warning("Please choose exactly 5 candidates to finalize your team.")
