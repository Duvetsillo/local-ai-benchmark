# Industry-Vertical UX Design Patterns

Apply these domain-specific UX patterns when designing for regulated, specialized, or complex industry contexts. Each vertical carries unique constraints around compliance, user expertise, workflow cadence, and risk tolerance. Treat these patterns as baseline requirements — not optional enhancements — when operating within the given domain.

---

## Healthcare UX

Design healthcare interfaces with the understanding that errors cost lives, workflows are constantly interrupted, and regulatory compliance is non-negotiable.

### HIPAA Considerations for UI Design

Follow the principle of minimum necessary display. Show only the PHI (Protected Health Information) a user needs for their current task. Never pre-populate screens with full patient records when a summary suffices.

| HIPAA UI Requirement | Implementation Guidance |
|---|---|
| Minimum necessary display | Default to summary views; require deliberate action to expand full records. Mask SSN, DOB, and MRN in lists — show last four digits only. |
| Auto-lockout | Enforce session timeout at 15 minutes of inactivity for workstations, 5 minutes for mobile. Display a 60-second warning before lockout. Preserve unsaved work in a secure draft state. |
| Audit trails | Log every PHI view, edit, print, and export event with user ID, timestamp, patient ID, and action type. Surface audit history to compliance officers through a dedicated log viewer. |
| PHI in notifications | Never include patient names, diagnoses, or identifiers in push notifications, email subjects, or lock-screen previews. Use generic prompts such as "New result available — tap to view." |
| Screen capture prevention | On mobile, disable screenshot capability on PHI-displaying screens. On desktop, display a visible watermark with the logged-in user's ID overlaid on printable views. |
| Break-the-glass access | Provide emergency override for records outside a provider's assigned patients. Require documented reason, send immediate alert to compliance, and flag the access in the audit log. |

### Provider-Facing Interfaces

Design clinical dashboards to answer the question "What do I need to act on right now?" within two seconds of screen load.

- **Patient list / worklist:** Sort by acuity or time-sensitivity by default. Display patient name, room/bed, chief complaint, and pending action count. Use color-coded flags — red for critical, yellow for abnormal, gray for routine.
- **Chart review:** Organize by problem-oriented structure. Provide tabs for Active Problems, Medications, Allergies, Labs, Notes, and Imaging. Pin the allergy banner to the top of every screen when an allergy exists.
- **Order entry (CPOE):** Support type-ahead search with autocomplete. Display frequency, route, and default dose inline. Surface relevant clinical decision support alerts before order signing — not after.
- **Alert management:** Classify alerts into tiers. Tier 1 (hard stop): requires acknowledgment before proceeding. Tier 2 (interruptive): displays modal but allows override with documented reason. Tier 3 (passive): displays inline banner. Reduce alert fatigue by suppressing duplicate alerts within the same session.

### Patient-Facing Interfaces

Design patient portals for a reading level of grade 6–8. Avoid medical jargon; provide plain-language explanations alongside clinical terms.

- **Appointment booking:** Show available slots in calendar and list views. Display provider photo, specialty, and estimated wait time. Allow filtering by location, insurance accepted, and language spoken.
- **Telehealth:** Test connection (camera, microphone, bandwidth) before joining. Provide a virtual waiting room with estimated wait. Display a persistent "End Visit" button. Support screen sharing for reviewing results together.
- **Medication management:** Show medication name (generic and brand), purpose in plain language, dosage schedule with visual timeline, and refill status. Provide tap-to-call pharmacy and one-tap refill request.
- **Health data visualization:** Display lab results with reference ranges using horizontal bar charts. Mark abnormal values in red/yellow. Show trend lines over the past 12 months. Include a plain-language interpretation such as "Your cholesterol is in the normal range."

### Diagnostic and Medication Safety UI

Present lab results in a structured table with the following columns:

