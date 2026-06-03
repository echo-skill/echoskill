---
name: write-verified-advisory
description: Author professional, evidence-based technical advisories, consultant reports, or research memos as local .md files. This skill is invoked when asked to summarize technical research, provide formal guidance to stakeholders, or document empirical findings from a session. Triggers include phrases like "write a report," "prepare an advisory," "summary for the client," or "technical memo."
effective_targets: ['claude', 'gemini']
---

# Verified Advisory & Technical Report Creation

This skill defines a standardized workflow for producing authoritative, research-backed technical reports. It mandates a dual-output structure to ensure both internal technical integrity and professional stakeholder communication.

## Mandates

### 1. Hallucination Defense: Physical Proof Mandate
Every technical claim and quote MUST be physically proven via raw tool output in the current session. **Summarized memory or "model reconstruction" of quotes is strictly prohibited.**

**Verification Mandates:**
1.  **Direct Tool Proof:** You MUST execute a tool (`curl`, `grep`, or `web_fetch`) that returns the **exact verbatim text** of the quote you intend to use.
2.  **The "Literal Block" Rule:** In Artifact C (Audit), you MUST provide a "Physical Proof Block" for every single quote. This block MUST contain:
    *   The EXACT tool command used.
    *   The EXACT raw output from that command (including surrounding context).
3.  **No "Drafting" Quotes:** You are PROHIBITED from "drafting" or "refining" a quote. You must copy and paste it from the tool output. If the tool output is messy (e.g., HTML), you may strip tags but you MAY NOT change words or sentence structure.
4.  **No Phrasal Hallucinations:** Do not use phrases like "The ability to start a debug session is controlled by..." unless you see that EXACT string in a tool output.
5.  **Failure Protocol:** If you cannot find the EXACT PHRASE in a tool output, you MUST state "VERIFICATION FAILED" and either find the correct phrasing or describe the fact without quoting.
6.  **Multiple Links:** You may link to multiple sources to support a claim (e.g., one for the permission name, one for the explanation), but each quote must be individually verified against one of them.

### 2. Dual-Artifact Mandate
The agent MUST produce two distinct artifacts for every advisory task to ensure both internal clarity and professional external delivery:

#### Artifact A: The Master Advisory (Internal Reference)
- **Voice:** Senior Consultant to Peer/Internal Team.
- **Terminology:** Uses technical terms like "Stakeholder," "Customer," and specific first names (e.g., "Nihanth").
- **Content:** The "Master Source of Truth." Includes full technical deep-dives, historical context, and internal rationale that might be too blunt or "meta" for the customer. It MUST preserve all session learnings, best practices, code snippets, sandbox logs, and detailed context gathered during research, ensuring zero context loss. The external message draft is designed to be a polished, action-oriented subset of this master context.
- **Expertise Presentation:** DO NOT include verification dates or methods. Present findings with the authority of a seasoned consultant.
- **Citations:** Use clean inline hyperlinks and verbatim quotes to back claims.
    - ✅ "As detailed in [Apigee's official documentation](URL), the policy is strictly bound to its own local bundle..."
    - ✅ "This behavior is consistent with the [spec's runtime requirements](URL), where we find the following quote: '...'"
    - ❌ "Verified: 2026-03-30 via curl..." (MOVE TO ARTIFACT C)
    - **Source Preference:** Avoid citing local `.md` files as sources in the advisory, as customers typically receive information via email or chat. Instead, search for the corresponding communication (email or chat) and cite it by date and subject/context.
- **Format:** Saved under `{customer-project-repo-root}/customer/issues/MM-dd-issue-name/README.md`.

#### Artifact B: The Draft Communication (Customer-Facing)
- **Voice:** Senior Consultant speaking directly to the customer.
- **Tone:** Professional, second-person ("You," "Your team"). 
- **Terminology:** AVOIDS "Consultant-speak" like "Stakeholder." Treats the audience as known colleagues.
- **Content:** Polished, actionable summary derived from the Master Advisory. It must NOT contain any critical logic or data that isn't present in the Master Advisory.
- **Styling (Email Appearance):** To make the output look like an email rather than a document:
    - **No Headings:** Do NOT use Markdown headings (`#`, `##`, etc.). 
    - **Formatting:** Use bold text on its own line with an empty line above and below to separate sections.
    - **Font Size:** Ensure the visual structure implies a uniform font size throughout, avoiding size variations typical of document headers.
    - **HTML Format:** Always use HTML format for the draft email when bullets or links are involved.
- **Mandatory Closing:** 
    - Always encourage the customer to ping for any clarifications.
    - Offer the option to schedule a meeting for further discussion.
    - **Intelligent Constraint:** If a meeting is already scheduled for the same day, mention that meeting as the next follow-up opportunity rather than suggesting an additional separate session.
