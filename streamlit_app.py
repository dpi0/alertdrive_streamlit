import streamlit as st
import os
import av
import re
import threading
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page
from streamlit_webrtc import (
    VideoHTMLAttributes,
    webrtc_streamer,
    WebRtcMode,
)
from dotenv import load_dotenv
from twilio.rest import Client
from detadb_helper import DBManager
from alert_helper.audio_handle import AudioFrameHandler
from alert_helper.video_handle import VideoFrameHandler
from contact_utils.helper import send_email
from contact_utils.constants import (
    SMTP_SERVER_ADDRESS,
    PORT,
    SENDER_PASSWORD,
    SENDER_ADDRESS,
)

st.set_page_config(
    page_title="AlertDrive: Deep Learning Based Alertness Evaluation",
    page_icon="alertdrive.ico",
)

load_dotenv()

alarm_file_path = os.path.join("alert_helper", "assets", "audio_files", "wake_up.wav")

WAIT_DOZEOFF_TIME = 4
WAIT_HEADPOSN_TIME = 5

EAR_THRESH = 0.14
LEFT_THRESH = 18
RIGHT_THRESH = 18
DOWN_THRESH = 18
UP_THRESH = 18


thresholds = {
    "EAR_THRESH": EAR_THRESH,
    "LEFT_THRESH": LEFT_THRESH,
    "RIGHT_THRESH": RIGHT_THRESH,
    "DOWN_THRESH": DOWN_THRESH,
    "UP_THRESH": UP_THRESH,
    "WAIT_DOZEOFF_TIME": WAIT_DOZEOFF_TIME,
    "WAIT_HEADPOSN_TIME": WAIT_HEADPOSN_TIME,
}

video_handler = VideoFrameHandler()
audio_handler = AudioFrameHandler(sound_file_path=alarm_file_path)

lock = threading.Lock()

shared_state = {"play_alarm": False}


def video_frame_callback(frame: av.VideoFrame):
    frame = frame.to_ndarray(format="bgr24")

    frame, play_alarm = video_handler.process(frame, thresholds)
    with lock:
        shared_state["play_alarm"] = play_alarm

    return av.VideoFrame.from_ndarray(frame, format="bgr24")


def audio_frame_callback(frame: av.AudioFrame):
    with lock:
        play_alarm = shared_state["play_alarm"]

    new_frame: av.AudioFrame = audio_handler.process(
        frame, play_sound=play_alarm
    )
    return new_frame


def get_ice_servers():
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    token = client.tokens.create()

    return token.ice_servers


