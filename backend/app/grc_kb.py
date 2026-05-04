"""GRC (Governance, Risk, Compliance) knowledge base.

Practitioner-oriented reference covering the broader GRC discipline that surrounds
RMF - frameworks, regulations, risk concepts, audit types, governance structures,
and tooling. Not legal or audit advice.
"""
from __future__ import annotations

TOPICS: list[dict] = [
    {
        "slug": "what-is-grc",
        "title": "What is GRC?",
        "category": "Foundations",
        "body": """**GRC = Governance, Risk, and Compliance.** It's the umbrella discipline for how an \
organization sets direction, identifies what could derail it, and makes sure it follows the rules.

**The three pillars:**

- **Governance** - *Who decides what, and how?* Board oversight, committees, policies, roles, \
authority delegation, decision rights, ethics.
- **Risk** - *What could go wrong, and how do we deal with it?* Identify risks, measure them, \
decide whether to accept / mitigate / transfer / avoid, monitor over time.
- **Compliance** - *Are we following the rules?* Laws, regulations, contracts, internal policies. \
Includes both regulatory compliance (HIPAA, SOX, GDPR…) and internal compliance (your own \
acceptable-use policy).

**Where RMF fits:** RMF is one specific *risk management* methodology used inside the *compliance* \
context for U.S. federal systems. GRC is broader - it includes things like enterprise risk \
management (ERM), vendor risk, financial controls, data privacy, and ethics - not just \
cybersecurity.

**Why GRC exists as a function:** Without coordination, you get the same control tested four times \
by four different audit teams, the same risk owned by no one, and the same policy contradicting \
itself in three places. A GRC function unifies the activity into one inventory of risks, controls, \
and assurance.

**Common GRC tools:** Archer, ServiceNow GRC, MetricStream, OneTrust, AuditBoard, LogicGate, \
Hyperproof, Drata, Vanta. They share a common data model: risks → controls → tests → evidence → \
findings → remediation.""",
    },
    {
        "slug": "three-lines",
        "title": "Three Lines of Defense (the Org Chart of Risk)",
        "category": "Foundations",
        "body": """The **Three Lines of Defense** model (IIA, refreshed 2020 as the **Three Lines \
Model**) describes who owns what in risk and control:

| Line | Who | What they do |
| --- | --- | --- |
| **1st Line** | Operations / business units | **Own** the risk. Build and run the controls every day. (e.g., IT operations runs patching; sales follows the contract approval process.) |
| **2nd Line** | Risk, Compliance, IT Security, GRC office | **Oversee** and challenge. Set policy, monitor, advise. *Not* independent enough to audit. |
| **3rd Line** | Internal Audit | **Independently assure.** Reports to the Audit Committee, not management. Tests whether 1 and 2 actually work. |
| External | External auditors / regulators | Outside the model - provide further independent assurance to shareholders / regulators. |

**Why it matters:** Audits have specific independence requirements. If your "internal audit" \
also writes the policies they audit, that's a finding. The model also gives a clean answer to \
"who's responsible for [X]?" - first line owns it; second oversees it; third audits it.

**Common confusion:** The Information System Security Officer (ISSO) is usually first line. The \
Information System Security Manager (ISSM) is second line. The SCA acts as third line for the \
specific package (independent assessor).""",
    },
    {
        "slug": "risk-concepts",
        "title": "Core Risk Concepts: Inherent vs Residual, Appetite vs Tolerance",
        "category": "Risk",
        "body": """A handful of definitions cause endless confusion. Here's what they actually mean:

- **Inherent risk** - the risk *before* any controls are applied. The "natural" risk of doing the \
activity at all.
- **Residual risk** - the risk *after* controls are applied. What's left over.
- **Risk appetite** - how much risk the organization *wants* to take to achieve its goals \
(strategic, set by the board). "We want to grow into new markets" implies some appetite for \
expansion risk.
- **Risk tolerance** - the maximum *deviation* from the appetite that's still acceptable \
(operational, set by management). Appetite is the target; tolerance is the guardrail.
- **Risk capacity** - the maximum risk the organization could absorb without failing. Always >= \
appetite.

**Treatment options for any risk** (the four T's):

1. **Treat** (mitigate) - apply controls to reduce probability or impact.
2. **Tolerate** (accept) - acknowledge it and live with it. Requires documented sign-off.
3. **Transfer** - push it to someone else (insurance, contracts, outsourcing).
4. **Terminate** (avoid) - stop doing the activity entirely.

**Likelihood × Impact = Risk Score** is the bread-and-butter calculation. Most orgs use a 5×5 \
heatmap with subjective ratings. Quantitative risk (FAIR, Monte Carlo) is more rigorous but \
heavier to operate.

**Inherent risk lives forever, residual risk is what you report.** Auditors care about residual \
risk relative to your appetite/tolerance. If residual exceeds tolerance, you have a finding (or a \
documented risk acceptance).""",
    },
    {
        "slug": "frameworks-overview",
        "title": "Compliance Frameworks Cheat Sheet",
        "category": "Compliance",
        "body": """The major frameworks you'll encounter, and what they're actually for:

| Framework | Scope | Required by | Type |
| --- | --- | --- | --- |
| **NIST CSF** (Cybersecurity Framework) | Cybersecurity outcomes (Identify, Protect, Detect, Respond, Recover, Govern) | Voluntary, but widely adopted (US fed contractors, critical infra) | Outcomes/maturity |
| **NIST SP 800-53** | Federal info system controls | DoD/Federal via FISMA | Prescriptive controls |
| **ISO/IEC 27001** | Information Security Management System (ISMS) | International, voluntary cert | Management system + controls |
| **SOC 2** | Service org controls (Trust Services Criteria) | SaaS / cloud providers (customer demand) | Audit attestation (Type I/II) |
| **PCI-DSS** | Payment card data | Anyone handling cardholder data | Prescriptive controls + cert |
| **HIPAA** | Protected Health Information | Covered entities + business associates | US law (HHS) |
| **GDPR** | Personal data of EU residents | Anyone processing EU resident data | EU regulation |
| **CCPA / CPRA** | California consumer data | Businesses meeting thresholds with CA residents' data | CA state law |
| **SOX** | Financial reporting controls (esp. ITGCs) | US public companies | US law (SEC) |
| **FedRAMP** | Cloud services for US gov | Federal cloud customers | NIST-derived authorization |
| **CMMC** | Cybersecurity for DoD contractors | DoD contracts | DoD certification |
| **FISMA** | Federal information security | All US federal agencies | US law (drives RMF/NIST 800-53) |
| **HITRUST CSF** | Healthcare (and beyond) - combined framework | Healthcare org assurance | Cert (i1, r2) |
| **NIST 800-171** | CUI in non-federal systems | DoD contractors (DFARS clause) | Prescriptive controls |

**Crosswalks matter.** Most large orgs implement once and report against many frameworks. NIST CSF \
maps to ~everything; OSCAL is making machine-readable cross-framework profiles real. The "Secure \
Controls Framework (SCF)" publishes a free crosswalk across 100+ frameworks.""",
    },
    {
        "slug": "nist-csf",
        "title": "NIST Cybersecurity Framework (CSF) 2.0",
        "category": "Compliance",
        "body": """**NIST CSF** is the most widely adopted *outcome-oriented* cybersecurity framework. \
It tells you *what* good cybersecurity looks like, not *how* to do it.

**The six Functions (CSF 2.0, Feb 2024):**

1. **Govern (GV)** - *new in 2.0*. Strategy, roles, policy, supply-chain risk, oversight.
2. **Identify (ID)** - Asset management, business environment, governance, risk assessment.
3. **Protect (PR)** - Access control, awareness, data security, protective tech.
4. **Detect (DE)** - Anomalies, continuous monitoring, detection processes.
5. **Respond (RS)** - Response planning, communications, analysis, mitigation, improvements.
6. **Recover (RC)** - Recovery planning, improvements, communications.

Each Function has Categories and Subcategories, which map to specific controls in 800-53, ISO \
27001, COBIT, etc.

**Implementation Tiers** describe maturity (Partial → Risk Informed → Repeatable → Adaptive). \
Profiles describe current vs target state.

**When to use it:** Strategic cybersecurity conversations. Board reports. Cross-framework mapping. \
Assessing cybersecurity maturity at the organizational level.

**When not to use it:** As a control catalog. CSF references controls; it doesn't define them. \
Pair with 800-53, ISO 27002, or your own catalog.""",
    },
    {
        "slug": "iso-27001",
        "title": "ISO/IEC 27001 - Information Security Management System",
        "category": "Compliance",
        "body": """**ISO/IEC 27001** is the international standard for an **Information Security \
Management System (ISMS)**. The key word is *system* - it's about establishing repeatable \
processes, not just deploying controls.

**Structure:**

- **Clauses 4–10** - the management system requirements (context, leadership, planning, support, \
operation, performance evaluation, improvement). These are *mandatory* and what gets audited \
for certification.
- **Annex A** - a list of 93 controls (in 27001:2022; was 114 in 27001:2013) organized into 4 \
themes: Organizational, People, Physical, Technological. Detailed implementation guidance is in \
**ISO/IEC 27002**.

**Certification:**

- A **certification body** (e.g., BSI, DNV, Schellman) audits annually after a multi-stage initial \
audit (Stage 1 documentation review, Stage 2 implementation audit). The cert is valid for 3 years \
with annual surveillance audits.
- Many customers ask for it as table-stakes for B2B SaaS, especially in Europe.

**Comparison to NIST CSF / 800-53:**
- 27001 is *management system* + control catalog (Annex A). 800-53 is *just* a control catalog. \
CSF is *just* an outcomes framework.
- 27001 → control selection drives a **Statement of Applicability (SoA)** - every control is \
either implemented or excluded with justification.""",
    },
    {
        "slug": "soc2",
        "title": "SOC 2 - Service Organization Controls (Trust Services Criteria)",
        "category": "Compliance",
        "body": """**SOC 2** is an audit attestation report performed under **AICPA's SSAE 18** for \
service organizations. It's the most common B2B SaaS compliance ask in the U.S.

**The five Trust Services Criteria (TSC):**

- **Security** - *required for every SOC 2*. Common Criteria covering access, ops, risk, change.
- **Availability** - uptime, capacity, monitoring.
- **Processing Integrity** - data is accurate, complete, timely.
- **Confidentiality** - data marked confidential is protected.
- **Privacy** - personal information handled per the org's privacy notice.

You pick which of the four optional TSCs apply (security is mandatory).

**Type I vs Type II:**
- **Type I** - controls *designed* properly at a point in time. Quick to obtain (~weeks).
- **Type II** - controls *operated effectively* over a period (typically 6–12 months). What \
customers actually want.

**Bridge letters** cover the gap between your last Type II and the customer's review date.

**Common pitfalls:**
- Treating SOC 2 as a checklist rather than a management system. Auditors test whether your \
controls *actually run* - sample-based evidence collection.
- Scoping too broadly. SOC 2 is about a service; define the service boundary clearly.

**SOC 1 vs SOC 2 vs SOC 3:**
- SOC 1 = financial reporting controls (for customer auditors)
- SOC 2 = TSC controls (security/availability/etc.)
- SOC 3 = SOC 2 summary intended for public/marketing use""",
    },
    {
        "slug": "pci-dss",
        "title": "PCI DSS - Payment Card Industry Data Security Standard",
        "category": "Compliance",
        "body": """**PCI DSS v4.0** (mandatory March 2025) is the standard for protecting cardholder \
data. Required by the card brands (Visa, MC, Amex, Discover, JCB) for anyone who stores, \
processes, or transmits cardholder data.

**12 high-level requirements grouped into 6 goals:**

1. Build and maintain a secure network (firewalls, change defaults)
2. Protect cardholder data (encryption, retention)
3. Maintain a vulnerability management program (AV, secure dev)
4. Implement strong access control (least privilege, unique IDs, physical access)
5. Regularly monitor and test networks (logging, scanning, pen testing)
6. Maintain an information security policy

**Scope is everything.** The PCI scope includes any system that *stores, processes, transmits, or \
could affect the security of* cardholder data. Reduce scope via tokenization, P2PE, network \
segmentation. Out-of-scope systems don't have to comply.

**Validation paths:**

- **SAQ (Self-Assessment Questionnaire)** - small merchants. Multiple variants (A, A-EP, B, C, D, \
P2PE) based on how you handle cards.
- **ROC (Report on Compliance)** - large merchants and service providers. Done by a **QSA** \
(Qualified Security Assessor).
- **AOC (Attestation of Compliance)** - the signed cover sheet provided to acquirers and \
business partners.

**v4.0 changes:** Customized approach (achieve the objective by other means with documented \
validation), MFA across the CDE, stronger crypto requirements, more emphasis on continuous \
processes.""",
    },
    {
        "slug": "hipaa",
        "title": "HIPAA - Privacy & Security of Protected Health Information",
        "category": "Compliance",
        "body": """**HIPAA** is U.S. federal law (1996) governing PHI (Protected Health Information). \
The implementing regulations are at **45 CFR Parts 160 and 164** (the Privacy Rule, Security \
Rule, Breach Notification Rule, Enforcement Rule).

**Who's covered:**

- **Covered Entities (CE)** - health plans, healthcare clearinghouses, healthcare providers who \
transmit health information electronically.
- **Business Associates (BA)** - vendors of covered entities that handle PHI on their behalf \
(SaaS, billing companies, attorneys with PHI access). Must have a **Business Associate Agreement \
(BAA)** with the CE.

**The Security Rule** (Subpart C of Part 164) requires three categories of safeguards:

- **Administrative** - risk analysis, workforce training, contingency planning, BAAs, sanctions.
- **Physical** - facility access, workstation use, device/media controls.
- **Technical** - access control, audit controls, integrity, person/entity authentication, \
transmission security.

Each safeguard is either **Required** (must implement) or **Addressable** (must implement OR \
document why an equivalent measure is reasonable).

**The Privacy Rule** governs how PHI may be used/disclosed (treatment/payment/operations + \
authorizations + minimum necessary).

**Breach Notification** - for unsecured PHI breaches, notify affected individuals within 60 days, \
HHS within 60 days (or annually if <500 affected), and media if >500 in a state.

**Enforcement:** OCR (HHS Office for Civil Rights). Penalties up to $1.5M/year per violation \
category. Resolution agreements often hit single-digit millions; criminal penalties possible.""",
    },
    {
        "slug": "gdpr",
        "title": "GDPR - EU General Data Protection Regulation",
        "category": "Compliance",
        "body": """**GDPR** (Regulation EU 2016/679, in force May 2018) governs personal data of EU \
residents. Extraterritorial - applies to any organization processing EU resident data, regardless \
of where the org is based.

**Key concepts:**

- **Personal data** - any info relating to an identified or identifiable natural person. Broad \
definition: includes IP addresses, cookies, pseudonymous IDs.
- **Special category data** - health, biometric, genetic, racial/ethnic, political, religious, \
union, sex life. Stricter rules.
- **Data Subject** - the person the data is about. Has rights.
- **Controller** - decides why and how data is processed (the company collecting it).
- **Processor** - processes data on behalf of a controller (a SaaS vendor, typically). Bound by \
a **Data Processing Agreement (DPA)**.

**Six lawful bases for processing** (must pick one):
1. Consent
2. Contract necessity
3. Legal obligation
4. Vital interests
5. Public interest
6. Legitimate interests (with balancing test)

**Data subject rights:**
- Access, rectification, erasure ("right to be forgotten"), restriction, portability, objection, \
not subject to solely automated decisions (incl. profiling).

**Breach notification:** Notify supervisory authority within **72 hours** of becoming aware. \
Notify affected individuals if high risk.

**International transfers:** Need a transfer mechanism - Standard Contractual Clauses (SCCs), \
Binding Corporate Rules (BCRs), adequacy decision (US has the Data Privacy Framework after \
Schrems II).

**Penalties:** Up to **4% of annual global turnover or €20M, whichever higher** for severe \
infringements; 2%/€10M for lesser ones.

**DPO** - Data Protection Officer required for public bodies, large-scale monitoring, or \
large-scale special category processing.""",
    },
    {
        "slug": "fedramp",
        "title": "FedRAMP - Federal Risk and Authorization Management Program",
        "category": "Compliance",
        "body": """**FedRAMP** standardizes the security authorization of cloud services for \
federal government use. Your CSP gets authorized once; many federal customers can then use it.

**Impact levels** (mirror FIPS 199):

- **Low** - minimal impact. ~149 controls.
- **Moderate** - most non-classified workloads. ~287 controls. Most common level.
- **High** - sensitive data with serious impact. ~370 controls.
- **LI-SaaS** - low-impact SaaS, lighter process for tactical adoption.

**Authorization paths:**

- **Agency ATO** - a single agency sponsors the authorization. CSP works with that agency's AO.
- **JAB P-ATO** - Joint Authorization Board (DoD, DHS, GSA) provisional authorization. Heavier \
process; broader downstream reuse. Limited slots.

**Process:**
1. Become "FedRAMP Ready" via a **3PAO** (Third Party Assessment Org).
2. Build the package (SSP, SAP, SAR, POA&M, etc.) - same artifacts as RMF.
3. Authorization decision.
4. **Continuous Monitoring** - monthly POA&M, monthly scans, annual assessment.

**Relationship to other frameworks:**
- FedRAMP Mod ≈ DoD Impact Level 2 / IL4 (with overlay).
- 800-171 ≠ FedRAMP - 800-171 is for CUI in *non-federal* systems (contractor-side).
- Authorization reciprocity exists across agencies but is patchy.

**FedRAMP 20x** (announced 2024) - modernization push: API-first, OSCAL-native, faster cycles, \
continuous authorization model.""",
    },
    {
        "slug": "cmmc",
        "title": "CMMC - Cybersecurity Maturity Model Certification",
        "category": "Compliance",
        "body": """**CMMC 2.0** is the DoD's certification program for contractors handling **Federal \
Contract Information (FCI)** or **Controlled Unclassified Information (CUI)**.

**Three levels:**

| Level | What | Based on | Assessment |
| --- | --- | --- | --- |
| **Level 1** - Foundational | 17 basic safeguards for FCI | FAR 52.204-21 | Annual self-assessment |
| **Level 2** - Advanced | 110 controls for CUI | NIST SP 800-171 | Triennial 3rd-party (C3PAO) for prioritized; self-assessment for non-prioritized |
| **Level 3** - Expert | Level 2 + ~24 enhanced from 800-172 | 800-171 + 800-172 | Triennial gov-led |

**Where it appears:** DFARS 252.204-7012, -7019, -7020, -7021. The CMMC clause flows into \
contracts handling FCI/CUI starting with phased rollout (Phase 1 in late 2024 / 2025).

**SPRS score** - interim self-assessment scoring (out of 110) registered in Supplier Performance \
Risk System. Required for many DoD contracts even before CMMC 3PAO assessment.

**System Security Plan (SSP) + POA&M** - required artifacts. Same RMF concepts; lighter than \
800-53.

**3PAO** - CMMC Third Party Assessment Organization, accredited by Cyber AB, conducts the L2 \
assessment.

**Common gotchas:**
- Confusing FCI scope with CUI scope. Many contractors have both.
- Assuming Microsoft 365 Commercial counts - for CUI you typically need Government Cloud (GCC \
High) or equivalent.
- Believing "we have an ATO so we're good" - your federal customer's ATO doesn't make you CMMC \
compliant.""",
    },
    {
        "slug": "sox",
        "title": "SOX - Sarbanes-Oxley & ITGCs",
        "category": "Compliance",
        "body": """**SOX** (Sarbanes-Oxley Act of 2002) is U.S. federal law for public companies to \
ensure the integrity of financial reporting. Two sections matter most for IT/security:

- **§302** - CEO/CFO certify the accuracy of financial statements.
- **§404** - Management assesses *internal control over financial reporting (ICFR)*; external \
auditor attests to it.

**ITGCs (IT General Controls)** are the IT-side controls that support ICFR. They cover:

- **Access to Programs and Data** - provisioning, de-provisioning, periodic access reviews, \
privileged access, MFA, segregation of duties.
- **Change Management** - change approval, testing, separation of dev/prod, emergency change.
- **Computer Operations** - job scheduling, monitoring, incident response, backup/recovery.
- **System Development** - SDLC, project approvals, deployment.

**Why this matters to security teams:** Financial statement auditors (and the PCAOB) test ITGCs \
sample-based. A weak control here means the ICFR opinion gets qualified, which moves stock prices.

**Key practitioner notes:**
- *In-scope* applications are those that affect financial reporting (general ledger, ERP, billing, \
payroll). Other applications usually aren't SOX-relevant.
- **Segregation of duties** is the most-failed control. Same person shouldn't be able to create a \
vendor AND approve a payment to that vendor.
- Auditors don't accept "we have a policy" - they want evidence of execution (signed approvals, \
ticketing system records, screenshots, exports).

**Penalties:** Personal liability for CEO/CFO. Criminal penalties for willful violations. \
Companies have paid $100M+ for material weaknesses.""",
    },
    {
        "slug": "third-party-risk",
        "title": "Third-Party / Vendor Risk Management (TPRM)",
        "category": "Risk",
        "body": """**TPRM** is the discipline of managing risk introduced by third parties - vendors, \
suppliers, processors, integrators, anyone who touches your data or systems.

**Why it matters:** Most of your attack surface and compliance burden now lives with vendors. \
Notable third-party-driven incidents: SolarWinds (2020), Kaseya (2021), MOVEit (2023), Snowflake \
customers (2024). Your customers and regulators hold *you* responsible.

**Lifecycle:**

1. **Onboarding due diligence** - security questionnaire (often SIG, CAIQ), SOC 2 review, \
financial check, legal review.
2. **Tiering** - risk-rate vendors (typically Critical / High / Medium / Low) based on data \
sensitivity, system criticality, regulatory exposure.
3. **Contracting** - DPA / BAA / security addendum / right-to-audit / breach notification \
timelines / SLAs.
4. **Ongoing monitoring** - annual reassessment for high-tier vendors; continuous monitoring tools \
(BitSight, SecurityScorecard); track expiration of certs, SOC 2 bridge letters.
5. **Offboarding** - data return/destruction, access revocation, certificate of destruction.

**Common questionnaires:**
- **SIG (Standardized Information Gathering)** - Shared Assessments. The big one.
- **CAIQ (Consensus Assessments Initiative Questionnaire)** - Cloud Security Alliance. Cloud-focused.
- **VSAQ** - Google's open-source framework.
- Custom for everyone else.

**Fourth-party risk:** Your vendor's vendors. SolarWinds was a fourth-party event for many. Hard \
to manage; usually relies on contractual flow-down.

**Tooling:** OneTrust, ProcessUnity, Whistic, Aravo, ServiceNow Vendor Risk, Drata Trust Center.""",
    },
    {
        "slug": "audit-types",
        "title": "Types of Audits & Attestations",
        "category": "Audit",
        "body": """Many flavors of audit exist; people frequently conflate them. Here's the field guide.

**By auditor relationship:**

- **First-party** - internal audit, self-assessment.
- **Second-party** - customer or supplier auditing you; you auditing your vendor.
- **Third-party** - independent auditor (often required for cert/attestation).

**By output:**

- **Audit** - opinion on whether assertions are correct. Statutory financial audit, ISO cert audit.
- **Attestation** - auditor attests to the truth of a statement made by management. SOC 2 is an \
attestation, not an audit, technically.
- **Examination** - broader review without formal assurance opinion.
- **Agreed-upon procedures (AUP)** - auditor performs specific procedures the customer asked for; \
no opinion issued.

**By assurance type:**

- **Type I** - design only, point-in-time. SOC 1 Type I, SOC 2 Type I, ISAE 3402 Type I.
- **Type II** - design AND operating effectiveness over a period. The one customers want.

**Common audit/attestation reports:**

- **SOC 1 / SOC 2 / SOC 3** - AICPA, US.
- **ISAE 3402 / 3000** - international SOC equivalents.
- **ISO 27001 / 27701 / 22301** - certification audits.
- **PCI ROC** - Report on Compliance.
- **HITRUST i1 / r2** - assessment with certification.
- **Pen test reports** - specific to security testing; not really an "audit".
- **FedRAMP SAR** - Security Assessment Report.

**Year-round survival tip:** Maintain *evidence inventory* keyed to controls. Every audit ends up \
asking similar questions; reuse.""",
    },
    {
        "slug": "policies-procedures",
        "title": "Policies, Standards, Procedures, Guidelines",
        "category": "Governance",
        "body": """The hierarchy of governance documents - frequently confused, often badly implemented:

| Level | Purpose | Tone | Example |
| --- | --- | --- | --- |
| **Policy** | High-level, mandatory direction. *What and why.* | "The organization shall…" | "All systems handling PII shall encrypt data at rest." |
| **Standard** | Specific, mandatory technical requirement. *Which technologies / settings.* | "Production servers shall use AES-256-GCM…" | "Approved cipher suites: TLS 1.2/1.3 with PFS." |
| **Procedure** | Step-by-step. *How.* | "1. Open ticket. 2. Assign…" | Patch management procedure. |
| **Guideline** | Recommended, not mandatory. *Suggestions.* | "Consider…", "It is recommended…" | Secure coding guideline. |

**Why the hierarchy matters:**
- Auditors test against your *standards and procedures*, not the policy. A vague policy with no \
standards is a gap.
- Policies should be stable (annual review). Standards change with technology. Procedures change \
with operations.
- Mandatory language matters. If you wrote "should" instead of "shall", an auditor accepts \
non-compliance.

**Common problems:**
- Policy says X; standard says Y; reality does Z. Three sources of truth, all wrong.
- Policies that are 60+ pages and nobody reads. Better: short policy + linked standards.
- Policies "approved" but never re-reviewed. Auditors check for review dates.

**Lifecycle:** Draft → review (legal, security, ops) → approve (typically CISO/CIO/board for \
top-level) → publish → train → review annually → revise or sunset.""",
    },
    {
        "slug": "kris-kpis",
        "title": "KRIs, KPIs, KCIs - Measuring GRC",
        "category": "Governance",
        "body": """If you can't measure it, you can't manage it. GRC programs use a few related but \
distinct metrics:

- **KPI (Key Performance Indicator)** - a metric for *performance* against goals. \
"99.9% system uptime", "<24h MTTR for high-severity findings".
- **KRI (Key Risk Indicator)** - leading indicator that a *risk is increasing*. "Number of \
overdue access reviews", "% of vendors with expired SOC 2", "phishing click rate".
- **KCI (Key Control Indicator)** - measure of whether a *control is operating*. "% of changes \
with documented approval", "MFA coverage %".

**Good metrics are SMART:** Specific, Measurable, Actionable, Relevant, Time-bound.

**Common GRC metrics worth tracking:**

- Open findings by severity, aging
- POA&M closure rate vs commitment
- Time to remediate critical vulns
- % of users with privileged access (and quarterly trend)
- Failed access reviews
- Security training completion %
- Mean time to detect / respond / contain
- Policy exception count and aging
- Vendor reassessment overdue %
- Third-party incident count

**Anti-patterns:**
- "Number of training emails sent." Useless. Track outcomes (click rate, completion).
- Vanity metrics (e.g., "100% policy coverage" with no enforcement).
- Metrics no one acts on. If a KRI breaches threshold and nothing happens, it's not a real KRI.""",
    },
    {
        "slug": "data-classification",
        "title": "Data Classification & Handling",
        "category": "Governance",
        "body": """Data classification is the foundation of nearly every security control decision. \
You can't protect what you can't categorize.

**Typical scheme** (organizations vary; this is the most common pattern):

| Classification | Description | Examples | Handling |
| --- | --- | --- | --- |
| **Public** | Authorized for general release | Marketing, published reports | No restriction |
| **Internal** | Default for org info | Memos, internal wikis | Org-only access |
| **Confidential** | Sensitive business info | Customer lists, source code, finances | Need-to-know, encryption in transit |
| **Restricted / Highly Confidential** | Regulated or strategic | PII, PHI, payment, M&A, credentials | Need-to-know, encryption everywhere, audit, sometimes air-gapped |

**Key principles:**
- The data's classification **dictates** the controls. Restricted data on a laptop with no \
encryption is automatically a finding.
- **Owner** (typically a business leader) classifies. **Custodian** (IT / Security) protects.
- **Inheritance** - a system handling Restricted data inherits Restricted-level controls. The \
*system* takes the classification of its highest data.

**Crosswalk to regulatory classes:**
- US Federal: Public / CUI / Classified (Confidential / Secret / Top Secret)
- DoD: Unclassified / CUI / Confidential / Secret / Top Secret + SCI/SAP compartments
- EU: Personal data / Special category personal data
- Healthcare: Non-PHI / PHI
- Cardholder: Out-of-scope / CHD / SAD (PCI definitions)

**Handling rules** are usually a matrix: classification × handling activity (storage, transmission, \
disposal, copying, sharing). Build it once; reference everywhere.""",
    },
    {
        "slug": "incident-management",
        "title": "Incident Management - From Detection to Lessons Learned",
        "category": "Operations",
        "body": """A security incident isn't just a technical event - it's a *governed process* that \
crosses security, IT ops, legal, communications, and HR.

**Lifecycle (NIST SP 800-61 Rev. 2):**

1. **Preparation** - playbooks, tooling, training, contact lists, retainer with IR firm.
2. **Detection & Analysis** - alerts triaged; severity assigned; incident declared.
3. **Containment / Eradication / Recovery** - short-term contain → root-cause eradicate → restore \
to known-good state.
4. **Post-Incident Activity** - lessons learned, controls improved, evidence retained.

**Severity matters.** Build a clear matrix (e.g., Sev 1 = active confirmed compromise of crown \
jewels; Sev 4 = isolated low-impact event). Tie to escalation paths and notification \
requirements.

**Notification & disclosure obligations** (selection):
- **GDPR** - supervisory authority within 72h.
- **HIPAA** - affected individuals within 60d; HHS within 60d (or annually if <500).
- **SEC cyber rule** - material cybersecurity incidents disclosed via 8-K within 4 business days \
(US public companies).
- **State breach laws** - all 50 US states + DC + territories.
- **Sector regulators** - financial (e.g., NY DFS 72h), healthcare, critical infrastructure.

**Tabletop exercises** annually at minimum. Include legal, comms, exec - not just technical.

**Forensic readiness:** logging retention, immutable backups, chain-of-custody procedures, \
pre-approved IR firms (you don't want to be negotiating an IR contract at 2 AM during an \
active breach).""",
    },
    {
        "slug": "frameworks-mapping",
        "title": "Crosswalking Frameworks - Implement Once, Report Many",
        "category": "Compliance",
        "body": """Mid- and large-size orgs juggle many frameworks. The smart play: implement one \
**baseline control set** that satisfies the union of requirements, then map your evidence to each \
report.

**Why:**
- Stop testing the same control 4× for 4 audits.
- Drive consistent control language across teams.
- Cut audit costs 30–50% over time.

**Common backbone choices:**

- **NIST CSF** - outcomes-based; great for cross-framework mapping. Doesn't define controls.
- **NIST SP 800-53** - superset for federal; maps cleanly to FedRAMP, CMMC, 800-171.
- **ISO 27001/27002** - superset for international; maps to most regulations.
- **Secure Controls Framework (SCF)** - purpose-built crosswalk catalog (free, 100+ mappings).

**Tools:**
- **OSCAL** (NIST) - open standard for machine-readable controls/profiles/assessments. Enables \
automated crosswalk and continuous compliance.
- **GRC platforms** (Archer, ServiceNow GRC, Hyperproof, Drata, Vanta) bundle pre-built mappings.

**Practical approach:**
1. Pick a primary baseline (often ISO 27001 or NIST 800-53 Mod).
2. Document your control once, with evidence references.
3. Map each control to *all* applicable frameworks.
4. For each audit, generate the framework view and exportable evidence.

**Watch out for delta requirements** - frameworks have unique items that don't crosswalk cleanly. \
Privacy regs (GDPR, CCPA) often add controls others don't have. Build the deltas as overlays, not \
parallel programs.""",
    },
    {
        "slug": "grc-tools",
        "title": "GRC Tooling Landscape",
        "category": "Operations",
        "body": """The GRC tool market is crowded. Pick based on the size + maturity of your program.

**Enterprise platforms** (heavy, customizable, expensive):

- **Archer (RSA / Ottawa)** - long-standing market leader. Highly customizable; needs admin team.
- **ServiceNow GRC** - strong if you already run ServiceNow. Risk, Audit, Vendor Risk, Compliance.
- **MetricStream** - broad GRC suite; common in financial services.
- **Diligent (Galvanize ACL)** - audit/risk-focused with analytics.

**Mid-market / focused:**

- **AuditBoard** - internal audit / SOX / ITGCs. Strong UX.
- **Hyperproof** - compliance-focused; good cross-framework view.
- **LogicGate Risk Cloud** - flexible workflow builder.
- **Resolver** - ERM-focused.

**SaaS compliance automation** (built for tech companies chasing SOC 2/ISO/HIPAA fast):

- **Drata, Vanta, Secureframe, Tugboat Logic, Strike Graph, Thoropass, Sprinto** - automate \
evidence collection from cloud + HR + IT systems; pre-built control mappings; auditor portals.

**Privacy / data governance:**

- **OneTrust** - privacy + TPRM + GRC suite. Market leader for privacy ops.
- **TrustArc, BigID, Securiti** - privacy + data discovery.

**TPRM-specialized:**

- **Whistic, ProcessUnity, Aravo, BitSight, SecurityScorecard, UpGuard.**

**Selection criteria:**
- Will this scale with us in 3 years?
- Does it have native integrations with our stack (cloud, HRIS, IDP, ticketing)?
- API quality (everything ends up in someone's data lake).
- Auditor familiarity - your external auditor not knowing the tool slows you down.
- Don't pick a tool to be your control program - *your program* drives the tool.""",
    },
]


