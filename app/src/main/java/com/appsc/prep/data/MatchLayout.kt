package com.appsc.prep.data

/**
 * A "Match List I with List II" question split into its parts, so it can be shown as the printed paper's two-list
 * table: the lead-in, List I's title and items (a, b, c ...), List II's title and items (i, ii ... / 1, 2 ... / I, II ...),
 * and the closing line ("Select the correct answer ..."). Pure text work; null when the stem is not a two-list
 * matching question, so it keeps its plain text.
 *
 * Handles the layouts found in the apps' questions (checked against every matching MCQ of the Group 1 / Group 2 apps):
 * headings "List I / List-II / Column A / Group-B / Table A" with or without "(title)"; both headings on one line;
 * headings glued to an item line; items one per line, or pairs on one line ("A. Banawali – 1. R. S. Bisht"), or a
 * whole list on one line ("D. Banaras; 1. 1916 2. 1905 ..."); and lists with no headings at all when the options are
 * codes ("a-iii, b-i ..."). Item labels are followed in their own sequence (a, b, c ... / i, ii, iii ...), so names
 * with initials ("a. A. Vaidyanathan") are not mistaken for labels.
 */
data class MatchLayout(
    val intro: String,
    val leftTitle: String,
    val left: List<Pair<String, String>>,
    val rightTitle: String,
    val right: List<Pair<String, String>>,
    val outro: String,
) {
    companion object {
        private val ROM = listOf("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")
        private val SEQ = mapOf(
            "a" to "abcdefgh".map { it.toString() },
            "A" to "ABCDEFGH".map { it.toString() },
            "1" to (1..8).map { it.toString() },
            "i" to ROM,
            "I" to ROM.map { it.uppercase() },
        )
        private const val LAB = """([a-hA-H1-8]|i{1,3}|iv|vi{0,3}|I{1,3}|IV|VI{0,3})"""
        private val HEAD = Regex(
            """(?<![A-Za-z])(?:List|Column|Group|Set|Table)\s*[-–—]?\s*(II|I|A|B|1|2)(?![A-Za-z0-9])\s*(\(([^()]*(?:\([^()]*\)[^()]*)*)\))?\s*[:.]?""",
            RegexOption.IGNORE_CASE,
        )
        private val AFTER_HEAD = Regex(
            """^\s*(\n|$|\(?([a-hA-H1-8]|i{1,3}|iv|I{1,3}|IV)[.)]\s|\([a-hA-H1-8ivxIVX]+\)|(?:List|Column|Group|Set|Table)\b|[-/|]\s*(?:List|Column|Group|Set|Table)\b|[-–—]\s*\n)""",
            RegexOption.IGNORE_CASE,
        )
        private val OUTRO = Regex(
            """(?:^|\s)((?:Select|Choose|Mark|Pick|Find|Identify)\s+the\s+correct|(?:Select|Choose)\s+(?:the\s+)?(?:answer|code|correct)|Codes?\s*[:–—-]|Codes?\s*$|The\s+correct\s+(?:answer|code|match)|Which\s+of\s+the|How\s+many|Answer\s+(?:options|codes)|Options?\s*:)""",
            RegexOption.IGNORE_CASE,
        )
        private val ANY_LABEL = Regex("""(?:^|(?<=[\s;,]))\(?$LAB[.)](?=\s)""", RegexOption.MULTILINE)
        private val CODE = Regex("""\(?([A-Ha-h1-8]|[ivxIVX]{1,4})\)?\s*[-–→]\s*\(?([ivxIVX]{1,4}|[1-8]|[A-Ha-h])\)?""")
        private val MATCH_WORD = Regex("""\bmatch(?!es\b)|\bpairs\b""", RegexOption.IGNORE_CASE)

        private fun style(l: String) = when {
            l in ROM -> "i"
            l in SEQ["I"]!! -> "I"
            l[0].isDigit() -> "1"
            l[0].isLowerCase() -> "a"
            else -> "A"
        }

        /** the next item label [lab] from [start]: one at the start of a line wins (so "B. C. Rangarajan" does not
         *  yield a "C." item), else the first one inside a line ("D. Banaras; 1. 1916 2. 1905") */
        private fun labelAt(text: String, lab: String, start: Int): MatchResult? {
            val e = Regex.escape(lab)
            Regex("""(?:^|(?<=[;]\s))\(?$e[.)](?=\s|$)|(?:^|(?<=[;]\s))\($e\)""", RegexOption.MULTILINE).find(text, start)?.let { return it }
            return Regex("""(?:^|(?<=[\s;,]))\(?$e[.)](?=\s|$)|(?:^|(?<=[\s;,]))\($e\)""", RegexOption.MULTILINE).find(text, start)
        }

        private fun clean(t: String) = t.replace(Regex("""\s+"""), " ").trim()
            .replace(Regex("""\s*[-–—:;,]+$"""), "").trim()
            .replace(Regex("""^[-–—:;,]+\s*"""), "").trim()

        /** [options] lets a list without "List I / List II" headings count, when the options are matching codes. */
        fun parse(stem: String, options: List<String> = emptyList()): MatchLayout? {
            val heads = HEAD.findAll(stem).toList()
            for (h1 in heads) {
                if (h1.groupValues[1].uppercase() !in setOf("I", "A", "1")) continue
                // a real heading is followed by a newline, an item label or the other heading – not by "with ..."
                if (h1.range.last + 1 < stem.length && !AFTER_HEAD.containsMatchIn(stem.substring(h1.range.last + 1))) continue
                val h2 = heads.firstOrNull { it.range.first > h1.range.last && it.groupValues[1].uppercase() in setOf("II", "B", "2") } ?: continue
                runCatching { build(stem, h1, h2) }.getOrNull()?.let { return it }
            }
            if (MATCH_WORD.containsMatchIn(stem) && options.count { o -> CODE.findAll(o).count() >= 2 } >= 2) return runCatching { build(stem, null, null) }.getOrNull()
            return null
        }

        private data class Mark(val start: Int, val end: Int, val side: Char, val lab: String)

        private fun build(stem: String, h1: MatchResult?, h2: MatchResult?): MatchLayout? {
            var intro = if (h1 != null) stem.substring(0, h1.range.first).trim() else ""
            val fl = ANY_LABEL.find(stem, if (h1 != null) h1.range.last + 1 else 0) ?: return null
            val lstyle = style(fl.groupValues[1])
            val seqL = SEQ[lstyle]!!
            if (fl.groupValues[1] != seqL[0]) return null
            val lp = mutableListOf<Mark>()
            var pos = fl.range.first
            for (lab in seqL) {
                val m = labelAt(stem, lab, pos) ?: break
                lp += Mark(m.range.first, m.range.last + 1, 'L', lab)
                pos = m.range.last + 1
            }
            if (lp.size < 2) return null
            // where List II starts: after its heading when that heading follows the first List I item; otherwise prefer
            // a label at the start of a line, so names with initials ("a. A. Vaidyanathan") do not start List II
            val from = if (h2 != null && h2.range.first > lp[0].start) h2.range.last + 1 else lp[0].end
            val cands = ANY_LABEL.findAll(stem, from).filter { m ->
                val l = m.groupValues[1]; style(l) != lstyle && l == SEQ[style(l)]!![0]
            }.toList()
            val atLine = cands.filter { m ->
                val s = m.range.first
                s == 0 || stem[s - 1] == '\n' || stem.substring(maxOf(0, s - 2), s) in setOf("; ", ";\n")
            }
            val rs = atLine.firstOrNull() ?: cands.firstOrNull() ?: return null
            val seqR = SEQ[style(rs.groupValues[1])]!!
            val rp = mutableListOf<Mark>()
            pos = rs.range.first
            for (lab in seqR) {
                val m = labelAt(stem, lab, pos) ?: break
                rp += Mark(m.range.first, m.range.last + 1, 'R', lab)
                pos = m.range.last + 1
            }
            if (rp.size < 2) return null
            val lastR = rp.last().start
            val lpKept = lp.filter { it.start < lastR || it.start < rp[0].start }
            val marks = (lpKept + rp + listOfNotNull(h2?.let { Mark(it.range.first, it.range.last + 1, 'H', "") })).sortedBy { it.start }
            val left = mutableListOf<Pair<String, String>>()
            val right = mutableListOf<Pair<String, String>>()
            var tail = ""
            for ((k, mk) in marks.withIndex()) {
                if (mk.side == 'H') continue
                val next = if (k + 1 < marks.size) marks[k + 1].start else stem.length
                if (next < mk.end) return null
                var txt = stem.substring(mk.end, next)
                if (marks.drop(k + 1).all { it.side == 'H' }) {
                    OUTRO.find(txt)?.let { om ->
                        val at = om.groups[1]!!.range.first
                        tail = txt.substring(at) + stem.substring(next)
                        txt = txt.substring(0, at)
                    }
                }
                val t = clean(txt)
                if (t.isEmpty()) return null
                (if (mk.side == 'L') left else right) += mk.lab to t
            }
            if (left.size < 2 || right.size < 2) return null
            var lt = ""
            var rt = ""
            if (h1 == null) {
                // no headings: the lead-in's last short line is List I's title; a short last line inside the last
                // List I item ("Articles:", "State/UT") is List II's title
                intro = stem.substring(0, lp[0].start).trim()
                val il = intro.split('\n')
                if (il.size > 1 && il.last().length <= 60 && !il.last().trimEnd().endsWith("?")) {
                    lt = il.last().trim().trimEnd(':').trim(); intro = il.dropLast(1).joinToString("\n").trim()
                }
                val raw = if (lpKept.last().end <= rp[0].start) stem.substring(lpKept.last().end, rp[0].start).trimEnd().split('\n') else emptyList()
                if (raw.size > 1 && raw.last().trim().length <= 60) {
                    rt = raw.last().trim().trimEnd(':').trim()
                    val (lab, _) = left.last()
                    left[left.lastIndex] = lab to clean(raw.dropLast(1).joinToString("\n"))
                    if (left.last().second.isEmpty()) return null
                }
            }
            fun title(h: MatchResult?) = h?.groups?.get(3)?.value?.trim().orEmpty()
            fun fromIntro(n: String) = Regex("""(?:List|Column|Group|Set|Table)\s*[-–—]?\s*$n(?![A-Za-z0-9])\s*\(([^)]+)\)""", RegexOption.IGNORE_CASE)
                .find(intro)?.groupValues?.get(1)?.trim().orEmpty()
            return MatchLayout(
                intro = intro,
                leftTitle = title(h1).ifBlank { lt }.ifBlank { fromIntro("(?:I|A|1)") },
                left = left,
                rightTitle = title(h2).ifBlank { rt }.ifBlank { fromIntro("(?:II|B|2)") },
                right = right,
                outro = tail.replace(Regex("""[ \t]+"""), " ").trim(),
            )
        }

        private val PAIR = Regex("""\(?([A-Ha-h1-8]|[ivxIVX]{1,4})\)?\s*[-–→]\s*\(?([ivxIVX]{1,4}|[1-8]|[A-Ha-h])\)?""")
        private val REST = Regex("""[\s,;]*""")

        /** "a-iii, b-ii, c-i, d-iv" -> "(a) – (iii),  (b) – (ii), ..."; any other option text is returned unchanged. */
        fun option(text: String): String {
            val ms = PAIR.findAll(text).toList()
            if (ms.size < 2) return text
            var pos = 0
            for (m in ms) {
                if (!REST.matches(text.substring(pos, m.range.first))) return text
                pos = m.range.last + 1
            }
            if (!REST.matches(text.substring(pos))) return text
            return ms.joinToString(",  ") { "(${it.groupValues[1]}) – (${it.groupValues[2]})" }
        }
    }
}

