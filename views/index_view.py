import flet as ft
from flet_route import Params,Basket
from bdd import importExcelSql
from dlgLoad import DLG

class IndexView:
    def __init__(self):
        ...

    def view(self,page:ft.Page, params:Params, basket:Basket):
        def pick_files_result(e: ft.FilePickerResultEvent):
            selected_files.color = "black"
            if e.files:
                selected_files.value = ", ".join(map(lambda f: f.name, e.files))
                radieImport.bgcolor = "grey"
                radieImport.disabled = True
                depotImport.bgcolor = "grey"
                depotImport.disabled = True
            else:
                selected_files.value = "Aucune Sélection!"
            page.update()

        def pickFileRadie(e: ft.FilePickerResultEvent):
            textRadie.color = "black"
            if e.files:
                textRadie.value = ", ".join(map(lambda f: f.name, e.files))
                encoursImport.bgcolor = "grey"
                encoursImport.disabled = True
                depotImport.bgcolor = "grey"
                depotImport.disabled = True
            else:
                textRadie.value = "Aucune Sélection!"
            page.update()

        def pickFileDepot(e: ft.FilePickerResultEvent):
            textDepot.color = "black"
            if e.files:
                textDepot.value = ", ".join(map(lambda f: f.name, e.files))
                encoursImport.bgcolor = "grey"
                encoursImport.disabled = True
                radieImport.bgcolor = "grey"
                radieImport.disabled = True
            else:
                textDepot.value = "Aucune Sélection!"
            page.update()
            

        pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
        selected_files = ft.Text()

        pickRadie = ft.FilePicker(on_result=pickFileRadie)
        textRadie = ft.Text()

        pickDepot = ft.FilePicker(on_result=pickFileDepot)
        textDepot = ft.Text()

        page.overlay.append(pick_files_dialog)
        page.overlay.append(pickRadie)
        page.overlay.append(pickDepot)
        

        def filePickerTest(e):
            pick_files_dialog.pick_files(allowed_extensions=["xlsx"])

        def filePickerRadie(e):
            pickRadie.pick_files(allowed_extensions=["xlsx"])

        def filePickerDepot(e):
            pickDepot.pick_files(allowed_extensions=["html"])
        
        def valid(pick_file, text_value, param):
            if text_value.value != None and text_value.value != "Aucune Sélection!":
                pathFile = pick_file.result.files[0].path
                try:
                    dlg = DLG.load()
                    page.open(dlg)
                    importExcelSql(pathFile, param)
                    page.close(dlg)
                    text_value.value = "Importation terminée avec succès !"
                    text_value.color = "green"
                except KeyError:
                    text_value.value = "Fichier Incompatible!"
                    text_value.color = "red"
            page.update()

        
        def validImport(e):
            if encoursImport.disabled == False:
                valid(pick_files_dialog, selected_files, "encours")
            elif depotImport.disabled == False:
                valid(pickDepot, textDepot, "depot")
            else:
                valid(pickRadie, textRadie, "radie")


        def cancelImport(e):
            selected_files.value = "Aucune Sélection!"
            textRadie.value = "Aucune Sélection!"
            textDepot.value = "Aucune Sélection!"
            textRadie.color = selected_files.color = textDepot.color ="black"
            encoursImport.disabled = False
            radieImport.disabled = False
            depotImport.disabled = False
            encoursImport.bgcolor = ""
            radieImport.bgcolor = ""
            depotImport.bgcolor = ""
            page.update()

        def containerImport(image, func):
            return ft.Container(
                content=ft.Image(src=image),
                tooltip="Importer un fichier",
                border_radius=20,
                padding=10,
                expand=True,
                on_click=func
            )
        
        
        encoursImport = containerImport("/e.png", filePickerTest)
        radieImport = containerImport("/r.png", filePickerRadie)
        depotImport = containerImport("/d.png", filePickerDepot)


        def btnImport(text, color, icon, func):
            return ft.Container(
                content=ft.ElevatedButton(text=text, on_click=func, color=color, expand=True, icon=icon), 
                border_radius=20,
                border=ft.border.all(1, "#696B6A"),
                height=40,
            )
        
        
        btnValid = btnImport("Valider", "black", ft.icons.CHECK_ROUNDED, validImport)
        btnCancel = btnImport("Annuler", "red", ft.icons.CANCEL_OUTLINED, cancelImport)
        

        return ft.View(
            "/",
            controls=[
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            [
                                ft.Text("ENCOURS", size=25, weight=ft.FontWeight.W_500),
                                ft.Row([encoursImport], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([selected_files], alignment=ft.MainAxisAlignment.CENTER),
                            ],
                            col=3,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        ft.Column(
                            [
                                ft.Text("DEPOT", size=25, weight=ft.FontWeight.W_500),
                                ft.Row([depotImport], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([textDepot], alignment=ft.MainAxisAlignment.CENTER),
                            ],
                            col=3,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        ft.Column(
                            [
                                ft.Text("RADIE", size=25, weight=ft.FontWeight.W_500),
                                ft.Row([radieImport], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([textRadie], alignment=ft.MainAxisAlignment.CENTER),
                            ],
                            col=3,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND
                ),
                ft.Row(
                    [
                        ft.Column([btnValid, btnCancel], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER
        )
