package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.hasScrollAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollToNode
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.platform.PrefsStorage
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.Nav
import com.appsc.prep.ui.screens.QuizScreen
import com.appsc.prep.ui.screens.QuizSource
import com.appsc.prep.ui.screens.SectionScreen
import com.appsc.prep.ui.theme.PrepTheme
import com.github.takahirom.roborazzi.captureRoboImage
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** "Finished · review": the finished MCQs of a section / subsection with their keys and explanations. */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class ReviewShotsTest {
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

    /** Book 4 row 10: subsection 3 all finished (two wrong), subsection 0 half done. */
    private fun app(): AppState {
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        val mcq = runBlocking { app.repo.book(4); app.repo.mcq(4) }
        mcq.subQuestions(10, 3).forEachIndexed { i, q ->
            if (i == 2) app.store.markSeen(q.id, viewed = true) else app.store.recordAnswer(q.id, i % 4 != 1)
            if (i != 2 && q.options.isNotEmpty() && q.answer >= 0) app.store.recordPick(q.id, if (i % 4 == 1) (q.answer + 1) % q.options.size else q.answer)
        }
        mcq.subQuestions(10, 0).take(12).forEach { app.store.recordAnswer(it.id, true) }
        return app
    }

    private fun show(app: AppState, content: @androidx.compose.runtime.Composable () -> Unit) {
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { content() } } }
        rule.waitForIdle()
        rule.mainClock.advanceTimeBy(1500)
        rule.waitForIdle()
    }

    @Test fun sectionShowsFinishedReview() {
        show(app()) { SectionScreen(4, 10, nav) }
        rule.onRoot().captureRoboImage("screenshots/review/1_section_subsections.png")
        rule.onNode(hasScrollAction()).performScrollToNode(hasText("answers & explanations", substring = true))
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/review/2_section_practice_card.png")
    }

    /** A whole section finished (as on the phone: 0 unattempted): the review button under the counters. */
    @Test fun sectionAllFinishedHasReviewButton() {
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        val mcq = runBlocking { app.repo.book(4); app.repo.mcq(4) }
        mcq.rows[10]!!.forEach { app.store.recordAnswer(it.id, true) }
        show(app) { SectionScreen(4, 10, nav) }
        rule.onNode(hasScrollAction()).performScrollToNode(hasText("Review all ${mcq.rows[10]!!.size}", substring = true))
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/review/7_section_all_finished.png")
    }

    @Test fun reviewListShowsKeysAndExplanations() {
        val app = app()
        val n = runBlocking { app.repo.mcq(4) }.subQuestions(10, 3).size
        show(app) { QuizScreen(QuizSource("sub", 4, 10, 3), "review", "Subsection MCQs", nav) }
        rule.onNodeWithText("All $n finished", substring = true).assertExists()
        rule.onRoot().captureRoboImage("screenshots/review/3_review_top.png")
        // one MCQ at a time: Next moves on (Question 2 of n)
        rule.onNodeWithText("Question 1 of $n", substring = true).assertExists()
        // the top bar's copy works in review too, as in practice
        rule.onNodeWithContentDescription("Copy this MCQ").assertExists()
        rule.onNodeWithText("Next").performClick()
        rule.waitForIdle()
        rule.onNodeWithText("Question 2 of $n", substring = true).assertExists()
        rule.onRoot().captureRoboImage("screenshots/review/4_review_wrong_one.png")
        rule.onNodeWithText("Previous").performClick()
        rule.waitForIdle()
        rule.onNode(hasScrollAction()).performScrollToNode(hasText("All $n finished", substring = true))
        rule.waitForIdle()
        rule.onNodeWithText("Wrong").performClick()
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/review/5_review_filter_wrong.png")
    }

    /** Review shows every MCQ of the set, the ones not answered yet too (with their keys and explanations). */
    @Test fun reviewShowsTheUnansweredToo() {
        val app = app()
        val all = runBlocking { app.repo.mcq(4) }.subQuestions(10, 0)
        show(app) { QuizScreen(QuizSource("sub", 4, 10, 0), "review", "Subsection MCQs", nav) }
        rule.onNodeWithText("Review all ${all.size} · 12 finished", substring = true).assertExists()
        rule.onNodeWithText("Not answered").performClick()
        rule.waitForIdle()
        rule.onNodeWithText("Not attempted", substring = true).assertExists()
        rule.onRoot().captureRoboImage("screenshots/review/8_review_not_attempted.png")
    }

    /** "Practise" on a subsection already all finished opens the review, not the same MCQs again. */
    @Test fun practiseWhenAllFinishedOpensReview() {
        val app = app()
        val n = runBlocking { app.repo.mcq(4) }.subQuestions(10, 3).size
        show(app) { QuizScreen(QuizSource("sub", 4, 10, 3), "new", "Subsection MCQs", nav) }
        assertTrue(rule.onAllNodes(hasText("All $n finished", substring = true)).fetchSemanticsNodes().isNotEmpty())
    }

    /** At the end of a quiz: "Finished all · review answers". */
    @Test fun resultsOfferTheReview() {
        val app = app()
        val qs = runBlocking { app.repo.mcq(4) }.subQuestions(10, 8)
        show(app) { QuizScreen(QuizSource("sub", 4, 10, 8), "all", "Subsection MCQs", nav) }
        qs.forEachIndexed { i, q ->
            if (q.options.isNotEmpty()) rule.onNodeWithText(q.options[(q.answer.coerceAtLeast(0) + (i % 2)) % q.options.size], substring = false).performClick()
            rule.waitForIdle()
            rule.onNodeWithText(if (i == qs.size - 1) "See results" else "Next").performClick()
            rule.waitForIdle()
        }
        rule.onNodeWithText("Finished all", substring = true).assertExists()
        rule.onRoot().captureRoboImage("screenshots/review/6_results_finished_all.png")
    }
}
