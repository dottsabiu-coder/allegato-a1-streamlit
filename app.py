import streamlit as st
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

# ── CONFIG ──
st.set_page_config(
    page_title="Allegato A1 – Regione Siciliana",
    page_icon="🦷",
    layout="centered"
)

W, H = A4
BLU_NAVY  = colors.HexColor('#192850')
BLU_CIELO = colors.HexColor('#C0D2DF')
ORO       = colors.HexColor('#8B6740')
GRIGIO_L  = colors.HexColor('#666666')

DOCS = [
    (1,  "Documento che definisce ed esplicita l'organizzazione e le politiche di gestione delle risorse", "1A.01.03.01"),
    (2,  "Documentazione inerente il sistema informativo", "1A.01.04.01"),
    (3,  "Documento/programma che descrive le modalita per la valutazione e il miglioramento della qualita delle prestazioni e dei servizi erogati", "1A.01.05.01"),
    (4,  "Procedura per la presentazione e gestione di reclami, osservazioni e suggerimenti.", "1A.01.06.01"),
    (5,  "Documento/procedura che descrive le modalita di erogazione dell'assistenza", "1A.02.02.01"),
    (6,  "Piano per la gestione delle emergenze", "1A.02.02.02"),
    (7,  "Protocollo per l'isolamento di pazienti con patologie contagiose o potenzialmente tali", "1A.02.02.03"),
    (8,  "Procedura che definisce i requisiti per la redazione, l'aggiornamento, la conservazione e la verifica della documentazione sanitaria nonche le modalita di controllo.", "1A.02.05.01"),
    (9,  "Documento formale di incarico del responsabile della Manutenzione", "1A.03.01.01"),
    (10, "Inventario delle attrezzature aggiornato e verificato annualmente e procedura per l'identificazione delle attrezzature", "1A.03.02.01"),
    (11, "Piano per la gestione e la manutenzione (ordinaria e straordinaria) delle strutture, impianti, attrezzature e apparecchiature biomediche.", "1A.03.02.02"),
    (12, "Documentazione tecnica relativa alle singole attrezzature e apparecchiature immediatamente disponibile agli operatori interessati e alla funzione preposta alla manutenzione", "1A.03.02.03"),
    (13, "Documentazione tecnica - caratteristiche ambientali e accessibilita", "1A.03.05.01"),
    (14, "Documentazione tecnica - protezione antincendio", "1A.03.05.02"),
    (15, "Documentazione tecnica - protezione acustica", "1A.03.05.03"),
    (16, "Documentazione tecnica - sicurezza elettrica e continuita elettrica", "1A.03.05.04"),
    (17, "Documentazione tecnica - sicurezza anti-infortunistica", "1A.03.05.05"),
    (18, "Documentazione tecnica - protezione da radiazioni ionizzanti", "1A.03.05.06"),
    (19, "Documentazione tecnica - eliminazione barriere architettoniche", "1A.03.05.07"),
    (20, "Documentazione tecnica - smaltimento dei rifiuti", "1A.03.05.08"),
    (21, "Documentazione tecnica - condizioni microclimatiche", "1A.03.05.09"),
    (22, "Documentazione tecnica - impianti di distribuzione dei gas", "1A.03.05.10"),
    (23, "Documentazione tecnica - materiali esplodenti", "1A.03.05.11"),
    (24, "Documentazione tecnica - protezione antisismica", "1A.03.05.12"),
    (25, "Obblighi assicurativi definiti dalla normativa applicabile", "1A.04.12.04"),
    (26, "Carta dei servizi", "1A.05.03.01"),
    (27, "Modalita identificazione di tirocinanti, specializzandi e altri soggetti che intervengono nel percorso assistenziale.", "1A.05.03.03"),
    (28, "Report criticita riscontrate dall'analisi dei reclami e dei risultati delle indagini di customer satisfaction e relativi Piani di intervento", "1A.05.03.05"),
    (29, "Piano aziendale per la gestione del rischio", "1A.06.02.01"),
    (30, "Procedura per la pulizia e sanificazione degli ambienti", "1A.06.02.02"),
    (31, "Procedura per la protezione dagli incidenti per esposizione a materiale biologico o altre sostanze pericolose", "1A.06.02.03"),
    (32, "Sistema (Piani di intervento/report) per l'identificazione e la segnalazione di near miss, eventi avversi ed eventi sentinella", "1A.06.02.04"),
]


def _build_inventario(s, nome, tit, dir_, resp_mnt, anno, oggi):
    """Genera dinamicamente il documento 10 in base ai dati della struttura."""
    righe = []
    idx_ru = 1
    for i in range(s.get('n_riuniti', 1)):
        sala = f"Sala {i+1}"
        righe.append(f"RU-{idx_ru:02d} | Riunito odontoiatrico n.{i+1:<3} | {sala:<16} | Funzionante")
        idx_ru += 1

    for i in range(s.get('n_sale_med', 0)):
        righe.append(f"SM-{i+1:02d} | Sala medica / visita n.{i+1:<5} | Sala Med.{i+1:<7} | Funzionante")

    if s.get('ha_opt'):
        for i in range(s.get('n_sale_rx', 1)):
            righe.append(f"RX-{i+1:02d} | Ortopantomografo (OPT)        | Sala RX {i+1:<8} | Funzionante")

    if s.get('ha_cbct'):
        righe.append("CB-01 | CBCT / Radiologia 3D         | Sala RX         | Funzionante")

    righe.append("ST-01 | Autoclave Classe B            | Sterilizzazione | Funzionante")
    righe.append("CP-01 | Compressore odontoiatrico     | Locale tecnico  | Funzionante")

    if s.get('ha_scanner'):
        righe.append("SC-01 | Scanner intraorale            | Sala 1          | Funzionante")
    if s.get('ha_stampante3d'):
        righe.append("3D-01 | Stampante 3D                  | Lab. digitale   | Funzionante")
    if s.get('ha_cad'):
        righe.append("CAD-01| CAD/CAM / Fresatrice          | Lab. digitale   | Funzionante")

    inventario = "\n".join(righe)

    locali = []
    if s.get('n_riuniti', 0):    locali.append(f"{s['n_riuniti']} sala/e operativa/e con riunito")
    if s.get('n_sale_med', 0):   locali.append(f"{s['n_sale_med']} sala/e medica/e")
    if s.get('n_sale_rx', 0):    locali.append(f"{s['n_sale_rx']} sala/e radiologica/e")
    if s.get('n_sterile', 0):    locali.append(f"{s['n_sterile']} locale/i sterilizzazione")
    if s.get('n_attesa', 0):     locali.append(f"{s['n_attesa']} sala/e attesa")
    if s.get('n_bagni', 0):      locali.append(f"{s['n_bagni']} servizi igienici")
    composizione = ", ".join(locali) if locali else "da specificare"

    return f"""INVENTARIO ATTREZZATURE E PROCEDURA DI IDENTIFICAZIONE
Cod. Requisito 1A.03.02.01 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

COMPOSIZIONE DELLA STRUTTURA
{composizione}

PROCEDURA DI IDENTIFICAZIONE
Ogni attrezzatura e identificata con codice univoco su etichetta apposta sull'apparecchiatura.
Il registro e aggiornato annualmente e ogni volta che si aggiunge, dismette o sostituisce un'attrezzatura.

INVENTARIO ATTREZZATURE BIOMEDICHE
{inventario}

VERIFICA ANNUALE
Data ultima verifica: {oggi}    Responsabile Manutenzione: {resp_mnt}
Firma: ______________________

COLLAUDO NUOVE ACQUISIZIONI
Ad ogni nuova acquisizione: collaudo tecnico di sicurezza.
Verbale conservato nella documentazione tecnica della singola apparecchiatura."""


