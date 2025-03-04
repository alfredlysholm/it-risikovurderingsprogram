import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os
import sys
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfgen import canvas
from PIL import Image as PILImage, ImageDraw, ImageFont

# Konfigurer logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('it_risikovurdering.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ITRisikovurderingsApp:
    def __init__(self, master):
        self.master = master
        self.master.title("IT Risikovurdering v1.0.0")
        self.master.geometry("1200x800")
        
        # Program information
        self.VERSION = "1.0.0"
        self.DEVELOPER = "Alfred Lysholm Clausen"
        self.SUPPORT_EMAIL = "alcla@trafikstyrelsen.dk"
        self.SUPPORT_PHONE = "+4541781909"
        
        # Sæt baggrundsfarve
        self.master.configure(bg='#e6e9ef')
        
        # Konfigurer stil for ttk widgets
        style = ttk.Style()
        
        # Hovedfarver
        PRIMARY_COLOR = '#1a73e8'
        SECONDARY_COLOR = '#000000'  # Ændret til sort
        BACKGROUND_COLOR = '#ffffff'
        HOVER_COLOR = '#1557b0'
        
        # Radiobutton stil
        style.configure('TRadiobutton',
                       font=('Helvetica', 11),
                       background=BACKGROUND_COLOR,
                       foreground=SECONDARY_COLOR,
                       indicatorsize=20,  # Endnu større indikator
                       padding=[12, 8])   # Mere padding for bedre layout
        
        # Definerer en custom stil for radiobuttons
        self.master.option_add('*TRadiobutton*Indicator.diameter', 20)
        self.master.option_add('*TRadiobutton*Indicator.borderWidth', 2)
        
        # Tilføjer tydelig hover-effekt
        style.map('TRadiobutton',
                 background=[('active', '#e8f0fe'), ('pressed', '#d2e3fc')],  # Lysere baggrund ved hover
                 foreground=[('active', PRIMARY_COLOR), ('selected', PRIMARY_COLOR)],
                 indicatorcolor=[('selected', PRIMARY_COLOR), ('active', PRIMARY_COLOR), ('', '#d0d0d0')],  # Farve ændring ved hover
                 indicatorbackground=[('pressed', '#d2e3fc'), 
                                    ('active', '#f8f9fa'), 
                                    ('selected', 'white'),
                                    ('!disabled', 'white')],
                 relief=[('active', 'flat')])
        
        # Knap stil
        style.configure('TButton',
                       font=('Helvetica', 11),
                       background=PRIMARY_COLOR,
                       foreground='black',
                       padding=[10, 5])
        
        style.map('TButton',
                 background=[('active', HOVER_COLOR), ('disabled', '#cccccc')],
                 foreground=[('active', 'black'), ('disabled', '#666666')])

        # Notebook stil
        style.configure('TNotebook', background='#e6e9ef')
        style.configure('TNotebook.Tab', 
                       padding=[20, 10],
                       font=('Helvetica', 11, 'bold'),  
                       background='#ffffff',
                       foreground='black')  
        
        style.map('TNotebook.Tab',
                 background=[('selected', '#e6e9ef')],  
                 foreground=[('selected', 'black')],    
                 expand=[('selected', [1, 1, 1, 0])])   
        
        # Frame stil
        style.configure('TFrame', background=BACKGROUND_COLOR)
        
        # Label stil
        style.configure('Header.TLabel',
                       font=('Helvetica', 24, 'bold'),
                       background=BACKGROUND_COLOR,
                       foreground=SECONDARY_COLOR)
        
        style.configure('Subheader.TLabel',
                       font=('Helvetica', 16),
                       background=BACKGROUND_COLOR,
                       foreground=SECONDARY_COLOR)
        
        style.configure('TLabel',
                       font=('Helvetica', 11),
                       background=BACKGROUND_COLOR,
                       foreground=SECONDARY_COLOR)
        
        # Entry stil
        style.configure('TEntry', 
                       fieldbackground=BACKGROUND_COLOR,
                       foreground=SECONDARY_COLOR)
        
        # Label stil for velkomsttekst
        style.configure('Welcome.TLabel',
                       font=('Helvetica', 12),
                       background='#f8f9fa',
                       foreground=SECONDARY_COLOR,
                       padding=[20, 20],
                       wraplength=800)
        
        # Beskrivelsestekst stil
        style.configure('Description.TLabel',
                       font=('Helvetica', 11),
                       background='#f8f9fa',
                       foreground=SECONDARY_COLOR,
                       padding=[20, 10],
                       wraplength=800)
        
        # Initialiser StringVar variabler
        self.system_name = tk.StringVar()
        self.system_owner = tk.StringVar()
        self.system_supplier = tk.StringVar()
        self.assessment_responsible = tk.StringVar()
        self.assessment_date = tk.StringVar()
        
        # Initialiser variabler for vurderinger
        self.kritikalitet_vars = {}
        self.gdpr_vars = {}
        self.fortrolighed_vars = {}
        self.integritet_vars = {}
        self.robusthed_vars = {}
        self.tilgaengelighed_vars = {}
        
        # Initialiser kommentar dictionaries
        self.kritikalitet_comments = {}
        self.gdpr_comments = {}
        self.fortrolighed_comments = {}
        self.integritet_comments = {}
        self.robusthed_comments = {}
        self.tilgaengelighed_comments = {}
        
        # Initialiser current_assessment dictionary
        self.current_assessment = {
            'system_info': {},
            'kritikalitet': {},
            'gdpr': {},
            'fortrolighed': {},
            'integritet': {},
            'robusthed': {},
            'tilgaengelighed': {}
        }
        
        # Opret menubar med moderne stil
        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)
        
        # Fil menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Fil", menu=self.file_menu)
        self.file_menu.add_command(label="Gem vurdering", command=self.save_assessment)
        self.file_menu.add_command(label="Åbn vurdering", command=self.open_assessment)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Afslut", command=self.master.quit)

        # Info menu
        self.info_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Info", menu=self.info_menu)
        self.info_menu.add_command(label="Om programmet", command=self.show_about)

        # Opret notebook
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Opret frames for hver fane
        self.welcome_frame = ttk.Frame(self.notebook)
        self.system_info_frame = ttk.Frame(self.notebook)
        self.kritikalitet_frame = ttk.Frame(self.notebook)
        self.gdpr_frame = ttk.Frame(self.notebook)
        self.fortrolighed_frame = ttk.Frame(self.notebook)
        self.integritet_frame = ttk.Frame(self.notebook)
        self.robusthed_frame = ttk.Frame(self.notebook)
        self.tilgaengelighed_frame = ttk.Frame(self.notebook)
        self.rapport_frame = ttk.Frame(self.notebook)
        
        # Tilføj frames til notebook
        self.notebook.add(self.welcome_frame, text="Velkommen")
        self.notebook.add(self.system_info_frame, text="System Information")
        self.notebook.add(self.kritikalitet_frame, text="Kritikalitetsvurdering")
        self.notebook.add(self.gdpr_frame, text="GDPR Vurdering")
        self.notebook.add(self.fortrolighed_frame, text="Fortrolighedsvurdering")
        self.notebook.add(self.integritet_frame, text="Integritetsvurdering")
        self.notebook.add(self.robusthed_frame, text="Robusthedsvurdering")
        self.notebook.add(self.tilgaengelighed_frame, text="Tilgængelighedsvurdering")
        self.notebook.add(self.rapport_frame, text="Samlet Risikovurdering")
        
        # Opret velkomstside
        welcome_container = ttk.Frame(self.welcome_frame, style='TFrame')
        welcome_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Velkomstbesked
        welcome_text = """Velkommen til IT-Risikovurdering! Dette program er udviklet til at hjælpe dig med at udføre en vurdering af dit IT-system eller projekt. Formålet er at identificere potentielle risici og sikre, at systemet lever op til gældende sikkerhedskrav og bedste praksis.

Programmet guider dig gennem en række trin, hvor du bliver bedt om at besvare spørgsmål og give relevante oplysninger om systemets sikkerhed, fortrolighed, integritet og robusthed. På baggrund af dine svar genererer programmet en rapport og en risikomatrix, der giver dig et klart overblik over systemets samlede risikoniveau.

For at komme i gang kan du vælge at starte en ny vurdering eller åbne en tidligere gemt vurdering. Uanset hvad, er det vigtigt at besvare spørgsmålene så detaljeret som muligt for at opnå en præcis og brugbar risikovurdering.

Vi håber, at dette værktøj vil gøre det lettere for dig at arbejde struktureret og effektivt med IT-sikkerhed."""
        
        ttk.Label(welcome_container,
                 text=welcome_text,
                 style='Welcome.TLabel',
                 wraplength=800).pack(fill=tk.X, pady=(0, 20))
        
        # Knapper i en frame
        button_frame = ttk.Frame(welcome_container, style='TFrame')
        button_frame.pack(pady=20)
        
        # Start ny vurdering knap
        new_assessment_btn = ttk.Button(
            button_frame,
            text="Start ny vurdering",
            style='Large.TButton',
            command=lambda: self.notebook.select(1)
        )
        new_assessment_btn.pack(pady=(0, 20))
        
        # Åbn eksisterende vurdering knap
        open_assessment_btn = ttk.Button(
            button_frame,
            text="Åbn eksisterende vurdering",
            style='Large.TButton',
            command=self.open_assessment
        )
        open_assessment_btn.pack()

        # Initialiser svar dictionaries
        self.kritikalitet_svar = {}
        self.gdpr_svar = {}
        self.gdpr_text_vars = {}
        self.fortrolighed_svar = {}
        self.integritet_svar = {}
        self.robusthed_svar = {}
        self.tilgaengelighed_svar = {}
        
        # Opret alle sider
        self.create_assessment_page()
        self.create_kritikalitet_page()
        self.create_gdpr_page()
        self.create_fortrolighed_page()
        self.create_integritet_page()
        self.create_robusthed_page()
        self.create_tilgaengelighed_page()
        self.create_rapport_page()
        
        # Bind tab-skift event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        current_tab = self.notebook.select()
        tab_id = self.notebook.index(current_tab)
        
        if tab_id == 1:  # System Information
            if not hasattr(self, 'system_info_created'):
                self.create_assessment_page()
                self.system_info_created = True
        elif tab_id == 2:  # Kritikalitetsvurdering
            if not hasattr(self, 'kritikalitet_created'):
                self.create_kritikalitet_page()
                self.kritikalitet_created = True
        elif tab_id == 3:  # GDPR Vurdering
            if not hasattr(self, 'gdpr_created'):
                self.create_gdpr_page()
                self.gdpr_created = True
        elif tab_id == 4:  # Fortrolighed
            if not hasattr(self, 'fortrolighed_created'):
                self.create_fortrolighed_page()
                self.fortrolighed_created = True
        elif tab_id == 5:  # Integritet
            if not hasattr(self, 'integritet_created'):
                self.create_integritet_page()
                self.integritet_created = True
        elif tab_id == 6:  # Robusthed
            if not hasattr(self, 'robusthed_created'):
                self.create_robusthed_page()
                self.robusthed_created = True
        elif tab_id == 7:  # Tilgængelighed
            if not hasattr(self, 'tilgaengelighed_created'):
                self.create_tilgaengelighed_page()
                self.tilgaengelighed_created = True
        elif tab_id == 8:  # Samlet Rapport
            self.create_rapport_page()

    def create_assessment_page(self):
        # Ryd eksisterende widgets
        for widget in self.system_info_frame.winfo_children():
            widget.destroy()
            
        # Opret container med padding og hvid baggrund
        container = ttk.Frame(self.system_info_frame, style='TFrame', padding="40 40 40 40")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Overskrift
        header = ttk.Label(
            container,
            text="System Information",
            style='Header.TLabel'
        )
        header.pack(pady=(0, 30))
        
        # Input felter i en frame med hvid baggrund
        input_frame = ttk.Frame(container, style='TFrame')
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # System navn
        ttk.Label(input_frame, text="System navn:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        name_entry = ttk.Entry(input_frame, width=50, textvariable=self.system_name)
        name_entry.pack(anchor=tk.W, pady=(0, 15))
        
        # System ejer
        ttk.Label(input_frame, text="System ejer:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        owner_entry = ttk.Entry(input_frame, width=50, textvariable=self.system_owner)
        owner_entry.pack(anchor=tk.W, pady=(0, 15))
        
        # System leverandør
        ttk.Label(input_frame, text="System leverandør:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        supplier_entry = ttk.Entry(input_frame, width=50, textvariable=self.system_supplier)
        supplier_entry.pack(anchor=tk.W, pady=(0, 15))
        
        # Vurderingsansvarlig
        ttk.Label(input_frame, text="Vurderingsansvarlig:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        responsible_entry = ttk.Entry(input_frame, width=50, textvariable=self.assessment_responsible)
        responsible_entry.pack(anchor=tk.W, pady=(0, 15))
        
        # Dato for vurdering
        ttk.Label(input_frame, text="Dato for vurdering:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        date_entry = ttk.Entry(input_frame, width=50, textvariable=self.assessment_date)
        date_entry.pack(anchor=tk.W, pady=(0, 15))
        # Sæt den aktuelle dato hvis feltet er tomt
        if not self.assessment_date.get():
            self.assessment_date.set(datetime.now().strftime("%Y-%m-%d"))
        
        # System beskrivelse
        ttk.Label(input_frame, text="System beskrivelse:", style='TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.system_description = tk.Text(input_frame, width=50, height=10)
        self.system_description.pack(anchor=tk.W, pady=(0, 20))
        
        # Knapper i bunden
        button_frame = ttk.Frame(container, style='TFrame')
        button_frame.pack(pady=20)
        
        # Gem knap
        save_button = ttk.Button(
            button_frame,
            text="Gem vurdering",
            style='Large.TButton',
            command=self.save_assessment
        )
        save_button.pack(side=tk.LEFT, padx=10)
        
        # Næste knap
        next_button = ttk.Button(
            button_frame,
            text="Næste →",
            style='Large.TButton',
            command=lambda: self.notebook.select(2)
        )
        next_button.pack(side=tk.LEFT, padx=10)

    def create_kritikalitet_page(self):
        for widget in self.kritikalitet_frame.winfo_children():
            widget.destroy()
            
        # Overskrift og forklaring
        header_label = ttk.Label(
            self.kritikalitet_frame,
            text="Kritikalitetsvurdering",
            font=("Helvetica", 20, "bold")
        )
        header_label.pack(pady=(20,5))
        
        info_text = """Kritikalitetsvurderingen danner basis for valg af serviceniveau hos leverandøren 
samt planlægning af nødberedskab (forretningsvidereførelse)."""
        info_label = ttk.Label(
            self.kritikalitet_frame,
            text=info_text,
            wraplength=900
        )
        info_label.pack(pady=(0,20))
        
        # Opret en canvas og scrollbar
        canvas = tk.Canvas(self.kritikalitet_frame)
        scrollbar = ttk.Scrollbar(self.kritikalitet_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Spørgsmål og radiobuttons
        self.kritikalitet_vars = {}
        spørgsmål = [
            "1. Indeholder systemet data, som er væsentlige for at styrelsen kan udføre sine kerneopgaver?",
            "2. Vil styrelsens kerneaktiviteter blive væsentligt påvirkede, hvis systemet er utilgængeligt i mere end 24 timer?",
            "3. Vil et længerevarende systemnedbrud kunne have indvirkning på personers liv og helbred?",
            "4. Kan en fejl eller kompromittering af systemet føre til fysiske skader på personer eller materiel i forbindelse med luftfart?",
            "5. Har systemet en direkte eller indirekte rolle i sikkerheden ved luftfart?",
            "6. Er systemet samfundskritisk? (er det omfattet af NIS2-direktivets krav til væsentlige eller vigtige sektorer + DIGST's definition)?",
            "7. Er der risiko for væsentlige økonomiske eller omdømmemæssige tab for styrelsen, hvis systemet kompromitteres eller fejler?",
            "8. Kan nedetid i systemet påvirke andre organisationer, myndigheder eller sektorer negativt?",
            "9. Er systemet integreret med andre kritiske systemer, hvor fejl kan skabe dominoeffekter?",
            "10. Behandler systemet personoplysninger?",
            "11. Behandler systemet data, som er omfattet af Sikkerhedscirkulæret? (klassificeret information TTJ/FTR/HEM/YHEM)",
            "12. Er systemet udsat for en væsentlig risiko for cyberangreb eller misbrug?",
            "13. Anvender systemet nye teknologier som fx kunstig intelligens, hvor bias eller fejl i output kan føre til væsentlige konsekvenser for styrelsen eller de registrerede (GDPR?)?",
            "14. Kan fejl i systemet føre til juridiske eller regulatoriske sanktioner, fx bøder?"
        ]

        # Point for hvert spørgsmål
        self.point_vægte = {spørgsmål[i]: vægt for i, vægt in enumerate([5,5,8,8,8,6,4,4,4,3,5,4,3,3])}

        for spørgsmål_text in spørgsmål:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Spørgsmålstekst
            label = ttk.Label(frame, text=spørgsmål_text, wraplength=750)
            label.pack(side=tk.LEFT, pady=5)
            
            # Opret StringVar med standardværdi "Nej"
            var = tk.StringVar()
            var.set("Nej")  # Sæt standardværdi
            self.kritikalitet_vars[spørgsmål_text] = var
            
            # Radio-knapper frame
            radio_frame = ttk.Frame(frame)
            radio_frame.pack(side=tk.RIGHT, padx=30)
            
            # Ja knap
            ja_radio = ttk.Radiobutton(
                radio_frame,
                text="Ja",
                value="Ja",
                variable=var,
                command=lambda s=spørgsmål_text: self.on_radio_click(s)
            )
            ja_radio.pack(side=tk.LEFT, padx=15)
            
            # Nej knap
            nej_radio = ttk.Radiobutton(
                radio_frame,
                text="Nej",
                value="Nej",
                variable=var,
                command=lambda s=spørgsmål_text: self.on_radio_click(s)
            )
            nej_radio.pack(side=tk.LEFT, padx=15)
            
            # Kommentarfelt
            comment_frame = self.create_comment_section(frame, 'kritikalitet', spørgsmål_text)
            comment_frame.pack(side=tk.RIGHT, padx=10)

        # Separator
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=20)

        # Resultat frame
        result_frame = ttk.LabelFrame(scrollable_frame, text="Resultat af kritikalitetsvurdering")
        result_frame.pack(fill=tk.X, padx=20, pady=20)
        
        inner_result_frame = ttk.Frame(result_frame)
        inner_result_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Resultat labels
        self.score_label = ttk.Label(
            inner_result_frame,
            text="Score: 0",
            font=('Helvetica', 12, 'bold')
        )
        self.score_label.pack(pady=5)
        
        self.kritikalitet_label = ttk.Label(
            inner_result_frame,
            text="Kritikalitet: D",
            font=('Helvetica', 12, 'bold')
        )
        self.kritikalitet_label.pack(pady=5)
        
        self.forklaring_label = ttk.Label(
            inner_result_frame,
            text="Forklaring: Systemafbrud medfører mindre ulemper og begrænsede tab eller omkostninger.",
            wraplength=800
        )
        self.forklaring_label.pack(pady=5)

        # Gem knap
        save_button = ttk.Button(
            scrollable_frame,
            text="Gem vurdering",
            command=self.save_assessment
        )
        save_button.pack(pady=20)

        # Pack canvas og scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y")
        
        print("Kritikalitetsvurdering oprettet")

    def on_radio_click(self, spørgsmål_text):
        """Håndterer klik på radio-knap"""
        var = self.kritikalitet_vars[spørgsmål_text]
        value = var.get()
        
        print(f"\nRadio-knap klikket:")
        print(f"Spørgsmål: '{spørgsmål_text}'")
        print(f"Valgt værdi: {value}")
        
        self.update_kritikalitet()

    def update_kritikalitet(self):
        """Opdaterer den samlede kritikalitetsscore"""
        print("\nBeregner kritikalitetsscore:")
        total_score = 0
        
        # Beregn total score
        for spørgsmål, var in self.kritikalitet_vars.items():
            svar = var.get()
            print(f"\nSpørgsmål: '{spørgsmål}'")
            print(f"Svar: {svar}")
            if svar == "Ja":
                vægt = self.point_vægte.get(spørgsmål, 0)
                total_score += vægt
                print(f"Vægt: {vægt}")
                print(f"Løbende score: {total_score}")
        
        # Bestem kritikalitet og forklaring baseret på score
        if total_score > 50:  # A: Over 50 point
            kritikalitet = "A"
            forklaring = "Korte systemafbrud (timer) vil medføre katastrofale følgevirkninger for forretningen som følge af væsentlige og uoprettelige svigt i målopfyldelse eller brud på love og aftaler"
        elif total_score >= 21:  # B: 21-50 point
            kritikalitet = "B"
            forklaring = "Langvarige system-afbrud (dage) vil medføre alvorlige følgevirkninger for forretningen som følge af væsentlige og uoprettelige svigt i målopnåelse eller brud på love og aftaler."
        elif total_score >= 12:  # C: 12-20 point
            kritikalitet = "C"
            forklaring = "Systemafbrud vil medføre væsentlig ulempe, men ikke i væsentlig grad hindre målopfyldelse eller føre til brud på love eller aftaler."
        else:  # D: Under 11 point
            kritikalitet = "D"
            forklaring = "Systemafbrud medfører mindre ulemper og begrænsede tab eller omkostninger."
        
        print(f"\nEndelig vurdering:")
        print(f"Total score: {total_score}")
        print(f"Kritikalitet: {kritikalitet}")
        print(f"Forklaring: {forklaring}")
        
        # Opdater labels
        self.score_label.config(text=f"Score: {total_score}")
        self.kritikalitet_label.config(text=f"Kritikalitet: {kritikalitet}")
        self.forklaring_label.config(text=f"Forklaring: {forklaring}")

    def create_gdpr_page(self):
        for widget in self.gdpr_frame.winfo_children():
            widget.destroy()
            
        # Overskrift
        header_label = ttk.Label(
            self.gdpr_frame,
            text="GDPR Vurdering",
            font=("Helvetica", 20, "bold")
        )
        header_label.pack(pady=20)
        
        # Opret en canvas og scrollbar
        canvas = tk.Canvas(self.gdpr_frame)
        scrollbar = ttk.Scrollbar(self.gdpr_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # GDPR spørgsmål med kombineret ja/nej og tekstfelter
        gdpr_spørgsmål = [
            ("1. Behandler systemet almindelige personoplysninger?", True),
            ("2. Behandler systemet CPR-numre eller oplysninger om strafbare forhold?", False),
            ("3. Behandler systemet følsomme eller særligt beskyttelsesværdige personoplysninger?", True),
            ("4. Behandler systemet persondata om flere end 5000 personer?", False),
            ("5. Bliver der overført data til lande uden for EU/EØS?", True),
            ("6. Er der hjemmel til behandlingen?", True),
            ("7. Gør systemet brug af automatisk beslutningstagning eller profilering?", False),
            ("8. Foretager systemet systematisk overvågning?", False),
            ("9. Er der udarbejdet en databehandleraftale?", False),
            ("10. Er der etableret procedurer for sletning af personoplysninger?", False),
            ("11. Er behandlingsaktiviteterne beskrevet i fortegnelsen?", False),
            ("12. Skal der udarbejdes en konsekvensanalyse?", False)
        ]

        self.gdpr_vars = {}
        self.gdpr_text_vars = {}

        for spørgsmål, has_text in gdpr_spørgsmål:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Spørgsmålstekst
            label = ttk.Label(frame, text=spørgsmål, wraplength=750)
            label.pack(side=tk.LEFT, pady=5)
            
            # Radio buttons frame
            radio_frame = ttk.Frame(frame)
            radio_frame.pack(side=tk.RIGHT, padx=30)
            
            var = tk.StringVar(value="Nej")
            self.gdpr_vars[spørgsmål] = var
            
            tk.Radiobutton(
                radio_frame, 
                text="Ja", 
                value="Ja", 
                variable=var,
                font=("Helvetica", 10),
                bg="white",
                selectcolor="lightblue",
                width=6,
                height=1,
                command=lambda s=spørgsmål: self.on_gdpr_change(s)
            ).pack(side=tk.LEFT, padx=15)
            
            tk.Radiobutton(
                radio_frame, 
                text="Nej", 
                value="Nej", 
                variable=var,
                font=("Helvetica", 10),
                bg="white",
                selectcolor="lightblue",
                width=6,
                height=1,
                command=lambda s=spørgsmål: self.on_gdpr_change(s)
            ).pack(side=tk.LEFT, padx=15)

            # Hvis spørgsmålet skal have tekstfelt
            if has_text:
                text_frame = ttk.Frame(scrollable_frame)
                text_frame.pack(fill=tk.X, padx=50, pady=(0, 10))
                
                text_var = tk.Text(text_frame, height=2, width=80)
                text_var.pack(fill=tk.X)
                self.gdpr_text_vars[spørgsmål] = text_var
                
            # Tilføj kommentarfelt
            comment_frame = self.create_comment_section(frame, 'gdpr', spørgsmål)
            comment_frame.pack(side=tk.RIGHT, padx=10)

        # Pack canvas og scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y")

        # Gem knap
        save_button = ttk.Button(
            scrollable_frame,
            text="Gem vurdering",
            command=self.save_assessment
        )
        save_button.pack(pady=20)

    def on_gdpr_change(self, spørgsmål):
        # Gem GDPR svar når der laves ændringer
        self.save_gdpr_data()

    def save_gdpr_data(self):
        gdpr_data = {}
        for spørgsmål, var in self.gdpr_vars.items():
            # Brug et unikt ID i stedet for hele spørgsmålsteksten
            spørgsmål_id = f"gdpr_spm_{list(self.gdpr_vars.keys()).index(spørgsmål) + 1}"
            svar = {
                "spørgsmål": spørgsmål,  # Gem selve spørgsmålet som en værdi
                "svar": var.get()
            }
            if spørgsmål in self.gdpr_text_vars:
                uddybende = self.gdpr_text_vars[spørgsmål].get("1.0", tk.END).strip()
                if uddybende:
                    svar["uddybende"] = uddybende
            gdpr_data[spørgsmål_id] = svar
        self.gdpr_svar = gdpr_data

    def create_fortrolighed_page(self):
        for widget in self.fortrolighed_frame.winfo_children():
            widget.destroy()
            
        # Overskrift
        header_label = ttk.Label(
            self.fortrolighed_frame,
            text="Fortrolighedsvurdering",
            font=("Helvetica", 20, "bold")
        )
        header_label.pack(pady=20)
        
        # Opret en canvas og scrollbar
        canvas = tk.Canvas(self.fortrolighed_frame)
        scrollbar = ttk.Scrollbar(self.fortrolighed_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Fortroligheds spørgsmål
        fortrolighed_spørgsmål = [
            "1. Kan læk af data skade Trafikstyrelsen eller andre?",
            "2. Har brugerne af systemet adgang til data ud over deres arbejdsrelaterede behov?",
            "3. Er data, der behandles i systemet, tilgængelige for eksterne parter?",
            "4. Mangler der kryptering i systemet under overførsel og under lagring?",
            "5. Har uvedkommende tidligere haft adgang til data i systemet?"
        ]

        self.fortrolighed_vars = {}

        for spørgsmål in fortrolighed_spørgsmål:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Spørgsmålstekst
            label = ttk.Label(frame, text=spørgsmål, wraplength=750)
            label.pack(side=tk.LEFT, pady=5)
            
            # Radio buttons frame
            radio_frame = ttk.Frame(frame)
            radio_frame.pack(side=tk.RIGHT, padx=30)
            
            var = tk.StringVar(value="Nej")
            self.fortrolighed_vars[spørgsmål] = var
            
            tk.Radiobutton(
                radio_frame, 
                text="Ja", 
                value="Ja", 
                variable=var,
                command=lambda s=spørgsmål: self.on_fortrolighed_change(s),
                font=("Helvetica", 10),
                bg="white",
                selectcolor="lightblue",
                width=6,
                height=1
            ).pack(side=tk.LEFT, padx=15)
            
            tk.Radiobutton(
                radio_frame, 
                text="Nej", 
                value="Nej", 
                variable=var,
                command=lambda s=spørgsmål: self.on_fortrolighed_change(s),
                font=("Helvetica", 10),
                bg="white",
                selectcolor="lightblue",
                width=6,
                height=1
            ).pack(side=tk.LEFT, padx=15)
            
            # Tilføj kommentarfelt
            comment_frame = self.create_comment_section(frame, 'fortrolighed', spørgsmål)
            comment_frame.pack(side=tk.RIGHT, padx=10)

        # Separator før resultat
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=20)

        # Resultat frame
        result_frame = ttk.LabelFrame(scrollable_frame, text="Resultat af fortrolighedsvurdering")
        result_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Indre frame til resultatet
        inner_result_frame = ttk.Frame(result_frame)
        inner_result_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.fortrolighed_result_label = ttk.Label(
            inner_result_frame,
            text="Ingen kritiske fortrolighedsproblemer identificeret",
            wraplength=800,
            style='Result.TLabel'
        )
        self.fortrolighed_result_label.pack(pady=5)

        # Pack canvas og scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y")

        # Gem knap
        save_button = ttk.Button(
            scrollable_frame,
            text="Gem vurdering",
            command=self.save_assessment
        )
        save_button.pack(pady=20)

    def on_fortrolighed_change(self, spørgsmål):
        self.save_fortrolighed_data()
        self.update_fortrolighed_result()

    def update_fortrolighed_result(self):
        # Tæl antal "Ja" svar
        ja_count = sum(1 for var in self.fortrolighed_vars.values() if var.get() == "Ja")
        
        if ja_count == 0:
            result = "Ingen kritiske fortrolighedsproblemer identificeret"
        elif ja_count <= 2:
            result = "Der er identificeret nogle fortrolighedsproblemer som bør adresseres"
        else:
            result = "Der er identificeret kritiske fortrolighedsproblemer som kræver øjeblikkelig handling"
            
        self.fortrolighed_result_label.config(text=result)

    def save_fortrolighed_data(self):
        fortrolighed_data = {}
        for spørgsmål, var in self.fortrolighed_vars.items():
            fortrolighed_data[f"spm_{list(self.fortrolighed_vars.keys()).index(spørgsmål) + 1}"] = {
                "spørgsmål": spørgsmål,
                "svar": var.get()
            }
        self.fortrolighed_svar = fortrolighed_data

    def create_integritet_page(self):
        for widget in self.integritet_frame.winfo_children():
            widget.destroy()
            
        # Overskrift
        header_label = ttk.Label(
            self.integritet_frame,
            text="Integritetsvurdering",
            font=("Helvetica", 20, "bold")
        )
        header_label.pack(pady=20)
        
        # Opret en canvas og scrollbar
        canvas = tk.Canvas(self.integritet_frame)
        scrollbar = ttk.Scrollbar(self.integritet_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Integritets spørgsmål
        integritet_spørgsmål = [
            "1. Er der risiko for uautoriseret ændring af data?",
            "2. Kan fejl i data medføre alvorlige konsekvenser?",
            "3. Er der krav om sporbarhed af dataændringer?",
            "4. Er systemets integritet afgørende for forretningen?",
            "5. Er der særlige lovkrav til datakvalitet?"
        ]

        self.integritet_vars = {}

        for spørgsmål in integritet_spørgsmål:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Spørgsmålstekst
            label = ttk.Label(frame, text=spørgsmål, wraplength=750)
            label.pack(side=tk.LEFT, pady=5)
            
            # Radio buttons frame
            radio_frame = ttk.Frame(frame)
            radio_frame.pack(side=tk.RIGHT, padx=30)
            
            var = tk.StringVar(value="Nej")
            self.integritet_vars[spørgsmål] = var
            
            tk.Radiobutton(
                radio_frame, 
                text="Ja", 
                value="Ja", 
                variable=var,
                command=lambda s=spørgsmål: self.on_integritet_change(s),
                font=("Helvetica", 10),
                bg="white",
                selectcolor="lightblue",
                width=6,
                height=1
            ).pack(side=tk.LEFT, padx=15)
            
            tk.Radiobutton(
                radio_frame, 
                text="Nej", 
                value="Nej", 
                variable=var,
                command=lambda s=spørgsmål: self.on_integritet_change(s),
                font=("Helvetica", 10),
                bg="white",
                selectcolor="lightblue",
                width=6,
                height=1
            ).pack(side=tk.LEFT, padx=15)
            
            # Tilføj kommentarfelt
            comment_frame = self.create_comment_section(frame, 'integritet', spørgsmål)
            comment_frame.pack(side=tk.RIGHT, padx=10)

        # Separator før resultat
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=20)

        # Resultat frame
        result_frame = ttk.LabelFrame(scrollable_frame, text="Resultat af integritetsvurdering")
        result_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Indre frame til resultatet
        inner_result_frame = ttk.Frame(result_frame)
        inner_result_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.integritet_result_label = ttk.Label(
            inner_result_frame,
            text="Systemet har normal integritetsbehov",
            wraplength=800,
            style='Result.TLabel'
        )
        self.integritet_result_label.pack(pady=5)

        # Pack canvas og scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y")

        # Gem knap
        save_button = ttk.Button(
            scrollable_frame,
            text="Gem vurdering",
            command=self.save_assessment
        )
        save_button.pack(pady=20)

    def on_integritet_change(self, spørgsmål):
        self.save_integritet_data()
        self.update_integritet_result()

    def update_integritet_result(self):
        # Tæl antal "Ja" svar
        ja_count = sum(1 for var in self.integritet_vars.values() if var.get() == "Ja")
        
        if ja_count <= 1:
            result = "Systemet har normal integritetsbehov"
        elif ja_count <= 3:
            result = "Systemet har forhøjet integritetsbehov - implementer passende kontroller"
        else:
            result = "Systemet har kritisk integritetsbehov - strenge kontroller er påkrævet"
            
        self.integritet_result_label.config(text=result)

    def save_integritet_data(self):
        integritet_data = {}
        for spørgsmål, var in self.integritet_vars.items():
            integritet_data[f"spm_{list(self.integritet_vars.keys()).index(spørgsmål) + 1}"] = {
                "spørgsmål": spørgsmål,
                "svar": var.get()
            }
        self.integritet_svar = integritet_data

    def create_robusthed_page(self):
        for widget in self.robusthed_frame.winfo_children():
            widget.destroy()
            
        # Overskrift
        header_label = ttk.Label(
            self.robusthed_frame,
            text="Robusthedsvurdering",
            font=("Helvetica", 20, "bold")
        )
        header_label.pack(pady=20)
        
        # Opret en canvas og scrollbar
        canvas = tk.Canvas(self.robusthed_frame)
        scrollbar = ttk.Scrollbar(self.robusthed_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Robustheds spørgsmål
        robusthed_spørgsmål = [
            "1. Har systemet tidligere været udsat for nedbrud eller sikkerhedshændelser med væsentlige konsekvenser?",
            "2. Kan fejl eller sikkerhedsbrud i systemet føre til tab eller ødelæggelse af data, som ikke kan genskabes fra andre systemer eller kilder?",
            "3. Er systemet afhængigt af en specifik teknologi eller leverandør, hvor der ikke findes alternativer?",
            "4. Er der risiko for, at leverandøren ikke kan levere som aftalt, fx pga. økonomiske problemer, konkurser eller geopolitiske forhold?",
            "5. Er leverandøren afhængig af underleverandører, der kan påvirke systemets sikkerhed eller drift?"
        ]

        self.robusthed_vars = {}

        for spørgsmål in robusthed_spørgsmål:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Spørgsmålstekst
            label = ttk.Label(frame, text=spørgsmål, wraplength=750)
            label.pack(side=tk.LEFT, pady=5)
            
            # Radio buttons frame
            radio_frame = ttk.Frame(frame)
            radio_frame.pack(side=tk.RIGHT, padx=30)
            
            var = tk.StringVar(value="Nej")
            self.robusthed_vars[spørgsmål] = var
            
            tk.Radiobutton(
                radio_frame, 
                text="Ja", 
                value="Ja", 
                variable=var,
                command=lambda s=spørgsmål: self.on_robusthed_change(s),
                font=("Helvetica", 10),
                bg="white",
                selectcolor="lightblue",
                width=6,
                height=1
            ).pack(side=tk.LEFT, padx=15)
            
            tk.Radiobutton(
                radio_frame, 
                text="Nej", 
                value="Nej", 
                variable=var,
                command=lambda s=spørgsmål: self.on_robusthed_change(s),
                font=("Helvetica", 10),
                bg="white",
                selectcolor="lightblue",
                width=6,
                height=1
            ).pack(side=tk.LEFT, padx=15)
            
            # Tilføj kommentarfelt
            comment_frame = self.create_comment_section(frame, 'robusthed', spørgsmål)
            comment_frame.pack(side=tk.RIGHT, padx=10)

        # Separator før resultat
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=20)

        # Resultat frame
        result_frame = ttk.LabelFrame(scrollable_frame, text="Resultat af robusthedsvurdering")
        result_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Indre frame til resultatet
        inner_result_frame = ttk.Frame(result_frame)
        inner_result_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.robusthed_result_label = ttk.Label(
            inner_result_frame,
            text="Systemet har tilstrækkelig robusthed",
            wraplength=800,
            style='Result.TLabel'
        )
        self.robusthed_result_label.pack(pady=5)

        # Pack canvas og scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y")

        # Gem knap
        save_button = ttk.Button(
            scrollable_frame,
            text="Gem vurdering",
            command=self.save_assessment
        )
        save_button.pack(pady=20)

    def on_robusthed_change(self, spørgsmål):
        self.save_robusthed_data()
        self.update_robusthed_result()

    def update_robusthed_result(self):
        # Tæl antal "Ja" svar
        ja_count = sum(1 for var in self.robusthed_vars.values() if var.get() == "Ja")
        
        if ja_count == 0:
            result = "Systemet har tilstrækkelig robusthed"
        elif ja_count <= 2:
            result = "Der er identificeret robusthedsudfordringer som bør adresseres"
        else:
            result = "Der er alvorlige robusthedsudfordringer som kræver øjeblikkelig handling"
            
        self.robusthed_result_label.config(text=result)

    def save_robusthed_data(self):
        robusthed_data = {}
        for spørgsmål, var in self.robusthed_vars.items():
            robusthed_data[f"spm_{list(self.robusthed_vars.keys()).index(spørgsmål) + 1}"] = {
                "spørgsmål": spørgsmål,
                "svar": var.get()
            }
        self.robusthed_svar = robusthed_data

    def create_tilgaengelighed_page(self):
        for widget in self.tilgaengelighed_frame.winfo_children():
            widget.destroy()
            
        # Overskrift
        header_label = ttk.Label(
            self.tilgaengelighed_frame,
            text="Tilgængelighedsvurdering",
            font=("Helvetica", 20, "bold")
        )
        header_label.pack(pady=20)

        # Underoverskrift
        sub_header = ttk.Label(
            self.tilgaengelighed_frame,
            text="Vurder konsekvensen hvis systemet er utilgængeligt i følgende perioder:",
            font=("Helvetica", 12)
        )
        sub_header.pack(pady=10)
        
        # Opret en canvas og scrollbar
        canvas = tk.Canvas(self.tilgaengelighed_frame)
        scrollbar = ttk.Scrollbar(self.tilgaengelighed_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Tidsperioder og svar muligheder
        tidsperioder = ["1 time", "4 timer", "1 dag", "2 dage", "1 uge"]
        svar_muligheder = [
            "Ingen konsekvens",
            "Mindre konsekvenser",
            "Alvorlige konsekvenser",
            "Kritiske konsekvenser"
        ]

        self.tilgaengelighed_vars = {}

        # Lav en header række med svarmuligheder
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Tom label for tidsperiode kolonnen
        ttk.Label(header_frame, text="", width=20).pack(side=tk.LEFT, padx=5)
        
        # Labels for hver svarmulighed
        for svar in svar_muligheder:
            ttk.Label(header_frame, text=svar, width=20, anchor="center").pack(side=tk.LEFT, padx=5)

        # Tilføj en separator efter header
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=5)

        # Opret rækker for hver tidsperiode
        for periode in tidsperioder:
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=10)
            
            # Tidsperiode label
            ttk.Label(frame, text=periode, width=20).pack(side=tk.LEFT, padx=5)
            
            # Opret variabel til at gemme svaret
            var = tk.StringVar(value="Ingen konsekvens")
            self.tilgaengelighed_vars[periode] = var
            
            # Radio buttons for hver svarmulighed
            for svar in svar_muligheder:
                tk.Radiobutton(
                    frame,
                    text="",
                    value=svar,
                    variable=var,
                    bg="white",
                    selectcolor="lightblue",
                    width=18,
                    anchor="center",
                    command=lambda p=periode: self.on_tilgaengelighed_change(p)
                ).pack(side=tk.LEFT, padx=5)
            
            # Tilføj kommentarfelt
            comment_frame = self.create_comment_section(frame, 'tilgaengelighed', periode)
            comment_frame.pack(side=tk.RIGHT, padx=10)

        # Separator før resultat
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=20)

        # Resultat frame
        result_frame = ttk.LabelFrame(scrollable_frame, text="Samlet tilgængelighedsvurdering")
        result_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Indre frame til resultatet
        inner_result_frame = ttk.Frame(result_frame)
        inner_result_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.tilgaengelighed_result_label = ttk.Label(
            inner_result_frame,
            text="Systemet har normal tilgængelighedsbehov",
            wraplength=800,
            style='Result.TLabel'
        )
        self.tilgaengelighed_result_label.pack(pady=5)

        # Pack canvas og scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y")

        # Gem knap
        save_button = ttk.Button(
            scrollable_frame,
            text="Gem vurdering",
            command=self.save_assessment
        )
        save_button.pack(pady=20)

    def on_tilgaengelighed_change(self, periode):
        self.save_tilgaengelighed_data()
        self.update_tilgaengelighed_result()

    def update_tilgaengelighed_result(self):
        # Point for hver svartype
        point_skala = {
            "Ingen konsekvens": 0,
            "Mindre konsekvenser": 1,
            "Alvorlige konsekvenser": 2,
            "Kritiske konsekvenser": 3
        }
        
        # Beregn total score
        total_score = sum(point_skala[var.get()] for var in self.tilgaengelighed_vars.values())
        
        if total_score <= 3:
            result = "Systemet har normal tilgængelighedsbehov"
        elif total_score <= 8:
            result = "Systemet har forhøjet tilgængelighedsbehov - implementer nødvendige kontroller"
        else:
            result = "Systemet har kritisk tilgængelighedsbehov - strenge tilgængelighedskrav skal implementeres"
            
        self.tilgaengelighed_result_label.config(text=result)

    def save_tilgaengelighed_data(self):
        tilgaengelighed_data = {}
        for periode, var in self.tilgaengelighed_vars.items():
            tilgaengelighed_data[f"periode_{list(self.tilgaengelighed_vars.keys()).index(periode) + 1}"] = {
                "periode": periode,
                "svar": var.get()
            }
        self.tilgaengelighed_svar = tilgaengelighed_data

    def save_current_page_data(self):
        # Gem system information
        self.current_assessment = {
            'system_info': {},
            'kritikalitet': {},
            'gdpr': {},
            'fortrolighed': {},
            'integritet': {},
            'robusthed': {},
            'tilgaengelighed': {}
        }
        
        # Tilføj system beskrivelse hvis den findes
        if hasattr(self, 'system_description'):
            self.current_assessment["system_info"]["system_description"] = self.system_description.get("1.0", tk.END).strip()

    def save_assessment(self):
        try:
            self.gem_vurdering()
        except Exception as e:
            messagebox.showerror("Fejl", f"Der opstod en fejl under gemning af vurdering: {str(e)}")
            print(f"Fejl under gemning af vurdering: {str(e)}")

    def open_assessment(self):
        # Informer brugeren om at funktionen ikke er færdig
        messagebox.showwarning("Under udvikling", "Funktionen 'Åbn vurdering' er endnu ikke færdig. Der arbejdes på at implementere denne funktion.")
        return  # Return immediately after showing the warning
        
    def load_recent_assessments(self):
        # Her skal vi tilføje koden til at indlæse seneste vurderinger
        # Dette er bare eksempel data
        self.recent_listbox.delete(0, tk.END)
        example_assessments = [
            "Risikovurdering - Server infrastruktur (21-01-2025)",
            "Risikovurdering - Netværkssikkerhed (20-01-2025)",
            "Risikovurdering - Cloud services (19-01-2025)"
        ]
        for assessment in example_assessments:
            self.recent_listbox.insert(tk.END, assessment)

    def create_rapport_page(self):
        for widget in self.rapport_frame.winfo_children():
            widget.destroy()
            
        # Overskrift
        header_label = ttk.Label(
            self.rapport_frame,
            text="Samlet Risikovurdering",
            font=("Helvetica", 20, "bold")
        )
        header_label.pack(pady=20)
        
        # Eksporter til PDF knap
        export_button = ttk.Button(
            self.rapport_frame,
            text="Eksportér til PDF",
            command=self.export_to_pdf
        )
        export_button.pack(pady=10)
        
        # Opret en canvas og scrollbar
        canvas = tk.Canvas(self.rapport_frame)
        scrollbar = ttk.Scrollbar(self.rapport_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # System Information sektion
        if hasattr(self, 'system_name'):
            system_frame = ttk.LabelFrame(scrollable_frame, text="System Information")
            system_frame.pack(fill=tk.X, padx=20, pady=10)
            
            system_info_text = f"""
System: {self.system_name.get()}
Ejer: {self.system_owner.get()}
Leverandør: {self.system_supplier.get()}
Ansvarlig: {self.assessment_responsible.get()}
Dato: {self.assessment_date.get()}
"""
            ttk.Label(system_frame, text=system_info_text, justify=tk.LEFT).pack(padx=10, pady=10)
            
        # Fortrolighed sektion
        fort_frame = ttk.LabelFrame(scrollable_frame, text="Fortrolighedsvurdering")
        fort_frame.pack(fill=tk.X, padx=20, pady=10)
        if hasattr(self, 'fortrolighed_result_label') and self.fortrolighed_result_label:
            ttk.Label(fort_frame, text=self.fortrolighed_result_label.cget("text"), justify=tk.LEFT).pack(padx=10, pady=10)
        else:
            ttk.Label(fort_frame, text="Ingen fortrolighedsvurdering udført endnu", justify=tk.LEFT).pack(padx=10, pady=10)
            
        # Integritet sektion
        int_frame = ttk.LabelFrame(scrollable_frame, text="Integritetsvurdering")
        int_frame.pack(fill=tk.X, padx=20, pady=10)
        if hasattr(self, 'integritet_result_label') and self.integritet_result_label:
            ttk.Label(int_frame, text=self.integritet_result_label.cget("text"), justify=tk.LEFT).pack(padx=10, pady=10)
        else:
            ttk.Label(int_frame, text="Ingen integritetsvurdering udført endnu", justify=tk.LEFT).pack(padx=10, pady=10)
            
        # Robusthed sektion
        rob_frame = ttk.LabelFrame(scrollable_frame, text="Robusthedsvurdering")
        rob_frame.pack(fill=tk.X, padx=20, pady=10)
        if hasattr(self, 'robusthed_result_label') and self.robusthed_result_label:
            ttk.Label(rob_frame, text=self.robusthed_result_label.cget("text"), justify=tk.LEFT).pack(padx=10, pady=10)
        else:
            ttk.Label(rob_frame, text="Ingen robusthedsvurdering udført endnu", justify=tk.LEFT).pack(padx=10, pady=10)
            
        # Tilgængelighed sektion
        til_frame = ttk.LabelFrame(scrollable_frame, text="Tilgængelighedsvurdering")
        til_frame.pack(fill=tk.X, padx=20, pady=10)
        if hasattr(self, 'tilgaengelighed_result_label') and self.tilgaengelighed_result_label:
            ttk.Label(til_frame, text=self.tilgaengelighed_result_label.cget("text"), justify=tk.LEFT).pack(padx=10, pady=10)
        else:
            ttk.Label(til_frame, text="Ingen tilgængelighedsvurdering udført endnu", justify=tk.LEFT).pack(padx=10, pady=10)

        # Tilføj forklaringstekst om risici og ledelsens rolle
        risk_explanation_frame = ttk.LabelFrame(scrollable_frame, text="Opsummering af Risici")
        risk_explanation_frame.pack(fill=tk.X, padx=20, pady=10)
        
        risk_explanation_text = """Denne sektion giver en kort opsummering af de identificerede risici og deres betydning for organisationen. Formålet er at sikre, at ledelsen forstår risikobilledet og kan træffe informerede beslutninger om håndteringen.

Ledelsens rolle og beslutningstagning:
• Ledelsen skal tage stilling til hver identificeret risiko og enten acceptere, reducere eller eliminere den.
• Beslutningen bør tage udgangspunkt i risikovurderingens prioritering og organisationens risikotolerance.
• Det skal være tydeligt, hvad hver risiko indebærer, samt hvilke konsekvenser en accept eller afvisning kan have."""

        ttk.Label(
            risk_explanation_frame,
            text=risk_explanation_text,
            justify=tk.LEFT,
            wraplength=800,
            style='Description.TLabel'
        ).pack(padx=10, pady=10)

        # Pack canvas og scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y")

    def generer_handlingsplan(self):
        handlinger = {
            "Dette skal gøres med det samme (Høj prioritet)": [],
            "Dette bør gøres snart (Mellem prioritet)": [],
            "Dette kan gøres på længere sigt (Lav prioritet)": []
        }
        
        # GDPR handlinger
        if hasattr(self, 'gdpr_vars'):
            gdpr_ja = [spørgsmål for spørgsmål, var in self.gdpr_vars.items() if var.get() == "Ja"]
            
            # Hvis der behandles følsomme personoplysninger
            if any(x in gdpr_ja for x in [
                "3. Behandler systemet følsomme eller særligt beskyttelsesværdige personoplysninger?",
                "2. Behandler systemet CPR-numre eller oplysninger om strafbare forhold?"
            ]):
                handlinger["Dette skal gøres med det samme (Høj prioritet)"].append("Beskyt følsomme personoplysninger:")
                handlinger["Dette skal gøres med det samme (Høj prioritet)"].extend([
                    "  • Lav en procedure for hvordan I håndterer henvendelser fra borgere om deres data",
                    "  • Sørg for at følsomme oplysninger er krypteret (sikret mod uautoriseret adgang)",
                    "  • Lav en analyse af konsekvenserne ved behandling af følsomme oplysninger",
                    "  • Dokumentér hvordan I behandler personoplysninger i jeres fortegnelse",
                    "  • Begræns adgangen til følsomme oplysninger til kun de nødvendige medarbejdere",
                    "  • Før log over hvem der tilgår følsomme oplysninger og hvornår",
                    "  • Sørg for at oplysninger bliver slettet automatisk når de ikke længere er nødvendige"
                ])
                
            # Hvis der mangler grundlæggende GDPR-compliance
            if "6. Er der hjemmel til behandlingen?" not in gdpr_ja or \
               "9. Er der udarbejdet en databehandleraftale?" not in gdpr_ja or \
               "10. Er der etableret procedurer for sletning af personoplysninger?" not in gdpr_ja:
                handlinger["Dette bør gøres snart (Mellem prioritet)"].append("Få styr på de grundlæggende GDPR-krav:")
                handlinger["Dette bør gøres snart (Mellem prioritet)"].extend([
                    "  • Find ud af hvilken lovhjemmel I har til at behandle oplysningerne",
                    "  • Lav databehandleraftaler med alle leverandører der behandler data for jer",
                    "  • Lav klare regler for hvornår og hvordan I sletter personoplysninger",
                    "  • Opdatér jeres dokumentation over hvordan I behandler personoplysninger",
                    "  • Sørg for at medarbejderne ved hvordan de skal håndtere personoplysninger",
                    "  • Lav en plan for hvad I gør hvis der sker et sikkerhedsbrud"
                ])

            # Hvis der er særlige risici
            if "5. Bliver der overført data til lande uden for EU/EØS?" in gdpr_ja or \
               "7. Gør systemet brug af automatisk beslutningstagning eller profilering?" in gdpr_ja or \
               "8. Foretager systemet systematisk overvågning?" in gdpr_ja or \
               "12. Skal der udarbejdes en konsekvensanalyse?" in gdpr_ja:
                handlinger["Dette bør gøres snart (Mellem prioritet)"].append("Håndtér særlige GDPR-risici:")
                handlinger["Dette bør gøres snart (Mellem prioritet)"].extend([
                    "  • Dokumentér hvordan I sikrer data der sendes ud af EU",
                    "  • Indfør ekstra sikkerhed omkring automatiske beslutninger",
                    "  • Vurdér om I skal have en databeskyttelsesrådgiver (DPO)",
                    "  • Lav en plan for hvordan I håndterer brud på datasikkerheden",
                    "  • Tænk databeskyttelse ind fra starten når I laver ændringer",
                    "  • Gennemgå jeres databeskyttelse regelmæssigt"
                ])

        # Kritikalitets handlinger
        if hasattr(self, 'kritikalitet_label'):
            if "Kritikalitet A" in self.kritikalitet_label.cget("text"):
                handlinger["Dette skal gøres med det samme (Høj prioritet)"].append("Sikr systemet mod nedbrud:")
                handlinger["Dette skal gøres med det samme (Høj prioritet)"].extend([
                    "  • Sørg for backup-systemer der kan tage over ved nedbrud",
                    "  • Lav automatisk skift til backup-systemer hvis noget går galt",
                    "  • Få lavet sikkerhedstest af systemet regelmæssigt",
                    "  • Sørg for at systemet overvåges døgnet rundt",
                    "  • Lav en plan for hvordan I kommer i gang igen efter et nedbrud"
                ])
            elif "Kritikalitet B" in self.kritikalitet_label.cget("text"):
                handlinger["Dette bør gøres snart (Mellem prioritet)"].append("Beskyt systemet mod problemer:")
                handlinger["Dette bør gøres snart (Mellem prioritet)"].extend([
                    "  • Lav regelmæssig backup af alle vigtige data",
                    "  • Lav en plan for hvordan I håndterer sikkerhedshændelser",
                    "  • Få tjekket systemets sikkerhed mindst én gang om året",
                    "  • Lav regler for hvordan ændringer i systemet skal godkendes"
                ])

        # Robusthed handlinger
        if hasattr(self, 'robusthed_vars'):
            robusthed_ja = [spørgsmål for spørgsmål, var in self.robusthed_vars.items() if var.get() == "Ja"]
            if len(robusthed_ja) >= 3:
                handlinger["Dette bør gøres snart (Mellem prioritet)"].append("Gør systemet mere stabilt:")
                handlinger["Dette bør gøres snart (Mellem prioritet)"].extend([
                    "  • Sørg for at systemet automatisk kan håndtere flere brugere",
                    "  • Fordel belastningen mellem flere servere",
                    "  • Test hvordan systemet klarer sig under høj belastning",
                    "  • Beskyt systemet mod overbelastning",
                    "  • Overvåg systemets ydeevne løbende"
                ])

        # Tilgængelighed handlinger
        if hasattr(self, 'tilgaengelighed_vars'):
            kritiske_perioder = [spørgsmål for spørgsmål, var in self.tilgaengelighed_vars.items() 
                               if var.get() in ["Alvorlige konsekvenser", "Kritiske konsekvenser"]]
            if kritiske_perioder:
                handlinger["Dette bør gøres snart (Mellem prioritet)"].append("Sørg for at systemet er tilgængeligt:")
                handlinger["Dette bør gøres snart (Mellem prioritet)"].extend([
                    "  • Overvåg om systemet er oppe og kører",
                    "  • Få besked automatisk hvis der er problemer",
                    "  • Planlæg hvor mange brugere systemet skal kunne håndtere",
                    "  • Planlæg hvornår I bedst kan lave vedligeholdelse",
                    "  • Skriv ned hvordan I holder systemet kørende"
                ])

        return handlinger

    def beregn_risiko_niveau(self):
        # Beregn sandsynlighed (1-4) baseret på svar
        sandsynlighed = 1
        
        if hasattr(self, 'robusthed_vars'):
            ja_count_robusthed = sum(1 for var in self.robusthed_vars.values() if var.get() == "Ja")
            sandsynlighed += min(ja_count_robusthed, 2)  # Max +2 fra robusthed
            
        if hasattr(self, 'tilgaengelighed_vars'):
            kritiske_perioder = sum(1 for var in self.tilgaengelighed_vars.values() 
                                  if var.get() in ["Alvorlige konsekvenser", "Kritiske konsekvenser"])
            sandsynlighed += min(kritiske_perioder // 2, 1)  # Max +1 fra tilgængelighed
            
        # Beregn konsekvens (1-4) baseret på svar
        konsekvens = 1
        
        if hasattr(self, 'kritikalitet_label'):
            if "Kritikalitet A" in self.kritikalitet_label.cget("text"):
                konsekvens = 4
            elif "Kritikalitet B" in self.kritikalitet_label.cget("text"):
                konsekvens = 3
            elif "Kritikalitet C" in self.kritikalitet_label.cget("text"):
                konsekvens = 2
                
        if hasattr(self, 'gdpr_vars'):
            if self.gdpr_vars["3. Behandler systemet følsomme eller særligt beskyttelsesværdige personoplysninger?"].get() == "Ja":
                konsekvens = max(konsekvens, 3)
                
        if hasattr(self, 'fortrolighed_vars'):
            ja_count_fortrolighed = sum(1 for var in self.fortrolighed_vars.values() if var.get() == "Ja")
            if ja_count_fortrolighed >= 4:
                konsekvens = max(konsekvens, 3)
                
        return sandsynlighed, konsekvens

    def generer_risikomatrix(self, sandsynlighed, konsekvens):
        # Opret en 4x4 matrix som et billede
        width = 800
        height = 800
        cell_size = width // 4
        img = PILImage.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Definer farver
        colors_matrix = [
            [(0,128,0), (0,128,0), (255,255,0), (255,165,0)],  # Første række
            [(0,128,0), (255,255,0), (255,165,0), (255,0,0)],  # Anden række
            [(255,255,0), (255,165,0), (255,0,0), (255,0,0)],  # Tredje række
            [(255,165,0), (255,0,0), (255,0,0), (255,0,0)]     # Fjerde række
        ]
        
        # Tegn celler med farver
        for i in range(4):
            for j in range(4):
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                cell_color = colors_matrix[i][j]
                draw.rectangle([x1, y1, x2, y2], fill=cell_color, outline='black')
                
                # Tilføj tekst
                if i == j == 0:
                    text = "Lav"
                elif i == 0 and j == 1:
                    text = "Lav"
                elif i == 0 and j == 2:
                    text = "Middel"
                elif i == 0 and j == 3:
                    text = "Høj"
                elif i == 1 and j == 0:
                    text = "Lav"
                elif i == 1 and j == 1:
                    text = "Middel"
                elif i == 1 and j == 2:
                    text = "Høj"
                elif i == 1 and j == 3:
                    text = "Kritisk"
                elif i == 2 and j == 0:
                    text = "Middel"
                elif i == 2 and j == 1:
                    text = "Høj"
                elif i == 2 and j == 2:
                    text = "Kritisk"
                elif i == 2 and j == 3:
                    text = "Kritisk"
                elif i == 3 and j == 0:
                    text = "Høj"
                else:
                    text = "Kritisk"
                
                # Brug default font i stedet for at prøve at loade arial
                font = ImageFont.load_default()
                
                # Centrér tekst i cellen
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                x = x1 + (cell_size - text_width) // 2
                y = y1 + (cell_size - text_height) // 2
                draw.text((x, y), text, fill='black', font=font)
        
        # Marker den aktuelle risiko
        current_x = (konsekvens - 1) * cell_size
        current_y = (sandsynlighed - 1) * cell_size
        draw.rectangle([current_x, current_y, current_x + cell_size, current_y + cell_size], 
                      outline='black', width=5)
        
        # Gem billedet midlertidigt
        matrix_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "risikomatrix_temp.png")
        img.save(matrix_path)
        return matrix_path

    def export_to_pdf(self):
        matrix_path = None
        try:
            print("Starter PDF eksport")
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Gem PDF rapport som"
            )
            
            if not filename:
                print("Ingen fil valgt - eksport annulleret")
                return
                
            print(f"Eksporterer til: {filename}")
            
            # Beregn risiko niveau
            try:
                print("Beregner risikoniveau")
                sandsynlighed, konsekvens = self.beregn_risiko_niveau()
                print(f"Risikoniveau beregnet: Sandsynlighed={sandsynlighed}, Konsekvens={konsekvens}")
            except Exception as e:
                print(f"Fejl i risikoberegning: {str(e)}")
                raise Exception(f"Kunne ikke beregne risikoniveau: {str(e)}")
            
            # Generer risikomatrix
            try:
                print("Genererer risikomatrix")
                matrix_path = self.generer_risikomatrix(sandsynlighed, konsekvens)
                print(f"Risikomatrix gemt til: {matrix_path}")
                
                # Verificer at matrix billedet eksisterer og kan åbnes
                if not os.path.exists(matrix_path):
                    raise Exception("Risikomatrix billedet blev ikke genereret korrekt")
                    
                # Test at billedet kan åbnes
                try:
                    with PILImage.open(matrix_path) as img:
                        img.verify()
                except Exception as e:
                    raise Exception(f"Kunne ikke validere risikomatrix billedet: {str(e)}")
                    
            except Exception as e:
                print(f"Fejl ved generering af risikomatrix: {str(e)}")
                raise Exception(f"Kunne ikke generere risikomatrix: {str(e)}")

            # Opret PDF dokument
            try:
                print("Opretter PDF dokument")
                doc = SimpleDocTemplate(
                    filename,
                    pagesize=A4,
                    rightMargin=72,
                    leftMargin=72,
                    topMargin=72,
                    bottomMargin=72
                )
                print("PDF dokument oprettet")
            except Exception as e:
                print(f"Fejl ved oprettelse af PDF dokument: {str(e)}")
                raise Exception(f"Kunne ikke oprette PDF dokument: {str(e)}")

            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            heading_style = styles['Heading2']
            normal_style = styles['Normal']
            
            elements = []
            print("Tilføjer indhold til PDF")

            try:
                # Titel
                elements.append(Paragraph("IT Risikovurdering", title_style))
                elements.append(Spacer(1, 20))

                # System Information
                if hasattr(self, 'system_name'):
                    elements.append(Paragraph("System Information", heading_style))
                    elements.append(Spacer(1, 10))
                    system_info = [
                        ["System:", self.system_name.get()],
                        ["Ejer:", self.system_owner.get()],
                        ["Leverandør:", self.system_supplier.get()],
                        ["Ansvarlig:", self.assessment_responsible.get()],
                        ["Dato:", self.assessment_date.get()]
                    ]
                    t = Table(system_info, colWidths=[100, 400])
                    t.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                        ('PADDING', (0, 0), (-1, -1), 6),
                    ]))
                    elements.append(t)
                    elements.append(Spacer(1, 20))

                # Risikomatrix sektion
                elements.append(Paragraph("Samlet Risikovurdering", heading_style))
                elements.append(Spacer(1, 10))
                
                risk_levels = {
                    (1,1): "Lav", (1,2): "Lav", (1,3): "Middel", (1,4): "Høj",
                    (2,1): "Lav", (2,2): "Middel", (2,3): "Høj", (2,4): "Kritisk",
                    (3,1): "Middel", (3,2): "Høj", (3,3): "Kritisk", (3,4): "Kritisk",
                    (4,1): "Høj", (4,2): "Kritisk", (4,3): "Kritisk", (4,4): "Kritisk"
                }
                current_risk = risk_levels.get((sandsynlighed, konsekvens), "Ukendt")
                
                elements.append(Paragraph(
                    f"Baseret på alle vurderinger er systemets risikoniveau: {current_risk}",
                    normal_style
                ))
                elements.append(Paragraph(
                    f"• Sandsynlighed: {sandsynlighed}/4",
                    normal_style
                ))
                elements.append(Paragraph(
                    f"• Konsekvens: {konsekvens}/4",
                    normal_style
                ))
                elements.append(Spacer(1, 20))
                
                # Risiko-opsummering
                elements.append(Paragraph("Opsummering af Risici", heading_style))
                elements.append(Spacer(1, 10))
                
                risk_explanation_text = """Denne sektion giver en kort opsummering af de identificerede risici og deres betydning for organisationen. Formålet er at sikre, at ledelsen forstår risikobilledet og kan træffe informerede beslutninger om håndteringen.

Ledelsens rolle og beslutningstagning:
• Ledelsen skal tage stilling til hver identificeret risiko og enten acceptere, reducere eller eliminere den.
• Beslutningen bør tage udgangspunkt i risikovurderingens prioritering og organisationens risikotolerance.
• Det skal være tydeligt, hvad hver risiko indebærer, samt hvilke konsekvenser en accept eller afvisning kan have."""

                for line in risk_explanation_text.split('\n'):
                    if line.strip():
                        if line.startswith('•'):
                            # Indrykket bullet point
                            elements.append(Paragraph('    ' + line, normal_style))
                        else:
                            elements.append(Paragraph(line, normal_style))
                        elements.append(Spacer(1, 6))

                elements.append(Spacer(1, 12))

                # Tilføj risikomatrix billede
                if os.path.exists(matrix_path):
                    img = Image(matrix_path)
                    img.drawHeight = 300
                    img.drawWidth = 400
                    elements.append(img)
                    elements.append(Spacer(1, 20))
                else:
                    print("Risikomatrix billede ikke fundet")

                # Handlingsplan
                elements.append(Paragraph("Handlingsplan", heading_style))
                elements.append(Spacer(1, 10))
                
                handlinger = self.generer_handlingsplan()
                for prioritet, actions in handlinger.items():
                    if actions:
                        if "Høj" in prioritet:
                            color = colors.red
                        elif "Mellem" in prioritet:
                            color = colors.orange
                        else:
                            color = colors.green
                            
                        elements.append(Paragraph(
                            f'<font color="{color}">{prioritet}</font>',
                            heading_style
                        ))
                        elements.append(Spacer(1, 10))
                        
                        for action in actions:
                            if action.startswith("  •"):
                                elements.append(Paragraph(f"    {action}", normal_style))
                            else:
                                elements.append(Paragraph(action, normal_style))
                        elements.append(Spacer(1, 15))

                # Tilføj dato og tid
                elements.append(Spacer(1, 30))
                
                # Tilføj opfølgningstekst
                elements.append(PageBreak())
                elements.append(Paragraph("Opfølgning på Risikovurdering", heading_style))
                elements.append(Spacer(1, 10))
                
                followup_text = """⚠ VIGTIGT: Opfølgning og Vedligeholdelse af Risikovurdering

• Når de anførte foranstaltninger med høj prioritet er implementeret, skal der udføres en ny risikovurdering for at vurdere effekten og identificere eventuelle nye risici.

• Risikovurderingen er en løbende proces, der skal gentages mindst én gang om året eller ved væsentlige ændringer i programmet."""

                for line in followup_text.split('\n'):
                    if line.strip():
                        if line.startswith('•'):
                            # Indrykket bullet point
                            elements.append(Paragraph('    ' + line, normal_style))
                        else:
                            elements.append(Paragraph(line, heading_style))
                        elements.append(Spacer(1, 8))
                
                elements.append(Spacer(1, 20))
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                elements.append(Paragraph(f"Rapport genereret: {current_time}", normal_style))

                # Gem PDF
                print("Bygger PDF dokument")
                doc.build(elements)
                print("PDF rapport gemt succesfuldt")
                messagebox.showinfo("Success", "PDF rapport er blevet genereret!")
                
            except Exception as e:
                print(f"Fejl ved generering af PDF indhold: {str(e)}")
                raise Exception(f"Kunne ikke generere PDF indhold: {str(e)}")

        except Exception as e:
            print(f"Fejl under PDF eksport: {str(e)}")
            messagebox.showerror("Fejl", f"Der opstod en fejl under generering af PDF rapport:\n{str(e)}")

        finally:
            # Opryd midlertidige filer
            if matrix_path and os.path.exists(matrix_path):
                try:
                    os.remove(matrix_path)
                    print("Midlertidig matrix fil slettet")
                except Exception as e:
                    print(f"Kunne ikke slette midlertidig matrix fil: {str(e)}")
    
    def gem_vurdering(self):
        try:
            print("Starter gemning af vurdering")
            # Få filnavn fra bruger
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                title="Gem vurdering som"
            )
            
            print(f"Valgt filnavn: {filename}")
            
            if not filename:
                print("Ingen fil valgt - afbryder gemning")
                return
                
            # Initialiser data dictionary med tomme værdier
            data = {
                "system_info": {
                    "navn": "",
                    "ejer": "",
                    "leverandør": "",
                    "ansvarlig": "",
                    "dato": "",
                    "system_description": ""
                },
                "kritikalitet": {},
                "gdpr": {},
                "fortrolighed": {},
                "integritet": {},
                "robusthed": {},
                "tilgaengelighed": {}
            }
            
            # Gem system info
            try:
                print("Gemmer system information")
                if hasattr(self, 'system_name') and self.system_name is not None:
                    data["system_info"]["navn"] = self.system_name.get()
                    print(f"System navn gemt: {data['system_info']['navn']}")
                if hasattr(self, 'system_owner') and self.system_owner is not None:
                    data["system_info"]["ejer"] = self.system_owner.get()
                if hasattr(self, 'system_supplier') and self.system_supplier is not None:
                    data["system_info"]["leverandør"] = self.system_supplier.get()
                if hasattr(self, 'assessment_responsible') and self.assessment_responsible is not None:
                    data["system_info"]["ansvarlig"] = self.assessment_responsible.get()
                if hasattr(self, 'assessment_date') and self.assessment_date is not None:
                    data["system_info"]["dato"] = self.assessment_date.get()
                if hasattr(self, 'system_description'):
                    data["system_info"]["system_description"] = self.system_description.get("1.0", tk.END).strip()

            except Exception as e:
                print(f"Fejl under gemning af system info: {str(e)}")
            
            # Gem vurderinger og kommentarer
            categories = {
                'kritikalitet': (self.kritikalitet_vars, self.kritikalitet_comments),
                'gdpr': (self.gdpr_vars, self.gdpr_comments),
                'fortrolighed': (self.fortrolighed_vars, self.fortrolighed_comments),
                'integritet': (self.integritet_vars, self.integritet_comments),
                'robusthed': (self.robusthed_vars, self.robusthed_comments),
                'tilgaengelighed': (self.tilgaengelighed_vars, self.tilgaengelighed_comments)
            }
            
            for category, (vars_dict, comments_dict) in categories.items():
                print(f"Gemmer {category} data")
                data[category] = {}  # Initialiser tom dictionary for kategorien
                
                for key, var in vars_dict.items():
                    try:
                        if var is not None:
                            value = var.get() if hasattr(var, 'get') else ""
                            comment = ""
                            
                            # Håndter kommentarer korrekt baseret på deres type
                            if key in comments_dict:
                                if isinstance(comments_dict[key], tk.Text):
                                    comment = comments_dict[key].get("1.0", tk.END).strip()
                                elif isinstance(comments_dict[key], str):
                                    comment = str(comments_dict[key])
                            
                            # Gem både svar og kommentar i data dictionary
                            data[category][key] = {
                                "svar": value,
                                "kommentar": comment
                            }
                            print(f"Gemt {category} svar: {value} og kommentar for {key}")
                    except Exception as e:
                        print(f"Fejl under gemning af {category} variabel {key}: {str(e)}")
                        data[category][key] = {"svar": "", "kommentar": ""}
            
            # Log data før gemning
            print("Data der skal gemmes:")
            print(str(data))
            
            # Gem til fil
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            print(f"Vurdering gemt succesfuldt til {filename}")
            messagebox.showinfo("Success", "Vurderingen er blevet gemt!")
            
        except Exception as e:
            print(f"Fejl under gemning af vurdering: {str(e)}")
            messagebox.showerror("Fejl", f"Der opstod en fejl under gemning af vurderingen:\n{str(e)}")

    def aabn_vurdering(self):
        try:
            # Få filnavn fra bruger
            filename = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                title="Åbn vurdering"
            )
            
            if not filename:
                return
                
            print(f"Åbner fil: {filename}")
            
            # Læs data fra fil
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Indlæs system info
            if "system_info" in data:
                if hasattr(self, 'system_name'):
                    self.system_name.set(data["system_info"].get("navn", ""))
                if hasattr(self, 'system_owner'):
                    self.system_owner.set(data["system_info"].get("ejer", ""))
                if hasattr(self, 'system_supplier'):
                    self.system_supplier.set(data["system_info"].get("leverandør", ""))
                if hasattr(self, 'assessment_responsible'):
                    self.assessment_responsible.set(data["system_info"].get("ansvarlig", ""))
                if hasattr(self, 'assessment_date'):
                    self.assessment_date.set(data["system_info"].get("dato", ""))
                if hasattr(self, 'system_description'):
                    self.system_description.delete("1.0", tk.END)
                    self.system_description.insert("1.0", data["system_info"].get("system_description", ""))
            
            # Indlæs vurderinger
            categories = {
                'kritikalitet': self.kritikalitet_vars,
                'gdpr': self.gdpr_vars,
                'fortrolighed': self.fortrolighed_vars,
                'integritet': self.integritet_vars,
                'robusthed': self.robusthed_vars,
                'tilgaengelighed': self.tilgaengelighed_vars
            }
            
            for category, vars_dict in categories.items():
                if category in data:
                    print(f"Indlæser {category} data")
                    for key, value_data in data[category].items():
                        try:
                            # Håndter både nyt og gammelt format
                            if isinstance(value_data, dict):
                                if key in vars_dict:
                                    vars_dict[key].set(value_data.get("svar", ""))
                                # Indlæs kommentar hvis den findes
                                comment_dict_name = f'{category}_comments'
                                if "kommentar" in value_data and hasattr(self, comment_dict_name):
                                    comment_dict = getattr(self, comment_dict_name)
                                    if isinstance(comment_dict, dict) and key in comment_dict:
                                        if isinstance(comment_dict[key], tk.Text):
                                            comment_dict[key].delete("1.0", tk.END)
                                            comment_dict[key].insert("1.0", value_data["kommentar"])
                            else:
                                # Gammelt format hvor value_data er selve svaret
                                if key in vars_dict:
                                    vars_dict[key].set(value_data)
                        except Exception as e:
                            print(f"Fejl under indlæsning af {category} svar {key}: {str(e)}")
                            continue

            # Opdater resultater
            if hasattr(self, 'update_kritikalitet'):
                self.update_kritikalitet()
            if hasattr(self, 'update_fortrolighed_result'):
                self.update_fortrolighed_result()
            if hasattr(self, 'update_integritet_result'):
                self.update_integritet_result()
            if hasattr(self, 'update_robusthed_result'):
                self.update_robusthed_result()
            if hasattr(self, 'update_tilgaengelighed_result'):
                self.update_tilgaengelighed_result()

            messagebox.showinfo("Success", "Vurdering er blevet indlæst!")
                
        except Exception as e:
            print(f"Fejl under åbning af vurdering: {str(e)}")
            messagebox.showerror("Fejl", f"Der opstod en fejl under åbning af vurderingen:\n{str(e)}")

    def load_recent_assessments(self):
        # Her skal vi tilføje koden til at indlæse seneste vurderinger
        # Dette er bare eksempel data
        self.recent_listbox.delete(0, tk.END)
        example_assessments = [
            "Risikovurdering - Server infrastruktur (21-01-2025)",
            "Risikovurdering - Netværkssikkerhed (20-01-2025)",
            "Risikovurdering - Cloud services (19-01-2025)"
        ]
        for assessment in example_assessments:
            self.recent_listbox.insert(tk.END, assessment)

    def create_comment_section(self, parent, category, question_key):
        """Opret et kommentarikon der åbner en popup med kommentarfelt"""
        comment_frame = ttk.Frame(parent)
        
        # Opret et ikon der indikerer kommentarmulighed (📝)
        comment_icon = ttk.Label(comment_frame, text="💭", cursor="hand2")
        comment_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        # Gem reference til kommentaren i det relevante dictionary hvis den ikke findes
        comments_dict = getattr(self, f"{category}_comments")
        if question_key not in comments_dict:
            comments_dict[question_key] = tk.StringVar()
        
        # Bind klik-event til ikonet
        comment_icon.bind('<Button-1>', lambda e: self.show_comment_dialog(category, question_key))
        
        return comment_frame
        
    def show_comment_dialog(self, category, question_key):
        """Viser popup-dialog med kommentarfelt"""
        # Opret top-level vindue
        dialog = tk.Toplevel(self.master)
        dialog.title("Tilføj kommentar")
        dialog.geometry("500x300")
        
        # Gør vinduet modalt (kan ikke interagere med hovedvinduet)
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Hovedramme med padding
        main_frame = ttk.Frame(dialog, padding="20 20 20 70")  # Extra padding i bunden til knapper
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Vis spørgsmålet
        question_label = ttk.Label(
            main_frame,
            text="Kommentar til spørgsmål:",
            wraplength=460
        )
        question_label.pack(pady=(0, 10))
        
        # Vis det aktuelle spørgsmål
        current_question = ttk.Label(
            main_frame,
            text=question_key,
            wraplength=460,
            style='Subheader.TLabel'
        )
        current_question.pack(pady=(0, 20))
        
        # Opret tekstfelt til kommentar
        comment_frame = ttk.Frame(main_frame)
        comment_frame.pack(fill=tk.BOTH, expand=True)
        
        comment_text = tk.Text(comment_frame, wrap=tk.WORD, width=50, height=8)
        comment_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tilføj scrollbar
        scrollbar = ttk.Scrollbar(comment_frame, orient="vertical", command=comment_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        comment_text.configure(yscrollcommand=scrollbar.set)
        
        # Indsæt eksisterende kommentar hvis den findes
        comments_dict = getattr(self, f'{category}_comments')
        existing_comment = comments_dict[question_key].get()
        if existing_comment:
            comment_text.insert("1.0", existing_comment)
        
        # Opret en fast ramme i bunden til knapperne
        button_container = ttk.Frame(dialog)
        button_container.pack(side=tk.BOTTOM, fill=tk.X)
        button_container.place(relx=0, rely=1.0, relwidth=1.0, height=60, anchor='sw')
        
        # Tilføj en tynd linje over knapperne
        separator = ttk.Separator(button_container, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 10))
        
        # Knapper
        button_frame = ttk.Frame(button_container)
        button_frame.pack(padx=20, anchor='e')
        
        def save_comment():
            comments_dict[question_key].set(comment_text.get("1.0", tk.END).strip())
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # Placer knapperne i højre side
        cancel_btn = ttk.Button(button_frame, text="Annuller", command=cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        save_btn = ttk.Button(button_frame, text="Gem", command=save_comment)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Centrér vinduet på skærmen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Sæt fokus på tekstfeltet
        comment_text.focus_set()
        
    def generer_risiko_opsummering(self):
        """Genererer en opsummering af de identificerede risici og deres alvorlighed."""
        opsummering = {
            "Kritiske risici (Kræver ledelsens accept)": [],
            "Væsentlige risici (Skal håndteres)": [],
            "Moderate risici (Bør vurderes)": []
        }
        
        # Beregn den samlede risikovurdering
        sandsynlighed, konsekvens = self.beregn_risiko_niveau()
        
        # GDPR risici
        if hasattr(self, 'gdpr_vars'):
            gdpr_ja = [spørgsmål for spørgsmål, var in self.gdpr_vars.items() if var.get() == "Ja"]
            
            # Følsomme personoplysninger
            if any(x in gdpr_ja for x in [
                "3. Behandler systemet følsomme eller særligt beskyttelsesværdige personoplysninger?",
                "2. Behandler systemet CPR-numre eller oplysninger om strafbare forhold?"
            ]):
                risiko = "Behandling af følsomme personoplysninger:\n" + \
                        "• Brud kan medføre alvorlige konsekvenser for personer\n" + \
                        "• Risiko for store bøder ved manglende beskyttelse\n" + \
                        "• Kræver særlige sikkerhedsforanstaltninger"
                opsummering["Kritiske risici (Kræver ledelsens accept)"].append(risiko)
            
            # Overførsel til tredjelande
            if "5. Bliver der overført data til lande uden for EU/EØS?" in gdpr_ja:
                risiko = "Overførsel af data til lande uden for EU:\n" + \
                        "• Risiko for utilstrækkelig databeskyttelse\n" + \
                        "• Kræver særligt overførselsgrundlag\n" + \
                        "• Skal dokumenteres i fortegnelsen"
                opsummering["Væsentlige risici (Skal håndteres)"].append(risiko)
            
            # Manglende compliance
            compliance_mangler = []
            if "6. Er der hjemmel til behandlingen?" not in gdpr_ja:
                compliance_mangler.append("• Mangler lovgrundlag for behandling")
            if "9. Er der udarbejdet en databehandleraftale?" not in gdpr_ja:
                compliance_mangler.append("• Mangler databehandleraftaler")
            if "10. Er der etableret procedurer for sletning af personoplysninger?" not in gdpr_ja:
                compliance_mangler.append("• Mangler sletterutiner")
                
            if compliance_mangler:
                risiko = "Mangler i GDPR-compliance:\n" + "\n".join(compliance_mangler)
                opsummering["Væsentlige risici (Skal håndteres)"].append(risiko)

        # Kritikalitets risici
        if hasattr(self, 'kritikalitet_label'):
            try:
                if "Kritikalitet A" in self.kritikalitet_label.cget("text"):
                    risiko = "Kritisk system for forretningen:\n" + \
                            "• Nedetid har store konsekvenser\n" + \
                            "• Kræver omfattende beredskab\n" + \
                            "• Høje krav til oppetid"
                    opsummering["Kritiske risici (Kræver ledelsens accept)"].append(risiko)
            except:
                pass
                
        # Tilgængeligheds risici
        if hasattr(self, 'tilgaengelighed_vars'):
            kritiske_perioder = [spørgsmål for spørgsmål, var in self.tilgaengelighed_vars.items() 
                               if var.get() in ["Alvorlige konsekvenser", "Kritiske konsekvenser"]]
            if kritiske_perioder:
                risiko = "Kritiske perioder for tilgængelighed:\n" + \
                        "• Systemet har perioder uden tolerance for nedetid\n" + \
                        "• Påvirker forretningens drift direkte\n" + \
                        "• Kræver backup og overvågning"
                opsummering["Væsentlige risici (Skal håndteres)"].append(risiko)

        # Robusthed risici
        if hasattr(self, 'robusthed_vars'):
            robusthed_ja = []
            for spørgsmål, var in self.robusthed_vars.items():
                try:
                    if var.get() == "Ja":
                        robusthed_ja.append(spørgsmål)
                except:
                    continue
                    
            if len(robusthed_ja) >= 3:
                risiko = "Problemer med systemets stabilitet:\n" + \
                        "• Tidligere hændelser eller nedbrud\n" + \
                        "• Test hvordan systemet klarer sig under høj belastning\n" + \
                        "• Beskyt systemet mod overbelastning\n" + \
                        "• Overvåg systemets ydeevne løbende"
                opsummering["Moderate risici (Bør vurderes)"].append(risiko)

        # Tilgængelighed handlinger
        if hasattr(self, 'tilgaengelighed_vars'):
            kritiske_perioder = [spørgsmål for spørgsmål, var in self.tilgaengelighed_vars.items() 
                               if var.get() in ["Alvorlige konsekvenser", "Kritiske konsekvenser"]]
            if kritiske_perioder:
                risiko = "Sørg for at systemet er tilgængeligt:\n" + \
                        "• Overvåg om systemet er oppe og kører\n" + \
                        "• Få besked automatisk hvis der er problemer\n" + \
                        "• Planlæg hvor mange brugere systemet skal kunne håndtere\n" + \
                        "• Planlæg hvornår I bedst kan lave vedligeholdelse\n" + \
                        "• Skriv ned hvordan I holder systemet kørende"
                opsummering["Væsentlige risici (Skal håndteres)"].append(risiko)

        # Risiko-opsummering
        if hasattr(self, 'kritikalitet_label'):
            try:
                if "Kritikalitet A" in self.kritikalitet_label.cget("text"):
                    risiko = "Kritisk system for forretningen:\n" + \
                            "• Nedetid har store konsekvenser\n" + \
                            "• Kræver omfattende beredskab\n" + \
                            "• Høje krav til oppetid"
                    opsummering["Kritiske risici (Kræver ledelsens accept)"].append(risiko)
            except:
                pass

        # Tilføj risikoniveau fra matrixen
        if sandsynlighed >= 3 and konsekvens >= 3:
            matrix_risiko = f"Høj samlet risiko (Sandsynlighed: {sandsynlighed}, Konsekvens: {konsekvens}):\n" + \
                          "• Kræver omgående handling\n" + \
                          "• Skal vurderes af ledelsen\n" + \
                          "• Risiko for store tab eller omkostninger"
            opsummering["Kritiske risici (Kræver ledelsens accept)"].append(matrix_risiko)
        elif sandsynlighed >= 2 and konsekvens >= 2:
            matrix_risiko = f"Medium samlet risiko (Sandsynlighed: {sandsynlighed}, Konsekvens: {konsekvens}):\n" + \
                          "• Kræver handling inden for rimelig tid\n" + \
                          "• Del af løbende forbedringer\n" + \
                          "• Bør vurderes af ledelsen"
            opsummering["Væsentlige risici (Skal håndteres)"].append(matrix_risiko)
            
        return opsummering

    def get_risk_explanation(self, risk_level):
        """Returnerer forklaringen for et givet risikoniveau"""
        if risk_level == "Højt":
            return "Uacceptabel risiko. Der bør omgående træffes foranstaltninger til at nedsætte risikoen på kort sigt. Ellers bør hele eller en del af aktiviteten afslås."
        elif risk_level == "Moderat":
            return "Acceptabel under kontrol.\nDer bør foretages en risikoledelsesmæssig opfølgning, og der bør etableres handlinger inden for rammerne af løbende forbedring på mellemlang og lang sigt."
        else:
            return "Acceptabel som den er. Risikoen kan accepteres uden yderligere handling."

    def show_about(self):
        """Viser information om programmet"""
        about_text = f"""IT Risikovurdering v{self.VERSION}

Udviklet af: {self.DEVELOPER}

Support:
E-mail: {self.SUPPORT_EMAIL}
Telefon: {self.SUPPORT_PHONE}

Dette program er udviklet til at hjælpe med at udføre IT-risikovurderinger på en struktureret og effektiv måde.
"""
        messagebox.showinfo("Om programmet", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ITRisikovurderingsApp(root)
    root.mainloop()