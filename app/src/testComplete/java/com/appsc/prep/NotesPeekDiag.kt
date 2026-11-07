package com.appsc.prep

import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.NotesFinder
import com.appsc.prep.data.Repository
import kotlinx.coroutines.runBlocking
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/** Diagnostic only (run with -Ddiag=1): what the book icon opens for every own MCQ, written as JSON lines. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class NotesPeekDiag {
    @Test fun dump() = runBlocking {
        val out = System.getenv("NOTES_DIAG") ?: return@runBlocking
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val repo = Repository { ctx.assets.open(it) }
        repo.mcqNotes = true
        fun js(s: String) = "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\t", " ") + "\""
        java.io.File(out).printWriter().use { w ->
            for (b in 1..6) {
                val m = runCatching { repo.mcq(b) }.getOrNull() ?: continue
                val book = repo.book(b)
                for ((_, qs) in m.rows) for (q in qs) {
                    if (q.id.startsWith("y")) continue
                    val p = m.placeOf(q.id)
                    val at = NotesFinder.best(q, book, p?.first ?: -1, p?.second ?: -1)
                    val keys = if (at == null) emptyList() else NotesFinder.keyLines(q, book.rows[at.row], at.sec)
                    val kt = keys.joinToString(" || ") { NotesFinder.text(listOf(it.third)) }
                    w.println("{\"id\":${js(q.id)},\"b\":$b,\"fr\":${p?.first ?: -1},\"fs\":${p?.second ?: -1},\"br\":${at?.row ?: -1},\"bs\":${at?.sec ?: -1}," +
                        "\"kr\":[${keys.joinToString(",") { "${it.first}" }}],\"keys\":${js(kt)},\"s\":${js(q.stem)},\"ans\":${js(q.options.getOrNull(q.answer).orEmpty())}}")
                }
            }
        }
    }
}
