package com.appsc.prep.data

import android.content.Context
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import java.time.LocalDate

/** A saved subsection: id is "book:row:sec". */
data class Saved(val id: String, val title: String, val rowTitle: String)

/** Read/done state, bookmarks, last position and reader settings, kept in SharedPreferences. */
class ProgressStore(context: Context) {
    private val prefs = context.getSharedPreferences("progress", Context.MODE_PRIVATE)

    var done by mutableStateOf(prefs.getStringSet(KEY_DONE, emptySet())!!.toSet())
        private set
    var saved by mutableStateOf(decodeSaved(prefs.getStringSet(KEY_SAVED, emptySet())!!))
        private set
    var activeDates by mutableStateOf(prefs.getStringSet(KEY_DATES, emptySet())!!.toSet())
        private set
    var lastRead by mutableStateOf(prefs.getString(KEY_LAST, null))
        private set
    var textScale by mutableFloatStateOf(prefs.getFloat(KEY_SCALE, 1f))
        private set

    fun isDone(id: String) = id in done

    fun setDone(id: String, value: Boolean) {
        if (value == (id in done)) return
        done = if (value) done + id else done - id
        prefs.edit().putStringSet(KEY_DONE, done).apply()
        if (value) markActive()
    }

    fun toggleDone(id: String) = setDone(id, id !in done)

    fun doneCount(book: Int, row: Int, total: Int): Int =
        (0 until total).count { subsectionId(book, row, it) in done }

    fun isSaved(id: String) = saved.any { it.id == id }

    fun toggleSaved(item: Saved) {
        saved = if (isSaved(item.id)) saved.filterNot { it.id == item.id } else listOf(item) + saved
        prefs.edit().putStringSet(KEY_SAVED, saved.mapIndexed { i, s -> "$i\t${s.id}\t${s.title}\t${s.rowTitle}" }.toSet()).apply()
    }

    fun rememberPosition(id: String) {
        lastRead = id
        prefs.edit().putString(KEY_LAST, id).apply()
    }

    fun changeTextScale(delta: Float) {
        textScale = (textScale + delta).coerceIn(0.85f, 1.45f)
        prefs.edit().putFloat(KEY_SCALE, textScale).apply()
    }

    /** Consecutive days (ending today or yesterday) on which something was marked done. */
    fun streak(today: LocalDate = LocalDate.now()): Int {
        var d = if (today.toString() in activeDates) today else today.minusDays(1)
        var n = 0
        while (d.toString() in activeDates) {
            n++
            d = d.minusDays(1)
        }
        return n
    }

    private fun markActive() {
        val t = LocalDate.now().toString()
        if (t !in activeDates) {
            activeDates = activeDates + t
            prefs.edit().putStringSet(KEY_DATES, activeDates).apply()
        }
    }

    private fun decodeSaved(raw: Set<String>): List<Saved> =
        raw.mapNotNull { line ->
            val p = line.split('\t')
            if (p.size < 4) null else (p[0].toIntOrNull() ?: 0) to Saved(p[1], p[2], p[3])
        }.sortedBy { it.first }.map { it.second }

    private companion object {
        const val KEY_DONE = "done"
        const val KEY_SAVED = "saved"
        const val KEY_DATES = "dates"
        const val KEY_LAST = "last"
        const val KEY_SCALE = "scale"
    }
}
