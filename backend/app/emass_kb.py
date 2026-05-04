"""eMASS knowledge base - curated topics + glossary.

This is practitioner-oriented reference content based on publicly available eMASS
documentation (eMASS User Guide, DoDI 8510.01, NIST SP 800-37 Rev. 2). It is not
authoritative DoD policy. eMASS is a closed government system; field names and
workflows reflect typical configurations as of mid-2020s.
"""
from __future__ import annotations

# Topics: each has slug, title, category, body (markdown).

TOPICS: list[dict] = [
    {
        "slug": "overview",
        "title": "What is eMASS?",
        "category": "Foundations",
        "body": """The **Enterprise Mission Assurance Support Service (eMASS)** is the U.S. Department of \
Defense's Governance, Risk, and Compliance (GRC) tool for managing the **Risk Management Framework (RMF)** \
process for DoD information systems. It is operated by the **Defense Information Systems Agency (DISA)** and \
runs on the NIPRNet (and a separate instance on SIPRNet for classified systems).

**What it does:**
- Tracks every DoD system through the RMF lifecycle from registration through decommissioning.
- Stores the full security authorization package: System Security Plan (SSP), control implementation \
statements, test results, POA&M, artifacts, and authorization decisions.
- Routes packages through workflows (ISSO → ISSM → SCA → AO) for review and signature.
- Maintains the authoritative record of system **Authority to Operate (ATO)** status across DoD.

**What it doesn't do:**
- It is not a vulnerability scanner, configuration manager, or SIEM. Findings come from external tools \
(ACAS, SCAP, STIG Viewer, etc.) and are uploaded as artifacts or test results.
- It does not automatically apply or enforce controls. eMASS is a **documentation and workflow** tool - \
the actual security controls live in your system.

**Who uses it:** ISSOs, ISSMs, SCAs, Authorizing Officials (AOs), Program Managers, and contractors \
working on DoD systems. Access is via PKI/CAC authentication.

**Public access:** eMASS itself is closed-network only. The eMASS User Guide and related references \
are available publicly via DISA. Interaction with eMASS for a real package always happens inside \
the .mil environment.""",
    },
    {
        "slug": "rmf-lifecycle",
        "title": "RMF Lifecycle in eMASS (the 6 + 1 steps)",
        "category": "Foundations",
        "body": """eMASS implements the NIST SP 800-37 Rev. 2 RMF in seven steps. The first step (Prepare) \
was added in Rev. 2 and is partly performed before a system is registered.

| Step | Name | What happens in eMASS |
|---|---|---|
| 0 | **Prepare** | Roles assigned, system boundaries defined, mission/business context documented. Mostly outside eMASS. |
| 1 | **Categorize** | Register the system; set Confidentiality / Integrity / Availability impact (Low/Mod/High); produce the FIPS 199 categorization. |
| 2 | **Select** | eMASS auto-selects the 800-53B baseline (Low/Moderate/High); apply tailoring (overlays, additions, removals); select inheritance. |
| 3 | **Implement** | Author Implementation Statements per control, attach artifacts, enter Hardware/Software inventory, document inherited controls. |
| 4 | **Assess** | The Security Control Assessor (SCA) executes test procedures (from 800-53A), enters test results (Compliant / Non-Compliant / Not Applicable / Not Reviewed) per CCI, generates the Security Assessment Report (SAR). |
| 5 | **Authorize** | AO reviews the package, makes a risk-based decision, signs the authorization (ATO / IATT / ATC / DATO). |
| 6 | **Monitor** | Continuous Monitoring (ConMon) - periodic re-assessment, POA&M maintenance, scan ingestion, annual reviews. Material changes can trigger a re-authorization. |

**Reality check:** Most of the work in eMASS is in Steps 3–6. Step 1–2 are typically a few days; \
Step 3 (Implement) takes the longest because it requires writing 200+ implementation statements; \
Step 6 is forever.""",
    },
    {
        "slug": "user-roles",
        "title": "eMASS User Roles & Responsibilities",
        "category": "Foundations",
        "body": """eMASS roles align with DoDI 8510.01. Roles are granted **per-system** (not globally), \
and a person may hold different roles on different systems.

**Core roles:**

- **ISSO (Information System Security Officer)** - Day-to-day owner of the package. Authors implementation \
statements, uploads artifacts, manages the POA&M. Most of the typing happens here.
- **ISSM (Information System Security Manager)** - Supervises one or more ISSOs. Reviews the package before \
it goes to the SCA. Signs off on changes within delegated authority.
- **ISSE (Information Systems Security Engineer)** - Provides technical engineering input; not always a \
distinct eMASS role.
- **SCA (Security Control Assessor)** - Independently tests the controls and enters test results. \
Produces the **Security Assessment Report (SAR)**. Cannot also be the ISSO/ISSM for the same system.
- **SCA-R (Security Control Assessor Representative)** - Works for the SCA; performs assessments under SCA authority.
- **AO (Authorizing Official)** - Senior official who accepts the residual risk and signs the ATO. Often a \
General Officer / SES. The AO has the only role that can grant authorization.
- **AODR (AO Designated Representative)** - Acts on behalf of the AO, typically for routine package actions.
- **PM/SM (Program Manager / System Manager)** - Owns mission/budget; usually approves resourcing decisions.
- **User Rep (User Representative)** - Speaks for the operational community of the system.

**Workflow tiers (typical):**
1. ISSO drafts → 2. ISSM reviews → 3. SCA assesses → 4. AODR/AO authorizes.

**Separation of duties:** SCA must be independent of the system being assessed (separate chain of command). \
This is the #1 finding source when violated.""",
    },
    {
        "slug": "categorize",
        "title": "Step 1 - Categorize: FIPS 199 in eMASS",
        "category": "Lifecycle",
        "body": """In Step 1, you record the system's **security categorization** using **FIPS 199** \
and **NIST SP 800-60 Vol. II** (information types).

**Process:**
1. Identify the **information types** the system processes (from 800-60 Vol. II - e.g., \"Personnel \
Management Information\", \"Financial Management\").
2. For each information type, determine the impact level (LOW / MODERATE / HIGH) for **Confidentiality, \
Integrity, and Availability**.
3. The system's overall categorization is the **high-water mark** across all info types in each CIA \
dimension.
4. Apply DoD-specific overlays (Privacy, Classified, etc.) where applicable.

**eMASS fields:**
- **System Type** (Major Application, General Support System, Platform IT, etc.)
- **Information Type(s)** with C/I/A ratings
- **Final System Categorization**: e.g., MODERATE-MODERATE-LOW
- **Overlays applied** (Privacy, Cross Domain, Intelligence, Classified, etc.)
- **Mission Assurance Category (MAC)** and **Confidentiality Level (CL)** - DoD legacy fields, often \
still required (MAC I/II/III; CL Public/Sensitive/Classified).

**Outputs:** A signed **Security Categorization** document, used by the SCA and AO. Categorization \
drives baseline selection in Step 2 - get it wrong and you'll rework hundreds of controls.

**Common mistake:** Categorizing too low to dodge controls. AOs see through it; SCAs reject it; you \
end up re-categorizing late and re-doing implementation statements.""",
    },
    {
        "slug": "select",
        "title": "Step 2 - Select: Baseline & Tailoring",
        "category": "Lifecycle",
        "body": """In Step 2, eMASS auto-selects the **NIST SP 800-53B baseline** based on your \
categorization (Low / Moderate / High), then you tailor.

**Baseline counts (Rev. 5):**
- LOW: ~149 controls + enhancements
- MODERATE: ~287
- HIGH: ~370

**Tailoring activities:**
- **Add** controls/enhancements above the baseline (rarely needed but allowed).
- **Remove** (\"tailor out\") controls that don't apply to the system. You must justify each removal.
- **Apply overlays**: Privacy, Classified, Cross-Domain, Space, Industrial Control Systems, etc. \
Overlays add or modify controls and can change parameter values.
- **Inherit** controls from a Common Control Provider (CCP) - see the Inheritance topic.
- **Set parameter values** (\"organization-defined values\") - e.g., AC-2 says lockout after \
\"[Assignment: organization-defined number]\" failed attempts; you set the number.

**eMASS field cheatsheet:**
- Each control has an **Implementation Status**: Planned, Implemented, Inherited, Not Applicable, \
or Manually Inherited.
- **Common Control Provider (CCP)**: the source from which a control is inherited (e.g., facility \
provider for PE-* controls).
- **Justification**: required if you tailor out a baseline control.

**Output:** A documented baseline + tailoring decisions. Becomes part of the SSP.

**Tip:** Run inheritance decisions BEFORE writing implementation statements - inheriting AC-3 from \
the host enclave is way less work than writing a fresh statement.""",
    },
    {
        "slug": "implement",
        "title": "Step 3 - Implement: Implementation Statements & Artifacts",
        "category": "Lifecycle",
        "body": """Step 3 is where you spend the most time. For every control in your tailored baseline, \
you write an **Implementation Statement** describing how the system actually meets the control.

**Implementation Statement: anatomy of a good one**
1. **Identify the actor**: \"The system administrator…\" / \"The application…\" / \"The Common Control Provider…\"
2. **Address every part** (a, b, c…) of the control statement, in order. eMASS will check.
3. **Be concrete**: tools, processes, frequencies. Bad: \"Audit logs are reviewed.\" Good: \"Splunk \
ingests `/var/log/auth.log` from all hosts; the SOC reviews high-severity alerts within 4 hours per \
SOP-IR-002.\"
4. **Reference your evidence**: \"…as documented in Artifact 14, AC-2 SOP.\" Don't make the SCA hunt.
5. **Match the language of the control**: if the control says \"automated mechanisms\", say what \
automated mechanism. If it says \"organization-defined frequency\", state your frequency.

**Artifacts to attach:**
- Policies and SOPs (PDF)
- Screenshots of configuration (group policy, IAM settings)
- Architecture diagrams (data flow, network)
- Scan results (ACAS, SCAP)
- Training records, role assignment letters
- Test results from the SCA in Step 4

**eMASS fields per control:**
- **Implementation Status** (Implemented / Planned / Inherited / Not Applicable / Manually Inherited)
- **Common Control Provider** (if inherited)
- **Implementation Plan / Description** (the statement)
- **Responsible Entities**
- **Estimated Completion Date** (if Planned)
- **CCI assignment** - each CCI gets its own status field

**Top mistakes:**
- Copy-pasting the control statement back as the implementation. The SCA will reject and POA&M it.
- Marking \"Not Applicable\" without a written justification. Always include the why.
- Writing in passive voice with no actor. Reads as wishful thinking.""",
    },
    {
        "slug": "assess",
        "title": "Step 4 - Assess: Test Results & SAR",
        "category": "Lifecycle",
        "body": """The **Security Control Assessor (SCA)** independently tests every control using the \
procedures from **NIST SP 800-53A Rev. 5**. eMASS structures this at the **CCI** level: each CCI \
gets a test result.

**Assessment methods (per 800-53A):**
- **Examine** - review documents/artifacts (policies, scan results)
- **Interview** - talk to people who perform the activity
- **Test** - execute the system to verify behavior

A single CCI may require multiple methods.

**Test result statuses (eMASS):**
- **Compliant** - control objective met
- **Non-Compliant** - failed; will require a POA&M item
- **Not Applicable** - control doesn't apply (with justification)
- **Not Reviewed** - not yet tested (should not appear in a finalized package)

**SAR (Security Assessment Report):** Auto-generated by eMASS from test results. The SAR is one of \
the three core documents the AO reviews (with SSP and POA&M). It includes:
- Overall residual risk
- List of non-compliant CCIs with rationale
- Recommended POA&M items

**Independence rule:** SCA must not be the ISSO/ISSM of the same system. Common org structures: \
Service-level SCA office (Air Force AFRL/AFOTEC, Army NETCOM SCA, etc.), or contracted independent \
assessor.

**Tip:** Get the SCA involved in Step 3, not Step 4. Pre-assessment review of implementation \
statements catches most rework before it becomes formal findings.""",
    },
    {
        "slug": "poam",
        "title": "POA&M (Plan of Action and Milestones)",
        "category": "Lifecycle",
        "body": """A **POA&M item** documents a known security weakness, the plan to fix it, and \
the schedule. Every Non-Compliant CCI in the SAR generates a POA&M item.

**Required POA&M fields (eMASS):**
- **Weakness Description** - what's wrong, in plain English
- **Source** - SCA assessment / scan tool / inspection / self-identified
- **CCI / Control reference**
- **Severity** - Very Low / Low / Moderate / High / Very High (eMASS uses CVSS-aligned)
- **Raw Severity Value** (often a CVSS score)
- **Adjusted / Residual Severity** - after compensating controls
- **Mitigations** - temporary measures reducing risk while you fix
- **Resources Required** - funds, hours, people
- **Scheduled Completion Date**
- **Milestones** - interim steps with dates
- **Identified Date** / **POA&M Creation Date**
- **Status** - Ongoing / Risk Accepted / Completed / Not Applicable

**Lifecycle:**
1. Created (by SCA or ISSO)
2. Reviewed by ISSM
3. Approved/accepted by AO (some severities require AO acknowledgment to delay or accept risk)
4. Worked / mitigated
5. Closed when remediation evidence is uploaded and re-tested

**Common-sense rules:**
- Don't park weaknesses in POA&M forever to dodge fixing them. Aging POA&M items get flagged in audits.
- Risk acceptance for High/Very High severity typically requires explicit AO signature.
- Vulnerabilities from scan ingestion can auto-create POA&M items when severity exceeds a threshold.

**Pitfall:** A POA&M item with no milestones is a red flag - auditors read it as \"we have no plan\".""",
    },
    {
        "slug": "authorize",
        "title": "Step 5 - Authorize: ATO / IATT / ATC / DATO",
        "category": "Lifecycle",
        "body": """In Step 5, the **Authorizing Official (AO)** reviews the full package and makes \
a **risk-based decision**. The AO accepts the residual risk in writing.

**Authorization decision types:**

| Type | Meaning | Typical duration |
|---|---|---|
| **ATO** | Authority to Operate - full production authorization | Up to 3 years (or under cATO, indefinite with continuous monitoring) |
| **ATO with Conditions** | ATO contingent on specific actions | Same as ATO, with conditions to clear |
| **IATT** | Interim Authority to Test - operate in a test environment with real data | 6 months typical, often extendable once |
| **ATC** | Authority to Connect - connects to a network rather than authorizes the system itself | Coupled to host network's ATO |
| **DATO** | Denial of ATO - system cannot operate | Until remediated and resubmitted |
| **cATO** | Continuous ATO - modern model with rolling re-authorization via ConMon | Indefinite |

**Package contents the AO reviews:**
1. **SSP** (System Security Plan) - implementation statements
2. **SAR** (Security Assessment Report) - what was tested and the results
3. **POA&M** - remaining risks and the plan to fix them
4. **RAR** (Risk Assessment Report) - overall mission risk picture
5. Authorization Decision Letter (signed by AO)

**Things AOs reject for:**
- Missing or sparse implementation statements
- Excessive Risk Acceptance without justification
- Aging POA&M items not being worked
- Critical vulnerabilities (CAT I) without compensating controls
- No continuous monitoring strategy

**Output:** Signed Authorization Decision Document (ADD), recorded in eMASS with effective date and \
expiration. The signed ATO is the gate for go-live.""",
    },
    {
        "slug": "monitor",
        "title": "Step 6 - Monitor: ConMon, Re-authorization, cATO",
        "category": "Lifecycle",
        "body": """**Continuous Monitoring (ConMon)** is the ongoing work that keeps a system authorized. \
DoDI 8510.01 requires it for all RMF-authorized systems.

**Required ConMon activities:**
- **Vulnerability scanning** - typically weekly or monthly with ACAS / Tenable / SCAP
- **Patching** - track and report CAT I/II/III remediation timelines
- **Configuration management** - STIG compliance scans, change control board (CCB) on changes
- **Annual control review** - re-assess a subset of controls every year (often 1/3 per year on \
a 3-year cycle)
- **POA&M aging** - keep items moving; close completed; re-baseline overdue
- **Hardware/Software inventory updates**
- **Incident reporting** - IR-* controls are heavily reviewed in audits
- **Training compliance** - AT-* records refreshed annually

**Re-authorization triggers:**
- ATO expiration (typically 3 years)
- **Significant change** - new boundary, classification change, major architecture change, change \
of mission. Don't try to slide a significant change in as \"minor\" - AOs read change logs.
- New threat that materially changes the risk picture

**cATO (Continuous ATO):** Modern model where the system is continuously assessed and authorized \
via automated pipelines, dashboards, and human review at smaller intervals. Requires significant \
engineering investment (DevSecOps, scan automation, SBOM, CMDB integration). DoD CIO has been \
pushing cATO since ~2022.

**eMASS ConMon features:**
- **Test Result Import** for STIG / ACAS / SCAP scans
- **Continuous Monitoring strategy** field per system (cadence, scope)
- **Annual review checklist** generated for each control family
- **POA&M aging report**

**Pitfall:** Treating ConMon as paperwork. The audit looks for evidence that scans are run, results \
reviewed, and remediations tracked - not just that strategy documents exist.""",
    },
    {
        "slug": "inheritance",
        "title": "Inheritance & Common Control Providers",
        "category": "Patterns",
        "body": """**Inheritance** lets your system rely on a control implemented by another system or \
provider (the **Common Control Provider, CCP**). It dramatically reduces work - done right.

**What can be inherited:**
- **Physical controls (PE-*)** - usually inherited from the facility/data center
- **Personnel security (PS-*)** - typically inherited from the agency HR / DISA security office
- **Common platform services** - inherited from a hosting environment (e.g., Cloud One, Platform One, \
NIPRNet, an enclave SOC, an enterprise IAM service)
- **Network controls** - many SC-* controls inherit from the WAN provider or boundary CSP

**Inheritance types in eMASS:**
- **Inherited** - full inheritance, no system action required, status comes from the provider
- **Manually Inherited / Hybrid** - partial inheritance; you implement the system-specific portion \
on top of the provider's
- **System-Specific** - no inheritance, you implement fully

**Provider package:** The CCP must have its own ATO and publish a **Customer Responsibility Matrix \
(CRM)** describing exactly which controls/CCIs they cover and which remain customer responsibility.

**Pitfalls:**
- Inheriting controls the provider didn't actually cover. The CRM is the source of truth - read it.
- Documenting inheritance without the actual control package linked. eMASS will fail you in review.
- Relying on \"common\" inheritance from a provider that has not authorized your specific tenancy.

**FedRAMP / DoD IL parallels:** When using a FedRAMP / DoD IL2/IL4/IL5/IL6 cloud service (AWS GovCloud, \
Azure Gov, etc.), the CSP provides a **CRM**. You typically inherit ~50–70% of controls; your \
implementation statements address the rest plus shared responsibility portions.""",
    },
    {
        "slug": "type-authorization",
        "title": "Type Authorization",
        "category": "Patterns",
        "body": """**Type Authorization** is when a single ATO covers multiple instances of the same \
system deployed at different sites with the same architecture and configuration baseline.

**Use case:** A weapons platform's mission system fielded to 30 bases, all configured identically. \
Instead of 30 separate ATO packages, the program issues one Type Authorization, and each site \
documents its **site-specific deployment** against the type-authorized baseline.

**Requirements:**
- The architecture, baseline configuration, and operational procedures must be **identical** across \
sites. Local variations break the type authorization.
- The Program Manager / Type Authorization holder is responsible for the central ATO and any \
updates.
- Each site usually still records its instance in eMASS as a child / inherited package and tracks \
its own ConMon activities (scans, POA&M items specific to local environment factors like physical \
security at the host facility).

**eMASS handling:** The type-authorized system is registered once; subordinate sites are registered \
as child systems that inherit the controls of the parent. Site-specific findings stay at the site \
level.

**Distinction:**
- **Reciprocity** = another agency accepts your ATO as-is.
- **Type Authorization** = you author one ATO and many sites operate under it.
- **Inheritance** = a CCP provides controls; your system inherits some.""",
    },
    {
        "slug": "reciprocity",
        "title": "Reciprocity",
        "category": "Patterns",
        "body": """**Reciprocity** is the principle that one agency or AO accepts another's existing \
ATO without re-doing the assessment, when:

1. The categorization and baseline are equivalent.
2. The implementation has not materially changed.
3. The receiving AO has confidence in the issuing AO's process.

**Why it matters:** Without reciprocity, every system that crosses agencies (e.g., a Navy app used \
by the Air Force) would re-do an ATO. With reciprocity, the receiving organization performs a \
**Reciprocity Determination** - usually a documents review and risk acknowledgment - and accepts \
the system.

**Common reciprocity flows:**
- DISA STIG-baselined system from Service A used by Service B
- FedRAMP-authorized SaaS adopted by DoD (FedRAMP Moderate ≈ DoD IL2/IL4 baseline)
- DoD authorized system used by another Federal agency

**eMASS handling:**
- Receiving AO records a **reciprocity decision** in eMASS, references the original ATO package, \
documents any additional risks specific to their operational environment.
- Receiving AO is still responsible for **operational/local controls** (training their users, \
incident response within their enclave, etc.).

**Friction points:**
- Different AO risk tolerances (Service-level cultures vary).
- Categorization mismatches (one org calls a system Moderate; another wants High for the same use).
- Stale package - the original ATO is from 2021 and the system has changed; reciprocity won't \
cover the gap.

**DoDI 8510.01 §3.7** explicitly directs AOs to grant reciprocity unless they document a \
specific reason not to.""",
    },
    {
        "slug": "documents",
        "title": "Core Documents in an eMASS Package",
        "category": "Reference",
        "body": """An RMF package in eMASS has a small number of formal documents and many supporting \
artifacts.

**The \"Big Three\" + 1:**
- **SSP - System Security Plan**: Describes the system, its boundary, categorization, controls, \
and implementation statements. Auto-generated by eMASS from your inputs.
- **SAR - Security Assessment Report**: SCA's findings on whether each control is met. Generated \
from test results.
- **POA&M - Plan of Action and Milestones**: Open weaknesses with mitigation plans.
- **RAR - Risk Assessment Report**: Mission/business risk picture. Often a separate document with \
threat analysis (NIST 800-30).

**Other typical artifacts:**
- **Authorization Boundary Diagram** - what's in scope, what's not, all data flows in/out
- **Hardware List & Software List** - inventory tied to controls (CM-8)
- **Network Diagram** - logical and physical
- **Configuration Management Plan** (CM-9)
- **Contingency Plan / DR Plan** (CP-2) and Test Results (CP-4)
- **Incident Response Plan** (IR-8) and IR Test Results
- **Continuous Monitoring Strategy** (CA-7)
- **Privacy Impact Assessment (PIA)** if PII involved
- **PPSM Registration** - Ports, Protocols, Services Management
- **Memoranda of Understanding/Agreement (MOU/MOA)** for inter-system connections (CA-3)
- **Acceptable Use Policy / Rules of Behavior** (PL-4)

**Signature documents (per package):**
- Authorization Decision Document (ADD) - signed by the AO
- POA&M - signed by ISSM and AO
- SSP - signed by ISSO and ISSM
- Categorization - signed by System Owner and approved by AO

**Tip:** eMASS generates most of these from your control inputs. Don't maintain parallel Word \
documents - they will drift.""",
    },
    {
        "slug": "test-result-import",
        "title": "Test Result Import (TRI) for STIGs and Scans",
        "category": "Reference",
        "body": """eMASS can ingest scan results directly via **Test Result Import (TRI)**, which \
auto-populates CCI test results and creates POA&M items for findings.

**Supported formats / sources:**
- **STIG checklist (.ckl)** files from STIG Viewer (manual STIG reviews)
- **SCAP** scan results (XCCDF/OVAL) from a SCAP-validated scanner (HBSS, Tenable.sc, etc.)
- **ACAS / Tenable.sc** vulnerability scans (.nessus or .csv)
- Custom CSVs in the eMASS-published format

**What eMASS does on import:**
1. Parses each finding (CAT I/II/III).
2. Maps to the affected CCI(s) using the STIG-to-CCI / CVE-to-CCI mapping.
3. Updates the CCI test result to **Non-Compliant** if a finding exists.
4. Creates a **POA&M item** if severity exceeds the configured threshold and one doesn't already \
exist.
5. Stamps the **Last Tested** date.

**Why this matters:** Without TRI, you'd manually transcribe hundreds of scan findings into eMASS \
test results - a quick way to introduce errors. With TRI, the data flows from scanner to package.

**Gotchas:**
- TRI doesn't replace the SCA's review; the SCA still has to validate findings, especially \
\"Not a Finding\" / false positives.
- Imported POA&M items have minimal fields populated; you still need to add milestones, mitigations, \
and resource estimates.
- Scan IDs and finding IDs change between scanner versions; mismatches break re-import deltas.""",
    },
    {
        "slug": "common-findings",
        "title": "Common SCA / Auditor Findings (and how to dodge them)",
        "category": "Reference",
        "body": """The same findings come up package after package. Most are unforced errors.

**Top findings:**

1. **Implementation statements that just restate the control text.** Fix: write what *your system* \
does, with named tools and processes.

2. **\"Not Applicable\" without justification.** Fix: every NA needs a one-paragraph rationale tied \
to system architecture or scope.

3. **POA&M items with no milestones or no resource estimate.** Fix: at minimum, set a target date \
and a quarterly milestone.

4. **Inheritance claimed without evidence.** Fix: link the CCP's ATO package; reference the CRM by \
control.

5. **Stale artifacts** (policies dated 2018; STIG checklists from a previous quarter). Fix: ConMon \
scans must be from the last review window (often within 30/60/90 days).

6. **AC-2 (Account Management)** weaknesses - privileged accounts not reviewed, no separation of \
duties, group accounts not justified.

7. **AU-* findings** - audit logs not centralized, no review process documented (\"who reads this \
and how often?\").

8. **CM-2 / CM-6** baseline drift - actual config doesn't match the documented baseline. Fix: SCAP \
scans + a CMDB.

9. **CP-2 / CP-4** - Contingency plan exists but has not been tested (CP-4 wants annual tabletop minimum).

10. **IR-4 / IR-6** - IR plan exists but is generic; no system-specific playbook; no evidence of \
training.

11. **SI-4** - SIEM coverage gaps; alerts don't reach the SOC; no documented IOC review.

12. **SA-22** - System uses unsupported components (EOL software, deprecated libraries). Hard to \
defend; usually requires a POA&M and AO acknowledgment.

13. **CA-3** - System interconnections lack signed MOU/MOA or current ISA.

14. **PL-4** - No Acceptable Use Policy, or AUP not signed by users.

15. **Separation of duties violation** - same person is ISSO and SCA. Auto-fail; restructure.

**Meta-pattern:** Auditors look for **evidence of operations**, not the existence of documents. A \
beautifully written IR plan that nobody trains to is a finding.""",
    },
    {
        "slug": "ppsm-hwsw",
        "title": "Hardware/Software Inventory & PPSM",
        "category": "Reference",
        "body": """Two often-neglected eMASS housekeeping items that are reviewed in every audit.

**Hardware/Software (HW/SW) Inventory:**
- Required by **CM-8 (Information System Component Inventory)**.
- eMASS has dedicated tabs for HW and SW lists; the package is reviewed for completeness.
- Each item should include vendor, model/version, location, function, and owner.
- Tied to vulnerability management - your scanner inventory and your CM-8 list should reconcile. \
Auditors love to find a server scanned by ACAS that isn't in CM-8.

**Software currency:** The list should reflect approved versions. EOL software triggers SA-22 \
findings.

**PPSM (Ports, Protocols, and Services Management):**
- Required for any DoD system that connects to a DoD network.
- You register every port/protocol/service the system uses on or across boundaries with the **DoD \
PPSM Registry** (a separate system from eMASS).
- The **PPSM Category Assurance List (CAL)** rates each port/protocol as Acceptable, Acceptable with \
mitigations, or Unacceptable.
- Findings: using \"Unacceptable\" PPSM-CAL items, or running ports not in the registration.

**Why this matters:**
- HW/SW gaps undermine *every* CM, RA, and SI control - you can't protect what isn't inventoried.
- PPSM violations stop ATC requests; they're a gating item for connecting to DoD networks.

**Tooling:**
- HW/SW: feed from a CMDB (ServiceNow, etc.) into eMASS via CSV imports.
- PPSM: separate workflow at https://public.cyber.mil/ppsm/ (registration is on .mil only).""",
    },
    {
        "slug": "privacy-overlay",
        "title": "Privacy Overlay (CNSSI 1253 Annex F-Privacy)",
        "category": "Reference",
        "body": """When a DoD system processes **Personally Identifiable Information (PII)** or \
Protected Health Information (PHI), the **Privacy Overlay** applies - a defined set of additional \
controls and parameter modifications layered onto the baseline.

**Triggers:**
- The system stores, processes, or transmits PII (federal employee, contractor, dependent, beneficiary)
- The system processes PHI (covered under HIPAA / Privacy Act)
- Inherits from a system that does

**What the overlay does:**
- Adds the **PT-* family** (Personally Identifiable Information Processing and Transparency) - Rev. 5 \
specific
- Adds privacy-specific parameters to many AC, AU, IR, MP, SC controls
- Requires a **Privacy Impact Assessment (PIA)** under the E-Government Act
- Requires a **System of Records Notice (SORN)** if the system is a Privacy Act system of records

**eMASS handling:**
- Apply the Privacy Overlay during Step 2 (Select).
- The control list expands automatically.
- Privacy-specific roles (Senior Agency Official for Privacy, SAOP) appear in workflows.
- The SCA's testing includes the privacy controls.

**Common gotchas:**
- Forgetting the SORN for a Privacy Act system.
- Treating PII as binary - eMASS asks for **PII confidentiality impact level** (Low/Moderate/High) \
which can drive additional controls beyond the overlay.
- Inheriting privacy controls from an enclave that doesn't actually cover your PII processing.""",
    },
    {
        "slug": "workflows-signatures",
        "title": "Workflows, CCB, and Package Submission",
        "category": "Reference",
        "body": """eMASS is workflow-driven. Almost every change moves through a sequence of approvals.

**Common workflows:**
- **Implementation submission**: ISSO drafts → ISSM reviews → SCA assesses → AO authorizes
- **POA&M update**: ISSO updates → ISSM approves → AO acknowledges (for risk acceptance)
- **Significant change**: triggers a re-review at the level matching the change scope - sometimes \
a full re-authorization
- **Document upload**: ISSO uploads → ISSM approves → becomes part of the package
- **Annual review**: scheduled checklist; ISSO walks through assigned controls; ISSM signs off

**CCB (Configuration Control Board):** A board of stakeholders (AO rep, SCA rep, system owner, \
operations) that approves significant changes to the authorized configuration. eMASS doesn't run \
the CCB - your program does - but CCB outputs (ECPs, change records) get attached to the package.

**Package submission:**
1. ISSO completes implementation in eMASS.
2. ISSM submits the package for assessment.
3. SCA performs the assessment, enters test results, generates SAR.
4. ISSM/ISSO addresses any pre-decision findings (e.g., re-test required).
5. Package routed to AODR / AO for decision.
6. AO signs Authorization Decision Document; ATO date set; expiration tracked.

**Notifications:**
- eMASS emails workflow steps to assigned users.
- Bottlenecks usually happen at SCA (capacity-constrained) and AO (long signature queues). Build \
schedule slack accordingly.

**Tip:** Pre-stage your package by walking the SCA through implementation statements before formal \
submission. A pre-assessment in Step 3 turns a 6-month formal cycle into 6 weeks.""",
    },
    {
        "slug": "reports",
        "title": "Useful eMASS Reports",
        "category": "Reference",
        "body": """eMASS includes a **Reports** module with hundreds of pre-built reports. The ones \
practitioners actually use:

- **Test Results Summary** - status of every CCI; great pre-AO sanity check.
- **POA&M Status Report** - open items, by severity, with aging.
- **POA&M Aging Report** - items past their scheduled completion date.
- **Implementation Status Report** - per-control implementation progress.
- **Authorization Status Report** - ATO expiration timeline; useful for portfolio AOs tracking dozens \
of systems.
- **Inheritance Report** - what your system inherits from where.
- **Hardware/Software Inventory Report** - exportable list for reconciliation.
- **Vulnerability Management Report** - scan-derived findings tied to CCIs.
- **System Categorization Report** - quick view of FIPS 199 + overlays.
- **eMASS Annual Review Workbook** - checklist used during annual self-assessment.

**Export formats:** PDF, Word, Excel.

**Custom reports:** Power users build CSV exports and process in Excel/Power BI for portfolio views \
across many systems.

**Tip for AOs:** Schedule a recurring POA&M Aging Report and Authorization Expiration Report - \
these surface the package risks before they become missed deadlines.""",
    },
    {
        "slug": "tips-onboarding",
        "title": "Onboarding to eMASS - Practical Tips",
        "category": "Reference",
        "body": """If you just got assigned an eMASS account on a system, here's the orientation \
nobody gives you.

**Day 1:**
1. Get your CAC working with eMASS - the first login often fails because of cert chains. Use IE / \
Edge in IE mode if you must.
2. Confirm your role is correct (ISSO/ISSM/SCA-R, etc.) for the system you're working on. Roles \
are per-system; getting added takes a request and approval.
3. Open the eMASS User Guide PDF (linked from inside eMASS). It's the canonical reference.
4. Find the **System Profile** of your system and read the SSP, SAR (if any), and POA&M end-to-end.

**Week 1:**
- Map every control to its **Implementation Status**. Note which are Inherited, which are System-Specific, \
which are Planned.
- For Inherited controls, identify the CCP and pull their CRM.
- Identify the next ATO expiration date. Set a calendar reminder 6 months prior.
- Walk the **Authorization Boundary Diagram**. If it's missing or ancient, that's your first task.

**Month 1:**
- Establish a ConMon rhythm: who runs scans, who reviews them, who updates eMASS.
- Aging POA&M items: triage and either close or rebaseline with new milestones.
- Identify your top 3 audit risks and start fixing them.

**Working efficiently:**
- Implementation statements are your biggest time sink. **Templates per family** save hours - start \
with the previous package's good statements.
- Use the eMASS **bulk edit** features for status changes across many CCIs.
- Don't fight eMASS's UX. It's a 2010s-era app. Plan to spend time clicking.

**Where to get help:**
- DISA eMASS support: tickets through the IDeA portal
- Your service-level RMF community of practice
- The eMASS User Guide (PDF) and DISA's RMF training site (cs.signal.army.mil, jko.jten.mil)""",
    },
    {
        "slug": "ui-walkthrough",
        "title": "eMASS UI Walkthrough: The Tabs You'll Live In",
        "category": "Reference",
        "body": """eMASS organizes a system package across a series of tabs. Most of your day-to-day \
clicks happen in the same handful.

**Top-level system tabs (typical layout):**

| Tab | What lives here | Who uses it most |
| --- | --- | --- |
| **System Information** | Name, registration number, type, owner, AO/SCA assignment, categorization, overlays, MAC/CL | ISSO/ISSM (setup); AO (review) |
| **Authorization Information** | ATO/IATT/ATC dates, package status, signed ADD, prior decisions | AO/AODR; portfolio managers |
| **Controls** | Implementation status per control, narrative, CCP, CCIs, test results | ISSO (write); SCA (test) |
| **Tests** | All test results aggregated; can filter by status/family | SCA |
| **POA&M** | Open and closed weaknesses, milestones, severity | ISSO + ISSM (work them); AO (accept) |
| **Artifacts** | Document repository: SSP, SAR, RAR, AUP, diagrams, scans | ISSO uploads; SCA reviews |
| **System Categorization** | FIPS 199 categorization detail, info types, overlays | ISSO; auditors |
| **System Plan / SSP** | Auto-generated from your control inputs | ISSO; auditors |
| **Hardware/Software** | CM-8 inventory | ISSO; SCA |
| **Ports/Protocols** | PPSM registration links | ISSO |
| **Connections** | System interconnections + ISAs | ISSO |
| **Workflow / Tasks** | Pending approvals routed to you | Everyone |
| **Reports** | Pre-built and custom reports | Everyone |

**Navigation tips:**
- Bookmark your system's URL once you find it. Search by registration number is faster than \
clicking through menus.
- The top **Tasks / Workflow** banner is where pending approvals land. Check it before doing \
anything else.
- Most tabs have a **Bulk Edit** mode (icon at top right). Save hours of clicking when changing \
status across many CCIs.
- Filtering is *per-column* on most data tables. Power users compose filters across columns \
(e.g., status=Non-Compliant AND family=AC).""",
    },
    {
        "slug": "tasks-workflow",
        "title": "eMASS Tasks & Workflow Inbox",
        "category": "Reference",
        "body": """The **Tasks** view is your inbox. Every workflow step that needs your action \
shows up here with a deadline.

**Common task types:**

- **Implementation Sub Review** - your ISSO has submitted controls; you (ISSM) review.
- **Assessment Submission** - SCA has finished testing; ISSM verifies before AO routing.
- **Authorization Submission** - package routed to AO/AODR for decision.
- **POA&M Submission** - new POA&M items awaiting ISSM approval.
- **Risk Acceptance** - High/Very-High severity POA&M needing AO acknowledgment.
- **Document Submission** - artifact uploaded; reviewer must approve.
- **Annual Review** - scheduled control re-review.
- **Significant Change Notification** - notify AO of material change.

**Workflow actions:**

| Action | Effect |
| --- | --- |
| **Approve** | Advance to next role. |
| **Return** | Send back with comments for rework. |
| **Reassign** | Hand the task to another user with the same role. |
| **Override** | Force advance (privileged role only; logged). |
| **Withdraw** | Submitter cancels their submission. |

**Notifications** are emailed by default. Configurable per user. Don't disable them - \
forgetting an approval blocks an entire ATO cycle.

**Reality check on cycle times:**
- ISSM review: hours to days.
- SCA assessment: weeks to months (depends on package size + tester availability).
- AO signature: days to months. Build slack.

**SLA tracking:** eMASS doesn't enforce SLAs but reports show task age. AO offices often have \
internal target SLAs (e.g., 14 days for routine ATO renewal).""",
    },
    {
        "slug": "system-registration",
        "title": "Registering a New System in eMASS",
        "category": "Lifecycle",
        "body": """Before you can do anything else, the system must be registered in eMASS. The \
registration request goes through your service or agency's eMASS administrator.

**Information you'll need to gather:**

- **System name** (formal title, not an acronym).
- **Acronym / short name** (used in URLs and exports).
- **Owner organization** and points of contact (System Owner, ISSO, ISSM, PM).
- **Authorizing Official** assignment.
- **System Type** - Major Application, General Support System, Platform IT, Mission System, etc.
- **Confidentiality / Integrity / Availability** preliminary impact (you'll refine in Step 1).
- **MAC** (I/II/III) and **Confidentiality Level** (Public / Sensitive / Classified).
- **Overlays** anticipated (Privacy, Cross Domain, Intelligence, Classified, Space, ICS).
- **Description / Mission statement** - one paragraph the AO will read.
- **Boundary description** - what's in, what's out.
- **Hosting environment** - on-prem, FedRAMP cloud, DoD cloud, etc.
- **Data types** processed (rough cut from 800-60).

**The request flow:**

1. ISSO/ISSM fills out the registration request form (often a service-level template).
2. Service-level eMASS administrator (or DISA admin) creates the system record.
3. Roles are assigned (ISSO, ISSM, SCA, AO, AODR, etc.) per the request.
4. System Owner confirms initial info.
5. Now you can start Step 1 (Categorize).

**Common rookie mistakes:**

- Picking the wrong **System Type**. Major Application vs Platform IT changes which controls \
apply and which AO routes the package. Get it right up front.
- Wrong AO assignment - some packages need a specific AO (Service-level vs Agency-level vs \
DoD-CIO depending on type/sensitivity).
- Acronym collision with existing systems. Search before requesting.

**De-registration / decommissioning:** When a system is sunsetted, the package transitions to \
**Decommissioned** state. The historical record persists; future reciprocity reviews can still \
reference it.""",
    },
    {
        "slug": "scoring",
        "title": "How eMASS Scores Your Package (Score, Risk, Status)",
        "category": "Reference",
        "body": """eMASS computes several rolled-up scores and statuses you'll see on dashboards.

**Implementation Status (per control):**
- **Implemented** - control is in place.
- **Inherited** - covered by a CCP.
- **Not Applicable** - documented justification.
- **Planned** - will be implemented by a target date.
- **Manually Inherited** - hybrid control where you do part.

**Test Result Status (per CCI):**
- **Compliant** - passed assessment.
- **Non-Compliant** - failed; POA&M generated.
- **Not Applicable** - control objective doesn't apply.
- **Not Reviewed** - not yet tested (shouldn't appear in a finalized package).

**Calculated package metrics:**

| Metric | What it means |
| --- | --- |
| **Compliance Score** | % of CCIs in Compliant + Inherited + N/A status (out of total). |
| **Implementation Score** | % of controls in Implemented + Inherited + N/A. |
| **Risk Score** | Aggregated severity of open POA&M items (often a CVSS-weighted sum). |
| **Test Coverage** | % of CCIs with a recorded test result (Compliant or Non-Compliant). |
| **Open Findings (by severity)** | Count of POA&M items: Very Low / Low / Moderate / High / Very High. |

**Color coding** (typical):
- Green: ready / compliant.
- Yellow: minor issues, in-progress.
- Red: blocking issues, expired ATO, overdue POA&M.

**Authorization Decision color** is what executives see first - keep it green or have a story.

**Scoring quirks to know:**
- "Not Reviewed" CCIs don't penalize the compliance score on some dashboards but ARE flagged in \
package readiness reports.
- Inherited controls show inherited scores from the CCP; if the CCP's package degrades, yours \
does too.
- Manual overrides require justification fields - leaving them blank fails review.""",
    },
    {
        "slug": "scan-ingestion",
        "title": "Vulnerability Scan Ingestion (ACAS / Tenable / SCAP)",
        "category": "Reference",
        "body": """eMASS doesn't run scans, but it ingests them via **Test Result Import (TRI)** and \
the **Vulnerability Management** module.

**Supported scanners:**
- **ACAS** (Tenable.sc / Tenable.io) - DoD's enterprise vuln scanner.
- **SCAP** scanner - any SCAP 1.2 / 1.3 validated tool (HBSS, OpenSCAP, etc.).
- **STIG Viewer** checklists (.ckl) - manual STIG reviews.
- **Custom CSV** - eMASS publishes a header format for arbitrary findings.

**What happens on import:**

1. Findings are parsed and de-duplicated against existing eMASS records.
2. Each finding is mapped to its associated **CCIs** (via STIG-to-CCI mapping for STIG findings, \
or CVE-to-CCI for vuln findings - though CVE mapping is sparse).
3. Existing CCI test results are updated to **Non-Compliant** if a finding exists.
4. POA&M items are auto-created for findings exceeding the configured severity threshold (often \
CAT II+).
5. **Last Test Date** stamp is updated.

**Cadence:** DoD typically expects:
- ACAS scans: weekly (some systems daily).
- STIG checklists: quarterly per asset (or on configuration change).
- All scan data uploaded to eMASS within 30 days.

**Common pitfalls:**

- **Duplicate POA&M creation** when a scan re-runs. eMASS tries to dedupe by finding ID; mismatch \
on plugin IDs across scanner versions causes duplicates.
- **Asset reconciliation** - findings against assets not in your CM-8 inventory get dropped or \
flagged.
- **False positives** - SCA must review and mark them Not Applicable with justification, \
otherwise POA&M continues to age.
- **Closed findings** that re-appear (regression) - eMASS reopens them; track why your patching \
didn't stick.""",
    },
    {
        "slug": "package-deliverables",
        "title": "Package Deliverable Checklist (What the AO Sees)",
        "category": "Reference",
        "body": """When the package goes to the AO, here's what the executive summary contains. \
Build the package with this in mind from day one.

**Required for any ATO submission:**

| Item | Source |
| --- | --- |
| **Authorization Decision Document (ADD)** | Generated; AO signs |
| **Executive Summary / Risk Recommendation** | SCA's narrative |
| **System Security Plan (SSP)** | Auto-generated from controls + narrative |
| **Security Assessment Report (SAR)** | Generated from test results; SCA signs |
| **Risk Assessment Report (RAR)** | Per NIST 800-30; ISSM authors |
| **Plan of Action & Milestones (POA&M)** | Live record; ISSM/AO sign |
| **System Categorization** | FIPS 199 worksheet, signed |
| **Authorization Boundary Diagram** | Architecture team |
| **Network Diagram** | Architecture team |
| **Hardware List** (CM-8) | CMDB feed |
| **Software List** (CM-8) | CMDB feed |
| **Data Flow Diagrams** | Architecture team |
| **Continuous Monitoring Strategy** (CA-7) | ISSM/CISO |
| **Configuration Management Plan** (CM-9) | CMDB owner |
| **Incident Response Plan** (IR-8) | SOC/IR team |
| **Contingency Plan** (CP-2) | Operations |
| **Privacy Impact Assessment** (if PII) | Privacy office |
| **Memoranda of Agreement / ISAs** (CA-3) | Inter-system links |
| **Acceptable Use Policy** (PL-4) | HR/Security |
| **PPSM registration** | PPSM Registry |
| **Training records** | LMS |

**Optional but commonly requested:**
- Penetration test report (often required at HIGH baseline)
- Source code review (for custom dev systems)
- Third-party SOC 2 / FedRAMP letters (for inherited services)
- Business Impact Analysis (BIA)

**Tip:** Most AOs read the **Executive Summary**, scan the **POA&M aging chart**, then \
spot-check **3-5 controls** of their choosing. Make the summary great; nail the POA&M; have \
strong implementation statements for the controls likely to be sampled (AC-2, AU-6, IR-4, \
SI-4, RA-5).""",
    },
    {
        "slug": "ato-renewal",
        "title": "ATO Renewals & Re-Authorization",
        "category": "Lifecycle",
        "body": """ATOs typically expire on a 3-year cycle (1-year IATTs are common). Renewing or \
re-authorizing requires planning.

**Three pathways at expiration:**

1. **Renewal** - same system, same scope, controls re-assessed (often a subset rotation), package \
updated. Common when no significant change has occurred.
2. **Re-Authorization** - significant change has occurred (architecture, scope, classification). \
Full re-do.
3. **Decommission** - sunset the system; transition users; archive evidence.

**Renewal timeline (typical):**
- **T-12 months** - Plan: identify staffing, SCA capacity, control rotation scope.
- **T-9 months** - Begin updates: refresh artifacts, narratives, scan results, training records.
- **T-6 months** - Submit to SCA.
- **T-3 months** - SAR complete; address findings.
- **T-1 month** - AO signature.
- **T-0** - New ATO date set.

**Significant change examples** that trigger re-authorization (vs renewal):
- Cloud migration / new hosting environment.
- Major architecture change (monolith to microservices).
- Categorization change (Mod -> High).
- Adding a new data type (e.g., introducing PII).
- Adding/removing major interconnections.
- Change in mission, classification, or AO.

**Continuous Authorization (cATO)** model:
- Eliminates the 3-year cycle in favor of ongoing automated assessment.
- Requires investment in: SCAP automation, scan continuous integration, real-time POA&M, robust \
ConMon, and AO comfort with telemetry-based decisions.
- Increasingly encouraged by DoD CIO; few orgs have fully achieved it.

**Late renewal consequences:** ATO expires - system must shut down. There are emergency \
extension paths (typically 30-90 days) but each one is a separate AO decision and reflects \
poorly on the program. Don't let it happen.""",
    },
    {
        "slug": "iatt-to-ato",
        "title": "IATT to ATO Transition",
        "category": "Lifecycle",
        "body": """An **IATT (Interim Authority to Test)** lets a system operate in a test environment \
- often with production-like data - while finishing implementation. Most IATTs are stepping \
stones to a full ATO.

**Typical IATT use cases:**
- **Live testing with real data** that wouldn't be possible in pure dev.
- **Pilot deployments** with limited user populations.
- **Operational test events** (e.g., DT/OT for weapons systems).
- **Migration cutovers** before going to full prod.

**IATT constraints (commonly imposed by AO):**
- Time-boxed (typically 6 months; sometimes extendable once).
- Restricted user population.
- Restricted data set or classification.
- Specific test environment isolation.
- Reduced control set (some controls deferred until ATO).

**Transitioning to full ATO:**

1. **Resolve deferred controls** - all controls that were waived or partially implemented for \
IATT must now be fully addressed.
2. **Production-grade evidence** - artifacts must reflect the production deployment, not the test \
one. Re-test with prod configurations.
3. **Risk Assessment update** - re-do the RAR with the production picture.
4. **POA&M reconciliation** - close items mitigated; rebaseline what's still open.
5. **Boundary diagram update** - production boundary is usually broader than test.
6. **Submit for ATO** as a new package decision (often as an addendum or full re-submission, \
depending on AO).

**Pitfall:** Treating IATT as "good enough." Some teams operate under serial IATT extensions \
because ATO never gets fully done. AOs and IGs notice. Plan IATT-to-ATO transition from day one.""",
    },
    {
        "slug": "emass-instances",
        "title": "eMASS Instances: NIPR, SIPR, JWICS, Cloud",
        "category": "Reference",
        "body": """There isn't one eMASS - there are multiple instances mapped to network and \
classification level.

| Instance | Network | Use |
| --- | --- | --- |
| **eMASS NIPR** | NIPRNet (Unclassified) | Most DoD systems |
| **eMASS SIPR** | SIPRNet (Secret) | Classified systems up to Secret |
| **eMASS JWICS** | JWICS (TS/SCI) | Top Secret / SCI systems |
| **DoN eMASS** | Navy/Marine instance | Department of the Navy |
| **NGA eMASS** | NGA instance | National Geospatial-Intelligence Agency |
| **Other agency** | Various | NSA, NRO, etc. typically have their own |

**Practical implications:**

- A package on NIPR cannot be moved to SIPR by export-import; the system is re-registered on the \
target instance.
- Cross-instance reciprocity exists but is documented separately (e.g., NIPR eMASS package \
referenced in a SIPR registration).
- Access to each instance requires separate accounts and CAC privileges.
- The eMASS API is per-instance.

**Cloud / commercial environment:** Systems hosted in DoD-authorized cloud (Cloud One, Platform \
One, etc.) still register in the appropriate eMASS instance. The cloud service provider has its \
own ATO; your tenant inherits applicable controls via the CRM.

**Common confusion:** "eMASS" often refers to the NIPR instance by default. When discussing a \
classified system, always specify which instance you mean.""",
    },
    {
        "slug": "emass-api",
        "title": "eMASS REST API (for Automation)",
        "category": "Reference",
        "body": """eMASS has a REST API used to automate package data exchange. It's not commonly used \
by individual ISSOs but central to ConMon automation.

**What you can do with the API:**

- Pull all controls, test results, POA&M items, artifacts.
- Submit test results / POA&M updates programmatically.
- Push scan results from your CI/CD or scan automation pipeline.
- Pull workflow statuses and tasks.
- Sync CMDB inventory into eMASS HW/SW lists.

**Authentication:**

- **CAC-based mutual TLS** for individual users (rare in API contexts).
- **PKI client certificate** for service accounts. Issued by DISA; tightly scoped.
- API access is granted per-system; a service account can only touch systems it's authorized for.

**Typical integrations:**

| Integration | Purpose |
| --- | --- |
| **Tenable / ACAS -> eMASS** | Push scan findings -> auto-create POA&M |
| **CMDB -> eMASS** | Sync HW/SW inventory (CM-8) |
| **GitOps / CI -> eMASS** | Auto-update artifacts on release |
| **Internal dashboards** | Pull eMASS data into your own ConMon dashboard |
| **Splunk / SIEM** | Cross-reference findings with control coverage |

**Common pain points:**

- Documentation can be sparse and version-specific. Service-level eMASS teams maintain internal \
guides.
- Rate limits exist; respect them or get throttled.
- Field semantics can vary between eMASS versions; test against your target instance.
- API access requests have a long lead time. Start the request 6+ months before you need it.

**Vendor tools that integrate:** Telos Xacta, RegScale, SteelCloud ConfigOS, RiskAware, and \
custom government solutions. Many large primes have built internal eMASS adapters.""",
    },
    {
        "slug": "common-overlays",
        "title": "DoD Overlays: Privacy, Cross-Domain, Classified, ICS, Space",
        "category": "Patterns",
        "body": """An **overlay** modifies the baseline by adding controls, removing them, or changing \
parameter values. CNSSI 1253 publishes the official overlays for National Security Systems.

**Common DoD overlays:**

| Overlay | Triggers when... | Typical effect |
| --- | --- | --- |
| **Privacy** | System processes PII | Adds PT-* family + privacy parameters across many controls; requires PIA + SORN |
| **Classified** | System processes classified data | Adds PE controls (TEMPEST, classified material handling), AC tightening |
| **Cross-Domain Solution (CDS)** | Information moves between security domains | Adds NSA-mandated controls, requires CDS-NCDSMO accreditation in addition to ATO |
| **Intelligence** | IC-relevant information | Adds ICD 503-aligned controls |
| **Space Platform** | Spacecraft / satellite systems | Adds latency / RF / on-orbit lifecycle controls |
| **Industrial Control Systems (ICS)** | OT / SCADA / building control | Adds IEC 62443-aligned, modifies SC and SI for OT realities |
| **Tactical** | Battlefield / deployed environments | Adjusts for intermittent connectivity, austere conditions |
| **PIT** | Platform IT (e.g., weapon systems) | Tailors many enterprise IT controls |

**Applying overlays in eMASS:**

1. Identify applicable overlays during Step 1 (Categorize).
2. Apply them in Step 2 (Select). eMASS recalculates the control set.
3. Document the overlay rationale in the SSP narrative.
4. Implement the added controls per the overlay's parameter values.

**Stacking overlays:** Multiple overlays often apply (e.g., Classified + Cross-Domain + Intel \
for a TS/SCI CDS). Each adds requirements. Where overlays conflict, the more restrictive wins.

**Common error:** Forgetting an overlay and discovering it during SCA assessment. By then \
hundreds of controls may need rework. Get overlay scoping right early - involve the AO and \
service-level RMF office.""",
    },
    {
        "slug": "common-acronyms-quickref",
        "title": "eMASS Acronym Quick-Reference",
        "category": "Reference",
        "body": """A condensed glossary of acronyms you'll encounter in any eMASS package. (See the \
**Glossary** tab for the full list.)

**Authorization decisions:**
- **ATO** Authority to Operate (3-year typical)
- **IATT** Interim Authority to Test (6-month typical)
- **ATC** Authority to Connect (network connection only)
- **DATO** Denial of Authority to Operate
- **cATO** Continuous ATO

**Roles:**
- **ISSO** Information System Security Officer (day-to-day owner)
- **ISSM** Information System Security Manager (supervisor of ISSOs)
- **ISSE** Information Systems Security Engineer
- **SCA** Security Control Assessor (independent tester)
- **AO** Authorizing Official (signs the ATO)
- **AODR** AO Designated Representative
- **PM/SM** Program/System Manager

**Documents:**
- **SSP** System Security Plan
- **SAR** Security Assessment Report
- **RAR** Risk Assessment Report
- **POA&M** Plan of Action and Milestones
- **ADD** Authorization Decision Document
- **PIA** Privacy Impact Assessment
- **SORN** System of Records Notice
- **MOU/MOA/ISA** Memo of Understanding/Agreement / Interconnection Security Agreement
- **CRM** Customer Responsibility Matrix (from CCP)
- **AUP** Acceptable Use Policy

**Concepts:**
- **CCI** Control Correlation Identifier
- **STIG** Security Technical Implementation Guide
- **SRG** Security Requirements Guide
- **CCP** Common Control Provider
- **ConMon** Continuous Monitoring
- **CCB** Configuration Control Board
- **PPSM** Ports, Protocols, and Services Management
- **TRI** Test Result Import
- **ACAS** Assured Compliance Assessment Solution
- **SCAP** Security Content Automation Protocol

**Frameworks:**
- **RMF** Risk Management Framework (NIST SP 800-37)
- **DoDI 8510.01** DoD Instruction implementing RMF
- **FIPS 199 / 200** Federal categorization / minimum requirements
- **CNSSI 1253** NSS categorization standard
- **NIST SP 800-53 / 53A / 53B** Controls / Assessment / Baselines

**Severity:**
- **CAT I/II/III** Vulnerability finding categories (highest to lowest)
- **CVSS** Common Vulnerability Scoring System

**Networks:**
- **NIPR** Non-classified IP Router Network
- **SIPR** Secret IP Router Network
- **JWICS** Joint Worldwide Intelligence Communications System (TS/SCI)""",
    },
]


