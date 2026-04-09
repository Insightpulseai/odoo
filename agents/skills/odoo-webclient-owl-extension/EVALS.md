# Evals — odoo-webclient-owl-extension

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | OWL component follows Odoo 18 patterns; patch() used correctly; assets in correct bundle |
| Completeness | JS, XML template, and SCSS all created; manifest updated; browser test performed |
| Safety | No global Composer/mail patches; no monkey-patching; no core JS modifications |
| Policy adherence | o_<module>_ class prefix; $o-* SCSS vars; no bare names; no ID selectors; no !important |
| Evidence quality | Browser console log captured; component rendering verified on test DB |
| Upgrade safety | Extensions use patch() API; no direct core file edits; no global side effects |
