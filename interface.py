import customtkinter as ctk
from tkinter import filedialog, messagebox

# Configuration globale pour un design moderne
ctk.set_appearance_mode("dark")  # Thème sombre
ctk.set_default_color_theme("blue")  # Palette de couleurs modernes

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Générateur de RAT - Interface Professionnelle")
        self.geometry("550x500")  # Taille augmentée pour plus d'espace visuel
        self.resizable(False, False)  # Empêche le redimensionnement pour préserver le design
        self.user_choices = {"options": [], "file_to_inject": None, "extension": ".exe", "output_path": None}

        # Configuration principale pour que tout le contenu s'étende
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Conteneur principal
        self.container = ctk.CTkFrame(self, corner_radius=10)
        self.container.grid(row=0, column=0)

        # Initialisation des pages
        self.pages = {}
        for Page in (IntroductionPage, OptionsPage, FileSelectionPage, OutputPage):
            page_name = Page.__name__
            page = Page(parent=self.container, controller=self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("IntroductionPage")

    def show_page(self, page_name):
        """Afficher une page spécifique."""
        page = self.pages[page_name]
        page.tkraise()


class CenteredFrame(ctk.CTkFrame):
    """Cadre professionnel avec un design soigné."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.inner_frame = ctk.CTkFrame(self, corner_radius=15)
        self.inner_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


class IntroductionPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Bienvenue dans le Générateur de RAT",
                     font=("Arial", 28, "bold"), text_color="lightblue").pack(pady=20)

        ctk.CTkLabel(self.inner_frame, text="Créez un RAT personnalisé avec des fonctionnalités avancées\n"
                                            "et injectez-le dans un fichier cible.",
                     font=("Arial", 18), justify="center").pack(pady=20)

        ctk.CTkButton(self.inner_frame, text="Commencer",
                      font=("Arial", 18), corner_radius=10,
                      command=lambda: controller.show_page("OptionsPage")).pack(pady=30)


class OptionsPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Options du RAT",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

        # Description et liste d'options avec des cases à cocher
        self.options = {
            "Keylogger": "Enregistre toutes les frappes du clavier.",
            "Ouvrir la webcam": "Active la webcam pour espionner.",
            "Capture d'écran": "Prend des captures d'écran à intervalles réguliers.",
            "Escalade de privilèges": "Obtient des droits administratifs.",
            "Vol des mots de passe": "Récupère les mots de passe enregistrés.",
            "Surveillance du microphone": "Écoute via le microphone.",
            "Récupération des fichiers": "Télécharge les fichiers spécifiques depuis la cible."
        }

        self.selected_options = {}
        for option, description in self.options.items():
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(self.inner_frame, text=option, variable=var,
                                       font=("Arial", 14), text_color="white",
                                       command=lambda o=option, d=description: self.show_description(o, d))
            checkbox.pack(anchor="w", pady=5)
            self.selected_options[option] = var

        self.description_label = ctk.CTkLabel(self.inner_frame, text="Sélectionnez une option pour voir sa description.",
                                              font=("Arial", 14), text_color="gray")
        self.description_label.pack(pady=15)

        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Précédent", font=("Arial", 16),
                      command=lambda: controller.show_page("IntroductionPage")).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=self.save_and_next).pack(side="right", padx=10)

    def show_description(self, option, description):
        """Affiche la description de l'option sélectionnée."""
        self.description_label.configure(text=f"{option} : {description}")

    def save_and_next(self):
        selected = [option for option, var in self.selected_options.items() if var.get()]
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner au moins une option.")
            return
        self.controller.user_choices["options"] = selected
        self.controller.show_page("FileSelectionPage")


class FileSelectionPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Sélectionner un fichier pour l'injection",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

        self.file_label = ctk.CTkLabel(self.inner_frame, text="Aucun fichier sélectionné",
                                       font=("Arial", 16), text_color="gray")
        self.file_label.pack(pady=10)

        # Menu déroulant et bouton pour sélectionner un fichier
        ctk.CTkLabel(self.inner_frame, text="Choisir l'extension :", font=("Arial", 14)).pack(pady=10)
        self.extension_menu = ctk.CTkOptionMenu(self.inner_frame, values=[".exe", ".pdf", ".txt", ".docx"],
                                                command=self.select_extension)
        self.extension_menu.pack(pady=10)

        ctk.CTkButton(self.inner_frame, text="Choisir un fichier", font=("Arial", 16),
                      command=self.choose_file).pack(pady=10)

        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Précédent", font=("Arial", 16),
                      command=lambda: controller.show_page("OptionsPage")).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Suivant", font=("Arial", 16),
                      command=self.next_page).pack(side="right", padx=10)

    def select_extension(self, extension):
        """Met à jour l'extension choisie."""
        self.controller.user_choices["extension"] = extension

    def choose_file(self):
        file_path = filedialog.askopenfilename(title="Choisir un fichier")
        if file_path:
            self.controller.user_choices["file_to_inject"] = file_path
            self.file_label.configure(text=f"Fichier sélectionné : {file_path}", text_color="white")

    def next_page(self):
        if not self.controller.user_choices["file_to_inject"]:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un fichier avant de continuer.")
            return
        self.controller.show_page("OutputPage")


class OutputPage(CenteredFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self.inner_frame, text="Emplacement de stockage",
                     font=("Arial", 24, "bold"), text_color="lightblue").pack(pady=20)

        self.output_label = ctk.CTkLabel(self.inner_frame, text="Aucun emplacement sélectionné",
                                         font=("Arial", 16), text_color="gray")
        self.output_label.pack(pady=10)

        ctk.CTkButton(self.inner_frame, text="Choisir un emplacement", font=("Arial", 16),
                      command=self.choose_output).pack(pady=10)

        # Boutons de navigation
        button_frame = ctk.CTkFrame(self.inner_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(button_frame, text="Précédent", font=("Arial", 16),
                      command=lambda: controller.show_page("FileSelectionPage")).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Générer", font=("Arial", 16),
                      command=self.generate_rat).pack(side="right", padx=10)

    def choose_output(self):
        output_path = filedialog.askdirectory(title="Choisir un emplacement de stockage")
        if output_path:
            self.controller.user_choices["output_path"] = output_path
            self.output_label.configure(text=f"Emplacement sélectionné : {output_path}", text_color="white")

    def generate_rat(self):
        if not self.controller.user_choices["output_path"]:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un emplacement de stockage.")
            return

        options = ", ".join(self.controller.user_choices["options"])
        file_to_inject = self.controller.user_choices["file_to_inject"]
        extension = self.controller.user_choices["extension"]
        output_path = self.controller.user_choices["output_path"]

        messagebox.showinfo(
            "Succès",
            f"RAT généré avec succès !\n\nOptions : {options}\nExtension : {extension}\n"
            f"Fichier injecté : {file_to_inject}\nStocké dans : {output_path}"
        )


if __name__ == "__main__":
    app = Application()
    app.mainloop()
