import streamlit as st
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
HEADERS = {"Authorization": "Bearer YOUR_HUGGING_FACE_API_KEY"}

# Google OAuth 2.0 details
CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
REDIRECT_URI = "YOUR_REDIRECT_URI"
SCOPE = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"

# Function to render the sign-up page
def render_signup_page():
    st.title("Sign Up")
    st.markdown("### Sign up with Google")

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "select_account consent"
    }
    google_signin_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    if st.button("Sign in with Google"):
        st.markdown(f'<meta http-equiv="refresh" content="0; url={google_signin_url}">', unsafe_allow_html=True)

    st.markdown("### Or sign up with your details")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    work_email = st.text_input("Work Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if password == confirm_password and first_name and last_name and work_email:
            st.success("Account created successfully!")
        else:
            st.error("Please fill all fields correctly.")

# Sidebar navigation
st.sidebar.title("AI Email Generator")
st.sidebar.subheader("Login / Sign up")
username = st.sidebar.text_input("Username:")
password = st.sidebar.text_input("Password:", type="password")

if st.sidebar.button("Login"):
    st.sidebar.success(f"Welcome {username}!")

if st.sidebar.button("Sign up"):
    st.query_params["page"] = "signup"

st.sidebar.subheader("Search History")
if "history" not in st.session_state:
    st.session_state.history = []

for idx, item in enumerate(st.session_state.history[-5:]):
    st.sidebar.text(f"{idx + 1}. {item}")

# Hugging Face API call
def generate_email(topic, sender, recipient, style):
    prompt = f"Write a {style.lower()} email about '{topic}'. From: {sender}, To: {recipient}."
    payload = {"inputs": prompt, "parameters": {"max_length": 300, "temperature": 0.7}}
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json()[0].get("generated_text", "Error: Unexpected response format.").strip()
    return f"Error: {response.status_code} - {response.json()}"

# SMTP Email sender
def send_email(sender_email, sender_password, recipient_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        return "✅ Email sent successfully!"
    except Exception as e:
        return f"❌ Error sending email: {e}"

# Main interface
st.markdown("# AI Email Generator & Sender")

if st.query_params.get("page") == "signup":
    render_signup_page()
else:
    topic = st.text_input("Enter email topic:")
    sender = st.text_input("Sender's Email:")
    recipient = st.text_input("Receiver's Email:")
    style = st.selectbox("Choose Email Tone:", ["Formal", "Casual", "Appreciating", "Complaint"])

    email_text = ""
    if st.button("Generate Email"):
        email_text = generate_email(topic, sender, recipient, style)
        st.text_area("Generated Email:", email_text, height=200)
        st.session_state.history.append(topic)

    sender_password = st.text_input("Sender Email Password", type="password")
    subject = st.text_input("Email Subject:")

    if st.button("Send Email"):
        if sender and sender_password and recipient and email_text and subject:
            st.success(send_email(sender, sender_password, recipient, subject, email_text))
        else:
            st.error("❗ Please fill all fields before sending.")