package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.platform.PrefsStorage
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.BooksScreen
import com.appsc.prep.ui.screens.DayScreen
import com.appsc.prep.ui.screens.ExamSubjectScreen
import com.appsc.prep.ui.screens.Nav
import com.appsc.prep.ui.screens.PlanScreen
import com.appsc.prep.ui.screens.ProgressScreen
import com.appsc.prep.ui.screens.ReaderScreen
import com.appsc.prep.ui.screens.SavedScreen
import com.appsc.prep.ui.screens.SectionScreen
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

/** APPSC Reader: APPSC Complete's full notes for reading only (tools/reader_build.py). */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class ReaderTest {
    @get:Rule val rule = createComposeRule()
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

    private fun shot(name: String, app: AppState = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx)), content: @androidx.compose.runtime.Composable () -> Unit): AppState {
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { content() } } }
        rule.waitForIdle()
        repeat(4) { rule.mainClock.advanceTimeBy(1500); rule.waitForIdle(); Thread.sleep(300) }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/reader/$name.png")
        return app
    }

    @Test fun itIsTheReaderEdition() {
        assertEquals("APPSC Reader", repo.appName)
        assertTrue(repo.reader && !repo.complete && !repo.revision)
    }

    /** All 927 topics, only their full notes (no one-page summaries), each topic's pages in headed groups. */
    @Test fun everyTopicIsItsFullNotesInGroups() = runBlocking {
        assertEquals(927, repo.index.sumOf { it.rows.size })
        var pages = 0
        for (b in 1..6) {
            val bk = repo.book(b)
            assertEquals(repo.index[b - 1].rows.size, bk.rows.size)
            bk.rows.forEachIndexed { ri, r ->
                assertEquals("$b:$ri", repo.index[b - 1].rows[ri].subsectionCount, r.secs.size)
                assertTrue("$b:$ri", r.secs.isNotEmpty() && r.secs.none { it.full || it.empty })
                assertTrue("$b:$ri", r.secs.none { "Full notes" in it.badges })
                // every page has its group, and a group's pages are together
                assertTrue("$b:$ri", r.secs.all { it.group.isNotEmpty() })
                val runs = r.secs.map { it.group }.fold(mutableListOf<String>()) { a, g -> if (a.lastOrNull() != g) a += g; a }
                assertEquals("$b:$ri groups split", runs.toSet().size, runs.size)
                assertTrue("$b:$ri", r.secs.all { s -> s.blocks.isNotEmpty() })
            }
            pages += bk.rows.sumOf { it.secs.size }
            assertTrue(repo.mcq(b).rows.isEmpty())
            assertTrue(repo.index[b - 1].rows.all { it.questionCount == 0 })
        }
        assertTrue(pages in 10000..10676)
        // the plan reads every topic once
        val study = repo.plan.days.filter { it.type == "study" }.flatMap { d -> d.rows.map { it.book to it.row } }
        assertEquals(927, study.toSet().size)
    }

    /** 3.19's page ids (APPSC Complete's) move to the new pages; read marks and markers go with them. */
    @Test fun readMarksAndMarkersMoveToTheNewPages() {
        val moves = repo.idMoves
        assertEquals("reader-2", moves.version)
        val store = ProgressStore(PrefsStorage(ctx))
        // APPSC Complete's 1:0:9 is topic 1's first full-notes page
        store.toggleDone("1:0:9")
        store.addMark("1:0:9", "Sohgaura", 0, "Oldest", "Sources")
        store.addMark("1:0:0", "gone", 0, "Literary sources", "Sources")
        store.migrate(moves)
        val to = moves.map["1:0:9"]!!
        assertTrue(store.isDone(to))
        assertEquals(listOf(to), store.marks.map { it.page })
    }

    /** Simple meanings: the harder words of the notes, in simple Indian English, found in any form. */
    @Test fun simpleMeanings() {
        val d = repo.dictionary
        assertTrue(d.simple.size > 9000)
        assertEquals("accord", d.simpleMeaning("accords")?.first)
        assertTrue(d.lookup("statutory")!!.simple!!.contains("law"))
        val words = d.hardWords("The Basel accords set statutory capital norms for banks.")
        assertTrue(words.toString(), "accord" in words && "statutory" in words)
    }

    /** Markers: added, recoloured, taken off, and carried in a backup. */
    @Test fun markersAreKeptAndBackedUp() {
        val store = ProgressStore(PrefsStorage(ctx))
        store.addMark("4:0:1", "4.6 billion years", 0, "Basics", "Universe")
        store.addMark("4:0:1", "4.6 billion years", 1, "Basics", "Universe")
        store.addMark("4:0:1", "IAU", 3, "Basics", "Universe")
        assertEquals(2, store.marksOn("4:0:1").size)
        assertEquals(1, store.marksOn("4:0:1").first { it.text == "4.6 billion years" }.color)
        val backup = store.backup()
        store.clearMarks("4:0:1", "IAU")
        assertEquals(1, store.marks.size)
        store.restore(backup, repo.idMoves)
        assertEquals(setOf("4.6 billion years", "IAU"), store.marks.map { it.text }.toSet())
        val again = ProgressStore(PrefsStorage(ctx))
        assertEquals(store.marks.size, again.marks.size)
    }

    private fun marked(): AppState {
        val app = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        app.store.addMark("4:0:0", "Hottest = Venus, not Mercury", 0, "Basics & units", "Universe")
        app.store.addMark("4:0:0", "13.8 billion years", 1, "Basics & units", "Universe")
        app.store.addMark("4:0:0", "failed to clear its orbit", 2, "Basics & units", "Universe")
        app.store.addMark("4:0:0", "parsec = 3.26 light years", 3, "Basics & units", "Universe")
        return app
    }

    @Test fun shotPageWithMarkers() { shot("6b_page_marked", marked()) { ReaderScreen(4, 0, 0, nav) } }
    @Test fun shotMarkers() {
        val app = marked()
        shot("8b_markers", app) {
            SavedScreen(nav)
        }
        rule.onNodeWithText("Markers (4)").performClick()
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/reader/8b_markers.png")
    }

    @Test fun shotMeaning() {
        shot("6c_meaning") { ReaderScreen(3, 0, 0, nav); com.appsc.prep.ui.components.MeaningSheet("accords", { _, _, _ -> }) {} }
        com.github.takahirom.roborazzi.captureScreenRoboImage("screenshots/reader/6c_meaning.png")
    }

    @Test fun shotToday() { shot("1_today") { TodayScreen(nav) } }
    @Test fun shotPlan() { shot("2_plan") { PlanScreen(nav) } }
    @Test fun shotNotes() { shot("3_notes") { BooksScreen(nav) } }
    @Test fun shotSubject() { shot("4_subject") { ExamSubjectScreen(0, 0, nav) } }
    @Test fun shotTopic() { shot("5_topic") { SectionScreen(1, 0, nav) } }
    @Test fun shotTopicGeo() { shot("5b_topic") { SectionScreen(4, 0, nav) } }
    @Test fun shotPage() { shot("6_page") { ReaderScreen(4, 0, 1, nav) } }
    @Test fun shotProgress() { shot("7_progress") { ProgressScreen(nav) } }
    @Test fun shotSaved() { shot("8_saved") { SavedScreen(nav) } }
    @Test fun shotDay() { shot("9_day") { DayScreen(1, nav) } }
}