def hide_all():
    st.set_page_config(initial_sidebar_state="collapsed")

    st.markdown(
        """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
        #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 4rem;}
        div[data-testid="stSidebarNav"] {display: none;}
        .css-15zrgzn {display: none}
        .css-1dp5vir {display: none} 
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
        unsafe_allow_html=True,
    )


# hide_all()

navbar = option_menu(
    menu_title=None,
    options=["Home", "About", "Contact", "Login"],
    icons=[
        "broadcast",
        "person-fill",
        "telephone-fill",
        "box-arrow-in-right",
    ],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0!important",
            "background-color": "#000",
        },
        "icon": {"color": "white", "font-size": "16px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "padding": "8px",
            "--hover-color": "#2f2f2f",
        },
        "nav-link-selected": {"background-color": "rgb(250, 30, 55)"},
    },
)


def display_home():
    hide_image_fullscreen = """
    <style>
    button[title="View fullscreen"]{
        visibility: hidden;}
    </style>
    """

    st.markdown(hide_image_fullscreen, unsafe_allow_html=True)

    col1, mid, col2 = st.columns([1, 1, 14])
    with col1:
        st.image("alertdrive.ico", width=81)
    with col2:
        original_title = '<p style="color:#fff; font-weight:bold; font-size: 50px;">AlertDrive</p>'
        st.markdown(original_title, unsafe_allow_html=True)

    st.markdown("##### A Deep-Learning Based Driver Alertness Evaluation")

    st.write("")
    st.markdown("## 📕About this App")
    st.markdown(
        """
        In an era where road safety is of paramount importance, driver attentiveness plays a vital role in preventing accidents and safeguarding lives. With a mission to enhance road safety and reduce the risks associated with drowsy driving, welcome **:red[AlertDrive]**.
        """
    )

    st.markdown("## 🚀Necessity")
    st.markdown(
        """
        The necessity of this project stems from the **:orange[dire consequences of driver inattention on road safety]**. Distractions, fatigue, and other factors can significantly impair a driver's ability to stay alert, increasing the likelihood of accidents. 
        
        By developing a comprehensive driver monitoring system, we can proactively identify signs of inattentiveness and provide drivers with **:red[real-time feedback and alerts]**, helping them maintain focus on the road.
        
        Furthermore, the integration of **:blue[age verification functionality]** ensures that the system is used responsibly, preventing underage individuals from accessing the monitoring system.
        """
    )

    st.markdown("## 🤔How to use this app?")
    st.markdown(
        """
        To get started, follow these steps to create an account:

        1. 🙍🏽**Ensure that you are 18 years of age or older**, as our age verification systems require participants to meet this requirement.
        2. Visit our registration page and provide the necessary information to create your account.
        3. Once your account is successfully created, 🔒**log in to the app** using your credentials.
        
        Once you are logged in, you will be presented with the following features:

        **:green[Live Video Analysis]:** Click on the "Start" button to initiate the live video feed from your camera system. 
        This feature will continuously monitor your facial expressions and head position to provide real-time feedback on your level of attentiveness while driving. 
        
        It will specifically detect any instances where you may doze off or divert your attention away from the road.

        **:green[Session Control]:** You have the flexibility to stop the monitoring session at any time. If you choose to end the session, you will be prompted to either receive a detailed report of your session via email or simply log out if you prefer not to receive the report.
        """
    )

    st.write("")
    st.write("")
    st.markdown(
        """
                **:red[Remember]**, your safety is our top priority. By utilizing our app's live video analysis and session control features, you can take proactive steps towards enhancing your driving awareness and ensuring a secure journey.
                
                Enjoy your ride 🚗 and Stay Alert 🚨!
                """
    )


def display_about():
    st.markdown("# About")
    st.markdown("### Introduction")
    st.markdown(
        """
        **:red[AlertDrive]**, developed as part of my BTECH ECE project at **:green[Jamia Hamdard University]**, is a powerful tool that **helps drivers stay alert and attentive** on the road.

        As the developer of AlertDrive, I take great pride and satisfaction in developing a web app that can potentially save lives. """
    )

    st.markdown("### Personal Outlook")
    st.markdown(
        """
                The journey of building this app has been **both challenging and rewarding** 😅. Seeing the positive impact it can have on driver safety fuels my motivation to further improve and expand its capabilities.
                """
    )

    st.markdown("### Future Outlook")
    st.markdown(
        """
                In the future, I envision expanding AlertDrive's functionality by incorporating additional features. One potential enhancement could involve **:orange[integrating emotion detection algorithms]** to identify drivers' emotional states 😁.
                
                Moreover, **:orange[exploring voice analysis]** techniques could allow AlertDrive to monitor speech patterns and identify signs of fatigue or drowsiness based on changes in vocal characteristics.

                """
    )

    st.write("")

    st.markdown(
        """
                 I am confident that AlertDrive will contribute significantly to improving road safety, and I hope it serves as a valuable resource for drivers to stay vigilant and prevent accidents caused by driver inattention.

                👨🏽*Divyansh Pandit*
                """
    )


def display_contact():
    st.title("📫Have a message?")

    def validate_email(email):
        pattern = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
        return re.match(pattern, email)

    def validate_subject(subject):
        if not subject:
            return False

        pattern = r"^[\w\s.-]+$"
        return bool(re.match(pattern, subject)) and len(subject) <= 100

    def validate_body(body):
        return bool(body) and len(body) <= 1000

    with st.form("Email Form"):
        receiver_email = "dvynsh24@gmail.com"
        sender_email = st.text_input(
            label="Email Address", placeholder="Your Email Address"
        )
        email_subject = st.text_input(
            label="Subject", placeholder="Your Message is regarding?"
        )
        email_body = st.text_area(
            label="Message", placeholder="Your thoughts here..."
        )
        file_uploaded = st.file_uploader("Attachment")

        if st.form_submit_button(label="Send"):
            if not validate_email(sender_email):
                st.warning("📢Please enter a valid email address.")

            elif not validate_subject(email_subject):
                st.warning(
                    "✍️Subject is not valid. Please make sure it is alphanumeric and does not exceed 100 characters."
                )

            elif not validate_body(email_body):
                st.warning(
                    "✍️Email Message is not valid. Please make sure it is not empty and does not exceed 500 characters."
                )

            else:
                email_top_text = f"""
                -------------------------------------
                EMAIL DETAILS:
                Sender's Email Address: {sender_email}
                Subject: {email_subject}
                -------------------------------------
                """

                email_all_text = email_top_text + email_body

                send_email(
                    sender=SENDER_ADDRESS,
                    password=SENDER_PASSWORD,
                    receiver=receiver_email,
                    smtp_server=SMTP_SERVER_ADDRESS,
                    smtp_port=PORT,
                    email_message=email_all_text,
                    subject=email_subject,
                    attachment=file_uploaded,
                )

                st.success("🎉Hooray! Your message was sent successfully!")


def display_login():
    db = DBManager("test_db")
    users_db = db.get_all_users()
    user_usernames: list = [user["key"] for user in users_db]
    user_names: list = [user["name"] for user in users_db]
    user_emails: list = [user["email"] for user in users_db]
    user_passwds: list = [user["password"] for user in users_db]

    data_db: dict = {
        "credentials": {
            "usernames": {
                username: {
                    "email": email,
                    "name": name,
                    "password": password,
                }
                for username, name, email, password in zip(
                    user_usernames, user_names, user_emails, user_passwds
                )
            }
        }
    }

    authenticator = stauth.Authenticate(
        data_db["credentials"],
        cookie_name="login",
        key="mainapp",
        cookie_expiry_days=30,
    )

    user_name, auth_status, user_email = authenticator.login(
        "🔒Login", "main"
    )

    flag_loggedin = False

    if auth_status is False:
        st.error("⛔ Incorrect username or password. Try Again.")

    elif auth_status is None:
        st.warning("⚠️ Please enter your username and password")

    else:
        flag_loggedin = True
        message_logged_in = st.success("🎉 Successfully logged in!")
        message_logged_in.empty()
        col1, mid, col2 = st.columns([1, 1, 14])
        with col1:
            st.image("alertdrive.ico", width=81)
        with col2:
            original_title = '<p style="color:#fff; font-weight:bold; font-size: 50px;">AlertDrive Session</p>'
            st.markdown(original_title, unsafe_allow_html=True)

        st.markdown(
            f"#### 👋 Welcome {data_db['credentials']['usernames'][user_name]['name']}, {data_db['credentials']['usernames'][user_name]['email']}"
        )
        
        st.write("")
        st.markdown("##### Now click start, and we'll see how well you perform!")

        ctx = webrtc_streamer(
            key="drowsiness-detection",
            mode=WebRtcMode.SENDRECV,
            video_frame_callback=video_frame_callback,
            audio_frame_callback=audio_frame_callback,
            rtc_configuration={"iceServers": get_ice_servers()},
            media_stream_constraints={
                "video": {"height": {"ideal": 480}},
                "audio": True,
            },
            video_html_attrs=VideoHTMLAttributes(
                autoPlay=True, controls=False, muted=False
            ),
            async_processing=True,
        )
                
        authenticator.logout("Logout", "main", key="key_logout")

    st.write("")
    st.write("")
    st.write("")
    st.write("")

    if not flag_loggedin:
        st.write("Don't have an account?")
        signup_button = st.button("Signup")
        if signup_button:
            switch_page("signup")


if navbar == "Home":
    display_home()

elif navbar == "About":
    display_about()

elif navbar == "Contact":
    display_contact()

elif navbar == "Login":
    display_login()
