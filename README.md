# Password Manager Tool

Questo repository contiene un semplice **gestore di password** sviluppato in Python. Lo strumento offre probabilmente funzionalità di base per archiviare, generare e recuperare in modo sicuro le credenziali di accesso.

## 📁 Struttura del Progetto

Il progetto è composto da due file Python principali e una directory di configurazione dell'IDE:

*   **`main.py`**: Script principale per l'esecuzione del programma. Contiene l'interfaccia utente (a riga di comando o grafica) e la logica di interazione con l'utente.
*   **`library.py`**: Modulo di libreria che gestisce le operazioni core del password manager, come la crittografia, il salvataggio su file/database, la generazione di password sicure e la ricerca di credenziali.
*   **`.idea/`**: Directory con le impostazioni specifiche dell'IDE **IntelliJ IDEA** (irrilevante per l'esecuzione del programma).

## 🚀 Come Iniziare

### Prerequisiti
*   **Python 3** installato sul sistema.
*   Conoscenza di base dell'uso del terminale.

### Installazione ed Esecuzione

1.  **Clona il repository**:
    ```bash
    git clone https://github.com/msabetta/PasswordManager.git
    cd PasswordManager
    ```

2.  **Esegui il programma**:
    ```bash
    python main.py
    ```
    *(Su alcuni sistemi potrebbe essere necessario usare `python3 main.py`)*

## 🛠️ Funzionalità Presunte (da verificare nel codice)

*   **Generazione Password Sicure**: Crea password complesse e casuali.
*   **Archiviazione Criptata**: Salva le credenziali in modo sicuro, probabilmente con crittografia.
*   **Recupero Credenziali**: Cerca e restituisce le password salvate per un dato servizio/account.
*   **Master Password**: Protegge l'accesso al vault delle password con un'unica password principale.

## 📦 Dipendenze

Le librerie Python necessarie potrebbero non essere elencate in un file `requirements.txt`. Per installarle, dopo aver esaminato il codice, puoi installarle manualmente con pip. Esempi di possibili librerie includono `cryptography`, `pycryptodome` o `passlib`.

```bash
# Esempio (da adattare in base al codice)
pip install cryptography
```

## ⚠️ Nota sulla Sicurezza
Questo progetto sembra pensato per **scopo didattico o dimostrativo**. Prima di usarlo per password reali, assicurati di:
*   Aver compreso appieno il meccanismo di crittografia utilizzato.
*   Aver verificato che non ci siano vulnerabilità note.
*   Effettuare backup regolari del file contenente le password criptate.
