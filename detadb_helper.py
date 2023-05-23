from deta import Deta
import streamlit as st


class DBManager:
    def __init__(self, database_name) -> None:
        self.deta = Deta(st.secrets["DETA_KEY"])
        self.db = self.deta.Base(database_name)

    def insert_user(self, username, name, age, gender, email, password):
        return self.db.put(
            {
                "key": username,
                "name": name,
                "age": age,
                "gender": gender,
                "email": email,
                "password": password,
            }
        )

    def get_all_users(self):
        result = self.db.fetch()
        return result.items

    def get_by_username(self, username):
        return self.db.get(username)

    def update_user(self, username, updates):
        return self.db.update(updates, username)

    def delete_user(self, username):
        return self.db.delete(username)