def get_testo(num, s):
    nome      = s['denominazione'].title()
    tit       = s['titolare'].title()
    dir_      = s.get('direttore', '').strip() or tit
    resp_mnt  = s.get('resp_manut', '').strip() or tit
    adr       = f"{s['indirizzo'].title()}, {s['comune'].title()} ({s['provincia'].upper()})"
    albo      = s.get('albo', '').strip()
    cf        = s.get('cf', '').strip()
    telefono  = s.get('telefono', '').strip()
    pec       = s.get('pec', '').strip()
    asp       = s.get('asp', '').strip()
    anno      = s['anno']
    oggi      = date.today().strftime('%d/%m/%Y')

    albo_str = f"Albo: {albo}" if albo else ""
    cf_str   = f"CF/PIVA: {cf}" if cf else ""
    tel_str  = f"Tel: {telefono}" if telefono else ""
    pec_str  = f"PEC: {pec}" if pec else ""
    asp_str  = f"ASP: {asp}" if asp else ""
    contatti = " | ".join(filter(None, [albo_str, cf_str, tel_str, pec_str]))

    intestazione = f"""Studio: {nome}
Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}
Sede: {adr} | {asp_str}
{contatti}
"""

    testi = {

        1: f"""DOCUMENTO DI ORGANIZZAZIONE E POLITICHE DI GESTIONE DELLE RISORSE
Cod. Requisito 1A.01.03.01 - REV. 1/{anno}

{intestazione}
1. SCOPO E CAMPO DI APPLICAZIONE
Il presente documento definisce l'organizzazione interna dello studio odontoiatrico {nome}, con sede in {adr}, le politiche adottate per la gestione delle risorse umane, materiali e tecnologiche, e analizza i principali processi al fine di individuare le fasi critiche nelle quali e possibile che si verifichino disservizi, in ottemperanza al requisito 1A.01.03.01 del D.A. 9 gennaio 2024 n. 20 della Regione Siciliana.

2. STRUTTURA ORGANIZZATIVA
2.1 Organigramma
Lo studio e organizzato secondo il seguente schema gerarchico-funzionale:
- Responsabile Sanitario / Titolare ({tit}): esercita la responsabilita clinica, gestionale e legale della struttura. Coordina l'attivita del personale, garantisce il rispetto delle normative sanitarie vigenti, supervisiona i processi di qualita e gestisce i rapporti con le autorita sanitarie (ASP {asp}).
- Direttore Tecnico ({dir_}): supervisiona i processi tecnici e clinici, verifica la conformita delle procedure alle linee guida, coordina la formazione del personale e garantisce la qualita delle prestazioni erogate.
- Odontoiatri collaboratori: eseguono le prestazioni odontoiatriche nelle discipline di competenza, redigono e aggiornano le cartelle cliniche, garantiscono il consenso informato e la corretta informazione ai pazienti.
- Igienisti dentali: eseguono le sedute di igiene orale professionale, effettuano lo screening dei tessuti molli, gestiscono le procedure di sterilizzazione e la preparazione del campo operatorio.
- Assistenti alla Poltrona (ASO): supportano il clinico durante le procedure, gestiscono la sterilizzazione degli strumenti, preparano e riordinano le sale operative, accolgono i pazienti.
- Personale amministrativo: gestisce l'accoglienza, la prenotazione degli appuntamenti, la fatturazione, l'archiviazione della documentazione e le comunicazioni con i pazienti.

2.2 Sostituzioni
In caso di assenza del Responsabile Sanitario, le funzioni sono delegate al Direttore Tecnico o a un odontoiatra collaboratore designato preventivamente e per iscritto.

3. POLITICHE DI GESTIONE DELLE RISORSE
3.1 Risorse Umane
- Tutto il personale sanitario mantiene aggiornamento professionale continuo ECM secondo i crediti obbligatori per categoria.
- Verifica annuale delle competenze tramite colloquio e revisione della documentazione ECM.
- Ogni nuovo collaboratore riceve un percorso di inserimento che include: illustrazione delle procedure interne, formazione sulla sicurezza (D.lgs 81/2008), addestramento ai sistemi informatici e alle procedure di sterilizzazione.
- Il personale esposto a radiazioni ionizzanti e inserito nel programma di sorveglianza fisica della radioprotezione ai sensi del D.lgs 101/2020.

3.2 Risorse Materiali
- Manutenzione periodica di tutte le attrezzature secondo il piano di manutenzione (cfr. Documento 11).
- Controllo settimanale delle scorte di materiale sanitario monouso e di consumo.
- Gestione dell'inventario secondo la procedura di identificazione delle attrezzature (cfr. Documento 10).
- Acquisti effettuati esclusivamente da fornitori certificati CE con documentazione tecnica completa.

3.3 Sicurezza e Qualita
- Protocolli di sterilizzazione conformi alle norme EN ISO 17665 e alla circolare ministeriale n. 400.IV/9.b1/1998.
- Formazione del personale sui rischi specifici dell'attivita odontoiatrica con aggiornamento periodico.
- Monitoraggio continuo degli indicatori di qualita e soddisfazione del paziente.

4. ANALISI DEI PROCESSI E IDENTIFICAZIONE DELLE FASI CRITICHE
4.1 Processo di Accoglienza e Prenotazione
Fasi: contatto telefonico/online - registrazione dati - conferma appuntamento - accoglienza in studio.
Rischio identificato: errori nella gestione dell'agenda, mancata raccolta di informazioni anamnestiche urgenti.
Misure di controllo: software gestionale con alert per allergie e patologie rilevanti, check-list accoglienza, verifica dell'identita del paziente ad ogni accesso.

4.2 Processo Clinico
Fasi: anamnesi - diagnosi - piano di trattamento - consenso informato - trattamento - follow-up.
Rischio identificato: errori diagnostici, reazioni avverse a farmaci/materiali, complicanze intraoperatorie.
Misure di controllo: anamnesi sistematica con modulo standardizzato, aggiornata ad ogni visita; protocolli clinici per ciascuna disciplina; verifica dell'allergia prima di ogni somministrazione di anestetico; disponibilita di kit di emergenza sempre verificato.

4.3 Processo di Sterilizzazione
Fasi: decontaminazione - lavaggio - confezionamento - sterilizzazione in autoclave - stoccaggio.
Rischio identificato: contaminazione crociata, guasto dell'autoclave, utilizzo di materiale non sterile.
Misure di controllo: cicli di sterilizzazione tracciati con etichetta su ogni busta (data, ciclo, operatore); test Helix/Bowie-Dick giornaliero; test biologico settimanale con registrazione degli esiti; verifica visiva dell'integrita delle buste prima dell'uso.

4.4 Processo Amministrativo e Documentale
Fasi: apertura cartella - registrazione prestazioni - fatturazione - archiviazione - conservazione.
Rischio identificato: perdita di dati, accesso non autorizzato, non conformita GDPR.
Misure di controllo: backup automatico giornaliero su sistema sicuro; credenziali personali per ogni utente; contratto con DPO o Responsabile della Protezione dei Dati; archivio fisico chiuso a chiave.

5. MONITORAGGIO, REVISIONE E MIGLIORAMENTO
5.1 Indicatori di Processo
- Tasso di rispetto degli orari degli appuntamenti (target: >90%)
- Numero di reclami mensili e relativo esito
- Esito dei test di sterilizzazione (target: 100% conformi)
- Tasso di completamento dei piani di trattamento

5.2 Strumenti di Monitoraggio
- Audit clinici interni con cadenza semestrale, documentati con verbale.
- Riunioni di staff mensili con revisione degli indicatori e dei casi critici.
- Questionari di soddisfazione del paziente somministrati dopo i trattamenti principali.
- Revisione annuale del presente documento con aggiornamento se necessario.

5.3 Gestione delle Non Conformita
Ogni non conformita rilevata e registrata su apposito modulo, analizzata nelle cause e oggetto di azione correttiva con responsabile e scadenza definiti.

Data di prima adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Firma Direttore Tecnico: {dir_} ______________________
Prossima revisione prevista: ___/___/______""",

        2: f"""DOCUMENTAZIONE INERENTE IL SISTEMA INFORMATIVO
Cod. Requisito 1A.01.04.01 - REV. 1/{anno}

{intestazione}
1. SCOPO
Il presente documento descrive il sistema informativo adottato dallo studio {nome} per la gestione delle attivita cliniche e amministrative, le misure di sicurezza adottate per la protezione dei dati personali e sanitari, la conformita alle normative vigenti in materia di privacy e sicurezza informatica.

2. SISTEMA GESTIONALE IN USO
2.1 Software Clinico-Amministrativo
Lo studio adotta un sistema informatico integrato per la gestione delle seguenti funzioni:
- Agenda elettronica e gestione degli appuntamenti
- Cartella clinica digitale del paziente
- Gestione del piano di trattamento e dei preventivi
- Fatturazione elettronica e gestione della cassa
- Reportistica clinica e gestionale
- Archivio radiografico digitale (DICOM o equivalente)

2.2 Hardware
- Stazioni di lavoro (PC/Mac) in sala clinica e in segreteria
- Server locale o accesso a servizio cloud certificato
- Dispositivi di backup
- Stampante per documenti clinici e amministrativi
- Dispositivi per acquisizione immagini radiografiche digitali

3. SICUREZZA E PROTEZIONE DEI DATI
3.1 Misure Tecniche
- Credenziali di accesso personali (username e password) per ogni utente; accesso differenziato per ruolo (clinico, amministrativo).
- Sessioni automaticamente chiuse dopo periodo di inattivita.
- Backup automatico giornaliero dei dati su dispositivo esterno e/o servizio cloud con cifratura dei dati.
- Protezione antivirus e firewall aggiornati.
- Cifratura dei dati sensibili in archivio e in transito (protocollo HTTPS/TLS per servizi online).

3.2 Misure Organizzative
- Solo il personale autorizzato puo accedere ai dati sanitari dei pazienti.
- Log degli accessi e delle modifiche alla cartella clinica registrati automaticamente dal sistema.
- Distruzione sicura dei supporti rimovibili dismessi.
- Politica di clear desk: nessun documento contenente dati personali lasciato incustodito.

4. CONFORMITA AL GDPR E AL D.LGS 196/2003
4.1 Adempimenti
- E stato redatto il Registro del Trattamento dei Dati ai sensi dell'art. 30 del Regolamento UE 679/2016 (GDPR).
- E stato nominato, ove necessario, il Responsabile della Protezione dei Dati (DPO).
- I pazienti ricevono l'informativa privacy ex art. 13 GDPR prima della presa in carico e firmano il modulo di consenso al trattamento dei dati.
- I consensi firmati sono conservati nella cartella clinica del paziente per l'intera durata della conservazione della documentazione.
- In caso di data breach, e prevista la notifica al Garante entro 72 ore ai sensi dell'art. 33 GDPR.

4.2 Diritti degli Interessati
Il paziente ha diritto di accesso, rettifica, cancellazione, portabilita e opposizione al trattamento dei propri dati, nei limiti consentiti dalla normativa sanitaria vigente. Le richieste sono gestite dal Responsabile Sanitario o dal DPO entro 30 giorni.

5. AGGIORNAMENTO E MANUTENZIONE DEL SISTEMA
- Gli aggiornamenti del software gestionale sono effettuati periodicamente dal fornitore, previa verifica della compatibilita con le funzionalita in uso.
- Il personale riceve formazione all'utilizzo del sistema ad ogni aggiornamento significativo.
- E prevista una procedura di disaster recovery per il ripristino dei dati in caso di guasto o perdita: recupero dal backup piu recente entro 24 ore.
- Il contratto di assistenza con il fornitore del software prevede SLA per la risoluzione dei guasti.

6. FORMAZIONE DEL PERSONALE
Il personale e formato sull'utilizzo corretto del sistema informativo, sulla protezione dei dati personali e sulle procedure da seguire in caso di incidente informatico. La formazione e documentata con verbale e firma.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        3: f"""PROGRAMMA PER LA VALUTAZIONE E IL MIGLIORAMENTO DELLA QUALITA
Cod. Requisito 1A.01.05.01 - REV. 1/{anno}

{intestazione}
1. SCOPO E OBIETTIVI
Il presente programma descrive le modalita con cui lo studio {nome} effettua la valutazione sistematica delle prestazioni erogate e dei servizi offerti, al fine di garantire il miglioramento continuo della qualita, in conformita al requisito 1A.01.05.01 del D.A. 9 gennaio 2024 n. 20.

2. INDICATORI DI QUALITA MONITORATI
2.1 Indicatori Clinici
- Tasso di complicanze post-operatorie: numero di complicanze / totale interventi (target: <2%)
- Tasso di successo implantare a 12 mesi (target: >95%)
- Conformita test sterilizzazione: n. test conformi / n. test totali (target: 100%)
- Tasso di completamento piani di trattamento (target: >80%)
- Correttezza della compilazione della cartella clinica (audit semestrale)

2.2 Indicatori di Processo
- Rispetto degli orari degli appuntamenti: ritardo medio (target: <10 minuti)
- Tasso di appuntamenti cancellati/non presentati (target: <10%)
- Tempo medio di risposta telefonica (target: <3 squilli)
- Completezza della documentazione al momento della visita

2.3 Indicatori di Soddisfazione
- Punteggio medio questionario soddisfazione (target: >=8/10)
- Numero di reclami per trimestre (monitorato con trend)
- Net Promoter Score (NPS): quanti pazienti raccomanderebbero lo studio
- Tasso di fidelizzazione: pazienti che tornano per follow-up o nuovi trattamenti

3. STRUMENTI E METODI DI RACCOLTA DATI
3.1 Questionari di Soddisfazione
Somministrati su base campionaria dopo ogni trattamento significativo (prima visita, fine piano di trattamento, interventi chirurgici). Il questionario valuta: qualita percepita delle cure, comfort durante il trattamento, chiarezza delle informazioni ricevute, efficienza amministrativa, disponibilita del personale.

3.2 Registro dei Reclami
Ogni reclamo, osservazione o suggerimento ricevuto e registrato su apposito modulo con: data, modalita di ricezione, contenuto, azioni intraprese, esito e data di chiusura (cfr. Documento 4).

3.3 Audit Clinici Interni
Con cadenza semestrale, il Responsabile Sanitario effettua la revisione di un campione di cartelle cliniche, verificando: completezza dell'anamnesi, presenza del consenso informato, correttezza delle registrazioni delle prestazioni, conformita ai protocolli clinici adottati.

3.4 Riunioni di Staff
Con cadenza mensile, il personale si riunisce per la revisione degli indicatori, la discussione dei casi clinici complessi, il confronto sulle procedure e l'identificazione di aree di miglioramento.

4. PIANO DI MIGLIORAMENTO
4.1 Procedura
Per ogni area di miglioramento identificata viene redatto un Piano di Intervento che specifica:
- Obiettivo di miglioramento
- Azioni da intraprendere
- Responsabile dell'azione
- Scadenza prevista
- Indicatore di verifica del raggiungimento dell'obiettivo

4.2 Revisione
I piani di miglioramento sono verificati nelle riunioni mensili di staff e nel report annuale di qualita.

5. DOCUMENTAZIONE
Tutti i dati raccolti, gli esiti degli audit, i questionari e i piani di miglioramento sono conservati in archivio per almeno 5 anni e messi a disposizione del Gruppo di Valutazione (GdV) su richiesta.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        4: f"""PROCEDURA PER LA PRESENTAZIONE E GESTIONE DI RECLAMI, OSSERVAZIONI E SUGGERIMENTI
Cod. Requisito 1A.01.06.01 - REV. 1/{anno}

{intestazione}
1. SCOPO E CAMPO DI APPLICAZIONE
La presente procedura definisce le modalita con cui lo studio {nome} raccoglie, gestisce e risponde ai reclami, alle osservazioni e ai suggerimenti presentati da pazienti, familiari o accompagnatori, garantendo trasparenza, tempestivita e tutela dell'utente, in conformita al D.lgs 150/2009 e alla normativa regionale vigente.

2. MODALITA DI PRESENTAZIONE
Il paziente puo presentare reclamo, osservazione o suggerimento attraverso i seguenti canali:
- Modulo cartaceo disponibile in sala d'attesa e consegnato all'accettazione
- Email o PEC allo studio: {pec if pec else '(indirizzo email studio)'}
- Colloquio diretto con il Responsabile Sanitario o con il personale amministrativo
- Lettera scritta recapitata alla sede dello studio
Il modulo e disponibile in piu copie e il personale e formato per supportare il paziente nella compilazione.

3. GESTIONE DEL RECLAMO - PROCEDURA OPERATIVA
3.1 Ricezione e Registrazione (entro 24 ore lavorative)
- Il reclamo e ricevuto dal personale amministrativo o dal Responsabile Sanitario.
- Viene registrato sul Registro dei Reclami con: data e ora di ricezione, modalita di presentazione, generalita del paziente (se fornite), descrizione sintetica del contenuto.
- Al paziente viene rilasciata ricevuta di avvenuta presentazione del reclamo (o inviata conferma via email).

3.2 Analisi e Istruttoria (entro 7 giorni lavorativi)
- Il Responsabile Sanitario valuta il reclamo, raccoglie elementi informativi dal personale coinvolto, esamina la documentazione clinica pertinente.
- Per reclami di natura clinica complessa, il termine puo essere esteso fino a 30 giorni, con comunicazione al paziente.

3.3 Risposta al Paziente
- La risposta scritta e inviata entro 7 giorni lavorativi (30 per casi complessi).
- La risposta contiene: esito dell'istruttoria, azioni correttive intraprese o previste, indicazione di ulteriori vie di tutela (URP ASP, Giudice di Pace, ecc.).

3.4 Chiusura e Archiviazione
- Il reclamo e chiuso con annotazione dell'esito sul registro.
- La documentazione e conservata per almeno 5 anni.

4. ANALISI SISTEMATICA E MIGLIORAMENTO
- Con cadenza trimestrale il Responsabile Sanitario analizza i dati aggregati: numero e tipologia di reclami, tempi di risposta, tipologie di esito.
- Le criticita ricorrenti sono oggetto di piani di miglioramento documentati (cfr. Documento 28).
- I risultati sono discussi nelle riunioni mensili di staff.

5. TUTELA DELLA RISERVATEZZA
I dati identificativi del paziente reclamante sono trattati nel rispetto del GDPR 679/2016 e non sono divulgati al personale non coinvolto nella gestione del reclamo.

6. REGISTRO DEI RECLAMI
Il registro e tenuto aggiornato dal personale amministrativo e contiene per ogni reclamo:
N. progressivo | Data | Contenuto sintetico | Responsabile istruttoria | Esito | Data chiusura

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        5: f"""PROCEDURA PER LE MODALITA DI EROGAZIONE DELL'ASSISTENZA
Cod. Requisito 1A.02.02.01 - REV. 1/{anno}

{intestazione}
1. SCOPO
Il presente documento definisce le modalita con cui lo studio {nome} eroga le prestazioni odontoiatriche, dalla prenotazione al follow-up, garantendo continuita assistenziale, sicurezza e qualita delle cure.

2. PRESTAZIONI EROGATE
Lo studio eroga le seguenti prestazioni odontoiatriche:
- Visita odontoiatrica e consulenza (prima visita, visita di controllo, visita urgente)
- Odontoiatria conservativa e restaurativa (otturazioni in composito, onlay, inlay)
- Endodonzia (devitalizzazione, ritrattamento canalare)
- Parodontologia e igiene orale professionale (detartrasi, levigatura radicolare, chirurgia parodontale)
- Protesi dentale fissa (corone, ponti in metallo-ceramica, zirconia, composito) e mobile (protesi totale, parziale)
- Implantologia orale (inserimento impianti, protesi su impianti)
- Ortodonzia fissa e mobile (apparecchi metallici, in ceramica, allineatori trasparenti)
- Chirurgia orale (estrazione semplice e chirurgica, apicectomia, disinclusione dentale)
- Radiologia dentale digitale (radiografia endorale, ortopantomografia, CBCT ove disponibile)
- Sbiancamento dentale professionale

3. PERCORSO ASSISTENZIALE DEL PAZIENTE
3.1 Prenotazione e Primo Accesso
- Prenotazione tramite telefono, di persona o via email/portale online.
- Al momento della prenotazione: raccolta dati anagrafici, indicazione del motivo della visita, verifica disponibilita agenda.
- I tempi di attesa per la prima visita sono comunicati al momento della prenotazione.
- Per urgenze dolorose o traumatiche, e previsto uno slot giornaliero dedicato o la gestione in giornata ove possibile.

3.2 Prima Visita
- Accoglienza in sala attesa. Il personale di segreteria verifica i dati, consegna l'informativa privacy GDPR e il modulo anamnestico.
- Il paziente compila l'anamnesi medica e firma il consenso al trattamento dei dati.
- Il clinico esegue la visita completa: esame clinico extraorale e intraorale, esame dei tessuti molli, rilevazione dei parametri parodontali ove indicato, prescrizione di esami radiografici necessari.
- Viene redatto il piano di trattamento con priorita e opzioni terapeutiche, e fornito preventivo scritto.
- Il paziente firma il consenso informato per i trattamenti previsti.

3.3 Trattamento
- Ogni prestazione e eseguita nel rispetto dei protocolli clinici adottati dallo studio.
- Prima di ogni seduta: verifica dell'identita del paziente, revisione dell'anamnesi e della terapia farmacologica in corso.
- Il clinico registra le prestazioni eseguite nella cartella clinica del paziente al termine di ogni seduta.
- Materiali e dispositivi medici utilizzati sono marcati CE e tracciati (lotto, scadenza).

3.4 Continuita Assistenziale e Follow-up
- Al termine del piano di trattamento, viene programmata la visita di controllo.
- Urgenze di pazienti in carico sono gestite con priorita.
- In caso di complicanze o necessita di invio a specialista, lo studio fornisce lettera di invio con la documentazione clinica pertinente.
- I pazienti sono richiamati per i controlli periodici di igiene orale e le visite annuali di controllo.

3.5 Pazienti con Disabilita o Bisogni Speciali
I pazienti con disabilita fisica o cognitiva, anziani fragili o bambini piccoli ricevono assistenza prioritaria e personalizzata. Lo studio garantisce accessibilita fisica (cfr. Documento 19) e, ove necessario, si avvale di collaborazioni con strutture specializzate.

4. INFORMAZIONE E CONSENSO
Prima di ogni trattamento significativo il paziente riceve informazioni complete su: diagnosi, opzioni terapeutiche, rischi e benefici, alternative, costo previsto. Il consenso informato e firmato e conservato in cartella clinica.

5. MODALITA DI PAGAMENTO
Sono accettati: contanti (entro i limiti di legge), POS/carta di credito/debito, bonifico bancario, finanziamento rateale tramite finanziarie convenzionate. Il preventivo scritto e consegnato prima dell'inizio del trattamento.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        6: f"""PIANO PER LA GESTIONE DELLE EMERGENZE
Cod. Requisito 1A.02.02.02 - REV. 1/{anno}

{intestazione}
1. SCOPO E CAMPO DI APPLICAZIONE
Il presente piano definisce le procedure operative da adottare in caso di emergenza medica, tecnica o strutturale presso lo studio {nome}, al fine di garantire la sicurezza dei pazienti, degli operatori e dei visitatori, in conformita al D.lgs 81/2008, al DM 10/03/1998 e alle Linee Guida ERC (European Resuscitation Council) per il Basic Life Support.

2. TIPOLOGIE DI EMERGENZA PREVISTE
2.1 Emergenze Mediche a Carico del Paziente
- Sincope vaso-vagale (la piu frequente in studio odontoiatrico)
- Shock anafilattico da anestetico locale, latex o materiali
- Crisi ipoglicemica o iperglicemica in paziente diabetico
- Crisi epilettica
- Crisi ipertensiva o ipotensiva grave
- Infarto acuto del miocardio
- Ictus cerebrale
- Arresto cardiaco
- Reazione allergica lieve/moderata
- Aspirazione/ingestione di corpo estraneo

2.2 Emergenze a Carico dell'Operatore
- Puntura accidentale con ago o strumento tagliente
- Contatto con materiale biologico (sangue, saliva) su mucose o ferite cutanee
- Infortunio sul lavoro

2.3 Emergenze Tecniche
- Guasto improvviso di apparecchiatura durante una procedura
- Interruzione dell'energia elettrica
- Perdita d'acqua o allagamento
- Guasto al sistema di gas medicali

2.4 Emergenze Strutturali
- Incendio
- Terremoto
- Necessita di evacuazione della struttura

3. DOTAZIONI DI EMERGENZA - INVENTARIO E VERIFICHE
3.1 Kit di Pronto Soccorso
Conservato in posizione accessibile, con contenuto verificato mensilmente:
Adrenalina 1:1000 fiale (per anafilassi), Idrocortisone fiale, Antistaminico fiale e/o compresse, Glucosio 33% fiale (per ipoglicemia), Nitroglicerina spray sublinguale, Aspirina 300 mg compresse masticabili, Diazepam fiale (per crisi epilettica), Glucagone kit (per coma ipoglicemico), Soluzione fisiologica 250 ml, Siringhe e aghi sterili, Laccio emostatico, Garze sterili e bende, Guanti sterili.

3.2 Defibrillatore Semiautomatico Esterno (DAE)
Posizionato in luogo visibile e accessibile. Verificato mensilmente (spia verde = pronto all'uso). Manutenzione e sostituzione elettrodi e batterie secondo indicazioni del fabbricante. Almeno un operatore per turno ha conseguito il brevetto BLS-D.

3.3 Bombola di Ossigeno
Presente con maschera con reservoir e valvola a flusso regolabile. Verifica mensile della pressione. Sostituzione quando la pressione scende sotto il livello minimo indicato.

3.4 Estintori
N. _____ estintori a polvere/CO2, verificati semestralmente da ditta specializzata. Registro dei controlli conservato in studio.

4. PROCEDURE OPERATIVE PER EMERGENZA MEDICA
4.1 Procedura Generale
1. Valutare la sicurezza dell'ambiente.
2. Valutare lo stato di coscienza del paziente (stimolo verbale e tattile).
3. Chiamare immediatamente il 118 (o far chiamare da un collaboratore) descrivendo: localita, numero di persone coinvolte, tipo di emergenza, condizioni del paziente.
4. Non abbandonare mai il paziente.
5. Applicare le manovre di BLS se necessario.
6. Accogliere il personale del 118 all'ingresso e fornire le informazioni cliniche.
7. Compilare il Modulo Segnalazione Evento Avverso dopo la risoluzione dell'emergenza.

4.2 Sincope Vaso-Vagale
Reclinare la sedia fino alla posizione di Trendelenburg (gambe in alto). Allentare abiti stretti. Verificare la respirazione. Somministrare glucosio se il paziente e cosciente e ipoglicemico. Monitorare i parametri vitali. Chiamare il 118 se il recupero non avviene entro 1-2 minuti.

4.3 Shock Anafilattico
Interrompere immediatamente la somministrazione dell'agente causale. Chiamare il 118. Posizionare il paziente supino con gambe elevate (se cosciente). Somministrare adrenalina 0,5 mg IM nel muscolo vasto laterale della coscia. Preparare l'accesso venoso. Somministrare ossigeno ad alto flusso. Monitorare la pressione arteriosa e la frequenza cardiaca.

4.4 Arresto Cardiaco
Verificare assenza di risposta e respiro normale. Chiamare il 118. Iniziare le compressioni toraciche (30:2 con ventilazioni). Utilizzare il DAE appena disponibile. Continuare la RCP fino all'arrivo del 118.

5. PROCEDURA DI EVACUAZIONE
1. Il Responsabile dell'Emergenza (Responsabile Sanitario o suo delegato) attiva l'allarme.
2. Il personale guida i pazienti verso le vie di esodo indicate nella planimetria affissa.
3. Chiamare il 115 (Vigili del Fuoco) in caso di incendio.
4. Non utilizzare ascensori in caso di incendio o terremoto.
5. Raggiungere il punto di raccolta esterno: _________________________________.
6. Verificare la presenza di tutto il personale e dei pazienti.
7. Non rientrare nella struttura senza autorizzazione delle autorita.

6. FORMAZIONE E ADDESTRAMENTO
- Tutto il personale e formato sul BLS-D con brevetto aggiornato ogni 2 anni.
- Esercitazioni di evacuazione effettuate almeno una volta l'anno, con verbale.
- Formazione di aggiornamento sulle emergenze mediche in studio almeno ogni 3 anni.
- I nuovi assunti ricevono formazione sull'emergenza entro i primi 30 giorni di lavoro.

7. REGISTRO DELLE EMERGENZE
Ogni evento di emergenza e registrato con: data, ora, tipo di emergenza, paziente/operatore coinvolto, azioni intraprese, esito, osservazioni. Il registro e conservato per almeno 5 anni.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        7: f"""PROTOCOLLO PER L'ISOLAMENTO DI PAZIENTI CON PATOLOGIE CONTAGIOSE
Cod. Requisito 1A.02.02.03 - REV. 1/{anno}

{intestazione}
1. SCOPO
Definire le misure di isolamento e le precauzioni da adottare per la gestione di pazienti con patologie infettive trasmissibili o potenzialmente tali, al fine di prevenire la trasmissione di agenti infettivi tra pazienti e tra paziente e operatore, in conformita alle Linee Guida CDC, alle Raccomandazioni OMS e al D.lgs 81/2008.

2. PATOLOGIE CHE RICHIEDONO PRECAUZIONI AGGIUNTIVE
2.1 Trasmissione per via aerea/droplet
- Tubercolosi polmonare attiva
- Influenza con complicanze respiratorie
- Infezioni respiratorie acute da agenti patogeni ad alta trasmissibilita (es. SARS-CoV-2 e varianti)
- Parotite, morbillo, varicella (in fase prodromica)

2.2 Trasmissione per contatto con sangue/liquidi biologici
- Epatite B (HBsAg positivo, in particolare se HBeAg positivo o con alta carica virale)
- Epatite C (anti-HCV positivo con viremia rilevabile)
- HIV (in qualsiasi stadio, con particolare attenzione in fase di alta viremia)
- Sifilide in fase attiva con lesioni orali

2.3 Infezioni cutanee e mucose
- Herpes labiale in fase attiva
- Candidosi orale grave
- Impetigine o infezioni cutanee diffuse

3. PRECAUZIONI STANDARD (APPLICATE CON TUTTI I PAZIENTI)
Le precauzioni standard costituiscono il livello base di protezione e sono applicate indipendentemente dalla diagnosi:
- Igiene delle mani con gel idroalcolico o lavaggio con acqua e sapone prima e dopo il contatto con il paziente e dopo la rimozione dei guanti.
- Guanti monouso in nitrile o lattice (con verifica allergie al latex).
- Mascherina chirurgica di tipo IIR o FFP2 per procedure che generano aerosol.
- Occhiali protettivi o visiera.
- Camice monouso impermeabile.
- Protezione del piano di lavoro con teli protettivi monouso, sostituiti dopo ogni paziente.

4. PRECAUZIONI AGGIUNTIVE PER PATOLOGIE AD ALTO RISCHIO
4.1 Separazione Temporale
Il paziente con patologia a rischio e programmato come ultimo appuntamento della sessione clinica (mattina o pomeriggio), per consentire una sanificazione approfondita della sala prima della sua rimessa in funzione.

4.2 Separazione Spaziale
Utilizzo di sala operativa dedicata con adeguata ventilazione naturale o meccanica. Il paziente non sosta in sala d'attesa con altri pazienti: viene accolto direttamente in sala operativa.

4.3 DPI Aggiuntivi
- Mascherina FFP2 o FFP3 per patologie a trasmissione aerea.
- Doppio guanto per procedure invasive in pazienti HBV/HCV/HIV.
- Camice impermeabile a manica lunga.
- Calzari monouso ove necessario.

4.4 Strumentario
Utilizzo esclusivo di strumenti monouso ove disponibile. Strumenti riutilizzabili sottoposti a ciclo completo di decontaminazione, lavaggio e sterilizzazione in autoclave Classe B.

5. GESTIONE POST-TRATTAMENTO
- Rifiuti: classificati come rifiuti sanitari pericolosi a rischio infettivo (codice CER 18.01.03*) e smaltiti in appositi contenitori rigidi.
- Sterilizzazione: ciclo completo per tutti gli strumenti riutilizzabili con documentazione del ciclo.
- Sanificazione approfondita della sala con disinfettante virucida certificato (cloro 0,5%, perossido di idrogeno accelerato o equivalente).
- Cambio dei DPI da parte dell'operatore con igiene delle mani al termine del trattamento.

6. COMUNICAZIONE CON IL PAZIENTE
Il paziente e informato delle misure adottate, che sono volte alla tutela della sua salute e di quella degli altri pazienti e del personale. Nessuna discriminazione e attuata nell'erogazione delle cure.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        8: f"""PROCEDURA PER LA GESTIONE DELLA DOCUMENTAZIONE SANITARIA
Cod. Requisito 1A.02.05.01 - REV. 1/{anno}

{intestazione}
1. SCOPO
La presente procedura definisce i requisiti per la redazione, l'aggiornamento, la conservazione, la verifica e il controllo della documentazione sanitaria prodotta dallo studio {nome}, in conformita al DPR 128/1969, al DM 5 agosto 1977, al D.lgs 196/2003, al GDPR 679/2016 e alle Linee Guida regionali.

2. TIPOLOGIE DI DOCUMENTAZIONE GESTITA
- Cartella clinica del paziente (anamnesi, diagnosi, piano di trattamento, registrazioni delle prestazioni)
- Consensi informati firmati per ogni tipologia di trattamento
- Informativa privacy GDPR firmata dal paziente
- Modulo anamnestico medico aggiornato
- Referti e immagini radiografiche (endorali, ortopantomografie, CBCT)
- Preventivi firmati e piani di trattamento
- Documentazione protesica (prescrizioni al laboratorio, verbali di consegna)
- Referti di laboratorio e specialistici
- Documentazione relativa all'utilizzo di dispositivi medici impiantabili (impianti: lotto, ditta, modello)

3. REDAZIONE DELLA DOCUMENTAZIONE
3.1 Apertura della Cartella Clinica
La cartella clinica e aperta ad ogni nuovo paziente prima o al momento della prima visita. Contiene: dati anagrafici completi, anamnesi medica e farmacologica dettagliata, consenso al trattamento dei dati, consenso alle cure.

3.2 Registrazione delle Prestazioni
Ogni prestazione eseguita e registrata nella cartella clinica del paziente con: data, descrizione della prestazione, dente/arcata interessata, materiali utilizzati (con lotto ove pertinente), eventuali note cliniche, firma del clinico esecutore.

3.3 Aggiornamento dell'Anamnesi
L'anamnesi medica e farmacologica e verificata e aggiornata ad ogni accesso del paziente. Il paziente e invitato a comunicare eventuali variazioni dello stato di salute o della terapia farmacologica.

4. ACCESSO, SICUREZZA E RISERVATEZZA
- L'accesso alla cartella clinica e riservato al personale sanitario autorizzato dello studio.
- Le cartelle cartacee sono conservate in archivio fisico chiuso a chiave.
- Le cartelle digitali sono protette da credenziali personali con accesso differenziato per ruolo.
- Il paziente ha diritto di accesso alla propria documentazione clinica ai sensi dell'art. 15 GDPR; le copie sono rilasciate previa verifica dell'identita entro 30 giorni dalla richiesta.

5. CONSERVAZIONE E TEMPI DI ARCHIVIAZIONE
- Cartella clinica: minimo 10 anni dall'ultima prestazione, salvo indicazioni piu restrittive.
- Referti radiografici: almeno 20 anni per radiografie diagnostiche (DPR 14 gennaio 1997 n. 37).
- Consensi informati: per tutta la durata di conservazione della cartella clinica.
- Documentazione relativa a impianti (dispositivi medici impiantabili): 15 anni dalla data dell'intervento ai sensi del D.lgs 137/2022.
- Documentazione di sterilizzazione (tracciabilita cicli): minimo 5 anni.

6. CONSEGNA DELLA DOCUMENTAZIONE AL PAZIENTE
- Copie della documentazione clinica sono rilasciate su richiesta scritta del paziente o del suo legale rappresentante.
- Le immagini radiografiche digitali sono consegnate su supporto USB o tramite piattaforma sicura.
- L'invio elettronico avviene solo tramite canali cifrati (PEC o piattaforma GDPR-compliant).

7. VERIFICA E CONTROLLO
Il Responsabile Sanitario effettua con cadenza semestrale un audit a campione sulle cartelle cliniche per verificare: completezza dell'anamnesi, presenza e completezza dei consensi, regolarita delle registrazioni delle prestazioni, conformita alla presente procedura.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        9: f"""DOCUMENTO FORMALE DI INCARICO DEL RESPONSABILE DELLA MANUTENZIONE
Cod. Requisito 1A.03.01.01 - REV. 1/{anno}

Studio: {nome} | Sede: {adr}

ATTO DI NOMINA

Il/La sottoscritto/a {tit}, in qualita di Responsabile Sanitario e Legale Rappresentante dello Studio Odontoiatrico {nome}, con sede in {adr}, C.F./P.IVA {cf if cf else '___________'},

NOMINA

quale Responsabile della Manutenzione della struttura il/la:

Sig./Dott. {resp_mnt}

MANSIONI E RESPONSABILITA ASSEGNATE
Il Responsabile della Manutenzione ha il compito di:
1. Coordinare e supervisionare tutti gli interventi di manutenzione ordinaria e straordinaria delle strutture, degli impianti, delle attrezzature e delle apparecchiature biomediche dello studio.
2. Gestire e mantenere aggiornato l'inventario delle attrezzature (cfr. Documento 10), con verifica annuale obbligatoria.
3. Pianificare, documentare e verificare l'esecuzione del piano di manutenzione preventiva programmata (cfr. Documento 11), con cadenze stabilite per ciascuna tipologia di attrezzatura.
4. Gestire i rapporti con i fornitori di assistenza tecnica, richiedere i preventivi, verificare la qualita degli interventi eseguiti e conservare i rapporti di lavoro.
5. Verificare la conformita delle attrezzature alle normative vigenti (marcatura CE, norme CEI, normative di settore) e segnalare al Responsabile Sanitario eventuali non conformita.
6. Conservare e aggiornare la documentazione tecnica relativa a ciascuna attrezzatura (manuali d'uso, certificati di collaudo, rapporti di manutenzione) come previsto dal Documento 12.
7. Coordinare il collaudo tecnico di sicurezza (CTS) ad ogni nuova acquisizione di apparecchiatura, prima della messa in servizio, e conservare il relativo verbale.
8. Segnalare tempestivamente al Responsabile Sanitario qualsiasi guasto, anomalia o situazione di rischio che possa compromettere la sicurezza degli operatori o dei pazienti.
9. Partecipare alle riunioni periodiche di sicurezza.
10. Collaborare con il RSPP per quanto di competenza in materia di sicurezza degli impianti e delle attrezzature.

RISORSE MESSE A DISPOSIZIONE
Per l'espletamento delle proprie funzioni, il Responsabile della Manutenzione dispone di:
- Accesso all'archivio della documentazione tecnica delle attrezzature
- Budget per la manutenzione ordinaria, previa approvazione del Responsabile Sanitario per spese straordinarie
- Elenco aggiornato dei fornitori e delle ditte di assistenza tecnica autorizzate

DURATA DELL'INCARICO
L'incarico ha durata indeterminata e puo essere revocato in qualsiasi momento con comunicazione scritta.

Luogo e data: {s['comune'].title() if s.get('comune') else adr}, {oggi}

Firma del Responsabile Sanitario: ______________________
{tit}

Firma del Responsabile della Manutenzione per accettazione: ______________________
{resp_mnt}""",

        11: f"""PIANO DI MANUTENZIONE STRUTTURE, IMPIANTI E ATTREZZATURE
Cod. Requisito 1A.03.02.02 - REV. 1/{anno}

{intestazione}
1. SCOPO
Il presente piano definisce le attivita di manutenzione ordinaria programmata e le modalita di gestione della manutenzione straordinaria per tutte le strutture, gli impianti e le attrezzature biomediche dello studio {nome}, al fine di garantirne il corretto funzionamento, la sicurezza degli operatori e dei pazienti e la conformita normativa.

2. MANUTENZIONE ORDINARIA PROGRAMMATA
2.1 Attrezzature Biomediche

RIUNITI ODONTOIATRICI
- Frequenza: semestrale
- Eseguita da: tecnico autorizzato dalla casa costruttrice
- Comprende: verifica della pressione dell'aria, controllo dei circuiti idraulici, lubrificazione dei manipoli, verifica delle lampade, test dei sistemi di aspirazione, verifica delle valvole antiretrazione.
- Documentazione: rapporto tecnico del fornitore, conservato nel fascicolo dell'apparecchiatura.

AUTOCLAVE CLASSE B
- Test Bowie-Dick: ogni giorno di utilizzo (primo ciclo della giornata a vuoto)
- Test Helix: ogni giorno di utilizzo con strumento tubolare
- Manutenzione completa: annuale, da tecnico autorizzato
- Test biologico: settimanale (Geobacillus stearothermophilus)
- Taratura della sonda di temperatura e pressione: annuale
- Tutti i test registrati nel registro di sterilizzazione con firma dell'operatore.

ORTOPANTOMOGRAFO (OPT) / APPARECCHIATURE RADIOLOGICHE
- Manutenzione e taratura: annuale, da tecnico specializzato
- Verifica dosimetrica: annuale, da Esperto Qualificato in Radioprotezione
- Pulizia del rivelatore/sensore digitale: secondo indicazioni del fabbricante
- Documentazione: verbale di manutenzione, report dosimetrico, conservati nell'archivio.

COMPRESSORE ODONTOIATRICO
- Drenaggio della condensa: settimanale
- Sostituzione filtri aria: semestrale o secondo ore di lavoro
- Manutenzione completa: annuale da tecnico specializzato

SCANNER INTRAORALE (ove presente)
- Aggiornamento software: semestrale o quando disponibile
- Pulizia dell'ottica: mensile con panno in microfibra
- Calibrazione: secondo indicazioni del fabbricante

2.2 Impianti e Strutture

IMPIANTO ELETTRICO
- Verifica e misure di sicurezza (DM 37/2008, norma CEI 64-8): biennale da elettricista abilitato
- Verifica dell'impianto di messa a terra e del differenziale: annuale
- Documentazione: dichiarazione di conformita iniziale + verbali delle verifiche periodiche.

SISTEMA ANTINCENDIO ED ESTINTORI
- Verifica visiva degli estintori: mensile (spia, sigillo, indicatore di pressione)
- Manutenzione degli estintori: semestrale da ditta specializzata
- Manutenzione annuale: con sostituzione agente estinguente se necessario
- Verifica delle vie di esodo e dell'illuminazione di emergenza: mensile
- Documentazione: registro antincendio, verbali delle verifiche semestrali.

IMPIANTI DI CLIMATIZZAZIONE/VENTILAZIONE
- Pulizia e sostituzione filtri: ogni 3 mesi o secondo utilizzo
- Manutenzione completa: semestrale da tecnico abilitato F-GAS
- Documentazione: registro dell'impianto F-GAS, rapporti di manutenzione.

IMPIANTO IDRICO E ACQUA RIUNITI
- Verifica e disinfezione delle linee dell'acqua dei riuniti: ogni 6 mesi (Legionella prevention)
- Test microbiologico dell'acqua erogata dal riunito: annuale
- Documentazione: rapporti di laboratorio, schede di trattamento.

3. MANUTENZIONE STRAORDINARIA
- Gli interventi straordinari sono richiesti dal Responsabile della Manutenzione al Responsabile Sanitario.
- Vengono affidati a ditte specializzate certificate per la tipologia di intervento.
- Ogni intervento e documentato con: data, tipo di guasto, ditta incaricata, descrizione dell'intervento, pezzi sostituiti, esito, firma del tecnico e prossima scadenza di verifica.
- In caso di guasto a un'apparecchiatura biomedica durante una procedura clinica, l'operatore segue la procedura di emergenza tecnica (cfr. Documento 6) e segnala il guasto al Responsabile della Manutenzione.

4. REGISTRO DELLA MANUTENZIONE
Il Responsabile della Manutenzione tiene aggiornato un registro (cartaceo o informatico) in cui sono riportati per ciascuna apparecchiatura e impianto: tutte le attivita di manutenzione effettuate, le date di esecuzione, i tecnici o le ditte intervenute, gli esiti e le prossime scadenze.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Firma Responsabile Manutenzione: {resp_mnt} ______________________
Prossima revisione: ___/___/______""",

        12: f"""DOCUMENTAZIONE TECNICA ATTREZZATURE E APPARECCHIATURE BIOMEDICHE
Cod. Requisito 1A.03.02.03 - REV. 1/{anno}

{intestazione}
1. SCOPO
Il presente documento descrive le modalita con cui lo studio {nome} raccoglie, organizza, aggiorna e rende immediatamente disponibile la documentazione tecnica relativa a ciascuna attrezzatura e apparecchiatura biomedica in dotazione, in conformita al D.lgs 46/1997 (dispositivi medici), al D.lgs 81/2008 e alle indicazioni del MAMB.

2. CONTENUTO DEL FASCICOLO TECNICO DI OGNI APPARECCHIATURA
Per ogni attrezzatura e apparecchiatura presente nello studio e conservato un fascicolo individuale contenente:
a) Dati identificativi: nome, modello, numero di serie, anno di fabbricazione, ditta fornitrice, data di acquisto.
b) Documentazione normativa: dichiarazione di conformita CE / dichiarazione EU di conformita, marcatura CE, foglio illustrativo in lingua italiana.
c) Manuale d'uso e manutenzione: in lingua italiana, integrale, con istruzioni per l'uso corretto, la pulizia, la disinfezione e la manutenzione.
d) Documentazione di installazione: verbale di installazione e collaudo tecnico di sicurezza (CTS), firmato dal tecnico installatore.
e) Registri di manutenzione: tutti i rapporti di assistenza tecnica, le manutenzioni ordinarie e straordinarie, in ordine cronologico.
f) Certificati di taratura/calibrazione: per le apparecchiature che richiedono taratura periodica (autoclave, OPT, scanner).
g) Rapporti di verifica periodica: verbali delle ispezioni obbligatorie o raccomandate.
h) Segnalazioni di guasto: registrazione di ogni guasto, anomalia e relativo intervento risolutivo.