| Column | Content |
|---|---|
| Test name | Full name with common abbreviation |
| Result value | Numeric value with unit |
| Reference range | Low–high range for the patient's demographics |
| Flag | H (high), L (low), C (critical) with color coding |
| Trend | Sparkline or arrow indicating direction from prior result |
| Date collected | Timestamp of specimen collection |

For critical value alerts, use a full-screen interstitial requiring acknowledgment. Log the time from result availability to provider acknowledgment.

Implement medication safety as follows:

- **Drug interaction warnings:** Display severity (contraindicated, major, moderate, minor), the interacting pair, and the clinical consequence in one sentence. Provide a "Learn more" link to the clinical monograph.
- **Look-alike / sound-alike (LASA) differentiation:** Use tall-man lettering (e.g., DOBUTamine vs DOPamine). Display both generic and brand names. Show the indication next to the drug name in selection lists.
- **Dose calculation aids:** Auto-calculate weight-based dosing. Display the formula, patient weight, and calculated dose. Require manual confirmation if the calculated dose deviates more than 20% from standard ranges.

### Clinical Workflow Optimization

Reduce clicks to critical actions. Target three clicks or fewer from login to the most common task (viewing results, placing an order, documenting a note).

- **Interruption recovery:** Save in-progress work automatically every 10 seconds. When a provider switches patients, preserve the prior context in a "return to" queue displayed in the navigation bar. Restore exact scroll position and cursor location on return.
- **Context preservation:** Display the current patient's name, photo (if available), DOB, and allergy status in a persistent header across all screens. Use color-coded banners for isolation precautions or fall risk.

### Accessibility in Healthcare

Design for an aging patient population with declining vision, motor control, and cognitive capacity.

- Set minimum touch targets to 48x48dp for patient-facing mobile interfaces.
- Support font scaling up to 200% without layout breakage.
- Provide high-contrast mode as a persistent toggle, not buried in settings.
- Offer multilingual support with right-to-left layout for Arabic, Hebrew, and similar scripts. Translate clinical terms, not just UI chrome.
- For cognitive accessibility, use step-by-step wizards instead of complex forms. Limit choices per screen to five or fewer.

---

## Financial Services UX

Design financial interfaces around the twin imperatives of trust and clarity. Users must feel secure and must understand the financial implications of every action.

### Trust and Security Communication

| Trust Signal | Implementation |
|---|---|
| Security indicators | Display a persistent security badge or lock icon on authenticated pages. Show "Bank-level 256-bit encryption" in the footer of sensitive pages. |
| Certification badges | Display FDIC, SIPC, SOC 2, or PCI-DSS badges near account balances and transaction forms. Link each badge to a verification page. |
| Transparent fee structure | Show all fees in a single, scrollable table before account opening. Display fee impact inline during transactions (e.g., "Wire transfer fee: $25 will be deducted from your balance"). |
| Login security | Show the last login date, time, and device on the post-login dashboard. Offer "Not you? Secure your account" as a prominent link. |
| Fraud alerts | Use push notification + in-app banner + SMS for suspected fraud. Provide one-tap "This was me" / "This wasn't me" actions. Freeze the card immediately on "wasn't me" and provide next steps. |

### Transaction Confirmation and Verification

For high-value transactions (define threshold per institution, typically above $1,000):

1. Display a review screen with sender, recipient, amount, fee, and estimated delivery.
2. Require secondary authentication (biometric or one-time code).
3. Show a countdown timer ("You have 30 seconds to cancel") on the confirmation screen.
4. Deliver a receipt via in-app notification, email, and downloadable PDF.

Track transaction status with a horizontal stepper: Initiated > Processing > Completed (or Failed). Show estimated completion time at each step.

### Portfolio Visualization and Risk Display