GLOSSARY: dict[str, str] = {
    # Core concepts
    "GRC": "Governance, Risk, and Compliance - the discipline of coordinating how an organization is directed, what could go wrong, and whether it follows the rules.",
    "ERM": "Enterprise Risk Management - the org-wide approach to identifying, assessing, and managing risks (financial, operational, strategic, cyber).",
    "ICFR": "Internal Control over Financial Reporting - controls designed to provide reasonable assurance that financial statements are reliable. Tested under SOX.",
    "ITGC": "IT General Controls - IT controls supporting financial reporting (access, change, operations, SDLC). Heavily tested in SOX audits.",
    "ITAC": "IT Application Controls - controls embedded in business applications (e.g., approval workflows, segregation of duties enforcement).",
    "SoD": "Segregation of Duties - splitting tasks across people so no one person can complete a fraud-prone activity alone (e.g., create vendor + approve payment).",

    # Risk concepts
    "Inherent Risk": "Risk before any controls are applied; the natural risk of doing the activity.",
    "Residual Risk": "Risk remaining after controls are applied. What's reported and accepted.",
    "Risk Appetite": "The amount of risk the org is willing to take to achieve strategic goals (board-set).",
    "Risk Tolerance": "Allowable variance from the risk appetite (operational guardrail).",
    "Risk Capacity": "Maximum risk the org could absorb without failing.",
    "FAIR": "Factor Analysis of Information Risk - quantitative cyber risk methodology.",
    "ALE": "Annual Loss Expectancy = ARO × SLE. Quantitative risk metric.",
    "ARO": "Annualized Rate of Occurrence - how often a loss event is expected per year.",
    "SLE": "Single Loss Expectancy - dollar loss per occurrence.",

    # Roles / functions
    "CRO": "Chief Risk Officer - senior executive owning enterprise risk.",
    "CCO": "Chief Compliance Officer - senior executive owning compliance program.",
    "CISO": "Chief Information Security Officer - owns cyber risk and security strategy.",
    "DPO": "Data Protection Officer - required role under GDPR for certain orgs.",
    "Audit Committee": "Board committee overseeing financial reporting, internal control, and external/internal audit. Independent of management.",
    "Three Lines": "Three Lines Model (IIA) - operations (1st), risk/compliance (2nd), internal audit (3rd).",

    # Frameworks
    "NIST CSF": "NIST Cybersecurity Framework - outcome-based framework with 6 Functions (Govern, Identify, Protect, Detect, Respond, Recover) in v2.0.",
    "ISO 27001": "International standard for an Information Security Management System (ISMS). Annex A lists controls.",
    "ISO 27002": "Implementation guidance for ISO 27001 Annex A controls.",
    "ISO 27701": "Privacy extension to ISO 27001/27002 (PIMS).",
    "ISO 22301": "Business continuity management system standard.",
    "SOC 1": "AICPA report on controls relevant to user entities' financial reporting.",
    "SOC 2": "AICPA report on Trust Services Criteria (Security required; Availability, Processing Integrity, Confidentiality, Privacy optional).",
    "SOC 3": "Public-facing summary of a SOC 2 report.",
    "SSAE 18": "AICPA standard governing SOC reports.",
    "ISAE 3402": "International equivalent to SOC 1 (financial controls).",
    "ISAE 3000": "International equivalent to SOC 2 (broader assurance).",
    "PCI-DSS": "Payment Card Industry Data Security Standard. Required for handling cardholder data.",
    "QSA": "Qualified Security Assessor - auditor authorized to perform PCI ROC.",
    "ROC": "Report on Compliance (PCI). Detailed assessment by a QSA.",
    "AOC": "Attestation of Compliance (PCI). Cover letter to acquirers/partners.",
    "SAQ": "Self-Assessment Questionnaire (PCI). Smaller merchants.",
    "HIPAA": "US law governing PHI (Protected Health Information).",
    "PHI": "Protected Health Information - individually identifiable health information.",
    "BAA": "Business Associate Agreement - required HIPAA contract between Covered Entity and Business Associate.",
    "CE": "Covered Entity (HIPAA) - health plans, providers, clearinghouses.",
    "BA": "Business Associate (HIPAA) - vendor handling PHI for a Covered Entity.",
    "OCR": "HHS Office for Civil Rights - enforces HIPAA.",
    "GDPR": "EU General Data Protection Regulation - personal data of EU residents.",
    "DPA": "Data Processing Agreement - controller/processor contract under GDPR.",
    "DPIA": "Data Protection Impact Assessment - required under GDPR for high-risk processing.",
    "SCC": "Standard Contractual Clauses - EU-approved transfer mechanism for international data transfers.",
    "BCR": "Binding Corporate Rules - intra-group transfer mechanism under GDPR.",
    "CCPA": "California Consumer Privacy Act (and CPRA expansion).",
    "SOX": "Sarbanes-Oxley Act of 2002 - US financial reporting integrity law for public companies.",
    "PCAOB": "Public Company Accounting Oversight Board - oversees external auditors of public companies.",
    "FedRAMP": "Federal Risk and Authorization Management Program - standardized cloud authorization for US federal agencies.",
    "FISMA": "Federal Information Security Modernization Act - US federal info security law.",
    "FIPS 199": "Federal standard for security categorization (Low/Moderate/High).",
    "CMMC": "Cybersecurity Maturity Model Certification - DoD certification for contractors.",
    "FCI": "Federal Contract Information - non-public info provided/generated under federal contracts.",
    "CUI": "Controlled Unclassified Information - sensitive unclassified info needing safeguarding.",
    "DFARS": "Defense Federal Acquisition Regulation Supplement - DoD contracting clauses.",
    "SPRS": "Supplier Performance Risk System - DoD supplier scoring (incl. interim NIST 800-171 score).",
    "HITRUST": "HITRUST CSF - combined healthcare-focused framework with i1 and r2 certifications.",
    "COBIT": "Control Objectives for Information and Related Technologies (ISACA) - IT governance framework.",
    "ITIL": "Information Technology Infrastructure Library - service management framework.",
    "COSO": "Committee of Sponsoring Organizations - Internal Control framework basis for SOX.",
    "SCF": "Secure Controls Framework - free cross-framework control crosswalk catalog.",
    "OSCAL": "Open Security Controls Assessment Language (NIST) - machine-readable format for controls/profiles/assessments.",

    # Audit
    "Type I": "Audit/attestation testing control DESIGN at a point in time.",
    "Type II": "Audit/attestation testing both DESIGN and OPERATING EFFECTIVENESS over a period.",
    "Bridge Letter": "Auditor letter covering the gap between the end of a Type II reporting period and a customer's review date.",
    "Material Weakness": "Deficiency in ICFR creating a reasonable possibility that a material misstatement would not be prevented/detected. SOX-killer.",
    "Significant Deficiency": "Less severe than Material Weakness but warrants attention by management.",
    "Control Deficiency": "Lowest severity; control not designed or operating to prevent/detect misstatement.",

    # Risk + governance
    "KRI": "Key Risk Indicator - leading metric showing a risk is increasing.",
    "KCI": "Key Control Indicator - metric showing a control is operating.",
    "KPI": "Key Performance Indicator - metric for performance against a goal.",
    "Risk Register": "Inventory of identified risks with owner, scoring, treatment plan.",
    "RACI": "Responsibility matrix: Responsible / Accountable / Consulted / Informed.",
    "MoR": "Management of Risk - UK-origin risk methodology.",

    # Privacy
    "PII": "Personally Identifiable Information - any data that identifies a natural person.",
    "PI": "Personal Information (broader, used in CCPA).",
    "PHI": "Protected Health Information (HIPAA).",
    "Data Controller": "GDPR - entity that determines purposes and means of processing personal data.",
    "Data Processor": "GDPR - entity processing personal data on behalf of the controller.",
    "Data Subject": "GDPR - the natural person whose data is being processed.",
    "Right to be Forgotten": "GDPR Art. 17 - right of erasure of personal data under certain conditions.",

    # TPRM
    "TPRM": "Third-Party Risk Management.",
    "VRM": "Vendor Risk Management (often used interchangeably with TPRM).",
    "SIG": "Standardized Information Gathering questionnaire (Shared Assessments).",
    "CAIQ": "Consensus Assessments Initiative Questionnaire (Cloud Security Alliance).",
}


def list_topics() -> list[dict]:
    return [{"slug": t["slug"], "title": t["title"], "category": t["category"]} for t in TOPICS]


def get_topic(slug: str) -> dict | None:
    for t in TOPICS:
        if t["slug"] == slug:
            return t
    return None


def list_glossary() -> list[dict]:
    return [{"term": k, "definition": v} for k, v in sorted(GLOSSARY.items())]


def lookup_term(term: str) -> dict | None:
    key = term.strip().upper().replace(".", "").replace("&", "").replace(" ", "")
    for k, v in GLOSSARY.items():
        if k.upper().replace(".", "").replace("&", "").replace(" ", "") == key:
            return {"term": k, "definition": v}
    return None
