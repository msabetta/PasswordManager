class Menu:
    # =====================================================
    # MENU
    # =====================================================
    @classmethod
    def menu(cls):
        print("\n==== PASSWORD MANAGER ====")
        print("1) Aggiungi password")
        print("2) Visualizza password")
        print("3) Importa CSV")
        print("4) Esci")
        return input("Scelta: ")
