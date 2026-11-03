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

    /** A subject's pages as word sets, and in how many pages each word is: built once per book, then kept. */
    private class Index(val pages: List<Triple<Int, Int, Set<String>>>, val df: Map<String, Int>)

    private val indexes = java.util.concurrent.ConcurrentHashMap<Int, Index>()
    private val found = java.util.concurrent.ConcurrentHashMap<String, Place>()

    private fun index(book: Book): Index = indexes.getOrPut(book.id) {
        val pages = book.rows.flatMapIndexed { ri, r -> r.secs.mapIndexed { si, s -> Triple(ri, si, words(s.title + " " + text(s.blocks))) } }
        val df = HashMap<String, Int>()
        for ((_, _, w) in pages) for (x in w) df[x] = (df[x] ?: 0) + 1
        Index(pages, df)
    }

    /** Builds the book's index ahead of time (the quiz does it while a question shows). */
    fun warm(book: Book) {
        index(book)
    }

    fun best(q: Question, book: Book, filedRow: Int): Place? {
        found[q.id + "|" + q.answer]?.let { return it }
        val ix = index(book)
        val ask = words(q.stem) + words(q.explanation) + q.notes.flatMap { words(it) } + q.solution.flatMap { words(it) }
        val ans = answerWords(q)
        // rarer words count more: a page with "Swarnandhra" beats one with "scheme"
        val n = ix.pages.size.toDouble()
        fun idf(x: String) = kotlin.math.ln(1 + n / ((ix.df[x] ?: 0) + 1))
        val wa = ask.associateWith { idf(it) }
        val wb = ans.associateWith { 3 * idf(it) }
        return ix.pages.map { (ri, si, w) ->
            var s = 0.0
            for ((x, v) in wa) if (x in w) s += v
            for ((x, v) in wb) if (x in w) s += v
            if (ans.isNotEmpty() && ans.all { it in w }) s *= 1.5
            if (ri == filedRow) s *= 1.15 // a tie goes to the topic it is filed under
            Place(ri, si, s)
        }.maxByOrNull { it.score }?.takeIf { it.score > 0 }?.also { found[q.id + "|" + q.answer] = it }
    }

    /** Whether a block holds the answer (most of its words): such lines are marked. */
    fun marks(blk: Block, answer: Set<String>): Boolean =
        answer.isNotEmpty() && words(text(listOf(blk))).let { w -> answer.count { it in w } * 2 >= answer.size }

    /**
     * The blocks of a page to mark for [q]: those holding its answer; when the answer is a code ("1 and 3 only") or
     * no line holds it, the two blocks that share the most of the question's words.
     */
    fun marked(q: Question, blocks: List<Block>): Set<Int> {
        val ans = answerWords(q)
        val byAnswer = blocks.indices.filter { marks(blocks[it], ans) }.toSet()
        if (byAnswer.isNotEmpty()) return byAnswer
        val ask = words(q.stem) + words(q.explanation)
        return blocks.indices.map { it to words(text(listOf(blocks[it]))).count { w -> w in ask } }
            .filter { it.second >= 2 }.sortedByDescending { it.second }.take(2).map { it.first }.toSet()
    }
}
