package com.appsc.prep

import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.BooksScreen
import com.appsc.prep.ui.screens.DayScreen
import com.appsc.prep.ui.screens.Nav
import com.appsc.prep.ui.screens.PlanScreen
import com.appsc.prep.ui.screens.ProgressScreen
import com.appsc.prep.ui.screens.QuizRound
import com.appsc.prep.ui.screens.QuizScreen
import com.appsc.prep.ui.screens.QuizSource
import com.appsc.prep.ui.screens.ReaderScreen
import com.appsc.prep.ui.screens.SectionScreen
import com.appsc.prep.ui.screens.TodayScreen
import com.appsc.prep.ui.theme.PrepTheme
import com.github.takahirom.roborazzi.captureRoboImage
import kotlinx.coroutines.runBlocking
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class ScreenshotTest {
    @get:Rule
    val rule = createComposeRule()

    private val nav = object : Nav {
        override fun quiz(kind: String, book: Int, index: Int, mode: String, sub: Int) {}
        override fun day(n: Int) {}
        override fun row(book: Int, row: Int) {}
        override fun read(book: Int, row: Int, sec: Int) {}
        override fun book(id: Int) {}
        override fun back() {}
    }

    private fun shot(name: String, preload: Int? = null, content: @Composable () -> Unit) {
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val app = AppState(Repository(ctx), ProgressStore(ctx))
        if (preload != null) runBlocking { app.repo.book(preload); app.repo.mcq(preload) }
        rule.setContent {
            PrepTheme { CompositionLocalProvider(LocalApp provides app) { content() } }
        }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/$name.png")
    }

    @Test fun today() = shot("1_today") { TodayScreen(nav) }
    @Test fun plan() = shot("2_plan") { PlanScreen(nav) }
    @Test fun day1() = shot("3_day1") { DayScreen(1, nav) }
    @Test fun section() = shot("4_section", preload = 2) { SectionScreen(2, 0, nav) }
    @Test fun reader() = shot("5_reader", preload = 2) { ReaderScreen(2, 0, 0, nav) }
    @Test fun readerTable() = shot("6_reader_table", preload = 2) { ReaderScreen(2, 0, 1, nav) }
    @Test fun quiz() = shot("9_quiz") { QuizScreen(QuizSource("row", 2, 0), "new", "PYQ Practice", nav) }

    @Test fun quizExplained() {
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val repo = Repository(ctx)
        // first History row whose first question carries a CDI explanation
        val mcq = runBlocking { repo.mcq(1) }
        val row = mcq.rows.entries.sortedBy { it.key }.first { it.value.firstOrNull()?.explanation?.isNotBlank() == true }
        val q = row.value.first()
        shot("10_quiz_answered") { QuizScreen(QuizSource("row", 1, row.key), "all", "PYQ Practice", nav) }
        rule.onNodeWithText(q.options[q.answer]).performClick()
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/10_quiz_answered.png")
    }

    private fun roundShot(name: String, kind: Char, click: (com.appsc.prep.data.Question) -> String) {
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val repo = Repository(ctx)
        val q = runBlocking { repo.mcq(2) }.let { m -> (m.rows.values + m.units.values).flatten() }.first { it.kind == kind && (kind != 'u' || it.cancelled) }
        shot(name) { QuizRound("t", listOf(q), listOf(q), {}, {}) }
        rule.onNodeWithText(click(q)).performClick()
        rule.waitForIdle()
        if (kind == 'f') {
            rule.onNodeWithText("Didn't know").performClick()
            rule.waitForIdle()
        }
        rule.onRoot().captureRoboImage("screenshots/$name.png")
    }

    @Test fun flashcard() = roundShot("11_flashcard", 'f') { "Show answer" }
    @Test fun unscored() = roundShot("12_unscored", 'u') { it.options[0] }

    @Test fun books() = shot("7_notes") { BooksScreen(nav) }
    @Test fun progress() = shot("8_progress") { ProgressScreen(nav) }
}
