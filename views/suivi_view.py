import flet as ft
from flet_route import Params,Basket
from views.action.suivi import Suivi

class SuiviView:
    def __init__(self):
        ...

    def view(self,page:ft.Page, params:Params, basket:Basket):

        return ft.View(
            "/suivi",
            controls=[
                Suivi(page)
            ]
        )