import reflex as rx

from app.pages.auth import login_page, signup_page
from app.pages.friends import friends_page
from app.pages.game_lobby import game_lobby_page
from app.pages.game_room import game_room_page
from app.pages.games import games_page
from app.pages.home import home_page
from app.pages.messages import messages_page
from app.pages.profile import profile_page
from app.pages.settings import settings_page
from app.pages.transactions import transactions_page
from app.states.auth_state import AuthState
from app.states.friends_state import FriendsState
from app.states.games_state import GamesState
from app.states.messages_state import MessagesState
from app.states.profile_state import ProfileState
from app.states.room_state import RoomState
from app.states.settings_state import SettingsState
from app.states.social_state import SocialState
from app.states.wallet_state import WalletState


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
    game_lobby_page,
    route="/games/[game_slug]",
    on_load=[AuthState.guard_session, GamesState.load_lobby],
)
app.add_page(
    games_page,
    route="/games",
    on_load=[AuthState.guard_session, GamesState.load_hub],
)
app.add_page(
    game_room_page,
    route="/game/room/[room_id]",
    on_load=[AuthState.guard_session, RoomState.load_room],
)
app.add_page(
    transactions_page,
    route="/transactions",
    on_load=[AuthState.guard_session, WalletState.load_wallet],
)
app.add_page(
    settings_page,
    route="/settings",
    on_load=[AuthState.guard_session, SettingsState.load_settings],
)
app.add_page(
    login_page, route="/login", on_load=AuthState.redirect_if_authenticated
)
app.add_page(
    signup_page, route="/signup", on_load=AuthState.redirect_if_authenticated
)
