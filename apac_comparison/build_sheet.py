"""Builds APAC_CCP_Comparison.xlsx (openpyxl)."""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HEAD = PatternFill("solid", fgColor="E3ECF5")
FILLME = PatternFill("solid", fgColor="FFF8E1")
thin = Side(style="thin", color="C9D3DD")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="top")

CCP_GLOBAL = "https://ccp-global.org (quarterly PQD summary lists every member CCP's disclosure page)"

cols = ["CCP", "Country", "Regulator", "Main products cleared", "Default fund name",
        "Cover standard", "Default fund size (local, latest)", "Total initial margin held",
        "CCP own capital in waterfall", "Largest member stress exposure", "Credit rating",
        "PQD source / link", "Analyst notes"]

rows = [
    ["NSE Clearing Ltd (NCL)", "India", "SEBI",
     "Cash equities, equity derivatives, currency, interest rate futures, commodities, debt / tri-party repo",
     "Core Settlement Guarantee Fund (Core SGF)",
     "Cover 3 in equity derivatives (or ₹10,500 cr floor); cash: 2 members + 1 custodian",
     "₹13,632.84 cr total; ₹12,792.35 cr F&O (30 Sep 2026)", "", "5% of segment MRC ahead of Core SGF", "",
     "CRISIL AAA (since 2008)", "https://www.nseindia.com/static/nse-clearing/pfmi-disclosures",
     "Members' share of Core SGF currently funded by NSE/NCL"],
    ["Clearing Corporation of India Ltd (CCIL)", "India", "Reserve Bank of India",
     "Government securities, repo, tri-party repo, forex settlement and forwards, rupee interest rate derivatives",
     "Segment-wise default funds", "", "", "", "", "", "",
     "https://www.ccilindia.com/web/ccil/pfmi-disclosures1", "Monthly PQD 'Key Risk Areas' reports"],
    ["SGX Derivatives Clearing (SGX-DC)", "Singapore", "Monetary Authority of Singapore",
     "Listed futures and options (equity index, commodities, FX), cleared OTC commodities",
     "Clearing fund", "", "", "", "", "", "", CCP_GLOBAL, ""],
    ["HKFE Clearing Corp / HKCC (HKEX)", "Hong Kong", "Securities and Futures Commission",
     "HKEX futures and options", "Reserve fund", "", "", "", "", "", "", CCP_GLOBAL,
     "HKEX also runs HKSCC (cash) and OTC Clear (OTC derivatives)"],
    ["Japan Securities Clearing Corp (JSCC)", "Japan", "Financial Services Agency",
     "Listed derivatives, cash equities, interest rate swaps, CDS, JGB OTC", "Clearing fund",
     "", "", "", "", "", "", CCP_GLOBAL, ""],
    ["ASX Clear (Futures)", "Australia", "ASIC and Reserve Bank of Australia",
     "ASX 24 futures and options, OTC interest rate derivatives", "Default fund",
     "", "", "", "", "", "", CCP_GLOBAL, ""],
]

wb = Workbook()
ws = wb.active
ws.title = "Comparison"
ws.append(cols)
for r in rows:
    ws.append(r)
widths = [26, 11, 20, 38, 24, 30, 28, 20, 24, 22, 18, 40, 34]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=len(cols)):
    for c in row:
        c.border, c.alignment = BOX, WRAP
        c.font = Font(name="Calibri", size=10, bold=c.row == 1)
        if c.row == 1:
            c.fill = HEAD
        elif c.value in ("", None):
            c.fill = FILLME
ws.freeze_panes = "B2"

g = wb.create_sheet("How to fill")
notes = [
    "APAC CCP comparison: how to complete it",
    "",
    "Yellow cells are blank on purpose: fill them only from each CCP's official disclosures, never estimates.",
    "Where to find each column in the CPMI-IOSCO public quantitative disclosures (PQD):",
    "  • Default fund size: section 4.1 (prefunded default resources)",
    "  • Cover standard and largest stress exposure: section 4.4 (credit risk stress tests)",
    "  • Total initial margin held: section 6.1",
    "  • CCP own capital in the waterfall: section 4.1 / the CCP's rulebook",
    "Record the 'as of' date and currency for every number, and convert to USD in a separate column if comparing sizes.",
    "Good starting point: CCP Global's quarterly PQD summary, which links to every member CCP's disclosure page.",
    "NCL figures: Core SGF balances from NSE's Q2 FY27 disclosures; cover rules from NSE Clearing's Core SGF policy.",
]
for line in notes:
    g.append([line])
g.column_dimensions["A"].width = 110
g["A1"].font = Font(name="Calibri", size=13, bold=True, color="1F3B5C")
for r in range(2, g.max_row + 1):
    g.cell(r, 1).font = Font(name="Calibri", size=10.5)

out = Path(__file__).with_name("APAC_CCP_Comparison.xlsx")
wb.save(out)
print(out)
