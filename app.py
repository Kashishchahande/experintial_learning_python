import os
import sqlite3
import hmac
from datetime import date, datetime

import streamlit as st

st.set_page_config(
    page_title="Digital Notice Board",
    page_icon="📢",
    layout="wide"
)

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notices.db")
CATEGORIES = ["Academic", "Examination", "Events", "Placements", "Holidays", "General"]

# Demo credentials. Configure environment variables before deployment.
ADMIN_USER = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "admin123")


def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def initialize():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS notices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                publish_date TEXT NOT NULL,
                expiry_date TEXT,
                created_at TEXT NOT NULL
            )
        """)


def all_notices():
    with connect() as con:
        return con.execute(
            "SELECT * FROM notices ORDER BY publish_date DESC, id DESC"
        ).fetchall()


def save_notice(title, description, category, pub, expiry, notice_id=None):
    values = (
        title.strip(), description.strip(), category, pub.isoformat(),
        expiry.isoformat() if expiry else None
    )
    with connect() as con:
        if notice_id is None:
            con.execute("""
                INSERT INTO notices
                (title, description, category, publish_date, expiry_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, values + (datetime.now().isoformat(timespec="seconds"),))
        else:
            con.execute("""
                UPDATE notices
                SET title=?, description=?, category=?, publish_date=?, expiry_date=?
                WHERE id=?
            """, values + (notice_id,))


def main():
    initialize()

    st.markdown("""
    <style>
    .block-container {padding-top: 2rem;}
    h1 {color: #2457A7;}
    </style>
    """, unsafe_allow_html=True)

    st.title("📢 Digital Notice Board")
    st.caption("A centralized platform for important college announcements.")

    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Choose a page", ["Home", "Admin Login", "Manage Notices"])
        st.divider()
        st.caption("Python • Streamlit • SQLite")

    if "admin" not in st.session_state:
        st.session_state.admin = False

    if page == "Home":
        notices = all_notices()
        today = date.today().isoformat()
        active = [
            n for n in notices
            if n["publish_date"] <= today
            and (not n["expiry_date"] or n["expiry_date"] >= today)
        ]

        c1, c2, c3 = st.columns(3)
        c1.metric("Active Notices", len(active))
        c2.metric("Categories", len(set(n["category"] for n in active)))
        c3.metric("Published Today", sum(n["publish_date"] == today for n in active))

        st.subheader("Search and Filter")
        search = st.text_input("Search title or description")
        a, b = st.columns(2)
        with a:
            category = st.selectbox("Category", ["All"] + CATEGORIES)
        with b:
            order = st.selectbox("Sort by date", ["Newest First", "Oldest First"])

        results = active
        if search.strip():
            q = search.casefold().strip()
            results = [
                n for n in results
                if q in n["title"].casefold() or q in n["description"].casefold()
            ]
        if category != "All":
            results = [n for n in results if n["category"] == category]

        results = sorted(
            results,
            key=lambda n: (n["publish_date"], n["id"]),
            reverse=(order == "Newest First")
        )

        st.subheader("Published Notices")
        st.caption(f"{len(results)} notice(s) found")
        if not results:
            st.info("No notices found. Try changing the search or category.")
        for n in results:
            with st.container(border=True):
                st.subheader("📌 " + n["title"])
                st.caption(f"{n['category']}  •  Published: {n['publish_date']}")
                st.write(n["description"])
                if n["expiry_date"]:
                    st.caption("Valid until: " + n["expiry_date"])

    elif page == "Admin Login":
        if st.session_state.admin:
            st.success("Administrator is logged in.")
            if st.button("Log out"):
                st.session_state.admin = False
                st.rerun()
        else:
            st.subheader("Administrator Login")
            with st.form("login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
            if submit:
                valid = (
                    hmac.compare_digest(username, ADMIN_USER)
                    and hmac.compare_digest(password, ADMIN_PASS)
                )
                if valid:
                    st.session_state.admin = True
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

    elif page == "Manage Notices":
        if not st.session_state.admin:
            st.warning("Please log in from the Admin Login page first.")
            st.stop()

        notices = all_notices()
        add_tab, edit_tab, delete_tab = st.tabs(
            ["Add Notice", "Edit Notice", "Delete Notice"]
        )

        with add_tab:
            with st.form("add_form", clear_on_submit=True):
                title = st.text_input("Title")
                description = st.text_area("Description")
                category = st.selectbox("Category", CATEGORIES)
                pub = st.date_input("Publish date", value=date.today())
                has_expiry = st.checkbox("Set expiry date")
                expiry = st.date_input("Expiry date", value=date.today()) if has_expiry else None
                submit = st.form_submit_button("Publish Notice")

            if submit:
                if not title.strip() or not description.strip():
                    st.error("Title and description are required.")
                elif expiry and expiry < pub:
                    st.error("Expiry date cannot be before publish date.")
                else:
                    save_notice(title, description, category, pub, expiry)
                    st.success("Notice published successfully.")
                    st.rerun()

        with edit_tab:
            if not notices:
                st.info("There are no notices to edit.")
            else:
                choices = {f"#{n['id']} - {n['title']}": n for n in notices}
                label = st.selectbox("Select notice", list(choices), key="edit_choice")
                selected = choices[label]
                with st.form("edit_form"):
                    title = st.text_input("Title", value=selected["title"])
                    description = st.text_area("Description", value=selected["description"])
                    category = st.selectbox(
                        "Category", CATEGORIES,
                        index=CATEGORIES.index(selected["category"])
                    )
                    pub = st.date_input(
                        "Publish date",
                        value=date.fromisoformat(selected["publish_date"])
                    )
                    has_expiry = st.checkbox(
                        "Set expiry date", value=bool(selected["expiry_date"])
                    )
                    expiry = st.date_input(
                        "Expiry date",
                        value=date.fromisoformat(selected["expiry_date"])
                        if selected["expiry_date"] else date.today()
                    ) if has_expiry else None
                    submit = st.form_submit_button("Save Changes")

                if submit:
                    if not title.strip() or not description.strip():
                        st.error("Title and description are required.")
                    elif expiry and expiry < pub:
                        st.error("Expiry date cannot be before publish date.")
                    else:
                        save_notice(
                            title, description, category, pub, expiry, selected["id"]
                        )
                        st.success("Notice updated.")
                        st.rerun()

        with delete_tab:
            if not notices:
                st.info("There are no notices to delete.")
            else:
                choices = {f"#{n['id']} - {n['title']}": n for n in notices}
                label = st.selectbox("Select notice", list(choices), key="delete_choice")
                selected = choices[label]
                st.warning("Selected notice: " + selected["title"])
                confirm = st.checkbox("I confirm deletion.")
                if st.button("Delete Notice", type="primary"):
                    if confirm:
                        with connect() as con:
                            con.execute("DELETE FROM notices WHERE id=?", (selected["id"],))
                        st.success("Notice deleted.")
                        st.rerun()
                    else:
                        st.error("Confirm deletion first.")

    st.divider()
    st.caption("Digital Notice Board System | Academic Project")


if __name__ == "__main__":
    main()
