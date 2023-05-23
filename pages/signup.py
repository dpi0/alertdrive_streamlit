import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import streamlit_authenticator as stauth
import time
import re
from deepface import DeepFace
from PIL import Image
from detadb_helper import DBManager
import numpy


db = DBManager("test_db")

if (
    "button_age_verif" not in st.session_state
    and "key_checkbox" not in st.session_state
    and "user_above_18" not in st.session_state
    and "register_state" not in st.session_state
):
    st.session_state["button_age_verif"] = False
    st.session_state["key_checkbox"] = False
    st.session_state["user_above_18"] = False
    st.session_state["register_state"] = False


captured_img_from_cam = None


def signup_form(age, gender):
    def validate_username_presence(username):
        try:
            return db.get_by_username(username)["key"] == username
        except (TypeError, AttributeError) as e:
            print("Username not present but, Email already present -->", e)

    def validate_email_presence(email):
        all_emails: list = [user["email"] for user in db.get_all_users()]
        for email_address in all_emails:
            if email_address == email:
                return True

    def validate_name(name):
        pattern = r"^[A-Za-z\s]+$"
        return re.match(pattern, name) is not None

    def validate_username(username):
        pattern = r"^[a-zA-Z0-9]{4,20}$"
        return re.match(pattern, username)

    def validate_email(email):
        pattern = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
        return re.match(pattern, email)

    def validate_password(password):
        pattern = (
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
        )
        return re.match(pattern, password)


    st.write("")
    st.write("")
    
    with st.form("Signup Form"):
        st.subheader("👋Welcome! Please fill in your details.")

        name = st.text_input("**Your Name**")
        username = st.text_input("**Username**")
        email = st.text_input("**Email Address**")
        password = st.text_input("**Password**", type="password")
        confirm_password = st.text_input(
            "**Confirm Password**", type="password"
        )

        hashed_password_list: list = [password, confirm_password]
        hashed_password: list = stauth.Hasher(hashed_password_list).generate()

        if st.form_submit_button("Register"):
            st.session_state["register_state"] = not st.session_state[
                "register_state"
            ]
            if not validate_name(name):
                st.error(
                    "🤦Please provide a valid full name without numbers, \
                        special characters, or spaces."
                )
            elif validate_username_presence(username):
                st.error(
                    "⛔User already exists. Please login or try a different \
                        username"
                )
            elif validate_email_presence(email):
                st.error(
                    "⛔Email Address already exists. Please login or try a \
                        different email address"
                )
            elif not validate_username(username):
                st.warning(
                    "🤦Please enter a valid username. Having alphanumeric \
                        characters only and between 4 and 20 characters long"
                )
            elif not validate_email(email):
                st.warning("📢Please enter a valid email address.")
            elif not validate_password(password):
                st.warning(
                    "🔑Please enter a valid password. It should have at least \
                        8 characters, one uppercase letter, one lowercase \
                            letter, one digit, and one special character."
                )
            elif password != confirm_password:
                st.error(
                    "⛔Passwords do not match. Please re-enter the password."
                )

            elif (
                captured_img_from_cam is not None
                and st.session_state["button_age_verif"]
                and st.session_state["key_checkbox"]
                and st.session_state["user_above_18"]
                and st.session_state["register_state"]
            ):
                db.insert_user(
                    username, name, age, gender, email, hashed_password[0]
                )

                with st.spinner("Processing..."):
                    time.sleep(2)
                st.success("You have successfully signed up!", icon="🌱")
                time.sleep(1)
                st.balloons()
                time.sleep(2)
                switch_page("streamlit_app")


st.subheader("First Off! 🙏Please verify your age to proceed.")

col1, col2, col3 = st.columns([2, 0.9, 0.5])

with col1:
    if st.button("Verify your age"):
        st.session_state["button_age_verif"] = not st.session_state[
            "button_age_verif"
        ]
with col2:
    st.write("Already have an account?")
with col3:
    if st.button("Login"):
        switch_page("streamlit_app")


if st.session_state["button_age_verif"]:
    captured_img_from_cam = st.camera_input("Ready, set, picture time!")
    st.checkbox("Proceed with this photo?", key="key_checkbox")


if (
    captured_img_from_cam is not None
    and st.session_state["button_age_verif"]
    and st.session_state["key_checkbox"]
):
    # message_wait = st.warning("Please wait while we process your picture..")

    pre_processed_img = Image.open(captured_img_from_cam)
    # st.image(pre_processed_img)

    proceesed_img = numpy.asarray(pre_processed_img)
    # st.image(proceesed_img)

    result = DeepFace.analyze(
        img_path=proceesed_img,
        actions=["age", "gender"],
        enforce_detection=False,
    )

    user_age_gender: list = [
        result[0]["age"],
        result[0]["dominant_gender"],
    ]

    if user_age_gender[0] > 18:
        st.session_state["user_above_18"] = True


if (
    captured_img_from_cam is not None
    and st.session_state["button_age_verif"]
    and st.session_state["key_checkbox"]
    and st.session_state["user_above_18"]
):
    # message_wait.empty()
    success_age_confirm = st.success(
        "🎉Hooray! Age confirmed to be above 18."
    )

    signup_form(user_age_gender[0], user_age_gender[1])


elif (
    captured_img_from_cam is not None
    and st.session_state["button_age_verif"]
    and st.session_state["key_checkbox"]
    and not st.session_state["user_above_18"]
):
    st.error(
        "🤦We're sorry, but the minimum age requirement for proceeding \
            is 18 or older."
    )


# st.write(
#     f"""
# ## Session state:
# {st.session_state["button_age_verif"]=}

# {st.session_state["key_checkbox"]=}

# {st.session_state["user_above_18"]=}

# {st.session_state["register_state"]=}

# """
# )
