import streamlit as st, requests, os
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="FinShield")
st.title("🛡️ FinShield")
st.caption("Don't trust. Verify.")

mode = st.radio("What did you receive?", ["Message", "Financial Claim", "Screenshot"], horizontal=True)

def show_result(r):
    st.header(r["risk_level"])
    st.metric("Risk score", r["score"])
    st.subheader(f"{len(r['red_flags'])} risk indicator(s)")
    for f in r["red_flags"]:
        st.markdown(f"🔴 **{f['category']}** — matched `{f['matched']}`. {f['reason']}")
    st.subheader("Structured decision (Mercury Decide)")
    st.json(r["mercury"])
    st.subheader("Why this matters")
    st.write(r["explanation"])
    st.subheader("Verify before acting")
    for s in r["verification_steps"]:
        st.markdown("- " + s)
    st.subheader("Safe next steps")
    for s in r["safe_next_steps"]:
        st.markdown("- " + s)
    st.subheader("Evidence")
    for e in r["evidence"]:
        st.markdown(f"**{e['claim']}** — {e['status']}. Ref: {e['reference']}")
    st.caption(r["uncertainty"])

if mode in ("Message", "Financial Claim"):
    text = st.text_area("Paste content here...", height=160)
    if st.button("ANALYZE", type="primary") and text.strip():
        with st.spinner("Analyzing..."):
            endpoint = "/api/v1/analyze/text" if mode == "Message" else "/api/v1/analyze/claim"
            r = requests.post(BACKEND_URL + endpoint, json={"text": text}, timeout=60).json()
        show_result(r)
else:
    up = st.file_uploader("Upload screenshot", type=["png", "jpg", "jpeg"])
    if up is not None and st.button("ANALYZE", type="primary"):
        with st.spinner("Analyzing..."):
            r = requests.post(BACKEND_URL + "/api/v1/analyze/image", files={"file": up}, timeout=120).json()
        show_result(r)