3. ORGANIZZAZIONE E ACCESSIBILITA
3.1 Archivio Fisico
I fascicoli tecnici sono conservati in un raccoglitore/archivio dedicato, identificato per apparecchiatura, accessibile al Responsabile della Manutenzione e al Responsabile Sanitario.

3.2 Archivio Digitale
Ove possibile, la documentazione e duplicata in formato digitale (PDF) su disco o cloud con accesso protetto, per garantire la disponibilita anche in caso di perdita del cartaceo.

3.3 Disponibilita agli Operatori
Il Responsabile della Manutenzione garantisce che il manuale d'uso di ogni apparecchiatura sia immediatamente disponibile agli operatori che la utilizzano, nelle immediate vicinanze del posto di utilizzo o su supporto digitale accessibile.

4. AGGIORNAMENTO
Il fascicolo tecnico e aggiornato ad ogni:
- Intervento di manutenzione ordinaria o straordinaria
- Modifica o aggiornamento dell'apparecchiatura
- Sostituzione di componenti principali
- Nuova verifica o certificazione periodica

5. FORMAZIONE
Prima di utilizzare qualsiasi apparecchiatura, il personale riceve formazione specifica sull'uso corretto, le procedure di sicurezza e le azioni da intraprendere in caso di guasto o anomalia. La formazione e documentata con verbale e firma dell'operatore.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Firma Responsabile Manutenzione: {resp_mnt} ______________________
Prossima revisione: ___/___/______""",

        25: f"""OBBLIGHI ASSICURATIVI DEFINITI DALLA NORMATIVA APPLICABILE
