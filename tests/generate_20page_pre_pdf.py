"""Generate a 20-page NABH Patient Rights & Education (PRE) PDF for testing.

Content covers all 12 PRE requirements with keywords/concepts that the matcher
engine will successfully process. Uses fpdf2 with Helvetica (no Unicode needed).

CRITICAL LAYOUT RULES:
- multi_cell() MUST specify new_x="LMARGIN", new_y="NEXT" to avoid cursor issues
- cell() with new_x/new_y must use proper flags
"""
from fpdf import FPDF
import os


class PatientDoc(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.set_x(10)
            self.cell(95, 6, "Greenfield Hospital - Patient Rights & Education Manual v3.1",
                      align="L", new_x="LMARGIN", new_y="NEXT")
            self.set_x(10)
            self.cell(95, 6, f"Page {self.page_no()}", align="R",
                      new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(80, 80, 120)
            self.line(10, 18, 200, 18)
            self.ln(4)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "CONFIDENTIAL - For internal use only.",
                  align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"Doc: PRE-MAN-2026-021  |  Page {self.page_no()} of {{nb}}",
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
    pdf = PatientDoc()
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
    pdf.cell(0, 12, "Patient Rights & Education Manual", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "Annual Review & Consolidated Edition", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    for label, value in [
        ("Document Control No:", "PRE-MAN-2026-021"),
        ("Version:", "3.1 (Annual Review)"),
        ("Effective Date:", "01 January 2026"),
        ("Review Date:", "31 December 2026"),
        ("Prepared By:", "Ms. Anita Desai, Quality Director"),
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
        "This document constitutes the comprehensive Patient Rights & Education Manual "
        "of Greenfield Multi-Specialty Hospital, Bengaluru. It has been prepared "
        "in accordance with NABH 5th Edition accreditation standards and defines "
        "the hospital's commitment to patient rights, informed consent, privacy, "
        "and health education programs.",
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
        ("1", "Patient Rights Charter"),
        ("  1.1", "Charter of Patient Rights"),
        ("  1.2", "Display and Communication of Rights"),
        ("  1.3", "Staff Training on Patient Rights"),
        ("  1.4", "Monitoring and Compliance"),
        ("2", "Informed Consent Process"),
        ("  2.1", "Consent Policy and Types"),
        ("  2.2", "Consent Documentation Standards"),
        ("  2.3", "Special Consent Situations"),
        ("  2.4", "Audit of Consent Forms"),
        ("3", "Patient Confidentiality and Privacy"),
        ("  3.1", "Privacy Policy and Data Protection"),
        ("  3.2", "Medical Record Confidentiality"),
        ("  3.3", "Patient Information Disclosure Protocols"),
        ("  3.4", "Breach Reporting and Remediation"),
        ("4", "Patient and Family Education"),
        ("  4.1", "Health Education Programme"),
        ("  4.2", "Disease-Specific Education Materials"),
        ("  4.3", "Discharge Education and Follow-Up"),
        ("5", "Grievance Redressal System"),
        ("  5.1", "Complaint Registration Process"),
        ("  5.2", "Grievance Committee and Review"),
        ("  5.3", "Turnaround Time and Escalation"),
        ("6", "Patient Feedback Mechanism"),
        ("  6.1", "Feedback Collection Methods"),
        ("  6.2", "Quarterly Analysis and Action Plans"),
        ("7", "End of Life Care and Advance Directives"),
        ("  7.1", "Advance Directive Policy"),
        ("  7.2", "DNR and End of Life Decisions"),
        ("  7.3", "Palliative Care Services"),
        ("8", "Patient Financial Transparency"),
        ("  8.1", "Estimated Cost of Treatment"),
        ("  8.2", "Daily Billing and Itemized Statements"),
        ("9", "Restraint and Seclusion Protocol"),
        ("  9.1", "Types of Restraints and Indications"),
        ("  9.2", "Prescription and Monitoring"),
        ("10", "Clinical Trial and Research Ethics"),
        ("  10.1", "Ethics Committee and IRB"),
        ("  10.2", "Informed Consent for Research"),
        ("11", "Patient Identification Protocol"),
        ("  11.1", "Patient ID Band System"),
        ("  11.2", "Two-Factor Verification Protocol"),
        ("12", "Transfer and Discharge Protocol"),
        ("  12.1", "Transfer of Care Protocol"),
        ("  12.2", "Discharge Summary Standards"),
        ("13", "Approval and Version History"),
    ]
    for num, title in toc:
        is_main = not num.startswith(" ")
        pdf.set_font("Helvetica", "B" if is_main else "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(15, 6, num.strip())
        pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")

    # ================================================================
    # CHAPTER 1: PATIENT RIGHTS CHARTER (2-3 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(1, "Patient Rights Charter")

    pdf.sec("1.1 Charter of Patient Rights")
    pdf.txt(
        "Greenfield Multi-Specialty Hospital is committed to upholding the rights "
        "of every patient who seeks care within our facility. The patient rights "
        "charter is based on the NABH 5th Edition standards and the Charter of "
        "Patient Rights adopted by the Clinical Establishments (Registration and "
        "Regulation) Act, 2010. This charter applies to all patients, regardless "
        "of age, gender, race, religion, economic status, or medical condition."
    )
    pdf.txt("Every patient has the right to:")
    for r in [
        "Receive respectful and dignified care at all times",
        "Access medical records and receive transparent information about their condition",
        "Give informed consent before any medical procedure or treatment",
        "Confidentiality and privacy of personal health information",
        "Seek a second opinion without fear of retribution",
        "Refuse treatment to the extent permitted by law and be informed of consequences",
        "Receive detailed information about treatment costs and financial implications",
        "File a grievance or complaint without fear of reprisal",
        "Receive emergency care without discrimination",
        "Be protected from neglect, abuse, and exploitation",
    ]:
        pdf.bul(r)
    pdf.ln(2)
    pdf.txt(
        "The patient rights charter is prominently displayed at all patient entry points, "
        "admission desks, inpatient wards, outpatient departments, and on the hospital "
        "website. A printed copy of the charter is provided to every patient at the "
        "time of admission. The charter is available in English, Hindi, Kannada, and "
        "other regional languages as required."
    )

    pdf.sec("1.2 Display and Communication of Rights")
    pdf.txt(
        "Patient rights are displayed on notice boards in the following locations: "
        "main entrance lobby, all ward reception areas, OPD waiting areas, emergency "
        "department waiting area, dialysis unit, ICU waiting room, and the admission "
        "office. Posters are printed in font size 16 or larger for easy reading."
    )
    pdf.txt(
        "At the time of admission, the admitting staff member reads and explains "
        "the key patient rights to the patient or their attendant. A signed "
        "acknowledgement is obtained on the admission form indicating that the "
        "patient has been informed of their rights. This acknowledgement is filed "
        "in the patient medical record."
    )

    pdf.sec("1.3 Staff Training on Patient Rights")
    pdf.txt(
        "All clinical and non-clinical staff receive training on patient rights "
        "during induction and annually thereafter. Training content includes: "
        "understanding the patient rights charter, respecting patient autonomy, "
        "maintaining confidentiality, proper consent processes, and handling "
        "patient grievances with empathy."
    )
    pdf.txt(
        "Department-specific training is provided for staff in high-interaction "
        "areas: emergency department, critical care units, labour room, and "
        "psychiatry unit. Training attendance is documented in the staff training "
        "register. Competency is assessed through case scenarios and observed "
        "patient interactions."
    )

    pdf.sec("1.4 Monitoring and Compliance")
    pdf.txt(
        "Compliance with patient rights standards is monitored through: patient "
        "satisfaction surveys (monthly), grievance log analysis (quarterly), "
        "audit of informed consent documents (monthly), observation of staff-patient "
        "interactions (quarterly), and review of medical record documentation (monthly)."
    )
    pdf.txt(
        "The Patient Rights Committee meets quarterly to review compliance data "
        "and recommend improvements. The committee includes the Medical Director, "
        "Quality Director, Nursing Superintendent, Patient Relations Officer, and "
        "a patient representative. Annual compliance reports are submitted to the "
        "Hospital Governing Board."
    )

    # ================================================================
    # CHAPTER 2: INFORMED CONSENT (2-3 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(2, "Informed Consent Process")

    pdf.sec("2.1 Consent Policy and Types")
    pdf.txt(
        "Informed consent is a fundamental patient right and a legal requirement "
        "before any medical or surgical intervention. The informed consent policy "
        "at Greenfield Hospital ensures that every patient or their legally "
        "authorized representative receives adequate information about the proposed "
        "treatment, alternatives, risks, benefits, and consequences before consenting."
    )
    pdf.txt("Types of consent used at this facility:")
    for c in [
        "General consent for admission and routine care - obtained at admission",
        "Specific consent for surgical/invasive procedures - procedure-specific forms",
        "Consent for anesthesia - separate from surgical consent",
        "Consent for blood transfusion - includes risks of transfusion reactions",
        "Consent for photography/recording - for educational or documentation purposes",
        "Consent for research participation - reviewed by Institutional Ethics Committee",
        "Emergency consent - when patient is unable to consent and delay would be harmful",
        "Consent for HIV testing - pre-test counseling and post-test disclosure",
    ]:
        pdf.bul(c)
    pdf.ln(2)
    pdf.txt(
        "The consent policy document (PRE-POL-CONSENT-2026-01) is available in "
        "all clinical departments. All medical staff are required to be familiar "
        "with and adhere to the consent policy. The policy is reviewed annually "
        "by the Medical Advisory Board."
    )

    pdf.sec("2.2 Consent Documentation Standards")
    pdf.txt(
        "All consent forms must be in a language that the patient understands. "
        "If the patient cannot read, the consent form is read out in the presence "
        "of a witness who attests to the same. The following elements must be "
        "present on every consent form:"
    )
    for d in [
        "Patient name, UHID (Unique Hospital Identification Number), and date of birth",
        "Procedure/treatment name in plain language (not just medical terminology)",
        "Description of the procedure in simple terms",
        "Risks and potential complications explained",
        "Expected benefits and success rates",
        "Alternative treatment options available",
        "Consequences of refusing treatment",
        "Name and signature of the treating physician who explained the procedure",
        "Date and time of consent",
        "Patient/representative signature and relationship to patient",
        "Witness name, signature, and designation",
    ]:
        pdf.bul(d)
    pdf.ln(2)
    pdf.txt(
        "For patients who are minors, consent is obtained from the parent or legal "
        "guardian. For patients who are unconscious or mentally incapacitated, "
        "consent is obtained from the next of kin or legally authorized representative. "
        "In emergency situations where consent cannot be obtained, treatment is "
        "provided under the emergency care provision and documented with two "
        "physician attestations."
    )

    pdf.sec("2.3 Special Consent Situations")
    pdf.txt(
        "Special consent requirements apply to: sterilization procedures (with "
        "mandatory 48-hour waiting period per PNDT Act), organ donation (governed "
        "by the Transplantation of Human Organs Act), medical termination of pregnancy "
        "(as per MTP Act 1971), research studies (with IRB-approved consent forms), "
        "and HIV testing (pre- and post-test counseling mandatory)."
    )
    pdf.txt(
        "For surgeries requiring blood transfusion, a separate consent for blood "
        "transfusion is obtained. For patients of the Jehovah's Witness faith, "
        "a specific refusal of blood products form is signed and witnessed. "
        "Valid informed refusal is documented with the same rigor as informed consent."
    )

    pdf.sec("2.4 Audit of Consent Forms")
    pdf.txt(
        "A monthly audit of 10% of consent forms from each department is conducted "
        "by the Quality Department. The consent audit checklist includes: presence of "
        "all required elements, legibility, completeness of signatures and dates, "
        "evidence of risk discussion, and compliance with language requirements."
    )
    pdf.txt(
        "Consent audit compliance target is 95%. Audit results are reported in the "
        "monthly Quality Review Meeting. Non-compliance triggers corrective action "
        "including re-training of the concerned department. The annual consent audit "
        "summary is presented to the Hospital Governing Board."
    )

    # ================================================================
    # CHAPTER 3: CONFIDENTIALITY & PRIVACY (2 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(3, "Patient Confidentiality and Privacy")

    pdf.sec("3.1 Privacy Policy and Data Protection")
    pdf.txt(
        "Greenfield Hospital maintains a comprehensive patient privacy and "
        "confidentiality policy (PRE-POL-PRIVACY-2026-01) that governs the "
        "collection, storage, access, and disclosure of patient personal health "
        "information. This policy aligns with the NABH confidentiality standards, "
        "the Information Technology Act 2000, and the Digital Personal Data "
        "Protection Act 2023."
    )
    pdf.txt(
        "All patient information including medical records, diagnostic reports, "
        "billing information, and personal identifiers is considered confidential. "
        "Access to patient information is granted only on a need-to-know basis "
        "for treatment, payment, and healthcare operations. All staff sign a "
        "confidentiality agreement at the time of employment."
    )

    pdf.sec("3.2 Medical Record Confidentiality")
    pdf.txt(
        "Medical records are stored in secure, access-controlled areas. Electronic "
        "medical records are protected by role-based access controls, audit trails, "
        "and encryption. Physical records are stored in locked cabinets with access "
        "logs. Records are retained for the period mandated by NABH and applicable "
        "regulations (minimum 3 years for routine records, 7 years for medico-legal "
        "cases, and permanently for minors until they attain majority plus 3 years)."
    )
    pdf.txt(
        "The medical record department follows strict protocols: records are issued "
        "only against a signed requisition, outpatient records are returned on the "
        "same day, inpatient records are returned within 48 hours of discharge, "
        "and records under court subpoena are tracked separately. Breach of "
        "confidentiality is a serious misconduct and may result in disciplinary "
        "action including termination of employment."
    )

    pdf.sec("3.3 Patient Information Disclosure Protocols")
    pdf.txt(
        "Patient information may be disclosed to: treating healthcare providers "
        "within the hospital, referring physicians with patient consent, insurance "
        "companies with patient authorization, public health authorities as required "
        "by law (notifiable diseases), and law enforcement with proper legal authority "
        "(court order or subpoena)."
    )
    pdf.txt(
        "Information disclosure to family members is governed by the patient's "
        "express wishes. At admission, the patient designates a primary contact "
        "person to whom clinical updates may be provided. Where the patient has "
        "not authorized disclosure, information is shared only on a need-to-know "
        "basis with the designated attendant."
    )

    pdf.sec("3.4 Breach Reporting and Remediation")
    pdf.txt(
        "Any suspected or actual breach of patient confidentiality must be reported "
        "immediately to the Privacy Officer (Quality Director). The breach reporting "
        "timeline is within 2 hours of discovery. A breach investigation is initiated "
        "within 24 hours and a written report is submitted within 7 days."
    )
    pdf.txt(
        "Breach remediation includes: containment of the breach (securing records, "
        "revoking access), notification of affected patients (if risk of harm exists), "
        "corrective action (disciplinary measures, process changes), and preventive "
        "measures (staff training, system enhancements). All breaches are logged in "
        "the confidentiality breach register and reported quarterly to the governing board."
    )

    # ================================================================
    # CHAPTER 4: PATIENT & FAMILY EDUCATION (2 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(4, "Patient and Family Education")

    pdf.sec("4.1 Health Education Programme")
    pdf.txt(
        "Greenfield Hospital operates a comprehensive patient and family education "
        "programme designed to empower patients with knowledge about their health "
        "condition, treatment plan, and self-care requirements. The health education "
        "programme is coordinated by the Nursing Education Department in collaboration "
        "with clinical departments."
    )
    pdf.txt("Education is provided at the following touchpoints:")
    for e in [
        "At admission: orientation to the ward, hospital routines, and patient rights",
        "During stay: disease-specific education, medication counselling, dietary guidance",
        "Before procedures: pre-procedure education and preparation instructions",
        "At discharge: discharge instructions, medication schedule, follow-up plan",
        "Post-discharge: telephonic follow-up, outpatient education sessions",
    ]:
        pdf.bul(e)
    pdf.ln(2)
    pdf.txt(
        "Patient education is documented in the medical record using the patient "
        "education record form. The education provided, patient understanding, and "
        "any barriers to learning (language, literacy, cultural) are documented. "
        "Translator services are available for patients who do not speak English, "
        "Hindi, or Kannada."
    )

    pdf.sec("4.2 Disease-Specific Education Materials")
    pdf.txt(
        "The hospital maintains a library of patient education materials for common "
        "conditions including: diabetes mellitus, hypertension, coronary artery disease, "
        "chronic kidney disease, asthma and COPD, stroke, cancer, tuberculosis, "
        "HIV/AIDS, and post-surgical wound care."
    )
    pdf.txt(
        "Education materials are available in multiple formats: printed leaflets and "
        "brochures, video presentations on bedside entertainment systems, digital "
        "content accessible via QR codes, and verbal education by nursing staff. "
        "All materials are reviewed annually by the respective clinical departments "
        "for clinical accuracy and readability. Materials are available in English, "
        "Hindi, Kannada, Tamil, and Telugu."
    )

    pdf.sec("4.3 Discharge Education and Follow-Up")
    pdf.txt(
        "At the time of discharge, every patient receives structured discharge "
        "education covering: diagnosis summary, medications (name, dose, frequency, "
        "duration), dietary recommendations, activity restrictions, wound care "
        "instructions (if applicable), signs and symptoms requiring medical attention, "
        "follow-up appointment details, and emergency contact numbers."
    )
    pdf.txt(
        "Discharge education is provided by the nursing staff and reinforced by "
        "the treating physician. The patient or attendant is asked to demonstrate "
        "understanding (teach-back method) of key instructions. A written discharge "
        "summary is provided in the patient's preferred language. Telephonic "
        "follow-up is conducted within 48-72 hours of discharge for high-risk patients."
    )

    pdf.sec("4.4 Patient Education and Support Groups")
    pdf.txt(
        "The hospital facilitates patient support groups for chronic conditions "
        "including diabetes, hypertension, cancer, and chronic kidney disease. "
        "Support group meetings are held monthly and are facilitated by clinical "
        "specialists. Patient education sessions are conducted in the community "
        "health education centre located on the ground floor of the hospital."
    )
    pdf.txt(
        "Topics covered in patient education sessions include: disease management, "
        "medication adherence, dietary modifications, exercise recommendations, "
        "stress management techniques, and warning signs requiring urgent medical "
        "attention. Attendance at education sessions is documented and the "
        "effectiveness is evaluated through pre- and post-session knowledge "
        "assessments. Patient education materials are distributed at each session."
    )
    pdf.txt(
        "The hospital also maintains a patient resource library with books, pamphlets, "
        "and videos on common health conditions. The library is open to patients "
        "and their families from 8 AM to 8 PM daily. A part-time librarian assists "
        "patients in locating relevant educational materials. Digital resources are "
        "accessible through bedside tablets and the hospital's patient portal."
    )

    # ================================================================
    # CHAPTER 5: GRIEVANCE REDRESSAL (1-2 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(5, "Grievance Redressal System")

    pdf.sec("5.1 Complaint Registration Process")
    pdf.txt(
        "Greenfield Hospital operates a structured patient grievance redressal system "
        "that allows patients and their families to register complaints, suggestions, "
        "and feedback through multiple channels. The policy document "
        "(PRE-POL-GRIEVANCE-2026-01) defines the complete grievance handling process."
    )
    pdf.txt("Patients can register complaints through:")
    for g in [
        "Complaint/suggestion boxes located at each ward and OPD (collected daily)",
        "Dedicated patient relations desk at the main lobby (8 AM to 8 PM)",
        "Grievance phone line: 1800-XXX-XXXX (24x7 toll-free)",
        "Email: grievances@greenfieldhospital.com",
        "Online portal on the hospital website",
        "In-person reporting to the Patient Relations Officer",
        "Direct reporting to any staff member (who must escalate within 1 hour)",
    ]:
        pdf.bul(g)
    pdf.ln(2)
    pdf.txt(
        "All complaints are logged in the centralized grievance register with a "
        "unique complaint number. The register captures: complaint date, patient "
        "name and UHID, complainant name and relationship, complaint category, "
        "detailed description, assigned investigator, and resolution status."
    )

    pdf.sec("5.2 Grievance Committee and Review")
    pdf.txt(
        "The Grievance Redressal Committee meets weekly to review all open complaints. "
        "The committee composition: Medical Director (Chair), Quality Director, "
        "Nursing Superintendent, Patient Relations Officer, Head of concerned "
        "department, and a patient representative."
    )
    pdf.txt(
        "Complaints are categorized as: clinical (treatment-related), service "
        "(hospitality, facilities), behavioral (staff attitude, communication), "
        "administrative (billing, admission), and other. Severity classification: "
        "minor (resolved at ward level), moderate (requires departmental investigation), "
        "major (risk of litigation or serious patient harm), and sentinel (never events)."
    )

    pdf.sec("5.3 Turnaround Time and Escalation")
    pdf.txt(
        "Complaint resolution turnaround times: acknowledgment within 24 hours, "
        "minor complaints resolved within 3 working days, moderate complaints "
        "resolved within 7 working days, major complaints resolved within 15 "
        "working days, and sentinel events reported within 1 hour with immediate "
        "investigation."
    )
    pdf.txt(
        "Escalation matrix: Level 1 - Department Head (for service and minor "
        "complaints), Level 2 - Quality Director (for moderate complaints not "
        "resolved at Level 1 within 3 days), Level 3 - Grievance Committee "
        "(for unresolved Level 2 complaints and all major complaints), and "
        "Level 4 - Hospital Governing Board (for unresolved Level 3 complaints "
        "or sentinel events). All complaint resolutions are documented and "
        "closed with complainant sign-off where possible."
    )

    # ================================================================
    # CHAPTER 6: PATIENT FEEDBACK (1 page)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(6, "Patient Feedback Mechanism")

    pdf.sec("6.1 Feedback Collection Methods")
    pdf.txt(
        "Patient feedback is collected through multiple channels to ensure "
        "representative sampling. The patient feedback system captures experiences "
        "across all touchpoints of the patient journey. Feedback is collected from "
        "inpatients at discharge, outpatients after consultation, emergency "
        "department patients after treatment, and day-care patients after procedure."
    )
    pdf.txt("Feedback collection methods used:")
    for f in [
        "Bedside feedback tablets at discharge (real-time, digital)",
        "Paper-based feedback forms distributed at discharge counters",
        "Telephonic feedback within 48-72 hours of discharge",
        "Online feedback portal accessible via QR code on discharge summary",
        "Direct interviews by Patient Relations Officer (sample basis)",
        "Focus group discussions with patient representatives (quarterly)",
    ]:
        pdf.bul(f)
    pdf.ln(2)
    pdf.txt(
        "The feedback form covers: overall satisfaction, communication with doctors, "
        "nursing care quality, cleanliness and hygiene, food quality, admission and "
        "discharge process, billing transparency, and recommendation likelihood. "
        "Responses are rated on a 5-point Likert scale and open-ended comments are "
        "encouraged."
    )

    pdf.sec("6.2 Quarterly Analysis and Action Plans")
    pdf.txt(
        "Feedback data is analyzed quarterly by the Quality Department. Analysis "
        "includes: overall satisfaction score (target >= 4.0/5.0), domain-wise "
        "scores and trends, comparison with previous quarters and same quarter "
        "last year, and qualitative analysis of open-ended comments."
    )
    pdf.txt(
        "Action plans are developed for areas scoring below 3.5/5.0. The action "
        "plan includes: root cause analysis, corrective actions with timelines, "
        "responsible person/department, and monitoring mechanism. Action plan "
        "progress is reviewed monthly at the Quality Review Meeting. Patient "
        "feedback trends and actions taken are reported in the annual Quality "
        "Improvement Report presented to the Governing Board."
    )

    # ================================================================
    # CHAPTER 7: END OF LIFE CARE (1-2 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(7, "End of Life Care and Advance Directives")

    pdf.sec("7.1 Advance Directive Policy")
    pdf.txt(
        "Greenfield Hospital respects the right of patients to make advance "
        "directives regarding their medical care in the event of incapacitation. "
        "An advance directive (living will) is a written document that specifies "
        "the patient's preferences for medical treatment when they are unable to "
        "communicate their decisions. The advance directive policy "
        "(PRE-POL-ADVANCE-DIRECTIVE-2026-01) aligns with Indian Supreme Court "
        "guidelines on advance directives."
    )
    pdf.txt(
        "Patients may document advance directives at the time of admission or "
        "during their hospital stay. The advance directive is witnessed by two "
        "independent witnesses (not family members or hospital staff directly "
        "involved in care). The directive is filed in the medical record and "
        "flagged prominently. The directive is reviewed by the treating physician "
        "and the patient's designated healthcare proxy (if appointed)."
    )

    pdf.sec("7.2 DNR and End of Life Decisions")
    pdf.txt(
        "Do Not Resuscitate (DNR) orders are made in consultation with the patient, "
        "family, and treating physician. DNR decisions are documented on a specific "
        "DNR order form signed by the treating consultant. The DNR status is "
        "reviewed daily during consultant rounds and can be reversed at any time "
        "based on clinical improvement or patient/family request."
    )
    pdf.txt(
        "End-of-life decisions including withdrawal of life support are made by "
        "consensus among the treating team, patient (if capable), and family members. "
        "The hospital's ethics committee is consulted for any disagreements or "
        "ethical dilemmas. Palliative care consultation is offered to all patients "
        "with terminal illness."
    )

    pdf.sec("7.3 Palliative Care Services")
    pdf.txt(
        "The hospital provides palliative care services through a multidisciplinary "
        "team including palliative care physicians, nurses, social workers, and "
        "counsellors. Palliative care is available for patients with life-limiting "
        "illnesses including advanced cancer, end-stage organ failure, and "
        "neurodegenerative conditions. Services include pain management, symptom "
        "control, psychological support, and spiritual care."
    )
    pdf.txt(
        "Palliative care services are available in the dedicated palliative care "
        "unit (4-bed facility), as inpatient consultation across all wards, and "
        "through the outpatient palliative care clinic held every Wednesday and "
        "Friday. The palliative care team conducts family meetings to discuss "
        "goals of care, advance care planning, and coordination of community "
        "palliative care services. Bereavement support is offered to families "
        "for up to 12 months following the patient's death."
    )
    pdf.txt(
        "Pain management services include pharmacological interventions following "
        "the WHO analgesic ladder, interventional pain procedures, physical therapy "
        "for pain relief, and complementary therapies including relaxation techniques "
        "and music therapy. Pain scores are documented using the Numeric Rating "
        "Scale (NRS) or Wong-Baker FACES scale (for paediatric patients) at each "
        "nursing shift assessment."
    )

    # ================================================================
    # CHAPTER 8: FINANCIAL TRANSPARENCY (1 page)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(8, "Patient Financial Transparency")

    pdf.sec("8.1 Estimated Cost of Treatment")
    pdf.txt(
        "Greenfield Hospital is committed to financial transparency. At the time "
        "of admission, a written estimated cost of treatment is provided to the "
        "patient or attendant. The cost estimate includes: room charges, doctor "
        "consultation fees, investigation costs (laboratory and radiology), "
        "medication costs (estimated), procedure/surgery costs, nursing care "
        "charges, and other applicable fees."
    )
    pdf.txt(
        "Cost estimates are generated by the admission office based on the "
        "diagnosis and proposed treatment plan. The estimate is valid for 7 days "
        "and may be revised if the clinical condition changes or additional "
        "procedures become necessary. Any revision in the estimate is communicated "
        "to the patient or attendant with justification."
    )

    pdf.sec("8.2 Daily Billing and Itemized Statements")
    pdf.txt(
        "Itemized daily bills are provided to patients or attendants every morning "
        "for the previous day's charges. The daily bill includes a detailed breakdown "
        "of all charges: room rent, doctor visits, nursing procedures, medications "
        "administered, investigations performed, consumables used, and any other "
        "services."
    )
    pdf.txt(
        "At the time of discharge, a final consolidated bill is provided with "
        "complete itemization. The final bill is reviewed by the patient or "
        "attendant before payment. Any billing discrepancies are resolved by "
        "the billing department in consultation with the clinical team. A "
        "helpline number for billing queries is prominently displayed."
    )

    # ================================================================
    # CHAPTER 9: RESTRAINT & SECLUSION (1 page)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(9, "Restraint and Seclusion Protocol")

    pdf.sec("9.1 Types of Restraints and Indications")
    pdf.txt(
        "Physical restraints are used only as a last resort when all other "
        "alternatives have failed and the patient is at imminent risk of harm "
        "to self or others. The restraint and seclusion protocol "
        "(PRE-POL-RESTRAINT-2026-01) defines the standards for use of restraints."
    )
    pdf.txt("Types of restraints used at this facility:")
    for rst in [
        "Soft wrist restraints - for patients pulling out IV lines or catheters",
        "Soft ankle restraints - for patients attempting to get out of bed unsafely",
        "Mitt restraints - for patients interfering with wound dressings or feeding tubes",
        "Lap belts - for patients in wheelchairs at risk of falls",
        "Full side rails (with physician order) - for patients at risk of rolling off bed",
        "Chemical restraints - only with physician prescription for acute agitation",
    ]:
        pdf.bul(rst)
    pdf.ln(2)

    pdf.sec("9.2 Prescription and Monitoring")
    pdf.txt(
        "Restraints must be prescribed by a physician with clear indication and "
        "duration. The restraint order is valid for a maximum of 24 hours and "
        "must be reviewed and renewed daily. The prescription specifies the type "
        "of restraint, reason for use, and duration."
    )
    pdf.txt(
        "Monitoring requirements: patient checked every 15 minutes (circulation, "
        "skin integrity, vital signs), restraint released every 2 hours for range "
        "of motion exercises, and reassessment of continued need every shift. "
        "Restraint use is documented in the patient record using the restraint "
        "monitoring flow sheet. Attempts to discontinue restraint are documented "
        "every shift."
    )

    # ================================================================
    # CHAPTER 10: CLINICAL TRIAL & RESEARCH ETHICS (1 page)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(10, "Clinical Trial and Research Ethics")

    pdf.sec("10.1 Ethics Committee and IRB")
    pdf.txt(
        "Greenfield Hospital maintains an Institutional Ethics Committee (IEC) / "
        "Institutional Review Board (IRB) registered with the Central Drugs Standard "
        "Control Organization (CDSCO) and compliant with Schedule Y of the Drugs "
        "and Cosmetics Rules, 1945, and ICMR ethical guidelines. The IEC reviews "
        "all research proposals involving human participants conducted within the "
        "hospital."
    )
    pdf.txt(
        "The IEC composition includes: Chairperson (eminent medical scientist), "
        "basic medical scientist, clinician, legal expert, social scientist or "
        "philosopher, lay person from the community, and a member secretary. "
        "The committee has 12 members with at least 50% non-institutional members."
    )

    pdf.sec("10.2 Informed Consent for Research")
    pdf.txt(
        "All research participants must provide written informed consent on "
        "IEC-approved consent forms. The consent form includes: purpose of the "
        "study, procedures involved, risks and benefits, confidentiality provisions, "
        "compensation for participation (if any), contact information for queries, "
        "and statement that participation is voluntary and can be withdrawn at "
        "any time without penalty."
    )
    pdf.txt(
        "The IEC ensures that vulnerable populations (children, pregnant women, "
        "mentally ill, economically disadvantaged) receive additional protections. "
        "Continuing review of approved studies is conducted annually or more "
        "frequently based on risk level. Adverse events during research are "
        "reported to the IEC within 24 hours."
    )
    pdf.txt(
        "Research data management follows strict protocols: all research data is "
        "de-identified before analysis, stored on secured hospital servers with "
        "access limited to the research team, and retained for a minimum of 3 years "
        "after study completion as per ICMR guidelines. Publication of research "
        "findings requires prior approval from the hospital's research committee. "
        "Authorship follows ICMJE guidelines and honorary authorship is prohibited. "
        "Any conflict of interest must be disclosed by all investigators at the "
        "time of protocol submission and annually thereafter."
    )
    pdf.txt(
        "Clinical trial registration: All clinical trials conducted at this facility "
        "are registered with the Clinical Trials Registry of India (CTRI) before "
        "enrollment of the first participant. Trial registration numbers are "
        "displayed on all informed consent forms and in all publications arising "
        "from the research. The IEC monitors trial progress through annual status "
        "reports and may conduct site visits for high-risk studies."
    )

    # ================================================================
    # CHAPTER 11: PATIENT IDENTIFICATION (1 page)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(11, "Patient Identification Protocol")

    pdf.sec("11.1 Patient ID Band System")
    pdf.txt(
        "Every patient admitted to Greenfield Hospital receives a unique patient "
        "identification wristband (patient ID band) at the time of admission. "
        "The ID band contains: patient full name, UHID (Unique Hospital Identification "
        "Number), date of birth, gender, and admission date."
    )
    pdf.txt(
        "ID bands are colour-coded for safety alerts: white for standard patients, "
        "red for patients with allergies, yellow for fall risk patients, and purple "
        "for DNR/DNAR patients. The ID band must be worn on the patient's wrist "
        "(dominant hand preferred) and checked before every medication administration, "
        "blood transfusion, specimen collection, diagnostic procedure, and surgical "
        "intervention."
    )

    pdf.sec("11.2 Two-Factor Verification Protocol")
    pdf.txt(
        "Patient identification requires two-factor verification: use of at least "
        "two patient identifiers. Acceptable identifiers: patient name and UHID "
        "(combination used as standard), patient name and date of birth, or "
        "patient name and admission number. Room number or bed number are not "
        "accepted as patient identifiers."
    )
    pdf.txt(
        "The two-factor verification is performed: before medication administration, "
        "before blood collection, before diagnostic procedures, before surgical "
        "procedures (time-out protocol), before blood transfusion, and at the "
        "time of patient transfer. Compliance with the patient identification "
        "protocol is audited monthly with a target of 100% compliance."
    )

    # ================================================================
    # CHAPTER 12: TRANSFER & DISCHARGE (1 page)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(12, "Transfer and Discharge Protocol")

    pdf.sec("12.1 Transfer of Care Protocol")
    pdf.txt(
        "Patient transfers within the hospital follow a structured transfer of "
        "care protocol (PRE-POL-TRANSFER-2026-01). Transfer types include: "
        "ward-to-ward transfer (change in clinical status requiring different "
        "level of care), ward-to-ICU transfer (clinical deterioration requiring "
        "intensive monitoring), ICU-to-ward step-down (clinical improvement), "
        "and inter-hospital transfer (need for higher level of care elsewhere)."
    )
    pdf.txt(
        "The transfer protocol requires: verbal handover between referring and "
        "receiving nurses (ISBAR format), transfer summary documented in medical "
        "record, transfer of all medical records and investigations, continuity "
        "of medications during transfer, and notification of receiving consultant "
        "before transfer. Patient ID band is verified before and after transfer."
    )

    pdf.sec("12.2 Discharge Summary Standards")
    pdf.txt(
        "Every discharge summary contains: patient demographics, admission date "
        "and time, discharge date and time, diagnosis (primary and secondary), "
        "procedures performed during admission, hospital course summary, discharge "
        "condition, discharge medications (name, dose, frequency, duration), "
        "follow-up appointments, and patient education provided."
    )
    pdf.txt(
        "The discharge summary is signed by the treating consultant and provided "
        "to the patient at the time of discharge. A copy is retained in the medical "
        "record. Discharge summaries are completed within 24 hours of discharge. "
        "Discharge counselling is provided to the patient and attendants covering "
        "medication instructions, dietary advice, activity limitations, warning "
        "signs, and follow-up schedule."
    )
    pdf.txt(
        "Discharge against medical advice (DAMA/LAMA): When a patient chooses to "
        "leave against medical advice, a LAMA form is signed by the patient or "
        "attendant acknowledging the risks of premature discharge. The treating "
        "doctor documents the discussion including potential consequences and "
        "alternative options offered. In case of absconding (patient leaves without "
        "notice), immediate notification is sent to the hospital administration, "
        "security, and local police as per protocol. All DAMA and absconding cases "
        "are reviewed monthly by the Quality Department."
    )
    pdf.txt(
        "Inter-hospital transfer protocol: When a patient requires transfer to "
        "another facility for specialized care not available at this hospital, "
        "the following steps are followed: receiving hospital is identified and "
        "confirmed accepting the patient, transfer summary and all medical records "
        "are prepared, patient is stabilized before transfer, qualified medical "
        "escort accompanies the patient in the ambulance, transfer documentation "
        "is completed including transfer form and handover notes, and the accepting "
        "physician is updated on patient status during transit. Emergency contact "
        "numbers are exchanged between the transferring and receiving teams."
    )

    # ================================================================
    # CHAPTER 13: APPROVAL AND VERSION HISTORY (1-2 pages)
    # ================================================================
    pdf.add_page()
    pdf.ch_title(13, "Approval and Version History")

    pdf.sec("13.1 Document Approval")
    pdf.txt("This document has been reviewed and approved by the following authorities:")
    pdf.ln(2)
    a_cols = ["Role", "Name", "Signature", "Date"]
    a_widths = [55, 50, 45, 30]
    pdf.tbl_hdr(a_cols, a_widths)
    for i, row in enumerate([
        ("Medical Director", "Dr. Rajesh Kumar", "________________", "01/01/2026"),
        ("Quality Director", "Ms. Anita Desai", "________________", "01/01/2026"),
        ("Nursing Superintendent", "Ms. Lakshmi Nair", "________________", "01/01/2026"),
        ("Patient Relations Officer", "Mr. Suresh Patel", "________________", "01/01/2026"),
        ("Hospital Administrator", "Mr. Vikram Singh", "________________", "01/01/2026"),
    ]):
        pdf.tbl_row(row, a_widths, fill=(i % 2 == 0))
    pdf.ln(6)

    pdf.sec("13.2 Version History")
    v_cols = ["Version", "Date", "Author", "Changes"]
    v_widths = [20, 30, 45, 85]
    pdf.tbl_hdr(v_cols, v_widths)
    for i, row in enumerate([
        ("1.0", "15/06/2024", "Ms. Anita Desai", "Initial release of Patient Rights Manual"),
        ("2.0", "01/01/2025", "Ms. Anita Desai", "Annual review; added digital consent and privacy policy"),
        ("3.0", "01/07/2025", "Ms. Anita Desai", "Mid-year update; revised grievance process and feedback system"),
        ("3.1", "01/01/2026", "Ms. Anita Desai", "Annual review; NABH 5th Edition alignment"),
    ]):
        pdf.tbl_row(row, v_widths, fill=(i % 2 == 0))
    pdf.ln(6)

    pdf.sec("13.3 Distribution List")
    pdf.txt(
        "Controlled copies distributed to: Quality Department (master copy), "
        "Medical Director's office, all ward nursing stations, admission office, "
        "patient relations desk, billing department, emergency department, OPD "
        "registration, ICU, and the hospital intranet (electronic copy). This "
        "document is the property of Greenfield Multi-Specialty Hospital."
    )
    pdf.txt(
        "All controlled copies are numbered and tracked through the Quality "
        "Management System. Document holders are responsible for maintaining "
        "the current version. Uncontrolled copies are marked as such and are "
        "not subject to automatic update."
    )

    # =============================================
    # APPENDIX A: AUDIT TOOLS (1 page)
    # =============================================
    pdf.add_page()
    pdf.ch_title("A", "Audit Tools and Checklists")
    pdf.sec("A.1 Patient Rights Compliance Audit Checklist")
    pdf.txt(
        "The patient rights compliance audit checklist is used by the Quality "
        "Department to conduct monthly audits. The checklist covers the following "
        "domains: Charter display and accessibility (patient rights displayed in "
        "all required locations, charter available in multiple languages, printed "
        "copy provided at admission), Informed consent documentation (consent forms "
        "signed and dated, risks documented, witness signature present, consent in "
        "patient's language), Confidentiality practices (medical records secured, "
        "patient discussions in private areas, staff confidentiality agreements on "
        "file), Patient education documentation (education provided documented, "
        "teach-back method used, discharge instructions provided), and Grievance "
        "redressal (complaint register maintained, complaints resolved within TAT, "
        "patient satisfaction with resolution)."
    )
    pdf.txt(
        "Audit scoring: Each criterion is scored as Compliant (2 points), "
        "Partially Compliant (1 point), or Non-Compliant (0 points). The overall "
        "compliance percentage is calculated as (total score / maximum possible "
        "score) x 100. The audit compliance target is >= 90% for all departments. "
        "Departments scoring below 80% are required to submit a corrective action "
        "plan within 7 working days."
    )
    pdf.txt(
        "Audit frequency: Monthly audits of all inpatient wards and high-risk "
        "departments (ICU, OT, Emergency, Labour Room). Quarterly audits of "
        "OPD and diagnostic services. Annual comprehensive audit of all departments. "
        "Audit findings are presented at the monthly Quality Review Meeting and "
        "annual audit summaries are submitted to the Hospital Governing Board."
    )

    pdf.sec("A.2 Consent Form Audit Tool")
    pdf.txt(
        "The consent form audit tool evaluates a random sample of 10 consent forms "
        "per department per month. The tool checks: Patient identification complete "
        "(name, UHID, DOB), Procedure name clearly written in plain language, Risks "
        "and complications documented, Alternatives discussed, Patient questions "
        "documented, Physician signature present with date and time, Patient/guardian "
        "signature present, Witness signature present with designation, Consent form "
        "language matches patient's preferred language, and Consent obtained within "
        "valid timeframe before procedure (minimum 24 hours for elective procedures)."
    )

    # =============================================
    # SAVE
    # =============================================
    out = "D:/ComplyScan/tests/nfr1_20page_pre.pdf"
    pdf.output(out)
    print(f"Generated: {out}")
    print(f"Total pages: {pdf.page_no()}")
    print(f"File size: {os.path.getsize(out):,} bytes")
    return out


if __name__ == "__main__":
    build()
