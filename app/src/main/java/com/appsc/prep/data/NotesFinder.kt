package com.appsc.prep.data

/**
 * The notes page that holds an MCQ's fact: every page of its subject is scored on the question's words, and above
 * all on its right answer's ("$42,000", "Tadikonda"), so the page shown is the one that answers it, not just the
 * page the MCQ happens to be filed under.
 */
object NotesFinder {
    data class Place(val row: Int, val sec: Int, val score: Double)

    /** "[September 2025 · page title]" at the end of a current-affairs MCQ's note: the page it was written from. */
    private val TAG = Regex("""\s*\[[^\]·]*·\s*([^\]]+)]\s*$""")

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
    private class Index(
        val pages: List<Triple<Int, Int, Set<String>>>,
        val df: Map<String, Int>,
        /** page title -> its pages */
        val byTitle: Map<String, List<Pair<Int, Int>>>,
        val book: Book,
    )

    private val indexes = java.util.concurrent.ConcurrentHashMap<Int, Index>()
    private val found = java.util.concurrent.ConcurrentHashMap<String, Place>()

    private fun index(book: Book): Index {
        // another copy of the book (the notes were switched, or reloaded): its pages differ, so start afresh
        indexes[book.id]?.let { if (it.book !== book) clear() }
        return indexes.getOrPut(book.id) { build(book) }
    }

    private fun build(book: Book): Index = run {
        val pages = book.rows.flatMapIndexed { ri, r -> r.secs.mapIndexed { si, s -> Triple(ri, si, words(s.title + " " + text(s.blocks))) } }
        val df = HashMap<String, Int>()
        for ((_, _, w) in pages) for (x in w) df[x] = (df[x] ?: 0) + 1
        val byTitle = HashMap<String, MutableList<Pair<Int, Int>>>()
        book.rows.forEachIndexed { ri, r ->
            r.secs.forEachIndexed { si, sec ->
                byTitle.getOrPut(sec.title.trim()) { mutableListOf() } += ri to si
            }
        }
        Index(pages, df, byTitle, book)
    }

    /** Forgets every index (the notes were switched). */
    fun clear() {
        indexes.clear()
        found.clear()
    }

    /** Builds the book's index ahead of time (the quiz does it while a question shows). */
    fun warm(book: Book) {
        index(book)
    }

    fun best(q: Question, book: Book, filedRow: Int, filedSec: Int = -1): Place? {
        val ix = index(book) // first: a switched book clears what was found in the other
        found[q.id + "|" + q.answer]?.let { return it }
        // a current-affairs MCQ names its notes page: "... [September 2025 · India's first Centralised Advanced Smart Kitchen — Kadapa]"
        val named = q.notes.mapNotNull { TAG.find(it)?.groupValues?.get(1)?.trim() }.flatMap { ix.byTitle[it].orEmpty() }.toSet()
        val facts = q.notes.map { it.replace(TAG, "") }
        val ask = words(q.stem) + words(q.explanation) + facts.flatMap { words(it) } + q.solution.flatMap { words(it) }
        val ans = answerWords(q)
        // rarer words count more: a page with "Swarnandhra" beats one with "scheme"
        val n = ix.pages.size.toDouble()
        fun idf(x: String) = kotlin.math.ln(1 + n / ((ix.df[x] ?: 0) + 1))
        val wa = ask.associateWith { idf(it) }
        val wb = ans.associateWith { 3 * idf(it) }
        return ix.pages.filter { named.isEmpty() || (it.first to it.second) in named }.map { (ri, si, w) ->
            var s = 0.0
            for ((x, v) in wa) if (x in w) s += v
            for ((x, v) in wb) if (x in w) s += v
            if (ans.isNotEmpty() && ans.all { it in w }) s *= 1.5
            if (ri == filedRow) s *= 1.15 // a tie goes to the topic it is filed under
            if (ri == filedRow && si == filedSec) s *= 1.3 // and to the page it was written from
            Place(ri, si, s)
        }.maxByOrNull { it.score }?.takeIf { it.score > 0 }?.also { found[q.id + "|" + q.answer] = it }
    }

    private val NUMBERED = Regex("""^\s*(\d)\.\s+(.+)$""")
    private val WHY = Regex("""^Statement (\d):\s*(.+)$""")

