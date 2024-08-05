import flet as ft
from modal.authMysql import BDD_MYSQL
from dlgLoad import DLG
import locale

bddSuivi = BDD_MYSQL('suivi')

class Suivi(ft.UserControl):
    def __init__(self, page):
        super().__init__(expand=True)

        self.page = page
        self.search = ft.TextField(hint_text="Folio...", expand=True)
        self.connex = ft.Text("Pas de Connexion...", size=20, weight="bold", text_align="center")

        self.dbSuivi = bddSuivi.getData(filter='0') if isinstance(bddSuivi.getData(filter='0'), (list, tuple)) else False

        self.data_table = ft.DataTable(
            border=ft.border.all(1, "black"),
            vertical_lines=ft.BorderSide(1, "grey"),
            border_radius=5,
            data_row_color={
                ft.MaterialState.PRESSED: "#FFC107"
            },
            columns=[
                ft.DataColumn(ft.Text(max_lines=1, no_wrap=True, value="Caisse")),
                ft.DataColumn(ft.Text(max_lines=1, no_wrap=True, value="Folio")),
                ft.DataColumn(ft.Text(max_lines=1, no_wrap=True, value="Rib")),
                ft.DataColumn(ft.Text(max_lines=1, no_wrap=True, value="Montant recouvré")),
                ft.DataColumn(ft.Text(max_lines=1, no_wrap=True, value="Retard (j)")),
                ft.DataColumn(ft.Text(max_lines=1, no_wrap=True, value="Dernière date d'action")),
                ft.DataColumn(ft.Text(max_lines=1, no_wrap=True, value="Action récente"))
            ]
        )

        def passToHistory(e):
            dlg = DLG.load() 
            self.page.open(dlg)
            self.page.go(e.control.data)


        if self.dbSuivi:
            for x in self.dbSuivi:
                if x['agence'] == self.page.client_storage.get('agence'):
                    self.data_table.rows.append(
                        ft.DataRow(
                            on_select_changed=passToHistory,
                            selected=False,
                            cells=[
                                ft.DataCell(ft.Text(x['caisse'])),
                                ft.DataCell(ft.Text(x['folio'])),
                                ft.DataCell(ft.Text(x['rib'])),
                                ft.DataCell(ft.Text(locale.format_string("%.2f", float(x['montant_recouvre']), grouping=True))),
                                ft.DataCell(ft.Text(x['retard_act'])),
                                ft.DataCell(ft.Text(x['date_action'])),
                                ft.DataCell(
                                    ft.Text(f"{x['action']}\n{x['detail']}", max_lines=2, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)
                                ),
                            ],
                            data=f'/history/{x['id_scoring']}'
                        )
                    )
            self.connex.visible = False
        else:
            self.connex.visible = True

        def inputsearch(e):
            search_folio = str(self.search.value).lower()
            myfilter = list(filter(lambda x:search_folio in str(x['folio']).lower(), self.dbSuivi))
            self.data_table.rows = []
    
            # THEN PUSH THE RESULT TO YOU TABLE
            if not self.search.value == "":
                # AND IF LENGHT OF RESULT > 0
                if len(myfilter) > 0 :
                    for x in myfilter:
                        if x['agence'] == self.page.client_storage.get('agence'):
                            self.data_table.rows.append(
                                ft.DataRow(
                                    on_select_changed=passToHistory,
                                    selected=False,
                                    cells=[
                                        ft.DataCell(ft.Text(x['caisse'])),
                                        ft.DataCell(ft.Text(x['folio'])),
                                        ft.DataCell(ft.Text(x['rib'])),
                                        ft.DataCell(ft.Text(locale.format_string("%.2f", float(x['montant_recouvre']), grouping=True))),
                                        ft.DataCell(ft.Text(x['retard_act'])),
                                        ft.DataCell(ft.Text(x['date_action'])),
                                        ft.DataCell(
                                            ft.Text(f"{x['action']}\n{x['detail']}", max_lines=2, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)
                                        ),
                                    ],
                                    data=f'/history/{x['id_scoring']}'
                                )
                            )
                        self.update()
                else:
                    self.data_table.rows = []
                    self.update()
    
            else:
                for x in self.dbSuivi:
                    if x['agence'] == self.page.client_storage.get('agence'):
                        self.data_table.rows.append(
                            ft.DataRow(
                                on_select_changed=passToHistory,
                                selected=False,
                                cells=[
                                    ft.DataCell(ft.Text(x['caisse'])),
                                    ft.DataCell(ft.Text(x['folio'])),
                                    ft.DataCell(ft.Text(x['rib'])),
                                    ft.DataCell(ft.Text(locale.format_string("%.2f", float(x['montant_recouvre']), grouping=True))),
                                    ft.DataCell(ft.Text(x['retard_act'])),
                                    ft.DataCell(ft.Text(x['date_action'])),
                                    ft.DataCell(
                                        ft.Text(f"{x['action']}\n{x['detail']}", max_lines=2, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)
                                    ),
                                ],
                                data=f'/history/{x['id_scoring']}'
                            )
                        )
                    self.update()

        
        self.search.on_change = inputsearch
        

        self.table = ft.Container(
            border_radius=10,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text("SUIVI", size=30, weight=ft.FontWeight.W_500)
                            )
                        ], 
                        alignment=ft.MainAxisAlignment.CENTER
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