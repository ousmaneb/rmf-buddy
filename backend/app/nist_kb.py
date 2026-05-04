"""NIST publication library - quick reference for the core RMF document set.

Each entry is a practitioner cheatsheet, NOT a substitute for reading the source.
Links go to the official NIST CSRC pages.
"""
from __future__ import annotations

PUBLICATIONS: list[dict] = [
    {
        "slug": "sp-800-37r2",
        "title": "NIST SP 800-37 Rev. 2 - Risk Management Framework",
        "category": "Process",
        "url": "https://csrc.nist.gov/pubs/sp/800/37/r2/final",
        "summary": "The authoritative process for authorizing federal information systems. Defines the 7-step RMF (Prepare, Categorize, Select, Implement, Assess, Authorize, Monitor).",
        "body": """**What it is:** The DoD/Federal authorization process. Tells you the steps and \
the order. Does *not* tell you what controls to apply (that's 800-53) or how to test them \
(that's 800-53A).

**The 7 steps:**
0. **Prepare** - organizational + system-level activities before the RMF runs (added in Rev. 2).
1. **Categorize** the system (per FIPS 199 and SP 800-60).
2. **Select** the baseline (per SP 800-53B) and tailor it.
3. **Implement** the controls.
4. **Assess** the controls (per SP 800-53A).
5. **Authorize** - the AO accepts residual risk and signs the ATO.
6. **Monitor** continuously.

**Key Rev. 2 changes vs Rev. 1:**
- Added the Prepare step (org + system).
- Stronger linkage to ERM (Enterprise Risk Management).
- Improved alignment with the Cybersecurity Framework.

**When you'll reach for this:** When someone asks "where in the process are we?", \
when defending the AO timeline, when explaining roles & responsibilities (Appendix D).

**DoD instantiation:** DoDI 8510.01.""",
    },
    {
        "slug": "sp-800-53r5",
        "title": "NIST SP 800-53 Rev. 5 - Security and Privacy Controls",
        "category": "Controls",
        "url": "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final",
        "summary": "The catalog of 1,189 security and privacy controls (and enhancements) used by federal systems.",
        "body": """**What it is:** The control catalog. Twenty families (AC, AT, AU, CA, CM, CP, IA, \
IR, MA, MP, PE, PL, PM, PS, PT, RA, SA, SC, SI, SR), each with controls and enhancements.

**Major Rev. 5 changes vs Rev. 4:**
- **Outcome-based language** - controls describe *what* must be achieved, not *how*.
- **Privacy controls integrated** - the new PT family + privacy parameters across many controls.
- **Supply Chain Risk Management (SR) family** added.
- **Removed** the prior Appendix J privacy overlay structure (now woven through).
- **Threat-informed** control selection.

**Where to find:**
- OSCAL JSON (machine-readable): https://github.com/usnistgov/oscal-content/
- Final PDF + Excel summary on csrc.nist.gov

**Anatomy of a control:**
- ID (e.g., AC-2)
- Statement (parts a, b, c…)
- Discussion / Supplemental Guidance
- Related Controls
- References
- Control Enhancements (AC-2(1), AC-2(2)…)

**When you'll reach for this:** Always. This is the source of truth for control text.""",
    },
    {
        "slug": "sp-800-53ar5",
        "title": "NIST SP 800-53A Rev. 5 - Assessment Procedures",
        "category": "Assessment",
        "url": "https://csrc.nist.gov/pubs/sp/800/53/a/r5/ipd",
        "summary": "Assessment objectives and procedures for testing each 800-53 Rev. 5 control. Used by SCAs.",
        "body": """**What it is:** Companion to 800-53 that breaks each control into discrete \
**assessment objectives** and tells the assessor how to test them.

**Three assessment methods:**
- **Examine** - review documents, configs, scan results
- **Interview** - talk to people who execute the activity
- **Test** - exercise the system to verify behavior

A single control objective may require multiple methods.

**How it relates to CCIs:** DoD's CCI list is essentially a tactical decomposition of \
800-53A objectives into testable atoms tied to specific assessment statements.

**Output of assessment:** The Security Assessment Report (SAR) - input to the AO's \
authorization decision.

**When you'll reach for this:** When planning an assessment, when responding to an SCA \
finding, when writing test procedures, when defending an implementation in pre-assessment.""",
    },
    {
        "slug": "sp-800-53b",
        "title": "NIST SP 800-53B - Control Baselines",
        "category": "Controls",
        "url": "https://csrc.nist.gov/pubs/sp/800/53/b/upd1/final",
        "summary": "Defines the Low, Moderate, and High baselines (and the Privacy baseline) by listing which 800-53 controls apply at each impact level.",
        "body": """**What it is:** The mapping from FIPS 199 impact level → set of 800-53 controls.

**Baseline counts (Rev. 5):**
- LOW: ~149 controls + enhancements
- MODERATE: ~287
- HIGH: ~370
- PRIVACY: parameter-modifying overlay across many baselines

**Tailoring rules** (also covered in 800-37):
- You can **add** controls above the baseline.
- You can **remove** ("tailor out") with documented justification.
- You can **inherit** from a Common Control Provider.
- You can apply **overlays** (Privacy, Classified, ICS, Space, etc.).

**OSCAL profiles:** Each baseline is published as a "resolved profile" - a self-contained \
catalog of just the baseline controls. Useful for ingestion.

**When you'll reach for this:** When tailoring (Step 2). When asked "is X in the Moderate \
baseline?" (the answer's in the data we ship in Browse).""",
    },
    {
        "slug": "sp-800-60",
        "title": "NIST SP 800-60 Vols. I & II - Information Type Mapping",
        "category": "Categorization",
        "url": "https://csrc.nist.gov/pubs/sp/800/60/v1/r1/final",
        "summary": "Catalog of standard federal information types and their suggested confidentiality / integrity / availability impact levels. Drives FIPS 199 categorization.",
        "body": """**What it is:** Two volumes:
- **Vol. I** - methodology for identifying information types and impact.
- **Vol. II** - the catalog itself: dozens of information types (Personnel Management, Financial \
Management, Disaster Management, etc.) with default C/I/A impact ratings.

**How you use it:**
1. Identify which information types your system processes.
2. Look up the suggested C/I/A impact per information type in Vol. II.
3. Adjust per organizational context if you can justify it.
4. Take the **high water mark** across all types in each CIA dimension → that's your system's \
overall categorization (FIPS 199).

**Example walk-through:** A system processing both "Personnel Management" (M-M-L) and \
"Financial Management" (M-H-M) info types categorizes as MODERATE-HIGH-MODERATE.

**Pitfall:** Skipping 800-60 and guessing. Auditors expect to see your 800-60 mapping in the \
categorization document.""",
    },
    {
        "slug": "fips-199",
        "title": "FIPS 199 - Security Categorization",
        "category": "Categorization",
        "url": "https://csrc.nist.gov/pubs/fips/199/final",
        "summary": "The federal standard for categorizing information and systems by impact (Low / Moderate / High) across Confidentiality, Integrity, Availability.",
        "body": """**What it is:** A short, dense standard (16 pages) that defines the **three impact \
levels** and how to apply them.

**Impact level definitions (paraphrased):**
- **LOW** - loss could have **limited** adverse effect.
- **MODERATE** - loss could have **serious** adverse effect.
- **HIGH** - loss could have **severe or catastrophic** adverse effect.

**Per CIA dimension:**
- **Confidentiality** - unauthorized disclosure
- **Integrity** - unauthorized modification or destruction
- **Availability** - disruption of access or use

**Output:** A categorization tuple `{C: low|mod|high, I: low|mod|high, A: low|mod|high}`. \
The system's overall categorization is the **high water mark** across all information types.

**Why it matters:** Drives baseline selection in 800-53B → drives every subsequent control \
selection and assessment intensity.

**For National Security Systems:** Use **CNSSI 1253** instead of pure FIPS 199.""",
    },
    {
        "slug": "fips-200",
        "title": "FIPS 200 - Minimum Security Requirements",
        "category": "Controls",
        "url": "https://csrc.nist.gov/pubs/fips/200/final",
        "summary": "Mandates that federal systems meet the 800-53 baseline appropriate to their FIPS 199 categorization. The 'thou shalt' that makes 800-53 binding.",
        "body": """**What it is:** Brief federal standard (17 pages) that:
1. Lists 17 minimum security requirement areas (basically the 800-53 family names).
2. Mandates that federal agencies select and apply 800-53 controls per their FIPS 199 \
categorization.
3. Allows tailoring per the rules in 800-53B / 800-37.

**Why it exists:** Without FIPS 200, 800-53 would be guidance ("we suggest these controls"). \
With FIPS 200, 800-53 baselines become **mandatory** for federal systems.

**When you'll reach for this:** Almost never directly - it's a one-page citation. But you \
*will* cite it when explaining why the baseline is non-optional.""",
    },
    {
        "slug": "cnssi-1253",
        "title": "CNSSI 1253 - Categorization for National Security Systems",
        "category": "Categorization",
        "url": "https://www.cnss.gov/CNSS/issuances/Instructions.cfm",
        "summary": "The categorization + baseline standard for National Security Systems (NSS). Replaces FIPS 199 / 800-53B for classified and intelligence systems.",
        "body": """**What it is:** Committee on National Security Systems Instruction (CNSSI) 1253 \
covers categorization and control selection for **National Security Systems** - systems that \
involve intelligence, cryptologic activities, command and control of military forces, weapons \
systems, or are otherwise designated by 44 USC §3552(b)(6).

**Key differences from FIPS 199 / 800-53B:**
- **Categorization** is per-objective (Confidentiality / Integrity / Availability) but does \
not require the high-water-mark rule across CIA - different baselines may apply to each.
- Adds the **Classified Information Overlay**, **Privacy Overlay**, **Cross-Domain Solution \
Overlay**, **Space Platform Overlay**, **Intelligence Overlay**, etc. - published as Annexes.
- Coordinates with DoDI 8510.01 for DoD systems.

**When you'll reach for this:** When working on classified, intelligence, or NSS-designated \
systems. Don't apply FIPS 199 to a classified system - wrong standard.""",
    },
    {
        "slug": "sp-800-30r1",
        "title": "NIST SP 800-30 Rev. 1 - Risk Assessment",
        "category": "Process",
        "url": "https://csrc.nist.gov/pubs/sp/800/30/r1/final",
        "summary": "Methodology for conducting risk assessments at the system, mission/business, and organizational tiers. Underpins the RAR.",
        "body": """**What it is:** The methodology behind the **Risk Assessment Report (RAR)** \
in your eMASS package.

**Process at a glance:**
1. **Prepare** - define purpose, scope, threat sources to consider.
2. **Identify threat sources** (adversarial, accidental, structural, environmental).
3. **Identify threat events** - what could those sources do?
4. **Identify vulnerabilities** the events could exploit.
5. **Determine likelihood** of each threat event.
6. **Determine impact** if it succeeds.
7. **Determine risk** as a function of likelihood × impact.

**Output:** A risk register / risk assessment narrative the AO uses to make the authorization \
decision alongside the SAR and POA&M.

**When you'll reach for this:** When writing or updating the RAR; when responding to "what's \
the residual risk?" in package reviews.""",
    },
    {
        "slug": "sp-800-160",
        "title": "NIST SP 800-160 Vols. 1 & 2 - Systems Security Engineering",
        "category": "Engineering",
        "url": "https://csrc.nist.gov/pubs/sp/800/160/v1/r1/final",
        "summary": "Engineering principles for building secure systems (Vol. 1) and developing cyber-resilient systems (Vol. 2). Read by the ISSE.",
        "body": """**What it is:** Two-volume reference for system security engineering.

**Vol. 1 - Systems Security Engineering:** Engineering processes for building security into \
systems from inception, aligned with ISO/IEC/IEEE 15288 (system lifecycle).

**Vol. 2 - Developing Cyber-Resilient Systems:** Adds the cyber-resilience perspective - \
designing for the assumption that adversaries will succeed sometimes. Concepts: redundancy, \
diversity, deception, segmentation, dynamic positioning.

**When you'll reach for this:** Less in day-to-day eMASS work; more when designing a new \
system, building a security architecture document, or arguing for resilience-oriented \
investments.""",
    },
    {
        "slug": "nist-csf-2",
        "title": "NIST Cybersecurity Framework (CSF) 2.0",
        "category": "Process",
        "url": "https://csrc.nist.gov/projects/cybersecurity-framework",
        "summary": "Outcome-based framework for managing cybersecurity risk. Six Functions (Govern, Identify, Protect, Detect, Respond, Recover). Voluntary; widely adopted by US fed contractors and critical infrastructure.",
        "body": """**CSF 2.0** (Feb 2024) is the most widely adopted *outcome-oriented* cybersecurity \
framework in the United States.

**Six Functions:**
1. **Govern (GV)** - new in 2.0. Strategy, roles, policy, supply chain, oversight.
2. **Identify (ID)** - assets, business environment, governance, risk assessment.
3. **Protect (PR)** - access control, awareness, data security.
4. **Detect (DE)** - anomalies, continuous monitoring.
5. **Respond (RS)** - response planning, communications, mitigation.
6. **Recover (RC)** - recovery planning, improvements.

**Implementation Tiers** (Partial -> Risk Informed -> Repeatable -> Adaptive) describe maturity. \
**Profiles** describe current vs target state.

**When to use:** Strategic conversations, board reports, cross-framework mapping. Reference \
controls in 800-53 / ISO 27001 / etc. for implementation detail.""",
    },
    {
        "slug": "sp-800-18r1",
        "title": "NIST SP 800-18 Rev. 1 - Guide for Developing System Security Plans",
        "category": "Process",
        "url": "https://csrc.nist.gov/pubs/sp/800/18/r1/final",
        "summary": "How to author a System Security Plan (SSP). Companion to 800-53 / 800-37; basis for the SSP template every RMF package uses.",
        "body": """**SP 800-18** is the methodology guide for writing the **System Security Plan** \
that's required by the RMF. Every authorization package's SSP is built to its outline.

**Standard SSP sections:**
- System identification (name, owner, contacts)
- System operational status
- General system description / purpose
- System environment
- System interconnections / information sharing
- Related laws, regs, policies
- Security categorization
- Security controls (per 800-53)
- Information system rules of behavior
- Plan completion date / approvals

**When to use:** Reference whenever you author or review an SSP. eMASS auto-generates much of \
this, but the structure matches 800-18.

**Note:** Originally Rev. 1 (2006). A Rev. 2 draft has been in development. Substantively \
superseded for control content by 800-53 Rev. 5 + 800-37 Rev. 2.""",
    },
    {
        "slug": "sp-800-39",
        "title": "NIST SP 800-39 - Managing Information Security Risk",
        "category": "Process",
        "url": "https://csrc.nist.gov/pubs/sp/800/39/final",
        "summary": "Multi-tier risk management framework: organization, mission/business process, and information system tiers.",
        "body": """**SP 800-39** describes the **three-tier risk management** approach NIST applies \
across all federal information security:

| Tier | Scope | Output |
| --- | --- | --- |
| **Tier 1** | Organization | Risk strategy, governance, executive risk frame |
| **Tier 2** | Mission / Business Process | Risk-informed business processes; enterprise architecture |
| **Tier 3** | Information System | RMF (800-37) operates here |

**Why it matters:** RMF (800-37) lives at Tier 3 but is informed by Tier 1 and 2 decisions. The \
AO's risk decision should reflect the organizational risk frame, not just the system's residual \
risk.

**When you'll reach for this:** Building an Enterprise Risk Management (ERM) integration story; \
explaining to executives why a system-level risk decision needs context from above; aligning RMF \
with NIST CSF Govern function.""",
    },
    {
        "slug": "sp-800-34r1",
        "title": "NIST SP 800-34 Rev. 1 - Contingency Planning Guide",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/34/r1/final",
        "summary": "How to develop contingency plans for federal information systems. Backbone of the CP-* control family.",
        "body": """**SP 800-34** prescribes the contingency planning process required by 800-53's \
**CP family**. The Contingency Plan (CP-2) and Contingency Plan Testing (CP-4) are reviewed in \
every ATO assessment.

**Key planning concepts:**
- **BIA (Business Impact Analysis)** - identify critical mission/business functions and recovery \
priorities.
- **MTD (Maximum Tolerable Downtime)** - the longest the org can be without the system.
- **RTO (Recovery Time Objective)** - target restoration time.
- **RPO (Recovery Point Objective)** - max tolerable data loss (in time).

**Contingency strategies:** backup, alternate sites (cold/warm/hot), equipment replacement, \
roles & responsibilities.

**Plan lifecycle:** Develop -> Test (annual minimum: tabletop, functional, full-scale) -> \
Exercise -> Update -> Train.

**When you'll reach for this:** Authoring or reviewing the CP-2 plan; preparing for CP-4 \
exercises; explaining DR/BCP requirements to system owners.""",
    },
    {
        "slug": "sp-800-40r4",
        "title": "NIST SP 800-40 Rev. 4 - Patch Management",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/40/r4/final",
        "summary": "How to plan and run an enterprise patch management program. Underpins SI-2 (Flaw Remediation).",
        "body": """**SP 800-40 Rev. 4** (Apr 2022) modernized the patch management guidance for cloud \
and DevOps realities.

**Major themes:**
- **Patch management as enterprise risk reduction**, not just IT hygiene.
- **Asset inventory** as a precondition. You can't patch what you don't know.
- **Maintenance windows are an old paradigm.** Modern systems patch continuously.
- **Out-of-cycle / emergency patches** for critical vulns (especially actively exploited).

**Operational metrics:**
- Mean Time to Patch (MTTP) by severity
- Patch coverage % across asset types
- Aging report for unpatched vulnerabilities
- Failed patch rate

**When you'll reach for this:** Building or reviewing a patch management program; defending SI-2 \
implementation; designing CI/CD pipelines for system updates.""",
    },
    {
        "slug": "sp-800-47r1",
        "title": "NIST SP 800-47 Rev. 1 - System Interconnections",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/47/r1/final",
        "summary": "Managing the security of system interconnections. Backbone of CA-3 (System Interconnections).",
        "body": """**SP 800-47 Rev. 1** (Jul 2021) governs how to plan, document, and manage \
interconnections between systems with different ATOs.

**Interconnection lifecycle:**
1. **Planning** - define requirements, identify parties, determine connection type.
2. **Documenting** - **ISA (Interconnection Security Agreement)** is the key artifact. Older MOU/MOA \
 also referenced.
3. **Implementing** - configure secure transport, document data types crossing the boundary.
4. **Maintaining** - periodic re-review (typically annually or with significant change).
5. **Disconnecting** - formal termination process.

**ISA contents:**
- Names, types, owners of both systems
- Data classification crossing the boundary
- Security controls protecting the connection
- Termination conditions
- Signatures from both AOs

**Common findings:** missing or expired ISAs, ISAs not reflecting current data flows, \
connections without ISAs.""",
    },
    {
        "slug": "sp-800-50r1",
        "title": "NIST SP 800-50 Rev. 1 - Cybersecurity Awareness Training",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/50/r1/final",
        "summary": "How to design, build, and run a cybersecurity awareness and training program. Backbone of the AT-* family.",
        "body": """**SP 800-50 Rev. 1** (Sep 2024) updated the awareness/training guidance with \
modern delivery channels and metrics.

**Three program tiers:**
- **Awareness** - everyone (basic security hygiene, phishing, social engineering)
- **Training** - role-based (developers, admins, managers)
- **Education** - specialized (security professionals, advanced certs)

**Operational components:**
- Training needs assessment
- Curriculum (content, delivery, frequency)
- Tracking + records (often via LMS)
- Effectiveness metrics (phishing simulation click rates, completion %, knowledge checks)
- Annual refresh requirement

**When you'll reach for this:** Building/reviewing AT-1 and AT-2 implementations; defending the \
training program in audit; answering "how do you know awareness training works?".""",
    },
    {
        "slug": "sp-800-52r2",
        "title": "NIST SP 800-52 Rev. 2 - TLS Implementation Guide",
        "category": "Cryptography",
        "url": "https://csrc.nist.gov/pubs/sp/800/52/r2/final",
        "summary": "Federal guidance on TLS configuration. Mandatory cipher suites, version requirements, certificate validation.",
        "body": """**SP 800-52 Rev. 2** specifies the TLS configurations federal systems must use \
when transmitting sensitive data.

**Key requirements:**
- **TLS 1.2 minimum**; TLS 1.3 recommended.
- TLS 1.0 / 1.1 / SSL prohibited.
- Cipher suite restrictions (forward secrecy required for many use cases).
- Certificate validation (full chain, revocation checking).
- FIPS 140-3-validated crypto modules.

**Common findings:**
- Servers still allowing TLS 1.0/1.1 for "compatibility"
- Self-signed or expired certificates
- Weak cipher suites enabled
- No certificate revocation checking

**When you'll reach for this:** Configuring or auditing TLS endpoints; building SC-8 / SC-13 \
implementation evidence; pen-test response.""",
    },
    {
        "slug": "sp-800-61r2",
        "title": "NIST SP 800-61 Rev. 2 - Computer Security Incident Handling",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/61/r2/final",
        "summary": "The federal incident response process. Foundation of the IR-* control family and most enterprise IR programs.",
        "body": """**SP 800-61 Rev. 2** is the incident handling reference cited everywhere. The \
4-phase lifecycle is the standard.

**Lifecycle:**
1. **Preparation** - playbooks, tooling, training, contacts, IR retainer.
2. **Detection & Analysis** - alerts triaged, severity assigned, incident declared.
3. **Containment / Eradication / Recovery** - short-term contain, root-cause eradicate, restore \
to known-good.
4. **Post-Incident Activity** - lessons learned, evidence retained, controls improved.

**Severity classification** is org-defined. NIST proposes Functional Impact, Information Impact, \
and Recoverability dimensions.

**Coordination:** IR teams must coordinate with management, legal, comms, HR, law enforcement \
(US-CERT / CISA reporting required for federal incidents per FISMA), and partners.

**When you'll reach for this:** Authoring IR-8 plan, preparing tabletop exercises, post-incident \
review. NIST is updating to Rev. 3 (draft as of 2024).""",
    },
    {
        "slug": "sp-800-63",
        "title": "NIST SP 800-63 - Digital Identity Guidelines",
        "category": "Identity",
        "url": "https://csrc.nist.gov/projects/digital-identity-guidelines",
        "summary": "Federal digital identity standard covering enrollment, authentication, federation. Four documents: 63-3, 63A, 63B, 63C.",
        "body": """**SP 800-63** is the federal digital identity reference, structured as four \
volumes:

| Volume | Topic |
| --- | --- |
| **800-63-3** | Overview & risk-based identity proofing |
| **800-63A** | Enrollment & Identity Proofing |
| **800-63B** | Authentication & Lifecycle Management |
| **800-63C** | Federation & Assertions |

**Identity Assurance Levels (IAL):**
- IAL1: self-asserted
- IAL2: remote/in-person identity proofing
- IAL3: in-person identity proofing with strict requirements

**Authentication Assurance Levels (AAL):**
- AAL1: single-factor
- AAL2: multi-factor (something you have + know/are)
- AAL3: hardware-based MFA, verifier impersonation resistance

**Federation Assurance Levels (FAL):**
- FAL1: bearer assertions
- FAL2: + signing
- FAL3: + holder-of-key

**Rev. 4 (draft 2024)** modernized for passkeys, biometrics, and continuous evaluation.

**When you'll reach for this:** Designing IA controls; setting MFA requirements; defending \
authentication architecture; configuring FedRAMP or DoD identity solutions.""",
    },
    {
        "slug": "sp-800-82r3",
        "title": "NIST SP 800-82 Rev. 3 - Industrial Control Systems Security",
        "category": "Specialty",
        "url": "https://csrc.nist.gov/pubs/sp/800/82/r3/final",
        "summary": "Securing OT environments: SCADA, DCS, ICS, PLCs, IIoT. Companion to the ICS overlay.",
        "body": """**SP 800-82 Rev. 3** (Sep 2023) is the federal guidance for securing OT (operational \
technology) systems where IT controls don't translate cleanly.

**Key OT-vs-IT differences:**
- Availability often trumps confidentiality (you can't reboot a turbine to apply a patch).
- Lifecycles measured in decades.
- Proprietary protocols (Modbus, DNP3, OPC) often unencrypted.
- Real-time response requirements.
- Physical safety implications.

**Architecture patterns:**
- **Purdue Model** (levels 0-5) for network segmentation.
- **DMZ between IT and OT** is now mainstream.
- **Unidirectional gateways / data diodes** for one-way data flow.

**Aligns with:** IEC 62443 (international OT cybersecurity standard).

**When you'll reach for this:** Authoring an ATO for an industrial system; mapping OT systems to \
800-53 controls (with the ICS overlay); defending segmentation decisions to safety engineers.""",
    },
    {
        "slug": "sp-800-88r1",
        "title": "NIST SP 800-88 Rev. 1 - Media Sanitization",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/88/r1/final",
        "summary": "How to securely sanitize and dispose of storage media. Underpins MP-6 (Media Sanitization).",
        "body": """**SP 800-88 Rev. 1** prescribes media sanitization. Three sanitization levels:

| Level | Method | Use case |
| --- | --- | --- |
| **Clear** | Logical (overwrite) | Reusing within org, low-sensitivity |
| **Purge** | Cryptographic erase, secure erase, degauss | Reusing across orgs / sensitive data |
| **Destroy** | Shred, incinerate, melt | Highest classification or non-reusable |

**Decision tree:** based on data classification + media reuse plans.

**Documentation:** **Certificate of Sanitization/Destruction** required for each media item; \
serial numbers tracked.

**Modern wrinkles:**
- SSDs: cryptographic erase preferred; overwrite less reliable.
- Cloud storage: provider-managed sanitization (verify in CRM).
- Mobile devices: built-in factory reset is generally Purge-equivalent.

**When you'll reach for this:** Decommissioning hardware; setting media handling policy; \
auditing destruction certificates.""",
    },
    {
        "slug": "sp-800-92",
        "title": "NIST SP 800-92 - Computer Security Log Management",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/92/final",
        "summary": "How to plan, generate, transmit, store, analyze, and dispose of security logs. Backbone of the AU-* family.",
        "body": """**SP 800-92** is the foundational log management reference. Many AU-family controls \
trace directly to its guidance.

**Log management lifecycle:**
1. **Planning** - decide what to log, retention, who reviews.
2. **Generation** - configure source systems.
3. **Transmission** - secure transport (often syslog over TLS).
4. **Storage** - centralized SIEM or log warehouse; integrity protection.
5. **Analysis** - correlation, alerting, periodic review.
6. **Disposal** - retention enforcement.

**Common challenges:**
- Volume - log volume often exceeds storage budget; sampling vs filtering tradeoffs.
- Time synchronization - NTP across all sources.
- Integrity - tamper detection (hash chains, write-once storage).
- Coverage - cloud / SaaS / serverless logs often missed.

**Key controls supported:** AU-2 (Event Logging), AU-6 (Audit Review), AU-9 (Protection of Audit \
Info), AU-11 (Audit Record Retention), AU-12 (Audit Generation).

**Note:** Currently being updated. NIST has a draft Rev. 1.""",
    },
    {
        "slug": "sp-800-115",
        "title": "NIST SP 800-115 - Technical Guide to Information Security Testing",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/115/final",
        "summary": "How to plan and execute security testing: discovery, vuln scanning, pen testing, password cracking, social engineering, war dialing, war driving.",
        "body": """**SP 800-115** is the federal reference for security assessment and testing techniques.

**Test categories:**
- **Discovery** - network mapping, port scanning, service identification.
- **Vulnerability scanning** - automated identification of known vulnerabilities (Nessus, ACAS).
- **Penetration testing** - simulated attacks to validate controls.
- **Application security testing** - SAST, DAST, fuzzing.
- **Wireless testing** - RF surveys, rogue AP detection.
- **Password cracking** - validate password policy effectiveness.
- **Social engineering** - phishing simulations, pretexting.
- **Physical testing** - tailgating, badge cloning.

**Test planning:**
- Rules of engagement
- Scope (in / out)
- Authorization letter
- Communication plan
- Stop conditions

**When you'll reach for this:** Planning a penetration test; building a vuln management program; \
defending CA-2/CA-8 implementations.""",
    },
    {
        "slug": "sp-800-122",
        "title": "NIST SP 800-122 - Protecting PII",
        "category": "Privacy",
        "url": "https://csrc.nist.gov/pubs/sp/800/122/final",
        "summary": "How to identify, classify, and safeguard Personally Identifiable Information. Backbone of the Privacy Overlay.",
        "body": """**SP 800-122** defines PII and prescribes how to protect it. Pairs with the Privacy \
Overlay in CNSSI 1253 Annex F-Privacy.

**PII confidentiality impact levels:**
- **Low** - limited harm if disclosed (name only)
- **Moderate** - more sensitive (SSN partial, DOB, etc.)
- **High** - most sensitive (full SSN, financial, medical, biometric)

**Factors raising the impact level:**
- Identifiability (how easy to link to a person)
- Quantity (single record vs millions)
- Data field sensitivity
- Context of use
- Obligation to protect (Privacy Act, HIPAA, GLBA, etc.)

**Required documents:**
- **Privacy Impact Assessment (PIA)** for any system processing PII
- **System of Records Notice (SORN)** if a Privacy Act system of records

**Breach handling:** Coordinate with org's privacy office and legal. NIST recommends \
risk-of-harm analysis before notification (consistent with state breach laws).""",
    },
    {
        "slug": "sp-800-128",
        "title": "NIST SP 800-128 - Security-Focused Configuration Management",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/128/final",
        "summary": "How to manage information system configurations from a security perspective. Backbone of CM-* family.",
        "body": """**SP 800-128** lays out **SecCM (Security-Focused Configuration Management)** - \
the security overlay on broader IT configuration management.

**Four phases:**
1. **Planning** - establish CM scope and process
2. **Identification** - baseline configurations (CM-2)
3. **Configuration Change Control** - CCB process (CM-3)
4. **Configuration Monitoring** - drift detection (CM-6)

**Baseline types:**
- Hardware configurations
- Software (OS + apps)
- Firmware
- Documentation

**Tooling:** SCAP-compliant scanners check actual configs vs baseline. Drift triggers \
investigation.

**Common findings:**
- Baselines documented but not enforced
- No SCAP compliance scans
- Unauthorized changes not detected
- Production diverges from documented baseline

**When you'll reach for this:** CM family implementation evidence; defending SCAP-based \
compliance; building config drift detection.""",
    },
    {
        "slug": "sp-800-137",
        "title": "NIST SP 800-137 - Information Security Continuous Monitoring",
        "category": "Process",
        "url": "https://csrc.nist.gov/pubs/sp/800/137/final",
        "summary": "How to plan and implement Continuous Monitoring (ConMon) for federal information systems. Required by 800-37 Step 6.",
        "body": """**SP 800-137** prescribes the **ISCM (Information Security Continuous Monitoring)** \
strategy required by RMF Step 6.

**ConMon process:**
1. **Define ISCM strategy** at organizational level.
2. **Establish ISCM program** with selected metrics + cadence.
3. **Implement ISCM program** - tools, automation, processes.
4. **Analyze and report** findings.
5. **Respond** to findings.
6. **Review and update** strategy.

**Common metrics:**
- Vulnerability counts by severity (open, closed, aged)
- Patch compliance %
- Configuration compliance % (SCAP scans)
- Account hygiene (privileged access, dormant accounts)
- Log review compliance
- Training compliance %

**Frequency:** based on **CISO-defined risk tolerances**. Critical metrics often near-real-time; \
others monthly/quarterly/annually.

**A draft Rev. 1 (SP 800-137A and SP 800-137B)** decomposes ISCM into program assessment \
methodology and information sharing.

**When you'll reach for this:** Authoring CA-7 strategy; building or reviewing the ConMon \
dashboard; defending the monitoring program in audit.""",
    },
    {
        "slug": "sp-800-145",
        "title": "NIST SP 800-145 - The NIST Definition of Cloud Computing",
        "category": "Specialty",
        "url": "https://csrc.nist.gov/pubs/sp/800/145/final",
        "summary": "The 5-4-3 model: 5 essential characteristics, 4 deployment models, 3 service models. Universal cloud reference.",
        "body": """**SP 800-145** is the canonical cloud definition cited by everyone. Short doc; deep \
impact.

**5 essential characteristics:**
1. On-demand self-service
2. Broad network access
3. Resource pooling
4. Rapid elasticity
5. Measured service

**4 deployment models:**
- Public
- Private
- Community
- Hybrid

**3 service models:**
- IaaS (Infrastructure)
- PaaS (Platform)
- SaaS (Software)

**Why it matters:** Authorization boundaries, control inheritance, FedRAMP/DoD IL definitions all \
trace back to this model. When mapping a SaaS to your control responsibility (vs the CSP's), the \
service model determines where the line is drawn.""",
    },
    {
        "slug": "sp-800-161r1",
        "title": "NIST SP 800-161 Rev. 1 - Supply Chain Risk Management (C-SCRM)",
        "category": "Process",
        "url": "https://csrc.nist.gov/pubs/sp/800/161/r1/final",
        "summary": "Cybersecurity supply chain risk management practices for the federal enterprise. Backbone of the SR-* family.",
        "body": """**SP 800-161 Rev. 1** (May 2022) is the federal C-SCRM (Cybersecurity Supply Chain \
Risk Management) reference. The new SR family in 800-53 Rev. 5 was added based on this guidance.

**C-SCRM activities:**
- Identify suppliers and supply chain dependencies
- Assess supplier cybersecurity posture
- Implement contractual flow-down requirements
- Continuous monitoring of supplier risk
- Incident response coordination across the supply chain
- Supply chain integrity (counterfeit detection, tamper evidence)

**SBOM (Software Bill of Materials):** central to modern C-SCRM. Required by EO 14028 for \
federal software providers.

**Drivers:** SolarWinds (2020), Log4Shell (2021), MOVEit (2023). Federal mandate from EO 14028.

**When you'll reach for this:** SR family implementation; vendor risk reviews; SBOM strategy; \
defending procurement security clauses.""",
    },
    {
        "slug": "sp-800-171r3",
        "title": "NIST SP 800-171 Rev. 3 - Protecting CUI in Non-Federal Systems",
        "category": "Controls",
        "url": "https://csrc.nist.gov/pubs/sp/800/171/r3/final",
        "summary": "Security requirements for protecting Controlled Unclassified Information when stored on non-federal systems. Backbone of CMMC L2 and DFARS 252.204-7012.",
        "body": """**SP 800-171 Rev. 3** (May 2024) defines the security requirements for handling **CUI \
(Controlled Unclassified Information)** in *non-federal* systems - i.e., contractor and partner \
environments.

**Structure:**
- **17 families** of requirements (Access Control, Audit & Accountability, etc.)
- **97 security requirements** in Rev. 3 (down from 110 in Rev. 2)
- Derived from 800-53 Moderate baseline, tailored for non-federal use

**DFARS 252.204-7012** mandates 800-171 for DoD contractors handling CUI.

**Self-assessment scoring:**
- 110-point scale (Rev. 2) - SPRS submission required.
- Rev. 3 changes the scoring; transition guidance pending.

**CMMC link:** CMMC Level 2 IS 800-171 with third-party assessment.

**When you'll reach for this:** DoD contractor assessments; SPRS scoring; CMMC Level 2 \
preparation; building/auditing CUI environments.""",
    },
    {
        "slug": "sp-800-172",
        "title": "NIST SP 800-172 - Enhanced Security Requirements for CUI",
        "category": "Controls",
        "url": "https://csrc.nist.gov/pubs/sp/800/172/final",
        "summary": "Additional security requirements for CUI in High Value Asset (HVA) or critical-program contexts. Layered on top of 800-171.",
        "body": """**SP 800-172** (Feb 2021) adds enhanced requirements above 800-171 for CUI in higher-\
risk contexts - typically critical defense programs or High Value Assets (HVAs).

**~35 enhanced requirements** addressing:
- **Penetration-resistant architectures**
- **Damage-limiting operations**
- **Advanced cyber threat actor (APT) defense**

**Use case:** Mapped to **CMMC Level 3** (Expert) for the most sensitive DoD programs.

**When you'll reach for this:** CMMC Level 3 assessments; defending HVA / critical infrastructure \
programs; building advanced detection / deception capabilities.""",
    },
    {
        "slug": "sp-800-184",
        "title": "NIST SP 800-184 - Guide for Cybersecurity Event Recovery",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/184/final",
        "summary": "How to plan and execute recovery from a cybersecurity incident. Bridges IR (containment) and CP (continuity).",
        "body": """**SP 800-184** focuses specifically on **recovery** - the often-neglected back-half of \
incident response. Containment stops the bleeding; recovery restores operations.

**Recovery phases:**
1. **Plan** - recovery playbooks for likely scenarios.
2. **Triage & assess** - what's broken, what's clean, what's uncertain.
3. **Restore** - from backups, rebuild, or migrate.
4. **Validate** - confirm restored systems are not re-compromised.
5. **Communicate** - users, customers, regulators.
6. **Lessons learned** - playbook updates.

**Critical reminders:**
- Don't restore from infected backups. Validate backup integrity before use.
- Reset credentials org-wide for ransomware/credential-theft incidents.
- Account for incident-related changes (e.g., temporary firewall rules) before declaring \
recovery complete.

**When you'll reach for this:** Designing IR playbooks; post-ransomware recovery planning; \
tabletop exercise scenarios beyond detection.""",
    },
    {
        "slug": "sp-800-190",
        "title": "NIST SP 800-190 - Application Container Security",
        "category": "Specialty",
        "url": "https://csrc.nist.gov/pubs/sp/800/190/final",
        "summary": "Security guidance for Docker / Kubernetes / container orchestration. Risk areas, threats, and countermeasures.",
        "body": """**SP 800-190** addresses the unique security considerations of containerized \
environments (Docker, Kubernetes, OpenShift, etc.).

**Five major risk areas:**
1. **Image risks** - vulnerable base images, embedded secrets, malicious content.
2. **Registry risks** - insecure registries, stale images, lack of authentication.
3. **Orchestrator risks** - unrestricted admin access, network segmentation, shared kernels.
4. **Container runtime risks** - excessive privileges, vulnerable runtimes, drift.
5. **Host OS risks** - kernel vulns, container breakout.

**Countermeasures:**
- Image scanning (CI + registry + runtime)
- Signed images + policy enforcement (Sigstore, cosign)
- RBAC + network policies in Kubernetes
- Read-only root filesystems
- Distroless base images

**Note:** Older (2017). Modern guidance has expanded to SP 800-204 series for microservices and \
beyond. Still useful as the federal baseline for container security.""",
    },
    {
        "slug": "sp-800-207",
        "title": "NIST SP 800-207 - Zero Trust Architecture",
        "category": "Engineering",
        "url": "https://csrc.nist.gov/pubs/sp/800/207/final",
        "summary": "The federal Zero Trust Architecture (ZTA) reference. Driving force behind EO 14028 and federal ZTA mandates.",
        "body": """**SP 800-207** (Aug 2020) is the federal definition of **Zero Trust Architecture**. \
EO 14028 (May 2021) made ZTA a federal mandate.

**Tenets:**
- Verify explicitly - no implicit trust based on network location.
- Least privilege access.
- Assume breach.
- Continuous verification - authentication and authorization aren't one-and-done.

**Logical components:**
- **PE (Policy Engine)** - decides access.
- **PA (Policy Administrator)** - establishes/terminates sessions.
- **PEP (Policy Enforcement Point)** - enforces decisions.
- Trust algorithms drawing from Identity, Asset, Resource, and Environment data.

**Deployment patterns:**
- Enhanced Identity Governance
- Micro-segmentation
- Software-Defined Perimeter / ZTNA

**Companion docs:** SP 800-207A (planning ZTA), SP 1800-35 (NCCoE practice guide).

**When you'll reach for this:** Architecting modern access; CIO ZTA strategy; explaining \
"why MFA isn't enough"; mapping ZT to 800-53 controls.""",
    },
    {
        "slug": "sp-800-218",
        "title": "NIST SP 800-218 - Secure Software Development Framework (SSDF)",
        "category": "Engineering",
        "url": "https://csrc.nist.gov/pubs/sp/800/218/final",
        "summary": "Software development practices to reduce vulns and respond when they occur. Required by EO 14028 federal software self-attestation.",
        "body": """**SP 800-218** (Feb 2022) is the **SSDF (Secure Software Development Framework)**. \
EO 14028 + OMB M-22-18 require federal software vendors to self-attest to SSDF practices.

**Four practice categories:**
- **Prepare the Organization (PO)** - policies, training, infrastructure.
- **Protect the Software (PS)** - protect code from tampering, manage releases.
- **Produce Well-Secured Software (PW)** - secure design, secure coding, testing.
- **Respond to Vulnerabilities (RV)** - identify, analyze, remediate, disclose.

**Each practice has tasks** with examples of implementation.

**Self-attestation:** OMB form (CISA-published) used by federal software providers; covers \
SSDF tasks + EO 14028 sec. 4(e) requirements.

**SBOM (Software Bill of Materials)** is increasingly part of compliance evidence.

**When you'll reach for this:** Federal software vendor compliance; SDLC security maturity; \
defending dev-side controls in an ATO.""",
    },
    {
        "slug": "sp-800-221",
        "title": "NIST SP 800-221 - Enterprise ICT Risk Management",
        "category": "Process",
        "url": "https://csrc.nist.gov/pubs/sp/800/221/final",
        "summary": "Integrates cybersecurity, privacy, and ICT (information and communication technology) risk management into Enterprise Risk Management (ERM).",
        "body": """**SP 800-221** (Nov 2022) integrates cybersecurity / privacy / ICT supply chain \
risks into broader **ERM (Enterprise Risk Management)**.

**Key concepts:**
- **Risk register** at the enterprise level
- **Risk profile** integration across cyber, privacy, ICT, and traditional ERM categories
- **CSF (Cybersecurity Framework) alignment** for the cyber slice
- **800-37 RMF** for system-level risk integration
- Translation between technical risk (CVSS) and business risk (impact dollars, mission impact)

**Why it matters:** Boards want one view of risk - cyber alongside financial, operational, \
strategic. SP 800-221 gives federal CISOs the language to talk to CFOs and ERM teams.

**When you'll reach for this:** Building a CISO-to-ERM bridge; aggregating system-level risks \
to enterprise; explaining cyber risk in business terms.""",
    },
    {
        "slug": "fips-140-3",
        "title": "FIPS 140-3 - Security Requirements for Cryptographic Modules",
        "category": "Cryptography",
        "url": "https://csrc.nist.gov/projects/cryptographic-module-validation-program/standards",
        "summary": "Federal standard for validation of cryptographic modules. Required for any crypto in federal systems.",
        "body": """**FIPS 140-3** (effective Sep 2019; superseded FIPS 140-2 for new validations Sep \
2021) specifies validation requirements for cryptographic modules used in federal systems.

**Aligned with:** ISO/IEC 19790:2012 + 24759:2017.

**Four security levels** (1=basic, 4=physical tamper-resistance for hostile environments).

**Validation process** by **CMVP (Cryptographic Module Validation Program)**:
- Modules tested by NVLAP-accredited labs.
- Listed on NIST CMVP validated module list.
- Validation period: typically 5 years before re-validation needed.

**Why it matters:**
- Federal systems cannot use crypto from unvalidated modules.
- FedRAMP requires FIPS 140-3 validated crypto modules in moderate+ baselines.
- DoD requires it across the board.

**Common pitfall:** Using a library that has FIPS-mode but isn't FIPS-certified, or using a \
certified module in a non-approved configuration.

**When you'll reach for this:** Selecting crypto libraries / HSMs; defending SC-13 evidence; \
cloud service crypto inheritance.""",
    },
    {
        "slug": "fips-197",
        "title": "FIPS 197 - Advanced Encryption Standard (AES)",
        "category": "Cryptography",
        "url": "https://csrc.nist.gov/pubs/fips/197/final",
        "summary": "The federal standard for symmetric encryption. AES-128, AES-192, AES-256.",
        "body": """**FIPS 197** standardizes the **Advanced Encryption Standard (AES)**, the \
mandatory symmetric encryption algorithm for federal systems.

**Variants:** AES-128 / AES-192 / AES-256.

**Use across federal systems:**
- Data at rest encryption
- TLS / VPN tunnels
- Database encryption
- File / volume encryption
- Backup encryption

**Modes of operation:** specified in **NIST SP 800-38 series** (CBC, GCM, CTR, etc.). GCM is the \
modern default for authenticated encryption.

**Quantum considerations:** AES-256 considered quantum-resistant; AES-128 weakened by Grover's \
algorithm to ~64-bit security. Post-quantum cryptography (PQC) doesn't replace AES; it \
addresses asymmetric crypto.""",
    },
    {
        "slug": "fips-180-4",
        "title": "FIPS 180-4 - Secure Hash Standard (SHS)",
        "category": "Cryptography",
        "url": "https://csrc.nist.gov/pubs/fips/180/4/final",
        "summary": "Federal standard for cryptographic hash functions. SHA-1, SHA-2 family (SHA-224/256/384/512).",
        "body": """**FIPS 180-4** specifies approved hash functions:
- **SHA-1** - deprecated for digital signatures and most uses (collisions found 2017).
- **SHA-2 family**: SHA-224, SHA-256, SHA-384, SHA-512, SHA-512/224, SHA-512/256. All approved.
- **SHA-3** family is in **FIPS 202** (separate document; sponge construction).

**Federal use cases:**
- Digital signatures (with FIPS 186-5)
- HMAC for authentication
- Password hashing (with proper KDF like PBKDF2 / scrypt / Argon2id - see SP 800-132)
- Certificate fingerprints
- Integrity checks

**Practical guidance:**
- SHA-256 is the default modern choice.
- SHA-1 is fine ONLY for non-security uses (file de-dup, etc.).
- For password storage, use a slow KDF, not raw SHA-2.""",
    },
    {
        "slug": "fips-186-5",
        "title": "FIPS 186-5 - Digital Signature Standard (DSS)",
        "category": "Cryptography",
        "url": "https://csrc.nist.gov/pubs/fips/186-5/final",
        "summary": "Approved algorithms for digital signatures: ECDSA, RSA, EdDSA. Updated Feb 2023.",
        "body": """**FIPS 186-5** (Feb 2023) updates the federal digital signature standard.

**Approved algorithms:**
- **RSA** - per FIPS 186-5 + PKCS #1 v2.2 (RFC 8017). Min 2048-bit modulus.
- **ECDSA** - elliptic curve DSA. Approved curves in FIPS 186-5 Appendix.
- **EdDSA** - Edwards-curve DSA (Ed25519, Ed448). Newly approved in Rev. 5.

**Removed:** DSA (the original Digital Signature Algorithm) is deprecated for new signatures.

**Hash function pairing:** Per FIPS 180-4 / FIPS 202. Typically SHA-256+ for modern use.

**Quantum considerations:** All current asymmetric algorithms are vulnerable to Shor's algorithm \
on a sufficiently large quantum computer. NIST is standardizing PQC algorithms (FIPS 203, 204, \
205, 206) for post-quantum signatures.""",
    },
    {
        "slug": "sp-800-150",
        "title": "NIST SP 800-150 - Cyber Threat Information Sharing",
        "category": "Operations",
        "url": "https://csrc.nist.gov/pubs/sp/800/150/final",
        "summary": "Guidance for establishing, participating in, and operating cyber threat information sharing programs.",
        "body": """**SP 800-150** prescribes practices for sharing cyber threat intelligence (CTI) \
across organizations.

**Information types:**
- Indicators of Compromise (IoCs) - hashes, IPs, domains, registry keys
- Tactics, Techniques, Procedures (TTPs)
- Threat actor profiles
- Vulnerabilities + exploit data
- Defensive measures

**Standards for sharing:**
- **STIX (Structured Threat Information Expression)** - data format
- **TAXII (Trusted Automated Exchange of Indicator Information)** - transport protocol
- **MITRE ATT&CK** - common TTP vocabulary

**Sharing organizations:**
- ISACs (Information Sharing & Analysis Centers) by sector
- ISAOs (Information Sharing & Analysis Orgs) - broader
- CISA / US-CERT for federal coordination
- FBI InfraGard for critical infrastructure

**Trust models:** TLP (Traffic Light Protocol) - White, Green, Amber, Red - controls \
redistribution.

**When you'll reach for this:** Joining a sector ISAC; building CTI capability; integrating \
threat feeds into your SIEM / SOAR.""",
    },
]


def list_publications() -> list[dict]:
    return [
        {"slug": p["slug"], "title": p["title"], "category": p["category"],
         "summary": p["summary"], "url": p["url"]}
        for p in PUBLICATIONS
    ]


def get_publication(slug: str) -> dict | None:
    for p in PUBLICATIONS:
        if p["slug"] == slug:
            return p
    return None
