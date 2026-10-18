package com.appsc.prep

import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.unit.dp
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollToNode
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.platform.PrefsStorage
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.ReaderScreen
import com.appsc.prep.ui.screens.SectionScreen
import com.appsc.prep.ui.theme.PrepTheme
import com.github.takahirom.roborazzi.captureRoboImage
import kotlinx.coroutines.runBlocking
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** Sample screenshots of one topic (-Psample.tag=before|after). Not a pass/fail test. */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class SampleShotsTest {
    @get:Rule val rule = createComposeRule()
    private val nav = object : com.appsc.prep.ui.screens.Nav {
        override fun quiz(kind: String, book: Int, index: Int, mode: String, sub: Int) {}
        override fun day(n: Int) {}
        override fun row(book: Int, row: Int) {}
        override fun read(book: Int, row: Int, sec: Int) {}
        override fun book(id: Int) {}
        override fun back() {}
    }

    private fun shot(name: String, book: Int = 2, content: @androidx.compose.runtime.Composable () -> Unit) {
        val tag = System.getProperty("sample.tag") ?: return
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(book); app.repo.mcq(book) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { content() } } }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/sample/${tag}_$name.png")
    }

    @Test fun section() = shot("0_topic") { SectionScreen(2, 106, nav) }
    @Test fun page1() = shot("1_page") { ReaderScreen(2, 106, 1, nav) }
    @Test fun page2() = shot("2_page") { ReaderScreen(2, 106, 2, nav) }
    @Test fun page5() = shot("3_page") { ReaderScreen(2, 106, 5, nav) }
    @Test fun marriage() = shot("4_marriage_topic") { SectionScreen(2, 107, nav) }
    @Test fun marriage1() = shot("5_marriage_page") { ReaderScreen(2, 107, 0, nav) }
    @Test fun regionAp() = shot("6_regionalism_ap_topic") { SectionScreen(2, 120, nav) }
    @Test fun regionAp2() = shot("7_regionalism_ap_page") { ReaderScreen(2, 120, 2, nav) }

    // 2.56: one topic per other book
    @Test fun history() = shot("b1_topic", 1) { SectionScreen(1, 10, nav) }
    @Test fun history1() = shot("b1_page", 1) { ReaderScreen(1, 10, 1, nav) }
    @Test fun economy() = shot("b3_topic", 3) { SectionScreen(3, 80, nav) }
    @Test fun economy1() = shot("b3_page", 3) { ReaderScreen(3, 80, 1, nav) }
    @Test fun geography() = shot("b4_topic", 4) { SectionScreen(4, 36, nav) }
    @Test fun geography1() = shot("b4_page", 4) { ReaderScreen(4, 36, 1, nav) }
    @Test fun science() = shot("b5_topic", 5) { SectionScreen(5, 42, nav) }
    @Test fun science1() = shot("b5_page", 5) { ReaderScreen(5, 42, 1, nav) }
    @Test fun current() = shot("b6_topic", 6) { SectionScreen(6, 14, nav) }
    @Test fun current1() = shot("b6_page", 6) { ReaderScreen(6, 14, 1, nav) }
    @Test fun polity() = shot("b2_polity_topic") { SectionScreen(2, 0, nav) }
    @Test fun polity1() = shot("b2_polity_page") { ReaderScreen(2, 0, 1, nav) }
    @Test fun polity2() = shot("b2_cm_topic") { SectionScreen(2, 40, nav) }
    @Test fun polity3() = shot("b2_cm_page") { ReaderScreen(2, 40, 2, nav) }

    /** Structured explanations (Solution + Additional Information): before = the old one-line explanation. */
    private fun explained(n: Int, wrong: Boolean) {
        val tag = System.getProperty("sample.tag") ?: return
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val q0 = runBlocking { Repository { ctx.assets.open(it) }.mcq(1) }.rows[5]!!.filter { it.solution.isNotEmpty() }[n]
        val q = if (tag == "before") q0.copy(solution = emptyList(), extra = emptyList()) else q0
        val pick = if (wrong) (q.answer + 1) % q.options.size else q.answer
        shot("expl${n}_${if (wrong) "wrong" else "right"}", 1) { com.appsc.prep.ui.screens.QuizRound("e$n", listOf(q), listOf(q), {}, {}) }
        rule.onNodeWithText(q.options[pick]).performClick()
        rule.waitForIdle()
        rule.onNode(androidx.compose.ui.test.hasScrollToNodeAction()).performScrollToNode(
            androidx.compose.ui.test.hasText(if (tag == "before") "EXPLANATION" else "SOLUTION"))
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/sample/${tag}_expl${n}_${if (wrong) "wrong" else "right"}.png")
        if (tag == "after") {
            rule.onNode(androidx.compose.ui.test.hasScrollToNodeAction()).performScrollToNode(androidx.compose.ui.test.hasText("ADDITIONAL INFORMATION"))
            rule.waitForIdle()
            rule.onRoot().captureRoboImage("screenshots/sample/${tag}_expl${n}_${if (wrong) "wrong" else "right"}_more.png")
        }
    }
    @Test fun expl0() = explained(0, true)
    @Test fun expl1() = explained(1, false)
    @Test fun expl4() = explained(4, true)

    /** MCQ practice sets (2.59): the same answers drawn on 2.58 (before) and 2.59 (after). */
    private fun practice(name: String, find: List<String>, content: @androidx.compose.runtime.Composable () -> Unit) {
        val tag = System.getProperty("sample.tag") ?: return
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        val ids = runBlocking { app.repo.book(2); app.repo.mcq(2).rows[106].orEmpty().map { it.id } }
        ids.take(12).forEachIndexed { i, id -> app.store.recordAnswer(id, i % 3 != 0) } // 8 right, 4 wrong
        ids.drop(12).take(3).forEach { app.store.markSeen(it) } // answer seen first
        rule.mainClock.autoAdvance = false
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { content() } } }
        rule.mainClock.advanceTimeBy(3000)
        val target = find.first { t -> rule.onAllNodes(androidx.compose.ui.test.hasText(t)).fetchSemanticsNodes().isNotEmpty() ||
            runCatching { rule.onNode(androidx.compose.ui.test.hasScrollToNodeAction()).performScrollToNode(androidx.compose.ui.test.hasText(t)) }.isSuccess }
        rule.onNode(androidx.compose.ui.test.hasScrollToNodeAction()).performScrollToNode(androidx.compose.ui.test.hasText(target))
        rule.mainClock.advanceTimeBy(1000)
        rule.onRoot().captureRoboImage("screenshots/sample/${tag}_$name.png")
        rule.mainClock.autoAdvance = true
    }

    /** The section's MCQ card alone (the whole section screen does not settle in Robolectric). */
    @Test fun practiceSection() {
        val tag = System.getProperty("sample.tag") ?: return
        rule.setContent {
            PrepTheme {
                androidx.compose.foundation.layout.Box(androidx.compose.ui.Modifier.padding(16.dp)) {
                    com.appsc.prep.ui.components.PracticeCard(
                        "All section MCQs", "88 questions · all in one go", Triple(84, 75, 88), onStart = {},
                        sets = com.appsc.prep.ui.components.PracticeSets(4, 9, 88, practice = 13),
                    )
                }
            }
        }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/sample/${tag}_p1_section_card.png")
    }
    @Test fun practiceProgress() = practice("p2_progress", listOf("MCQs to practise", "Study activity", "STUDY ACTIVITY")) {
        com.appsc.prep.ui.screens.ProgressScreen(nav)
    }
}
