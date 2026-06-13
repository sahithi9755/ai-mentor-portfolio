import streamlit as st
from google import genai
import os, json

st.set_page_config(page_title='Résumé Scorer', layout='wide')
st.title('Résumé vs JD Fit Scorer')
st.caption('Day 5 Lab 5A — Free tools end-to-end')

col1, col2 = st.columns(2)
with col1:
    resume = st.text_area('Paste résumé', height=400)
with col2:
    jd = st.text_area('Paste job description', height=400)

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = st.text_input(
        "Gemini API key",
        type="password",
        help="Free key from aistudio.google.com"
    )

if st.button('Score') and resume and jd and api_key:
    with st.spinner('Scoring...'):
        client = genai.Client(api_key=api_key)
        prompt = f"""You are a placement coach. Given this résumé and JD,
return JSON: {{
  "score": int 0-100,
  "rationale": str,
  "missing_skills": [str],
  "suggestions": [str],
  "technical_skills_match": int,
  "soft_skills_match": int,
  "experience_relevance": int,
  "project_fit": int,
  "learning_resources": [
    {{
      "skill": str,
      "resource_type": "YouTube Channel" | "Free Course",
      "link": str
    }}
  ]
}}.
Only include the top 3 missing skills in "learning_resources".

Résumé:
{resume}

JD:
{jd}"""
        resp = client.models.generate_content(
            model='gemini-2.5-flash', contents=prompt,
            config={'response_mime_type': 'application/json'})

        result = json.loads(resp.text)

        st.metric('Fit Score', f"{result['score']}/100")

        # Breakdown chart of sub-scores
        sub_scores = {
            'Technical Skills': result.get('technical_skills_match', 0),
            'Soft Skills': result.get('soft_skills_match', 0),
            'Experience Relevance': result.get('experience_relevance', 0),
            'Project Fit': result.get('project_fit', 0)
        }
        st.bar_chart(sub_scores)

        st.subheader('Rationale')
        st.write(result['rationale'])
        st.subheader('Missing skills')
        for s in result['missing_skills']:
            st.write(f'- {s}')
        
        st.subheader('Top 3 Missing Skills & Resources')
        for res in result.get('learning_resources', []):
            st.write(f"**{res['skill']}** ({res['resource_type']}): [Link]({res['link']})")

        st.subheader('Suggestions')

        for s in result['suggestions']:
            st.write(f'- {s}')