"""Add appendix content to reach exactly 20 pages."""

with open('tests/generate_nfr1_test_doc.py', 'r', encoding='utf-8') as f:
    content = f.read()

appendix = """
    # ================================================================
    # APPENDIX: FORMS AND CHECKLISTS
    # ================================================================
    pdf.add_page()
    pdf.chapter_title(8, "Appendix: Standard Forms and Checklists")

    pdf.section_title("8.1 Hand Hygiene Audit Form (Monthly)")
    pdf.body_text(
        "The hand hygiene audit form is used by trained infection control observers during monthly direct "
        "observation audits. Each observation is recorded with the following data fields: Ward/Unit, "
        "Observer name, Date and time of observation, Staff member observed (designation, not name for "
        "anonymity), Moment observed (Moment 1 through 5), Action taken (hand rub, hand wash, or no action), "
        "Technique compliance (satisfactory/unsatisfactory), and Overall compliance (compliant/non-compliant)."
    )
    pdf.body_text(
        "Audit data is compiled monthly and the hand hygiene compliance rate is calculated per ward and "
        "per hospital. Results are displayed on the compliance dashboard and trended over time. "
        "The compliance target is >= 90%. Units falling below 80% trigger a corrective action plan. "
        "The audit form is retained for 3 years as evidence of the ongoing monitoring programme."
    )

    pdf.section_title("8.2 Biomedical Waste Daily Register Template")
    pdf.body_text(
        "The following template is used for daily recording of biomedical waste generation in each ward:"
    )
    reg_cols = ["Ward", "Yellow(kg)", "Red(kg)", "White(pcs)", "Blue(pcs)", "Black(kg)", "Total(kg)"]
    reg_widths = [35, 25, 25, 25, 25, 25, 25]
    pdf.table_header(reg_cols, reg_widths)
    reg_rows = [
        ("ICU", "2.3", "1.8", "12", "8", "1.5", "5.6"),
        ("General Med", "3.1", "2.4", "8", "5", "2.1", "7.6"),
        ("General Surg", "2.8", "2.1", "10", "6", "1.8", "6.7"),
        ("OT", "1.9", "3.2", "15", "4", "0.9", "6.0"),
        ("Emergency", "1.5", "1.2", "6", "3", "1.3", "4.0"),
        ("Labour Room", "0.8", "0.6", "4", "2", "0.7", "2.1"),
        ("NICU", "0.4", "0.3", "3", "2", "0.4", "1.1"),
        ("OPD", "0.3", "0.2", "2", "1", "0.5", "1.0"),
        ("Laboratory", "0.6", "0.8", "5", "3", "0.3", "1.9"),
        ("Pharmacy", "0.2", "0.1", "1", "0", "0.4", "0.7"),
    ]
    for i, row in enumerate(reg_rows):
        pdf.table_row(row, reg_widths, fill=(i % 2 == 0))

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    grand_total = ["TOTAL", "13.9", "12.7", "66", "34", "9.9", "36.7"]
    pdf.table_row(grand_total, reg_widths, fill=True)
    pdf.ln(4)

    pdf.body_text(
        "Waste per bed per day calculation: Total daily waste (36.7 kg) / 300 beds = 0.122 kg/bed/day "
        "(well below the benchmark of <=1.5 kg/bed/day). Monthly waste trend shows a 3% increase from "
        "the previous month, primarily due to increased surgical volumes. Year-on-year comparison shows "
        "an 8% increase consistent with the hospital bed occupancy growth from 78% to 85%."
    )

    pdf.section_title("8.3 Needle Stick Injury Report Form")
    pdf.body_text(
        "The needle stick injury report form (NSI form / exposure report form) captures the following "
        "information for each occupational exposure incident:"
    )
    pdf.bullet("Incident Number: Auto-generated sequential number (e.g., NSI-2026-042)")
    pdf.bullet("Date and Time of Incident: [DD/MM/YYYY HH:MM]")
    pdf.bullet("Location/Ward where incident occurred")
    pdf.bullet("Exposed Staff: Name, Employee ID, Designation, Department")
    pdf.bullet("Type of Exposure: Needle stick / Sharps injury / Splash to mucous membrane / Blood splash")
    pdf.bullet("Device involved: Syringe, IV cannula, scalpel, suture needle, lancet, other")
    pdf.bullet("Source Patient: Name/ID, HIV status (if known), HBsAg status (if known), HCV status (if known)")
    pdf.bullet("Immediate action taken: Washed area / Applied antiseptic / Squeezed wound / Irrigated eyes")
    pdf.bullet("Baseline testing done: Yes/No, Date of sample")
    pdf.bullet("PEP initiated: Yes/No, Drug regimen, Time from exposure to PEP initiation")
    pdf.bullet("Reported by (exposed staff): Signature and Date")
    pdf.bullet("Received by (ICN/Occupational Health): Signature and Date")
    pdf.ln(2)
    pdf.body_text(
        "All forms are filed in the confidential exposure register binder maintained at the Occupational "
        "Health Office. Digital copies are entered into the electronic health record system with restricted "
        "access (Occupational Health Officer and ICN only). Follow-up testing results are attached to the "
        "original form. Records are retained for 10 years post-exposure per hospital policy."
    )

    pdf.section_title("8.4 Environmental Cleaning Audit Checklist")
    pdf.body_text(
        "The environmental cleaning audit checklist is used by the Infection Control Nurse during weekly "
        "cleaning audits. Each area is assessed against the following criteria:"
    )
    pdf.bullet("Floors: Clean, dry, no stains, no litter, appropriate disinfectant used (ATP pass)")
    pdf.bullet("High-touch surfaces: Bed rails, call button, IV pole, door handle, light switch, faucet, toilet flush")
    pdf.bullet("Bathrooms: Clean, disinfectant available, soap dispenser full, hand towel available")
    pdf.bullet("Waste bins: Appropriate colour, not overflowing, lined, lids closed")
    pdf.bullet("Sharps containers: Not more than three-quarters full, correctly labeled")
    pdf.bullet("Linen: Stored appropriately, clean linen separated from soiled, cart covered")
    pdf.bullet("Ventilation: AC filters clean, no dust accumulation on vents, air changes adequate")
    pdf.bullet("ATP results: All tested surfaces <= 250 RLU")
    pdf.bullet("Cleaning product dilution: Correct concentration verified")
    pdf.bullet("Cleaning schedule posted and followed")
    pdf.ln(2)
    pdf.body_text(
        "Corrective actions for any failed items are documented on the audit form with the responsible person, "
        "corrective action taken, and date of completion. The cleaning audit results are reported to the "
        "Infection Control Committee monthly and form part of the hospital environmental monitoring "
        "programme. The audit checklist is reviewed annually and updated based on new guidelines or "
        "identified gaps."
    )

    pdf.section_title("8.6 Infection Control Committee Meeting Minutes Template")
    pdf.body_text(
        "The ICC meeting minutes template captures the following for each monthly meeting:"
    )
    pdf.bullet("Meeting date, time, location, and quorum confirmation (>= 60% attendance)")
    pdf.bullet("Attendees: List of members present and apologies")
    pdf.bullet("Previous meeting minutes: Review and approval")
    pdf.bullet("Surveillance report: Monthly HAI rates, trends, and comparison with benchmarks")
    pdf.bullet("Hand hygiene audit results: Compliance rates by ward, action items")
    pdf.bullet("Biomedical waste report: Monthly waste quantification, CBWTF compliance")
    pdf.bullet("Occupational exposure report: NSI incidents, PEP compliance, follow-up status")
    pdf.bullet("Training update: Training completion rates, competency assessment results")
    pdf.bullet("Environmental monitoring: ATP results, cleaning audit findings")
    pdf.bullet("Sterilization/CSSD update: Sterilizer performance, biological indicator results")
    pdf.bullet("Outbreak/infection alerts: Any active clusters or alerts")
    pdf.bullet("Action items: Assignee, deadline, status of previous action items")
    pdf.bullet("Any other business (AOB)")
    pdf.ln(2)
    pdf.body_text(
        "Minutes are recorded by the Documentation Officer (Quality Department) and circulated to all members "
        "within 7 days. Action items are tracked with status updates at the subsequent meeting. Minutes are "
        "retained for the current accreditation cycle. The ICC chairperson signs off on the final minutes."
    )


"""

# Insert before the approval chapter
old_marker = """    # ================================================================
    # CHAPTER 8: APPROVAL AND VERSION HISTORY (Page 21)
    # ================================================================"""

new_marker = """    # ================================================================
    # CHAPTER 9: APPROVAL AND VERSION HISTORY
    # ================================================================"""

content = content.replace(old_marker, appendix + new_marker)
content = content.replace('pdf.chapter_title(8, "Approval', 'pdf.chapter_title(9, "Approval')
content = content.replace('"8.1 Document Approval"', '"9.1 Document Approval"')
content = content.replace('"8.2 Version History"', '"9.2 Version History"')
content = content.replace('"8.3 Distribution"', '"9.3 Distribution"')

with open('tests/generate_nfr1_test_doc.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done - added appendix")
