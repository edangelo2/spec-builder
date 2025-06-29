import os, json, requests, streamlit as st

st.set_page_config(page_title="Spec Builder", layout="wide")

api = os.getenv("API_BASE_URL", "http://backend:8000")
headers: dict[str, str] = {}  # no auth headers needed

# -------- UI Layout --------
left, right = st.columns([1, 2])

with left:
    st.header("Upload spec")
    doc = st.file_uploader(".docx specification", type=["docx"])
    if doc and st.button("Ingest"):
        r = requests.post(f"{api}/ingest", files={"file": doc}, timeout=60)
        st.session_state["spec"] = r.json()

    if "spec" in st.session_state:
        spec = st.session_state["spec"]
        section = st.selectbox("Sections", list(spec.keys()))
        status = spec[section]["status"]
        st.markdown(f"**Status:** {status}")
        if st.button("Refine", key=section):
            requests.post(f"{api}/refine", json={"section": section}, timeout=120)

with right:
    if "spec" in st.session_state:
        raw = st.text_area("Original", st.session_state["spec"][section]["raw"], height=300)
        refined = st.text_area("Refined", st.session_state["spec"][section].get("refined", ""), height=300)
        if raw and refined:
            st.markdown("### Diff")
            st.code("placeholder for diff viewer — integrate differ here")