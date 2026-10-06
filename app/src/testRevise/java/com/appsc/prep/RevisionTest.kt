package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.data.TableBlock
import com.appsc.prep.data.TextBlock
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.platform.PrefsStorage
import com.appsc.prep.ui.screens.Nav
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.ReaderScreen
import com.appsc.prep.ui.screens.TodayScreen
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

/** APPSC Revision: the exam-ready condensed notes (tools/build_revision.py), day-wise like the notes app. */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class RevisionTest {
    @get:Rule
    val rule = createComposeRule()

    private val ctx get() = ApplicationProvider.getApplicationContext<android.content.Context>()
    private val repo by lazy { Repository { ctx.assets.open(it) } }

    /** The same assets read as the notes app does (no edition.json): the full notes, to compare with. */
    private val notes by lazy {
        Repository { name -> if (name == "edition.json") throw java.io.FileNotFoundException(name) else ctx.assets.open(name) }
    }

    private val nav = object : Nav {
        override fun quiz(kind: String, book: Int, index: Int, mode: String, sub: Int) {}
        override fun day(n: Int) {}
        override fun row(book: Int, row: Int) {}
        override fun read(book: Int, row: Int, sec: Int) {}
        override fun book(id: Int) {}
        override fun back() {}
    }

    private fun text(blocks: List<com.appsc.prep.data.Block>) = blocks.joinToString("\n") { b ->
        when (b) {
            is TextBlock -> b.runs.joinToString("") { it.text }
            is TableBlock -> (listOf(b.head) + b.rows).joinToString("\n") { r -> r.joinToString(" | ") { c -> c.joinToString("") { it.text } } }
        }
    }

    @Test fun sameDaysAndPagesShorterText() = runBlocking {
        assertTrue(repo.revision)
        assertEquals("APPSC Revision", repo.appName)
        var full = 0
        var short = 0
        for (b in 1..6) {
            val rev = repo.book(b)
            val notes = this@RevisionTest.notes.book(b)
            // every page of the notes is here, at the same place, so the 90-day plan and progress line up
            assertEquals(notes.rows.size, rev.rows.size)
            rev.rows.zip(notes.rows).forEach { (r, n) ->
                assertEquals(n.title, r.title)
                assertEquals(n.secs.map { it.title }, r.secs.map { it.title })
            }
            full += notes.rows.sumOf { r -> r.secs.sumOf { it.wordCount } }
            short += rev.rows.sumOf { r -> r.secs.sumOf { it.wordCount } }
        }
        assertTrue("revision is $short of $full words", short < full * 6 / 10)
    }

    /** A page's revision facts are what its MCQs test, answer in bold, each fact once; source tags never. */
    @Test fun factsFromTheMcqs() = runBlocking {
        val page = repo.book(2).rows[0].secs[1] // Indian Councils Acts 1861, 1892, 1909
        val t = text(page.blocks)
        for (fact in listOf("indirect election", "six months", "Raja of Benaras", "ordinance")) {
            assertTrue("$fact missing:\n$t", t.contains(fact, ignoreCase = true))
        }
        assertTrue(t, page.blocks.any { it is TextBlock && it.kind == 'x' }) // exam angles first
        assertTrue(t, page.blocks.any { b -> b is TextBlock && b.runs.any { it.bold } }) // answers in bold
        // no filler from the explanations, no source tags, no repeated sentence
        for (b in 1..6) {
            repo.book(b).rows.forEach { r ->
                r.secs.forEach { s ->
                    val x = text(s.blocks)
                    assertTrue("${s.title}: $x", !x.contains("[GK]") && !x.contains("Not in your sources"))
                    assertTrue("${s.title}: $x", !Regex("""(?m)^Statements? [\d, and]+ (is|are) (correct|incorrect)""").containsMatchIn(x))
                    val lines = s.blocks.filterIsInstance<TextBlock>().map { tb -> tb.runs.joinToString("") { it.text } }
                    assertEquals(s.title, lines.size, lines.toSet().size)
                }
            }
        }
    }

    /** Read-aloud reads the key facts: full forms, numbers and all, the same way as in the notes app. */
    @Test fun readAloudReadsKeyFacts() = runBlocking {
        repo.checkedAcronyms
        val page = repo.book(2).rows[0].secs[1]
        val spoken = com.appsc.prep.data.SpeechText.parts(page.title, page.blocks, 2, repo.book(2).rows[0].title).joinToString(" ") { it.second }
        assertTrue(spoken, spoken.contains("six months"))
        assertTrue(spoken, spoken.contains("Indian Councils Act"))
        assertTrue(spoken, !spoken.contains("[GK]") && !spoken.contains("CDI"))
    }

    @Test fun screens() {
        val app = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(2); app.repo.mcq(2) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { TodayScreen(nav) } } }
        rule.waitForIdle()
        rule.onAllNodesWithText("APPSC Revision").fetchSemanticsNodes().let { assertEquals(1, it.size) }
        rule.onRoot().captureRoboImage("screenshots/revision_1_today.png")
    }

    @Test fun revisionPage() {
        val app = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(2); app.repo.mcq(2) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { ReaderScreen(2, 0, 1, nav) } } }
        rule.waitForIdle()
        rule.onAllNodesWithText("Full notes").fetchSemanticsNodes().let { assertEquals(0, it.size) } // standalone
        rule.onRoot().captureRoboImage("screenshots/revision_2_page.png")
    }
}