- **Asset allocation:** Use a donut chart with labeled segments for each asset class. Display percentage and dollar value on hover/tap. Provide a table view toggle for accessibility.
- **Performance over time:** Default to a line chart showing portfolio value over 1Y. Offer selectors for 1D, 1W, 1M, 3M, 6M, 1Y, 5Y, ALL. Overlay benchmark comparison (e.g., S&P 500) as a dashed line. Display percentage gain/loss and dollar gain/loss simultaneously.
- **Risk-return visualization:** Plot investments on a scatter chart with risk (standard deviation) on the X-axis and return on the Y-axis. Label efficient frontier. Provide tooltips with fund name, expense ratio, and Sharpe ratio.
- **Risk scores:** Display as a 1–10 scale with color gradient (green to red). Accompany with a one-sentence plain-language explanation: "A score of 7 means this investment has moderate-to-high volatility."

### Account Overview and Mobile Banking

Structure the account overview with a clear visual hierarchy:

1. **Total net worth** — top of screen, largest typography.
2. **Account cards** — horizontally scrollable cards for each account (checking, savings, investment, credit). Show name, last four digits, and current balance.
3. **Recent activity** — last five transactions with merchant name, category icon, amount, and date. "See all" link to full history.
4. **Quick actions** — prominent buttons for Transfer, Pay, Deposit. Place within thumb reach on mobile.

For mobile banking, implement biometric authentication (Face ID, fingerprint) as the default login. Support quick balance check from the lock screen via widget without full authentication. Send push notifications for all transactions over a user-configurable threshold. Provide card controls (freeze/unfreeze, set spending limits, toggle international transactions) accessible within two taps.

### Regulatory Compliance UX

Design KYC (Know Your Customer) flows as a multi-step wizard with progress indicator. Request documents in order of likelihood the user has them available (government ID, then proof of address, then selfie verification). Show estimated time to complete ("About 5 minutes"). Allow saving progress and resuming later.

Present terms and disclosures in a scrollable container with section headings. Highlight material changes in bold. Require explicit checkbox consent for each regulatory disclosure rather than a single blanket acceptance.

---

## E-Commerce UX

Optimize every interaction for conversion while maintaining transparency and trust.

### Product Discovery

- **Search:** Implement predictive type-ahead with product thumbnails in suggestions. Support natural language queries ("red running shoes under $100"). Show recent searches and trending searches on focus.
- **Filters:** Display filters in a left sidebar on desktop, full-screen overlay on mobile. Show the number of results updating in real time as filters are applied. Support multi-select within filter categories. Provide "Clear all" and per-filter "X" removal.
- **Category navigation:** Use a mega-menu on desktop with subcategory groupings and featured product images. On mobile, use a drill-down hierarchy with back navigation. Show breadcrumbs on product pages.
- **Visual search:** Allow image upload to find visually similar products. Display results in a grid with similarity score or "Best match" label.

### Product Comparison, Reviews, and Recommendations

Build comparison tables with sticky headers and a maximum of four products side by side. Highlight differentiating features with bold text or background color. Allow adding/removing products from the comparison without navigating away.

| Review Element | Specification |
|---|---|
| Rating distribution | Horizontal bar chart showing count per star level (5 down to 1) |
| Verified purchase badge | Green checkmark + "Verified Purchase" label |
| Helpfulness voting | "Was this review helpful? Yes (count) / No (count)" |
| Photo/video reviews | Thumbnail gallery above text reviews; tap to enlarge |
| AI-summarized reviews | Display a three-sentence summary of positive and negative themes at the top of the review section. Label clearly: "AI-generated summary based on X reviews." |

For recommendation systems, always explain the reasoning: "Recommended because you viewed [Product]" or "Frequently bought with [Product]." Allow users to dismiss recommendations and provide feedback ("Not interested") to refine the algorithm.

### Shopping Cart and Checkout Optimization

Maintain a persistent cart across sessions and devices. Show a mini-cart dropdown on the cart icon hover/click with item thumbnails, quantities, and subtotal.

Checkout flow — target five steps or fewer:

1. **Cart review** — quantity adjustment, remove item, "Save for later," coupon code entry, free shipping progress bar ("Add $12.50 more for free shipping").
2. **Account** — guest checkout prominently offered alongside sign-in. Pre-fill fields for returning users.
3. **Shipping** — address autocomplete via Google Places or similar. Show delivery date estimates per shipping option.
4. **Payment** — express options (Apple Pay, Google Pay, PayPal) above the fold. Credit card form with card type auto-detection, inline validation, and formatting.
5. **Confirmation** — order number, summary, estimated delivery, tracking link (when available), "Continue shopping" button.

Handle errors gracefully: highlight the specific field in red, display the error message directly below the field, and preserve all other entered data.

### Post-Purchase Experience

Send an order confirmation email within 60 seconds. Provide a tracking page with a map view of package location when supported. Send proactive notifications at shipped, out-for-delivery, and delivered stages. Design the return initiation flow as a self-service wizard: select item, select reason, choose return method (drop-off or pickup), generate label. Request a review 7–14 days after confirmed delivery — not before.

---

## SaaS / B2B UX

Design enterprise software to minimize time-to-value and support complex organizational hierarchies.

### Complex Onboarding

Structure onboarding as a checklist that the user can complete in any order, not a rigid linear wizard. Display the checklist persistently in a sidebar or banner until all steps are complete. Include:

- **Account setup** (profile, company info, branding)
- **Integration connection** (connect primary data source or tool)
- **First core action** (create first project/campaign/report)
- **Team invitation** (invite at least one collaborator)
- **Sample data** — pre-populate the workspace with realistic sample data so users can explore features immediately. Provide a "Clear sample data" action when ready.

Track and optimize time-to-first-value (TTFV). Measure the elapsed time from signup to the first meaningful action (e.g., generating a report, sending a campaign). Target TTFV under 10 minutes.

### Feature Discovery and In-App Guidance

- **Contextual tooltips:** Trigger on first visit to a new section. Point to the specific UI element. Dismiss on click or after five seconds. Never show more than one tooltip at a time.
- **What's new:** Use a changelog drawer accessible from the navigation bar. Badge the icon with a dot for unread updates. Group entries by date with title, description, and screenshot/GIF.
- **Feature flags and gradual rollout:** When rolling out a new feature to a subset of users, display a "Beta" badge. Provide an in-app feedback channel specific to the beta feature.

### Collaboration Patterns

| Pattern | Design Specification |
|---|---|
| Shared workspaces | Display workspace name in the top-left. Show member avatars in the header. Provide a workspace switcher dropdown. |
| Commenting / annotation | Support inline comments anchored to specific elements (cells, paragraphs, pixels). Display comment threads in a right-side panel. Resolve and reopen comments. |
| @mentions | Trigger user picker on "@" keystroke. Notify mentioned users via in-app notification and email. Highlight mentions in the activity feed. |
| Activity feeds | Show chronological feed of workspace events. Filter by event type (edits, comments, status changes). Display actor avatar, action description, target object, and timestamp. |
| Real-time presence | Show colored avatar dots (green = active, yellow = idle, gray = offline) in the workspace member list and on shared documents. |

### Admin vs. End-User Experiences

Separate admin and end-user interfaces through role-based UI rendering, not separate applications. Use a single codebase with conditional component display.

- **Admin panel:** Provide user management (invite, deactivate, role assignment), billing management, organization settings, SSO/SAML configuration, and audit logs. Display audit logs in a searchable, filterable table with columns for user, action, target, IP address, and timestamp.
- **Permission configuration:** Use a matrix view with roles as columns and permissions as rows. Support custom role creation. Preview the end-user experience for any role with an "Impersonate" function available only to super-admins.

### Upgrade, Expansion, and Integration UX

Design feature gating to show the locked feature's UI with a frosted overlay and "Upgrade to unlock" call-to-action. Never hide gated features entirely — users need to understand the value before paying.

Present plan comparison in a table with the current plan highlighted. List features in rows grouped by category. Use checkmarks and "x" marks for boolean features, and specific values (e.g., "Up to 10 users") for quantitative limits.