Cod. Requisito 1A.04.12.04 - REV. 1/{anno}

{intestazione}
1. RIFERIMENTI NORMATIVI
- Legge 8 marzo 2017, n. 24 (Legge Gelli-Bianco): obbligo di copertura assicurativa o misure equivalenti per strutture sanitarie e professionisti.
- Decreto del Ministero dello Sviluppo Economico 9 gennaio 2015, n. 10: requisiti minimi delle polizze assicurative per esercenti le professioni sanitarie.
- D.lgs 9 aprile 2008, n. 81 (Testo Unico Sicurezza): assicurazione INAIL per i lavoratori.

2. ASSICURAZIONE RESPONSABILITA CIVILE PROFESSIONALE
Ai sensi della Legge 24/2017, lo studio e coperto da polizza assicurativa per responsabilita civile verso terzi per danni derivanti da attivita sanitaria:
Compagnia assicurativa: ________________________________
Numero di polizza: ________________________________
Data di decorrenza: ___/___/______
Data di scadenza: ___/___/______
Massimale per sinistro: EUR ________________________________
Massimale annuo: EUR ________________________________
Estensione della copertura: responsabilita civile per danni a pazienti e terzi derivanti dall'attivita odontoiatrica, compresi i collaboratori dello studio.

3. ASSICURAZIONE INAIL
La struttura assolve agli obblighi previdenziali e assicurativi per i lavoratori dipendenti ai sensi del DPR 30 giugno 1965, n. 1124:
Codice ditta INAIL: ________________________________
Posizione Assicurativa Territoriale (PAT): ________________________________
Classe di rischio: ________________________________

4. ASSICURAZIONE STRUTTURA E CONTENUTO
Polizza assicurativa per danni alla struttura, agli impianti e al contenuto (attrezzature, arredi, strumentazione):
Compagnia assicurativa: ________________________________
Numero di polizza: ________________________________
Validita: dal ___/___/______ al ___/___/______
Massimale: EUR ________________________________

5. VERIFICA ANNUALE
Il Responsabile Sanitario verifica annualmente la validita e l'adeguatezza di tutte le coperture assicurative, procedendo al rinnovo prima della scadenza. Copia di tutte le polizze attive e conservata in archivio e messa a disposizione del GdV su richiesta.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        26: f"""CARTA DEI SERVIZI
Cod. Requisito 1A.05.03.01 - REV. 1/{anno}

{nome.upper()}
{adr}
Tel: {telefono if telefono else '__________________'}  |  PEC/Email: {pec if pec else '__________________'}
Responsabile Sanitario: {tit}  |  Albo: {albo if albo else '__________________'}
ASP di riferimento: {asp}

PRESENTAZIONE DELLO STUDIO
Lo studio odontoiatrico {nome}, con sede in {adr}, e autorizzato all'esercizio di attivita sanitaria ai sensi del D.A. 9 gennaio 2024 n. 20 della Regione Siciliana. La struttura eroga prestazioni odontoiatriche di alta qualita in un ambiente confortevole, moderno e in piena conformita con le normative vigenti in materia di sicurezza e igiene.

