import streamlit as st
import pandas as pd
from utils.auth_utils import require_login, check_role, render_sidebar
from models.announcement import Announcement

st.set_page_config(page_title="Announcements", page_icon="📢", layout="wide")
require_login()
render_sidebar()
check_role(['Admin'])

st.title("📢 Manage Announcements")

ann_model = Announcement()

with st.expander("Create New Announcement", expanded=True):
    with st.form("new_announcement"):
        title = st.text_input("Title")
        message = st.text_area("Message")
        if st.form_submit_button("Post Announcement"):
            if title and message:
                ann_model.create(title, message)
                st.success("Posted!")
                st.rerun()
            else:
                st.error("Title and Message required.")

st.subheader("History")
anns = ann_model.get_all()
if anns:
    for ann in anns:
        c1, c2 = st.columns([4, 1])
        with c1:
            st.info(f"**{ann['title']}**\n\n{ann['message']}\n\n*Posted: {ann['created_at']}*")
        with c2:
            if st.button("Delete", key=f"del_ann_{ann['id']}"):
                ann_model.delete(ann['id'])
                st.rerun()