For integrations, design the OAuth flow to open in a popup window (not a redirect) to preserve context. Show connection status (connected, disconnected, error) on each integration card. Provide a test button for webhook configurations that sends a sample payload and displays the response.

---

## Education UX

Design learning platforms to sustain engagement, support diverse learning modalities, and serve multiple user roles within the same system.

### Course Navigation and Content Structure

- **Syllabus view:** Display the full course outline with module names, lesson titles, estimated duration, and due dates. Indicate completed, in-progress, and locked items with distinct icons and colors.
- **Module hierarchy:** Use a collapsible tree structure in a left sidebar. Highlight the current lesson. Display next/previous navigation at the bottom of each lesson.
- **Progress tracking:** Show a progress bar at the course level and the module level. Display percentage complete and estimated time remaining.
- **Resume functionality:** Persist the user's last position (page, scroll offset, video timestamp). Display a "Continue where you left off" card on the dashboard with course thumbnail, title, and progress.

### Assignment and Assessment UX

Design file upload to accept drag-and-drop and click-to-browse. Show upload progress, file name, size, and a preview thumbnail. Allow multiple file submission. Display due date, time remaining, and late penalty policy prominently.

| Assessment Element | Design Specification |
|---|---|
| Quiz interface | One question per screen with navigation sidebar showing question status (answered, unanswered, flagged). Display time remaining in a fixed header for timed exams. |
| Question navigation | Number grid allowing jump-to-question. Color-code: blue (current), green (answered), white (unanswered), orange (flagged for review). |
| Answer review | After submission, show correct/incorrect indicators per question. Display the correct answer and an explanation. Link to the relevant course material. |
| Grade display | Show numeric score, letter grade, and class statistics (mean, median) where permitted. Display grade trend over assignments in a line chart. |
| Draft saving | Auto-save every 30 seconds. Display "Draft saved at [time]" in the footer. Allow explicit "Save draft" action. Warn before navigating away from unsaved changes. |

### Multi-Role Interfaces

Build a role switcher for users with multiple roles (e.g., a teaching assistant who is also a student in another course). Display the active role in the navigation header.

- **Student view:** Focus on upcoming deadlines, grades, and course content. Minimize administrative controls.
- **Instructor view:** Prioritize grading queue, student submissions, class analytics, and content editing. Provide a "View as student" preview toggle.
- **Admin view:** Surface enrollment management, course creation, system analytics, and compliance reporting.

### Discussion and Collaboration

Implement threaded discussions with reply, quote, and @mention support. Display posts in chronological order with newest-first option. Allow instructor posts to be pinned. Support rich text, code blocks, image embedding, and LaTeX rendering for STEM courses. For peer review, assign reviewers automatically and anonymize submissions during the review period. Display peer feedback alongside instructor feedback.

### Accessibility in Education

Meet WCAG 2.1 AA as a minimum; target WCAG 2.1 AAA for publicly funded institutions. Provide captions and transcripts for all video and audio content. Offer alternative assessment formats (extended time, text-to-speech compatibility, alternative response formats). Ensure all interactive elements are fully keyboard navigable. Test with screen readers (NVDA, JAWS, VoiceOver) for every release.

---

## Real-Time Collaboration Patterns

Apply these patterns across any application that supports simultaneous multi-user interaction.

### Presence Indicators

Display presence status using universally understood signals:

| Status | Visual Indicator | Trigger |
|---|---|---|
| Online / Active | Solid green dot on avatar | User has interacted within the last 5 minutes |
| Idle / Away | Yellow or hollow dot on avatar | No interaction for 5–15 minutes |
| Offline | Gray dot or no indicator | No interaction for 15+ minutes or explicitly set |
| Do Not Disturb | Red dot with minus sign | Manually set by user; suppresses notifications |
| Currently viewing | User avatar displayed on the element (cell, page, section) | User's viewport includes the element |

