import flet as ft
from flet_route import Params,Basket
from modal.authMysql import BDD_MYSQL
from dlgLoad import DLG
import bcrypt
import base64
from bdd import BDD_SQL

bddUser = BDD_MYSQL('user')

class LoginView:
    def __init__(self, navbar, appbar):
        self.navbar = navbar
        self.appbar = appbar

    def view(self,page: ft.Page, params:Params, basket:Basket):

        page.client_storage.clear()
        dbSql = BDD_SQL()
        self.navbar.visible = False
        self.appbar.visible = False
        page.update()

        def login(e):
            dlg = DLG.load()
            page.open(dlg)

            emptyUser = True

            try:
                for item in bddUser.getData():
                    
                    password = mdp.value.encode('utf-8')

                    encoded_value = item['mdp']

                    try:
                        hashed_bytes = base64.b64decode(encoded_value)
                        
                        if bcrypt.checkpw(password, hashed_bytes) and item['pseudo'] == user.value.lower():
                            if not agence.value:
                                agence.error_text = "Champ obligatoire"
                                page.update()
                                page.close(dlg)
                                return
                            
                            if item['agence'] == "0" or agence.value == item['agence']:
                                self.navbar.visible = True
                                self.appbar.visible = True
                                page.client_storage.set("user", item['pseudo'])
                                page.client_storage.set("mdp", mdp.value)
                                page.client_storage.set("id", item['id'])
                                page.client_storage.set("agence", agence.value)
                                page.client_storage.set("role", item['role'])
                                page.update()
                                emptyUser = False
                                page.go('/reporting')
                                return
                        
                    except Exception as e:
                        continue
                
                if emptyUser:
                    dlg = DLG.userFailed()
                    page.open(dlg)
                    
            except Exception as e:
                dlg = DLG.errorConnex()
                page.open(dlg)

        logo = ft.Container(ft.Image(src="/icon.png"), alignment=ft.alignment.center, margin=ft.margin.only(top=20))
        user = ft.TextField(label="Utilisateur", on_submit=login)
        mdp = ft.TextField(label="Mot de passe", can_reveal_password=True, on_submit=login, password=True)
        agence = ft.Dropdown(label="Agence")
        for item in dbSql.getData('agence'):
            agence.options.append(
                ft.dropdown.Option(key=str(item[2]).strip(), text=str(item[1]).strip())
            )
        btnSend = ft.ElevatedButton(
            "Se connecter", 
            on_click=login, 
            icon=ft.icons.LOGIN, 
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5), padding=17),
            expand=True,
            bgcolor="red",
            color="white"
        )
        
        

        return ft.View(
            "/login",
            controls=[
                ft.Column(
                    [
                        logo,
                        user,
                        mdp,
                        agence,
                        ft.Row([btnSend])
                    ]
                )
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            scroll="auto"
        )
