import flet as ft
import requests
from bdd import BDD_SQL
from modal.authMysql import BDD_MYSQL
import locale
import datetime
from views.tools.pdfScore import outputPDF
from dlgLoad import DLG

locale.setlocale(locale.LC_ALL, 'French_France.1252')

bddSuivi = BDD_MYSQL('suivi')
bddScoring = BDD_MYSQL('scoring')
bddCaution = BDD_MYSQL('caution')

class Scoring(ft.UserControl):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page

        dbSql = BDD_SQL()
        bddEncours = dbSql.getData('encours')
        bddRadie = dbSql.getData('radie')
        bddAgence = dbSql.getData('agence', f'conso={self.page.client_storage.get('agence')}')
        bddCaisse = dbSql.getData('caisse', f'conso={self.page.client_storage.get('agence')}')

        
        def hideError(e):
            if not isinstance(e.control, ft.Checkbox):
                e.control.error_text = "Champ obligatoire" if not e.control.value else ""
                self.update()
        
        self.confPret = False
        self.confNant = False
        self.confAct = False
        self.confConv = False
        
        self.dlg = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Impression du fichier PDF en cours...", text_align="center", size=15),
                        actions_alignment="center"
                    ) 
        
        
        
        self.closePDF = ft.ElevatedButton(
                            "OK", 
                            on_click=lambda _: self.page.close(self.dlg2),
                            bgcolor="red",
                            color="white"
                        )
        
        self.dlg2 = ft.AlertDialog(
                        modal=False,
                        title=ft.Text("Téléchargement du PDF réussi.", text_align="center", size=15),
                        actions=[self.closePDF],
                        actions_alignment="center"
                    ) 

        def sendScoring(e):
            if not agent.value:
                dlg = DLG.agentEmpty() 
                self.page.open(dlg)
                return
            
            
            
            self.confPret = True if self.nbrConfPret == 4 else False
            self.confNant = True if self.nbrConfNant == 4 else False
            self.confAct = True if self.nbrConfAct == 4 else False
            self.confConv = True if self.nbrConfConv == 4 else False
            
            def errorInput(param):
                param.error_text = "Champ obligatoire" if not param.value else ""

            if not cinMbr.value or (not checkMat.value and not checkImmo.value) or not date_picker.value or not inputFolio.value or not inputCaisse.value or not inputRib.value:
                dlg = DLG.checkEmpty() 
                self.page.open(dlg)
                errorInput(cinMbr)
                errorInput(inputFolio)
                errorInput(inputRib)
                errorInput(inputCaisse)
                inputDate.error_text = "Champ obligatoire" if not date_picker.value else ""
                self.update()
                self.page.update()
                return
            
            self.dlg.actions.clear()
            self.dlg.actions.append(
                ft.ElevatedButton(
                    "Imprimer", 
                    bgcolor="#FEC61F",
                    color="black",
                    icon=ft.icons.DOWNLOAD,
                    on_click=lambda e: saveme.save_file(allowed_extensions=['pdf'], file_name=f"recap_{inputCaisse.value}_{inputFolio.value}_{inputRib.value}.pdf"),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                )
            )
            self.page.update()

            self.update()
            dlg = DLG.load() 
            self.page.open(dlg)

            try:
                sendScore = bddScoring.postData(
                    arg=[
                            {
                                "nom": f"{nameMbr.value.strip()}",
                                "agence": self.page.client_storage.get('agence'),
                                "caisse": f"{inputCaisse.value.strip()}",
                                "folio": f"{inputFolio.value}",
                                "rib": f"{inputRib.value}",
                                "cin": f"{cinMbr.value}",
                                "phone": f"{phoneMbr.value}",
                                "adresse": f"{adresseMbr.value.strip()}",
                                "date_octroi": f"{dateCrdt.value}",
                                "montant": f"{montantCrdt.value.strip()}",
                                "encours": f"{crd.value.strip()}",
                                "retard": f"{retard.value}",
                                "score": f"{score.value}",
                                "date_passation": f"{inputDate.value}",
                                "responsable": f"{agent.value}"
                            }
                        ]
                    )

                sendSuivi = False
                sendCaution = False

                if sendScore:
                    max_id = int(sendScore[0]['max_id'])
                    sendSuivi = bddSuivi.postData(
                        arg=[
                                {
                                    "id_scoring": f"{max_id}",
                                    "date_action": f"{inputDate.value}",
                                    "responsable": f"{agent.value}",
                                    "retard_act": f"{retard.value}"
                                }
                            ]
                        )
                    
                    hypoCau = 'oui' if hypothequeCau.value else 'non'
                    sendCaution = bddCaution.postData(
                        arg=[
                                {
                                    "id_scoring": f"{max_id}",
                                    "nom": f"{nameCau.value.strip()}",
                                    "adresse": f"{adresseCau.value}",
                                    "adresse_act": f"{actuelCau.value}",
                                    "cin": f"{cinCau.value}",
                                    "hypotheque": f"{hypoCau}"
                                }
                            ]
                        )
                    

                if sendScore and sendSuivi and sendCaution:
                    self.page.open(self.dlg)
                
                else:
                    dlg = DLG.errorExcept() 
                    self.page.open(dlg)

            except requests.exceptions.RequestException as e:
                dlg = DLG.errorExcept() 
                self.page.open(dlg)

        def pdfImmo():
            nbrT = 1
            typeTer = []
            for item in self.tableTerrain.rows:
                seingC = 0
                hypoTer = False
                sousSeingC = False
                beImmo = False
                for i in range(2, len(item.cells)):
                    if i == 2:
                        if item.cells[i].content.value:
                            beImmo = True

                    if i == 3 or i == 4:
                        if item.cells[i].content.value:
                            seingC += 1

                    if i == 5:
                        if item.cells[i].content.value:
                            hypoTer = True

                if seingC == 2:
                    sousSeingC = True
                

                typeTer.append(
                    {"BE": beImmo, "seingConforme": sousSeingC, "hypotheque": hypoTer}
                )
                
                nbrT += 1
            
            return typeTer

        def downloadPDF(e: ft.FilePickerResultEvent):
            save_location = e.path
            if save_location:
                while True:
                    try:
                        pdf = outputPDF(
                                    agence=bddAgence[0][1],
                                    caisse=next((option.text for option in inputCaisse.options if option.key == inputCaisse.value), None),
                                    folio=inputFolio.value,
                                    nom=nameMbr.value,
                                    rib=inputRib.value,
                                    dateP=date_picker.value.strftime("%Y-%m-%d"),
                                    dateO=dateCrdt.value,
                                    montant=crd.value,
                                    duree=duree.value,
                                    responsable=agent.value,
                                    retard=retard.value,
                                    capital=capital.value,
                                    interet=interet.value,
                                    penalite=penalite.value,
                                    scoring=score.value,
                                    existMbr=existeMbr.value,
                                    solveMbr=solvablembr.value,
                                    trouveMbr=trouveMbr.value,
                                    existCau=existeCau.value,
                                    solveCau=solvableCau.value,
                                    trouveCau=trouveCau.value,
                                    hypoCau=hypothequeCau.value,
                                    immo=checkImmo.value,
                                    mae=checkMat.value,
                                    typeMae=[
                                        {"exist": existMae.value, "BE": beMae.value, "privilege": privMae.value},
                                        {"exist": existVH.value, "BE": beVH.value, "privilege": privVH.value, "gage": gageVH.value, "grise": griseVH.value},
                                        {"exist": existBat.value, "BE": beBat.value, "privilege": privBat.value, "gage": gageBat.value},
                                    ],
                                    typeImmo=pdfImmo(),
                                    existPret=self.existCp,
                                    confPret=self.confPret,
                                    existAct=self.existAct,
                                    confAct=self.confAct,
                                    existConv=self.existConv,
                                    confConv=self.confConv,
                                    existNat=self.existNant,
                                    confNat=self.confNant,
                                    ficheRecou=self.recouvre
                                )
                        pdf.output(save_location)
                        self.page.open(self.dlg2)
                        break
                    except Exception as error:
                        continue
                

        saveme = ft.FilePicker(on_result=downloadPDF)
        self.page.overlay.append(saveme)
            

        title = ft.Text("SCORING", size=30, weight=ft.FontWeight.W_500)
        

        self.sumScore = 44
        
        self.lastCount = 2

        score = ft.Text(value=1, size=40, color="red", weight="bold", font_family="digital7")


        def change_date(e):
            inputDate.value = date_picker.value.strftime("%Y-%m-%d")
            inputDate.error_text = ""
            self.update()

        def dismiss_date(e):
            if date_picker.value:
                inputDate.value = date_picker.value.strftime("%Y-%m-%d")
                inputDate.error_text = ""
            else:
                inputDate.error_text = "Champ obligatoire"
            self.update()

        date_picker = ft.DatePicker(
            on_change=change_date,
            on_dismiss=dismiss_date,
            cancel_text="Annuler",
            help_text="Choisir une date"
        )

        self.page.overlay.append(date_picker)

        date_button = ft.IconButton(
            icon=ft.icons.CALENDAR_MONTH,
            icon_color="black",
            tooltip="Date de passation/validation",
            on_click=lambda _: date_picker.pick_date()
        )

        inputDate = ft.TextField(
            hint_text="Date passation/validation*", 
            border_width=0, 
            expand=True, 
            read_only=True
        )

        dateP = ft.Container(
            content=ft.Row([inputDate, date_button]),
            border=ft.border.all(1, "black"),
            border_radius=5, 
        )

        def titleScoring(text, key):
            return ft.Row(
                [
                    ft.Container(
                        ft.Text(text, size=20, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, weight="bold")), 
                        height=50, 
                        alignment=ft.alignment.bottom_center
                    )
                ], 
                alignment=ft.MainAxisAlignment.CENTER,
                key=key
            )
        
        
        titleMbr = titleScoring("Membre", "mbr")
        titleCredit = titleScoring("Information de Crédit", "crd")
        titleCau = titleScoring("Caution", "cau")
        titleDos = titleScoring("Dossier", "dos")


        def searchMbr(e):
            hideError(e)
            caisse = str(inputCaisse.value).lower()
            folio = str(inputFolio.value).lower()
            rib = str(inputRib.value).lower()
            bdd = bddRadie if checkRadie.value else bddEncours
            myfilter = list(list(filter(lambda x: caisse == str(x[1]).lower() and folio == str(x[2])[:-6].lower() and rib == str(x[3]).lower(), bdd)))
            if len(myfilter) > 0:
                nameMbr.value = myfilter[0][4]
                adresseMbr.value = myfilter[0][5]
                formatDate = datetime.datetime.strptime(str(myfilter[0][7]), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") 
                dateCrdt.value = formatDate
                montantCrdt.value = locale.format_string("%.2f", myfilter[0][9], grouping=True)
                crd.value = locale.format_string("%.2f", myfilter[0][10], grouping=True)
                retard.value = f"{myfilter[0][16]} jours"
                duree.value = myfilter[0][8]
                agent.value = myfilter[0][17]
                capital.value = locale.format_string("%.2f", myfilter[0][13], grouping=True)
                interet.value = locale.format_string("%.2f", myfilter[0][14], grouping=True)
                penalite.value = locale.format_string("%.2f", myfilter[0][15], grouping=True)
            else:
                nameMbr.value = ""
                adresseMbr.value = ""
                dateCrdt.value = ""
                agent.value = ""
                montantCrdt.value = ""
                crd.value = ""
                retard.value = ""
                duree.value = ""
                capital.value = ""
                interet.value = ""
                penalite.value = ""
            self.update()

        
        

        inputCaisse = ft.Dropdown(on_change=searchMbr, label="Caisse*", bgcolor="white")
        for item in bddCaisse:
            inputCaisse.options.append(
                ft.dropdown.Option(key=str(item[2]).strip(), text=str(item[1]).strip())
            )
        inputFolio = ft.TextField(label="Folio*", hint_text="Folio", on_change=searchMbr, input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""), bgcolor="white")
        inputRib = ft.TextField(label="Rib*", hint_text="Rib", on_change=searchMbr, input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""), bgcolor="white")
        checkRadie = ft.Checkbox(
                        label="RADIE", 
                        label_style=ft.TextStyle(size=18, weight="bold"), 
                        on_change=searchMbr, 
                        fill_color={
                            ft.MaterialState.DEFAULT: ft.colors.WHITE,
                            ft.MaterialState.SELECTED: ft.colors.BLUE_900,
                        }
                    )
        colRadie = ft.Container(
            checkRadie,
            bgcolor=ft.colors.RED_100,
            border=ft.border.all(1, "black"),
            border_radius=5,
            padding=12
        )
        btnValid = ft.Row(
            [
                ft.Container(
                    ft.Text("Valider", size=20, weight=ft.FontWeight.W_500),
                    bgcolor="#FEC61F",
                    alignment=ft.alignment.center,
                    border_radius=5,
                    padding=10,
                    shadow=ft.BoxShadow(
                        spread_radius=0.5,
                        blur_radius=5,
                        offset=ft.Offset(0, 0),
                        blur_style=ft.ShadowBlurStyle.OUTER,
                    ),
                    on_click=sendScoring,
                    expand=True
                )
            ]
        )

        
        def toggleSwitch(param):
            if param.control.data == "avis":
                if param.control.value:
                    self.recouvre = True
                else:
                    self.recouvre = False
            param.control.label = "OUI" if param.control.value else "NON"
            self.update()
        
        self.score = 0

        self.existCp = False
        self.nbrConfPret = 0
        self.existNant = False
        self.nbrConfNant = 0
        self.existAct = False
        self.nbrConfAct = 0
        self.existConv = False
        self.nbrConfConv = 0



        def cPret(e):
            def contratExist(data):
                if e.control.data == data:
                    return True if e.control.value else False
                
            def contratConforme(data):
                if e.control.data == data:
                    return 1 if e.control.value else -1
                else:
                    return 0

            self.existCp = contratExist("existCP")
            self.existNant = contratExist("existNant")
            self.existAct = contratExist("existAct")
            self.existConv = contratExist("existConv")

            self.nbrConfPret += contratConforme("confPret")
            self.nbrConfNant += contratConforme("confNant")
            self.nbrConfAct += contratConforme("confAct")
            self.nbrConfConv += contratConforme("confConv")

                
        def changeSwitch(e):
            toggleSwitch(e)
            cPret(e)
            if e.control.value:
                self.lastCount = self.lastCount + 1
            else:
                if self.lastCount <= 0:
                    return
                self.lastCount = self.lastCount - 1
            
            scoreDos = int(self.lastCount) / int(self.sumScore)

            if not existeMbr.value:
                self.score = 1
                mbrFictif.visible = True
            else:
                mbrFictif.visible = False
                if 0 <= scoreDos < 0.2:
                    self.score = 1
                elif 0.2 <= scoreDos < 0.4:
                    self.score = 2
                elif 0.4 <= scoreDos < 0.6:
                    self.score = 3
                elif 0.6 <= scoreDos < 0.8:
                    self.score = 4
                else:
                    self.score = 5
            
            score.value = self.score
            self.update()

        def swtichMbrCau(text):
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Text(value=text),
                        ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                border=ft.border.all(1, "grey"),
                expand=True,
                padding=10,
                margin=10,
                border_radius=5
            )
        

        def millier(e):
            if not e.control.value:
                e.control.error_text = "Champ obligatoire"
                self.update()
                return
            e.control.value = locale.format_string("%.0f", int(e.control.value), grouping=True)
            e.control.error_text = ""
            self.update()
        
        
        # *************MEMBRE*************
        nameMbr = ft.TextField(expand=True, read_only=True, label="Nom", border_color="grey")
        adresseMbr = ft.TextField(expand=True, read_only=True, label="Adresse", border_color="grey")
        cinMbr = ft.TextField(expand=True, label="CIN*", border_color="grey", on_change=millier, input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""))
        phoneMbr = ft.TextField(expand=True, label="Téléphone", border_color="grey")
        existeMbr = ft.Switch(scale=0.8, label="OUI", key="null", value=True, on_change=changeSwitch, inactive_track_color="red")
        trouveMbr = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)
        solvablembr = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)
        vraiId = swtichMbrCau("Vrai identité: ")
        cinLegal = swtichMbrCau("Photocopie CIN \nlégalisée: ")
        resid = swtichMbrCau("Certificat de résidence: ")
        planRep = swtichMbrCau("Plan de repérage: ")
        travCert = swtichMbrCau("Certificat d'occupation /\nAttestation de travail: ")
        photoId = swtichMbrCau("Photo d'identité: ")

        # *************CREDIT*************
        agent = ft.TextField(read_only=True, label="Agent (Gestionnaire): ", border_color="grey")
        dateCrdt = ft.TextField(expand=True, read_only=True, label="Date octroi: ", border_color="grey")
        montantCrdt = ft.TextField(expand=True, read_only=True, label="Montant", border_color="grey")
        crd = ft.TextField(expand=True, read_only=True, label="Encours ou Capital passé en perte", border_color="grey")
        retard = ft.TextField(expand=True, read_only=True, label="Retard", border_color="grey")
        duree = ft.TextField(expand=True, read_only=True, label="Durée", border_color="grey")
        capital = ft.TextField(expand=True, read_only=True, label="Montant Capital", border_color="grey")
        interet = ft.TextField(expand=True, read_only=True, label="Montant Intérêts", border_color="grey")
        penalite = ft.TextField(expand=True, read_only=True, label="Montant Pénalités", border_color="grey")

        # *************CAUTION*************
        nameCau = ft.TextField(expand=True, label="Nom", border_color="grey")
        adresseCau = ft.TextField(expand=True, label="Adresse", border_color="grey")
        actuelCau = ft.TextField(expand=True, label="Adresse actuelle", border_color="grey")
        cinCau = ft.TextField(expand=True, label="CIN", border_color="grey")
        hypothequeCau = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)
        existeCau = ft.Switch(scale=0.8, label="OUI", value=True, on_change=changeSwitch)
        trouveCau = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)
        solvableCau = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)

        contentSwitch = ft.Column(
                            [
                                ft.Row(
                                    [
                                        vraiId,
                                        cinLegal,
                                        resid
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.Row(
                                    [
                                        travCert,
                                        planRep,
                                        photoId,
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                            ]
                        )
        

        # self.dbScoring = bddScoring.getData()

        def defScroll(e):
            contentScoring.scroll_to(key=e.control.key, duration=1000)

        self.menubar = ft.Container(
            expand=True,
            bgcolor="#FEC61F",
            border_radius=5,
            padding=5,
            content=ft.Row(
                [
                    ft.ElevatedButton("Membre", key="mbr", on_click=defScroll),
                    ft.ElevatedButton("Information de Crédit", key="crd", on_click=defScroll),
                    ft.ElevatedButton("Caution", key="cau", on_click=defScroll),
                    ft.ElevatedButton("Dossier", key="dos", on_click=defScroll)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        

        contentScoring = ft.Column(
                        expand=True,
                        scroll="auto"
                    )
        
        # ****************INSERTION MEMBRE****************
        contentScoring.controls.append(
            titleMbr
        )

        contentScoring.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(ft.Text("Le membre est-il ...?")), 
                                ft.Row([ft.Text("Existe: "), existeMbr]),
                                ft.Row([ft.Text("Trouvé: "), trouveMbr]),
                                ft.Row([ft.Text("Solvable: "), solvablembr])
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Row([nameMbr]),
                        ft.Row([adresseMbr]),
                        ft.Row([cinMbr]),
                        ft.Row([phoneMbr]),
                        contentSwitch
                    ]
                ),
                border=ft.border.all(1, "red"),
                border_radius=5,
                padding=10
            )
        )


        # ****************INSERTION CREDIT****************
        contentScoring.controls.append(
            titleCredit
        )

        contentScoring.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row([dateCrdt, montantCrdt, crd, retard], spacing=30),
                        ft.Row([duree, capital, interet, penalite], spacing=30)
                    ], 
                    spacing=30
                ),
                border=ft.border.all(1, ft.colors.BLACK54),
                border_radius=5,
                padding=15
            )
        )


        # ****************INSERTION CAUTION****************
        contentScoring.controls.append(
            titleCau
        )

        contentScoring.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(ft.Text("La caution en \nrapport avec ce dossier.")), 
                                ft.Row([ft.Text("Hypothèque: "), hypothequeCau]),
                                ft.Row([ft.Text("Existe: "), existeCau]),
                                ft.Row([ft.Text("Trouvé: "), trouveCau]),
                                ft.Row([ft.Text("Solvable: "), solvableCau])
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Row([nameCau]),
                        ft.Row([adresseCau]),
                        ft.Row([actuelCau]),
                        ft.Row([cinCau]),
                        contentSwitch
                    ]
                ),
                border=ft.border.all(1, "#FEC61F"),
                border_radius=5,
                padding=10
            )
        )


        # ****************INSERTION DOSSIER****************
        contentScoring.controls.append(
            titleDos
        )

        def titleDossier(text):
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Text(
                            text, 
                            size=18, 
                            color="blue", 
                            style=ft.TextStyle(
                                decoration=ft.TextDecoration.UNDERLINE,
                                decoration_color="blue"
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                margin=ft.margin.only(top=20)
            )
        # ****************RENSEIGNEMENT SUR CONTRAT DE PRET****************
        contentScoring.controls.append(
            titleDossier("RENSEIGNEMENT SUR CONTRAT DE PRET")
        )

        def switchDossier():
            return ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)
        

        contentScoring.controls.append(
            ft.Row(
                [
                    ft.DataTable(
                        expand=True,
                        border=ft.border.all(1, "black"),
                        vertical_lines=ft.BorderSide(1, "grey"),
                        border_radius=10,
                        columns=[
                            ft.DataColumn(ft.Text("Dossier")),
                            ft.DataColumn(ft.Text("Existence")),
                            ft.DataColumn(ft.Text("Bien rempli")),
                            ft.DataColumn(ft.Text("Signature")),
                            ft.DataColumn(ft.Text("Legalisation")),
                            ft.DataColumn(ft.Text("Enregistrement"))
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Contrat de prêt")),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="existCP", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confPret", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confPret", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confPret", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confPret", on_change=changeSwitch)),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Acte de nantissement")),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="existNant", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confNant", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confNant", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confNant", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confNant", on_change=changeSwitch)),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Acte de cautionnement solidaire et indivisible", size=11)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="existAct", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confAct", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confAct", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confAct", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confAct", on_change=changeSwitch)),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Convention d'hypothèque")),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="existConv", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confConv", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confConv", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confConv", on_change=changeSwitch)),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", data="confConv", on_change=changeSwitch)),
                                ]
                            )
                        ]
                    )
                ]
            )
        )

        # ****************RENSEIGNEMENT SUR LE RECOUVREMENT****************
        contentScoring.controls.append(
            titleDossier("RENSEIGNEMENT SUR LE RECOUVREMENT")
        )

        self.recouvre = False

        contentScoring.controls.append(
            ft.Row(
                [
                    ft.DataTable(
                        border=ft.border.all(1, "black"),
                        vertical_lines=ft.BorderSide(1, "grey"),
                        border_radius=10,
                        columns=[
                            ft.DataColumn(ft.Text("Etapes")),
                            ft.DataColumn(ft.Text("Fiche historique")),
                            ft.DataColumn(ft.Text("Autre pièce")),  
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("RECOUVREMENT PAR PRESSION")),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=toggleSwitch, data="avis")),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=toggleSwitch, data="avis")),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("ENVOI 1er AVIS")),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=toggleSwitch, data="avis")),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=toggleSwitch, data="avis")),
                                ]
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("ENVOI 2e AVIS")),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=toggleSwitch, data="avis")),
                                    ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=toggleSwitch, data="avis")),
                                ]
                            )
                        ],
                        expand=True
                    )
                ]
            )
        )

        self.sumMae = 0
        self.sumTerrain = 5

        def mustGarant():
            if not checkMat.value and not checkImmo.value:
                contentImmo.bgcolor = "red"
                contentMat.bgcolor = "red"
            else:
                contentImmo.bgcolor = "#FEC61F"
                contentMat.bgcolor = "#FEC61F"
            self.update()


        def toggleMae(e):
            mustGarant()
            if checkMat.value:
                self.sumScore += self.sumMae
                self.garantMae.visible = True
            else:
                self.sumScore -= self.sumMae
                for row in self.garantMae.rows:
                    switchs = list(filter(lambda x: isinstance(x.content, ft.Switch), row.cells))
                    row.cells[0].content.value = False

                    for switch in switchs:
                        if switch.content.value:
                            self.lastCount -= 1
                        switch.content.value = False
                        switch.content.label = 'NON'

                    i = 0
                    for cell in row.cells:
                        if i == 0:
                            i += 1
                            continue
                        cell.content.disabled = True
                self.sumMae = 0
                self.garantMae.visible = False
            self.update()

        
        def toggleImmo(e):
            mustGarant()
            if checkImmo.value:
                self.sumScore += self.sumTerrain
                self.tableTerrain.visible = True
            else:
                self.sumScore -= self.sumTerrain
                row1 = self.tableTerrain.rows[:1]
                
                for row in self.tableTerrain.rows:
                    i = 0
                    for cell in row.cells:
                        if i == 0:
                            i += 1
                            continue
                        if cell.content.value:
                            self.lastCount -= 1
                        cell.content.value = False
                        cell.content.label = 'NON'

                for row in row1:
                    i = 0
                    for cell in row.cells:
                        if i == 0:
                            i += 1
                            continue
                        cell.content.value = False

                self.tableTerrain.rows = row1 
                self.nbrterrain = 1      
                self.tableTerrain.visible = False
                self.sumTerrain = 5
            addBtn.visible = True if checkImmo.value else False
            removeBtn.visible = True if checkImmo.value else False
            self.update()




        def checkGarant(text, func):
            return ft.Checkbox(
                label=text, 
                value=True, 
                label_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_400),
                fill_color={
                    ft.MaterialState.DEFAULT: ft.colors.WHITE,
                    ft.MaterialState.SELECTED: ft.colors.BLUE_900,
                },
                on_change=func
            )
        
        checkMat = checkGarant("Matérielle", toggleMae)
        checkImmo = checkGarant("Immobilière", toggleImmo)

        # ****************SITUATON DES GARANTIES****************
        contentScoring.controls.append(
            titleDossier("SITUATON DES GARANTIES")
        )

        contentMat = ft.Container(
                        checkMat, 
                        border=ft.border.all(1, "grey"),
                        border_radius=5,
                        padding=10,
                        bgcolor="#FEC61F",
                        height=40
                    )
        
        contentImmo = ft.Container(
                        checkImmo, 
                        border=ft.border.all(1, "grey"),
                        border_radius=5,
                        padding=10,
                        bgcolor="#FEC61F",
                        height=40
                    )

        contentScoring.controls.append(
            ft.Row(
                [
                    ft.Text("Types de garanties:", size=18, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
                    contentMat,
                    contentImmo
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )


        

        def getIndex(e):
            ligne = self.garantMae.rows[e.control.data]
            nbrSwitch = len(list(filter(lambda x: isinstance(x.content, ft.Switch), ligne.cells)))
            
            def checkRow(param):
                i = 0
                for cell in ligne.cells:
                    if isinstance(cell.content, ft.Switch):
                        if cell.content.value:
                            self.lastCount -= 1
                        cell.content.value = False
                        cell.content.label = 'NON'
                    if i == 0:
                        i += 1
                        continue
                    cell.content.disabled = param

            if e.control.value:
                checkRow(False)
                self.sumScore += nbrSwitch
                self.sumMae += nbrSwitch

            else:
                checkRow(True)
                self.sumScore -= nbrSwitch
                self.sumMae -= nbrSwitch
            
            self.update()

        checkStock = ft.Checkbox(label="MAE, STOCK", on_change=getIndex, data=0)
        checkVehicule = ft.Checkbox(label="VEHICULE MOTORISE,\nMOTO, ENGIN", on_change=getIndex, data=1, label_style=ft.TextStyle(size=11))
        checkBateau = ft.Checkbox(label="VEDETTE\nBATEAU", on_change=getIndex, data=2)

        existMae = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)
        beMae = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)
        privMae = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)

        existVH = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)
        beVH = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)
        privVH = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)
        gageVH = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)
        griseVH = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)

        existBat = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)
        beBat = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)
        privBat = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)
        gageBat = ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, disabled=True)

        self.garantMae = ft.DataTable(
                            expand=True,
                            border=ft.border.all(1, "black"),
                            vertical_lines=ft.BorderSide(1, "grey"),
                            border_radius=10,
                            heading_row_height=120,
                            columns=[
                                ft.DataColumn(ft.Text("BIEN MATERIELLE")),
                                ft.DataColumn(ft.Text("Existence\nmatérielle\nTrouvable", text_align="center")),
                                ft.DataColumn(ft.Text("Bon état", text_align="center")),
                                ft.DataColumn(ft.Text("Inscription\nde privilège\nau tribunal", text_align="center")),
                                ft.DataColumn(ft.Text("Photocopie\ncarte grise\ndu véhicule", text_align="center")),
                                ft.DataColumn(ft.Text("Inscription\nde gage\nAPMF\n(vedette, bateau)\nou véhicule", text_align="center"))
                            ],
                            rows=[
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(checkStock),
                                        ft.DataCell(existMae),
                                        ft.DataCell(beMae),
                                        ft.DataCell(privMae),
                                        ft.DataCell(ft.Text("")),
                                        ft.DataCell(ft.Text("")),
                                    ]
                                ),
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(checkVehicule),
                                        ft.DataCell(existVH),
                                        ft.DataCell(beVH),
                                        ft.DataCell(privVH),
                                        ft.DataCell(griseVH),
                                        ft.DataCell(gageVH),
                                    ]
                                ),
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(checkBateau),
                                        ft.DataCell(existBat),
                                        ft.DataCell(beBat),
                                        ft.DataCell(privBat),
                                        ft.DataCell(ft.Text("")),
                                        ft.DataCell(gageBat),
                                    ]
                                )
                            ]
                        )
        
        contentScoring.controls.append(
            ft.Container(
                content=ft.Row(
                    [
                        self.garantMae
                    ]
                ),
                margin=ft.margin.only(top=20)
            )
        )


        self.nbrterrain = 1
        self.tableTerrain = ft.DataTable(
                            expand=True,
                            border=ft.border.all(1, "black"),
                            vertical_lines=ft.BorderSide(1, "grey"),
                            border_radius=10,
                            heading_row_height=120,
                            columns=[
                                ft.DataColumn(ft.Text("BIENS IMMEUBLES\n(TERRAINS, MAISONS)", size=13)),
                                ft.DataColumn(ft.Text("Existence\nmatérielle\nTrouvable", text_align="center")),
                                ft.DataColumn(ft.Text("Bon état", text_align="center")),
                                ft.DataColumn(ft.Text("Titre foncier\nCadastre\nCertificat foncier", text_align="center")),
                                ft.DataColumn(ft.Text("Certificat\nde\nsituation juridique", text_align="center")),
                                ft.DataColumn(ft.Text("Hypothèque\nnotariée", text_align="center"))
                            ],
                            rows=[
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(ft.Text(f"TERRAIN {self.nbrterrain}")),
                                        ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)),
                                        ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)),
                                        ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, data=f"seingTer{self.nbrterrain}")),
                                        ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, data=f"seingTer{self.nbrterrain}")),
                                        ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, data=f"hypo{self.nbrterrain}")),
                                    ]
                                )
                            ]
                        )
        
        
        def addTerrain(e):
            self.nbrterrain += 1
            self.tableTerrain.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"TERRAIN {self.nbrterrain}")),
                        ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)),
                        ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=changeSwitch)),
                        ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, data=f"seingTer{self.nbrterrain}")),
                        ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, data=f"seingTer{self.nbrterrain}")),
                        ft.DataCell(ft.Switch(scale=0.8, label="NON", on_change=changeSwitch, data=f"hypo{self.nbrterrain}")),
                    ]
                )
            )
            self.sumTerrain += 5
            self.sumScore += 5
            self.update()

        def removeTerrain(e):
            if self.nbrterrain <= 1:
                return
            self.nbrterrain -= 1
            row = self.tableTerrain.rows[-1]
            for cell in row.cells:
                if cell.content.value == True:
                    self.lastCount -= 1
            self.tableTerrain.rows.pop()
            self.sumTerrain -= 5
            self.sumScore -= 5
            self.update()


        contentScoring.controls.append(
            ft.Container(ft.Row([self.tableTerrain]), margin=ft.margin.only(top=20))
        )

        def btnTerrain(icon, bg, func):
            return ft.FilledButton(
                text="Terrain",
                icon=icon, 
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    bgcolor=bg
                ),
                on_click=func
            )

        addBtn = btnTerrain("add", "amber", addTerrain)
        removeBtn = btnTerrain("remove", "red", removeTerrain)

        contentScoring.controls.append(
            ft.Container(
                content=ft.Row([removeBtn, addBtn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        )
        

        contentScoring.controls.append(
            ft.Row([ft.Container(ft.Text("Audit - SMMEC 2024"), height=50)], alignment=ft.MainAxisAlignment.CENTER)
        )


        scoreContent = ft.Container(
            content=ft.Row(
                [
                    ft.Text(f"Score:", size=20, color="red", weight=ft.FontWeight.W_600),
                    score
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_AROUND
            ),
            bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLACK87),
            border_radius=5,
            padding=5
        )

        mbrFictif = ft.TextField(
            value="MEMBRE FICTIF !", 
            text_style=ft.TextStyle(font_family="arial", weight=ft.FontWeight.W_600),
            bgcolor="red",
            color="white",
            border_width=0,
            text_align="center",
            visible=False,
            height=40,
            content_padding=5,
            expand=True,
            read_only=True
        )
        

        self.form = ft.Container(
            bgcolor=ft.colors.GREY_200,
            border_radius=5,
            col=2.5,
            padding=10,
            content=ft.Column(
                [
                    colRadie, 
                    dateP, 
                    agent,
                    inputCaisse,
                    inputFolio, 
                    inputRib,
                    scoreContent,
                    btnValid
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        self.table = ft.Container(
            border_radius=10,
            col=9.5,
            padding=10,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row([title], alignment="center"),
                                ft.Row([self.menubar]),
                                ft.Row([mbrFictif]),
                            ]
                        )
                    ),
                    contentScoring
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