GLOSSARY: dict[str, str] = {
    # Authorization decisions
    "ATO": "Authority to Operate. The signed authorization that lets a DoD system run in production. Granted by the Authorizing Official (AO) for up to 3 years (or indefinitely under cATO).",
    "IATT": "Interim Authority to Test. Temporary authorization (typically 6 months) to operate in a test environment with real data, before full ATO.",
    "ATC": "Authority to Connect. Authorization to connect a system to a network or enclave. Different from ATO - it covers the connection, not the system itself.",
    "DATO": "Denial of Authority to Operate. AO has determined the residual risk is unacceptable; system cannot operate.",
    "cATO": "Continuous ATO. Modern model where ongoing automated assessment + human review replaces the 3-year re-authorization cycle.",

    # Roles
    "AO": "Authorizing Official. Senior official who accepts residual risk and signs the ATO. Often a flag officer or SES.",
    "AODR": "AO Designated Representative. Acts on behalf of the AO for routine package actions.",
    "ISSO": "Information System Security Officer. Day-to-day owner of the security package and the person who does most of the eMASS data entry.",
    "ISSM": "Information System Security Manager. Supervises one or more ISSOs; reviews packages before SCA submission.",
    "ISSE": "Information Systems Security Engineer. Provides technical engineering input on the system's security architecture.",
    "SCA": "Security Control Assessor. Independently tests controls and produces the SAR. Must be organizationally independent of the ISSO/ISSM.",
    "SCA-R": "Security Control Assessor Representative. Performs assessments on behalf of the SCA.",
    "PM": "Program Manager. Owns budget, schedule, and mission for the system.",
    "SO": "System Owner. Senior person responsible for the system overall (sometimes the same as PM).",
    "User Rep": "User Representative. Speaks for the operational user community of the system.",

    # Documents
    "SSP": "System Security Plan. The package document describing the system, boundary, categorization, and how each control is implemented.",
    "SAR": "Security Assessment Report. The SCA's record of what was tested and the results.",
    "POA&M": "Plan of Action and Milestones. Open security weaknesses, the plan to fix them, and target dates.",
    "RAR": "Risk Assessment Report. Mission/business risk picture (NIST 800-30).",
    "ADD": "Authorization Decision Document. The signed letter granting (or denying) ATO.",
    "PIA": "Privacy Impact Assessment. Required when a system processes PII.",
    "SORN": "System of Records Notice. Public Federal Register notice required when a system is a Privacy Act system of records.",
    "ISA": "Interconnection Security Agreement. Documents the security terms of a connection between two systems with different ATOs.",
    "MOU": "Memorandum of Understanding. Less formal than an ISA; often used for inter-system relationships.",
    "MOA": "Memorandum of Agreement. Formal agreement between organizations on responsibilities.",
    "CRM": "Customer Responsibility Matrix. CCP-published list of which controls/CCIs the provider covers and which are customer responsibility.",
    "AUP": "Acceptable Use Policy. Rules of Behavior signed by users (PL-4).",

    # Frameworks / standards
    "RMF": "Risk Management Framework. NIST SP 800-37 process for authorizing federal systems.",
    "NIST": "National Institute of Standards and Technology. Publishes the SP 800-* series.",
    "FIPS 199": "Federal Information Processing Standard for security categorization (Low/Moderate/High by Confidentiality/Integrity/Availability).",
    "FIPS 200": "Minimum security requirements for federal systems.",
    "CNSSI 1253": "Committee on National Security Systems Instruction defining categorization for National Security Systems and the privacy/classified overlays.",
    "DoDI 8510.01": "DoD Instruction implementing RMF in the Department of Defense.",
    "FedRAMP": "Federal Risk and Authorization Management Program. Standardized cloud security authorization for federal agencies; FedRAMP Moderate ≈ DoD IL2/IL4.",
    "CMMC": "Cybersecurity Maturity Model Certification. DoD certification framework for contractors handling FCI/CUI.",

    # Concepts
    "CCI": "Control Correlation Identifier. DoD's atomic decomposition of NIST 800-53 controls; used for compliance tracking and STIG mapping.",
    "STIG": "Security Technical Implementation Guide. DISA-published configuration hardening guidance for products.",
    "SRG": "Security Requirements Guide. Higher-level DISA guidance from which STIGs are derived.",
    "CCP": "Common Control Provider. An organization or system that implements controls inherited by other systems.",
    "Inheritance": "Relying on another system/provider's implementation of a control instead of implementing it yourself.",
    "Type Authorization": "A single ATO covering multiple identically-deployed instances of the same system.",
    "Reciprocity": "One AO accepting another's existing ATO without repeating the assessment.",
    "ConMon": "Continuous Monitoring. Ongoing scanning, review, and POA&M maintenance after ATO.",
    "CCB": "Configuration Control Board. Stakeholder body that approves changes to the authorized baseline.",
    "ECP": "Engineering Change Proposal. Formal change record reviewed by the CCB.",
    "PPSM": "Ports, Protocols, and Services Management. DoD registry and category-assurance list for network ports/protocols.",
    "PPSM CAL": "PPSM Category Assurance List. Rates each port/protocol as Acceptable / Acceptable-with-mitigation / Unacceptable.",

    # Categorization / data
    "MAC": "Mission Assurance Category. DoD legacy field (I/II/III) often still required.",
    "CL": "Confidentiality Level. DoD legacy field (Public / Sensitive / Classified).",
    "PII": "Personally Identifiable Information. Triggers the Privacy Overlay if processed.",
    "PHI": "Protected Health Information. Triggers Privacy Overlay + HIPAA considerations.",
    "FCI": "Federal Contract Information. Lower-sensitivity contractor data covered by FAR/DFARS.",
    "CUI": "Controlled Unclassified Information. Sensitive unclassified data; basis for CMMC controls.",

    # eMASS-specific terms
    "TRI": "Test Result Import. eMASS feature that ingests STIG/SCAP/ACAS scan results and updates CCI test statuses.",
    "ACAS": "Assured Compliance Assessment Solution. DoD's enterprise vulnerability scanner (Tenable-based).",
    "SCAP": "Security Content Automation Protocol. NIST standard for machine-readable security content (XCCDF/OVAL/CPE/CCE/CVE).",
    "HBSS": "Host Based Security System. Legacy DoD endpoint security suite (largely replaced by ESS).",
    "ESS": "Endpoint Security Solution. Successor to HBSS.",
    "Significant Change": "A change to the authorized system that materially affects security; triggers re-authorization.",
    "Common Control": "A control implemented once for use by many systems (typically by a CCP).",
    "Hybrid Control": "A control where part is inherited and part is system-specific.",

    # Severity / impact
    "CAT I": "Category I finding. Vulnerabilities that allow an attacker immediate access. Highest severity.",
    "CAT II": "Category II finding. Vulnerabilities that have a high potential of giving access.",
    "CAT III": "Category III finding. Vulnerabilities that provide information for a more serious attack.",
    "CVSS": "Common Vulnerability Scoring System. Numeric severity score (0-10) used in POA&M severity fields.",

    # Networks / instances
    "NIPR": "Non-classified Internet Protocol Router Network. The unclassified DoD network. Default eMASS instance.",
    "SIPR": "Secret IP Router Network. Classified DoD network up to Secret. Has its own eMASS instance.",
    "JWICS": "Joint Worldwide Intelligence Communications System. TS/SCI network. Has its own eMASS instance.",
    "DISN": "Defense Information System Network. The DoD's enterprise network infrastructure.",
    "DREN": "Defense Research and Engineering Network.",
    "GIG": "Global Information Grid. Older term for DoD's enterprise network.",

    # Cloud / hosting
    "Cloud One": "Air Force-managed enterprise cloud (Azure / AWS GovCloud).",
    "Platform One": "Air Force-managed DevSecOps platform (Iron Bank, Big Bang).",
    "Iron Bank": "DoD's hardened-container repository (part of Platform One).",
    "Big Bang": "DoD's reference DevSecOps platform stack.",
    "milCloud 2.0": "DISA-managed DoD cloud (legacy / transitioning).",
    "IL2": "DoD Impact Level 2. Public + non-critical info.",
    "IL4": "DoD Impact Level 4. CUI / non-public.",
    "IL5": "DoD Impact Level 5. Higher-sensitivity CUI / National Security Systems.",
    "IL6": "DoD Impact Level 6. Classified up to Secret.",

    # Cross-domain / specialty
    "CDS": "Cross-Domain Solution. Tech that allows controlled info movement across security domains.",
    "NCDSMO": "National Cross Domain Strategy and Management Office. Authorizes CDS deployments.",
    "TEMPEST": "NSA standard for emanations security (preventing classified leakage via electromagnetic emissions).",

    # APIs / automation
    "OSCAL": "Open Security Controls Assessment Language. NIST machine-readable format for controls/profiles/assessments. Increasingly used to automate eMASS workflows.",
    "TRI": "Test Result Import. eMASS feature ingesting STIG/SCAP/ACAS scan results to update CCI test statuses.",

    # Org structures
    "ECSM": "Enterprise Cybersecurity Management.",
    "DAOA": "Designated Approving / Authorizing Official Authority.",
    "DCO": "Defensive Cyberspace Operations.",
    "PIT": "Platform Information Technology. Specialized IT embedded in weapons/platforms.",

    # Lifecycle / process
    "ECP": "Engineering Change Proposal. Formal change record reviewed by the CCB.",
    "CDR": "Critical Design Review. Major program milestone often gating ATO progress.",
    "PDR": "Preliminary Design Review.",
    "TRR": "Test Readiness Review.",
    "Significant Change": "A change to the authorized system that materially affects security; triggers re-authorization.",
}


def list_topics() -> list[dict]:
    """Public listing - no body, for sidebars."""
    return [
        {"slug": t["slug"], "title": t["title"], "category": t["category"]}
        for t in TOPICS
    ]


def get_topic(slug: str) -> dict | None:
    for t in TOPICS:
        if t["slug"] == slug:
            return t
    return None


def list_glossary() -> list[dict]:
    return [{"term": k, "definition": v} for k, v in sorted(GLOSSARY.items())]


def lookup_term(term: str) -> dict | None:
    # Case-insensitive, also matches stripped of punctuation
    key = term.strip().upper().replace(".", "").replace("&", "").replace(" ", "")
    for k, v in GLOSSARY.items():
        if k.upper().replace(".", "").replace("&", "").replace(" ", "") == key:
            return {"term": k, "definition": v}
    return None
