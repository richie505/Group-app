package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performScrollToNode
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

    @Test fun sameDaysAndPagesAllMapped() = runBlocking {
        assertTrue(repo.revision)
        assertEquals("APPSC Revision", repo.appName)
        for (b in 1..6) {
            val rev = repo.book(b)
            val notes = this@RevisionTest.notes.book(b)
            // every page of the notes is here, at the same place, so the 90-day plan and progress line up
            assertEquals(notes.rows.size, rev.rows.size)
            rev.rows.zip(notes.rows).forEach { (r, n) ->
                assertEquals(n.title, r.title)
                assertEquals(n.secs.map { it.title }, r.secs.map { it.title })
                // and every page is a mind map (tools/build_mindmap.py)
                r.secs.forEach { s -> assertTrue("${r.title} / ${s.title}", s.map.isNotEmpty()) }
            }
        }
    }

    private fun mapText(nodes: List<com.appsc.prep.data.MapNode>): String =
        nodes.joinToString("\n") { n -> n.runs.joinToString("") { it.text } + "\n" + mapText(n.children) }

    /** A page's mind map keeps its facts: every number of the notes page, its exam angles; source tags never. */
    @Test fun mapsKeepTheFacts() = runBlocking {
        val notesPage = notes.book(2).rows[0].secs.first { it.title.startsWith("Indian Councils Acts 1861") }
        val page = repo.book(2).rows[0].secs.first { it.title == notesPage.title }
        val m = mapText(page.map)
        val numbers = Regex("""\d+(?:\.\d+)?""")
        val inMap = numbers.findAll(m.replace(",", "")).map { it.value }.toSet()
        for (n in numbers.findAll(text(notesPage.blocks).replace(",", "")).map { it.value }.toSet()) {
            assertTrue("$n missing from the map:\n$m", n in inMap || n.length == 1)
        }
        assertTrue(m, m.contains("indirect election", ignoreCase = true) || m.contains("1861"))
        val topic = repo.book(2).rows[0].secs.joinToString("\n") { mapText(it.map) }
        assertTrue("Raja of Benaras", topic.contains("Raja of Benaras"))
        // exam angles stay, as their own nodes
        val withAngle = notes.book(2).rows[0].secs.count { s -> s.blocks.any { it is TextBlock && it.kind == 'x' } }
        val mapsWithAngle = repo.book(2).rows[0].secs.count { s -> mapText(s.map).isNotEmpty() && hasAngle(s.map) }
        assertEquals(withAngle, mapsWithAngle)
        // no source tags or gap lines anywhere
        for (b in 1..6) {
            repo.book(b).rows.forEach { r ->
                r.secs.forEach { s ->
                    val x = mapText(s.map)
                    assertTrue("${s.title}: $x", !x.contains("[GK]") && !x.contains("(CDI)") && !x.contains("Not in your sources"))
                }
            }
        }
    }

    private fun hasAngle(nodes: List<com.appsc.prep.data.MapNode>): Boolean = nodes.any { it.kind == 'x' || hasAngle(it.children) }

    /** Read-aloud reads the key facts: full forms, numbers and all, the same way as in the notes app. */
    @Test fun readAloudReadsKeyFacts() = runBlocking {
        repo.checkedAcronyms
        val page = repo.book(2).rows[0].secs.first { it.title.startsWith("Indian Councils Acts 1861") }
        val spoken = com.appsc.prep.data.SpeechText.parts(page.title, page.blocks, 2, repo.book(2).rows[0].title).joinToString(" ") { it.second }
        assertTrue(spoken, spoken.contains("six months") || spoken.contains("6 months"))
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

    /** Mind maps (pilot: the Preamble topic, book 2 row 4): every fact of the page on the map. */
    private fun mindMap(sec: Int, scrollTo: String? = null) {
        val tag = System.getProperty("sample.tag") ?: "after"
        val app = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(2); app.repo.mcq(2) }
        if (tag == "after") assertTrue(runBlocking { app.repo.book(2).rows[4].secs[sec].map.isNotEmpty() })
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { ReaderScreen(2, 4, sec, nav) } } }
        rule.waitForIdle()
        if (scrollTo != null && tag == "after") {
            rule.onNode(androidx.compose.ui.test.hasScrollToNodeAction())
                .performScrollToNode(androidx.compose.ui.test.hasText(scrollTo, substring = true))
            rule.waitForIdle()
        }
        rule.onRoot().captureRoboImage("screenshots/sample/${tag}_mindmap_$sec${if (scrollTo != null) "b" else ""}.png")
    }

    @Test fun mindMapMaking() = mindMap(0)
    @Test fun mindMapMakingMore() = mindMap(0, "UDHR")
    @Test fun mindMapText() = mindMap(1)
    @Test fun mindMapKeywords() = mindMap(2)
    @Test fun mindMapCases() = mindMap(4)
}
