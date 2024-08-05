import flet as ft
from modal.authMysql import BDD_MYSQL
from bdd import BDD_SQL
from dlgLoad import DLG
import numpy as np
import pandas as pd
import locale

class FilterReport:
    def __init__(self, page):
        bddDepot = BDD_SQL()
        bddScoring = BDD_MYSQL('scoring')
        bddSuivi = BDD_MYSQL('suivi')

        self.dbDepot = bddDepot.getData('depot')
        self.dbScoring = bddScoring.getData() if isinstance(bddScoring.getData(), (list, tuple)) else False
        self.dbSuivi = bddSuivi.getData() if isinstance(bddSuivi.getData(), (list, tuple)) else False
        self.page = page

    def funcReport(self, min_date=None, max_date=None):
        df_depot = pd.DataFrame(np.array(self.dbDepot))

        if self.dbScoring and self.dbSuivi:
            df_scoring = pd.DataFrame(self.dbScoring)
            df_suivi = pd.DataFrame(self.dbSuivi)
        else:
            return False
        

        df_depot[2] = pd.to_datetime(df_depot[2])
        df_depot[6] = df_depot[6].astype(float)


        df_scoring['date_passation'] = pd.to_datetime(df_scoring['date_passation'])
        df_scoring = df_scoring[(df_scoring['agence'] == self.page.client_storage.get('agence'))]

        df_depot.rename(columns={df_depot.columns[3]: 'caisse', df_depot.columns[4]: 'folio', df_depot.columns[6]: 'montant'}, inplace=True)
        

        joinT = pd.merge(left=df_scoring, right=df_depot, on='folio', how='left')
        
        filtered_depot = joinT[(joinT['date_passation'] >= min_date) & (df_depot[2] >= min_date) & (df_depot[2] <= max_date)] if min_date and max_date else df_depot
        print(filtered_depot)
        sum_by_folio = filtered_depot.groupby(['caisse', 'folio'])['montant'].sum().reset_index()
        # sum_by_folio.rename(columns={sum_by_folio.columns[3]: 'caisse'}, inplace=True)
        # if min_date and max_date:
        #     if min_date <= max_date:
        #         fD = joinT[(joinT['date_passation'] >= min_date) & (df_depot[2] >= min_date) & (df_depot[2] <= max_date)]
        #         sum_d = fD.groupby(['caisse_x', 'folio'])['montant'].sum().reset_index()
        #         print(sum_d)
        
        # sum_by_folio.rename(columns={sum_by_folio.columns[0]: 'folio', sum_by_folio.columns[1]: 'montant'}, inplace=True)

        # filtered_scoring = df_scoring[(df_scoring['agence'] == self.page.client_storage.get('agence')) & (df_scoring['date_passation'] >= min_date) & (df_scoring['date_passation'] <= max_date)] if min_date and max_date else df_scoring[(df_scoring['agence'] == self.page.client_storage.get('agence'))]
        # filtered_scoring = df_scoring[(df_scoring['agence'] == self.page.client_storage.get('agence'))]
        # sdcJ = filtered_scoring.groupby(['caisse', 'folio']).agg(nbr = ('rib', 'count')).reset_index()
        # join = pd.merge(left=sdcJ, right=sum_by_folio, on='folio', how='left')
        
        # filtered_suivi = df_suivi[(df_suivi['agence'] == self.page.client_storage.get('agence'))]
        # print(df_suivi)


        result_dict = sum_by_folio.to_dict(orient='records')


        return result_dict



