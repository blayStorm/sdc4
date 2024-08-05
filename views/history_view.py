import flet as ft
from flet_route import Params,Basket
from views.action.history import History

class HistoryView:
    def __init__(self):
        ...

    def view(self, page:ft.Page, params:Params, basket:Basket):
        # print(params)
        # print(basket)

        return ft.View(
            "/history/:id_scoring",
            controls=[
                History(params, page)
            ]
        )
