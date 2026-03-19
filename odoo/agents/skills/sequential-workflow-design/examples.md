# Sequential Workflow Design — Examples

## Example 1: Document Translation Pipeline

```
Step 1: Extract
  Input: Raw document (PDF/DOCX)
  Process: OCR/parse to plain text
  Output: Clean text string
  Gate: Text length > 0, encoding valid

Step 2: Translate
  Input: Clean text
  Process: LLM translation (source → target language)
  Output: Translated text
  Gate: Output language detection matches target

Step 3: Format
  Input: Translated text
  Process: Apply original document formatting
  Output: Formatted translated document
  Gate: Layout validation passes

Total steps: 3
Fallback: Return partial result with error annotation
```

## Example 2: Odoo Module Upgrade

```
Step 1: Port
  Input: 18.0 module source
  Process: oca-port origin/18.0 origin/19.0
  Output: Ported module code
  Gate: No merge conflicts

Step 2: Upgrade Code
  Input: Ported module
  Process: odoo-bin upgrade_code
  Output: Odoo 19 compatible code (tree→list, etc.)
  Gate: No syntax errors

Step 3: Test Install
  Input: Upgraded module
  Process: odoo-bin -d test_module -i module --stop-after-init
  Output: Installation result
  Gate: Exit code 0, no ERROR in logs

Total steps: 3
Fallback: Classify failure per testing.md matrix
```