- **Format:** Saved under `{customer-project-repo-root}/customer/issues/MM-dd-issue-name/message_draft.md`.

#### Artifact C: The Verification Audit & Gap Analysis (Author-Facing)
- **Format:** Rendered as a response in the chat session.
- **Content:** Raw, thorough, and technical audit trail for the author.
- **Audit Trail:** Lists every fact/claim from Artifact A and provides:
    - The exact command used to verify (e.g., `curl -L -s <URL> | grep '...'`).
    - The timestamp of the verification.
    - A snippet of the raw response that confirmed the claim.
- **Gap Analysis:** Lists any claims that were not fully sourced, explains why certain items were categorized as assumptions, and identifies "misses" for potential iteration.

### 3. Structure & Tone (Master Advisory)
- **Tone:** Professional, direct, and authoritative (Senior Consultant/Engineer persona).
- **Required Sections:**
    - **Executive Summary / Context:** Concise statement of the issue or request.
    - **Verified Technical Findings:** Detailed evidence with verified links and quotes.
    - **Advisory & Recommendations:** Clear, actionable guidance derived from the findings.
    - **Caveats:** Only include critical constraints for the stakeholder (e.g., version limits).

### 4. Privacy & Portability
- **Path Neutrality:** Never include local absolute paths or machine-specific locations. Use generic placeholders like `<PROJECT_ROOT>`.

### 5. Link Formatting Integrity
- **Standard Markdown:** ALWAYS use standard Markdown `[Text](URL)` syntax when writing to local `.md` files (Advisories, READMEs, message drafts). 
- **Tool-Specific Conversion:** ONLY convert to platform-specific syntax (e.g., Google Chat `<URL|Text>`) at the final step when calling the specific messaging tool. NEVER commit platform-specific link syntax to the local repository or workspace documentation.

### 6. Delivery & Storage Mandate
- **Google Drive Upload:** Once the advisory and draft are ready, the agent MUST upload the files to Google Drive.
    - **Path Resolution:** Check `customer.yaml` in the project root for the customer's specific Google Drive folder ID or path. If not specified, default to `My Drive / Customers / <Customer Name>`.
    - **Folder Link:** Whenever the agent uploads or updates a file on Google Drive, it MUST provide a clickable/navigable link to the destination folder in the chat response.
    - **Option A: Google Doc & Cloud Sharing (Highly Recommended if Customer Supports Google Docs):** Create a native Google Doc inside the customer's shared Google Drive folder. Use the global reusable script located at `~/.gemini/skills/write-verified-advisory/scripts/build_native_google_doc.py` to automate the parse-upload-convert-export workflow:
      ```bash
      python3 ~/.gemini/skills/write-verified-advisory/scripts/build_native_google_doc.py \
        --input <path_to_advisory.md> \
        --folder <drive_folder_id> \
        --name "<Document Name>"
      ```
      This automatically creates a native Google Doc and outputs a high-fidelity local Word `.docx` file side-by-side.
    - **Option B: Local Word Document (.docx) Alternative:** If not using Option A, generate a polished Microsoft Word (`.docx`) file locally. If `pandoc` is not available, convert the Markdown file to basic HTML first, then run the built-in macOS utility:
      `textutil -convert docx <file>.html -output <file>.docx`
      *Note: Google Doc or Docx creation is offered at the end as an alternative to the HTML email draft.*
    - **Option C: Gmail Draft (Mandatory for Email):** For email communications, ALWAYS create a draft only (never send directly). The email draft MUST be created as a fully formatted, rich HTML-based email in Gmail using the content of `message_draft.md` with appropriate inline hyperlinks.

### 7. Post-Send Synchronization Mandate
- **Verification of Sent Content:** After the user confirms they have sent the email, the agent SHOULD check the sent email (via Gmail API) to see if the content was altered during the sending process.
- **Targeted Edits Only:** If changes are detected (e.g., altered greeting, footer, or minor phrasing), the agent MUST update the local `.md` files to match the sent version.
- **No Sweeping Overwrites:** Edits must be targeted at the sentence or paragraph level. Do NOT overwrite the entire file.
- **Git Commit First:** The agent MUST commit the current state of the `.md` files to git *before* making any updates based on the sent email.

### 8. Link Validation & 404 Prevention Mandate
- **Active Link Verification:** Every external hyperlink/URL (pointing to external domains like `cloud.google.com` or general web guides) included in any advisory, message draft, or documentation MUST be actively tested and verified in the browser or via a network request in the current session BEFORE final delivery.
- **No Assumptions:** Never assume a URL is correct just because it follows a standard pattern. Document URLs change, redirect, or return 404.
- **Dead Link Prevention:** Under no circumstances should a dead, broken, or 404 link be presented to a user or customer. If a link is found to be dead during validation, the agent MUST search for the correct active URL, verify it, and use it instead.
- **Proof Enforced in Audit:** To guarantee this mandate is respected, the agent **MUST** list *every single hyperlink* generated in the advisory or draft in **Artifact C (Verification Audit)**, explicitly documenting its verification status (e.g., `"HTTP 200 OK verified via browser subagent"` or `"HTTP 200 OK verified via curl -I"`). No delivery can proceed without this verification block.

