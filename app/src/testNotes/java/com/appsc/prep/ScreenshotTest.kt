package com.appsc.prep

import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.longClick
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performScrollToNode
import androidx.compose.ui.test.performTouchInput
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.platform.PrefsStorage
import com.appsc.prep.platform.ReadAloud
import com.appsc.prep.ui.components.SpeechPage
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
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import androidx.compose.ui.test.onAllNodesWithContentDescription
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
        ReadAloud.init(ctx).stop() // each screen starts without read-aloud
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
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
    /**
     * Stepped clock: after the Google and word-meaning tests in the same run, this screen never reported idle
     * (an order-dependent Robolectric hang that does not occur alone), so it is drawn after 3 s instead of waiting.
     */
    @Test fun section() {
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(2); app.repo.mcq(2) }
        rule.mainClock.autoAdvance = false
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { SectionScreen(2, 0, nav) } } }
        rule.mainClock.advanceTimeBy(3000)
        rule.onNodeWithText("Polity, Society & IR").assertExists()
        rule.onRoot().captureRoboImage("screenshots/4_section.png")
        rule.mainClock.autoAdvance = true
    }
    @Test fun reader() = shot("5_reader", preload = 2) { ReaderScreen(2, 0, 0, nav) }
    @Test fun readerTable() = shot("6_reader_table", preload = 2) { ReaderScreen(2, 0, 1, nav) }

    /** Read aloud: the Listen button opens the player bar, speaks the page and highlights the paragraph. */
    @Test fun readerListen() {
        shot("15_listen", preload = 2) { ReaderScreen(2, 106, 0, nav) }
        rule.onNodeWithContentDescription("Listen").performClick()
        rule.waitForIdle()
        org.robolectric.shadows.ShadowLooper.idleMainLooper()
        rule.waitForIdle()
        rule.onNodeWithContentDescription("Pause").assertExists()
        rule.onRoot().captureRoboImage("screenshots/15_listen.png")
        assertEquals("2:106:0", ReadAloud.playback.value.pageId)
        assertTrue(ReadAloud.playback.value.playing)
        ReadAloud.stop()
    }

    /**
     * Long-press a word in the notes, tap Meaning: the dictionary card shows its meaning and notes pages.
     * Android 8.1: the selection magnifier of Android 9+ needs a real screen surface, which Robolectric lacks.
     */
    @Config(sdk = [27])
    @Test fun meaningOfASelectedWord() {
        shot("16_meaning", preload = 2) { ReaderScreen(2, 0, 0, nav) }
        rule.onAllNodesWithText("dyarchy", substring = true)[1].performTouchInput { longClick(centerLeft + androidx.compose.ui.geometry.Offset(width * 0.55f, 0f)) }
        rule.waitForIdle()
        rule.onNodeWithText("Meaning").performClick()
        rule.waitUntil(10_000) { rule.onAllNodesWithText("MEANING").fetchSemanticsNodes().isNotEmpty() }
        rule.waitUntil(20_000) { rule.onAllNodesWithText("IN YOUR NOTES").fetchSemanticsNodes().isNotEmpty() }
        rule.onRoot().captureRoboImage("screenshots/16_meaning.png")
    }

    /** 2.18: POCSO / JJ Act read once (merged into this section), short forms with full forms, links to kept facts. */
    @Test fun restructuredPage() {
        shot("20_section_merged", preload = 2) { SectionScreen(2, 137, nav) }
    }

    @Test fun fullFormsAndCoveredIn() {
        shot("21_full_forms", preload = 2) { ReaderScreen(2, 138, 3, nav) }
        rule.onNode(androidx.compose.ui.test.hasScrollToNodeAction()).performScrollToNode(androidx.compose.ui.test.hasText("ALSO COVERED IN"))
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/22_covered_in.png")
    }

    /** "Not in your sources": Search Google / Add to notes, and the reader's own note under the line. */
    @Test fun ownNoteUnderGap() {
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val (b, r, sx) = runBlocking {
            val repo = Repository { ctx.assets.open(it) }
            val bk = repo.book(2)
            val row = bk.rows.first { it.title.startsWith("Juvenile Justice Act 2015, POCSO") }
            Triple(2, row.index, row.secs.indexOfFirst { s -> s.title.startsWith("NCRB data") })
        }
        val gapIndex = runBlocking { Repository { ctx.assets.open(it) }.book(b).rows[r].secs[sx].blocks.indexOfFirst { com.appsc.prep.data.UserNotes.isGap(it) } }
        ProgressStore(PrefsStorage(ctx)).setAdded(com.appsc.prep.data.UserNotes.key("$b:$r:$sx", gapIndex), "NCRB 2022: Madhya Pradesh, Maharashtra and Uttar Pradesh reported the most crimes against children.")
        shot("23_own_note", preload = 2) { ReaderScreen(b, r, sx, nav) }
        rule.onNode(androidx.compose.ui.test.hasScrollToNodeAction()).performScrollToNode(androidx.compose.ui.test.hasText("Edit my note"))
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/23_own_note.png")
        // the text field's blinking cursor never lets Compose go idle: step the clock instead
        rule.mainClock.autoAdvance = false
        rule.onNodeWithText("Edit my note").performClick()
        rule.mainClock.advanceTimeBy(500)
        rule.onRoot().captureRoboImage("screenshots/24_add_note_dialog.png")
        rule.mainClock.autoAdvance = true
    }

    /** Google's copy menu does not show inside the app, so the page's paragraphs are listed to tick. */
    @Test fun pickTextFromGoogle() {
        var added = ""
        val paras = listOf(
            "Madhya Pradesh, Maharashtra, and Uttar Pradesh record the highest total numbers of crimes against children.",
            "Top States for Crimes Against Children",
            "Child marriage cases under the PCMA are led by Karnataka, Assam and West Bengal.",
        )
        shot("25_pick_text") { com.appsc.prep.ui.components.PickText(paras, preselect = 0, onAdd = { added = it }) {} }
        rule.onNodeWithText(paras[2]).performClick()
        rule.onNodeWithText("Add (2)").performClick()
        assertEquals(paras[0] + "\n" + paras[2], added)
    }

    /** Every notes page ends with its key terms; tapping one opens its meaning. */
    @Test fun keyTermsOnAPage() {
        shot("17_key_terms", preload = 2) { ReaderScreen(2, 0, 0, nav) }
        rule.onNode(androidx.compose.ui.test.hasScrollToNodeAction()).performScrollToNode(androidx.compose.ui.test.hasText("KEY TERMS"))
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/17_key_terms.png")
        rule.onNodeWithText("dyarchy").performClick()
        rule.waitUntil(20_000) { rule.onAllNodesWithText("IN INDIAN CONTEXT").fetchSemanticsNodes().isNotEmpty() }
        rule.onRoot().captureRoboImage("screenshots/18_key_term_meaning.png")
        // Google inside the app
        rule.onNodeWithText("Search on Google").performScrollTo().performClick()
        rule.waitForIdle()
        rule.onAllNodesWithText("Google · dyarchy")[0].assertExists()
        rule.onRoot().captureRoboImage("screenshots/19_google.png")
        // close Google: its web page would otherwise keep the next test from ever going idle
        rule.onAllNodesWithContentDescription("Close")[0].performClick()
        rule.waitForIdle()
        assertEquals("https://www.google.com/search?hl=en&gl=in&q=84th+Amendment", com.appsc.prep.ui.components.googleUrl("84th Amendment"))
    }

    /** Reading page A, then opening page B by hand: B is read, and the screen stays on B. */
    @Test fun readAloudFollowsTheOpenedPage() {
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        ReadAloud.init(ctx).play(SpeechPage("2:106:0", "A", listOf("one", "two")), 0, 1f) { null }
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(2); app.repo.mcq(2) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { ReaderScreen(2, 0, 0, nav) } } }
        rule.waitForIdle()
        assertEquals("2:0:0", ReadAloud.playback.value.pageId)
        // still on page B, not taken back to A
        rule.onAllNodesWithText("Changing structure and urban families", substring = true).assertCountEquals(0)
        ReadAloud.stop()
    }
    @Test fun quiz() = shot("9_quiz") { QuizScreen(QuizSource("row", 2, 0), "new", "MCQ Practice", nav) }

    @Test fun quizExplained() {
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val repo = Repository { ctx.assets.open(it) }
        // first History row whose first question carries an explanation
        val mcq = runBlocking { repo.mcq(1) }
        val row = mcq.rows.entries.sortedBy { it.key }.first { it.value.firstOrNull()?.explanation?.isNotBlank() == true }
        val q = row.value.first()
        shot("10_quiz_answered", preload = 1) { QuizScreen(QuizSource("row", 1, row.key), "all", "MCQ Practice", nav) }
        rule.onNodeWithText(q.options[q.answer]).performClick()
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/10_quiz_answered.png")
    }

    /** A Polity statements question: hint opened before answering, then a wrong pick with its technique note. */
    @Test fun hintAndTechnique() {
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val q = runBlocking { Repository { ctx.assets.open(it) }.mcq(2) }.rows.values.flatten().first {
            it.kind == 's' && com.appsc.prep.data.Techniques.kind(it) == com.appsc.prep.data.Techniques.Kind.STATEMENTS &&
                it.stem.length < 420 && com.appsc.prep.data.Techniques.hints(it).size >= 3
        }
        shot("13_hint") { QuizRound("h", listOf(q, q), listOf(q), {}, {}) }
        rule.onNodeWithText("Stuck? Show a hint").performClick()
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/13_hint.png")
        rule.onNodeWithText(q.options[(q.answer + 1) % q.options.size]).performClick()
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/14_wrong_technique.png")
    }


    @Test fun books() = shot("7_notes") { BooksScreen(nav) }
    @Test fun progress() {
        shot("8_progress") { ProgressScreen(nav) }
        // the backup card at the end
        rule.onNode(androidx.compose.ui.test.hasScrollToNodeAction()).performScrollToNode(androidx.compose.ui.test.hasText("Back up now"))
        rule.waitForIdle()
        rule.onAllNodesWithText("Last backup: never").fetchSemanticsNodes().let { assertEquals(1, it.size) }
        rule.onRoot().captureRoboImage("screenshots/26_backup.png")
    }
}
