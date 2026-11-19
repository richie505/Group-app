package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.hasScrollToNodeAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onFirst
import androidx.compose.ui.test.performScrollTo
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
import androidx.compose.ui.test.onAllNodesWithText
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
        assertEquals(68688, mcqs)
        assertEquals(mcqs, repo.planIds.size)
    }

    /** The plan: today to 21 Jan, every section read once in the first pass, then R2, R3, MCQ days and 5 mocks. */
    /** Group 2 codes and tags only; every PYQ stays (Group 1 and other papers' PYQs too), mapped by the syllabus. */
    @Test fun noGroup1Content() = runBlocking {
        val g2codes = repo.exams[0].subjects.flatMap { it.groups }.map { it.code }.toSet()
        for (b in repo.index) for (r in b.rows) {
            // the official syllabus lines it teaches ("X": beyond the official syllabus, kept for practice)
            assertTrue("${b.id}:${r.index} ${r.codes}", r.codes.isNotEmpty() && r.codes.all { it in g2codes || it == "X" })
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

    /** The official syllabus (27-04-2023): 8 subjects, 328 lines, every MCQ tied to a line or marked beyond it. */
    @Test fun builtOnTheOfficialSyllabus() = runBlocking {
        val syl = repo.syllabus!!
        assertEquals(8, syl.subjects.size)
        assertEquals(328, syl.leaves.size)
        assertEquals(listOf("Prelims", "Prelims", "Prelims", "Prelims", "Mains", "Mains", "Mains", "Mains"), syl.subjects.map { it.stage })
        val codes = syl.leaves.map { it.code }.toSet()
        val all = repo.index.flatMap { b -> repo.mcqWhere(b.id) { true } }
        assertTrue(all.all { it.leaf == "x" || it.leaf in codes })
        assertTrue(all.filter { it.id.startsWith("y") }.all { it.tier in setOf("g2", "ap", "up", "ot") })
        assertEquals(syl.leaves.sumOf { it.q }, all.count { it.leaf != "x" })
        // every line has notes behind it
        assertTrue(syl.leaves.all { it.rows.isNotEmpty() })
    }

    /** Prelims (Screening) part to 21 Feb, then the Mains part; every section read once in a first pass. */
    @Test fun thePlanRunsPrelimsThenMains() {
        val p = repo.plan
        assertEquals(java.time.LocalDate.of(2026, 11, 16), p.days.first().date)
        assertEquals(java.time.LocalDate.of(2027, 5, 19), p.days.last().date)
        assertEquals(185, p.days.size)
        val study = p.days.filter { it.type == "study" }.flatMap { d -> d.rows.map { it.book to it.row } }
        // every listed section once (one is hidden: nothing in it is in the Group 2 syllabus, tools/group2_fit.py)
        val listed = (1..6).sumOf { b -> repo.index[b - 1].rows.count { !it.hidden } }
        assertEquals(926, listed)
        assertEquals(listed, study.size)
        assertEquals(listed, study.toSet().size)
        assertEquals(12, p.days.count { it.type == "mock" })  // 5 Screening, 6 Mains, the Prelims day
        assertTrue(p.days.filter { it.date < java.time.LocalDate.of(2027, 2, 21) }.all { it.phase.startsWith("PRELIMS") })
        assertTrue(p.days.filter { it.date > java.time.LocalDate.of(2027, 2, 21) }.all { it.phase.startsWith("MAINS") })
        assertEquals("Prelims (21 Feb 2027)", p.nextExam(java.time.LocalDate.of(2027, 1, 1)).second)
        assertEquals("Mains (planned 22 May 2027)", p.nextExam(java.time.LocalDate.of(2027, 3, 1)).second)
        // planmcq.json is current
        val books = runBlocking { (1..6).associateWith { repo.mcq(it) } }
        val fresh = com.appsc.prep.data.DueMcqs.planMcqs(p) { b, row -> books[b]!!.rows[row]?.map { it.id } ?: emptyList() }
        assertEquals(fresh.days.map { it.second }, repo.planMcqs.days.map { it.second })
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

    /** "Practise" counts what its set opens: an unscored MCQ (no key / deleted), only viewed, is not one of them. */
    @Test fun practiseCountMatchesItsSet() {
        fun q(id: String, kind: Char) = com.appsc.prep.data.Question(id, "Q", emptyList(), listOf("a", "b"), if (kind == 'u') -1 else 0, "", false, "", emptyList(), kind = kind)
        val qs = listOf(q("ya", 's'), q("yb", 'u'), q("yc", 's'))
        val seen = setOf("ya", "yb")
        val answers = mapOf("yc" to false)
        val sets = com.appsc.prep.ui.components.practiceSets(qs, answers, seen)
        val opened = com.appsc.prep.ui.screens.pickSet(qs, answers, seen, "practice")
        assertEquals(opened.size, sets.practice)
        assertEquals(2, sets.practice)
    }

    /** The counts shown for a topic are its MCQs and pages; no MCQ is in two places. */
    @Test fun shownCountsMatch() = runBlocking {
        val seen = HashSet<String>()
        for (info in repo.index) {
            val book = repo.book(info.id)
            val m = repo.mcq(info.id)
            for ((r, row) in info.rows.withIndex()) {
                assertEquals("${info.id}:$r MCQs", row.questionCount, m.rows[r]?.size ?: 0)
                assertEquals("${info.id}:$r pages", row.subsectionCount, book.rows[r].secs.size)
            }
            for (q in m.rows.values.flatten()) assertTrue("twice: ${q.id}", seen.add(q.id))
        }
    }

    /** Every MCQ sits in a subsection of its topic, so a topic's subsections add up to the whole section. */
    @Test fun everyMcqIsInASubsection() = runBlocking {
        for (b in 1..6) {
            val book = repo.book(b)
            val m = repo.mcq(b)
            for ((r, qs) in m.rows) {
                val subs = m.subs[r] ?: emptyList()
                val n = book.rows[r].secs.size
                assertEquals("book $b row $r", qs.size, subs.size)
                assertTrue("book $b row $r: ${subs.filter { it !in 0 until n }}", subs.all { it in 0 until n })
            }
        }
    }

    @Test fun syllabusScreen() {
        runBlocking { repo.leafOf() }
        shot("5_syllabus") { com.appsc.prep.ui.screens.SyllabusScreen(nav) }
        rule.onNodeWithText("Indian History (30 marks)", substring = true).assertExists()
    }

    @Test fun syllabusSubject() {
        runBlocking { repo.leafOf() }
        shot("6_syllabus_subject") { com.appsc.prep.ui.screens.SylSubjectScreen(4, nav) }
    }

    @Test fun syllabusLine() {
        runBlocking { repo.leafOf() }
        val i = repo.syllabus!!.leaves.indexOfFirst { it.code == "M1A.3.11/3" }
        shot("7_syllabus_line") { com.appsc.prep.ui.screens.LeafScreen(i, nav) }
        assertTrue(rule.onAllNodesWithText("Nataka Samasthalu", substring = true).fetchSemanticsNodes().isNotEmpty())
    }

    @Test fun notesTabOfficialSyllabus() {
        shot("8_notes_tab") { com.appsc.prep.ui.screens.BooksScreen(nav) }
        rule.onNodeWithText("OFFICIAL APPSC SYLLABUS", substring = true).assertExists()
    }

    @Test fun todayTab() {
        runBlocking { repo.plan.days.take(2).forEach { d -> d.rows.forEach { repo.mcq(it.book) } } }
        shot("2_today") { com.appsc.prep.ui.screens.TodayScreen(nav) }
        rule.onNodeWithText("TODAY'S PRACTICE", substring = true).assertExists()
        // no plan: the countdown and the next notes page to read (note by note)
        rule.onNodeWithText("YOUR TARGETS").assertExists()
        rule.onNodeWithText("Set your target date").assertExists()
        rule.onNodeWithText("Next to read").assertExists()
    }

    /** The reader sets their own target date and MCQs a day; nothing is assigned. */
    @Test fun ownTargets() {
        val app = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        app.store.setTarget(java.time.LocalDate.now().plusDays(90), "Prelims")
        app.store.changeDailyGoal(250)
        assertEquals(250, com.appsc.prep.data.DailyTarget.of(app.store.activity, java.time.LocalDate.now(), app.store.dailyGoal).standard)
        // kept across a restart, and in a backup
        val again = ProgressStore(PrefsStorage(ctx))
        assertEquals(250, again.dailyGoal)
        assertEquals("Prelims", again.targetLabel)
        shot("2_own_targets", app) { com.appsc.prep.ui.screens.TodayScreen(nav) }
        rule.onNodeWithText("90 days left").assertExists()
        rule.onNodeWithText("Your MCQs a day: 250").assertExists()
        app.store.setTarget(null, ""); app.store.changeDailyGoal(0)
    }

    /** The notes MCQs follow APPSC's pattern (APPSC: Cracked): statement sets vary in how many are true, and
     *  "None of the above / Neither" is a real key. */
    @Test fun notesMcqsFollowAppscPattern() = runBlocking {
        var three = 0; var threeTwo = 0; var noneKey = 0; var noneHave = 0
        for (b in 1..6) for (q in repo.mcq(b).rows.values.flatten()) {
            if (q.id.startsWith("y") || q.answer !in q.options.indices) continue
            assertTrue("${q.id} carries its APPSC pattern tag", q.tags.any { it.startsWith("pattern:") })
            if (q.options.any { it.startsWith("None of the above") || it.startsWith("Neither") }) {
                noneHave++
                if (q.options[q.answer].startsWith("None of the above") || q.options[q.answer].startsWith("Neither")) noneKey++
            }
            val st = Regex("""(?m)^\s*[1-3]\.\s""").findAll(q.stem).count()
            if (st == 3 && !Regex("""(?m)^\s*4\.\s""").containsMatchIn(q.stem) && q.stem.contains("correct") && !q.stem.contains("incorrect")) {
                three++
                val k = q.options[q.answer]
                if (Regex("""^\d and \d only$""").matches(k.trim())) threeTwo++
            }
        }
        assertTrue("3-statement sets no longer almost all '2 true' ($threeTwo of $three)", threeTwo < 0.7 * three)
        assertTrue("None / Neither is a real key ($noneKey of $noneHave)", noneKey > 0.15 * noneHave)
    }

    /** "Stuck?": one tap shows the answer and its worked trick; like "From the notes", the pick then counts as a normal answer. */
    @Test fun stuckShowsAnswerAndTrick() {
        assertTrue(repo.solved.size >= 600)
        val q = "yQ1636012260"
        val mq = runBlocking { repo.mcq(3).rows.values.flatten().first { it.id == q } }
        val answer = mq.answer
        // the subsection also holds notes MCQs: answer them first so "new" opens on the worked PYQ
        val app0 = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        listOf("f0f791115fe35", "cp5b62f81bb432", "cpf2972849e383").forEach { app0.store.recordAnswer(it, true) }
        val app = shot("5_stuck", app0) { com.appsc.prep.ui.screens.QuizScreen(com.appsc.prep.ui.screens.QuizSource("sub", 3, 17, 8), "new", "Subsection MCQs", nav) }
        rule.waitUntil(30_000) { rule.onAllNodes(hasText("Urban Infrastructure Development Fund", substring = true)).fetchSemanticsNodes().isNotEmpty() }
        rule.onNode(hasText("Stuck? Show the answer and the trick")).performScrollTo().performClick()
        rule.waitForIdle()
        rule.onNodeWithText("HOW TO CRACK IT", substring = true).assertExists()
        rule.onNodeWithText("Words that give it away", substring = true).assertExists()
        com.github.takahirom.roborazzi.captureScreenRoboImage("screenshots/group2/5_stuck.png")
        rule.onNode(hasText(mq.options[answer]) and androidx.compose.ui.test.hasClickAction()).performScrollTo().performClick()
        rule.waitForIdle()
        // like "From the notes": the pick counts as a normal answer, not as an answer seen, and the MCQ is done
        assertEquals(true, app.store.answers[q])
        assertEquals("not counted as an answer seen", 0, app.store.dayLog().viewed)
        assertTrue("not practice again", !app.store.needsPractice(q))
        val sets = com.appsc.prep.ui.components.practiceSets(listOf(q), app.store.answers, app.store.seen)
        assertEquals(0, sets.unattempted)
        assertEquals(0, sets.practice)
    }

    /** Every notes MCQ says it follows APPSC's pattern, with its type. */
    @Test fun notesMcqShowsPatternTag() {
        shot("7_pattern_tag") { com.appsc.prep.ui.screens.QuizScreen(com.appsc.prep.ui.screens.QuizSource("sub", 3, 17, 8), "all", "Subsection MCQs", nav) }
        rule.waitUntil(30_000) { rule.onAllNodes(hasText("APPSC pattern · ", substring = true)).fetchSemanticsNodes().isNotEmpty() }
        com.github.takahirom.roborazzi.captureScreenRoboImage("screenshots/group2/7_pattern_tag.png")
    }

    @Test fun tricksScreen() {
        shot("6_tricks") { com.appsc.prep.ui.screens.TricksScreen(nav) }
        rule.onNodeWithText("THE METHOD").assertExists()
        rule.onNodeWithText("LEAN FALSE").assertExists()
    }

    @Test fun topicAndStatementMcq() {
        repo.mcqNotes = true
        // a subsection whose first MCQ is a 3-statement set (most MCQs are one-liners, as in APPSC's papers), in any book
        val (bk, ri, sub) = runBlocking {
            (1..6).firstNotNullOf { b ->
                repo.book(b)
                val m = repo.mcq(b)
                m.rows.keys.sorted().flatMap { r -> (0 until 40).map { r to it } }.firstOrNull { (r, s) ->
                    m.subQuestions(r, s).firstOrNull()?.let { "Consider the following statements" in it.stem && "1, 2 and 3" in it.options } == true
                }?.let { Triple(b, it.first, it.second) }
            }
        }
        val app = shot("3_statement_mcq") { com.appsc.prep.ui.screens.QuizScreen(com.appsc.prep.ui.screens.QuizSource("sub", bk, ri, sub), "all", "Section MCQs", nav) }
        rule.onNodeWithText("Consider the following statements", substring = true).assertExists()
        rule.onNodeWithText("1, 2 and 3").performClick()
        rule.waitForIdle()
        assertEquals(1, app.store.answers.size)
    }
}