For cursor sharing, display each collaborator's cursor in a distinct color with their name label. Fade the label after two seconds of inactivity to reduce visual clutter. Cap visible cursors at five; show a "+N others" indicator for additional collaborators.

### Conflict Resolution and Concurrent Editing

Choose a conflict resolution strategy based on the data model:

- **Operational Transformation (OT):** Use for text documents where character-level merging is required. Display all edits in real time with no visible merge artifacts.
- **CRDTs (Conflict-free Replicated Data Types):** Use for distributed systems where offline editing and eventual consistency are required. Particularly suited for list-based and map-based data structures.
- **Last-write-wins (LWW):** Use only for discrete fields (e.g., status dropdowns, single-value cells) where merging is not meaningful. Display a notification when another user overwrites a value: "[User] changed [field] from [old] to [new]."
- **Manual merge:** Offer a diff view showing both versions side by side when automatic resolution is not possible. Let the user accept left, accept right, or edit manually.

For concurrent editing of rich documents, highlight each user's active selection in their assigned color. Display an attribution tag ("Edited by [User] just now") on recently changed blocks. Fade the attribution after 30 seconds.

### Activity Feeds and Version History

Design activity feeds with the following structure per entry:

```
[Avatar] [User Name] [action verb] [target object] — [relative timestamp]
Example: JL  Jane Lee commented on Q3 Budget — 5 min ago
```

Provide filters for event type and involved user. Support real-time streaming of new events at the top of the feed. Show an unread count badge on the feed icon. Offer a toggle between real-time and digest modes (hourly or daily summary).

### Version History

Present version history as a vertical timeline with the most recent version at the top. For each version, display:

- Timestamp and author
- Summary of changes (auto-generated: "3 paragraphs added, 1 image removed")
- A "Preview" action that opens a read-only view of that version
- A "Restore" action with a confirmation dialog ("Restoring will create a new version with the contents of [date]. Current content will be preserved in history.")

Implement diff visualization with inline and side-by-side modes. Use green highlighting for additions, red with strikethrough for deletions, and yellow for modifications.

### Notification Design for Collaboration

Tier notifications by urgency and user preference:

| Notification Type | Default Delivery | User Override Options |
|---|---|---|
| @mention | In-app banner + push + email | Mute specific channels |
| Direct assignment | In-app banner + push + email | None (always delivered) |
| Change to watched item | In-app feed only | Upgrade to push; unwatch |
| Comment on own content | In-app banner + push | Downgrade to feed only; mute thread |
| Status change | In-app feed only | Upgrade to push for specific statuses |
| Digest summary | Email (daily) | Change frequency: real-time, hourly, daily, weekly |

Batch notifications intelligently. If five comments are posted on the same thread within two minutes, deliver one notification summarizing: "[User] and 4 others commented on [Thread]." Never deliver more than one push notification per thread per five-minute window unless the user is directly mentioned.

---

## Cross-Vertical Design Principles

Apply these principles regardless of industry:

1. **Respect domain expertise.** Design for expert users who use the system eight or more hours per day. Optimize for efficiency over learnability after the onboarding period.
2. **Fail safely.** In high-stakes domains (healthcare, finance), design destructive actions to require explicit confirmation, support undo, and never auto-execute irreversible operations.
3. **Comply by default.** Build regulatory requirements (HIPAA, PCI-DSS, FERPA, GDPR) into default UI behavior rather than relying on user configuration. Compliance should be the path of least resistance.
4. **Support task continuity.** Every vertical involves interruptions. Auto-save state, preserve context, and provide clear "return to" navigation for in-progress workflows.
5. **Layer information density.** Default to summary views with progressive disclosure to detailed views. Let the user control density through explicit view toggles (compact, comfortable, detailed) rather than making a single density choice for them.
6. **Design for the full lifecycle.** Map the complete user journey — not just the core transaction. Account for onboarding, daily use, error recovery, edge cases, account closure, and data export.
