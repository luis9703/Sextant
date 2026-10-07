# Pathways synthesis

## Present footholds and limits

HTML is the Web's core markup language, and the W3C describes the Web as an application platform for interactive cross-device experiences ([W3C HTML](https://www.w3.org/TR/html/all/); [W3C Web Standards](https://www.w3.org/standards/)). It is plausible as a delivery and interaction layer. It does not by itself settle the structure of calculations, ownership, audit, offline access or archival requirements.

Office-like work is already distributed across web and desktop. Google documents browser editing, Office-file compatibility and conversion as well as conditional offline support ([Office files in Google Workspace](https://support.google.com/docs/answer/9406611?hl=en-419); [offline Docs/Sheets/Slides](https://support.google.com/docs/answer/6388102?hl=en-NZ)). Current file and app interoperability is imperfect by design: ECMA-376 defines OOXML vocabularies and packaging, and Microsoft's described coauthoring flow supports selected Office formats while listing HTML as local-only ([ECMA-376](https://ecma-international.org/publications-and-standards/standards/ecma-376/); [Microsoft coauthoring file types](https://learn.microsoft.com/en-us/microsoft-365/cloud-storage-partner-program/plus/extensions)). Such constraints can change; they explain today's friction only.

Two public-company observations resist an immediate “no market” answer. Microsoft's FY2026 Form 10-K reports Microsoft 365 Commercial cloud revenue growth of 17%, seats growth of 6%, Consumer cloud revenue growth of 28%, and Consumer subscriber growth of 7%, while the named commercial bundle includes collaboration, security/compliance and Copilot as well as Office apps ([SEC filing](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm)). Kingsoft reports 2025 office software/services revenue growth of 16% and management attributes parts of this to WPS AI, broader scenarios and enterprise adoption ([Kingsoft annual report](https://ir.kingsoft.com/static-files/999c2fb6-9739-4c00-a3d7-ec00dc5430b6)). These are current commercial signals, not independent evidence of causation, product-level market share or what happens next.

## Four connected but distinct future pathways

### A. Agent-created artifacts make the suite a review and control room

**Bridge.** AI agents can already be directed to create Office-native artifacts, according to Microsoft's product documentation, with tenant storage and licensing/admin controls ([Microsoft Learn](https://learn.microsoft.com/copilot/microsoft-365/wordexcelppt-agents)). If agents become dependable at formulas, layout, citations and change tracking, more first drafts will arrive already formed. People may spend less time typing and more time checking source alignment, selecting variants, negotiating edits and authorizing consequential changes.

**Changed life and feedback.** An analyst asks for three versions of a monthly outlook; a manager sees the assumptions and requests a scenario, not a rewrite. Repetition makes traceable edits and review queues valuable. The suite's interface may become a set of exception and approval surfaces over persistent documents, data and tenant identity. Demand for the traditional authoring surface can fall even while paid suite/cloud services remain in use. This pathway differs from a no-file workflow: the durable artifact remains central.

**Conditions / branch.** Requires materially lower error rates for routine work, permission-aware agents, legible provenance and human override. If explanations are uncheckable or agents alter formulas silently, teams restrict generation and return to direct editing or manual spreadsheets. If AI creation becomes commoditized outside the suite but file exchange stays standard, value may move to interoperability or review services.

**What would change the assessment.** Repeated employer deployment of agents that both edit and preserve audit history would strengthen the transition; demos or isolated pilots would not. Continued dependence on staff to repair generated formulas or reformat files would weaken it. Competing explanation: revenue growth could reflect bundling/pricing or security services rather than greater document need.

### B. HTML is a lens on a living source, with snapshots at institutional boundaries

**Bridge.** Structured data, web components and role-based links could let one typed work object produce tailored views while retaining a canonical source and versions. The monthly deck's charts become navigable slices. Recipients ask questions or fork views; edits to source definitions propagate. Teams learn to argue over measure definitions and permissions instead of slide order.

**Changed life and feedback.** Once the audience can inspect the same live metric, analysts may stop rebuilding near-duplicate decks. Recipients can prepare questions before a meeting; managers may feel more agency but also see their comparisons exposed. Errors travel quickly across views, so the same demand for a correction may create urgency for a preserved “what was approved then” snapshot. A hybrid ecosystem emerges: HTML for reading/exploration, the structured model for computation and governance, and Office/PDF for handoff or record retention.

**Conditions / branch.** Needs semantic structure, stable identity and permission inheritance, reliable offline behavior or an export fallback, and institutional acceptance of versioned web records. If links change after approval, access cannot be granted across organizations, or screen readers/printing/data extraction fail, counterparties demand static files. The live object may then survive internally but not at organizational boundaries.

**What would change the assessment.** For a sampled workflow, observe whether source corrections automatically update downstream views without breaking approved history; count recurring retranscription and file-roundtrips from system logs, not anecdote alone. More HTML views alone could indicate communication trends without replacing authoring.

### C. Workflow systems become the source; documents become generated receipts

**Bridge.** An AI agent can combine database queries, task state, email and policy checks to propose a decision in the system where work already happens. If business systems offer trustworthy citations and replayable versions, a team may approve a decision directly and generate a brief or spreadsheet only when needed. The record is the event, inputs and rationale rather than the file.

**Changed life and feedback.** Repeated approvals make the system's fields and status transitions more important than document templates. People may learn to make decisions in smaller, continuous steps rather than wait for a monthly review deck. This can democratize access to current information, but also shifts power to whoever defines the workflow schema and agent permissions. New demand arises for contesting, correcting and exporting a decision trail.

**Conditions / branch.** Requires accessible APIs, stable data contracts, clear accountability for model-generated recommendations, and ability to preserve source snapshots. If source data are fragmented, meetings require narrative persuasion, or business logic cannot be encoded, people will continue to assemble Office documents as a boundary object. This route does not require Office vendors to disappear: suites may integrate workflow agents or become export/review clients.

**What would change the assessment.** Look for a routine decision where approvals and corrections occur in the operational system and generated documents are no longer the primary collaboration surface. A shift to HTML dashboards without changing who records or approves decisions would be a weaker signal. Rival explanation: a business app may simply add a document preview while the file remains canonical.

### D. Compatibility, offline capacity and institutional memory keep files in circulation

**Bridge.** A work artifact crosses employers, regulators, suppliers and decades of archives. Format support, local editing and stable exports have value when the receiver cannot join the creator's cloud. Offline web apps already exist but require setup and local browser storage in Google's documented workflow; this narrows rather than erases the local/offline branch ([Google offline help](https://support.google.com/docs/answer/6388102?hl=en-NZ)).

**Changed life and feedback.** People use AI to prepare more capable workbooks, but exchange them as familiar files because the next actor must inspect or modify them. Each new recipient may add macros, formulas, comments or a template rule. Those additions raise migration costs and preserve demand for compatibility testing, format repair and signed exports. The suite may look less like an app subscription and more like dependable machinery for rendering, editing and preserving old institutional memory.

**Conditions / branch.** Requires continuing heterogeneity in software access, offline requirements, archival rules or complex native features. If cross-platform fidelity improves and buyers accept web-native provenance, the network effect can decline. Hard constraint: files cannot magically make incompatible formulas or fonts behave identically; the current specific limitations are changeable, not proof of perpetual file dominance.

**What would change the assessment.** Track how often real cross-company workflows require editable Office attachments, offline use, archived version recovery and repair after conversion, with denominators by workflow. A falling Office subscription share alone could reflect a shift to cloud bundles while the artifact persists.

## Relative sequence and interactions

These paths can coexist by task. A likely order, conditional rather than dated: AI drafts and summarizes inside current apps first; structured sources then feed audience-specific web views; some recurring internal approvals migrate into workflow systems; external handoffs and archives continue to request files until shared identity, provenance and preservation rules change. The first two transitions can reinforce each other: more generated variants increase review burden; live linked sources reduce copying but heighten the need for permission and version controls. The final path can stall the others or create a complementary market for adapters.

## Observations that distinguish mechanisms

- **App use vs suite demand:** instrument active authoring, review, storage, identity and governance separately. Falling editor time with stable or rising subscription revenue suggests unbundling of use from payment, but pricing, bundle changes and seat definitions are competing explanations.
- **Artifact canonicality:** inspect approved workflows for the authoritative object (file hash, live object version, or workflow event). A browser-rendered page by itself does not identify the source of truth.
- **Round-trips and exports:** sample transactions to establish how often HTML links return as Office/PDF files and why. Track policy requirements, external access, offline needs and conversion defects separately.
- **Agent reliance:** measure accepted vs materially corrected AI edits in production tasks, with error severity and human review time. High generation volume can mean usefulness or costly rework.
- **Payment/capture:** separate end-user willingness to pay for editor features from employer payment for identity, retention, storage, AI usage or compliance. Vendor segment growth is not a direct measure of any one category.
- **Nonconsumption/refusal:** identify settings where no report is produced because cost/time is too high and ask if cheap agents unlock a new action, or create unwanted communication overload. No current broad population measure is available here.

## Unresolved branches

No reliable global series was located for HTML use as a communication format, office-suite penetration by task, artifact canonicality, comparative AI productivity, conversion error burden, or user-level payment preferences. These unknowns do not block conditional imagination; they block population-wide claims, precise timing and probabilities. “Everyone uses HTML” remains an unverified local impression or shorthand.
