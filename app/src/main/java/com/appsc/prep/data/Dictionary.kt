package com.appsc.prep.data

import java.io.InputStream

/**
 * Offline word meanings for "Meaning" on selected text: WordNet 3.1 (assets/dict/<letter>.tsv, built by
 * tools/build_dictionary.py), plus the short forms the notes use (SpeechText.expand).
 */
class Dictionary(private val open: (String) -> InputStream) {
    data class Sense(val pos: String, val definition: String, val example: String)

    /** [word] is the dictionary form found ("government" for "governments"). */
    data class Entry(val word: String, val senses: List<Sense>, val shortForm: String? = null)

    // the last few letter files used: (sorted lower-case keys, lines)
    private val letters = object : LinkedHashMap<Char, Pair<List<String>, List<String>>>(4, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<Char, Pair<List<String>, List<String>>>?) = size > 3
    }

    /** Meaning of a selected word or phrase, or null when neither the dictionary nor the notes know it. */
    @Synchronized
    fun lookup(selection: String): Entry? {
        val raw = selection.trim().trim { !it.isLetterOrDigit() }.replace(Regex("""\s+"""), " ")
        if (raw.isEmpty() || raw.length > 60) return null
        // a short form the notes use (SC, WTO, VCIC ...)
        val short = raw.takeIf { it.length in 2..10 && it.count(Char::isUpperCase) >= 2 }?.let { SpeechText.expand(it) }
        for (c in candidates(raw)) {
            find(c)?.let { return Entry(c, it, short) }
        }
        // a phrase not in the dictionary: its last word ("Federal Court" -> court) is not helpful, so stop
        return short?.let { Entry(raw, emptyList(), it) }
    }

    /** The selection and its likely dictionary forms: plural, past, -ing, -er/-est. */
    private fun candidates(raw: String): List<String> {
        val w = raw.lowercase().replace('’', '\'').removeSuffix("'s").removeSuffix("'")
        val out = linkedSetOf(w)
        if (' ' !in w) {
            fun add(s: String) { if (s.length >= 2) out += s }
            when {
                w.endsWith("ies") -> add(w.dropLast(3) + "y")
                w.endsWith("ves") -> { add(w.dropLast(3) + "f"); add(w.dropLast(3) + "fe") }
                w.endsWith("sses") || w.endsWith("shes") || w.endsWith("ches") || w.endsWith("xes") || w.endsWith("zes") -> add(w.dropLast(2))
            }
            if (w.endsWith("es")) { add(w.dropLast(1)); add(w.dropLast(2)) }
            if (w.endsWith("s") && !w.endsWith("ss")) add(w.dropLast(1))
            for (suffix in listOf("ed", "ing", "er", "est")) {
                if (!w.endsWith(suffix)) continue
                val stem = w.dropLast(suffix.length)
                if (stem.endsWith("i")) add(stem.dropLast(1) + "y")
                add(stem)
                add(stem + "e")
                if (stem.length > 2 && stem.last() == stem[stem.length - 2]) add(stem.dropLast(1))
            }
            if (w.endsWith("ly")) { add(w.dropLast(2)); if (w.endsWith("ily")) add(w.dropLast(3) + "y") }
        } else {
            // hyphens and spaces are written either way
            out += w.replace('-', ' ')
            out += w.replace(' ', '-')
        }
        return out.toList()
    }

    private fun find(word: String): List<Sense>? {
        val (keys, lines) = file(word.first()) ?: return null
        var lo = 0
        var hi = keys.size - 1
        while (lo <= hi) {
            val mid = (lo + hi) ushr 1
            val c = keys[mid].compareTo(word)
            when {
                c < 0 -> lo = mid + 1
                c > 0 -> hi = mid - 1
                else -> return lines[mid].split('\t').drop(1).mapNotNull { s ->
                    val p = s.split('|')
                    if (p.size < 2) null else Sense(POS[p[0]] ?: p[0], p[1], p.getOrElse(2) { "" })
                }
            }
        }
        return null
    }

    private fun file(first: Char): Pair<List<String>, List<String>>? {
        val c = first.lowercaseChar().let { if (it in 'a'..'z') it else '_' }
        letters[c]?.let { return it }
        val lines = runCatching { open("dict/$c.tsv").bufferedReader().use { it.readLines() } }.getOrNull() ?: return null
        val keys = lines.map { it.substringBefore('\t').lowercase() }
        return (keys to lines).also { letters[c] = it }
    }

    private companion object {
        val POS = mapOf("n" to "noun", "v" to "verb", "adj" to "adjective", "adv" to "adverb")
    }
}
