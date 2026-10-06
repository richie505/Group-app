package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
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
            val notes = repo.fullBook(b)
            // every page of the notes is here, at the same place, so the 90-day plan and progress line up
            assertEquals(notes.rows.size, rev.rows.size)
            rev.rows.zip(notes.rows).forEach { (r, n) ->
                assertEquals(n.title, r.title)
                assertEquals(n.secs.map { it.title }, r.secs.map { it.title })
            }
            full += notes.rows.sumOf { r -> r.secs.sumOf { it.wordCount } }
            short += rev.rows.sumOf { r -> r.secs.sumOf { it.wordCount } }
        }
        assertTrue("revision is $short of $full words", short < full / 2)
    }

    @Test fun keyFactsStaySourcesGo() = runBlocking {
        val page = repo.book(2).rows[0].secs[1] // Indian Councils Acts 1861, 1892, 1909
        val t = text(page.blocks)
        for (fact in listOf("separate electorate for Muslims", "Dyarchy in provinces", "All-India Federation", "1892")) {
            assertTrue("$fact missing:\n$t", t.contains(fact))
        }
        assertTrue(t, page.blocks.any { it is TextBlock && it.kind == 'x' }) // exam angles kept
        // no source tags anywhere
        for (b in 1..6) {
            repo.book(b).rows.forEach { r ->
                r.secs.forEach { s ->
                    val x = text(s.blocks)
                    assertTrue("${s.title}: $x", !x.contains("[GK]") && !x.contains("Not in your sources"))
                }
            }
        }
    }

    /** Read-aloud reads the key facts: full forms, numbers and all, the same way as in the notes app. */
    @Test fun readAloudReadsKeyFacts() = runBlocking {
        repo.checkedAcronyms
        val page = repo.book(2).rows[0].secs[1]
        val spoken = com.appsc.prep.data.SpeechText.parts(page.title, page.blocks, 2, repo.book(2).rows[0].title).joinToString(" ") { it.second }
        assertTrue(spoken, spoken.contains("separate electorate for Muslims"))
        assertTrue(spoken, spoken.contains("Government of India Act 1935")) // GoI -> Government of India
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

    @Test fun keyFactsAndFullNotes() {
        val app = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(2); app.repo.mcq(2) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { ReaderScreen(2, 0, 1, nav) } } }
        rule.waitForIdle()
        rule.onNodeWithText("Key facts").assertExists()
        rule.onRoot().captureRoboImage("screenshots/revision_2_key_facts.png")
        rule.onNodeWithText("Full notes").performClick()
        rule.waitUntil(20_000) { rule.onAllNodesWithText("Beginning of representative institutions", substring = true).fetchSemanticsNodes().isNotEmpty() }
        rule.onRoot().captureRoboImage("screenshots/revision_3_full_notes.png")
    }
}
