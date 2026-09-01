import reflex as rx

from app.pages.auth import login_page, signup_page
from app.pages.friends import friends_page
from app.pages.home import home_page
from app.pages.messages import messages_page
from app.pages.profile import profile_page
from app.states.auth_state import AuthState
from app.states.friends_state import FriendsState
from app.states.messages_state import MessagesState
from app.states.profile_state import ProfileState
from app.states.social_state import SocialState


def index() -> rx.Component:
    return home_page()


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            cross_origin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/", on_load=AuthState.check_session)
app.add_page(
    friends_page,
    route="/friends",
    on_load=[
        AuthState.guard_session,
        FriendsState.load_all,
        SocialState.load_side_data,
    ],
)
app.add_page(
    messages_page,
    route="/messages",
    on_load=[
        AuthState.guard_session,
        MessagesState.load_page,
        SocialState.load_side_data,
    ],
)
app.add_page(
    profile_page,
    route="/profile",
    on_load=[
        AuthState.guard_session,
        ProfileState.load_profile,
        SocialState.load_side_data,
    ],
)
app.add_page(
    login_page, route="/login", on_load=AuthState.redirect_if_authenticated
)
app.add_page(
    signup_page, route="/signup", on_load=AuthState.redirect_if_authenticated
)