PRESTAZIONI EROGATE
Visita odontoiatrica e consulenza (prima visita, visita di controllo, visita di urgenza)
Igiene orale professionale e parodontologia
Odontoiatria conservativa e restaurativa (composito, onlay, inlay ceramico)
Endodonzia (devitalizzazione, ritrattamento)
Protesi dentale fissa (corone e ponti in ceramica integrale, zirconia, metallo-ceramica)
Protesi mobile (protesi totale, protesi parziale scheletrata e in resina)
Implantologia orale e protesi su impianti
Ortodonzia fissa e mobile, allineatori trasparenti
Chirurgia orale (estrazioni semplici e chirurgiche, apicectomie)
Radiologia dentale digitale (radiografie endorali, ortopantomografia)
Sbiancamento dentale professionale

ORARI DI APERTURA
Lunedi - Venerdi: ______ / ______
Sabato: ______ / ______
Urgenze: gestite telefonicamente e, ove possibile, in giornata.

MODALITA DI ACCESSO E PRENOTAZIONE
Telefono: {telefono if telefono else '__________________'}
Email/PEC: {pec if pec else '__________________'}
Di persona: presso la reception dello studio negli orari di apertura
Le prenotazioni possono essere effettuate con anticipo fino a ______ settimane.
I tempi di attesa per la prima visita sono comunicati al momento della prenotazione.

STANDARD DI QUALITA E IMPEGNI
Lo studio si impegna a garantire:
- Puntualita: il paziente non attende piu di 15 minuti oltre l'orario dell'appuntamento; in caso di ritardo il paziente e informato tempestivamente.
- Trasparenza: preventivo scritto firmato prima di ogni trattamento significativo, con indicazione delle opzioni terapeutiche disponibili.
- Informazione: il paziente riceve spiegazioni complete su diagnosi, trattamento proposto, alternative, rischi e benefici prima di qualsiasi procedura.
- Riservatezza: i dati personali e sanitari sono trattati nel rispetto del Regolamento UE 679/2016 (GDPR).
- Risposta ai reclami: entro 7 giorni lavorativi dalla presentazione.
- Qualita tecnica: le prestazioni sono eseguite da professionisti abilitati, con aggiornamento ECM continuo e con attrezzature certificate e regolarmente manutenute.
- Sicurezza: protocolli di sterilizzazione conformi alle normative vigenti; utilizzo di materiali e dispositivi medici marcati CE.

TARIFFE E MODALITA DI PAGAMENTO
Il tariffario e esposto in sala d'attesa e disponibile su richiesta alla reception. Sono accettati: contanti (entro i limiti di legge), carte di credito/debito (POS), bonifico bancario, finanziamento rateale tramite finanziarie convenzionate. E rilasciata regolare ricevuta fiscale per ogni prestazione.

TUTELA DEL PAZIENTE
Per segnalazioni, reclami o suggerimenti: rivolgersi direttamente al Responsabile Sanitario o utilizzare il modulo reclami disponibile in sala attesa (cfr. Documento 4). In caso di insoddisfazione e possibile rivolgersi all'URP dell'ASP {asp} o all'Ordine degli Odontoiatri competente.

Data di emissione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        27: f"""MODALITA DI IDENTIFICAZIONE DI TIROCINANTI, SPECIALIZZANDI E COLLABORATORI IN FORMAZIONE
Cod. Requisito 1A.05.03.03 - REV. 1/{anno}

{intestazione}
1. SCOPO
Il presente documento definisce le modalita con cui lo studio {nome} identifica, gestisce e rende riconoscibili i soggetti in formazione che intervengono nel percorso assistenziale, garantendo la trasparenza nei confronti dei pazienti e la conformita normativa.

2. TIPOLOGIE DI SOGGETTI INTERESSATI
- Tirocinanti universitari (studenti dei corsi di laurea in odontoiatria, igiene dentale, assistenza odontoiatrica)
- Specializzandi (in chirurgia orale, ortodonzia, parodontologia o altre specializzazioni)
- Collaboratori in affiancamento formativo
- Osservatori (che non eseguono procedure cliniche dirette)
- Docenti o tutori universitari in visita

3. REQUISITI DI ACCESSO ALLO STUDIO
I soggetti in formazione possono accedere allo studio solo previa:
- Stipula di convenzione/accordo scritto tra lo studio e l'istituto/universita di appartenenza.
- Verifica della copertura assicurativa per responsabilita civile verso terzi durante l'attivita di tirocinio (a carico dell'istituto o dello studio).
- Valutazione del livello di preparazione da parte del Responsabile Sanitario o del Direttore Tecnico.
- Idoneita sanitaria in materia di malattie infettive trasmissibili (vaccinazioni obbligatorie, ove previste).

4. MODALITA DI IDENTIFICAZIONE E RICONOSCIMENTO
4.1 Cartellino Identificativo
Ogni soggetto in formazione indossa durante la permanenza in studio un cartellino identificativo visibile, riportante:
- Nome e cognome
- Qualifica (es. "Tirocinante", "Specializzando", "Osservatore")
- Istituto/universita di provenienza
Il cartellino e consegnato dal Responsabile Sanitario al primo accesso e riconsegnato al termine del tirocinio.

4.2 Abbigliamento Professionale
Il soggetto in formazione indossa divisa/camice distinto da quello del personale strutturato, oppure la divisa dello studio con una distinzione visiva (es. colore diverso del cartellino, targhetta specifica).

5. COMUNICAZIONE AL PAZIENTE E CONSENSO
5.1 Informazione Preventiva
Prima dell'inizio di ogni seduta in cui sia presente un soggetto in formazione, il paziente e informato verbalmente e/o per iscritto della presenza, del ruolo e del livello di autonomia del soggetto in formazione.

5.2 Diritto al Rifiuto
Il paziente ha il diritto di rifiutare la presenza del soggetto in formazione, in qualsiasi momento e senza necessita di fornire motivazioni. Il rifiuto non comporta alcuna conseguenza sulla qualita o sulla tempistica delle cure ricevute.

5.3 Documentazione del Consenso
Ove la presenza del tirocinante comporti un ruolo attivo (anche di assistenza), il paziente firma apposita sezione del consenso informato relativa alla presenza di personale in formazione.

6. LIVELLI DI SUPERVISIONE
- Osservazione passiva: il soggetto in formazione puo osservare la prestazione senza intervenire. Non e richiesta comunicazione preventiva al paziente.
- Assistenza indiretta: il soggetto in formazione assiste il clinico (porge materiali, aspira). E richiesta informazione al paziente.
- Esecuzione sotto supervisione diretta: il soggetto esegue manovre cliniche con il clinico strutturato presente e in grado di intervenire in ogni momento. E obbligatorio il consenso informato del paziente.

7. REGISTRO DEI SOGGETTI IN FORMAZIONE
Lo studio conserva un registro aggiornato dei soggetti in formazione presenti, con: nome, qualifica, istituto, periodo di presenza, referente accademico, tipo di attivita svolta.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        28: f"""REPORT CRITICITA E PIANI DI INTERVENTO - CUSTOMER SATISFACTION E RECLAMI
Cod. Requisito 1A.05.03.05 - REV. 1/{anno}

{intestazione}
1. SCOPO
Il presente documento definisce le modalita con cui lo studio {nome} raccoglie, analizza e utilizza i dati provenienti dall'analisi dei reclami e dalle indagini di soddisfazione del paziente, al fine di identificare le criticita e definire piani di intervento migliorativi.

2. METODOLOGIA DI RACCOLTA DATI
2.1 Questionari di Customer Satisfaction
Somministrati su base campionaria con le seguenti modalita:
- Questionario cartaceo consegnato in sala d'attesa al termine della seduta
- Link a questionario online inviato via SMS/email dopo il trattamento
- Intervista telefonica per pazienti selezionati (es. dopo trattamenti complessi)
Il questionario valuta le seguenti dimensioni:
a) Qualita percepita delle cure (scala 1-10)
b) Comfort e sensazione di sicurezza durante il trattamento (scala 1-10)
c) Chiarezza delle informazioni ricevute sul trattamento (scala 1-10)
d) Rispetto della privacy (scala 1-10)
e) Efficienza e cortesia del personale amministrativo (scala 1-10)
f) Rispetto dei tempi di attesa (scala 1-10)
g) Ambiente pulito e confortevole (scala 1-10)
h) Disponibilita a raccomandare lo studio ad altri (NPS: scala 0-10)
i) Commenti liberi e suggerimenti

2.2 Analisi dei Reclami
I dati del Registro dei Reclami (cfr. Documento 4) sono analizzati con cadenza trimestrale per identificare: tipologie di reclami piu frequenti, trend temporali, tempo medio di risposta, tasso di risoluzione soddisfacente.

3. ANALISI E REPORT PERIODICI
3.1 Report Trimestrale
Il Responsabile Sanitario elabora, con cadenza trimestrale, un report sintetico contenente:
- Numero di questionari raccolti e tasso di risposta
- Punteggio medio per ciascuna dimensione valutata
- NPS (Net Promoter Score) del trimestre
- Numero e tipologia di reclami ricevuti
- Confronto con i trimestri precedenti (trend)
- Principali criticita emerse

3.2 Report Annuale
Il report annuale contiene l'analisi complessiva dell'anno, l'identificazione delle aree di miglioramento prioritarie e la valutazione dell'efficacia dei piani di intervento adottati nell'anno precedente.

4. PIANI DI INTERVENTO
Per ogni criticita identificata (punteggio medio inferiore al target, aumento dei reclami, segnalazioni ricorrenti), e redatto un Piano di Intervento contenente:
- Descrizione della criticita
- Analisi delle cause (causa radice)
- Azioni correttive previste
- Responsabile dell'azione
- Scadenza
- Indicatore di verifica dell'efficacia
I piani di intervento sono discussi nelle riunioni mensili di staff e verificati nel report trimestrale successivo.

5. MODULO REPORT (DA COMPILARE PERIODICAMENTE)
Periodo di riferimento: ___/___/______ - ___/___/______
N. questionari somministrati: ______
N. questionari restituiti: ______  (tasso di risposta: ______%)
Punteggio medio soddisfazione generale: ______/10
NPS: ______
N. reclami ricevuti: ______
N. reclami risolti entro i termini: ______
Principali criticita emerse: ____________________________________________
Piano di intervento attivato: Si / No  - Descrizione: ______________________________

Data: {oggi}    Firma Responsabile Sanitario: {tit} ______________________""",

        29: f"""PIANO AZIENDALE PER LA GESTIONE DEL RISCHIO CLINICO
Cod. Requisito 1A.06.02.01 - REV. 1/{anno}

{intestazione}
1. SCOPO E POLITICA PER LA SICUREZZA DEL PAZIENTE
Il presente piano definisce le strategie, le procedure e gli strumenti adottati dallo studio {nome} per la gestione del rischio clinico, in conformita alla Legge 8 marzo 2017, n. 24 (Legge Gelli-Bianco), al D.A. 9 gennaio 2024 n. 20 della Regione Siciliana e alle Raccomandazioni del Ministero della Salute.
La direzione dello studio si impegna a promuovere una cultura della sicurezza basata su: prevenzione proattiva dei rischi, segnalazione non punitiva degli eventi avversi, analisi sistematica delle cause e miglioramento continuo.

2. ANALISI E CLASSIFICAZIONE DEI RISCHI
2.1 Rischio Infettivo
Rischio: trasmissione di agenti patogeni tra paziente e operatore o tra pazienti.
Probabilita: alta senza misure di controllo. Gravita: alta (HIV, HBV, HCV, SARS-CoV-2).
Misure di controllo:
- Protocollo di sterilizzazione conforme a EN ISO 17665 (autoclave Classe B, ciclo B con tracciabilita)
- Precauzioni standard con tutti i pazienti (DPI: guanti, mascherina, occhiali, camice)
- Precauzioni aggiuntive per pazienti con patologie infettive note (cfr. Documento 7)
- Disinfezione delle superfici con disinfettante virucida dopo ogni paziente
- Vaccinazione HBV obbligatoria per il personale a rischio
- Verifica annuale della copertura vaccinale del personale

2.2 Rischio da Radiazioni Ionizzanti
Rischio: esposizione ingiustificata o eccessiva del paziente e/o dell'operatore a radiazioni.
Misure di controllo:
- Applicazione del principio ALARA (As Low As Reasonably Achievable)
- Utilizzo di radiografia digitale (riduzione dose fino al 70% rispetto alla pellicola)
- Collimatore rettangolare per radiografie endorali
- Camice piombato per pazienti (obbligatorio per donne in eta fertile e bambini)
- Sorveglianza fisica e dosimetrica del personale esposto (D.lgs 101/2020)
- Formazione del personale sulla radioprotezione

2.3 Rischio Anestesiologico
Rischio: reazione avversa all'anestetico locale (allergia, sovradosaggio, intossicazione sistemica).
Misure di controllo:
- Anamnesi farmacologica accurata prima di ogni seduta con specifiche domande sulle allergie
- Utilizzo di anestetico con vasocostritore alla dose minima efficace
- Aspirazione prima dell'iniezione per evitare iniezione intravascolare
- Disponibilita di kit di emergenza verificato e completo
- Formazione BLS-D di almeno un operatore per turno

2.4 Rischio Emorragico
Rischio: emorragia post-estrattiva o durante procedure chirurgiche in pazienti a rischio.
Misure di controllo:
- Anamnesi farmacologica con identificazione di anticoagulanti, antiaggreganti, FANS, integratori
- Coordinamento con il medico curante per la gestione della terapia peri-operatoria
- Protocolli di emostasi locale (sutura, materiali emostatici, compressione)
- Istruzioni scritte post-operatorie fornite al paziente

2.5 Rischio da Corpo Estraneo
Rischio: aspirazione o ingestione accidentale di strumenti o materiali.
Misure di controllo:
- Utilizzo sistematico della diga di gomma per endodonzia e restauri
- Filo di seta o filo dentale legato agli strumenti endodontici
- Avvertimento del paziente prima dell'utilizzo di strumenti di piccole dimensioni
- Testa in posizione neutra/semi-reclinata (non completamente supina)

2.6 Rischio di Errore di Identita o di Sito
Rischio: trattamento eseguito sul paziente sbagliato, dente sbagliato o procedura errata.
Misure di controllo:
- Verifica dell'identita del paziente ad ogni accesso (nome, data di nascita)
- Revisione del piano di trattamento prima di ogni seduta
- Conferma verbale con il paziente del trattamento da eseguire e del dente interessato
- Radiografia di riferimento visibile durante l'intervento

3. SISTEMA DI SEGNALAZIONE DEGLI EVENTI
Ogni near miss, evento avverso o evento sentinella e segnalato, registrato e analizzato secondo la procedura del Documento 32. La segnalazione avviene su base volontaria, in un clima di fiducia reciproca, senza finalita punitive.

