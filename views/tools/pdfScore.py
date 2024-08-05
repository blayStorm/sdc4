from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 7, 'GRILLE D\'ANALYSE DE DOSSIER CONTENTIEUX', 0, 1, 'C')

    def footer(self):
        self.set_y(-17)
        self.set_font('Arial', 'B', 8)
        self.cell(self.w - 20, 15, '', 1, 1)
        self.set_y(-17)
        self.cell(self.w - 20, 10, "> LE CCL EST TENU RESPONSABLE DE LA VERACITE DE TOUTES LES INFORMATIONS, DECLARATIONS ET PIECES QU'IL A FOURNI", 0, 1)
        self.cell(self.w - 20, 0, "LORS DE LA PASSATION DU DOSSIER AVEC LE JURISTE", 0, 0)

    def chapter_title(self, num, label):
        self.set_font('Arial', 'B', 8)
        self.cell(0, 8, f'{num}- {label}', 0, 1, 'L')

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_image(self, image_path, x, y, w, h):
        self.image(image_path, x, y, w, h)

    def add_table(self, data, col_widths, row_height=8, ter=False):
        self.set_font('Arial', 'B', 8)
        i = 0
        for row in data:
            if i == 0:
                self.set_fill_color(221, 235, 247)
                color = True
            else:
                color = False
            i += 1
            max_line_height = row_height
            for datum, width in zip(row, col_widths):
                if ter:
                    width = 40
                if len(str(datum)) > 40:
                    line_height = self.get_string_width(datum) / width * row_height
                    max_line_height = max(max_line_height, line_height) - 3
            
            x = self.get_x()
            y = self.get_y()
            j = 0
            for datum, width in zip(row, col_widths):
                pos = 'C' if j != 0 else 'L'
                self.multi_cell(width, (max_line_height / len(str(datum).split('\n'))), str(datum), border=1, fill=color, align=pos)
                self.set_xy(x + width, y)
                x += width
                j += 1
            self.ln(max_line_height)

    def add_table2(self, data, col_widths, row_height=8, score=False):
        self.set_font('Arial', 'B', 8)
        i = 0
        for row in data:
            self.set_x(x= (self.w / 2) + 20)
            if i == 0 :
                self.set_fill_color(221, 235, 247)
                color = True
            else:
                color = False
            i += 1
            j = 0
            for datum, width in zip(row, col_widths):
                pos = 'C' if j != 0 else 'L'
                if score and j == 0:
                    self.set_fill_color(247, 188, 209)
                    self.cell(width, row_height, str(datum), border=1, fill=color, align=pos)
                    color = False
                else:
                    self.cell(width, row_height, str(datum), border=1, fill=color, align=pos)
                j += 1
            self.ln(row_height)

