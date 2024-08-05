import flet as ft
from flet_route import Routing, path
from views.index_view import IndexView 
from views.suivi_view import SuiviView
from views.setting_view import SettingView 
from views.login_view import LoginView 
from views.scoring_view import ScoringView 
from views.history_view import HistoryView 
from views.reporting_view import ReportingView 
from dlgLoad import DLG
from bdd import BDD_SQL

def main(page: ft.Page):

    page.title = "Suivi des dossiers contentieux"

    page.fonts = {
        "digital7": "/fonts/Seven Segment.ttf",
    }

    page.adaptive = True

    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[ft.Locale("fr", "FR")],
        current_locale=ft.Locale("fr", "FR")
    )
    page.client_storage.clear()
    page.window.maximized = True

    def route(e):
        if not page.client_storage.contains_key("user"):
            return
        
        db = BDD_SQL()
        if len(db.getData('depot')) == 0:
            e.control.selected_index = 0
            page.update()
            dlg = DLG.errorSpecial("La base de dépôt est vide!")
            page.open(dlg)
            return
        
        if len(db.getData('encours')) == 0:
            e.control.selected_index = 0
            page.update()
            dlg = DLG.errorSpecial("La base de la situation encours est vide!")
            page.open(dlg)
            return
        
        param = e.control.selected_index

        if param != 0:
            dlg = DLG.load()
            page.open(dlg)

        if param == 0:
            routeGo = '/'
        if param == 1:
            if page.client_storage.get("role") == '1':
                dlg = DLG.errorSpecial("Accès refusé!")
                page.open(dlg)
                return
            routeGo = '/scoring'
        if param == 2:
            routeGo = '/suivi'
        if param == 3:
            routeGo = '/reporting'
        if page.route == routeGo:
            if param != 0:
                try:
                    page.close(dlg)
                except Exception as e:
                    print(e)
            return
        
        page.go(f'{routeGo}')

    def routeSetting(e):
        if not page.client_storage.contains_key("user"):
            return
        page.go('/setting')

    def logout(e):
        navBar.visible = False
        navBar.selected_index = 0
        page.client_storage.clear()
        page.go('/login')

    navBar = ft.NavigationBar(
                height=60,
                bgcolor=ft.colors.with_opacity(0.5, "#696969"),
                indicator_color="amber",
                destinations=[
                    ft.NavigationBarDestination(
                        icon=ft.icons.UPLOAD_OUTLINED,
                        selected_icon=ft.icons.UPLOAD,
                        label="Import",
                        tooltip="Importer un fichier"
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.icons.LOOKS_5_OUTLINED,
                        selected_icon=ft.icons.LOOKS_ONE,
                        label="Scoring",
                        tooltip="Evaluer le score du dossier"
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.icons.LIBRARY_ADD_CHECK_OUTLINED,
                        selected_icon=ft.icons.LIBRARY_ADD_CHECK,
                        label="Suivi",
                        tooltip="Faire le suivi du dossier"
                    ),
                    ft.NavigationBarDestination(
                        icon=ft.icons.INSERT_CHART_OUTLINED_ROUNDED,
                        selected_icon=ft.icons.INSERT_CHART_ROUNDED,
                        label="Reporting"
                    )
                ],
                on_change=route,
                visible=False
            )
    
    appBar = ft.AppBar(
            bgcolor="#DF2041", 
            actions=[
                ft.IconButton(icon=ft.icons.QUESTION_MARK, icon_color="white", icon_size=20),
                ft.PopupMenuButton(
                    icon=ft.icons.PERSON,
                    icon_color="white",
                    items=[
                        ft.PopupMenuItem(icon=ft.icons.SETTINGS, text="Paramètre", on_click=routeSetting),
                        ft.PopupMenuItem(icon=ft.icons.LOGOUT, text="Se déconnecter", on_click=logout)
                    ]
                )
            ],
            visible=False
        )
    
    app_routes = [
        path(url="/", clear=True, view=IndexView().view),
        path(url="/scoring", clear=True, view=ScoringView().view),
        path(url="/suivi", clear=True, view=SuiviView().view),
        path(url="/setting", clear=True, view=SettingView().view),
        path(url="/login", clear=True, view=LoginView(navbar=navBar, appbar=appBar).view),
        path(url="/history/:id_scoring", clear=True, view=HistoryView().view),
        path(url="/reporting", clear=True, view=ReportingView().view),
    ]
    
    

    Routing(
        navigation_bar=navBar,
        page=page, 
        app_routes=app_routes, 
        appbar=appBar
    )

    print('START')
    
    page.go('/login')

ft.app(target=main, assets_dir="assets")