4. FORMAZIONE E AGGIORNAMENTO
Il personale riceve formazione periodica sulla gestione del rischio clinico, sulla sicurezza del paziente e sulle tecniche di comunicazione con il paziente. La formazione e documentata e inclusa nel programma ECM.

5. REVISIONE ANNUALE
Il presente piano e revisionato annualmente dal Responsabile Sanitario, tenendo conto dei dati sugli eventi avversi, dei reclami, degli esiti degli audit e delle eventuali modifiche normative.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        30: f"""PROCEDURA PER LA PULIZIA E SANIFICAZIONE DEGLI AMBIENTI
Cod. Requisito 1A.06.02.02 - REV. 1/{anno}

{intestazione}
1. SCOPO
La presente procedura definisce le frequenze, le modalita operative, i prodotti e le responsabilita per la pulizia, la disinfezione e la sanificazione di tutti gli ambienti dello studio {nome}, al fine di mantenere un livello igienico adeguato per una struttura sanitaria e prevenire le infezioni correlate all'assistenza.

2. DEFINIZIONI
- Pulizia: rimozione dello sporco fisico con detergente.
- Disinfezione: eliminazione dei microrganismi patogeni con prodotto biocida registrato.
- Sanificazione: combinazione di pulizia e disinfezione.
- Sterilizzazione: eliminazione di tutte le forme microbiche incluse le spore (solo per gli strumenti, in autoclave).
- Decontaminazione: trattamento preliminare degli strumenti prima del lavaggio (immersione in soluzione decontaminante).

3. PRODOTTI UTILIZZATI
Tutti i prodotti sono registrati al Ministero della Salute come presidio medico-chirurgico (PMC) o come biocida (D.lgs 205/2010):
- Disinfettante per superfici: soluzione a base di ipoclorito di sodio allo 0,5-1% o perossido di idrogeno accelerato al 0,5% (Virkon, Incidin, Rely+On o equivalente). Efficace su HIV, HBV, HCV, SARS-CoV-2.
- Detergente per pavimenti: detergente con attivita disinfettante (cloro al 0,1% per ambienti sanitari).
- Gel idroalcolico per mani: almeno al 70% di alcol etilico o isopropilico.
- Decontaminante per strumenti: soluzione di glutaraldeide o enzimi proteolitici secondo scheda tecnica.

4. FREQUENZA E MODALITA DEGLI INTERVENTI
4.1 Dopo Ogni Paziente (sala operativa)
- Rimozione e smaltimento di tutti i materiali monouso utilizzati (guanti, mascherine, teli, aspirati).
- Decontaminazione e raccolta degli strumenti riutilizzabili per il ciclo di sterilizzazione.
- Disinfezione di tutte le superfici della sala: piano di lavoro, bracciolo del riunito, poggiatesta, manipoli, lampada, tastiera del riunito, superfici toccate durante la procedura, con disinfettante virucida. Tempo di contatto: rispettare i tempi indicati dalla scheda tecnica del prodotto (in genere 1-5 minuti).
- Sostituzione dei teli di protezione monouso.
- Cambio e smaltimento dei contenitori di rifiuti se pieni o al termine della seduta.

4.2 Giornaliera (al termine della giornata)
- Pulizia e disinfezione dei pavimenti di tutte le aree (sale operative, corridoi, sala attesa, servizi igienici).
- Sanificazione completa dei servizi igienici (pavimento, pareti fino a 2 m, sanitari, rubinetteria, specchi, dispenser).
- Svuotamento e sanificazione dei raccoglitori dei rifiuti.
- Pulizia e disinfezione del piano dell'accettazione, delle sedie della sala attesa, degli interruttori della luce, delle maniglie delle porte.
- Registrazione sul registro delle pulizie.

4.3 Settimanale
- Pulizia approfondita di tutte le aree, inclusi angoli, battiscopa, davanzali, mensole, armadi (superficie esterna).
- Pulizia delle finestre e delle tende/veneziane.
- Pulizia e disinfezione delle poltrone e delle sedie in pelle/vinile.
- Verifica e pulizia dei filtri delle bocchette dell'aria condizionata.

4.4 Mensile
- Disinfezione delle pareti (almeno fino a 2 m di altezza) nelle sale operative.
- Pulizia a fondo dei pavimenti con macchina lavasciuga o prodotto specifico per la tipologia del pavimento.
- Verifica delle condizioni delle superfici: segnalazione di rotture, crepe o superfici non sanificabili al Responsabile della Manutenzione.

4.5 Annuale
- Sanificazione profonda dell'intera struttura, incluso il trattamento antilegionella delle linee idriche.
- Pulizia di lampadari, plafoniere, soffitti.

5. DPI DURANTE LE OPERAZIONI DI PULIZIA
- Guanti in lattice o nitrile spessi resistenti ai prodotti chimici.
- Mascherina di protezione delle vie respiratorie (almeno chirurgica).
- Camice monouso o grembiule impermeabile.
- Calzari monouso nelle sale operative.
- Occhiali protettivi se si utilizzano prodotti con rischio di schizzi.

6. REGISTRO DELLE PULIZIE
Ogni intervento di pulizia e registrato su apposito modulo con: data, ora di inizio e fine, area trattata, prodotti utilizzati, nome dell'operatore e firma. Il registro e conservato per almeno 1 anno ed e disponibile per il GdV.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        31: f"""PROCEDURA PER LA PROTEZIONE DAGLI INCIDENTI DA ESPOSIZIONE A MATERIALE BIOLOGICO
Cod. Requisito 1A.06.02.03 - REV. 1/{anno}

{intestazione}
1. SCOPO E CAMPO DI APPLICAZIONE
La presente procedura definisce le misure preventive e le azioni immediate da adottare in caso di incidente da esposizione occupazionale a materiale biologico (sangue, saliva, altri liquidi biologici) presso lo studio {nome}, in conformita al D.lgs 81/2008 (Titolo X - Agenti biologici), alla Circolare Ministeriale n. 56 del 23/12/1998 e alle Linee Guida per la gestione post-esposizione a HIV, HBV, HCV.

2. FATTORI DI RISCHIO NELL'ATTIVITA ODONTOIATRICA
- Puntura accidentale con ago da anestesia o strumento canalare
- Taglio con strumento tagliente (sonde, scalers, bisturi)
- Schizzo di sangue o saliva sulle mucose (congiuntiva, mucosa nasale, bocca)
- Schizzo su cute non integra (ferite, abrasioni, eczema)
Il rischio di sieroconversione dopo esposizione percutanea singola e: HBV 6-30%, HCV 0,5-2%, HIV 0,3%.

3. MISURE DI PREVENZIONE PRIMARIA (obbligatorie per tutto il personale)
3.1 Dispositivi di Protezione Individuale
- Guanti monouso in nitrile o lattice ad ogni contatto con pazienti e materiali biologici
- Doppio guanto per procedure ad alto rischio o con pazienti infetti noti
- Mascherina di tipo IIR o FFP2/FFP3 per procedure che generano aerosol
- Occhiali protettivi o visiera per protezione delle mucose
- Camice monouso impermeabile

3.2 Comportamenti Sicuri
- MAI reincappucciare gli aghi con entrambe le mani (se necessario, usare il metodo a una mano o il dispositivo sicuro)
- Smaltire aghi, bisturi e oggetti taglienti IMMEDIATAMENTE dopo l'uso nei contenitori rigidi per rifiuti taglienti, senza separarli dalla siringa
- Non sovrariempire i contenitori rigidi (massimo 3/4 della capacita)
- Mantenere il campo operatorio ordinato durante le procedure

3.3 Vaccinazioni
- Vaccinazione anti-HBV obbligatoria per il personale a rischio (D.lgs 81/2008)
- Documentazione del titolo anticorpale anti-HBs conservata in cartella del personale
- Aggiornamento della vaccinazione antitetanica

4. PROCEDURA IN CASO DI PUNTURA ACCIDENTALE O TAGLIO
4.1 Azioni Immediate (entro i primi 5 minuti)
1. Interrompere l'attivita e comunicare l'incidente al collega piu vicino.
2. Rimuovere i guanti.
3. Lasciare defluire liberamente il sangue dalla ferita per qualche secondo (NON premere, NON succhiare).
4. Lavare abbondantemente con acqua corrente e sapone per almeno 5 minuti.
5. Disinfettare con soluzione di ipoclorito di sodio al 5% o con soluzione alcolica al 70-90%; applicare per almeno 3 minuti.
6. Coprire la ferita con cerotto sterile.

4.2 Azioni Successive (entro 1-2 ore)
7. Identificare il paziente fonte: richiedere, con il suo consenso, l'esecuzione di test sierologici (HBsAg, anti-HCV, HIV Ab/Ag) oppure verificare se tali dati sono gia disponibili.
8. Recarsi al Pronto Soccorso piu vicino o al Centro Malattie Infettive di riferimento entro 1-2 ore dall'incidente (la profilassi post-esposizione per HIV e massimamente efficace se iniziata entro 2 ore).
9. Comunicare al medico del PS: tipo di strumento, tipo di paziente fonte, profondita della ferita, DPI indossati.
10. Seguire le indicazioni del medico per la profilassi post-esposizione (PEP) per HIV e la profilassi per HBV (immunoglobuline specifiche se non immune).

4.3 Adempimenti Amministrativi
11. Compilare la denuncia di infortunio sul lavoro (all'INAIL entro 2 giorni dall'incidente per infortuni >3 giorni, entro il giorno successivo per infortuni con prognosi > 30 giorni o mortali).
12. Registrare l'evento nel Registro degli Infortuni.
13. Compilare il Modulo Segnalazione Evento Avverso (cfr. Documento 32).
14. Effettuare il follow-up sierologico: a 45 giorni, 3 mesi e 6 mesi dall'esposizione.

5. PROCEDURA IN CASO DI SCHIZZO SU MUCOSE O OCCHI
1. Sciacquare abbondantemente con acqua corrente o soluzione fisiologica sterile per almeno 15 minuti.
2. Per gli occhi: irrigazione con soluzione fisiologica, tenendo le palpebre aperte.
3. NON usare disinfettanti sulle mucose.
4. Recarsi al Pronto Soccorso o al Centro Malattie Infettive.
5. Seguire le stesse procedure amministrative previste per la puntura accidentale.

