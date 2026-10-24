package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.data.Storage
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.Nav
import com.appsc.prep.ui.screens.QuizScreen
import com.appsc.prep.ui.screens.QuizSource
import com.appsc.prep.ui.theme.PrepTheme
import com.github.takahirom.roborazzi.captureRoboImage
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** APPSC One-liners: APPSC Complete with every MCQ a one-liner and no explanations. */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class OnelinerTest {
    @get:Rule val rule = createComposeRule()
    private val ctx get() = ApplicationProvider.getApplicationContext<android.content.Context>()
    private val repo get() = Repository { ctx.assets.open(it) }
    private val nav = object : Nav {
        override fun quiz(kind: String, book: Int, index: Int, mode: String, sub: Int) {}
        override fun day(n: Int) {}
        override fun row(book: Int, row: Int) {}
        override fun read(book: Int, row: Int, sec: Int) {}
        override fun book(id: Int) {}
        override fun back() {}
    }
    private class Mem : Storage {
        val sets = HashMap<String, Set<String>>(); val strings = HashMap<String, String>()
        override fun getStringSet(key: String) = sets[key].orEmpty()
        override fun getString(key: String) = strings[key]
        override fun getFloat(key: String, default: Float) = default
        override fun putStringSet(key: String, value: Set<String>) { sets[key] = value }
        override fun putString(key: String, value: String) { strings[key] = value }
        override fun putFloat(key: String, value: Float) {}
    }

    @Test fun edition() {
        val r = repo
        assertEquals("APPSC One-liners", r.appName)
        assertTrue(r.oneliner && r.complete && !r.revision)
        assertEquals(listOf("Group 1", "Group 2"), r.exams.map { it.title })
    }

    /** Every MCQ: one line, four different options, an answer, no explanation; topic counts match. */
    @Test fun everyMcqIsAOneLiner() {
        val r = repo
        var total = 0
        for (b in 1..6) {
            val book = runBlocking { r.mcq(b) }
            for ((row, qs) in book.rows) {
                assertEquals("book $b row $row count", r.rowInfo(b, row)?.questionCount, qs.size)
                for (q in qs) {
                    total++
                    assertTrue("${q.id}: one line", '\n' !in q.stem.trim() && q.stem.length <= 220)
                    assertEquals("${q.id}: 4 options", 4, q.options.map { it.trim().lowercase() }.distinct().size)
                    assertTrue("${q.id}: answer", q.answer in 0..3)
                    assertTrue("${q.id}: no explanation", q.explanation.isBlank() && q.solution.isEmpty() && q.extra.isEmpty())
                    assertTrue("${q.id}: plain options", q.options.none { Regex("""^\s*([1-6](\s*(,|and)\s*[1-6])+(\s*only)?|both\b|neither\b)""", RegexOption.IGNORE_CASE).containsMatchIn(it) })
                }
            }
        }
        assertTrue("one-liners: $total", total > 60_000)
    }

    /** planmcq.json is built from these MCQs (tools/oneliner_import.py runs tools/build_plan_mcq.py). */
    @Test fun planMcqFileIsCurrent() {
        val r = repo
        val books = runBlocking { (1..6).associateWith { r.mcq(it) } }
        val fresh = com.appsc.prep.data.DueMcqs.planMcqs(r.plan) { b, row -> books[b]!!.rows[row]?.map { it.id } ?: emptyList() }
        assertEquals(fresh.days.map { it.second }, r.planMcqs.days.map { it.second })
    }

    /** A topic's practice: the question and four options, then only "Correct!" or the answer. */
    @Test fun quiz() {
        val app = AppState(repo, ProgressStore(Mem()), AndroidPlatform(ctx))
        runBlocking { app.repo.mcq(1) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { QuizScreen(QuizSource("row", 1, 4), "all", "Section MCQs", nav) } } }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/oneliner/1_question.png")
        val q = runBlocking { app.repo.mcq(1).rows[4]!!.first() }
        rule.onAllNodesWithText(q.options[(q.answer + 1) % 4])[0].performClick()
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/oneliner/2_answered.png")
        assertEquals(0, rule.onAllNodesWithText("EXPLANATION").fetchSemanticsNodes().size)
        assertEquals(0, rule.onAllNodesWithText("Stuck? Show a hint").fetchSemanticsNodes().size)
    }
}
