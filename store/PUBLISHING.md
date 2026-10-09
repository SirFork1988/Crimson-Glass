# KDE Store publication status

Account: SirFork1988 (created by the owner).

Ten native component archives are built and verified. Their corresponding
editable sources are in components/. The global package source is in
global-theme/. Its local DRAFT archive is for validation only; final packaging
requires actual published companion IDs, as described in GLOBAL-THEME-NOTES.md.

The Store Files step requires accepting the publishing terms before file upload.
No native product has been submitted yet. Listings and archives are ready for
that acceptance and upload step. Publish the companions first, record their
IDs in published-ids.json, then build and upload the final global theme.

Package validation: all archive files/aliases verified against extracted source;
145,098 icon aliases resolve within the icon theme. Native global KPackage
install/show/remove passed in an isolated HOME. No live theme application was
performed during native package validation.

Local archives are in ../outputs/kde-store relative to the repository.
Source preparation does not alter the existing 1.1.0 GitHub release ZIP.