6. FORMAZIONE E AGGIORNAMENTO
Il personale riceve formazione specifica sulla gestione del rischio biologico all'assunzione e aggiornamento annuale. La formazione include: riconoscimento dei rischi, uso corretto dei DPI, procedure di risposta all'incidente, adempimenti normativi.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",

        32: f"""SISTEMA PER L'IDENTIFICAZIONE E SEGNALAZIONE DI NEAR MISS, EVENTI AVVERSI ED EVENTI SENTINELLA
Cod. Requisito 1A.06.02.04 - REV. 1/{anno}

{intestazione}
1. SCOPO E RIFERIMENTI NORMATIVI
Il presente sistema definisce le modalita con cui lo studio {nome} identifica, segnala, registra e analizza i near miss, gli eventi avversi e gli eventi sentinella, al fine di migliorare la sicurezza del paziente e prevenire il ripetersi degli eventi, in conformita alla Legge 8 marzo 2017, n. 24 (art. 1 e 2), al D.A. 9 gennaio 2024 n. 20 e alle Raccomandazioni Ministeriali per la sicurezza del paziente.

2. DEFINIZIONI
Near miss (mancato incidente): evento o situazione che avrebbe potuto causare un danno al paziente, all'operatore o alla struttura, ma che per caso o per un intervento tempestivo non ha determinato conseguenze. E il piu prezioso indicatore predittivo di rischio.
Evento avverso: evento inatteso, non desiderato e non intenzionale che ha causato o poteva causare un danno al paziente durante o in conseguenza dell'assistenza sanitaria. Puo essere prevenibile (errore) o non prevenibile (complicanza inevitabile).
Evento sentinella: evento avverso di particolare gravita, inaspettato, che causa la morte o un danno grave e permanente al paziente. Richiede analisi approfondita con metodo Root Cause Analysis (RCA).
Incidente: evento che ha causato un danno, anche minimo, al paziente o all'operatore.

3. CULTURA DELLA SEGNALAZIONE
Lo studio promuove una cultura non punitiva della segnalazione: la segnalazione di un near miss o di un evento avverso non ha finalita disciplinari, ma e volta esclusivamente al miglioramento della sicurezza. Il personale e incoraggiato a segnalare liberamente qualsiasi evento o situazione a rischio.

4. PROCEDURA DI SEGNALAZIONE
4.1 Chi Deve Segnalare
Tutto il personale dello studio (clinici, assistenti, personale amministrativo) che osserva o e coinvolto in un near miss, evento avverso o evento sentinella.

4.2 Come Segnalare
La segnalazione avviene tramite la compilazione del Modulo di Segnalazione, disponibile in formato cartaceo presso la postazione di sterilizzazione e in formato digitale sul sistema gestionale. Il modulo raccoglie:
- Data, ora e luogo dell'evento
- Tipo di evento (near miss / evento avverso / evento sentinella)
- Descrizione dettagliata di quanto accaduto
- Pazienti/operatori coinvolti (anonimizzati nell'analisi aggregata)
- Fattori che hanno contribuito all'evento o che ne hanno prevenuto le conseguenze
- Suggerimenti per la prevenzione

4.3 A Chi Segnalare
La segnalazione e consegnata al Responsabile Sanitario o al Direttore Tecnico, che ne accusa ricevuta.

5. ANALISI E GESTIONE DEGLI EVENTI
5.1 Near Miss ed Eventi Avversi
Il Responsabile Sanitario analizza la segnalazione entro 5 giorni lavorativi, identificando:
- Le cause immediate (errore umano, guasto tecnico, problema di comunicazione, fattore organizzativo)
- Le cause radice (perche le cause immediate si sono verificate)
- Le azioni correttive e preventive da adottare

5.2 Evento Sentinella
In caso di evento sentinella, il Responsabile Sanitario attiva immediatamente la Root Cause Analysis (RCA) coinvolgendo tutto il personale interessato. L'analisi segue la metodologia del diagramma causa-effetto (Ishikawa) o dell'albero degli eventi. I risultati e le azioni correttive sono documentati e comunicati all'ASP {asp} secondo le procedure vigenti.

6. REGISTRO DEGLI EVENTI E MONITORAGGIO
Tutti gli eventi segnalati sono registrati in ordine cronologico con: numero progressivo, data, tipo di evento, descrizione sintetica, cause identificate, azioni correttive adottate, esito della verifica dell'efficacia delle azioni.
Il Responsabile Sanitario effettua una revisione semestrale dei dati aggregati per identificare trend e aree di rischio ricorrenti. I risultati sono discussi nelle riunioni di staff e utilizzati per aggiornare il Piano di Gestione del Rischio (cfr. Documento 29).

7. COMUNICAZIONE CON IL PAZIENTE IN CASO DI EVENTO AVVERSO
In caso di evento avverso che abbia causato un danno al paziente, il Responsabile Sanitario informa il paziente in modo trasparente, tempestivo e con linguaggio comprensibile, spiegando cosa e accaduto, le conseguenze per la sua salute e le misure adottate. Questa comunicazione avviene nel rispetto della Legge 24/2017 e non costituisce di per se ammissione di responsabilita.

Data di adozione: {oggi}
Firma Responsabile Sanitario: {tit} ______________________
Prossima revisione: ___/___/______""",
    }

    temi_tecnici = {
        13: ("caratteristiche ambientali e accessibilita", "L. 13/1989, DPR 503/1996, DPR 380/2001, DM 236/1989",
             f"""Certificato di agibilita / abitabilita rilasciato dal Comune di {s.get('comune','').title()}.
Planimetria dei locali con indicazione delle destinazioni d'uso di ogni ambiente, superfici in mq e altezze.
Dichiarazione di conformita alle norme sull'accessibilita per persone con disabilita.
VEDI ALLEGATO: Planimetria dello studio allegata al presente documento."""),
        14: ("protezione antincendio", "DM 10/03/1998, D.lgs 81/2008, DM 3/8/2015",
             "Certificato di Prevenzione Incendi (CPI) rilasciato dal Comando VV.FF. competente, oppure dichiarazione di esenzione per strutture sotto soglia di rischio. Registro dei controlli periodici degli estintori (semestrale). Planimetria con indicazione delle vie di esodo, delle uscite di sicurezza, degli estintori e degli idranti. Verbali di manutenzione annuale dell'impianto di rilevazione fumi (ove presente). Piano di emergenza e di evacuazione (cfr. Documento 6)."),
        15: ("protezione acustica", "L. 447/1995, DPCM 5/12/1997, DM 11/11/2005",
             "Classificazione acustica dell'edificio attestante il rispetto dei limiti di immissione e di emissione sonora previsti per le strutture sanitarie. Eventuale perizia fonometrica redatta da tecnico competente in acustica ambientale iscritto all'elenco regionale. Relazione tecnica attestante la conformita alla classe acustica III (strutture sanitarie) per i locali destinati ad attivita clinica."),
        16: ("sicurezza elettrica e continuita elettrica", "DM 37/2008, norme CEI 64-8 (in particolare Vol. 7-710 per locali medici), D.lgs 81/2008",
             "Dichiarazione di conformita dell'impianto elettrico ai sensi del DM 37/2008, con allegati i progetti e gli schemi. Verbali delle verifiche periodiche biennali dell'impianto elettrico eseguite da organismo abilitato (DPR 462/2001). Verbale di verifica dell'impianto di messa a terra (DPR 462/2001). Schema unifilare aggiornato dell'impianto elettrico. Documentazione relativa al gruppo di continuita (UPS) o al gruppo elettrogeno, ove presente."),
        17: ("sicurezza anti-infortunistica", "D.lgs 81/2008 e s.m.i., D.lgs 106/2009",
             f"Documento di Valutazione dei Rischi (DVR) aggiornato, redatto dal datore di lavoro con il RSPP e il medico competente. Nomina del Responsabile del Servizio di Prevenzione e Protezione (RSPP). Nomina del Medico Competente (se prevista). Attestati di formazione sulla sicurezza del personale (art. 36 e 37 D.lgs 81/2008). Registro degli infortuni aggiornato. Verbali delle riunioni periodiche di sicurezza (art. 35 D.lgs 81/2008). Piano di emergenza e evacuazione."),
        18: ("protezione da radiazioni ionizzanti", "D.lgs 101/2020, Direttiva 2013/59/Euratom",
             "Comunicazione/autorizzazione all'utilizzo di apparecchiature radiogene (Comune o ASP, secondo la potenza). Nulla osta dell'ARPA Sicilia per l'esercizio dell'attivita con sorgenti di radiazioni. Relazione scritta dell'Esperto in Radioprotezione (RP) con valutazione del rischio e indicazioni di protezione. Verbali di sorveglianza fisica della radioprotezione (semestrale o annuale). Dosimetrie personali (badge) del personale classificato come esposto (Categoria A o B). Registro delle dosi erogate ai pazienti."),
        19: ("eliminazione barriere architettoniche", "L. 13/1989, DPR 503/1996, DM 236/1989, L.R. Sicilia 6/2010",
             f"Dichiarazione di conformita alle norme sull'accessibilita. Planimetria con indicazione dei percorsi accessibili ai disabili. Documentazione attestante la presenza di: rampa o ascensore per il superamento di dislivelli (pendenza max 8%), porte con larghezza netta >= 80 cm sulle vie principali, spazio di manovra per sedia a rotelle (cerchio di diametro 150 cm) nei punti di svolta, servizio igienico per disabili con spazio di manovra, maniglioni di sostegno, WC a parete con bordo a 50 cm. Segnaletica accessibile."),
        20: ("smaltimento dei rifiuti sanitari", "DPR 254/2003, D.lgs 152/2006, D.lgs 116/2020",
             "Registro di carico e scarico dei rifiuti speciali (per produttori > 10 kg/giorno, in alternativa formulari FIR). Contratto con ditta autorizzata al trasporto e smaltimento dei rifiuti sanitari pericolosi a rischio infettivo (CER 18.01.03*) e non pericolosi (CER 18.01.04). Formulari di identificazione del rifiuto (FIR) compilati ad ogni ritiro. Schede di sicurezza dei prodotti chimici utilizzati. Procedure per la classificazione, il deposito temporaneo e lo smaltimento dei rifiuti."),
        21: ("condizioni microclimatiche", "D.lgs 81/2008 (art. 63 e All. IV), UNI EN ISO 7730:2006",
             "Documentazione dell'impianto di riscaldamento e/o raffrescamento: progetto, conformita alle norme, libretto dell'impianto. Registro di manutenzione degli impianti di climatizzazione (pulizia filtri, verifica funzionale semestrale). Dichiarazione del tecnico abilitato attestante il rispetto dei parametri microclimatici: temperatura invernale 20-22 degC, estiva 24-26 degC; umidita relativa 40-60%; velocita dell'aria <0,15 m/s negli ambienti climatizzati. Registro F-GAS per impianti con fluido refrigerante."),
        22: ("impianti di distribuzione dei gas", "D.lgs 46/1997, UNI EN ISO 7396-1, D.lgs 81/2008",
             "Dichiarazione di conformita dell'impianto gas medicali (se presente impianto centralizzato di N2O o O2). Contratto di fornitura e schede di sicurezza dei gas medicali utilizzati. Certificato di collaudo e verifica dell'impianto. Verbali di manutenzione periodica. Procedure per la gestione sicura delle bombole (stoccaggio verticale, catene di sicurezza, ventilazione del locale). Se non e presente impianto centralizzato: dichiarazione di utilizzo esclusivo di bombole portatili con procedure di sicurezza documentate."),
        23: ("materiali esplodenti", "D.lgs 272/2013, T.U.L.P.S.",
             f"Dichiarazione del Responsabile Sanitario attestante che nello studio {nome} non sono presenti, non vengono utilizzati e non vengono stoccati materiali esplodenti o detonanti nell'ambito dell'attivita sanitaria odontoiatrica. I materiali radiografici e i gas medicali sono gestiti secondo le rispettive normative specifiche (cfr. Documenti 18 e 22)."),
        24: ("protezione antisismica", "DM 14/01/2008 (NTC 2008), DM 17/01/2018 (NTC 2018), OPCM 3274/2003",
             f"Classificazione sismica del Comune di {s.get('comune','').title()} ({s.get('provincia','').upper()}) secondo la mappa di pericolosita sismica INGV: Zona sismica ______. Documentazione tecnica dell'edificio (progetto strutturale, relazione geologica, collaudo statico) attestante la conformita alle norme tecniche per le costruzioni vigenti al momento della costruzione/ristrutturazione. Eventuale certificazione di vulnerabilita sismica o adeguamento sismico. Per edifici esistenti antecedenti al 1974: dichiarazione del tecnico abilitato."),
    }

    altri = {
        3: testi[3],
        4: testi[4],
        5: testi[5],
        7: testi[7],
        8: testi[8],
        9: testi[9],
        11: testi[11],
        12: testi[12],
        25: testi[25],
        26: testi[26],
        27: testi[27],
        28: testi[28],
        30: testi[30],
        31: testi[31],
        32: testi[32],
    }

    for n_t, (tema, norma, docs_list) in temi_tecnici.items():
        altri[n_t] = f"""DOCUMENTAZIONE TECNICA - {tema.upper()}
Cod. Requisito 1A.03.05.{str(n_t-12).zfill(2)} - REV. 1/{anno}

{intestazione}
NORMATIVA DI RIFERIMENTO
{norma}

DOCUMENTAZIONE DISPONIBILE E DICHIARAZIONE DI CONFORMITA
{docs_list}

DICHIARAZIONE
Il sottoscritto {tit}, Responsabile Sanitario dello studio {nome}, con sede in {adr},

DICHIARA

che la struttura possiede i requisiti previsti dalle vigenti leggi in materia di {tema}, come da documentazione allegata e disponibile per la verifica del Gruppo di Valutazione (GdV) dell'ASP {asp}.
La documentazione elencata e conservata presso lo studio ed e integralmente disponibile per l'ispezione.

Luogo e data: {s.get('comune','').title()}, {oggi}

Firma Responsabile Sanitario: ______________________
{tit}"""

    tutti = {**testi, **altri}
    return tutti.get(num, f"""DOCUMENTO {num}
Cod. {DOCS[num-1][2]} - REV. 1/{anno}

{intestazione}
Documento da compilare a cura del Responsabile della struttura.

Data: {oggi}    Firma: ______________________""")



