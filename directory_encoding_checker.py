import os


def check_encoding(directory, encoding='utf-8'):
    """
    Prochází všechny .txt soubory ve zvoleném adresáři a kontroluje
    jejich kódování. Při chybě vypíše název problematického souboru.

    :param directory: Cesta k adresáři se soubory.
    :param encoding: Kódování, které chceme prověřit (výchozí 'utf-8').
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding=encoding) as f:
                        # Pokus o načtení obsahu celého souboru
                        f.read()
                        print(f"zpracovávám {file_path}")
                except UnicodeDecodeError as e:
                    print(f"Chyba kódování v souboru: {file_path}")
                    print(f"Detaily chyby: {e}")


# Nastav cestu k adresáři, který chceš kontrolovat
directory_to_check = "./Export/AZcup25-v1"
check_encoding(directory_to_check)