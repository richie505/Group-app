package com.appsc.prep.data

/**
 * Markdown pasted into an explanation (from Gemini, ChatGPT, Google...) as note blocks, so it shows as
 * headings, bullets, bold and tables instead of raw "|", "**" and "#" marks.
 */
object MarkdownText {
    private val TABLE_SEP = Regex("""^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$""")
    private val BULLET = Regex("""^(\s*)[-*•+]\s+(.*)$""")
    private val HEADING = Regex("""^#{1,6}\s+(.*)$""")
    private val RULE = Regex("""^(-{3,}|\*{3,}|_{3,})$""")

    /** Whether [text] uses markdown worth laying out (a table, a heading, bullets or bold). */
    fun looksLike(text: String): Boolean {
        val lines = text.lines().map { it.trim() }
        return lines.any { it.startsWith("|") && it.count { c -> c == '|' } >= 2 } ||
            lines.any { HEADING.matches(it) } ||
            lines.count { BULLET.matches(it) } >= 2 ||
            text.contains("**")
    }

    fun blocks(text: String): List<Block> {
        val lines = text.replace("\r", "").lines()
        val out = mutableListOf<Block>()
        var i = 0
        while (i < lines.size) {
            val raw = lines[i]
            val s = raw.trim()
            when {
                s.isEmpty() || RULE.matches(s) -> i++
                s.startsWith("|") -> {
                    val rows = mutableListOf<List<List<Run>>>()
                    while (i < lines.size && lines[i].trim().startsWith("|")) {
                        val l = lines[i].trim()
                        if (!TABLE_SEP.matches(l)) rows += cells(l)
                        i++
                    }
                    if (rows.size >= 2) {
                        val cols = rows.maxOf { it.size }
                        val pad = rows.map { r -> r + List(cols - r.size) { listOf(Run("", 0)) } }
                        out += TableBlock(pad.first(), pad.drop(1))
                    } else if (rows.size == 1) {
                        out += TextBlock('p', rows[0].flatMapIndexed { k, c -> if (k == 0) c else listOf(Run(" · ", 0)) + c })
                    }
                }
                else -> {
                    val h = HEADING.matchEntire(s)
                    val b = BULLET.matchEntire(raw)
                    out += when {
                        h != null -> TextBlock('h', runs(h.groupValues[1]))
                        b != null -> TextBlock(if (b.groupValues[1].length >= 2) 's' else 'b', runs(b.groupValues[2]))
                        else -> TextBlock('p', runs(s))
                    }
                    i++
                }
            }
        }
        return out
    }

    private fun cells(line: String): List<List<Run>> =
        line.trim().removePrefix("|").removeSuffix("|").split("|").map { runs(it.trim()) }

    /** "**bold**", "*italic*" and "`code`" as runs; stray marks dropped. */
    fun runs(text: String): List<Run> {
        val out = mutableListOf<Run>()
        val bold = text.replace("`", "").replace("__", "**").split("**")
        bold.forEachIndexed { i, part ->
            if (part.isEmpty()) return@forEachIndexed
            val b = if (i % 2 == 1 && i < bold.size - 1) 1 else 0
            // *italic* inside: only a pair of single stars around a word
            val it = Regex("""(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])""")
            var last = 0
            it.findAll(part).forEach { m ->
                if (m.range.first > last) out += Run(part.substring(last, m.range.first), b)
                out += Run(m.groupValues[1], b or 2)
                last = m.range.last + 1
            }
            if (last < part.length) out += Run(part.substring(last), b)
        }
        return out.ifEmpty { listOf(Run("", 0)) }
    }
}