### 9. Standard Infrastructure Integration Guidelines
When documenting architecture that maps custom domains (e.g., `https://custom-subdomain.customer.com/`) to Google Cloud Services through third-party Identity Providers (e.g., Okta, Azure AD) and Google Cloud Load Balancers (GCLB), the advisory MUST clearly detail:
1.  **DNS Configuration:** Explicit instructions to create an `A` or `CNAME` record in the corporate DNS registrar pointing the custom subdomain to the public Anycast IP of the GCLB.
2.  **GCLB URL Map Rules:** The exact YAML/Terraform configuration for host and path rewriting (e.g., proxying `/us/home/cid/...` backend to Google's internal services while rewriting the host header).
3.  **IdP (Okta) Redirect URIs:** Explicitly state that the IdP Redirect URI must target Google's global federation endpoint (`https://auth.cloud.google/signin-callback/...`), NOT the custom domain, because session establishment must land on Google's endpoint first.
4.  **WIF Authorized Domains:** Confirm that the Workforce Provider configuration (`authorized_domains` in Terraform) contains the custom domain, as Google's sign-in endpoint will otherwise block the post-SSO callback.

### 10. Anti-AI Phrasing Mandate (Humanized Subject & Titles)
- **Strict Ban on Generic Jargon:** The agent MUST **NEVER** use the phrase "Technical Advisory", "Technical Report", or generic templates like "Technical Memo" in the document title, headings, email subject lines, or file names. These phrases are dry, formulaic, and distinctly AI-like.
- **Humanized, Focus-Driven Phrasing:** Instead, use context-specific, action-oriented, and natural human phrasing that immediately communicates the topic of the document.
  *   ❌ "Technical Advisory: Custom Domain Setup"
  *   ✅ "SSO Redirection Design & Configuration Guide: Gemini Custom Domain Setup"
  *   ❌ "Subject: Technical Review & Redirection Flow Diagrams"
  *   ✅ "Subject: Diagrams & Verification Guide: Custom Domain Setup for Gemini Enterprise"
- **Apply Everywhere:** This rule applies strictly across the Master Advisory titles, Google Doc names, Word file names, and email subject lines.

### 11. Programmatic Diagram Rendering Mandate (Mermaid-to-PNG)
- **The Requirement:** Whenever the advisory requires visual system, sequence, or architecture diagrams, the agent MUST author the diagram using plain-text Mermaid sequence blocks and save it locally as a raw `.mmd` file.
- **No Manual Interventions:** The agent MUST **NEVER** require the user to manually copy-paste raw Mermaid code into external web editors or local renderers to view the image.
- **The Programmatic Solution:** Use the global reusable rendering script located at `~/.gemini/skills/write-verified-advisory/scripts/render_mermaid.py` to compile and save the PNG image automatically:
  ```bash
  python3 ~/.gemini/skills/write-verified-advisory/scripts/render_mermaid.py <input_file.mmd> [output_file.png]
  ```
- **Kroki Compression Algorithm in Python:** The script deflates the input string (zlib) and base64-encodes the result:
  ```python
  import zlib
  import base64
  compressed = zlib.compress(mmd_text.encode('utf-8'), 9)
  encoded = base64.urlsafe_b64encode(compressed).decode('utf-8').replace('=', '')
  url = f"https://kroki.io/mermaid/png/{encoded}"
  ```
- **Deliverable Inclusion:** The generated `.png` diagram must be placed in the workspace, referenced in all documents, and uploaded directly to the customer's Google Drive folder alongside the technical advisory documents.

### 12. Frequent Commits Mandate
The agent MUST commit progress frequently to git. After each write, targeted correction, or edit to any markdown advisory document (`readme.md`, `message_draft.md`), you must commit the changes immediately to ensure a granular, trackable git history.

### 13. Verification Log Mandate ("What Was Tried")
The agent MUST include a dedicated section at the end of the internal Master Advisory (`readme.md`) titled "What Was Tried" or "Verification Log". This section must chronologically document every live test, API command, configuration execution, or script run in the active session to verify the described behavior. For each attempt, include:
*   The exact command/payload executed.
*   The target environment (e.g. active GCP project ID, active user/service account credentials, internal Google organization context, or sandbox environments).
*   The exact local filesystem path (working directory/CWD) where commands were run.
*   Detailed timestamps (date and local/UTC time) of the execution.
*   The verbatim response status, output, or error observed.
*   The conclusion drawn from the result (success, failure, or unexpected behavior).

**Rigorous Transition Verification Rule:**
To prove a script or test works and successfully affects a change, your verification log MUST show a clear transition from state X to state Y. Simply checking a final state without showing the starting state or showing no transition (e.g. state was already Y before the test run) is invalid. You MUST show GET/read command outputs before and after the mutation for each operation in question. For example, for an app key product update tool:
*   **Step 1 (Pre-state GET):** Retrieve and show starting state of key: `[Product A]`.
*   **Step 2 (Mutation POST):** Execute add/append operation and show POST response.
*   **Step 3 (Interim GET):** Retrieve and show key is now `[Product A, Product B]`.
*   **Step 4 (Mutation DELETE):** Execute delete/remove operation and show DELETE response.
*   **Step 5 (Post-state GET):** Retrieve and show final state of key: `[Product B]`.
This guarantees physical proof of state change and verifies that every single distinct mutation operation actually executed successfully.





### 14. Multi-Turn Communication & Historical Record Mandate
For issues involving multiple communication iterations or ongoing client feedback:
1.  **Preserve Original Message:** Keep the first sent message (`message_draft.md`) completely untouched as a historical record. Save all subsequent replies, follow-ups, or corrections in sequentially numbered draft files: `reply_message_2_draft.md`, `reply_message_3_draft.md`, etc.
2.  **Conversation History Timeline:** Maintain a chronological log in `readme.md` detailing every client response/inquiry, corresponding internal analysis dates, and target verification outcomes.
3.  **Omission & Alignment Review:** Maintain a private "Communication Review & Omission Analysis" section in `readme.md` to analyze whether previous outbound emails contained clear technical mistakes (such as suggesting an append-only operation can perform a replacement update) or were merely ambiguous. Use these findings to determine how to frame the next reply. To maintain consulting authority, do **not** apologize or explicitly state you made a mistake to the customer in subsequent draft emails unless there is a critical system safety impact; instead, simply confirm the client's correct observation and present the complete, verified technical sequence directly as a next step.
4.  **Demonstrate Sandbox Credibility:** When responding to a customer's correction or alternative findings to show we aren't just echoing their feedback, include raw request/response logs from our sandbox testing directly in the message draft. To verify credibility while respecting privacy/confidentiality, show real execution metadata such as partially-masked project IDs (e.g., `apigee-demo-11***` or `apigee-***-1125`), target sandbox organizations (e.g., `ca-bank-drz-***`), and exact timestamps of the test run. ALWAYS format all timestamps in the customer's local timezone (e.g., Eastern Time / ET for Toronto-based clients) rather than UTC/GMT to keep the context natural and customer-centric. If the customer's local timezone is not known, ask the user for clarification or, in the worst case, assume US Eastern Time (spelled out explicitly as ET or EST/EDT).





## Workflow

1.  **Drafting:** Outline the advisory based on session research.
2.  **Verification & Link Testing:** Execute the verification hierarchy for every assertion. Actively curl or browse every URL to verify HTTP 200 status.
3.  **Synthesis:** Construct **Artifact A** (Master .md file) and **Artifact B** (`message_draft.md`) with polished citations. Apply email styling to Artifact B.
4.  **Audit:** Construct **Artifact C** (chat response) with the full verification audit trail, including the URL validation proof block.
5.  **Review:** After generating the reports, the agent MUST review the output and explicitly call out any unsourced claims.
6.  **Delivery & Format Choice:** Provide local file paths for A and B. Offer Google Doc/Drive upload, local `.docx` generation via `textutil`, or Gmail Draft options.
7.  **Post-Send Sync:** If requested, check the sent email, commit existing state, and make targeted updates to the local files.
8.  **Consolidation & Cleanup (Git-Driven):** When finalizing the issue folder and preparing the draft to be shared:
    *   **Context Separation:** Ensure all customer-facing content is mapped to `message_draft.md`. All internal context, technical analysis, and metadata inappropriate for the customer must be moved to `readme.md`.
    *   **Pre-Consolidation Commit:** Save all additional context not already saved to `readme.md` and commit all files in the directory.
    *   **Content Migration:** Regenerate and consolidate all details from other intermediate markdown files (e.g., `developer_app_keys_migration_guide.md`) into either `message_draft.md` or `readme.md`. Commit immediately after this consolidation.
    *   **Iterative Diff & Validation:** Diff the current state against the pre-consolidation commits to ensure no technical details, context, or critical steps were lost or missed. Repeat the diff and review cycles, committing after each targeted correction/write.
    *   **File Deletion:** Once validation is complete and all session information resides in either `readme.md` or `message_draft.md`, delete any other intermediary `.md` files (such as `developer_app_keys_migration_guide.md`) and commit the final clean directory structure.

