"""Builds NSE_Clearing_Credit_Review.pdf from the text below (reportlab)."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

F = "/usr/share/fonts/truetype/crosextra/"
pdfmetrics.registerFont(TTFont("Carlito", F + "Carlito-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Carlito-Bold", F + "Carlito-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Carlito-Italic", F + "Carlito-Italic.ttf"))
pdfmetrics.registerFontFamily("Carlito", normal="Carlito", bold="Carlito-Bold",
                              italic="Carlito-Italic", boldItalic="Carlito-Bold")

NAVY = colors.HexColor("#1f3b5c")
INK = colors.HexColor("#222222")
MUTED = colors.HexColor("#5b6670")
LINE = colors.HexColor("#c9d3dd")
TINT = colors.HexColor("#eef3f8")

body = ParagraphStyle("body", fontName="Carlito", fontSize=10.5, leading=14.2,
                      textColor=INK, spaceAfter=5, alignment=TA_LEFT)
small = ParagraphStyle("small", parent=body, fontSize=8.8, leading=11.4, textColor=MUTED)
h1 = ParagraphStyle("h1", parent=body, fontName="Carlito-Bold", fontSize=17, leading=21,
                    textColor=NAVY, spaceAfter=2)
h2 = ParagraphStyle("h2", parent=body, fontName="Carlito-Bold", fontSize=12.2, leading=15,
                    textColor=NAVY, spaceBefore=9, spaceAfter=4)
cell = ParagraphStyle("cell", parent=body, fontSize=9.6, leading=12.2, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Carlito-Bold")


def P(t, s=body):
    return Paragraph(t, s)


def bullets(items, style=body):
    return ListFlowable([ListItem(P(i, style), leftIndent=10, value="•") for i in items],
                        bulletType="bullet", start="•", leftIndent=12, bulletFontSize=9,
                        bulletColor=NAVY, spaceAfter=4)


def table(rows, widths, header=True, shade_first_col=False):
    data = [[P(c, cellb if (header and r == 0) or (shade_first_col and j == 0) else cell)
             for j, c in enumerate(row)] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    st = [("GRID", (0, 0), (-1, -1), 0.4, LINE),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), TINT))
    if shade_first_col:
        st.append(("BACKGROUND", (0, 0), (0, -1), TINT))
    t.setStyle(TableStyle(st))
    return t


W = A4[0] - 36 * mm
story = []

story += [
    P("Counterparty Credit Review: NSE Clearing Limited", h1),
    P("Sample annual review of a central counterparty (CCP), written from public sources "
      "| Prepared by Shreya Chaurasia | November 2026", small),
    Spacer(1, 6),
]

story.append(table([
    ["Counterparty", "NSE Clearing Limited (NCL), formerly National Securities Clearing Corporation Ltd"],
    ["Sector / type", "Financial market infrastructure: central counterparty (clearing corporation)"],
    ["Country / regulator", "India / Securities and Exchange Board of India (SEBI)"],
    ["Ownership", "Wholly owned subsidiary of National Stock Exchange of India Ltd (NSE)"],
    ["External rating", "CRISIL AAA (local scale), held since 2008"],
    ["Proposed internal grade", "<b>Strong: approx. AA equivalent on a global scale. Outlook: Stable</b>"],
    ["Proposed risk appetite", "<b>Maintain.</b> Support continued clearing through NCL in equity derivatives "
                               "and cash; exposure mainly initial margin posted plus a capped assessment"],
], [42 * mm, W - 42 * mm], header=False, shade_first_col=True))

story += [P("1. Summary and recommendation", h2),
          P("NCL is India's dominant clearing house and the first clearing corporation set up in the country. "
            "It clears about nine in every ten rupees of exchange-traded equity derivatives in India. Its credit "
            "profile rests on three things: a large and growing Core Settlement Guarantee Fund (Core SGF, "
            "India's version of a default fund) sized to survive the default of the <b>three</b> largest members "
            "in equity derivatives, which is stricter than the international Cover 2 standard; conservative "
            "SEBI-prescribed margining, stress testing and default rules; and a very profitable, well-capitalised "
            "parent. The main risks are heavy dependence on equity options volumes, which regulators can cut "
            "quickly; concentration of activity among a few large brokers; and operational and cyber risk as "
            "settlement cycles shorten. I recommend a grade of <b>Strong (approx. AA)</b> and that we "
            "<b>maintain</b> current risk appetite.")]

story += [P("2. Business overview", h2),
          P("NCL was incorporated in August 1995 and clears trades executed on NSE across the cash market, "
            "equity derivatives, currency derivatives, interest rate futures, commodity derivatives and debt, "
            "including tri-party repo. As a vertically integrated clearing house it serves mainly its parent "
            "exchange. Market shares for fiscal 2026, as reported from NSE's draft red herring prospectus "
            "(DRHP), were:"),
          table([["Segment", "Cash market", "Equity derivatives", "Currency derivatives", "Interest rate futures"],
                 ["NSE / NCL share (FY26)", "88.42%", "91.04%", "74.09%", "88.83%"]],
                [W * 0.28] + [W * 0.18] * 4),
          Spacer(1, 6),
          P("The parent launched its initial public offering in September 2026, an offer for sale by existing "
            "shareholders with bidding from 17 to 21 September. Listing does not change NCL's regulatory status, "
            "but it adds public-market scrutiny of the group's governance and profitability.")]

story += [P("3. Financial profile", h2),
          table([["Metric", "Figure", "Source / comment"],
                 ["NCL net profit, FY25 (standalone)", "₹1,625.7 cr", "Company filings via Tofler; up from ₹210.6 cr four years earlier"],
                 ["NCL net profit margin, FY25", "59.1%", "Very high margins, typical of a dominant clearing house"],
                 ["NSE consolidated total income, FY26", "₹18,713 cr", "NSE press release, 5 May 2026 (FY25: ₹19,177 cr)"],
                 ["NSE consolidated profit after tax, FY26", "₹10,302 cr", "Down 15% on FY25, partly due to a one-off SEBI settlement provision"],
                 ["NSE total equity, FY26", "₹32,113.5 cr", "Per NSE's DRHP (FY25: ₹30,353.3 cr)"]],
                [W * 0.36, W * 0.16, W * 0.48]),
          Spacer(1, 5),
          P("<b>Assessment:</b> NCL's earnings power and its parent's equity base are far larger than the CCP's "
            "own contribution to the default fund, so the CCP can rebuild resources after a loss. The parent "
            "has every incentive to support NCL, since a clearing failure would halt NSE's own business. "
            "<i>Open item:</i> I used FY25 standalone figures for NCL; the FY26 audited statements are published "
            "on NSE's offer-documents page and should be reviewed before final approval.")]

story += [P("4. Margin methodology", h2),
          bullets([
              "<b>Derivatives:</b> initial margin is computed with SPAN®, a portfolio-based scenario model, and "
              "collected upfront for all open positions down to client level. NSE's margin pages describe "
              "initial margin calibrated to cover at least a 99% value-at-risk over a one-day horizon, with "
              "extreme loss margin charged on top.",
              "<b>Cash market:</b> VaR margin using exponentially weighted (EWMA) volatility, plus extreme loss "
              "margin and mark-to-market margin, adjusted against members' liquid assets in real time.",
              "<b>Collateral:</b> cash, fixed deposits with approved banks and bank guarantees, among other forms, "
              "subject to haircuts.",
              "<b>Analyst view:</b> a one-day horizon is shorter than the two-day minimum that European rules "
              "(EMIR) set for exchange-traded derivatives. This is partly offset by the extra extreme loss margin, "
              "intraday real-time margining and the large default fund. It is worth asking NCL how often margins "
              "were breached in back-tests over the last year.",
          ])]

story += [P("5. Default resources: Core Settlement Guarantee Fund", h2),
          table([["Date", "NCL Core SGF", "of which equity derivatives (F&amp;O)"],
                 ["30 Sep 2025", "₹12,487.43 cr", "–"],
                 ["31 Mar 2026", "₹13,026.78 cr", "–"],
                 ["30 Sep 2026", "₹13,632.84 cr", "₹12,792.35 cr"]],
                [W * 0.25, W * 0.30, W * 0.45]),
          Spacer(1, 5),
          bullets([
              "<b>Sizing (F&amp;O):</b> NCL is a Category A clearing corporation because it clears at least 40% "
              "of equity derivatives. Its minimum required corpus (MRC) is the higher of the loss from the "
              "simultaneous default of the <b>three</b> members (with associates) causing the largest exposure, "
              "or ₹10,500 crore. The F&amp;O fund was about 1.22x that floor at 30 Sep 2026.",
              "<b>Other segments:</b> cash market sized on two members plus one custodian; currency on at least "
              "two members.",
              "<b>Who pays in:</b> the clearing corporation at least 50%, the exchange at least 25%, and members "
              "at most 25%. For cash, F&amp;O and currency, the members' share is currently met by NSE/NCL, so "
              "members such as us contribute nothing up front.",
              "<b>Stress testing:</b> daily tests using SEBI hypothetical scenarios (scan ranges scaled 1.5x, "
              "1.75x for single stocks), ten years of historical one-day moves, and additional methods such as "
              "stressed VaR and filtered historical simulation. The MRC is reset monthly by the 15th, and SEBI "
              "also requires reverse stress tests, daily margin back-testing and an annual model validation.",
          ])]

story.append(KeepTogether([
    P("6. Default waterfall (SEBI framework, applied per segment)", h2),
    table([["Layer", "Resource used"],
           ["1", "Defaulter's own money: margins, its Core SGF contribution, excess funds in other segments"],
           ["2", "Insurance, if any"],
           ["3", "CCP's own resources equal to 5% of the segment MRC (\"skin in the game\")"],
           ["4", "Core SGF of the segment: penalties first, then the CCP's contribution (at least 25% of MRC), "
                 "then the rest pro rata"],
           ["5", "Share of the CCP's remaining resources, keeping back capital for an orderly wind-down"],
           ["6", "CCP and exchange contributions to other segments' Core SGFs, as approved by SEBI"],
           ["7", "Capped extra contribution from surviving members: lower of 2x their primary contribution or "
                 "20% of the segment Core SGF (derivatives); callable once in 30 days"],
           ["8", "Pro-rata haircut on payouts"]],
          [W * 0.08, W * 0.92]),
]))
story += [Spacer(1, 4),
          P("<b>What this means for our exposure:</b> as a clearing member our exposure to NCL is mainly the "
            "initial margin we post, plus the layer-7 assessment. Because NSE/NCL currently fund the members' "
            "share of the Core SGF, the size of our layer-7 cap depends on how primary contributions are "
            "attributed to members. This should be confirmed against NCL's bye-laws.")]

story += [P("7. Key risks and mitigants", h2),
          table([["Risk", "Why it matters", "Mitigants"],
                 ["Product concentration", "Group revenue relies on transaction charges (78.65% of NSE operating "
                  "revenue in FY26), mostly from equity options. Regulators can cut volumes quickly.",
                  "Very high margins give room to absorb a fall; default fund does not depend on volumes."],
                 ["Member concentration", "Top 5 trading members gave 31.92% of NSE's FY26 operating revenue; "
                  "a few large brokers carry much of the clearing risk.", "Cover 3 sizing in F&amp;O; member "
                  "net-worth rules; client-level margining."],
                 ["Model risk", "One-day margin horizon; scenario choices drive MRC.",
                  "Extreme loss margin; ₹10,500 cr floor; daily back-testing; annual validation."],
                 ["Regulatory / legal", "Parent took a SEBI settlement provision in FY26; group is closely "
                  "supervised.", "Strong regulator; settling past matters reduces uncertainty."],
                 ["Operational / cyber", "T+1 and optional T+0 settlement compress the time to fix failures.",
                  "SEBI cyber and business-continuity rules; CRISIL AAA reflects strong operations."]],
                [W * 0.18, W * 0.44, W * 0.38])]

story += [P("8. Monitoring triggers and questions for NCL", h2),
          bullets([
              "<b>Triggers to re-review:</b> Core SGF falling below the MRC; any member default; a material change "
              "to the margin model; a CRISIL rating action; margin back-test breaches well above 1%; or a change "
              "in ownership or regulation.",
              "<b>Questions for the next due-diligence call:</b> latest back-testing results; worst stress-test "
              "loss versus the MRC in the past 12 months; how layer-7 assessments are calculated for members whose "
              "contribution is funded by NSE; concentration of initial margin in the top members; and progress on "
              "the latest PFMI quantitative disclosures.",
          ])]

story += [P("Sources", h2),
          P("NSE Clearing: Policy on Composition and Contribution to Core SGF; equity derivatives, cash market and "
            "interest rate derivatives margin pages; PFMI disclosures page. SEBI Master Circular for Stock "
            "Exchanges and Clearing Corporations (Oct 2023), Chapter 3, Section 6. NSE press releases (5 May "
            "2026 and 6 Feb 2026). NSE Q2 FY27 financial disclosures as reported by IRIS/Multibagg (Core SGF "
            "balances). Bajaj Broking summary of NSE's DRHP (market shares). Scanx summary of NSE's DRHP (equity, "
            "revenue mix, member concentration). Tofler (NCL standalone profit history). Business Today "
            "(IPO dates). All figures should be re-checked against primary filings before use.", small),
          Spacer(1, 4),
          P("This is an independent sample analysis written from public information for learning purposes. It is "
            "not affiliated with or endorsed by any bank, and is not a credit rating.", small)]


def page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Carlito", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, "NSE Clearing Limited: sample counterparty credit review")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


out = Path(__file__).with_name("NSE_Clearing_Credit_Review.pdf")
SimpleDocTemplate(str(out), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                  topMargin=16 * mm, bottomMargin=16 * mm,
                  title="NSE Clearing Limited: Counterparty Credit Review",
                  author="Shreya Chaurasia").build(story, onFirstPage=page, onLaterPages=page)
print(out)
