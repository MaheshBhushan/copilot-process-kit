# Artwork and quality

Authority: process contract 1.0. Owner approves changes before republication.

Prepress checks PDF artwork in DraftArtwork on the same SharePoint site. Maximum size is 20971520 bytes (20 MB). Reject external URLs, parent traversal, unsupported extensions and missing files. Record manual preflight evidence in PreflightChecklistRef. Check agreed size, bleed, fonts, image quality, page count and customer proof against the actual job specification; this kit supplies no universal print tolerances. Ask Owner when a specification is missing.

Validate copies the PDF to ProductionFiles/ApprovalSnapshots/{ApprovalKey}.pdf before entering AwaitingApproval. This immutable snapshot is the exact approval subject. A later mutable draft cannot replace it. Release copies that approved snapshot without overwrite to ProductionFiles/{ApprovalKey}-approved.pdf and records ReleasedFilePath before ReadyForProduction.

Example: approval of PO-000123-r2 increments the order business Revision to 3. The released file remains PO-000123-r2-approved.pdf. Never rename it to match later business revisions. If artwork changes, request the supported correction cycle and a fresh approval. Escalate an Approved correction request to Owner; do not substitute artwork silently.

Production verifies ReleasedFilePath and assignment before StartProduction. Use the released file. Perform printing/finishing and manual QC against the agreed specification. Failed QC requires rework and repeat QC in InProduction. Complete only after QC passes; supply QCReference and WasteQuantity from zero through Quantity. Report inaccessible files and quality uncertainty to Owner; do not start from an unapproved draft.
