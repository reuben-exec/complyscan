"""Generate a 20-page NABH Hospital Infection Control PDF for NFR-1 testing.

Content covers all 7 HIC requirements with keywords/concepts that the matcher
engine will successfully process. Uses fpdf2 with Helvetica (no Unicode needed).

CRITICAL LAYOUT RULES:
- multi_cell() MUST specify new_x="LMARGIN", new_y="NEXT" to avoid cursor issues
- cell() with new_x/new_y must use proper flags
"""
from fpdf import FPDF
import os


class HospitalDoc(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.set_x(10)
            self.cell(95, 6, "Greenfield Hospital - Infection Control Manual v4.2",
                      align="L", new_x="LMARGIN", new_y="NEXT")
            self.set_x(10)
            self.cell(95, 6, f"Page {self.page_no()}", align="R",
                      new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(180, 180, 180)
            self.line(10, 18, 200, 18)
            self.ln(4)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "CONFIDENTIAL - For internal use only.",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"Doc: IC-MAN-2026-042  |  Page {self.page_no()} of {{nb}}",
                  align="C")

    def ch_title(self, num, title):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(0, 51, 102)
        self.ln(4)
        self.cell(0, 10, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 51, 102)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sec(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 80, 130)
        self.ln(2)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def txt(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def bul(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, "  * " + text, new_x="LMARGIN", new_y="NEXT")

    def tbl_hdr(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, col, border=1, fill=True, align="C")
        self.ln()

    def tbl_row(self, cells, widths, fill=False):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        if fill:
            self.set_fill_color(240, 245, 250)
        for i, cell in enumerate(cells):
            self.cell(widths[i], 6, cell, border=1, fill=fill, align="C")
        self.ln()


def build():
    pdf = HospitalDoc()
    pdf.alias_nb_pages()

    # =============================================
    # PAGE 1: COVER
    # =============================================
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 15, "GREENFIELD", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 15, "MULTI-SPECIALTY HOSPITAL", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_draw_color(0, 51, 102)
    pdf.set_line_width(1)
    pdf.line(40, pdf.get_y(), 170, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 12, "Infection Control Manual", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "Annual Review & Consolidated Edition", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    for label, value in [
        ("Document Control No:", "IC-MAN-2026-042"),
        ("Version:", "4.2 (Annual Review)"),
        ("Effective Date:", "01 January 2026"),
        ("Review Date:", "31 December 2026"),
        ("Prepared By:", "Dr. Priya Sharma, Infection Control Officer"),
        ("Approved By:", "Dr. Rajesh Kumar, Medical Director"),
    ]:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(60, 7, label, align="R")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"  {value}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5,
        "This document constitutes the comprehensive Infection Control Manual "
        "of Greenfield Multi-Specialty Hospital, Bengaluru. It has been prepared "
        "in accordance with NABH 5th Edition accreditation standards and is "
        "reviewed annually by the Infection Control Committee.",
        align="C", new_x="LMARGIN", new_y="NEXT")

    # =============================================
    # PAGE 2: TABLE OF CONTENTS
    # =============================================
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    toc = [
        ("1", "Hand Hygiene Policy and Compliance"),
        ("  1.1", "Policy Statement and Scope"),
        ("  1.2", "WHO Five Moments for Hand Hygiene"),
        ("  1.3", "Hand Hygiene Technique Specifications"),
        ("  1.4", "Products and Infrastructure"),
        ("  1.5", "Training Programme"),
        ("  1.6", "Monthly Audit Schedule and Compliance Monitoring"),
        ("  1.7", "Feedback and Corrective Action"),
        ("2", "Infection Control Committee and Organisational Structure"),
        ("  2.1", "Committee Composition and Charter"),
        ("  2.2", "Surveillance Programme"),
        ("  2.3", "Standard and Transmission-Based Precautions"),
        ("  2.4", "Environmental Cleaning Schedule"),
        ("  2.5", "Sterilization and Disinfection Protocols"),
        ("3", "Biomedical Waste Management and Documentation"),
        ("  3.1", "Colour-Coded Segregation System"),
        ("  3.2", "Daily Waste Generation Register"),
        ("  3.3", "Disposal and Transport Documentation"),
        ("  3.4", "CBWTF Registration and Compliance"),
        ("  3.5", "Staff Training on Biomedical Waste"),
        ("  3.6", "Spill and Accident Response"),
        ("4", "Needle Stick Injury and Occupational Exposure Management"),
        ("  4.1", "Confidential Exposure Register"),
        ("  4.2", "Immediate Reporting Protocol"),
        ("  4.3", "Post-Exposure Prophylaxis (PEP) Protocol"),
        ("  4.4", "Follow-Up Schedule and Immunisation Records"),
        ("5", "Infection Surveillance and Data Reporting"),
        ("  5.1", "Surveillance Programme and Case Definitions"),
        ("  5.2", "Device-Day Denominators and Infection Rates"),
        ("  5.3", "Monthly Surveillance Reports and National Benchmarking"),
        ("6", "Staff Infection Control Training and Competency"),
        ("  6.1", "Training Register and Attendance Tracking"),
        ("  6.2", "Initial and Annual Refresher Training"),
        ("  6.3", "Competency Assessment and Gap Analysis"),
        ("7", "Environmental Cleaning and Housekeeping Protocols"),
        ("  7.1", "Cleaning SOPs by Risk Area"),
        ("  7.2", "Daily and Terminal Cleaning Schedules"),
        ("  7.3", "Cleaning Product Specifications"),
        ("  7.4", "Environmental Monitoring (ATP Bioluminescence)"),
        ("8", "Approval and Version History"),
    ]
    for num, title in toc:
        is_main = not num.startswith(" ")
        pdf.set_font("Helvetica", "B" if is_main else "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(15, 6, num.strip())
        pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")

    # ================================================================
    # CHAPTER 1: HAND HYGIENE (3-4 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(1, "Hand Hygiene Policy and Compliance")

    pdf.sec("1.1 Policy Statement and Scope")
    pdf.txt(
        "This hand hygiene policy applies to all healthcare workers, support staff, "
        "contractors, and visitors within the hospital premises of Greenfield "
        "Multi-Specialty Hospital. The objective of this infection prevention policy "
        "is to reduce healthcare-associated infections (HAIs) through standardized "
        "hand hygiene practices in alignment with WHO Guidelines on Hand Hygiene in "
        "Health Care (2009, updated 2024). This policy is part of the hospital's "
        "broader hygiene protocol and constitutes a mandatory component of the "
        "infection control programme."
    )
    pdf.txt(
        "The policy applies to all clinical and non-clinical areas of the hospital "
        "including but not limited to: inpatient wards, intensive care units, "
        "operation theatres, emergency department, outpatient clinics, diagnostic "
        "laboratories, dialysis unit, physiotherapy department, and administrative "
        "offices where patient care activities occur. All personnel having direct "
        "or indirect contact with patients, patient-care equipment, or the patient "
        "environment must strictly follow the hand hygiene policy at all times."
    )
    pdf.txt(
        "Effective Date: 01 January 2026. Review Date: 31 December 2026. Approved "
        "by: Dr. Rajesh Kumar, Medical Director. Authorized by: Dr. Priya Sharma, "
        "Infection Control Officer. Document Control: IC-MAN-2026-042. Version: "
        "4.2. The policy is stamped under Document Control No: IC-POL-HYGIENE-2026-01 "
        "and has been reviewed by the Quality and Patient Safety (QPS) Committee."
    )

    pdf.sec("1.2 WHO Five Moments for Hand Hygiene")
    pdf.txt(
        "All staff must perform hand hygiene at the point of care using the WHO Five "
        "Moments for Hand Hygiene framework. This hand hygiene framework is the "
        "foundation of standard precautions at this hospital. The WHO hand hygiene "
        "guidelines define five critical moments when hand hygiene must be performed:"
    )
    for m in [
        "Moment 1: Before touching a patient",
        "Moment 2: Before clean/aseptic procedures",
        "Moment 3: After body fluid exposure risk",
        "Moment 4: After touching a patient",
        "Moment 5: After touching patient surroundings",
    ]:
        pdf.bul(m)
    pdf.ln(2)
    pdf.txt(
        "The five moments are displayed as hand hygiene indications posters at every "
        "point of care, entrance to patient rooms, and at each bed space. Compliance "
        "is monitored using the WHO Hand Hygiene Observation Tool by trained infection "
        "control nurses acting as unobtrusive observers. The hospital maintains a "
        "dedicated team of five trained observers who conduct rotational audits across "
        "all clinical areas on a weekly and monthly basis."
    )

    pdf.sec("1.3 Hand Hygiene Technique Specifications")
    pdf.txt(
        "Alcohol-based hand rub (ABHR) is the preferred method for routine hand "
        "antisepsis. The hand rubbing technique involves applying 3-5 mL of ABHR and "
        "rubbing all surfaces of the hands for a minimum duration of 20-30 seconds "
        "until the hands are dry. The hand rubbing technique is structured in seven "
        "standardized steps to ensure complete coverage of all hand surfaces."
    )
    pdf.txt(
        "Hand wash with soap and water requires a minimum washing duration of 40-60 "
        "seconds, especially when hands are visibly soiled or after using the "
        "restroom. The hand cleansing steps are: Step 1 - Apply product to cupped "
        "hand. Step 2 - Rub palms together. Step 3 - Rub right palm over left dorsum "
        "and vice versa. Step 4 - Rub palms with fingers interlaced. Step 5 - Rub "
        "backs of fingers on opposing palms. Step 6 - Rotational rubbing of thumbs. "
        "Step 7 - Rotational rubbing of fingertips. Step 8 - Rub wrists. The drying "
        "method uses disposable paper towels placed in dispensers adjacent to each "
        "sink. No cloth towels are permitted in clinical areas."
    )
    pdf.txt(
        "Surgical hand antisepsis requires a minimum scrub of 3-5 minutes using an "
        "antimicrobial surgical hand wash or surgical hand rub. The surgical scrub "
        "technique is documented in a separate SOP (IC-SOP-SURGSCRUB-2026-03). "
        "All surgical team members must perform surgical hand antisepsis before "
        "every surgical procedure. Nail brushes are not to be used as they may "
        "damage the skin."
    )

    pdf.sec("1.4 Products and Infrastructure")
    pdf.txt(
        "The following hand hygiene products are stocked hospital-wide. Alcohol-based "
        "hand rub (ABHR) - ethanol 70% v/v or isopropanol 60-80% v/v - is the "
        "primary product. Liquid soap with antimicrobial agents and moisturizing "
        "components is available at all hand wash stations. Disposable paper towels "
        "are supplied in all hand washing areas."
    )
    pdf.txt(
        "Infrastructure requirements: Hand hygiene dispensers are installed at every "
        "point of care, entrance to patient rooms, within arm's reach of the bedside, "
        "and in all patient care areas. Hand washing sinks with elbow-operated or "
        "sensor-operated taps, liquid soap, and disposable paper towels are available "
        "in all patient care areas. Hand rub dispensers are mounted on walls at a "
        "height of 100-120 cm for easy accessibility."
    )

    pdf.sec("1.5 Training Programme")
    pdf.txt(
        "All new employees receive hand hygiene training during orientation (within "
        "48 hours of joining, before patient contact). The training includes a "
        "theoretical component on infection prevention and a practical component on "
        "hand washing technique. Training register entries are maintained for all "
        "staff including name, employee ID, department, and designation."
    )
    pdf.txt(
        "Competency assessment is mandatory. Every staff member must pass a practical "
        "evaluation using the return demonstration method. Fluorescent gel (GloGerm) "
        "is used for objective assessment of hand hygiene technique. Staff are "
        "evaluated under the black light test and must achieve a passing score of "
        "80% or above. Staff who fail the competency assessment receive remedial "
        "training and are re-tested within 7 days."
    )
    pdf.txt(
        "Annual competency assessments are mandatory for all healthcare workers. "
        "The annual training cycle includes refresher training on updated hand "
        "hygiene guidelines, emerging threats, and new product techniques. Training "
        "records are retained for the current accreditation cycle. The training "
        "programme covers all shifts including night duty staff and weekend staff."
    )

    pdf.sec("1.6 Monthly Audit Schedule and Compliance Monitoring")
    pdf.txt(
        "Direct observation audits are conducted monthly across all wards by trained "
        "infection control nurses using the WHO Hand Hygiene Observation Tool. The "
        "monthly audit involves a trained observer methodology. Auditors observe hand "
        "hygiene compliance at each of the five moments and record opportunities and "
        "compliance. The audit frequency is monthly with quarterly trend analysis."
    )
    pdf.txt(
        "Compliance rates are calculated as observed hand hygiene actions divided by "
        "total opportunities, expressed as a percentage. The compliance target is "
        ">= 90%. The benchmark for high-performing units is >= 95%. The hand hygiene "
        "compliance rate for Q1 2026 was 87% with 340 observations and 296 correct "
        "actions. This represents an improvement from 81% in Q4 2025. The ICU achieved "
        "the highest compliance at 92%, while the general ward areas averaged 84%."
    )
    pdf.txt(
        "Monthly audit results are displayed on ward-level compliance dashboards. "
        "Weekly spot audits are conducted in high-risk areas (ICU, OT, NICU) to "
        "supplement the monthly formal audit. Compliance data is entered into the "
        "infection control database and trended monthly."
    )

    pdf.sec("1.7 Feedback and Corrective Action")
    pdf.txt(
        "A feedback mechanism communicates audit results to individual departments. "
        "Ward-level feedback is provided within 7 days of each monthly audit. The "
        "feedback loop includes individual feedback to non-compliant staff and "
        "departmental review meetings."
    )
    pdf.txt(
        "Corrective actions for non-compliance: individual feedback and coaching "
        "within 48 hours; departmental review if compliance falls below 80%; root "
        "cause analysis for persistent non-compliance; remedial training for "
        "repeat offenders; and performance improvement plans for chronic "
        "non-compliance. Trend analysis is reviewed monthly by the Infection "
        "Control Committee."
    )

    # ================================================================
    # CHAPTER 2: IC COMMITTEE (3-4 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(2, "Infection Control Committee and Organisational Structure")

    pdf.sec("2.1 Committee Composition and Charter")
    pdf.txt(
        "The Infection Control Committee (ICC) is the apex body responsible for "
        "infection control governance at Greenfield Multi-Specialty Hospital. The "
        "committee structure follows the infection control programme framework "
        "recommended by NABH and the WHO. The committee meets monthly with a quorum "
        "requirement of 60% attendance. Minutes are recorded and circulated to all "
        "members within 7 days. The committee reports to the Hospital Governing Body."
    )
    pdf.txt("The infection control committee team comprises:")
    for r in [
        "Chairperson: Dr. Rajesh Kumar (Medical Director)",
        "Infection Control Officer: Dr. Priya Sharma (Microbiologist)",
        "IC Nurse Coordinator: Ms. Lakshmi Nair (Senior Nurse)",
        "Members: Dr. Arjun Mehta (Physician), Dr. Sunita Rao (Surgeon), "
        "Dr. Kavitha Reddy (Pharmacist), Mr. Deepak Joshi (Biomedical Engineer)",
        "Nursing Representatives: One from each ward (ICU, OT, Emergency, "
        "General Medicine, General Surgery, Paediatrics, Orthopaedics)",
        "Documentation Officer: Mr. Rajan Verma (Quality Department)",
    ]:
        pdf.bul(r)
    pdf.ln(2)
    pdf.txt(
        "The infection control group meets on the first Tuesday of every month. "
        "Emergency meetings are convened within 24 hours for outbreak investigation. "
        "The Infection Control Manual is reviewed and updated annually. All committee "
        "members have defined roles and responsibilities documented in their job "
        "descriptions. The committee has authority to enforce infection control "
        "policies across all departments."
    )
    pdf.txt(
        "The ICC Terms of Reference include: reviewing and approving the annual "
        "infection control plan; monitoring HAI rates and trends; reviewing audit "
        "results; approving new infection control policies and protocols; reviewing "
        "outbreak investigations; monitoring antimicrobial stewardship activities; "
        "and reporting to the Hospital Governing Body on infection control performance."
    )

    pdf.sec("2.2 Surveillance Programme")
    pdf.txt(
        "The hospital maintains an active surveillance programme for healthcare-"
        "associated infections (HAI). The infection surveillance programme tracks "
        "device-associated infections using standardised case definitions aligned "
        "with CDC/NHSN criteria. The surveillance programme covers the following "
        "HAI categories:"
    )
    for s in [
        "CLABSI (Central Line-Associated Bloodstream Infection)",
        "CAUTI (Catheter-Associated Urinary Tract Infection)",
        "VAP (Ventilator-Associated Pneumonia)",
        "SSI (Surgical Site Infection)",
        "CRBSI (Catheter-Related Bloodstream Infection)",
    ]:
        pdf.bul(s)
    pdf.ln(2)
    pdf.txt(
        "The surveillance methodology includes active surveillance using prospective "
        "daily review of microbiology laboratory data, pharmacy data for antibiotic "
        "usage, and clinical records. Passive surveillance through voluntary clinical "
        "staff reporting supplements the active system. Targeted surveillance is "
        "conducted in ICU, NICU, OT, and high-risk procedure areas. Data sources "
        "include the microbiology laboratory, pharmacy, medical records, and nursing "
        "shift reports."
    )

    pdf.sec("2.3 Standard and Transmission-Based Precautions")
    pdf.txt(
        "Standard precautions are the foundation of infection prevention and are "
        "applied to all patients regardless of suspected or confirmed infection "
        "status. Standard precautions include hand hygiene, use of personal "
        "protective equipment (PPE), respiratory hygiene/cough etiquette, safe "
        "injection practices, and proper handling of patient-care equipment and "
        "environmental surfaces."
    )
    pdf.txt("Transmission-based precautions applied in addition to standard precautions:")
    pdf.bul("Contact precautions: For MDRO infections, C. difficile. Gloves and gown. Required signage includes a contact precaution sign on the room door.")
    pdf.bul("Droplet precautions: For influenza, pertussis, meningococcal disease. Surgical mask and eye protection for staff entering the room.")
    pdf.bul("Airborne precautions: For TB, measles, varicella, COVID-19. N95 respirator or PAPR required. Negative pressure isolation room must be used.")
    pdf.ln(2)
    pdf.txt(
        "Isolation precautions protocols are posted at each isolation room. All "
        "staff are trained on proper donning and doffing of PPE. Colour-coded "
        "signage is displayed at the entrance of each isolation room. Hand hygiene "
        "and PPE stations are available immediately outside each isolation room."
    )

    pdf.sec("2.4 Environmental Cleaning Schedule")
    pdf.txt(
        "Environmental cleaning standards are maintained through a structured protocol. "
        "The cleaning frequency is tiered by area risk level:"
    )
    pdf.bul("General wards: Twice daily cleaning (morning and evening) plus spot cleaning as needed.")
    pdf.bul("ICU/OT/NICU: Between cases terminal cleaning; high-touch surfaces cleaned every 4 hours.")
    pdf.bul("Common areas (corridors, waiting rooms, cafeteria): Three times daily cleaning.")
    pdf.bul("Toilets and washrooms: Cleaned four times daily with disinfection.")
    pdf.bul("Terminal cleaning: Performed upon patient discharge or transfer using approved disinfectant.")
    pdf.ln(2)
    pdf.txt(
        "High touch surfaces are defined as frequently touched surfaces that serve "
        "as environmental reservoirs for pathogens. These include: bed rails, call "
        "button, tray table, IV pole, monitor, remote control, door handle, light "
        "switch, faucet handle, toilet flush handle, keyboard, mouse, and stethoscope."
    )
    pdf.txt(
        "Cleaning validation is performed using visual inspection checklists and ATP "
        "bioluminescence testing for high-touch surfaces. Each cleaning session is "
        "documented on the cleaning log sheet with date, time, cleaner initials, and "
        "supervisor sign-off. The cleaning record is maintained for a minimum of 3 years "
        "as required by NABH documentation standards. Environmental cleaning rounds are "
        "conducted by the IC Nurse Coordinator on a weekly basis. Findings are documented "
        "on the environmental rounds checklist and any non-compliance is communicated to "
        "the housekeeping supervisor for immediate corrective action."
    )

    pdf.sec("2.5 Sterilization and Disinfection Protocols")
    pdf.txt(
        "The Central Sterile Supply Department (CSSD) manages sterilization and "
        "high-level disinfection of reusable medical devices. Methods include steam "
        "sterilization (autoclave) as the primary method; ethylene oxide (ETO) "
        "sterilization for heat-sensitive items; hydrogen peroxide plasma "
        "sterilization; and glutaraldehyde or peracetic acid for high-level "
        "disinfection of endoscopes."
    )
    pdf.txt(
        "Sterility assurance is maintained through biological indicators (Bacillus "
        "stearothermophilus spore tests) run weekly and with each load. Chemical "
        "indicators include Class 5 integrating indicators and Bowie Dick tests for "
        "pre-vacuum autoclaves. Traceability is maintained through load number, "
        "batch number, sterilization log, and expiry labeling."
    )
    pdf.txt(
        "The CSSD workflow: received items are sorted, cleaned manually or in a "
        "washer-disinfector, inspected for cleanliness, assembled, packaged, labeled "
        "with load number and expiry date, sterilized, stored in clean area, and "
        "distributed. Equipment reprocessing logs are maintained for each sterilizer."
    )

    # ================================================================
    # CHAPTER 3: BMW (3 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(3, "Biomedical Waste Management and Documentation")

    pdf.sec("3.1 Colour-Coded Segregation System")
    pdf.txt(
        "The hospital follows the colour-coded waste segregation system mandated "
        "by the Biomedical Waste Management Rules, 2016 and CPCB guidelines. Waste "
        "segregation is performed at the point of generation."
    )
    w_cols = ["Colour", "Container", "Waste Category", "Examples"]
    w_widths = [25, 35, 50, 80]
    pdf.tbl_hdr(w_cols, w_widths)
    for i, row in enumerate([
        ("Yellow", "Yellow bag", "Anatomical/soiled", "Body parts, dressings"),
        ("Red", "Red bag", "Contaminated recyclable", "Tubing, bottles, IV sets"),
        ("White", "Puncture-proof", "Sharps", "Needles, scalpels, blades"),
        ("Blue", "Cardboard box", "Glassware", "Glass ampoules, vials"),
        ("Black", "Black bag", "General non-hazardous", "Packaging, food waste"),
    ]):
        pdf.tbl_row(row, w_widths, fill=(i % 2 == 0))
    pdf.ln(4)
    pdf.txt(
        "Sharps containers must be puncture proof and labeled with the biohazard "
        "symbol. Containers are replaced when three-quarters full. Waste is stored "
        "in designated covered areas before transport."
    )

    pdf.sec("3.2 Daily Waste Generation Register")
    pdf.txt(
        "A biomedical waste register (daily waste log) is maintained in each ward "
        "and department. The register records: Date, Ward/Department, Yellow bag "
        "weight (kg), Red bag weight (kg), White container count, Blue container "
        "count, Black bag weight (kg), and Total weight (kg)."
    )
    pdf.txt(
        "The register includes rows for each generating unit: General Medicine, "
        "General Surgery, ICU, Operation Theatre, Emergency Department, OPD, "
        "Laboratory, Radiology, Pharmacy, and Administration. Grand totals are "
        "calculated weekly and monthly. Monthly total is compared to the previous "
        "month. Waste per bed per day is calculated and benchmarked against the "
        "target of 1.5 kg/bed/day."
    )

    pdf.sec("3.3 Disposal and Transport Documentation")
    pdf.txt(
        "Biomedical waste is transported from the hospital to the Common Biomedical "
        "Waste Treatment Facility (CBWTF) by an authorized transport service. "
        "Transport documentation includes: Vehicle registration number, driver name "
        "and license, collected by (hospital representative), waste manifest "
        "(challan), and waybill tracking number for each consignment."
    )
    pdf.txt(
        "The CBWTF receipt is filed with hospital records. Each waste consignment "
        "carries a manifest (challan) with details of waste type, quantity, colour, "
        "and weight. The waste chain of custody is documented from generation to "
        "final treatment."
    )

    pdf.sec("3.4 CBWTF Registration and Compliance")
    pdf.txt(
        "The hospital's CBWTF partner, GreenCycle Environmental Solutions Pvt. Ltd., "
        "holds a valid CPCB authorisation. Authorisation No: KA/BMW/2025/0847. "
        "Valid From: 01 April 2025. Valid Until: 31 March 2028."
    )
    pdf.txt(
        "Treatment methods: autoclave sterilization for infectious waste, incineration "
        "for anatomical and soiled waste, microwave treatment, and shredding for "
        "recyclable contaminated waste. Monthly waste summaries include waste "
        "quantification by category, waste per bed per day, and trend analysis."
    )

    pdf.sec("3.5 Staff Training on Biomedical Waste")
    pdf.txt(
        "All staff receive biomedical waste training during induction. Annual "
        "refresher training on BMW rules is mandatory. Training topics: BMW "
        "classification, BMW Rules 2016, waste segregation procedures, universal "
        "precautions, and spill response protocols."
    )
    pdf.txt(
        "Competency assessments are conducted after each training session. Training "
        "records are maintained in the training register. Awareness posters are "
        "displayed in each ward showing colour coding and segregation guidelines."
    )

    pdf.sec("3.6 Spill and Accident Response")
    pdf.txt(
        "Spill incidents are documented in the waste spill incident log. "
        "Classification: Minor spill (small quantity, no exposure), Major spill "
        "(significant quantity, potential exposure), Near Miss, and Reportable."
    )
    pdf.txt(
        "Spill response protocol: area cordoned off, PPE donned, spill contained "
        "using absorbent material, surface decontaminated with 1000 ppm sodium "
        "hypochlorite for blood spills, area cleaned and dried. Incident reporting "
        "within 1 hour, investigation within 24 hours."
    )

    # ================================================================
    # CHAPTER 4: NSI (2-3 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(4, "Needle Stick Injury and Occupational Exposure Management")

    pdf.sec("4.1 Confidential Exposure Register")
    pdf.txt(
        "The hospital maintains a confidential needle stick injury register "
        "(NSI register / sharps injury log / blood exposure register / "
        "occupational exposure register) for all occupational exposures involving "
        "blood or body fluids. The register is maintained by the Occupational Health "
        "Department and is accessible only to authorized personnel."
    )
    pdf.txt(
        "The register captures: Incident No, Date, Time, Exposed Staff name/Employee "
        "ID, Department, Type of exposure (needle stick, sharps injury, splash to "
        "mucous membrane, blood splash), Source Patient name/ID, Source Patient HIV "
        "status (HIV test result), Source Patient HBsAg status (Hepatitis B surface "
        "antigen), Source Patient HCV status (Hepatitis C antibody), and Exposed "
        "Staff baseline serology results."
    )
    pdf.txt(
        "All entries are treated as confidential health records protected under "
        "hospital privacy policy and applicable data protection laws. Quarterly "
        "reports are prepared for the Infection Control Committee."
    )

    pdf.sec("4.2 Immediate Reporting Protocol")
    pdf.txt(
        "All occupational exposures must be reported immediately. The reporting "
        "timeline is within 30 minutes of the incident. The protocol requires: "
        "wash the exposed area (running water and soap for needle stick; copious "
        "irrigation for splash to eyes/nose/mouth), report to the Infection Control "
        "Nurse (ICN) or Occupational Health desk, and complete the exposure report."
    )
    pdf.txt(
        "Reporting chain: Exposed staff reports to ICN within 30 minutes. ICN "
        "notifies Department Head within 1 hour. ICN notifies Occupational Health "
        "Officer within 1 hour. The incident is logged in the exposure register."
    )

    pdf.sec("4.3 Post-Exposure Prophylaxis (PEP) Protocol")
    pdf.txt(
        "PEP (post exposure prophylaxis) must be initiated within 24 hours of "
        "exposure, ideally within 2 hours. The PEP initiation is an emergency "
        "medication regimen prescribed by the Occupational Health Officer. For "
        "HIV exposure: 3-drug regimen Tenofovir 300 mg + Emtricitabine 200 mg "
        "(Truvada) + Dolutegravir 50 mg. This antiretroviral (ART) regimen is "
        "continued for 28 days with monitoring for side effects."
    )
    pdf.txt(
        "For Hepatitis B exposure: If the exposed staff member has documented "
        "seroprotection (Anti-HBs titer >= 10 mIU/mL), no treatment is needed. "
        "If non-immune, Hepatitis B immunoglobulin (HBIG) is administered within "
        "72 hours along with the first dose of hepatitis B vaccine (Engerix-B 20 "
        "mcg IM) following the 0-1-6 month schedule."
    )
    pdf.txt(
        "For Hepatitis C exposure: No PEP is currently available. Baseline testing "
        "and monitoring with repeat HCV testing at 4 weeks, 12 weeks, and 24 weeks "
        "post-exposure. If seroconversion occurs, referral to a hepatologist."
    )

    pdf.sec("4.4 Follow-Up Schedule and Immunisation Records")
    pdf.txt(
        "Post-exposure follow-up serological monitoring: Baseline testing (within "
        "24 hours) - HIV (Anti-HIV), HBsAg, Anti-HCV, Liver function tests. Repeat "
        "at 6 weeks, 3 months, 6 months, and 12 months post-exposure."
    )
    pdf.txt(
        "Hepatitis B vaccination is mandatory for all healthcare workers. Engerix-B "
        "20 mcg IM at 0, 1, and 6 months. Post-vaccination serology (Anti-HBs titer) "
        "checked 1-2 months after Dose 3. Seroprotection = Anti-HBs titer >= 10 "
        "mIU/mL. Non-responders receive booster doses. The immunisation register "
        "(vaccination record / vaccine card) tracks all occupational vaccinations."
    )
    pdf.txt(
        "Psychological support and counselling services are offered to all staff "
        "following an occupational exposure event. The hospital Employee Assistance "
        "Programme (EAP) provides confidential counselling sessions for staff experiencing "
        "anxiety or distress related to potential bloodborne pathogen exposure. Peer "
        "support is available through trained staff counsellors."
    )

    # ================================================================
    # CHAPTER 5: SURVEILLANCE (2-3 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(5, "Infection Surveillance and Data Reporting")

    pdf.sec("5.1 Surveillance Programme and Case Definitions")
    pdf.txt(
        "The infection surveillance programme follows CDC/NHSN case definitions. "
        "Data is collected prospectively and reported monthly to the ICC and "
        "hospital administration. Case definitions:"
    )
    pdf.bul("CLABSI: Primary bloodstream infection within 48h of central line placement, not related to another site.")
    pdf.bul("CAUTI: Urinary tract infection within 48h of urinary catheter placement, no other source.")
    pdf.bul("VAP: Pneumonia developing 48-72h after endotracheal intubation.")
    pdf.bul("SSI: Infection within 30 days of surgery (90 days for implants) at the surgical site.")
    pdf.ln(2)
    pdf.txt(
        "Surveillance sources include the microbiology laboratory (positive cultures), "
        "pharmacy (antibiotic usage data), medical records, and nursing reports. "
        "The methodology follows NHSN protocol for active surveillance. ICMR and "
        "WHO GLASS reporting standards are also followed."
    )

    pdf.sec("5.2 Device-Day Denominators and Infection Rates")
    pdf.txt(
        "Infection rates are calculated using device-day denominators: Number of "
        "infections divided by Number of device days multiplied by 1000 equals the "
        "rate per 1000 device days."
    )
    d_cols = ["Metric", "Jan 2026", "Feb 2026", "Mar 2026", "Q1 Avg"]
    d_widths = [50, 30, 30, 30, 30]
    pdf.tbl_hdr(d_cols, d_widths)
    for i, row in enumerate([
        ("CLABSI Rate", "2.1", "1.8", "1.5", "1.8"),
        ("CAUTI Rate", "3.4", "3.1", "2.8", "3.1"),
        ("VAP Rate", "4.2", "3.9", "3.5", "3.9"),
        ("SSI Rate (%)", "1.8", "2.0", "1.5", "1.8"),
        ("Central Line Days", "1,240", "1,180", "1,310", "1,243"),
        ("Catheter Days", "2,100", "2,050", "2,200", "2,117"),
        ("Ventilator Days", "890", "820", "910", "873"),
        ("Patient Days", "4,200", "4,000", "4,350", "4,183"),
    ]):
        pdf.tbl_row(row, d_widths, fill=(i % 2 == 0))
    pdf.ln(4)

    pdf.sec("5.3 Monthly Surveillance Reports and National Benchmarking")
    pdf.txt(
        "Monthly surveillance reports are prepared by the IC Nurse Coordinator "
        "and presented at the monthly ICC meeting. The report includes: total HAI "
        "count by type, device-day denominators, calculated rates per 1000 device "
        "days, trend compared with previous month, comparison with same month last "
        "year, and comparison with national/international benchmarks."
    )
    pdf.txt(
        "National benchmark comparison uses ICMR data, NHSN (CDC) data, and INICC "
        "data. The hospital target is to maintain rates below the national average "
        "and within the 50th percentile of NHSN benchmarks. EARS-Net and WHO GLASS "
        "data are used for international comparison. Departments compared include "
        "Medicine, Surgery, ICU, Orthopaedics, Obstetrics, Paediatrics, Emergency, "
        "OT, and NICU."
    )
    pdf.txt(
        "Infection data is shared through departmental bulletins (monthly), ICC "
        "meeting minutes, and the hospital intranet dashboard. Action required "
        "notices are issued for any rate exceeding the benchmark."
    )
    pdf.txt(
        "Antimicrobial resistance surveillance is conducted in collaboration with "
        "the microbiology laboratory. The antibiogram is updated quarterly and "
        "reported to the ICC. Common resistant pathogens include MRSA, ESBL-producing "
        "Enterobacteriaceae, carbapenem-resistant Acinetobacter, and VRE. The "
        "antimicrobial stewardship programme monitors antibiotic consumption using "
        "defined daily doses (DDD) per 100 patient days. Monthly antibiotic usage "
        "reports are reviewed by the ICC and the Pharmacy and Therapeutics Committee."
    )

    # ================================================================
    # CHAPTER 6: TRAINING (2-3 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(6, "Staff Infection Control Training and Competency")

    pdf.sec("6.1 Training Register and Attendance Tracking")
    pdf.txt(
        "The training register (training log / training record / infection control "
        "training register) is maintained by the Infection Control Office. Each "
        "session is documented with: Staff Name, Employee ID, Department, "
        "Designation, Topic, Date, Duration, Trainer name, and Signature."
    )
    pdf.txt("Training compliance is reported monthly to the ICC. Topics include:")
    for t in [
        "Hand Hygiene (WHO 5 Moments, technique, products)",
        "Standard Precautions and Transmission-Based Precautions",
        "Personal Protective Equipment (PPE) - donning and doffing",
        "Biomedical Waste Management - segregation, handling, disposal",
        "Sharps Safety and Needle Stick Injury Prevention",
        "Isolation Precautions - contact, droplet, airborne",
        "Environmental Cleaning and Disinfection",
        "Sterilization and High-Level Disinfection basics",
        "Infection Surveillance - staff role in reporting",
    ]:
        pdf.bul(t)
    pdf.ln(2)

    pdf.sec("6.2 Initial and Annual Refresher Training")
    pdf.txt(
        "All new employees receive infection control training within 48 hours of "
        "joining, before any patient contact. This initial training (induction "
        "training / orientation training / onboarding infection control) is "
        "mandatory for all new employees including permanent staff, temporary staff, "
        "contract workers, and students on rotation."
    )
    pdf.txt(
        "The orientation covers: hospital hand hygiene policy, standard precautions, "
        "PPE usage, waste segregation, sharps safety, and emergency protocols. "
        "The training is delivered by the Infection Control Nurse with a 2-hour "
        "session. Competency is assessed at the end. Staff who do not complete "
        "initial training within 48 hours are restricted from patient contact."
    )
    pdf.txt(
        "Annual refresher training is mandatory for all healthcare workers (every "
        "12 months). The annual training includes updated content reflecting new "
        "guidelines, emerging threats, revised protocols, and lessons learned from "
        "surveillance data."
    )
    pdf.txt(
        "Department-specific training is conducted for high-risk areas: ICU staff "
        "- central line care bundles, ventilator care bundles, CLABSI/CAUTI "
        "prevention; OT staff - SSI prevention, aseptic technique, sterile field "
        "management; Laboratory staff - biosafety levels, specimen handling; NICU "
        "staff - neonatal infection prevention; Emergency - triage infection control."
    )

    pdf.sec("6.3 Competency Assessment and Gap Analysis")
    pdf.txt(
        "Competency assessment methods: Practical demonstration (return demonstration) "
        "of hand hygiene; Direct observation of PPE donning/doffing; Fluorescent gel "
        "(GloGerm / black light test) for hand hygiene; Written competency test."
    )
    pdf.txt(
        "Pass criteria: Score >= 80% on written test; satisfactory practical "
        "demonstration; assessment marked as Competent. Staff who fail receive "
        "remedial training (coaching, one-on-one, supervised practice) and are "
        "re-assessed within 14 days."
    )
    pdf.txt(
        "Training gap analysis is conducted quarterly. Gap identification: failed "
        "assessments, surveillance data from areas with higher rates, audit findings, "
        "and staff feedback. Remedial training includes corrective sessions, "
        "one-on-one coaching, and re-training. The gap analysis report is presented "
        "to the ICC quarterly."
    )

    # ================================================================
    # CHAPTER 7: ENVIRONMENTAL CLEANING (2-3 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(7, "Environmental Cleaning and Housekeeping Protocols")

    pdf.sec("7.1 Cleaning SOPs by Risk Area")
    pdf.txt(
        "Environmental cleaning standard operating procedures (cleaning SOPs / "
        "housekeeping SOPs) are defined by risk area with step-by-step instructions."
    )
    pdf.bul("General Ward: Daily mopping with 0.1% sodium hypochlorite; dusting all surfaces daily; bed making upon patient discharge; waste removal twice daily.")
    pdf.bul("ICU: Terminal cleaning between patients; high-touch surfaces every 4 hours; daily deep cleaning with 0.5% sodium hypochlorite; positive pressure maintained.")
    pdf.bul("OT: Terminal cleaning between each case; floor mopping with disinfectant; AHU filters checked monthly; laminar airflow maintained per specifications.")
    pdf.bul("NICU: Hourly cleaning of high-touch surfaces; incubator cleaning between patients; strict hand hygiene compliance monitored continuously.")
    pdf.bul("Emergency Department: High-frequency cleaning of triage areas; isolation bay terminal cleaning; ambulance decontamination after each transport.")
    pdf.bul("Dialysis Unit: Water treatment room cleaning; dialyzer reprocessing area disinfection; patient station cleaning between sessions.")
    pdf.bul("Laboratory: Biosafety cabinet decontamination; bench surface disinfection; spill response procedures posted; hand washing sinks clearly marked.")
    pdf.bul("OPD: Consultation room cleaning between patients; waiting areas cleaned three times daily; hand sanitizer stations restocked twice daily.")
    pdf.ln(2)

    pdf.sec("7.2 Daily and Terminal Cleaning Schedules")
    pdf.txt(
        "The cleaning schedule (daily cleaning schedule / terminal cleaning schedule / "
        "housekeeping roster / disinfection schedule) assigns specific times and tasks:"
    )
    pdf.bul("06:00 - Morning round: floor mopping, bed making, bathroom cleaning, hand hygiene station restocking")
    pdf.bul("08:00 - Post-round: waste removal, handwash area restocking, surface disinfection")
    pdf.bul("10:00 - Mid-morning: corridor and common area dusting, mopping, glass cleaning")
    pdf.bul("12:00 - Midday: pantry and utility room cleaning, equipment surface disinfection")
    pdf.bul("14:00 - Afternoon round: floor mopping, surface disinfection, bathroom check")
    pdf.bul("16:00 - Late afternoon: waste removal, linen management, cleaning supply restocking")
    pdf.bul("18:00 - Evening round: bathroom deep cleaning, high-level disinfection of fixtures")
    pdf.bul("20:00 - Night preparation: floor mopping, handwash station check, supply replenishment")
    pdf.bul("22:00 - Final round: overnight preparation, corridor cleaning, waste disposal area check")
    pdf.ln(2)
    pdf.txt(
        "Terminal cleaning (discharge cleaning) upon discharge or transfer: removing "
        "all linens, cleaning surfaces top to bottom, floor mopping with disinfectant, "
        "bed frame and mattress disinfection, bedside table cleaning, bathroom terminal "
        "clean, and final inspection."
    )

    pdf.sec("7.3 Cleaning Product Specifications and Dilution Protocols")
    pdf.txt("Cleaning product specifications and disinfectant dilution protocols:")
    pdf.bul("Sodium hypochlorite (bleach): Routine 0.1% (1000 ppm); Terminal 0.5% (5000 ppm); Blood spill 1% (10000 ppm). Contact 10 min.")
    pdf.bul("Quaternary ammonium compounds (QAC): General surface disinfection 1:64 dilution. Contact 10 min.")
    pdf.bul("Phenolic disinfectants: Floor cleaning 1:50 dilution. Contact 10 min.")
    pdf.bul("Alcohol (70% isopropanol): Equipment disinfection ready to use. Contact 30 sec.")
    pdf.bul("Hydrogen peroxide (3%): Surface disinfection ready to use. Contact 1 min. Sporicidal.")
    pdf.bul("Peracetic acid: Endoscope HLD 0.2-0.35%. AER used. Contact 5-12 min.")
    pdf.ln(2)
    pdf.txt(
        "Safety Data Sheets (SDS) for all cleaning products are maintained in the "
        "housekeeping office. PPE (gloves, mask, eye protection) is mandatory when "
        "handling concentrated chemicals. Products stored in locked, ventilated "
        "chemical store room."
    )

    pdf.sec("7.4 Environmental Monitoring (ATP Bioluminescence)")
    pdf.txt(
        "Environmental monitoring uses ATP bioluminescence testing (ATP monitoring / "
        "hygiene monitoring / cleaning audit) to assess cleaning efficacy. The system "
        "uses a handheld luminometer with ATP swab devices measuring Relative Light "
        "Units (RLU)."
    )
    pdf.txt(
        "Pass/Fail criteria: RLU <= 250 = pass. RLU 251-500 = marginal (re-cleaning "
        "recommended). RLU > 500 = fail / unacceptable, requiring immediate re-cleaning "
        "and re-testing. Additional methods: surface culture swabs using contact plates "
        "(Rodac plates) with colony forming units (CFU) counted after 48-hour incubation."
    )
    pdf.txt(
        "Monitoring frequency: High-touch surfaces in ICU/OT - daily ATP testing. "
        "General wards - weekly ATP testing. Monthly environmental sampling with "
        "culture swabs. Quarterly comprehensive audit of all areas."
    )
    pdf.txt(
        "Corrective action for failures: immediate re-cleaning with appropriate "
        "disinfectant; re-testing within 24 hours; root cause investigation; "
        "re-training of staff if process deviation; documented corrective measure "
        "in environmental monitoring log. Non-conformance triggers investigation."
    )

    # ================================================================
    # CHAPTER 8: APPROVAL AND VERSION HISTORY (1-2 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(8, "Approval and Version History")

    pdf.sec("8.1 Document Approval")
    pdf.txt("This document has been reviewed and approved by the following authorities:")
    pdf.ln(2)
    a_cols = ["Role", "Name", "Signature", "Date"]
    a_widths = [55, 50, 45, 30]
    pdf.tbl_hdr(a_cols, a_widths)
    for i, row in enumerate([
        ("Medical Director", "Dr. Rajesh Kumar", "________________", "01/01/2026"),
        ("Infection Control Officer", "Dr. Priya Sharma", "________________", "01/01/2026"),
        ("IC Nurse Coordinator", "Ms. Lakshmi Nair", "________________", "01/01/2026"),
        ("Quality Director", "Mr. Rajan Verma", "________________", "01/01/2026"),
        ("Hospital Administrator", "Ms. Anita Desai", "________________", "01/01/2026"),
    ]):
        pdf.tbl_row(row, a_widths, fill=(i % 2 == 0))
    pdf.ln(6)

    pdf.sec("8.2 Version History")
    v_cols = ["Version", "Date", "Author", "Changes"]
    v_widths = [20, 30, 45, 85]
    pdf.tbl_hdr(v_cols, v_widths)
    for i, row in enumerate([
        ("1.0", "15/01/2024", "Dr. Priya Sharma", "Initial release of Infection Control Manual"),
        ("2.0", "01/01/2025", "Dr. Priya Sharma", "Annual review; added COVID-19 protocols and PPE guidelines"),
        ("3.0", "01/07/2025", "Dr. Priya Sharma", "Mid-year update; revised waste management rules"),
        ("4.0", "01/01/2026", "Dr. Priya Sharma", "Annual review; NABH 5th Edition alignment"),
        ("4.1", "15/03/2026", "Dr. Priya Sharma", "Updated surveillance benchmarks and infection rates"),
        ("4.2", "01/06/2026", "Dr. Priya Sharma", "Revised PEP protocol per new national guidelines"),
    ]):
        pdf.tbl_row(row, v_widths, fill=(i % 2 == 0))
    pdf.ln(6)

    pdf.sec("8.3 Distribution List")
    pdf.txt(
        "Controlled copies distributed to: Infection Control Office (master copy), "
        "all ward offices, ICU, Operation Theatre, NICU, Emergency Department, "
        "Central Sterile Supply Department, Laboratory, Housekeeping Office, Quality "
        "Department, Hospital Administration, and the hospital intranet (electronic "
        "copy). Uncontrolled copies are marked as such and are not subject to automatic "
        "update. This document is the property of Greenfield Multi-Specialty Hospital."
    )
    pdf.txt(
        "This document control system follows the guidelines of Document Control "
        "Procedure IC-DOC-CONTROL-2026-01. All controlled copies are numbered and "
        "tracked through the Quality Management System. Document holders are "
        "responsible for maintaining the current version."
    )

    # ================================================================
    # SAVE
    # ================================================================
    out = "D:/ComplyScan/tests/nfr1_20page_hic.pdf"
    pdf.output(out)
    print(f"Generated: {out}")
    print(f"Total pages: {pdf.page_no()}")
    print(f"File size: {os.path.getsize(out):,} bytes")
    return out


if __name__ == "__main__":
    build()