    /**
     * A "Consider the following statements" MCQ: each statement's own line (with its explanation, which gives the
     * right fact of a wrong statement), so all three facts are marked, not just the ones the option code points at.
     * Null when the MCQ has no numbered statements.
     */
    fun statementMarks(q: Question, blocks: List<Block>): Set<Int>? {
        val st = q.stem.lines().mapNotNull { NUMBERED.matchEntire(it)?.let { m -> m.groupValues[1] to m.groupValues[2] } }
        if (st.size < 2) return null
        val why = q.explanation.lines().mapNotNull { WHY.matchEntire(it.trim())?.let { m -> m.groupValues[1] to m.groupValues[2] } }.toMap()
        val bw = blocks.map { words(text(listOf(it))) }
        val out = mutableSetOf<Int>()
        for ((n, s) in st) {
            val ws = words(s)
            val w = ws + words(why[n].orEmpty().replace(Regex("^(Correct|Incorrect):", RegexOption.IGNORE_CASE), ""))
            if (w.isEmpty()) continue
            // the statement's own words count double (its explanation adds the right fact of a wrong one);
            // a short line beats a long one that shares as many
            val best = bw.indices.map { i ->
                val c = bw[i].count { it in w }
                i to (c to (c + bw[i].count { it in ws }) / Math.pow(bw[i].size.coerceAtLeast(1).toDouble(), 0.3))
            }.filter { (_, s2) -> s2.first >= 3 || s2.first * 2 >= w.size.coerceAtMost(6) }
                .maxByOrNull { it.second.second } ?: continue
            out += best.first
        }
        return out
    }

    /**
     * The key points of a topic for [q]: (page, line) of each line that states a fact the MCQ tests. A statement MCQ:
     * for each statement, its best line on any page of the topic (a text line, or a table: see [keyLines]).
     * Otherwise: the lines holding the answer on the page [at] (the one [best] found). Empty when none is clear; the
     * whole page shows then.
     */
    fun keyPoints(q: Question, row: NoteRow, at: Int): List<Pair<Int, Int>> =
        keyLines(q, row, at).map { it.first to it.second }.distinct()

    /**
     * [keyPoints] with what to show for each: (page, block, the block itself, or for a table just its matching row
     * under the table's head).
     */
    fun keyLines(q: Question, row: NoteRow, at: Int): List<Triple<Int, Int, Block>> {
        val st = q.stem.lines().mapNotNull { NUMBERED.matchEntire(it)?.let { m -> m.groupValues[1] to m.groupValues[2] } }
        if (st.size >= 2) {
            val why = q.explanation.lines().mapNotNull { WHY.matchEntire(it.trim())?.let { m -> m.groupValues[1] to m.groupValues[2] } }.toMap()
            // every text line (not headings) and every table row is a line
            val lines = row.secs.flatMapIndexed { si, s ->
                s.blocks.flatMapIndexed { bi, b ->
                    when {
                        b is TextBlock && b.kind != 'h' -> listOf(Triple(si, bi, b as Block))
                        b is TableBlock -> b.rows.map { r -> Triple(si, bi, TableBlock(b.head, listOf(r)) as Block) }
                        else -> emptyList()
                    }
                }
            }.map { (si, bi, b) -> Pair(Triple(si, bi, b), words(text(listOf(b)))) }
            val out = LinkedHashSet<Triple<Int, Int, Block>>()
            for ((n, s) in st) {
                val ws = words(s)
                val w = ws + words(why[n].orEmpty().replace(Regex("^(Correct|Incorrect):", RegexOption.IGNORE_CASE), ""))
                if (w.isEmpty()) continue
                val best = lines.map { (key, lw) ->
                    val c = lw.count { it in w }
                    Triple(key, c, (c + lw.count { it in ws }) / Math.pow(lw.size.coerceAtLeast(1).toDouble(), 0.3) + if (key.first == at) 0.2 else 0.0)
                }.filter { it.second >= 3 || it.second * 2 >= w.size.coerceAtMost(6) }.maxByOrNull { it.third } ?: continue
                out += best.first
            }
            return out.toList()
        }
        return oneLiner(q, row, at)
    }

