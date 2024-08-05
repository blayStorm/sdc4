import flet as ft
from flet_route import Params,Basket
from bdd import BDD_SQL
from modal.authMysql import BDD_MYSQL
import locale
from dlgLoad import DLG
import requests

bddSuivi = BDD_MYSQL('suivi')
bddScoring = BDD_MYSQL('scoring')


class History(ft.UserControl):
    def __init__(self, param, page):
        super().__init__(expand=True)

        title = ft.Text("ACTION", size=30, weight=ft.FontWeight.W_500)

        self.param = param
        self.page = page

        paramUrl = f"{self.param.id_scoring}"

        self.dbScoring = bddScoring.getData(paramUrl)
        self.dbSuivi = bddSuivi.getData(paramUrl)


        self.caisse = self.dbScoring[0]['caisse']
        self.folio = self.dbScoring[0]['folio']
        self.rib = self.dbScoring[0]['rib']

        

        db = BDD_SQL()

        bddEncours = db.getData('encours')
        bddDepot = db.getData('depot')
        # print(bddDepot)

        bddAction = db.getData('actions')
        bddDetail = db.getData('detail_action')
        bddEtatDossier = db.getData('etat_dossier')
        bddEtatMbr = db.getData('etat_Membre')
        bddCategorie = db.getData('categorie')

        def change_date(e):
            inputDate.value = dateAct.value.strftime("%Y-%m-%d")
            inputDate.error_text = ""
            self.page.update()

        def dismiss_date(e):
            if dateAct.value:
                inputDate.value = dateAct.value.strftime("%Y-%m-%d")
                inputDate.error_text = ""
            else:
                inputDate.error_text = "Champ obligatoire"
            self.page.update()

        dateAct = ft.DatePicker(
            on_change=change_date,
            on_dismiss=dismiss_date,
            cancel_text="Annuler",
            help_text="Choisir une date"
        )

        self.page.overlay.append(dateAct)

        date_button = ft.IconButton(
            icon=ft.icons.CALENDAR_MONTH,
            icon_color="black",
            tooltip="Date action",
            on_click=lambda _: dateAct.pick_date()
        )

        inputDate = ft.TextField(
            hint_text="Date action*",  
            suffix_text="(date action)",
            border_width=0,
            expand=True,
            read_only=True
        )

        

        def newAction(e):
            caisse = self.caisse
            folio = self.folio
            rib = self.rib

            def errorInput(param):
                param.error_text = "Champ obligatoire" if not param.value else ""
                self.page.update()

            def hideError(e):
                e.control.error_text = "Champ obligatoire" if not e.control.value else ""
                self.page.update()

            def sendSuivi(e):
                if not action.value or not detail.value or not inputDate.value or not etatD.value or not etatM.value or not categorie.value:
                    errorInput(action)
                    errorInput(detail)
                    errorInput(inputDate)
                    errorInput(etatD)
                    errorInput(etatM)
                    errorInput(categorie)
                    return
                
                def dropDText(param):
                    if param.value:
                        op = list(filter(lambda x: str(param.value) == str(x.key), param.options))
                        return op[0].text
                    else:
                        return ""
                    
                
                dlg = DLG.load() 
                self.page.dialog = dlg
                dlg.open = True
                self.page.update()


                try:
                    sendSuivi = bddSuivi.postData(
                        arg=[
                                {
                                    "id_scoring": f"{self.param.id_scoring}",
                                    "adresse_actuel": f"{adresse_act.value.strip()}",
                                    "date_action": f"{inputDate.value}",
                                    "etat_dossier": f"{dropDText(etatD)}",
                                    "etat_membre": f"{dropDText(etatM)}",
                                    "action": f"{dropDText(action)}",
                                    "detail": f"{dropDText(detail)}",
                                    "montant_recouvre": f"{recouvre.data}",
                                    "charge": f"{charge.value}",
                                    "encours_act": f"{encours_act.value}",
                                    "retard_act": f"{retardAct.value}",
                                    "categorie": f"{dropDText(categorie)}",
                                    "responsable": f"{responsableSuivi.value}",
                                    "rq": f"{comment.value.strip()}"
                                }
                            ]
                        )
                    
                    if sendSuivi:
                        dlg = DLG.valid() 
                        self.page.dialog = dlg
                        self.data_table.rows.insert(
                            0,                    
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text(f"{inputDate.value}")),
                                    ft.DataCell(ft.Text(f"{dropDText(action)}")),
                                    ft.DataCell(ft.Text(f"{dropDText(detail)}")),
                                    ft.DataCell(ft.Text(f"{dropDText(etatD)}")),
                                    ft.DataCell(ft.Text(f"{dropDText(etatM)}")),
                                    ft.DataCell(ft.Text(f"{adresse_act.value.strip()}")),
                                    ft.DataCell(ft.Text(f"{recouvre.value}")),
                                    ft.DataCell(ft.Text(f"{locale.format_string("%.2f", float(charge.value), grouping=True)}")),
                                    ft.DataCell(ft.Text(f"{locale.format_string("%.2f", float(encours_act.value), grouping=True)}")),
                                    ft.DataCell(ft.Text(f"{retardAct.value}")),
                                    ft.DataCell(ft.Text(f"{dropDText(categorie)}")),
                                    ft.DataCell(ft.Text(f"{responsableSuivi.value}")),
                                    ft.DataCell(ft.Text(f"{comment.value.strip()}"))
                                ]
                            )
                        )
                        self.update()
                    
                    else:
                        dlg = DLG.errorExcept2() 
                        self.page.dialog = dlg

                except requests.exceptions.RequestException as e:
                    dlg = DLG.errorExcept2() 
                    self.page.dialog = dlg
                
                dlg.open = True
                self.page.update()

            try:
                myfilter = list(list(filter(lambda x: caisse == str(x[1]).lower() and folio == str(x[2])[:-6].lower() and rib == str(x[3]).lower(), bddEncours)))
                myfilterR = list(list(filter(lambda x: caisse == str(x[3]).lower() and folio == str(x[4]).lower() and 'oui' != str(x[1]).lower(), bddDepot)))

                if len(myfilterR) > 0:
                    mntRecouvre = locale.format_string("%.2f", float(myfilterR[0][6]), grouping=True)
                    mntData = float(myfilterR[0][6])
                else:
                    mntRecouvre = 0
                    mntData = 0
                
                dateA = ft.Container(
                    content=ft.Row([inputDate, date_button]),
                    border=ft.border.all(1, "black"),
                    border_radius=5, 
                    expand=True
                )

                def dropDownFunc(param, bdd):
                    for item in bdd:
                        param.options.append(
                            ft.dropdown.Option(key=str(item[0]).strip(), text=str(item[1]).strip())
                        )

                def dropDetail(e):
                    hideError(e)
                    detail.options.clear()
                    for item in bddDetail:
                        if str(item[2]) == str(e.control.value):
                            detail.options.append(
                                ft.dropdown.Option(key=str(item[0]).strip(), text=str(item[1]).strip())
                            ) 
                    self.page.update()
                
                responsableSuivi = ft.TextField(expand=True, label="Responsable", value=myfilter[0][17], read_only=True)
                encours_act = ft.TextField(expand=True, label="Encours actuel", value=myfilter[0][10], read_only=True)
                action = ft.Dropdown(expand=True, label="Action*", on_change=dropDetail)
                detail = ft.Dropdown(expand=True, label="Détails*", on_change=hideError)
                etatD = ft.Dropdown(expand=True, label="Évolution du dossier*", on_change=hideError)
                etatM = ft.Dropdown(expand=True, label="Etat membre*", on_change=hideError, value=1)
                categorie = ft.Dropdown(expand=True, label="Catégorie*", on_change=hideError)
                retardAct = ft.TextField(expand=True, label="Retard", value=myfilter[0][16], read_only=True)
                charge = ft.TextField(expand=True, label="Charge", input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""), value=0)
                recouvre = ft.TextField(expand=True, label="Montant recouvré", value=mntRecouvre, read_only=True, data=mntData)
                adresse_act = ft.TextField(expand=True, label="Adresse actuelle")
                comment = ft.TextField(expand=True, label="Observations", multiline=True)
                

                def pick_files_result(e: ft.FilePickerResultEvent):
                    selected_files.value = (
                        ", ".join(map(lambda f: f.name, e.files)) if e.files else "Aucune Sélection!"
                    )
                    selected_files.update()
                    

                pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
                selected_files = ft.Text()

                self.page.overlay.append(pick_files_dialog)

                attachment = ft.ElevatedButton(
                                            "Pièce jointe",
                                            icon=ft.icons.ATTACH_FILE,
                                            on_click=lambda e: pick_files_dialog.pick_files(allowed_extensions=["pdf"]),
                                            expand=True
                                        )

                dropDownFunc(action, bddAction)
                dropDownFunc(etatD, bddEtatDossier)
                dropDownFunc(etatM, bddEtatMbr)
                dropDownFunc(categorie, bddCategorie)
                

                def closeDlg(e):
                    dlg.open = False,
                    self.page.update()

                dlg = ft.AlertDialog(
                    adaptive=True,
                    scrollable=True,
                    bgcolor="white",
                    modal=True,
                    title=ft.Row([ft.Text('Nouvelle action')], alignment="center"),
                    content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row([dateA, responsableSuivi]),
                                        ft.Row([recouvre, charge]),
                                        ft.Row([action, detail]),
                                        ft.Row([etatD, etatM]),
                                        ft.Row([retardAct, categorie]),
                                        ft.Row([encours_act, adresse_act]),
                                        ft.Row([comment]),
                                        ft.Row([attachment, selected_files]),
                                    ],
                                    expand=True,
                                    scroll="auto"
                                ),
                                bgcolor="white",
                                padding=ft.padding.only(top=10, bottom=10),
                                border_radius=5
                            ),
                    actions=[
                        ft.ElevatedButton("Annuler", on_click=closeDlg, bgcolor="red", color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))),
                        ft.ElevatedButton("Valider", on_click=sendSuivi, bgcolor="#FEC61F", color="black", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))),
                    ],
                    actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                self.page.open(dlg)
            except:
                dlg = DLG.errorExcept2() 
                self.page.dialog = dlg
            
            dlg.open = True
            self.page.update()


        btnNewSuivi = ft.ElevatedButton(
                        icon=ft.icons.ADD_BOX_OUTLINED,
                        text="Nouvelle action",
                        style=ft.ButtonStyle(
                            color="black",
                            shape=ft.RoundedRectangleBorder(radius=5)
                        ),
                        on_click=newAction,
                        visible=False
                    )
        
        
        btnNewSuivi.visible = True if int(self.page.client_storage.get('role')) > 1 else False


        self.menubar = ft.Container(
            expand=True,
            bgcolor="#FEC61F",
            border_radius=5,
            padding=10,
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Text("Caisse: "),
                            ft.ElevatedButton(
                                self.caisse,  
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=5)
                                )
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Text("Folio: "),
                            ft.ElevatedButton(
                                self.folio,  
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=5)
                                )
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Text("Rib: "),
                            ft.ElevatedButton(
                                self.rib,  
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=5)
                                )
                            ),
                        ]
                    ),
                    btnNewSuivi
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        self.data_table = ft.DataTable(
            border=ft.border.all(1, "black"),
            vertical_lines=ft.BorderSide(1, "grey"),
            border_radius=10,
            data_row_color={
                ft.MaterialState.SELECTED: "blue"
            },
            columns=[
                ft.DataColumn(ft.Text("Date action")),
                ft.DataColumn(ft.Text("Action")),
                ft.DataColumn(ft.Text("Détails")),
                ft.DataColumn(ft.Text("Etat dossier")),
                ft.DataColumn(ft.Text("Etat membre")),
                ft.DataColumn(ft.Text("Adresse actuelle")),
                ft.DataColumn(ft.Text("Récouvrement (j)")),
                ft.DataColumn(ft.Text("Charge")),
                ft.DataColumn(ft.Text("Encours (j)")),
                ft.DataColumn(ft.Text("Retard (j)")),
                ft.DataColumn(ft.Text("Catégorie")),
                ft.DataColumn(ft.Text("Responsable (j)")),
                ft.DataColumn(ft.Text("Remarque(s)"))
            ]
        )


        for x in self.dbSuivi:
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(x['date_action'])),
                        ft.DataCell(ft.Text(x['action'])),
                        ft.DataCell(ft.Text(x['detail'])),
                        ft.DataCell(ft.Text(x['etat_dossier'])),
                        ft.DataCell(ft.Text(x['etat_membre'])),
                        ft.DataCell(ft.Text(x['adresse_actuel'])),
                        ft.DataCell(ft.Text(locale.format_string("%.2f", float(x['montant_recouvre']), grouping=True))),
                        ft.DataCell(ft.Text(locale.format_string("%.2f", float(x['charge']), grouping=True))),
                        ft.DataCell(ft.Text(locale.format_string("%.2f", float(x['encours_act']), grouping=True))),
                        ft.DataCell(ft.Text(x['retard_act'])),
                        ft.DataCell(ft.Text(x['categorie'])),
                        ft.DataCell(ft.Text(x['responsable'])),
                        ft.DataCell(ft.Text(x['rq']))
                    ]
                )
            )


        name = ft.TextField(read_only=True, label="Nom", value=self.dbScoring[0]['nom'])
        cin = ft.TextField(read_only=True, label="CIN", value=self.dbScoring[0]['cin'])
        phone = ft.TextField(read_only=True, label="Téléphone", value=self.dbScoring[0]['phone'])
        adresse = ft.TextField(read_only=True, label="Adresse", value=self.dbScoring[0]['adresse'])
        dateO = ft.TextField(read_only=True, label="Date octroi", value=self.dbScoring[0]['date_octroi'])
        crd = ft.TextField(read_only=True, label="Montant", value=self.dbScoring[0]['montant'])
        encours = ft.TextField(read_only=True, label="Encours ou Capital passé en perte", value=self.dbScoring[0]['encours'])
        retard = ft.TextField(read_only=True, label="Retard", value=self.dbScoring[0]['retard'])
        score = ft.TextField(read_only=True, label="Score", value=self.dbScoring[0]['score'])
        dateP = ft.TextField(read_only=True, label="Date passation", value=self.dbScoring[0]['date_passation'])
        responsable = ft.TextField(read_only=True, label="Responsable", value=self.dbScoring[0]['responsable'])


        self.form = ft.Container(
            bgcolor=ft.colors.GREY_100,
            border_radius=5,
            col=3,
            padding=10,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(
                                    "Information Scoring", 
                                    size=20, 
                                    font_family="Arial"
                                )
                            )
                        ], 
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Column(
                        [
                            ft.Divider(height=10, color=ft.colors.GREY_100),
                            name,
                            cin,
                            phone, 
                            adresse, 
                            dateO,
                            crd,
                            encours, 
                            retard,
                            score,
                            dateP,
                            responsable
                        ],
                        expand=True,
                        scroll="auto"
                    )
                ]
            )
        )

        self.table = ft.Container(
            border_radius=10,
            col=9,
            content=ft.Column(
                [
                    ft.Container(
                        padding=10,
                        content=ft.Column(
                            [
                                ft.Row([title], alignment="center"),
                                ft.Row([self.menubar]),
                            ]
                        )
                    ),
                    ft.Column(
                        [
                            ft.Container(
                                content=ft.ResponsiveRow(
                                    [
                                        ft.Row([self.data_table], scroll="always")
                                    ]
                                ),
                                padding=10
                            )
                        ],
                        expand=True,
                        scroll="auto"
                    )
                ]
            )
        )

        self.content = ft.ResponsiveRow(
            controls=[
                self.form,
                self.table
            ]
        )

    def build(self):
        return self.content