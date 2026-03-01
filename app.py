import streamlit as st
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from main import get_video_id, get_transcript, generate_summary
from sqlite import createdb, fetch_summary, insert_summary
from rag import create_embedddb

load_dotenv()


@st.cache_resource
def init_db():
    createdb()
    create_embedddb()


init_db()


def send_email(recipient_email: str, video_url: str, summary: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", smtp_user)

    if not smtp_user or not smtp_password:
        st.error("Email credentials not configured. Fill in SMTP_USER and SMTP_PASSWORD in the .env file.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your YouTube Video Summary"
    msg["From"] = email_from
    msg["To"] = recipient_email

    plain_body = f"Video: {video_url}\n\n{summary}"
    html_body = f"""
    <html><body>
      <h2>YouTube Video Summary</h2>
      <p><strong>Video URL:</strong> <a href="{video_url}">{video_url}</a></p>
      <hr>
      <pre style="white-space: pre-wrap; font-family: sans-serif;">{summary}</pre>
    </body></html>
    """

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(email_from, recipient_email, msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError:
        st.error("SMTP authentication failed. Check SMTP_USER and SMTP_PASSWORD in .env.")
        return False
    except smtplib.SMTPException as e:
        st.error(f"Failed to send email: {e}")
        return False


def main():
    st.set_page_config(
        page_title="YouTube Summariser",
        page_icon="▶",
        layout="centered",
    )

    st.title("YouTube Video Summariser")
    st.caption("Paste a YouTube link to get a transcript and AI-generated summary.")

    url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/...",
    )

    submit = st.button("Summarise", type="primary", disabled=not url)

    if "transcript" not in st.session_state:
        st.session_state.transcript = None
    if "summary" not in st.session_state:
        st.session_state.summary = None
    if "current_url" not in st.session_state:
        st.session_state.current_url = None

    if submit and url:
        st.session_state.current_url = url
        st.session_state.transcript = None
        st.session_state.summary = None

        try:
            video_id = get_video_id(url)
        except ValueError:
            st.error("Invalid YouTube URL. Please check the link and try again.")
            st.stop()

        cached = fetch_summary(url)
        if cached:
            st.info("Loaded from cache.")
            with st.spinner("Fetching transcript..."):
                st.session_state.transcript = get_transcript(video_id)
            st.session_state.summary = cached
        else:
            with st.spinner("Fetching transcript from YouTube..."):
                transcript = get_transcript(video_id)

            if not transcript:
                st.error(
                    "Could not retrieve a transcript for this video. "
                    "The video may have no captions, or captions may be disabled."
                )
                st.stop()

            st.session_state.transcript = transcript

            with st.spinner("Generating summary with AI (this may take a moment)..."):
                generate_summary(url, transcript)
                st.session_state.summary = fetch_summary(url)

    if st.session_state.transcript:
        with st.expander("View Full Transcript", expanded=False):
            st.text(st.session_state.transcript)

    if st.session_state.summary:
        st.subheader("AI Summary")
        st.markdown(st.session_state.summary)
        st.divider()

        st.subheader("Email this Summary")
        email_input = st.text_input(
            "Your email address",
            placeholder="you@example.com",
        )
        send_button = st.button("Send to Email", disabled=not email_input)

        if send_button and email_input:
            with st.spinner("Sending email..."):
                success = send_email(
                    recipient_email=email_input,
                    video_url=st.session_state.current_url,
                    summary=st.session_state.summary,
                )
            if success:
                st.success(f"Summary sent to {email_input}")


if __name__ == "__main__":
    main()
