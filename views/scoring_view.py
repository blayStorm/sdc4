import flet as ft
from flet_route import Params,Basket
from views.action.scoring import Scoring


class ScoringView:
    def __init__(self):
        ...

    def view(self,page:ft.Page,params:Params,basket:Basket):

        return ft.View(
            "/scoring",
            controls=[Scoring(page)]
        )
