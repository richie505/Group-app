package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.hasScrollToNodeAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performScrollToNode
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.platform.PrefsStorage
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.BooksScreen
import com.appsc.prep.ui.screens.ExamSubjectScreen
import com.appsc.prep.ui.screens.Nav
import com.appsc.prep.ui.screens.ReaderScreen
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

/** APPSC Complete: the three apps' notes in one, the Notes tab split into Group 1 and Group 2. */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class CompleteTest {
    @get:Rule val rule = createComposeRule()
    private val ctx get() = ApplicationProvider.getApplicationContext<android.content.Context>()
    private val nav = object : Nav {
        override fun quiz(kind: String, book: Int, index: Int, mode: String, sub: Int) {}
        override fun day(n: Int) {}
        override fun row(book: Int, row: Int) {}
        override fun read(book: Int, row: Int, sec: Int) {}
        override fun book(id: Int) {}
        override fun back() {}
    }

    private fun show(name: String, content: @androidx.compose.runtime.Composable () -> Unit): AppState {
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(2); app.repo.mcq(2) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { content() } } }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/complete/$name.png")
        return app
    }

    @Test fun edition() {
        val repo = Repository { ctx.assets.open(it) }
        assertEquals("APPSC Complete", repo.appName)
        assertTrue(!repo.revision)
        assertEquals(listOf("Group 1", "Group 2"), repo.exams.map { it.title })
    }

    @Test fun notesTabGroup1AndGroup2() {
        show("1_notes_group1") { BooksScreen(nav) }
        rule.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("Indian Constitution"))
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/complete/2_notes_group2.png")
    }

    @Test fun group2Subject() {
        val repo = Repository { ctx.assets.open(it) }
        val s = repo.exams[1].subjects.indexOfFirst { it.title == "Indian Constitution" }
        show("3_group2_constitution") { ExamSubjectScreen(1, s, nav) }
    }

    /** A merged page: ROCKET facts first, Prep's extra facts after, a disagreement kept as "Sources differ". */
    @Test fun mergedPage() {
        val repo = Repository { ctx.assets.open(it) }
        val secs = runBlocking { repo.book(2).rows[4].secs }
        val i = secs.indexOfFirst { it.title.contains("part of the Constitution") }
        show("4_merged_preamble_cases") { ReaderScreen(2, 4, i, nav) }
        rule.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("Sources differ", substring = true))
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/complete/5_merged_sources_differ.png")
    }

    /** Current affairs: Prep's topics, the CA app's news pages by period, Prep's facts folded in. */
    @Test fun currentAffairsTopics() {
        val repo = Repository { ctx.assets.open(it) }
        val s = repo.exams[0].subjects.indexOfFirst { it.title == "Current Affairs" }
        show("6_ca_group1_topics") { ExamSubjectScreen(0, s, nav) }
    }

    @Test fun currentAffairsSection() {
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(6); app.repo.mcq(6) }
        rule.mainClock.autoAdvance = false
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { com.appsc.prep.ui.screens.SectionScreen(6, 32, nav) } } }
        rule.mainClock.advanceTimeBy(3000)
        rule.onRoot().captureRoboImage("screenshots/complete/7_ca_section_sep_oct.png")
        rule.mainClock.autoAdvance = true
    }

    private fun caPage(name: String, row: Int, sec: Int, scrollTo: String?) {
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(6); app.repo.mcq(6) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { ReaderScreen(6, row, sec, nav) } } }
        rule.waitForIdle()
        if (scrollTo != null) {
            rule.onNode(hasScrollToNodeAction()).performScrollToNode(hasText(scrollTo, substring = true))
            rule.waitForIdle()
        }
        rule.onRoot().captureRoboImage("screenshots/complete/$name.png")
    }

    @Test fun caBudgetPage() = caPage("8_ca_budget_with_prep_facts", 35, 0, "16.96")
    @Test fun caUpiPage() = caPage("9_ca_upi_sources_differ", 33, 9, "Sources differ")
}