class Reporting(ft.UserControl):
    def __init__(self, page):
        super().__init__(expand=True)

        self.page = page

        self.search = ft.TextField(hint_text="Folio...", expand=True, bgcolor="white", border_width=0.5)
        self.connex = ft.Text("Aucune donnée trouvée...", size=20, weight="bold", text_align="center")


        self.data_table = ft.DataTable(
            bgcolor="white",
            border=ft.border.all(0.5, "black"),
            vertical_lines=ft.BorderSide(0.5, "grey"),
            heading_row_color=ft.colors.GREY_200,
            border_radius=5,
            columns=[
                ft.DataColumn(ft.Text(max_lines=1, no_wrap=True, value="Caisse")),
                ft.DataColumn(ft.Text(max_lines=1, no_wrap=True, value="Folio")),
                ft.DataColumn(ft.Text(max_lines=1, no_wrap=True, value="Montant total (j)")),
            ]
        )



        self.listFolder = FilterReport(page)
        self.checkFolder = self.listFolder.funcReport()

        if self.checkFolder:
            for x in self.checkFolder:
                sumMontant =  x['montant'] if str(x['montant']) != 'nan' else 0
                self.data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(x['caisse'])),
                            ft.DataCell(ft.Text(x['folio'])),
                            ft.DataCell(ft.Text(locale.format_string("%.2f", sumMontant, grouping=True)))
                        ]
                    )
                )
            self.connex.visible = False
        else:
            self.connex.visible = True

       

        def filterDate(e):
            self.checkFolder = self.listFolder.funcReport(min_date=startDate.value, max_date=endDate.value)
            self.data_table.rows.clear()
            if self.checkFolder and len(self.checkFolder) > 0:
                for x in self.checkFolder:
                    sumMontant =  x['montant'] if str(x['montant']) != 'nan' else 0
                    self.data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(x['caisse'])),
                                ft.DataCell(ft.Text(x['folio'])),
                                ft.DataCell(ft.Text(locale.format_string("%.2f", sumMontant, grouping=True)))
                            ]
                        )
                    )
                self.connex.visible = False
            else:
                self.connex.visible = True
            
            self.update()

        def inputsearch(e):
            search_folio = str(self.search.value).lower()
            myfilter = list(filter(lambda x:search_folio in str(x['folio']).lower(), self.checkFolder))
            self.data_table.rows.clear()
    
            # THEN PUSH THE RESULT TO YOU TABLE
            if search_folio != "":
                if len(myfilter) > 0 :
                    for x in myfilter:
                        sumMontant =  x['montant'] if str(x['montant']) != 'nan' else 0
                        self.data_table.rows.append(
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text(x['caisse'])),
                                    ft.DataCell(ft.Text(x['folio'])),
                                    ft.DataCell(ft.Text(locale.format_string("%.2f", sumMontant, grouping=True)))
                                ]
                            )
                        )
                        self.update()
                else:
                    self.data_table.rows = []
                    self.update()
    
            else:
                for x in self.checkFolder:
                    sumMontant =  x['montant'] if str(x['montant']) != 'nan' else 0
                    self.data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(x['caisse'])),
                                ft.DataCell(ft.Text(x['folio'])),
                                ft.DataCell(ft.Text(locale.format_string("%.2f", sumMontant, grouping=True)))
                            ]
                        )
                    )
                    self.update()

        
        self.search.on_change = inputsearch

        def change_date(e):
            inputD = inputStart if e.control.data == 0 else inputEnd
            date_picker = startDate if e.control.data == 0 else endDate
            inputD.text = date_picker.value.strftime("%d/%m/%Y")

            if endDate.value and startDate.value:
                if startDate.value > endDate.value:
                    dlg = DLG.errorSpecial("La date de fin doit dépasser la date de début !")
                    self.page.open(dlg)

            self.update()


        startDate = ft.DatePicker(
            data=0,
            on_change=change_date,
            cancel_text="Annuler",
            help_text="Choisir une date"
        )


        endDate = ft.DatePicker(
            data=1,
            on_change=change_date,
            cancel_text="Annuler",
            help_text="Choisir une date"
        )


        self.page.overlay.append(startDate)
        self.page.overlay.append(endDate)


        inputStart = ft.ElevatedButton(
                        "Date de début",  
                        on_click=lambda _: self.page.open(startDate),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=5)
                        )
                    )
        
        inputEnd = ft.ElevatedButton(
                        "Date de fin",  
                        on_click=lambda _: self.page.open(endDate),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=5)
                        )
                    )


        start_button = ft.IconButton(
            icon=ft.icons.CALENDAR_MONTH,
            icon_color="black",
            on_click=lambda _: self.page.open(startDate),
            tooltip="Date de début"
        )


        end_button = ft.IconButton(
            icon=ft.icons.CALENDAR_MONTH,
            icon_color="black",
            on_click=lambda _: self.page.open(endDate),
            tooltip="Date de fin"
        )


        def c_card(title, param, icone, icon_color, bg_color):
            return ft.Container(
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Container(
                                            ft.Icon(name=icone, color=icon_color, size=40), 
                                            bgcolor=bg_color, 
                                            border_radius=5,
                                            padding=20
                                        )
                                    ]
                                ),
                                ft.Column(
                                    [
                                        ft.Text(title, size=15),
                                        ft.Text(param, weight="bold", size=25),
                                    ]
                                )
                            ],
                            scroll="auto"
                        ),
                        border=ft.border.all(0.3, "grey"),
                        bgcolor="white",
                        border_radius=10,
                        padding=20,
                        col={"sm": 6, "md": 4}
                    )

        
        card1 = c_card("Total des dossiers marqué", "2", ft.icons.FOLDER_SPECIAL_ROUNDED, "#DF2041", ft.colors.RED_50)
        card2 = c_card("Total action réalisé", "68", ft.icons.FACT_CHECK, "#696B6A", ft.colors.GREY_100)
        card3 = c_card("Total dossier passé", "12", ft.icons.PUBLISHED_WITH_CHANGES, "amber", ft.colors.with_opacity(0.2, "amber"))


        self.table = ft.Container(
            border_radius=10,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text("REPORTING", size=30, weight=ft.FontWeight.W_500)
                            )
                        ], 
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(
                        bgcolor="#FEC61F",
                        border_radius=5,
                        padding=ft.padding.only(left=10, right=10, bottom=5, top=5),
                        margin=ft.margin.only(left=10, right=10, bottom=5),
                        content=ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.Text("Opération: "),
                                        inputStart,
                                        start_button
                                    ]
                                ),
                                ft.Row(
                                    [
                                        ft.Text("Au: "),
                                        inputEnd,
                                        end_button
                                    ]
                                ),
                                ft.ElevatedButton(
                                    "OK",  
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=5),
                                        color="black"
                                    ),
                                    on_click=filterDate
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ),
                    ft.Column(
                        [
                            ft.Container(
                                margin=ft.margin.only(top=10, bottom=10),
                                padding=ft.padding.only(left=10, right=10),
                                content=ft.ResponsiveRow(
                                    [
                                        card1, card2, card3
                                    ],
                                    expand=True,
                                    spacing=20
                                )
                            ),
                            ft.Container(
                                padding=ft.padding.only(left=10, right=10),
                                content=ft.Row(
                                    [
                                        self.search
                                    ]
                                )
                            ),
                            ft.Column(
                                [
                                    ft.Container(
                                        content=ft.ResponsiveRow(
                                            [
                                                self.data_table,
                                                self.connex
                                            ]
                                        ),
                                        padding=10
                                    )
                                ]
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
                self.table
            ]
        )

    def build(self):
        return self.content