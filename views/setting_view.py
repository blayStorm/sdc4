import flet as ft
from flet_route import Params,Basket
from modal.authMysql import BDD_MYSQL
from dlgLoad import DLG
import bcrypt
import base64

class SettingView:
    def __init__(self):
        self.bddUser = BDD_MYSQL('user')

    def view(self, page: ft.Page, params:Params, basket:Basket):

        def loginUpdate():
            if mdpC.value and mdpU.value:
                if mdpC.value == mdpU.value:
                    dlg = DLG.load()
                    page.open(dlg)

                    try:

                        password = mdpC.value.encode('utf-8')
                        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

                        hashed_str = base64.b64encode(hashed).decode('utf-8')

                        id = page.client_storage.get('id')
                        sendUpdate = self.bddUser.setData(
                                        filter=f"{id}", 
                                        arg=[
                                                {
                                                    "pseudo": f"{str(userUpdate.value).lower()}",
                                                    "mdp": f"{hashed_str}",
                                                }
                                            ]
                                        )
                        if sendUpdate:
                            page.go('/login')

                    except Exception as e:
                        dlg = DLG.errorSpecial(text=f"{e}")
                        page.open(dlg)

                else:
                    dlg = DLG.errorSpecial(text="Mot de passe différent")
                    page.open(dlg)

            else:
                if not mdpC.value:
                    mdpC.error_text ="Champ obligatoire"

                if not mdpU.value:
                    mdpU.error_text ="Champ obligatoire"
                    
                page.update()


        def checkUpdate(e):
            if mdp.value != page.client_storage.get('mdp'):
                mdp.error_text = "Mot de passe incorrect"
                page.update()
            else:
                loginUpdate()

        userUpdate = ft.TextField(bgcolor="white", label="Pseudo", value=page.client_storage.get("user"))
        mdp = ft.TextField(bgcolor="white", label="Ancien mot de passe", password=True)
        mdpU = ft.TextField(bgcolor="white", label="Nouveau mot de passe", password=True)
        mdpC = ft.TextField(bgcolor="white", label="Confirmer le mot de passe", password=True)
        sendU = ft.ElevatedButton(
            "Mettre à jour", 
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5), padding=17), 
            bgcolor="red",
            color="white",
            expand=True,
            on_click=checkUpdate
        )

        return ft.View(
            "/setting",
            controls=[
                ft.Column(
                    [
                        ft.Row([ft.Text("Paramètre", size=30, weight=ft.FontWeight.W_500)], alignment="center"),
                        ft.Container(
                            bgcolor="#FEC61F",
                            border_radius=5,
                            padding=20,
                            content=ft.Column(
                                [
                                    userUpdate,
                                    mdp,
                                    mdpU,
                                    mdpC,
                                    ft.Row([sendU])
                                ]
                            )
                        )
                    ]
                )
            ]
        )
