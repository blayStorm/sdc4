import flet as ft
from flet_route import Params,Basket
from views.action.reporting import Reporting

class ReportingView:
    def __init__(self):
        ...

    def view(self,page:ft.Page, params:Params, basket:Basket):

        return ft.View(
            "/reporting",
            controls=[
                Reporting(page)
            ]
        )