    private val NUM = Regex("""\d[\d,.]*""")

    /** The numbers in a text, single digits too ("3 members" -> 3), which [words] leaves out. */
    private fun nums(t: String): Set<String> = NUM.findAll(t).map { it.value.trim('.', ',').replace(",", "") }.filter { it.isNotEmpty() }.toSet()

    /**
     * A one-liner's key points: the one or two lines (a text line, or one row of a table under its head) that state
     * its fact. Every line of the topic is scored on the right answer's words and numbers, the explanation's and the
     * stem's; a short line beats a long one that shares as many, and the page [at] (the one [best] found) wins a tie.
     * Never a whole table or a whole page: when no line is clear, nothing (the whole page shows then).
     */
    private fun oneLiner(q: Question, row: NoteRow, at: Int): List<Triple<Int, Int, Block>> {
        val opt = q.options.getOrNull(q.answer).orEmpty()
        val ans = answerWords(q)
        val an = if (ans.isEmpty() && opt.length < 25 && Regex("only|both|neither|above", RegexOption.IGNORE_CASE).containsMatchIn(opt)) emptySet() else nums(opt)
        val stem = words(q.stem)
        val why = words(q.explanation) - STOP
        val body = (row.secs.size - 3).coerceAtLeast(1) // the last three pages: number game, past papers, traps
        val lines = row.secs.flatMapIndexed { si, sec ->
            sec.blocks.flatMapIndexed { bi, b ->
                when {
                    b is TextBlock && b.kind != 'h' -> listOf(Triple(si, bi, b as Block))
                    b is TableBlock -> b.rows.map { r -> Triple(si, bi, TableBlock(b.head, listOf(r)) as Block) }
                    else -> emptyList()
                }
            }
        }
        val scored = lines.map { key ->
            val b = key.third
            // a table row on its own (its head's words would count for every row)
            val t = if (b is TableBlock) b.rows.joinToString("\n") { r -> r.joinToString(" | ") { c -> c.joinToString("") { it.text } } } else text(listOf(b))
            val lw = words(t)
            val a = ans.count { it in lw }
            val n = an.count { it in nums(t) }
            val e = why.count { it in lw }
            val st = stem.count { it in lw }
            var sc = (3.0 * a + 3.0 * n + 1.5 * e + st) / Math.pow(lw.size.coerceAtLeast(3).toDouble(), 0.35)
            if (key.first == at) sc += 0.6
            if (key.first >= body) sc *= 0.6
            Triple(key, sc, Triple(a + n, e + st, lw.size))
        }.filter { (_, _, c) ->
            // the answer must be on the line when the answer has words or numbers; else the question's words carry it
            (if (ans.isNotEmpty() || an.isNotEmpty()) c.first >= 1 else true) && c.first + c.second >= 2
        }.sortedByDescending { it.second }
        val top = scored.firstOrNull() ?: return emptyList()
        val out = mutableListOf(top.first)
        scored.getOrNull(1)?.let { (k, sc, _) -> if (sc >= top.second * 0.8 && k.first == top.first.first) out += k }
        return out.sortedWith(compareBy({ it.first }, { it.second }))
    }

    /** Whether a block holds the answer (most of its words): such lines are marked. */
    fun marks(blk: Block, answer: Set<String>): Boolean =
        answer.isNotEmpty() && words(text(listOf(blk))).let { w -> answer.count { it in w } * 2 >= answer.size }

    /**
     * The blocks of a page to mark for [q]: those holding its answer; when the answer is a code ("1 and 3 only") or
     * no line holds it, the two blocks that share the most of the question's words.
     */
    fun marked(q: Question, blocks: List<Block>): Set<Int> {
        statementMarks(q, blocks)?.let { return it }
        val ans = answerWords(q)
        val byAnswer = blocks.indices.filter { marks(blocks[it], ans) }.toSet()
        if (byAnswer.isNotEmpty()) return byAnswer
        val ask = words(q.stem) + words(q.explanation)
        return blocks.indices.map { it to words(text(listOf(blocks[it]))).count { w -> w in ask } }
            .filter { it.second >= 2 }.sortedByDescending { it.second }.take(2).map { it.first }.toSet()
    }
}
