import streamlit as st
import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

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

    base = {
        1: f"""DOCUMENTO DI ORGANIZZAZIONE E GESTIONE DELLE RISORSE
Cod. Requisito 1A.01.03.01 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}
Sede: {adr} | {asp_str}
{contatti}

1. SCOPO E CAMPO DI APPLICAZIONE
Il presente documento definisce l'organizzazione interna dello studio odontoiatrico, le politiche adottate per la gestione delle risorse umane, materiali e tecnologiche, e analizza i principali processi per individuare le fasi critiche in cui possono verificarsi disservizi.

2. STRUTTURA ORGANIZZATIVA
- Responsabile Sanitario / Titolare ({tit}): coordina le attivita cliniche e gestionali.
- Direttore Tecnico ({dir_}): supervisione tecnica e qualita dei processi clinici.
- Odontoiatri collaboratori: eseguono i trattamenti e si occupano della presa in carico dei pazienti.
- Igienisti dentali / ASO: supportano l'attivita clinica e garantiscono igiene e sterilizzazione.
- Personale amministrativo: gestisce accoglienza, appuntamenti e documentazione.

3. POLITICHE DI GESTIONE DELLE RISORSE
3.1 Risorse Umane - Aggiornamento ECM obbligatorio. Verifica annuale competenze.
3.2 Risorse Materiali - Manutenzione periodica attrezzature. Controllo scorte materiali sanitari.
3.3 Sicurezza - Protocolli sterilizzazione secondo normative. Formazione personale.

4. ANALISI PROCESSI E FASI CRITICHE
- Accoglienza: prenotazione, accettazione. Rischio: errori agenda. Misura: software gestionale.
- Trattamento: diagnosi, terapia. Rischio: errori clinici. Misura: check-list, protocolli.
- Sterilizzazione: pulizia, autoclave. Rischio: contaminazione. Misura: tracciabilita, test.
- Amministrazione: fatturazione, archiviazione. Rischio: perdita dati. Misura: backup.

5. MONITORAGGIO E MIGLIORAMENTO
Audit interni semestrali. Riunioni staff mensili. Analisi customer satisfaction.

Data di adozione: {oggi}    Firma Responsabile Sanitario: {tit}    Firma Direttore Tecnico: {dir_}""",

        2: f"""DOCUMENTAZIONE INERENTE IL SISTEMA INFORMATIVO
Cod. Requisito 1A.01.04.01 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. SISTEMA GESTIONALE IN USO
Lo studio adotta un sistema informatico per la gestione integrata delle attivita cliniche e amministrative: agenda elettronica, cartella clinica digitale, fatturazione, reportistica.

2. SICUREZZA DEI DATI
- Credenziali personali per ogni utente
- Backup automatico giornaliero su server/cloud certificato
- Accesso ai dati sensibili riservato al personale autorizzato (GDPR 679/2016)

3. CONFORMITA NORMATIVA
Sistema conforme al D.lgs 196/2003 e al GDPR 679/2016. Nominato il Responsabile del Trattamento Dati. I pazienti firmano il consenso al trattamento dati prima della presa in carico.

4. AGGIORNAMENTI E MANUTENZIONE
Software aggiornato periodicamente dal fornitore. Personale formato sull'utilizzo corretto. Accessi e modifiche ai dati clinici documentati.

Data di adozione: {oggi}    Firma: {tit}""",

        6: f"""PIANO PER LA GESTIONE DELLE EMERGENZE
Cod. Requisito 1A.02.02.02 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_} | Sede: {adr}

1. TIPOLOGIE DI EMERGENZA
- Medica paziente: sincope, shock anafilattico, arresto cardiaco, crisi epilettica, ipoglicemia
- Medica operatore: infortunio, esposizione a materiale biologico
- Tecnica: guasto attrezzature, interruzione energia, allagamento
- Strutturale: incendio, terremoto, evacuazione

2. DOTAZIONI DI EMERGENZA
Kit pronto soccorso, defibrillatore DAE, farmaci urgenza (adrenalina, antistaminici, glucosio), estintori.

3. PROCEDURA EMERGENZA MEDICA
1. Valutare lo stato del paziente  2. Chiamare il 118  3. Applicare protocollo BLSD
4. Non lasciare mai solo il paziente  5. Compilare modulo segnalazione evento

4. PROCEDURA DI EVACUAZIONE
Attivare allarme, guidare pazienti verso uscite di sicurezza, chiamare 115, non usare ascensori, radunarsi nel punto di raccolta esterno.

5. FORMAZIONE
Personale formato periodicamente. Esercitazioni evacuazione almeno una volta l'anno.

Data di adozione: {oggi}    Firma: {tit}""",

        29: f"""PIANO AZIENDALE PER LA GESTIONE DEL RISCHIO
Cod. Requisito 1A.06.02.01 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_} | Sede: {adr}

1. SCOPO
Definire strategie e procedure per la gestione del rischio clinico e organizzativo.

2. RISCHI CLINICI IDENTIFICATI E MISURE
- Rischio infettivo: sterilizzazione, DPI, protocolli controllo infezioni
- Rischio da radiazioni: ottimizzazione dosi, DPI, sorveglianza dosimetrica
- Rischio anestesiologico: anamnesi accurata, kit emergenza, formazione BLS-D
- Rischio emorragico: anamnesi farmacologica, protocolli chirurgici
- Rischio corpi estranei: diga di gomma, filo di seta su strumenti

3. PREVENZIONE INFEZIONI CORRELATE ALL'ASSISTENZA
Igiene mani prima e dopo ogni procedura. Autoclave Classe B con test settimanali.
DPI: guanti, mascherina, occhiali, camice monouso. Decontaminazione superfici dopo ogni paziente.

4. RACCOLTA E ANALISI EVENTI AVVERSI
Segnalazione tramite apposito modulo. Analisi semestrale per identificare azioni preventive.
Risultati comunicati al personale nelle riunioni di staff.

Data di adozione: {oggi}    Firma: {tit}""",

        30: f"""PROCEDURA PER LA PULIZIA E SANIFICAZIONE DEGLI AMBIENTI
Cod. Requisito 1A.06.02.02 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. FREQUENZA DEGLI INTERVENTI
Dopo ogni paziente: decontaminazione tutte le superfici della sala trattamento.
Giornaliera: pulizia e disinfezione pavimenti, sanificazione servizi igienici.
Settimanale: pulizia approfondita di tutte le aree, armadi, finestre, arredi.
Mensile: disinfezione pareti, pulizia bocchette di areazione.

2. PRODOTTI UTILIZZATI
Disinfettante per superfici a base di cloro o perossido di idrogeno certificato per uso sanitario.
Detergente per pavimenti con azione detergente e disinfettante.

3. DPI DURANTE LE PULIZIE
Guanti resistenti ai prodotti chimici, mascherina, camice monouso.

4. REGISTRO PULIZIE
Operazioni registrate con: data, ora, operatore, aree trattate, prodotti utilizzati.

Data di adozione: {oggi}    Firma: {tit}""",

        31: f"""PROCEDURA PROTEZIONE DA INCIDENTI CON MATERIALE BIOLOGICO
Cod. Requisito 1A.06.02.03 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. MISURE PREVENTIVE
DPI sistematici: guanti monouso, mascherina, occhiali, camice.
Mai reincappucciare aghi. Smaltire immediatamente nei contenitori rigidi dedicati.

2. PROCEDURA IN CASO DI PUNTURA O TAGLIO
1. Lasciare sanguinare abbondantemente senza premere
2. Lavare con acqua corrente e sapone per almeno 5 minuti
3. Disinfettare con ipoclorito di sodio al 5% o alcol 70%
4. Segnalare immediatamente al Responsabile
5. Recarsi al Pronto Soccorso entro 1-2 ore
6. Compilare modulo denuncia infortunio

3. PROCEDURA IN CASO DI SCHIZZO SU MUCOSE/OCCHI
Lavare abbondantemente con acqua sterile per almeno 15 minuti. Recarsi al Pronto Soccorso.

4. DOCUMENTAZIONE
Ogni incidente registrato nel registro degli infortuni.

Data di adozione: {oggi}    Firma: {tit}""",

        32: f"""SISTEMA PER L'IDENTIFICAZIONE E SEGNALAZIONE DI NEAR MISS ED EVENTI AVVERSI
Cod. Requisito 1A.06.02.04 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. DEFINIZIONI
Near miss: evento che avrebbe potuto causare un danno ma non si e verificato.
Evento avverso: evento inatteso che comporta un danno al paziente.
Evento sentinella: evento grave che richiede revisione immediata dei processi.

2. SISTEMA DI SEGNALAZIONE
Tutti gli operatori incoraggiati a segnalare senza timore di sanzioni.
Segnalazione tramite apposito modulo consegnato al Responsabile.
Le segnalazioni sono trattate con riservatezza.

3. ANALISI DEGLI EVENTI
Analisi delle cause per ogni segnalazione. Definizione azioni correttive con responsabile e scadenza.

4. MONITORAGGIO
Dati analizzati con cadenza semestrale. Risultati comunicati al personale nelle riunioni di staff.

Data di adozione: {oggi}    Firma: {tit}""",
    }

    temi_tecnici = {
        13: ("caratteristiche ambientali e accessibilita", "L. 13/1989, DPR 503/1996",
             "Certificato di agibilita, planimetria dei locali, dichiarazione conformita norme accessibilita"),
        14: ("protezione antincendio", "DM 10/03/1998, D.lgs 81/2008",
             "CPI o dichiarazione di esenzione, registro controlli estintori, piano emergenza"),
        15: ("protezione acustica", "L. 447/1995, DPCM 5/12/1997",
             "Classificazione acustica dell'edificio, eventuale perizia fonometrica"),
        16: ("sicurezza elettrica e continuita elettrica", "DM 37/2008, norme CEI 64-8",
             "Dichiarazione conformita impianto elettrico, verbali verifiche periodiche"),
        17: ("sicurezza anti-infortunistica", "D.lgs 81/2008",
             "DVR, nomina RSPP, attestati formazione, registro infortuni"),
        18: ("protezione da radiazioni ionizzanti", "D.lgs 101/2020",
             "Autorizzazione utilizzo apparecchiature radiogene, nulla osta ARPAS, dosimetrie personali"),
        19: ("eliminazione barriere architettoniche", "L. 13/1989, DPR 503/1996",
             "Dichiarazione conformita, planimetria percorsi accessibili, bagno disabili"),
        20: ("smaltimento dei rifiuti sanitari", "DPR 254/2003, D.lgs 152/2006",
             "Registro carico/scarico rifiuti speciali, contratto ditta smaltimento, formulari FIR"),
        21: ("condizioni microclimatiche", "D.lgs 81/2008, UNI EN ISO 7730",
             "Dichiarazione conformita impianti climatizzazione, registri manutenzione filtri"),
        22: ("impianti di distribuzione dei gas", "D.lgs 46/1997, UNI EN ISO 7396-1",
             "Dichiarazione conformita impianto gas medicali, contratto fornitura, certificato collaudo"),
        23: ("materiali esplodenti", "D.lgs 272/2013",
             "Dichiarazione di non utilizzo di materiali esplodenti nell'attivita sanitaria"),
        24: ("protezione antisismica", "DM 14/01/2008 - NTC",
             "Classificazione sismica del Comune, documentazione tecnica dell'edificio"),
    }

    altri = {
        3: f"""PROGRAMMA PER LA VALUTAZIONE E IL MIGLIORAMENTO DELLA QUALITA
Cod. Requisito 1A.01.05.01 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. INDICATORI MONITORATI
- Soddisfazione paziente: questionari post-trattamento. Target: >= 90%
- Tempi di attesa: monitoraggio tempo medio. Target: <= 15 minuti
- Gestione reclami: risposta entro 7 giorni lavorativi
- Qualita clinica: revisione casi complessi. Target tasso complicanze: < 2%
- Sterilizzazione: test biologici autoclavi. Target: 100% conformita

2. METODI DI VALUTAZIONE
Audit clinici interni semestrali. Riunioni staff mensili per revisione KPI.
Analisi statistica questionari soddisfazione. Revisione eventi avversi e near miss.

3. PIANO DI MIGLIORAMENTO
Obiettivi di miglioramento definiti con responsabile, tempi e indicatori di verifica.
Documentati e monitorati sistematicamente.

Data di adozione: {oggi}    Firma: {tit}""",

        4: f"""PROCEDURA RECLAMI, OSSERVAZIONI E SUGGERIMENTI
Cod. Requisito 1A.01.06.01 - REV. 1/{anno}

Studio: {nome} | Referente: {tit}

1. MODALITA DI PRESENTAZIONE
Modulo cartaceo in sala attesa, email/PEC, colloquio diretto con il referente.

2. GESTIONE DEL RECLAMO
Registrazione entro 24 ore. Analisi e coinvolgimento personale interessato.
Risposta al paziente entro 7 giorni lavorativi (30 giorni per reclami complessi).

3. ANALISI E MIGLIORAMENTO
Dati analizzati trimestralmente. Criticita ricorrenti oggetto di piani di miglioramento documentati.

4. REGISTRO
Tutti i reclami registrati con: data, descrizione, azioni intraprese, esito. Conservato 5 anni.

Data di adozione: {oggi}    Firma: {tit}""",

        5: f"""PROCEDURA PER LE MODALITA DI EROGAZIONE DELL'ASSISTENZA
Cod. Requisito 1A.02.02.01 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. PRENOTAZIONE
Telefono, di persona, email/portale online. Tempi di attesa comunicati alla prenotazione.

2. ACCOGLIENZA E ACCESSO ALLE CURE
Segreteria verifica dati e aggiorna cartella clinica. Alla prima visita: consenso informato e GDPR.
Pazienti con disabilita: assistenza prioritaria.

3. CONTINUITA ASSISTENZIALE
Urgenze: gestione prioritaria o invio al pronto soccorso.
Cartella clinica informatizzata accessibile a tutto il personale autorizzato.

4. MODALITA DI PAGAMENTO
Contanti, POS, bonifico, finanziamento rateale.
Preventivo scritto prima di ogni trattamento significativo.

Data di adozione: {oggi}    Firma: {tit}""",

        7: f"""PROTOCOLLO ISOLAMENTO PAZIENTI CON PATOLOGIE CONTAGIOSE
Cod. Requisito 1A.02.02.03 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. IDENTIFICAZIONE DEL RISCHIO
A rischio: patologie respiratorie acute, infezioni cutanee trasmissibili, epatiti virali, HIV, TBC attiva.

2. MISURE DI ISOLAMENTO
Separazione temporale: paziente programmato come ultimo appuntamento della sessione.
Separazione spaziale: sala trattamento dedicata con ventilazione adeguata.
DPI per il personale: mascherina FFP2/FFP3, guanti, camice monouso, occhiali, visiera.

3. PRECAUZIONI STANDARD (con TUTTI i pazienti)
Igiene delle mani prima e dopo il contatto. Guanti monouso, mascherina chirurgica, occhiali, camice.

4. GESTIONE POST-TRATTAMENTO
Rifiuti infetti: contenitori dedicati. Sterilizzazione completa strumenti. Sanificazione approfondita sala.

Data di adozione: {oggi}    Firma: {tit}""",

        8: f"""PROCEDURA PER LA GESTIONE DELLA DOCUMENTAZIONE SANITARIA
Cod. Requisito 1A.02.05.01 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. TIPOLOGIE DI DOCUMENTAZIONE
Cartella clinica, referti radiografici, consensi informati, piani di trattamento e preventivi.

2. REDAZIONE
Cartella clinica aperta ad ogni nuovo paziente. Ogni prestazione registrata con data, descrizione, firma.

3. ACCESSO E SICUREZZA
Accesso riservato al personale autorizzato. Dati protetti da credenziali personali. Archivio chiuso a chiave.

4. CONSERVAZIONE
Documentazione sanitaria: minimo 10 anni dall'ultima prestazione. Referti radiografici: almeno 20 anni.

5. CONSEGNA REFERTI
Formato cartaceo e/o digitale. Piattaforma sicura conforme al GDPR per invio elettronico.

6. CONFORMITA GDPR
Registro del Trattamento dei Dati redatto. Informativa privacy fornita ai pazienti.

Data di adozione: {oggi}    Firma: {tit}""",

        9: f"""DOCUMENTO FORMALE DI INCARICO DEL RESPONSABILE DELLA MANUTENZIONE
Cod. Requisito 1A.03.01.01 - REV. 1/{anno}

Il/La sottoscritto/a {tit}, Titolare / Legale Rappresentante dello Studio {nome},

NOMINA quale Responsabile della Manutenzione dello studio il/la: {resp_mnt}

FUNZIONI E RESPONSABILITA
- Coordinare tutti gli interventi di manutenzione ordinaria e straordinaria
- Gestire e aggiornare l'inventario delle attrezzature e apparecchiature biomediche
- Pianificare e documentare il calendario di manutenzione preventiva
- Gestire i rapporti con i fornitori e le ditte di assistenza tecnica
- Verificare la conformita delle attrezzature alle normative vigenti
- Conservare la documentazione tecnica delle attrezzature
- Coordinare il collaudo tecnico di sicurezza ad ogni nuova acquisizione

Luogo e data: {s['comune']}, {oggi}

Firma del Titolare: {tit} ______________________
Firma per accettazione: ______________________""",

        10: _build_inventario(s, nome, tit, dir_, resp_mnt, anno, oggi),

        11: f"""PIANO DI MANUTENZIONE STRUTTURE E ATTREZZATURE
Cod. Requisito 1A.03.02.02 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

MANUTENZIONE ORDINARIA PROGRAMMATA

Attrezzature biomediche:
- Riuniti: revisione semestrale dal tecnico autorizzato
- Autoclave Classe B: test biologico settimanale, manutenzione annuale + Bowie-Dick
- OPT/Radiologia: taratura annuale, verifica dosimetrica annuale
- Scanner intraorale: aggiornamento software semestrale, pulizia ottica mensile

Impianti e strutture:
- Impianto elettrico: verifica biennale da elettricista abilitato
- Sistema antincendio: verifica semestrale estintori, manutenzione annuale impianto
- Climatizzatori: manutenzione semestrale, pulizia filtri trimestrale
- Compressore odontoiatrico: drenaggio settimanale, manutenzione semestrale

MANUTENZIONE STRAORDINARIA
Interventi richiesti dal Responsabile della Manutenzione e affidati a ditte specializzate.
Ogni intervento documentato con: data, tipo, ditta incaricata, esito, prossima scadenza.

Data di adozione: {oggi}    Firma: {tit}""",

        12: f"""DOCUMENTAZIONE TECNICA ATTREZZATURE
Cod. Requisito 1A.03.02.03 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

DOCUMENTAZIONE DISPONIBILE PER OGNI ATTREZZATURA
Per ogni apparecchiatura e conservato un fascicolo contenente:
- Manuale d'uso e manutenzione in lingua italiana
- Dichiarazione di conformita CE
- Certificati di collaudo e installazione
- Registri degli interventi di manutenzione
- Verbali delle verifiche periodiche
- Rapporti di assistenza tecnica e certificati di taratura

ACCESSIBILITA
Documentazione conservata in archivio fisico presso lo studio e/o in formato digitale.
Il Responsabile della Manutenzione ha accesso completo alla documentazione.

FORMAZIONE ALL'USO
Ogni operatore riceve formazione specifica sull'uso corretto di ogni apparecchiatura.
La formazione e documentata con data e firma dell'operatore formato.

Data di adozione: {oggi}    Firma: {tit}""",

        25: f"""OBBLIGHI ASSICURATIVI
Cod. Requisito 1A.04.12.04 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. ASSICURAZIONE PROFESSIONALE RC
Ai sensi della Legge 8 marzo 2017, n. 24 (Legge Gelli-Bianco):
Compagnia: ____________________________
Polizza n.: ____________________________
Validita: dal ___/___/______ al ___/___/______
Massimale: EUR ____________________________

2. ASSICURAZIONE INAIL
Posizione INAIL: ____________________________
PAT: ____________________________

3. ASSICURAZIONE STRUTTURA
Polizza n.: ____________________________
Validita: dal ___/___/______ al ___/___/______

Data di adozione: {oggi}    Firma: {tit}""",

        26: f"""CARTA DEI SERVIZI
Cod. Requisito 1A.05.03.01 - REV. 1/{anno}

{nome.upper()} | {adr} | Responsabile: {tit} | ASP: {s['asp']}

PRESTAZIONI EROGATE
Odontoiatria conservativa e restaurativa, Endodonzia, Parodontologia e igiene orale,
Protesi dentale fissa e mobile, Implantologia, Ortodonzia, Chirurgia orale estrattiva,
Radiologia dentale digitale (OPT, RVG), Sbiancamento dentale professionale.

MODALITA DI ACCESSO
Prenotazioni: telefono, di persona, email. Urgenze: gestite in giornata ove possibile.

STANDARD DI QUALITA E IMPEGNI
- Tempi di attesa: max 15 minuti oltre l'orario dell'appuntamento
- Preventivo scritto prima di ogni trattamento significativo
- Informazione completa sulle opzioni di trattamento
- Privacy: dati trattati nel rispetto del GDPR
- Reclami: risposta entro 7 giorni lavorativi

TARIFFE
Esposte in sala attesa e disponibili su richiesta.
Accettati: contanti, POS, bonifico, finanziamenti rateali.

Data di revisione: {oggi}    Firma: {tit}""",

        27: f"""MODALITA DI IDENTIFICAZIONE DI TIROCINANTI E SPECIALIZZANDI
Cod. Requisito 1A.05.03.03 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. TIPOLOGIE DI SOGGETTI
Tirocinanti universitari, specializzandi, collaboratori a contratto.

2. MODALITA DI IDENTIFICAZIONE
Cartellino identificativo visibile con: nome, cognome, qualifica, istituto di provenienza.

3. COMUNICAZIONE AL PAZIENTE
Il paziente e informato della presenza di personale in formazione prima del trattamento.
Il paziente puo rifiutare la presenza del tirocinante senza conseguenze sulle cure ricevute.

4. SUPERVISIONE
L'attivita del personale in formazione e sempre sotto supervisione diretta del professionista responsabile.
I tirocini sono formalizzati con convenzione scritta con l'istituto/universita.

Data di adozione: {oggi}    Firma: {tit}""",

        28: f"""REPORT CUSTOMER SATISFACTION E RECLAMI
Cod. Requisito 1A.05.03.05 - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_}

1. METODOLOGIA
Questionari post-trattamento, analisi reclami, monitoraggio recensioni online.

2. INDICATORI MONITORATI
Soddisfazione generale, qualita cure, comportamento personale, tempi di attesa, chiarezza informazioni.

3. RISULTATI PERIODO DI RIFERIMENTO (da compilare)
Periodo: ___/___/______ - ___/___/______
N. questionari: ______  Soddisfazione media: ______/10
N. reclami: ______  N. risolti entro i termini: ______
Principali criticita: ____________________________________________

4. PIANI DI MIGLIORAMENTO
(da compilare a seguito dell'analisi dei risultati)

Data: {oggi}    Firma: {tit}""",
    }

    for n_t, (tema, norma, docs_list) in temi_tecnici.items():
        if n_t not in base and n_t not in altri:
            altri[n_t] = f"""DOCUMENTAZIONE TECNICA - {tema.upper()}
Cod. Requisito 1A.03.05.{str(n_t-12).zfill(2)} - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_} | Sede: {adr}

NORMATIVA DI RIFERIMENTO: {norma}

DOCUMENTAZIONE DISPONIBILE: {docs_list}

DICHIARAZIONE
Lo studio {nome}, con sede in {adr}, dichiara di possedere i requisiti previsti dalle vigenti leggi in materia di {tema}, come da documentazione allegata e disponibile per la verifica del GdV.

Responsabile: {tit}
Data verifica: {oggi}    Firma: ______________________"""

    tutti = {**base, **altri}
    return tutti.get(num, f"""DOCUMENTO {num}
Cod. {DOCS[num-1][2]} - REV. 1/{anno}

Studio: {nome} | Responsabile Sanitario: {tit} | Direttore Tecnico: {dir_} | Sede: {adr}

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
