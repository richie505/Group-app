package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.hasScrollToNodeAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performScrollToNode
import androidx.compose.ui.test.performClick
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.platform.PrefsStorage
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.BooksScreen
import com.appsc.prep.ui.screens.Nav
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

/** APPSC Group 2: APPSC Complete cut down to the Group 2 syllabus, with its own plan (tools/group2_build.py). */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class Group2Test {
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
        rule.mainClock.advanceTimeBy(1000)
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/group2/$name.png")
        return app
    }

    @Test fun itIsTheGroup2Edition() {
        assertEquals("APPSC Group 2", repo.appName)
        assertTrue(repo.complete && !repo.revision)
        assertEquals(listOf("Group 2"), repo.exams.map { it.title })
        assertEquals(8, repo.exams[0].subjects.size)
    }

    /** Every section, each mapped to the Group 2 syllabus; every MCQ and PYQ of theirs; the notes load in full. */
    @Test fun everythingTheAppShipsLoads() = runBlocking {
        assertEquals(927, repo.index.sumOf { it.rows.size })
        // every syllabus item points at a section of this app
        repo.exams[0].subjects.flatMap { it.groups }.flatMap { it.rows }.forEach { (b, r) -> assertTrue("$b:$r", repo.rowInfo(b, r) != null) }
        for (mode in listOf(false)) {
            repo.mcqNotes = mode
            for (b in 1..6) {
                val bk = repo.book(b)
                assertEquals(repo.index[b - 1].rows.size, bk.rows.size)
                val empty = repo.emptyPages(mode)
                bk.rows.forEachIndexed { ri, r ->
                    val n = repo.index[b - 1].rows[ri].subsectionCount
                    assertTrue(r.secs.size <= n)
                    for (si in r.secs.size until n) assertTrue("$b:$ri:$si" in empty)
                }
            }
        }
        var mcqs = 0
        for (b in 1..6) {
            val m = repo.mcq(b)
            m.rows.forEach { (ri, qs) ->
                mcqs += qs.size
                assertEquals(repo.index[b - 1].rows[ri].questionCount, qs.size)
                qs.forEach { q -> assertTrue(q.answer in -1 until q.options.size && q.options.size >= 2) }
            }
        }
        assertEquals(71013, mcqs)
        assertEquals(mcqs, repo.planIds.size)
    }

    /** The plan: today to 21 Jan, every section read once in the first pass, then R2, R3, MCQ days and 5 mocks. */
    /** Group 2 codes and tags only; every PYQ stays (Group 1 and other papers' PYQs too), mapped by the syllabus. */
    @Test fun noGroup1Content() = runBlocking {
        val g2codes = repo.exams[0].subjects.flatMap { it.groups }.map { it.code }.toSet()
        for (b in repo.index) for (r in b.rows) {
            assertTrue("${b.id}:${r.index} ${r.codes}", r.codes.isNotEmpty() && r.codes.all { it in g2codes })
            assertEquals("GROUP-II", r.tag)
            assertTrue(r.pyq, !r.pyq.contains("G1"))
        }
        for (b in 1..6) {
            for (mode in listOf(false)) {
                repo.mcqNotes = mode
                val text = repo.book(b).rows.joinToString("\n") { r -> r.secs.joinToString("\n") { com.appsc.prep.data.NotesFinder.text(it.blocks) } }
                assertTrue("book $b cites a Group 1 paper", !Regex("APPSC[- ]?G-?1\\b").containsMatchIn(text))
            }
        }
    }

    /** Prelims (Screening) part to 21 Feb, then the Mains part; every section read once in a first pass. */
    @Test fun thePlanRunsPrelimsThenMains() {
        val p = repo.plan
        assertEquals(java.time.LocalDate.of(2026, 11, 16), p.days.first().date)
        assertEquals(java.time.LocalDate.of(2027, 5, 19), p.days.last().date)
        assertEquals(185, p.days.size)
        val study = p.days.filter { it.type == "study" }.flatMap { d -> d.rows.map { it.book to it.row } }
        assertEquals(927, study.size)
        assertEquals(927, study.toSet().size)
        assertEquals(12, p.days.count { it.type == "mock" })  // 5 Screening, 6 Mains, the Prelims day
        assertTrue(p.days.filter { it.date < java.time.LocalDate.of(2027, 2, 21) }.all { it.phase.startsWith("PRELIMS") })
        assertTrue(p.days.filter { it.date > java.time.LocalDate.of(2027, 2, 21) }.all { it.phase.startsWith("MAINS") })
        assertEquals("Prelims (21 Feb 2027)", p.nextExam(java.time.LocalDate.of(2027, 1, 1)).second)
        assertEquals("Mains (planned 22 May 2027)", p.nextExam(java.time.LocalDate.of(2027, 3, 1)).second)
        // planmcq.json is current
        val books = runBlocking { (1..6).associateWith { repo.mcq(it) } }
        val fresh = com.appsc.prep.data.DueMcqs.planMcqs(p) { b, row -> books[b]!!.rows[row]?.map { it.id } ?: emptyList() }
        assertEquals(fresh.days.map { it.second }, repo.planMcqs.days.map { it.second })
        // spread: every study day of a part has the same number of MCQs (within 1), none before its topic's day
        assertTrue(p.spread)
        for (part in listOf("PRELIMS", "MAINS")) {
            val n = fresh.days.filter { it.first.type == "study" && it.first.phase.startsWith(part) }.map { it.second.size }
            assertTrue("$part ${n.min()}..${n.max()}", n.max() - n.min() <= 1)
        }
        val topicDay = HashMap<String, Int>()
        p.days.forEach { d -> d.rows.forEach { r -> books[r.book]!!.rows[r.row]?.forEach { q -> topicDay.putIfAbsent(q.id, d.n) } } }
        assertTrue(fresh.days.all { (d, ids) -> ids.all { topicDay[it]!! <= d.n } })
        assertEquals(71013, fresh.days.sumOf { it.second.size })
    }

    @Test fun aSessionIsFull() {
        val app = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        val t = com.appsc.prep.data.DailyTarget.of(app.store.activity, java.time.LocalDate.now())
        val s = com.appsc.prep.ui.screens.sessionIds(app)
        assertEquals(t.session, s.size)
        assertTrue(s.all { it in repo.planIds })
    }

    @Test fun readFromNotesFindsTheAnswerForMostMcqs() = runBlocking {
        repo.mcqNotes = false
        var tried = 0
        var hit = 0
        val miss = StringBuilder()
        for (b in 1..6) {
            val book = repo.book(b)
            val m = repo.mcq(b)
            val qs = m.rows.values.flatten().filter { q ->
                val o = q.options.getOrNull(q.answer).orEmpty()
                q.answer >= 0 && com.appsc.prep.data.NotesFinder.answerWords(q).isNotEmpty() && o.length in 3..40
            }
            for (q in qs.filterIndexed { i, _ -> i % 40 == 0 }) {
                tried++
                val at = com.appsc.prep.data.NotesFinder.best(q, book, m.placeOf(q.id)?.first ?: -1) ?: continue
                val w = com.appsc.prep.data.NotesFinder.words(com.appsc.prep.data.NotesFinder.text(book.rows[at.row].secs[at.sec].blocks))
                val ans = com.appsc.prep.data.NotesFinder.answerWords(q)
                if (ans.count { it in w } * 2 >= ans.size) hit++ else miss.append("${q.id} | ${q.stem.take(70)} => ${q.options[q.answer]} | ${book.rows[at.row].secs[at.sec].title}\n")
            }
        }
        java.io.File("build/group2-finder-misses.txt").writeText("hit $hit of $tried\n$miss")
        // 80%, not APPSC Complete's 85%: some PYQs filed under Group 2 topics ask a fact only a Group 1 section's
        // notes held (left out here), so no page of this app has it; the nearest page opens instead
        assertTrue("hit $hit of $tried", hit >= tried * 0.80)
    }

    @Test fun notesTab() {
        repo.mcqNotes = true
        shot("1_notes") { BooksScreen(nav) }
        rule.onNodeWithText("GROUP 2").assertExists()
        assertTrue(rule.onAllNodes(hasText("GROUP 1")).fetchSemanticsNodes().isEmpty())
        assertTrue(rule.onAllNodes(hasText("G1")).fetchSemanticsNodes().isEmpty())
    }

    @Test fun todayTab() {
        runBlocking { repo.plan.days.take(2).forEach { d -> d.rows.forEach { repo.mcq(it.book) } } }
        shot("2_today") { com.appsc.prep.ui.screens.TodayScreen(nav) }
        rule.onNodeWithText("TODAY'S PRACTICE", substring = true).assertExists()
        // the day's notes as an audiobook
        rule.onNode(androidx.compose.ui.test.hasScrollAction()).performScrollToNode(hasText("LISTEN TO TODAY'S NOTES"))
        rule.onNodeWithText("Listen", substring = true).assertExists()
        rule.onRoot().captureRoboImage("screenshots/group2/3_listen_card.png")
    }

    @Test fun topicAndStatementMcq() {
        repo.mcqNotes = true
        runBlocking { repo.book(4); repo.mcq(4) }
        val (ri, sub) = runBlocking {
            val m = repo.mcq(4)
            // a section whose first MCQ is a 3-statement set (most MCQs are one-liners now, as in APPSC's papers)
            m.rows.keys.sorted().flatMap { r -> (0 until 40).map { r to it } }.first { (r, s) ->
                m.subQuestions(r, s).firstOrNull()?.let { "Consider the following statements" in it.stem && "1, 2 and 3" in it.options } == true
            }
        }
        val app = shot("3_statement_mcq") { com.appsc.prep.ui.screens.QuizScreen(com.appsc.prep.ui.screens.QuizSource("sub", 4, ri, sub), "all", "Section MCQs", nav) }
        rule.onNodeWithText("Consider the following statements", substring = true).assertExists()
        rule.onNodeWithText("1, 2 and 3").performClick()
        rule.waitForIdle()
        assertEquals(1, app.store.answers.size)
    }
}
