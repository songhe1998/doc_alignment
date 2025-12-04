# JSON Escape Sequence Fix for Document Highlighting

## Date: December 3, 2025

## Problem Discovered

**Doc1 (nda_1.pdf) had NO HIGHLIGHTS while Doc2 (nda_2.pdf) worked fine.**

### Root Cause Analysis

Through deep debugging, we traced the issue to a **JSON parsing failure**:

```
❌ Error extracting topics from Document 1: Invalid \escape: line 33 column 49 (char 2601)
✅ Found 0 topics in Doc1
```

**Why it failed:**

The PDF (nda_1.pdf) has corrupted/mangled text from OCR or conversion:
```
"³Confidential Information´ PeaQV aQ\ data or information..."
                                   ^^^
                                   This backslash creates an invalid JSON escape
```

When OpenAI was asked to extract EXACT quotes, it faithfully copied the corrupted text including the backslash. But `aQ\` is not a valid JSON escape sequence (`\d` is invalid), causing `json.loads()` to fail.

**Result:** Zero topics extracted from Doc1 → Zero doc1_sections → No highlights for nda_1.pdf!

---

## The Fix

Added regex to remove invalid escape sequences before JSON parsing:

```python
# In nda_direct_alignment.py, line ~88
import re
# Replace backslash followed by a character that's NOT a valid JSON escape
# Valid JSON escapes: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
json_str = re.sub(r'\\([^"\\/bfnrtu])', r'\1', json_str)

topics_data = json.loads(json_str)
```

**How it works:**
- Finds patterns like `\d`, `\a`, `\q` (invalid escapes)
- Removes the backslash, keeping the character
- `aQ\ data` → `aQ data`
- Now JSON parses successfully!

---

## Results

### Before Fix:
```
Doc1 topics extracted: 0 ❌
Doc1 sections in alignments: 0/9 (EMPTY!) ❌
Doc1 highlights: NONE ❌
```

### After Fix:
```
Doc1 topics extracted: 6 ✅
Doc1 sections in alignments: 6/11 ✅
Doc1 sections exact match: 6/11 TRUE ✅
```

**Now both documents have working highlights!**

---

## Why Some Alignments Still Have Empty Sections

After the fix, we see:
- `doc1_sections` empty: 5/11 alignments
- `doc2_sections` empty: 2/11 alignments

**This is expected!** These are topics that exist in only ONE document:
- Topics like "Governing Law" only in Doc2 → doc1_sections is empty
- Topics like "Florida Sunshine Law" only in Doc1 → doc2_sections is empty

The alignment system correctly identifies topics that don't have a match in the other document. Empty sections for one side simply means that topic isn't covered in that document.

---

## Technical Details

### Valid JSON Escape Sequences:
- `\"` - quotation mark
- `\\` - backslash
- `\/` - forward slash
- `\b` - backspace
- `\f` - form feed
- `\n` - newline
- `\r` - carriage return
- `\t` - tab
- `\uXXXX` - unicode character

### Invalid (now fixed):
- `\d`, `\a`, `\q`, `\Q`, `\P`, `\V`, `\W`, etc.

These appear in corrupted PDF text from:
- OCR errors
- Font substitution issues
- PDF-to-text conversion artifacts
- Character encoding problems

---

## Files Modified

### `/nda_direct_alignment.py`
- Lines ~85-88: Added regex to clean invalid JSON escapes before parsing

---

## Testing

To verify the fix works:

1. Start server: `PORT=5090 python app.py`
2. Open: `http://127.0.0.1:5090`
3. Upload `nda_1.pdf` and `nda_2.pdf`
4. Select **Topic-Based (Direct)**
5. Click **Align Documents**
6. **Both documents should now show highlights!**

---

## Status: ✅ FIXED

The JSON parsing error that caused Doc1 to have no topics (and therefore no highlights) has been resolved. Both documents now extract topics correctly and display highlights.