def genera_pdf(s):
    # Normalize capitalization
    s = dict(s)
    s['denominazione'] = s['denominazione'].title()
    s['titolare']      = s['titolare'].title()
    s['comune']        = s['comune'].title()
    s['indirizzo']     = s['indirizzo'].title()
    s['provincia']     = s['provincia'].upper()
    if s.get('direttore') and s['direttore'].strip():
        s['direttore'] = s['direttore'].title()
    else:
        s['direttore'] = s['titolare']
    if s.get('resp_manut') and s['resp_manut'].strip():
        s['resp_manut'] = s['resp_manut'].title()
    else:
        s['resp_manut'] = s['titolare']

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    pg = [0]

    def footer(n):
        c.setFont('Helvetica', 7)
        c.setFillColor(GRIGIO_L)
        c.line(2*cm, 1.2*cm, W-2*cm, 1.2*cm)
        c.drawRightString(W-2*cm, 0.7*cm, str(n))
        c.setFillColor(colors.black)

    # ── PAGINA 1-2: TABELLA ALL.A1 ──
    def draw_row(i, num, desc, cod, y):
        RH = 0.68*cm
        c.setFillColor(colors.white if i%2==0 else colors.HexColor('#F5F5F5'))
        c.rect(2*cm, y-RH, W-4*cm, RH, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor('#CCCCCC'))
        c.setLineWidth(0.25)
        c.rect(2*cm, y-RH, W-4*cm, RH, fill=0)
        c.line(W-5.4*cm, y, W-5.4*cm, y-RH)
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 8)
        trunc = f'{num}. {desc}'
        max_w = W - 4*cm - 3.8*cm
        while c.stringWidth(trunc, 'Helvetica', 8) > max_w:
            trunc = trunc[:-1]
        if trunc != f'{num}. {desc}':
            trunc += '...'
        c.drawString(2.1*cm, y-RH*0.62, trunc)
        c.setFont('Helvetica-Oblique', 8)
        c.drawString(W-5.3*cm, y-RH*0.62, cod)
        return y - RH

    # Header pag 1
    c.setFont('Helvetica-Bold', 10)
    c.rect(2*cm, H-3.4*cm, 2.2*cm, 0.8*cm)
    c.drawString(2.15*cm, H-3.0*cm, 'ALL. A1')
    titolo = 'Per struttura non residenziale semplici monopresidio'
    tx = W/2 + 0.5*cm
    tw = c.stringWidth(titolo,'Helvetica-Bold',10)
    c.drawCentredString(tx, H-2.7*cm, titolo)
    c.line(tx-tw/2, H-2.82*cm, tx+tw/2, H-2.82*cm)
    c.setFont('Helvetica',8.5)
    c.drawCentredString(tx, H-3.2*cm,'(vedi definizioni art. 2 e classificazione art. 3 del D.A. 9 gennaio 2024 n. 20).')
    c.setFont('Helvetica-Bold',9)
    c.drawString(2*cm,H-3.85*cm,"Per una puntuale applicazione di ciascun requisito fare riferimento ai subcodici riportati nell'allegato")
    c.drawString(2*cm,H-4.3*cm,"A1 del D.A. 9 gennaio 2024 n. 20.")
    gdv=["Il Responsabile della struttura mettera a disposizione del GdV prima della visita i seguenti",
         "documenti previsti dai requisiti generali per l'autorizzazione di cui all'allegato A1 al decreto",
         "assessoriale 09 gennaio 2024 n. 20 (G.U.R.S. 26 gennaio 2024, n. 5, S.O. n. 4)"]
    bh=len(gdv)*0.41*cm+0.35*cm
    c.rect(2*cm,H-5.1*cm,W-4*cm,bh)
    yg=H-4.97*cm
    c.setFont('Helvetica-Bold',8.5)
    for l in gdv:
        c.drawString(2.2*cm,yg,l); yg-=0.41*cm
    c.setFillColor(colors.black)
    c.rect(2*cm,H-5.6*cm,W-4*cm,0.5*cm,fill=1)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold',9.5)
    c.drawCentredString(2*cm+(W-4*cm-3.5*cm)/2,H-5.37*cm,'DOCUMENTO')
    c.drawString(W-5.3*cm,H-5.37*cm,'Cod. Requisito')

    y = H-5.6*cm
    for i,(num,desc,cod) in enumerate(DOCS):
        if y - 0.68*cm < 1.8*cm:
            footer(pg[0]+1); pg[0]+=1; c.showPage()
            y = H-2.0*cm
            c.setFillColor(colors.black)
        y = draw_row(i,num,desc,cod,y)

    footer(pg[0]+1); pg[0]+=1; c.showPage()

    # ── 32 DOCUMENTI ──
    for num,desc,cod in DOCS:
        # COPERTINA
        c.setFillColor(BLU_CIELO)
        c.rect(0,0,W,H,fill=1,stroke=0)
        BX=W*0.38; BW=W-BX-1.5*cm; BY=2*cm; BH=H-BY-3*cm
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.HexColor('#8FA0B5'))
        c.setLineWidth(0.8)
        c.rect(BX,BY,BW,BH,fill=1)
        NH=3.8*cm
        c.setFillColor(BLU_NAVY)
        c.rect(BX,BY+BH-NH,BW,NH,fill=1,stroke=0)
        c.setFillColor(colors.white)
        sy=BY+BH-0.9*cm
        for line in [s['denominazione'], s['titolare'] + ' (Resp.)', s['direttore'] + ' (Dir.Tec.)', s['indirizzo'], s['comune']+' ('+s['provincia']+')']:
            if not line: continue
            c.setFont('Helvetica-Bold' if sy>BY+BH-1.5*cm else 'Helvetica',
                      9 if sy>BY+BH-1.5*cm else 8.5)
            c.drawCentredString(BX+BW/2,sy,line[:42]); sy-=0.5*cm
        cy=BY+BH-NH-0.9*cm
        c.setFillColor(colors.black)
        c.setFont('Helvetica-Bold',11)
        c.drawString(BX+0.5*cm,cy,f'DOCUMENTO {num}:'); cy-=0.48*cm
        c.setFont('Helvetica',9)
        words=desc.split(); line='';
        for w in words:
            test=(line+' '+w).strip()
            if c.stringWidth(test,'Helvetica',9)<BW-1*cm: line=test
            else:
                if cy<BY+3.5*cm: break
                c.drawString(BX+0.5*cm,cy,line); cy-=0.38*cm; line=w
        if line and cy>BY+3.5*cm:
            c.drawString(BX+0.5*cm,cy,line); cy-=0.65*cm
        c.setFont('Helvetica-Bold',10)
        c.drawString(BX+0.5*cm,cy,'Cod. Requisito'); cy-=0.42*cm
        c.drawString(BX+0.5*cm,cy,cod)
        c.setFont('Helvetica-Bold',9)
        c.drawString(BX+0.5*cm,BY+1.6*cm,f'REV. 1/{s["anno"]}')
        c.setFillColor(ORO)
        c.rect(BX,BY,BW,0.18*cm,fill=1,stroke=0)
        c.setFillColor(colors.HexColor('#8B6740'))
        c.setFont('Helvetica',7.5)
        c.drawString(BX+0.5*cm,BY+0.8*cm,s['titolare'].upper())
        footer(pg[0]+1); pg[0]+=1; c.showPage()

        # PAGINE CONTENUTO
        testo = get_testo(num,s)
        righe = testo.split('\n')

        def hdr():
            c.setFillColor(BLU_NAVY)
            c.rect(2*cm,H-2.0*cm,W-4*cm,0.65*cm,fill=1,stroke=0)
            c.setFillColor(colors.white)
            c.setFont('Helvetica-Bold',7.5)
            c.drawString(2.2*cm,H-1.65*cm,f"{s['denominazione'][:55]}  |  Documento {num} di 32")
            c.setFillColor(colors.black)
            return H-2.4*cm

        y=hdr()
        for raw in righe:
            riga=raw.strip()
            if not riga:
                y-=0.2*cm
                if y<2.0*cm:
                    footer(pg[0]+1); pg[0]+=1; c.showPage(); y=hdr()
                continue
            isH=(riga==riga.upper() and len(riga)>3 and not riga[0].isdigit()) or \
                riga.endswith(':') or (len(riga)<70 and riga[:2].rstrip('.').isdigit())
            font='Helvetica-Bold' if isH else 'Helvetica'
            sz=9.0 if isH else 8.5; lh=0.42*cm if isH else 0.37*cm
            words=riga.split(); cur=''; wrapped=[]
            for w in words:
                t=(cur+' '+w).strip()
                if c.stringWidth(t,font,sz)<W-4.2*cm: cur=t
                else:
                    if cur: wrapped.append(cur)
                    cur=w
            if cur: wrapped.append(cur)
            bh=len(wrapped)*lh+(0.1*cm if isH else 0)
            if y-bh<2.0*cm:
                footer(pg[0]+1); pg[0]+=1; c.showPage(); y=hdr()
            if isH: y-=0.07*cm
            for wl in wrapped:
                c.setFont(font,sz); c.drawString(2*cm,y,wl); y-=lh
            if isH: y-=0.07*cm

        # ── PAGINA PLANIMETRIA (solo per documento 13) ──
        if num == 13 and s.get('planimetria'):
            try:
                plan_data = s['planimetria']
                plan_name = s.get('planimetria_name', '')
                if plan_name.lower().endswith('.pdf'):
                    # PDF planimetria: usa pypdf per estrarre come immagine
                    try:
                        import pypdf, subprocess, tempfile, os
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tf:
                            tf.write(plan_data)
                            tf_path = tf.name
                        out_path = tf_path.replace('.pdf', '_plan')
                        subprocess.run(['pdftoppm', '-jpeg', '-r', '150', '-f', '1', '-l', '1',
                                         tf_path, out_path], capture_output=True)
                        img_files = sorted([f for f in os.listdir(os.path.dirname(out_path))
                                           if os.path.basename(out_path) in f])
                        if img_files:
                            img_path = os.path.join(os.path.dirname(out_path), img_files[0])
                            plan_img = Image.open(img_path)
                        else:
                            plan_img = None
                        os.unlink(tf_path)
                    except Exception:
                        plan_img = None
                else:
                    plan_img = Image.open(io.BytesIO(plan_data))

                if plan_img:
                    # Pagina planimetria
                    c.setFillColor(colors.white)
                    c.rect(0, 0, W, H, fill=1, stroke=0)
                    # Header
                    c.setFillColor(BLU_NAVY)
                    c.rect(2*cm, H-2.0*cm, W-4*cm, 0.65*cm, fill=1, stroke=0)
                    c.setFillColor(colors.white)
                    c.setFont('Helvetica-Bold', 7.5)
                    c.drawString(2.2*cm, H-1.65*cm,
                        f"{s['denominazione'][:55]}  |  Documento 13 - ALLEGATO: Planimetria")
                    c.setFillColor(colors.black)
                    # Titolo
                    c.setFont('Helvetica-Bold', 10)
                    c.drawCentredString(W/2, H-2.8*cm, "ALLEGATO - PLANIMETRIA DELLO STUDIO")
                    c.setFont('Helvetica', 8)
                    c.drawCentredString(W/2, H-3.3*cm,
                        f"Studio: {s['denominazione']} | Sede: {s['indirizzo'].title()}, {s['comune'].title()} ({s['provincia'].upper()})")
                    # Immagine centrata
                    img_w, img_h = plan_img.size
                    max_w = W - 4*cm
                    max_h = H - 6*cm
                    ratio = min(max_w / img_w, max_h / img_h)
                    draw_w = img_w * ratio
                    draw_h = img_h * ratio
                    x_img = (W - draw_w) / 2
                    y_img = (H - draw_h) / 2 - 0.5*cm
                    img_buf = io.BytesIO()
                    plan_img.save(img_buf, format='PNG')
                    img_buf.seek(0)
                    c.drawImage(ImageReader(img_buf), x_img, y_img, draw_w, draw_h,
                                preserveAspectRatio=True)
                    # Bordo
                    c.setStrokeColor(BLU_NAVY)
                    c.setLineWidth(1)
                    c.rect(x_img-0.2*cm, y_img-0.2*cm, draw_w+0.4*cm, draw_h+0.4*cm, fill=0)
                    footer(pg[0]+1); pg[0]+=1; c.showPage()
            except Exception as e:
                pass  # Se la planimetria non si inserisce, si ignora silenziosamente

        footer(pg[0]+1); pg[0]+=1; c.showPage()

    c.save()
    buf.seek(0)
    return buf.getvalue(), pg[0]


# ══════════════════════════════════════════
# INTERFACCIA STREAMLIT
# ══════════════════════════════════════════

# Session state inizializzato SUBITO, prima di qualsiasi widget
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes    = None
    st.session_state.pdf_filename = None
    st.session_state.pdf_pages    = None

st.title("🦷 Generatore Allegato A1")
st.subheader("Strutture Non Residenziali Semplici Monopresidio — Regione Siciliana")
st.markdown("*A cura della Dr.ssa Barbara Sabiu / AIO Palermo*")
st.divider()

with st.form("dati_studio"):
    st.subheader("📋 Dati dello Studio")

    col1, col2 = st.columns(2)
    with col1:
        denominazione = st.text_input("Denominazione / Ragione Sociale *",
                                       placeholder="es. Studio Odontoiatrico Bianchi S.r.l.")
        titolare      = st.text_input("Responsabile Sanitario / Titolare *",
                                       placeholder="es. Dott.ssa Maria Bianchi")
        direttore     = st.text_input("Direttore Tecnico (se diverso dal titolare)",
                                       placeholder="es. Dott. Marco Rossi")
        resp_manut    = st.text_input("Responsabile Manutenzione",
                                       placeholder="es. Geom. Luca Verdi")
    with col2:
        indirizzo  = st.text_input("Indirizzo sede *", placeholder="es. Via Roma 15")
        comune     = st.text_input("Comune *",         placeholder="es. Palermo")
        provincia  = st.text_input("Provincia (sigla) *", placeholder="PA", max_chars=2)
        cap        = st.text_input("CAP *",            placeholder="90100", max_chars=5)

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        asp_options = ["ASP Agrigento","ASP Caltanissetta","ASP Catania","ASP Enna",
                       "ASP Messina","ASP Palermo","ASP Ragusa","ASP Siracusa","ASP Trapani"]
        asp       = st.selectbox("ASP di riferimento *", asp_options, index=5)
        albo      = st.text_input("N. iscrizione Albo Odontoiatri *", placeholder="es. PA/1234")
        cf        = st.text_input("Codice Fiscale / P.IVA *", placeholder="es. 12345678901")
    with col4:
        telefono  = st.text_input("Telefono", placeholder="es. 091 123456")
        pec       = st.text_input("PEC / Email ufficiale", placeholder="studio@pec.it")
        anno      = st.text_input("Anno", value=str(date.today().year), max_chars=4)

    st.markdown("---")
    st.subheader("🏥 Composizione della Struttura")
    col5, col6, col7 = st.columns(3)
    with col5:
        n_riuniti   = st.number_input("N. riuniti odontoiatrici *", min_value=1, max_value=20, value=1, step=1)
        n_sale_med  = st.number_input("N. sale mediche/visita",     min_value=0, max_value=10, value=0, step=1)
        n_sale_rx   = st.number_input("N. sale radiologiche",       min_value=0, max_value=5,  value=1, step=1)
    with col6:
        n_sterile   = st.number_input("N. locali sterilizzazione",  min_value=0, max_value=5,  value=1, step=1)
        n_attesa    = st.number_input("N. sale attesa",             min_value=0, max_value=5,  value=1, step=1)
        n_bagni     = st.number_input("N. servizi igienici",        min_value=0, max_value=10, value=1, step=1)
    with col7:
        ha_scanner  = st.checkbox("Scanner intraorale",    value=True)
        ha_opt      = st.checkbox("Ortopantomografo (OPT)",value=True)
        ha_cbct     = st.checkbox("CBCT / 3D",             value=False)
        ha_stampante3d = st.checkbox("Stampante 3D",       value=False)
        ha_cad      = st.checkbox("CAD/CAM / Fresatrice",  value=False)

    st.markdown("---")
    st.subheader("📐 Planimetria dello Studio")
    planimetria_file = st.file_uploader(
        "Carica la planimetria (PDF, PNG, JPG) - verra allegata al Documento 13",
        type=["pdf", "png", "jpg", "jpeg"],
        help="La planimetria apparira come pagina allegata al Documento 13 (Caratteristiche ambientali)"
    )

    st.markdown("---")
    st.caption("I campi con * sono obbligatori")
    submitted = st.form_submit_button("📄 Genera PDF Allegato A1",
                                       use_container_width=True, type="primary")

if submitted:
    campi_mancanti = []
    if not denominazione: campi_mancanti.append("Denominazione")
    if not titolare:      campi_mancanti.append("Responsabile Sanitario")
    if not indirizzo:     campi_mancanti.append("Indirizzo")
    if not comune:        campi_mancanti.append("Comune")
    if not provincia:     campi_mancanti.append("Provincia")
    if not cap:           campi_mancanti.append("CAP")
    if not albo:          campi_mancanti.append("N. Albo Odontoiatri")
    if not cf:            campi_mancanti.append("Codice Fiscale / P.IVA")

    if campi_mancanti:
        st.error(f"⚠️ Compila i campi obbligatori: {', '.join(campi_mancanti)}")
    else:
        s = {
            'denominazione':  denominazione,
            'titolare':       titolare,
            'direttore':      direttore,
            'resp_manut':     resp_manut or titolare,
            'indirizzo':      indirizzo,
            'comune':         comune,
            'provincia':      provincia.upper(),
            'cap':            cap,
            'asp':            asp,
            'albo':           albo,
            'cf':             cf,
            'telefono':       telefono,
            'pec':            pec,
            'anno':           anno or str(date.today().year),
            'n_riuniti':      int(n_riuniti),
            'n_sale_med':     int(n_sale_med),
            'n_sale_rx':      int(n_sale_rx),
            'n_sterile':      int(n_sterile),
            'n_attesa':       int(n_attesa),
            'n_bagni':        int(n_bagni),
            'ha_scanner':     ha_scanner,
            'ha_opt':         ha_opt,
            'ha_cbct':        ha_cbct,
            'ha_stampante3d': ha_stampante3d,
            'ha_cad':         ha_cad,
            'planimetria':    planimetria_file.read() if planimetria_file else None,
            'planimetria_name': planimetria_file.name if planimetria_file else None,
        }

        with st.spinner("⏳ Generazione PDF in corso..."):
            try:
                pdf_bytes, n_pages = genera_pdf(s)
                nome_file = denominazione.replace(' ','_').replace('/','_')[:25]
                filename  = f"AllegatoA1_{nome_file}_{date.today().strftime('%Y%m%d')}.pdf"
                st.session_state.pdf_bytes    = pdf_bytes
                st.session_state.pdf_filename = filename
                st.session_state.pdf_pages    = n_pages
            except Exception as e:
                st.error(f"❌ Errore durante la generazione: {e}")
                import traceback
                st.code(traceback.format_exc())

# ── Download button SEMPRE fuori dallo spinner ──
if st.session_state.pdf_bytes is not None:
    st.success(f"✅ PDF generato con successo! ({st.session_state.pdf_pages} pagine)")
    st.download_button(
        label="⬇️ Scarica PDF Allegato A1",
        data=st.session_state.pdf_bytes,
        file_name=st.session_state.pdf_filename,
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )
    st.info("Il PDF contiene: tabella ALL.A1 + 32 copertine + documenti precompilati con i dati del tuo studio.")

st.divider()
st.caption("Generatore Allegato A1 — Regione Siciliana | A cura della Dr.ssa Barbara Sabiu / AIO Palermo")