def outputPDF(
        existPret, confPret, existNat, confNat, existAct, confAct, existConv, confConv,
        ficheRecou,
        agence, mae,
        immo,
        caisse, typeMae,
        folio, typeImmo,
        nom, existMbr,
        rib, solveMbr,
        dateP, trouveMbr,
        dateO, trouveCau,
        montant, existCau,
        duree, solveCau,
        retard, hypoCau,
        capital,
        interet,
        penalite,
        responsable,
        scoring,
    ):

    pdf = PDF()

    # Ajouter une page
    pdf.add_page()


    pdf.set_draw_color(148, 202, 0)
    pdf.set_line_width(1.5)


    # pdf.line(125, 40, 125, 250)

    page_width = pdf.w
    page_height = pdf.h
    middle_x = page_width / 2  + 17.5
    pdf.line(middle_x, 40, middle_x, page_height - 25)

    pdf.set_draw_color(0, 0, 0)  # Bleu par exemple
    pdf.set_line_width(0.3)

    # Ajouter une image
    image_path = 'http://localhost/apijuriste/logo.png' 
    # image_path = 'https://auditci.alwaysdata.net/logo.png' 
    pdf.add_image(image_path, 8, 15, 40, 14)
    

    if len(nom) < 30:
        taille = 8
    else:
        taille = 8
        
    pdf.set_x(50)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(20, 7, 'AGENCE:', 0, 0)
    pdf.set_font('Arial', '', 8)
    pdf.cell(40, 7, agence, 0, 0)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(20, 7, 'CAISSE:', 0, 0)
    pdf.set_font('Arial', '', 8)
    pdf.cell(300, 7, caisse.upper(), 0, 1)

    if not existMbr:
        pdf.set_fill_color(234, 64, 51)
        pdf.set_text_color(255, 255, 255)
        pdf.set_x(50)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(110, 6, 'MEMBRE FICTIF', 0, 1, fill=True, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(0, 0, 0)

    pdf.set_x(50)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(20, 7, 'FOLIO:', 0, 0)
    pdf.set_font('Arial', '', 8)
    pdf.cell(40, 7, f"{folio}", 0, 0)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(20, 7, 'NOM:', 0, 0)
    pdf.set_font('Arial', '', taille)
    pdf.cell(300, 7, nom.upper(), 0, 1)

    pdf.ln(2)
    check = "X"

    checkF = lambda x: "X" if x == True else ""

    pdf.chapter_title(1, 'RENSEIGNEMENT SUR LE MEMBRE')
    data = [
        ["Rubriques", "Oui"],
        ["Existe", checkF(existMbr)],
        ["Trouvé", checkF(trouveMbr)],
        ["Solvable", checkF(solveMbr)]
    ]
    col_widths = [50, 20]  # Largeur des colonnes
    pdf.add_table(data, col_widths)

    pdf.ln(3)

        
    pdf.chapter_title(2, 'RENSEIGNEMENT SUR LE DOSSIER')
    data = [
        ["Eléments qui composent le dossier", "Existence", "Conformité"],
        ["Contrat de prêt", checkF(existPret), checkF(confPret)],
        ["Acte de nantissement", checkF(existNat), checkF(confNat)],
        ["Acte de cautionnement solidaire\net indivisible", checkF(existAct), checkF(confAct)],
        ["Convention d'hypothèque", checkF(existConv), checkF(confConv)],
        ["Fiche historique de recouvrement\n(1er avis, 2em avis,...)", checkF(ficheRecou), ""]
    ]
    col_widths = [50, 20, 20]  # Largeur des colonnes
    pdf.add_table(data, col_widths)


    pdf.ln(3)

    pdf.chapter_title(3, 'RENSEIGNEMENT SUR LES GARANTIES')
    data = [
        ["TYPE DE GARANTIE", "Oui"],
        ["Garantie matérielle", checkF(mae)],
        ["Garantie immobilière", checkF(immo)]
    ]
    col_widths = [50, 20]  # Largeur des colonnes APMF\n(vedette, bateau) / véhicule
    pdf.add_table(data, col_widths) #:\nEst ce qu'elles sont …?

    pdf.ln(3)

    data = []
    data.append(["Si garanties matérielles:\n Est ce qu'elles sont ...?", "MAE", "VEHICULE", "BATEAU"])
    data.append(
        ["Existes, Trouvées (sur terrain)", checkF(typeMae[0]['exist']), checkF(typeMae[1]['exist']), checkF(typeMae[2]['exist'])]
    )
    data.append(
        ["En bon état", checkF(typeMae[0]['BE']), checkF(typeMae[1]['BE']), checkF(typeMae[2]['BE'])]
    )
    data.append(
        ["Inscription de privilège tribunal", checkF(typeMae[0]['privilege']), checkF(typeMae[1]['privilege']), checkF(typeMae[2]['privilege'])]
    )
    data.append(
        ["Inscription de gage APMF\n(vedette, bateau) / véhicule", "", checkF(typeMae[1]['gage']), checkF(typeMae[2]['gage'])]
    )
    data.append(
        ["Photocopie carte grise\ndu véhicule", "", checkF(typeMae[1]['grise']), ""]
    )

    col_widths = [50, 20, 20, 20]  # Largeur des colonnes
    pdf.add_table(data, col_widths)

    pdf.ln(5)

    data = []
    data.append(
        ["Si garantie immobilière, \nl'acte est-i de type", "Bon état", "Sous seing\nprivé\nconforme ?", "Notarié ?"]
    )

    if len(typeImmo) > 0:
        i = 1
        for item in typeImmo:
            data.append([f"TERRAIN {i}", checkF(item['BE']), checkF(item['seingConforme']), checkF(item['hypotheque'])])
            i += 1
    
    col_widths = [50, 20, 20, 20]  # Largeur des colonnes
    pdf.add_table(data, col_widths, ter=True)

    pdf.ln(3)

    pdf.set_y(34)
    pdf.set_x(x= (pdf.w / 2) + 20)

    pdf.chapter_title(4, 'RENSEIGNEMENT SUR LA CAUTION')
    data = [
        ["Rubriques", "Oui"],
        ["Hypothèque", checkF(hypoCau)],
        ["Existe", checkF(existCau)],
        ["Trouvé", checkF(trouveCau)],
        ["Solvable", checkF(solveCau)]
    ]
    col_widths = [50, 20]  # Largeur des colonnes
    pdf.add_table2(data, col_widths)

    pdf.ln(3)
    pdf.set_x(x= (pdf.w / 2) + 20)

    pdf.chapter_title(5, 'DATE DE RECEPTION')
    data = [
        ["Rubriques", "Date"],
        ["Date de passation", dateP]
    ]
    col_widths = [50, 20]  # Largeur des colonnes
    pdf.add_table2(data, col_widths)


    pdf.set_fill_color(220, 220, 220)
    pdf.set_font('Arial', 'I', 7)
    pdf.ln(0.3)
    pdf.set_x(x= (pdf.w / 2) + 30)
    pdf.cell(60, 5, 'Paraphe du responsable du dossier pour cette date', 0, 1, fill=True)

    pdf.ln(2)
    pdf.set_x(x= (pdf.w / 2) + 20)

    pdf.chapter_title(6, 'RENSEIGNEMENT SUR LE CREDIT')
    data = [
        ["Rubriques", "Informations"],
        ["Rib", rib],
        ["Responsable", responsable],
        ["Date du déblocage", dateO],
        ["Durée", duree],
        ["Montant octroyé", montant],
        ["Nombre jour de retard", retard],
        ["Solde capital", capital],
        ["Solde intérêt", interet],
        ["Solde pénalité", penalite]
    ]
    col_widths = [50, 20]  # Largeur des colonnes
    pdf.add_table2(data, col_widths)

    pdf.ln(3)
    pdf.set_x(x= (pdf.w / 2) + 20)

    pdf.chapter_title(7, 'SCORING')
    data = [
        ["SCORE", scoring]
    ]
    col_widths = [50, 20]  # Largeur des colonnes
    pdf.add_table2(data, col_widths, score=True)

    pdf.set_line_width(0.1)

    pdf.ln(5)
    pdf.set_x(x= (pdf.w / 2) + 20)
    pdf.cell(60, 5, 'LE RESPONSABLE DU DOSSIER', 0, 1)
    pdf.set_x(x= (pdf.w / 2) + 21)
    pdf.cell(45, 0.01, '', 1, 1)

    pdf.ln(15)
    pdf.set_x(x= (pdf.w / 2) + 20)
    pdf.cell(60, 5, 'JURISTE DE L\'AGENCE', 0, 1)
    pdf.set_x(x= (pdf.w / 2) + 21)
    pdf.cell(32, 0.01, '', 1, 1)

    # Enregistrer le fichier PDF dans le dossier spécifié
    return pdf
