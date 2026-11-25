# CCP Credit Risk Portfolio

Three pieces of work on **central counterparty (CCP) credit risk**: how clearing houses protect themselves when a member defaults, and how a bank's credit team would assess one.

| Folder | What it is |
|---|---|
| [`memo/`](memo/) | **Counterparty credit review of NSE Clearing Ltd**: business, financials, margin model, Core Settlement Guarantee Fund, default waterfall, risks, proposed grade and risk appetite (PDF) |
| [`stress_test/`](stress_test/) | **CCP margin and default fund stress test** in Python: VaR-based initial margin, margin back-test, stress scenarios, Cover 1/2/3 test and default waterfall |
| [`apac_comparison/`](apac_comparison/) | **Asia-Pacific CCP comparison sheet**: NSE Clearing, CCIL, SGX-DC, HKEX, JSCC and ASX Clear (Futures), built to be filled from PFMI quantitative disclosures |

## Key ideas

- **Initial margin** is the first line of defence: collateral sized to cover a member's likely loss while the CCP closes out its positions.
- **Default fund** (in India, the Core SGF) covers losses beyond margin. International standards (CPMI-IOSCO PFMI) ask systemically important CCPs to survive the default of their **two** largest members (Cover 2). SEBI requires NSE Clearing to cover **three** in equity derivatives.
- **Default waterfall** sets the order in which resources are used: defaulter's money, then the CCP's own capital ("skin in the game"), then the mutualised fund, then further CCP resources, member assessments and finally haircuts.

## Tools

Python (pandas, NumPy, matplotlib), openpyxl, reportlab. Sources are listed in the memo.

*Independent learning project from public information. Not affiliated with any exchange or bank.*
