# Authenticated pilot setup

Class: designer reconstruction specification. No agent export or deployment exists. All tenant checks are Pending. Administrator needs approved Copilot Studio licensing/capacity, maker access, SharePoint administration and Teams pilot publication permissions. Replace environment placeholders only in the tenant's approved deployment record.

## Publish the four authoritative sources

Markdown support is not assumed. Use native SharePoint pages:

1. Owner reviews each of the four knowledge Markdown files against contracts/process.json. Record version 1.0, approver and approval date in the tenant evidence record.
2. In the pilot SharePoint site, select New > Page > Blank. Set the title to the Markdown heading. Add a Text web part. Paste the entire body as plain text, apply headings and lists with the editor, and retain every rule and example. Do not paste raw Markdown and assume it renders.
3. Use page names 01-order-lifecycle.aspx, 02-approval-and-exceptions.aspx, 03-artwork-and-quality.aspx and 04-roles-and-service-levels.aspx. Publish each page. Record its actual SitePages URL and document version in the source register below.
4. These pages are the published representations of ProcessKnowledge. Keep the approved Markdown masters in ProcessKnowledge for governance; restrict editing to Owner/admin. Apply the approved knowledge-reader permissions to each page. Do not grant extra site-wide rights to make retrieval work. If SitePages cannot enforce the intended readership, stop and resolve permissions before publication.
5. Open each published page as a pilot reader and compare all paragraphs against its Markdown master. Test a denied identity separately. Register every page URL individually; links inside pages are not crawled automatically. Do not register the whole operational site or Orders.

| Source | Published URL | Owner approval | Reader/denied proof | Retrieval |
|---|---|---|---|---|
| Order lifecycle | Pending | Pending | Pending | Pending |
| Approval and exceptions | Pending | Pending | Pending | Pending |
| Artwork and quality | Pending | Pending | Pending | Pending |
| Roles and service levels | Pending | Pending | Pending | Pending |

## Construct and test

1. Create Print Process Assistant in the approved development environment. Paste agent-instructions.md into instructions.
2. In Settings > Security > Authentication select Authenticate with Microsoft. Confirm effective Teams 1:1 authentication. Never choose No authentication.
3. Select Knowledge > Add knowledge > SharePoint in the Featured URL option. Enter only the four actual published page URLs and descriptions. Do not select uploaded-file copies as a substitute for SharePoint permission trimming.
4. Disable Web Search, agent Use general knowledge and topic-level Allow the AI to use its own general knowledge where present. Record the actual setting labels/value and evidence. If the tenant cannot restrict answers to approved sources, hold publication.
5. Inspect tools, topics and flows. Remove all write actions and message-sending tools. No operational lists, order lookup action or external sources belong in this agent.
6. Confirm each actual source is Ready, then test retrieval as the intended reader; Ready alone does not prove retrievability. Check Restricted SharePoint Search policy and sensitivity/encryption restrictions with admin. Test guest limitations; guests are outside this internal pilot.
7. Run every evaluation case using separate permitted and denied identities. Capture answer, citation, identity class, source version and timestamp in the CSV evidence fields. Critical security failures block publication.
8. Publish only after Owner signs the gates. Add Microsoft Teams channel for 1:1 use, share to the five internal pilot users and retest published behavior. Record actual publication/version identifiers and evidence as Pending until performed. Never use group or channel chats as proof of 1:1 authentication.
9. After any source, auth, permission or instruction change, republish as required, restart the chat and rerun critical cases. Preserve prior evidence.

Microsoft's [SharePoint grounding guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint) describes URL sources, caller access and authentication. Its [authentication guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/configuration-end-user-authentication) covers authentication settings. Reviewed 14 October 2026; tenant UI and effective controls require verification.
