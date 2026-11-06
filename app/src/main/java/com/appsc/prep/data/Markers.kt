package com.appsc.prep.data

import androidx.compose.ui.graphics.Color

/**
 * A marker on a notes page (APPSC Reader): the marked words on page [page] ("book:row:sec") in colour [color],
 * found again by their text, so it stays on the line however the screen wraps it.
 */
data class Mark(val page: String, val text: String, val color: Int, val time: Long, val title: String, val rowTitle: String) {
    fun encode() = listOf(page, color.toString(), time.toString(), title, rowTitle, text.replace("\n", " ")).joinToString("\t")

    companion object {
        fun decode(line: String): Mark? {
            val p = line.split('\t')
            if (p.size < 6) return null
            return Mark(p[0], p.drop(5).joinToString("\t"), p[1].toIntOrNull() ?: 0, p[2].toLongOrNull() ?: 0L, p[3], p[4])
        }
    }
}

/** The marker colours and what each is for. */
object Markers {
    data class Pen(val name: String, val use: String, val fill: Color, val ink: Color)

    val pens = listOf(
        Pen("Yellow", "Key line", Color(0xFFFFF176), Color(0xFF8D6E00)),
        Pen("Green", "Dates & numbers", Color(0xFFB9F6CA), Color(0xFF1B5E20)),
        Pen("Pink", "Confusing", Color(0xFFF8BBD0), Color(0xFF880E4F)),
        Pen("Blue", "Revise again", Color(0xFFB3E5FC), Color(0xFF01579B)),
    )

    /** The lines of a selection worth marking (a selection over several blocks comes as several lines). */
    fun pieces(selection: String): List<String> =
        selection.split('\n').map { it.trim() }.filter { it.length >= 2 }

    /** [text] with every marked span on it given its marker's colour. */
    fun apply(text: androidx.compose.ui.text.AnnotatedString, marks: List<Mark>): androidx.compose.ui.text.AnnotatedString {
        if (marks.isEmpty()) return text
        val plain = text.text
        val spans = marks.flatMap { m ->
            generateSequence(plain.indexOf(m.text)) { i -> plain.indexOf(m.text, i + m.text.length).takeIf { it >= 0 } }
                .takeWhile { it >= 0 }.map { Triple(it, it + m.text.length, m.color) }.toList()
        }
        if (spans.isEmpty()) return text
        return androidx.compose.ui.text.AnnotatedString.Builder(text).apply {
            spans.forEach { (a, b, c) ->
                addStyle(androidx.compose.ui.text.SpanStyle(background = pens[c.coerceIn(0, pens.size - 1)].fill), a, b)
            }
        }.toAnnotatedString()
    }
}
