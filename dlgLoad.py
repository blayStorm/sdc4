import flet as ft

page = ft.Page

class DLG:
    def load():
        return ft.AlertDialog(
            modal=True,
            title=ft.Row([ft.ProgressRing()], alignment="center"),
            actions=[ft.Text("Veuillez patienter...")],
            actions_alignment="center"
        )
    
    def btnClose(param):
        return ft.TextButton(content=ft.Text("OK", color="black", weight=ft.FontWeight.W_500), on_click=lambda _: page.close(param))
    
    def valid():
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Row([ft.Icon(name=ft.icons.CHECK_CIRCLE_OUTLINED, size=75, color="green")], alignment="center"),
            content=ft.Row([ft.Text("Validation réussie")], alignment="center"),
            actions_alignment="center"
        )
        b = DLG.btnClose(dlg)
        dlg.actions.append(b)
        return dlg
    
    def checkEmpty():
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Row([ft.Icon(name=ft.icons.DANGEROUS_OUTLINED, size=75, color="red")], alignment="center"),
            content=ft.Row([ft.Text("Tous les champs marqués d'un (*) sont obligatoires.")], alignment="center"),
            actions_alignment="center"
        )
        b = DLG.btnClose(dlg)
        dlg.actions.append(b)
        return dlg
    
    def errorConnex():
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Row([ft.Icon(name=ft.icons.WARNING_AMBER_ROUNDED, size=75, color="amber")], alignment="center"),
            content=ft.Row([ft.Text("Echec de connexion...")], alignment="center"),
            actions_alignment="center"
        )
        b = DLG.btnClose(dlg)
        dlg.actions.append(b)
        return dlg
    
    def errorExcept():
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Row([ft.Icon(name=ft.icons.DANGEROUS_OUTLINED, size=75, color="red")], alignment="center"),
            content=ft.Row([ft.Text("Interruption de connexion ou dossier déjà évalué.")], alignment="center"),
            actions_alignment="center"
        )
        b = DLG.btnClose(dlg)
        dlg.actions.append(b)
        return dlg
    
    def errorExcept2():
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Row([ft.Icon(name=ft.icons.WARNING_AMBER_ROUNDED, size=75, color="amber")], alignment="center"),
            content=ft.Row([ft.Text("Interruption de connexion ou situation non mise à jour.")], alignment="center"),
            actions_alignment="center"
        )
        b = DLG.btnClose(dlg)
        dlg.actions.append(b)
        return dlg
    
    def agentEmpty():
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Row([ft.Icon(name=ft.icons.WARNING_AMBER_ROUNDED, size=75, color="amber")], alignment="center"),
            content=ft.Row([ft.Text("Dossier introuvable ou situation non mise à jour.")], alignment="center"),
            actions_alignment="center"
        )
        b = DLG.btnClose(dlg)
        dlg.actions.append(b)
        return dlg
    
    def userFailed():
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Row([ft.Icon(name=ft.icons.DANGEROUS_OUTLINED, size=75, color="red")], alignment="center"),
            content=ft.Row([ft.Text("Utilisateur inconnue!")], alignment="center"),
            actions_alignment="center"
        )
        b = DLG.btnClose(dlg)
        dlg.actions.append(b)
        return dlg
    
    def errorSpecial(text):
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Row([ft.Icon(name=ft.icons.DANGEROUS_OUTLINED, size=75, color="red")], alignment="center"),
            content=ft.Row([ft.Text(text)], alignment="center"),
            actions_alignment="center"
        )
        b = DLG.btnClose(dlg)
        dlg.actions.append(b)
        return dlg
    
    def guide(text):
        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Row([ft.Icon(name=ft.icons.DANGEROUS_OUTLINED, size=75, color="red")], alignment="center"),
            content=ft.Row([ft.Text(text)], alignment="center"),
            actions_alignment="center"
        )
        b = DLG.btnClose(dlg)
        dlg.actions.append(b)
        return dlg