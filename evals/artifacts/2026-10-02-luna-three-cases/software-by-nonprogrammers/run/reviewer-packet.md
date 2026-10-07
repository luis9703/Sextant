# Neutral review packet

## Question
“/sextant 我看到越来越多不懂编程的人也能借助 AI 做出自己的小工具。如果这种能力继续发展，未来十年软件、工作分工和公司的形态会变成什么样？请展开不同的未来。”

## Cutoff and scope
Information cutoff: 2026-10-02. Ten-year horizon, roughly through 2036, with no point probability. Broad/global question; institutional variation matters. Focus on AI-assisted creation by people without programming backgrounds and consequences for software, work division and firms. “Make” includes prototype, personal automation, maintained shared service and high-risk production system; these are distinct. No numerical premise for nonprogrammer prevalence is assumed. Current observations below are explicitly bounded; pathways are conditional and overlap.

## Candidates and conditions
1. **Local-tool abundance with maintenance layer.** Domain workers create team tools; organizations provide identity, data permissions, monitoring and recovery rails. Requires reusable components/connectors and accessible testing/ownership practices; may stall on maintenance, integrations or accountability.
2. **Domain expertise becomes executable and shifts roles.** Workers encode local process knowledge, reduce handoffs and potentially learn through use; requires worker discretion, ability to inspect/override, and incentives that recognize quality. Could instead extract tacit knowledge and reduce autonomy.
3. **Assurance becomes scarce; firms centralize rails.** Internal catalogs/platforms and specialists validate generated software; requires incidents, regulation, customer demands or economies sufficient to justify governance. Could fail through bottlenecks or shadow IT.
4. **Backlash and purposeful simplicity.** Failures, hidden lifecycle costs or deskilling lead to selective use, maintained products, human-owned critical processes and protected non-automation zones. Requires persistent total-cost/safety mismatch; weakened if verification becomes reliable and cheap.
5. **Situational software, less app ownership (speculative).** Runtime composition replaces some stable interfaces, conditional on reliable semantics/state, permissions, rollback, audit and recourse. Failure in any of these returns users to fixed tools.

## Supporting and conflicting evidence
- Stack Overflow 2025 survey retrospective (49k+ developer respondents; survey design is platform-specific): reports AI use in 79% of developers in 2025 and falling confidence/concerns about complex work; supports uptake among sampled developers alongside trust friction, not population-level nonprogrammer adoption. https://stackoverflow.blog/2026/10/01/a-look-back-before-we-look-forward-a-developer-survey-retrospective/
- GitHub enterprise software-team survey, 2,000 respondents across US, Brazil, Germany, India, 2024; self-reported ever-use and uneven company support. Supports gap between individual experimentation and institutionalization; respondents are software-team workers. https://github.blog/news-insights/research/survey-ai-wave-grows/
- NBER field deployment of conversational assistance to 5,179 customer-support agents: +14% mean issues/hour, heterogeneous effects with larger improvement for novice/low-skilled agents and minimal impact for experienced/high-skilled. Supports one bounded task-assistance/knowledge-diffusion mechanism, not software creation. https://www.nber.org/system/files/working_papers/w31161/revisions/w31161.rev1.pdf
- METR randomized trial of 16 experienced open-source developers performing 246 tasks on familiar mature projects with early-2025 tools: reports 19% increase in task completion time when AI permitted. Small and selected sample; counterevidence to universal acceleration, not representative of nonprogrammers or current/future systems. https://metr.org/Early_2025_AI_Experienced_OS_Devs_Study-paper.pdf
- NIST AI RMF Generative AI Profile recommends lifecycle testing, provenance, monitoring and operator proficiency; shows assurance practices are recognized, not which firm structure will be adopted. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- NIST Secure Software Development Practices for Generative AI and Dual-Use Foundation Models (SP 800-218A, 2024): security-development guidance remains relevant. https://doi.org/10.6028/NIST.SP.800-218A

## Evidence limits
This bounded search did not establish prevalence, retention, security incident rates or long-run maintenance outcomes for nonprogrammer-built tools, nor did it show firms already reorganizing around them. Surveys are self-reported and sample developers/software teams. The NBER study concerns support conversations, and METR's sample is small and experienced. These sources support conditional mechanisms, not certainty about 2036.
