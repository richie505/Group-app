package com.appsc.prep.data

/**
 * The notes page that holds an MCQ's fact: every page of its subject is scored on the question's words, and above
 * all on its right answer's ("$42,000", "Tadikonda"), so the page shown is the one that answers it, not just the
 * page the MCQ happens to be filed under.
 */
object NotesFinder {
    data class Place(val row: Int, val sec: Int, val score: Double)

    private val STOP = setOf(
        "the", "and", "for", "with", "from", "that", "this", "which", "following", "above", "below", "statements",
        "statement", "correct", "incorrect", "consider", "select", "answer", "using", "code", "codes", "given", "only",
        "both", "neither", "none", "all", "was", "were", "are", "is", "its", "their", "has", "have", "been", "under",
        "into", "about", "what", "who", "whom", "when", "where", "how", "not", "one", "two", "of", "in", "on", "to",
        "by", "as", "at", "an", "or", "be", "it", "india", "indian", "state", "states", "pradesh", "andhra", "government",
    )

    fun words(text: String): Set<String> =
        Regex("[A-Za-z][A-Za-z\\-]{2,}|\\d[\\d,.]*").findAll(text.lowercase()).map { it.value.trim('.', ',').replace(",", "") }
            .filter { it.length >= 2 && it !in STOP }.toSet()

    fun text(blocks: List<Block>): String = blocks.joinToString("\n") { b ->
        when (b) {
            is TextBlock -> b.runs.joinToString("") { it.text }
            is TableBlock -> (listOf(b.head) + b.rows).joinToString("\n") { r -> r.joinToString(" | ") { c -> c.joinToString("") { it.text } } }
        }
    }

    /** The right answer's words: the ones a page must hold to answer the MCQ. */
    fun answerWords(q: Question): Set<String> {
        val opt = q.options.getOrNull(q.answer).orEmpty()
        // "1 and 3 only", "Both", "All of the above": the answer is in the statements, not the option
        val plain = if (Regex("^(\\d|[ivx]+|[a-d])(\\s*(,|and)\\s*(\\d|[ivx]+|[a-d]))*( only)?$", RegexOption.IGNORE_CASE).matches(opt.trim()) ||
            Regex("both|neither|all of|none of|above", RegexOption.IGNORE_CASE).containsMatchIn(opt)
        ) "" else opt
        return words(plain + " " + q.answerText)
    }

    fun best(q: Question, book: Book, filedRow: Int): Place? {
        val ask = words(q.stem) + words(q.explanation) + q.notes.flatMap { words(it) } + q.solution.flatMap { words(it) }
        val ans = answerWords(q)
        // rarer words count more: a page with "Swarnandhra" beats one with "scheme"
        val pages = book.rows.flatMapIndexed { ri, r -> r.secs.mapIndexed { si, s -> Triple(ri, si, words(s.title + " " + text(s.blocks))) } }
        val df = HashMap<String, Int>()
        for ((_, _, w) in pages) for (x in w) if (x in ask || x in ans) df[x] = (df[x] ?: 0) + 1
        val n = pages.size.toDouble()
        fun idf(x: String) = kotlin.math.ln(1 + n / ((df[x] ?: 0) + 1))
        return pages.map { (ri, si, w) ->
            var s = 0.0
            for (x in ask) if (x in w) s += idf(x)
            for (x in ans) if (x in w) s += 3 * idf(x)
            if (ans.isNotEmpty() && ans.all { it in w }) s *= 1.5
            if (ri == filedRow) s *= 1.15 // a tie goes to the topic it is filed under
            Place(ri, si, s)
        }.maxByOrNull { it.score }?.takeIf { it.score > 0 }
    }
}
