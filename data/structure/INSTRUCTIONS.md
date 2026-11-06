# Structure each topic's full notes (APPSC Reader)

APPSC Reader shows only the full notes. Each topic has several full-notes pages, but they are listed in no clear
order, for example "Inscriptions" pages apart from each other. Arrange each topic's pages so that an aspirant
reads them in a sensible order, grouped under short headings.

Input: `data/structure/in/<n>.md`. Each topic looks like this:

    T 1:0 | <topic title>
    HINT <the topic's one-page summary headings, a hint at its natural parts>
    P1 <page title> :: <its first lines>
    P2 ...

Output: `data/structure/out/<n>.md`. For every topic, in the same order:

    T 1:0
    G <group heading> | 4,5,3
    G <group heading> | 10,11,12
    ...

## Rules

- Use **every page number exactly once**. Do not add, drop or merge pages.
- Order the groups the way a teacher would teach the topic: basics and definitions first, then the main parts
  (in time order for history), and exam traps or "Universal angles" or current relevance last.
- Within a group, list its pages in reading order.
- Make 2 to 7 groups. A topic with 3 pages or fewer may have just 1 group.
- A heading is plain English, 2 to 6 words, with no numbering and no Markdown, e.g. "Literary sources",
  "Inscriptions", "Coins and dating", "Exam angles". Use the HINT headings where they fit.
- Leave a blank line between topics.

When you finish, run `python3 tools/structure_check.py <n>` for each of your packets and fix every problem it
lists, until it reports 0 problems.
