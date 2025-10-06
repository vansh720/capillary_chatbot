# app.py
import streamlit as st
import json, re

st.set_page_config(page_title="CapillaryTech Chatbot", layout="wide")
st.title("CapillaryTech Chatbot — simple retriever")

@st.cache_data
def load_pages():
    try:
        with open("capillary_docs.json", "r", encoding="utf-8") as f:
            pages = json.load(f)
    except FileNotFoundError:
        return []
    entries = []
    for p in pages:
        url = p.get("url", "")
        text = p.get("text", "")
        # split into sentences
        sents = re.split(r'(?<=[\.\?\!])\s+', text)
        for s in sents:
            s = s.strip()
            if len(s) > 20:  # ignore tiny fragments
                entries.append({"sentence": s, "url": url})
    return entries

entries = load_pages()

def score_sentence(q, s):
    q_words = set(re.findall(r'\w+', q.lower()))
    s_words = set(re.findall(r'\w+', s.lower()))
    if not q_words:
        return 0
    return len(q_words & s_words) / len(q_words)

query = st.text_input("Ask a question about CapillaryTech (e.g. 'What is Loyalty+'):")

if st.button("Search") or query:
    if not query.strip():
        st.info("Type a question first.")
    else:
        scored = []
        for e in entries:
            sc = score_sentence(query, e["sentence"])
            if sc > 0:
                scored.append({"score": sc, "sentence": e["sentence"], "url": e["url"]})
        top = sorted(scored, key=lambda x: x["score"], reverse=True)[:5]
        if not top:
            st.write("No good match found. Try rephrasing (use keywords).")
        else:
            for t in top:
                st.markdown(f"**Answer (score {t['score']:.2f})**")
                st.write(t["sentence"])
                st.caption(t["url"])
                st.write("---")