/**
 * A "Consider the following pairs" question: its numbered pairs ("1. Burzahom – Rock-cut shrines") shown as a
 * table with the column headings when the paper gives them ("Historical place – Well-known for"). Null when the
 * stem is not laid out that way.
 */
data class PairsLayout(
    val intro: String,
    val headLeft: String,
    val headRight: String,
    val items: List<Triple<String, String, String>>,
    val outro: String,
) {
    companion object {
        private const val LAB = """([a-hA-H1-8]|i{1,3}|iv|vi{0,3}|I{1,3}|IV|VI{0,3})"""
        private val LINE = Regex("""^\s*\(?$LAB[.)]\s*(.+?)\s+[-–—:]\s+(.+?)\s*$""")
        private val LINE2 = Regex("""^\s*\(?$LAB[.)]\s*(.+?)\s*[–—]\s*(.+?)\s*$""")
        private val HEAD = Regex("""^(.*?)\s+[-–—]\s+(.*)$""")
        private val WORD = Regex("""\bpairs?\b|correctly matched|\bmatch(?!es\b)""", RegexOption.IGNORE_CASE)
        private val Q = Regex("""\s+((?:Which|How many|Select|Choose)\b.*)$""")

        fun parse(stem: String): PairsLayout? = runCatching { parseOrThrow(stem) }.getOrNull()

        private fun parseOrThrow(stem: String): PairsLayout? {
            if (!WORD.containsMatchIn(stem)) return null
            val lines = stem.split('\n').filter { it.isNotBlank() }
            val idx = lines.indices.filter { LINE.matches(lines[it]) || LINE2.matches(lines[it]) }
            if (idx.size < 2 || idx != (idx.first()..idx.last()).toList()) return null
            var extra = ""
            val items = idx.map { i ->
                val m = (LINE.matchEntire(lines[i]) ?: LINE2.matchEntire(lines[i]))!!
                var r = m.groupValues[3].trim()
                if (i == idx.last()) Q.find(r)?.let { q -> extra = q.groupValues[1]; r = r.substring(0, q.range.first).trim() }
                Triple(m.groupValues[1], m.groupValues[2].trim(), r)
            }
            var intro = lines.subList(0, idx.first()).joinToString("\n").trim()
            var hl = ""
            var hr = ""
            val head = if (idx.first() > 0) lines[idx.first() - 1].trim() else ""
            HEAD.matchEntire(head)?.let { hm ->
                if (head.length < 80 && !Regex("""[?:.]\s*$""").containsMatchIn(head)) {
                    hl = hm.groupValues[1].trim(' ', '(', ')'); hr = hm.groupValues[2].trim(' ', '(', ')')
                    intro = lines.subList(0, idx.first() - 1).joinToString("\n").trim()
                }
            }
            val outro = (extra + "\n" + lines.subList(idx.last() + 1, lines.size).joinToString("\n")).trim()
            return PairsLayout(intro, hl, hr, items, outro)
        }
    }
}
