# reporting/formatter.py

def format_full_report(final_output: dict, tone="formal"):

    intro_text = {
        "formal": "This is a formal analysis report summarizing contract risks.",
        "simple": "Here is a simple and easy-to-understand summary.",
        "executive": "Executive-level contract risk summary."
    }.get(tone, "Contract Summary Report")

    report = f"""
=====================================
      CONTRACT ANALYSIS REPORT
=====================================

Contract ID: {final_output['contract_id']}
Generated At: {final_output['generated_at']}
Overall Risk Level: {final_output['overall_risk']}

{intro_text}


LEGAL ANALYSIS (Risk: {final_output['legal']['risk_level']})
------------------------------------------------------------
"""

    for clause in final_output["legal"]["extracted_clauses"]:
        report += f"- {clause}\n"

    report += f"""

FINANCE ANALYSIS (Risk: {final_output['finance']['risk_level']})
------------------------------------------------------------
"""
    for clause in final_output["finance"]["extracted_clauses"]:
        report += f"- {clause['clause_text']}\n"

    report += f"""

COMPLIANCE ANALYSIS (Risk: {final_output['compliance']['risk_level']})
------------------------------------------------------------
"""
    for clause in final_output["compliance"]["extracted_clauses"]:
        report += f"- {clause}\n"

    report += f"""

OPERATIONS ANALYSIS (Risk: {final_output['operations']['risk_level']})
------------------------------------------------------------
"""
    for clause in final_output["operations"]["extracted_clauses"]:
        report += f"- {clause['clause_text']}\n"

    return report



def generate_executive_summary(final_output: dict):

    summary = f"""
===========================
     EXECUTIVE SUMMARY
===========================

Overall Contract Risk: {final_output['overall_risk']}

Key Risks:
- Legal Risk: {final_output['legal']['risk_level']}
- Finance Risk: {final_output['finance']['risk_level']}
- Compliance Risk: {final_output['compliance']['risk_level']}
- Operations Risk: {final_output['operations']['risk_level']}

Total Clauses Detected: {final_output['total_clauses']}
"""

    return summary