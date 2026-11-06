# Simple meanings for APPSC Reader's dictionary

You write the meaning of each word in your packet for APPSC aspirants in Andhra Pradesh who studied in Telugu
medium. They read the notes in English and stop at words like "accord", "statutory" or "erosion".

Input: `data/words/in/<n>.md`. Each line is `word | a line of the notes that uses it`.
Output: `data/words/out/<n>.md`. Write one line per input word, in the same order:

    word | meaning

## Rules for a meaning

- Write **simple Indian English**: short, everyday words that a class 8 student in India knows. Use Indian
  examples and units where they help (₹, lakh, crore, Lok Sabha, monsoon, panchayat).
- Give the sense the notes use. The example line shows that sense. For "pillar | Three pillars: minimum
  capital ..." write the "main part" sense, not the stone column.
- Keep it to **at most 15 words**. Do not repeat the word itself and do not start with "It means".
- For a verb, start with "to": `ratify | to give formal approval to an agreement or law`.
- Use no Markdown and no `|` inside the meaning.
- For a subject term (polity, economy, science, history), give the exam meaning in plain words:
  `deficit | the amount by which spending is more than income`.
- When the word is not English but is used in the notes (a Sanskrit or Telugu term), still explain it simply.
- When a word is so basic that no aspirant needs it, or you cannot tell what it means here, write `SKIP`:
  `angle | SKIP`.

## Examples

    crore | one hundred lakh, that is 1,00,00,000 (10 million)
    statutory | made by or required by a law passed by Parliament or a State legislature
    erosion | slow wearing away of soil or rock by water, wind or ice
    inscription | words cut into stone or metal, like Ashoka's edicts
    subsidy | money the government pays to keep a price low for people
    merge | to join two or more things into one

## When you finish

Run `python3 tools/words_check.py <n>` for each of your packets. It lists missing words and meanings that break
the rules. Fix them, then run it again until it reports 0 problems.
