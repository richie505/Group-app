package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.hasScrollToNodeAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollToNode
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.data.subsectionId
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

    private fun shot(name: String, book: Int, content: @androidx.compose.runtime.Composable () -> Unit): AppState {
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        app.repo.mcqNotes = true
        runBlocking { app.repo.book(book); app.repo.mcq(book) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { content() } } }
        rule.waitForIdle()
        rule.mainClock.advanceTimeBy(1000)
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/complete/$name.png")
        return app
    }

    /** A topic's subsections and its full-notes pages as one numbered list, without the "Full notes" heading. */
    @Test fun aTopicIsOneListOfSubsections() {
        shot("12_topic_one_list", 4) { com.appsc.prep.ui.screens.SectionScreen(4, 30, nav) }
        rule.onAllNodes(hasText("Full notes", substring = true, ignoreCase = true)).fetchSemanticsNodes().let { assertTrue("no Full notes heading or badge", it.isEmpty()) }
        rule.onNodeWithText("Subsections", substring = true, ignoreCase = true).assertExists()
        // the count read is of the pages shown (empty ones hidden)
        rule.onNodeWithText("SUBSECTIONS (15)", substring = true, ignoreCase = true).assertExists()
        rule.onNodeWithText("0 / 15", substring = true).assertExists()
    }

    /** A 3-statement MCQ: the title fits beside the buttons; one tap on an option answers it (no Check step). */
    @Test fun statementMcqSelectThenCheck() {
        val app = shot("13_statement_mcq", 4) { com.appsc.prep.ui.screens.QuizScreen(com.appsc.prep.ui.screens.QuizSource("sub", 4, 30, 0), "all", "Subsection MCQs", nav) }
        rule.onNodeWithText("Consider the following statements", substring = true).assertExists()
        rule.onNodeWithText("1, 2 and 3").performClick()
        rule.waitForIdle()
        assertTrue("no Check step", rule.onAllNodes(hasText("Check answer")).fetchSemanticsNodes().isEmpty())
        rule.onRoot().captureRoboImage("screenshots/complete/14_statement_mcq_checked.png")
        assertEquals(1, app.store.answers.size)
    }

        @Test fun readFromNotesOpensThePageWithTheAnswer() = runBlocking {
        val repo = Repository { ctx.assets.open(it) }
        val book = repo.book(6)
        val m = repo.mcq(6)
        val all = m.rows.values.flatten()
        // Swarnandhra 2047 and the CK Dinne smart kitchen: one-fact MCQs once, now statements of 3-statement MCQs
        fun pageFor(text: String): String {
            val q = all.first { it.stem.contains(text) }
            val at = com.appsc.prep.data.NotesFinder.best(q, book, m.placeOf(q.id)?.first ?: -1)!!
            val sec = book.rows[at.row].secs[at.sec]
            return sec.title + "\n" + com.appsc.prep.data.NotesFinder.text(sec.blocks)
        }
        assertTrue(pageFor("Swarnandhra").contains("Swarnandhra"))
        assertTrue(pageFor("CK Dinne").contains("Kitchen"))
    }

    @Test fun readFromNotesFindsTheAnswerForMostMcqs() = runBlocking {
        val repo = Repository { ctx.assets.open(it) }
        val report = StringBuilder()
        var tried = 0
        var hit = 0
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
                if (ans.count { it in w } * 2 >= ans.size) hit++ else report.append("${q.id} | ${q.stem.take(80)} => ${q.options[q.answer]} | ${book.rows[at.row].secs[at.sec].title}\n")
            }
        }
        java.io.File("build/notes-finder-misses.txt").writeText("hit $hit of $tried\n$report")
        assertTrue("hit $hit of $tried", hit >= tried * 0.85)
    }

    /** A 3-statement MCQ marks the line of each statement, not only those its option code points at. */
    @Test fun everyStatementIsMarkedInTheNotes() = runBlocking {
        val repo = Repository { ctx.assets.open(it) }
        repo.mcqNotes = true
        val m = repo.mcq(4)
        val q = m.rows.values.flatten().first { "Seasonal plantation" in it.stem }
        val book = repo.book(4)
        val at = com.appsc.prep.data.NotesFinder.best(q, book, m.placeOf(q.id)!!.first)!!
        val blocks = book.rows[at.row].secs[at.sec].blocks
        val marked = com.appsc.prep.data.NotesFinder.marked(q, blocks).map { com.appsc.prep.data.NotesFinder.text(listOf(blocks[it])) }
        println(marked)
        // the blueprint notes hold the first two statements on the classification page (the third is on Land Resources)
        for (fact in listOf("abiotic", "hydrogen")) assertTrue("$fact marked: $marked", marked.any { it.contains(fact, ignoreCase = true) })
        // across the bank: most statements of the statement MCQs find their line in the topic (the key points shown first)
        var stmts = 0; var hit = 0
        for (b in 1..6) {
            val bk = repo.book(b); val mq = repo.mcq(b)
            mq.rows.values.flatten().filter { it.id.startsWith("m") }.take(150).forEach { x ->
                val p = com.appsc.prep.data.NotesFinder.best(x, bk, mq.placeOf(x.id)?.first ?: -1) ?: return@forEach
                stmts += 3
                // a statement's line on any page of the topic: the key points "Read from the notes" shows first
                hit += com.appsc.prep.data.NotesFinder.keyPoints(x, bk.rows[p.row], p.sec).size.coerceAtMost(3)
            }
        }
        println("statement lines marked: $hit of $stmts")
        assertTrue("$hit of $stmts", hit * 10 >= stmts * 7)
    }

    /** A statement MCQ made from a one-fact MCQ answered wrong (or only viewed) comes back for revision. */
    @Test fun weakOneFactMcqsPassTheirRevisionOnToTheMergedMcq() {
        val repo = Repository { ctx.assets.open(it) }
        val merged = repo.merged
        assertTrue(merged.size > 10000)
        val (wrongId, wrongOlds) = merged.entries.first()
        val (viewedId, viewedOlds) = merged.entries.drop(1).first()
        val (rightId, rightOlds) = merged.entries.drop(2).first()
        val store = ProgressStore(PrefsStorage(ctx))
        store.recordAnswer(wrongOlds[0], false)
        store.markSeen(viewedOlds[1], viewed = true)
        store.recordAnswer(rightOlds[0], true)
        assertTrue(store.carryMerged(merged) >= 2)
        assertEquals(com.appsc.prep.data.Mastery.REVISE, store.mastery(wrongId))
        assertEquals(com.appsc.prep.data.Mastery.LEARNING, store.mastery(viewedId))
        assertEquals("a right one stays new: it is a new question", com.appsc.prep.data.Mastery.NEW, store.mastery(rightId))
        assertTrue(wrongId !in store.answers)
        assertEquals("only once", 0, store.carryMerged(merged))
    }

    /** Every file the app ships loads: both sets of notes, every MCQ, every plan day, and today's session is full. */
    @Test fun everythingTheAppShipsLoads() = runBlocking {
        val repo = Repository { ctx.assets.open(it) }
        var pages = 0
        for (mode in listOf(true, false)) {
            repo.mcqNotes = mode
            for (b in 1..6) {
                val bk = repo.book(b)
                assertEquals("book $b rows (notes ${if (mode) "MCQ" else "full"})", repo.index[b - 1].rows.size, bk.rows.size)
                val empty = repo.emptyPages(mode)
                bk.rows.forEachIndexed { ri, r ->
                    val n = repo.index[b - 1].rows[ri].subsectionCount
                    assertTrue("book $b row $ri pages", r.secs.size <= n)
                    // a page only the other notes have counts as read here
                    for (si in r.secs.size until n) assertTrue("book $b row $ri page $si", "$b:$ri:$si" in empty)
                }
                pages += bk.rows.sumOf { it.secs.size }
            }
        }
        assertEquals("one set of notes, shown in both modes", 2 * 11199, pages)
        var mcqs = 0
        for (b in 1..6) {
            val m = repo.mcq(b)
            m.rows.forEach { (ri, qs) ->
                mcqs += qs.size
                qs.forEach { q ->
                    assertTrue("${q.id}: 2+ options", q.options.size >= 2)
                    assertTrue("${q.id}: key in range", q.answer in -1 until q.options.size)
                }
                assertEquals("book $b row $ri: MCQ count in the index", repo.index[b - 1].rows[ri].questionCount, qs.size)
            }
        }
        assertEquals(35562, mcqs)
        assertEquals(mcqs, repo.planIds.size)
        assertTrue(repo.merged.keys.all { it in repo.planIds })
        val app = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        val t = com.appsc.prep.data.DailyTarget.of(app.store.activity, java.time.LocalDate.now())
        assertEquals("a session is full", t.session, com.appsc.prep.ui.screens.sessionIds(app).size)
    }

        /** The reader's own backup (APPSC_BACKUP=path; skipped without it): restores, and practice goes on from it. */
    @Test fun theReadersBackupRestoresHere() {
        val path = System.getenv("APPSC_BACKUP") ?: return
        val repo = Repository { ctx.assets.open(it) }
        val store = ProgressStore(PrefsStorage(ctx))
        val r = store.restore(java.io.File(path).readText(), repo.idMoves, repo.noteMoves, repo.mcqLinks)
        val carried = store.carryMerged(repo.merged)
        val app = AppState(repo, store, AndroidPlatform(ctx))
        val today = java.time.LocalDate.now()
        val t = com.appsc.prep.data.DailyTarget.of(store.activity, today)
        val due = com.appsc.prep.data.DailyTarget.dueRevision(store.hist, today) { it in repo.planIds }
        val session = com.appsc.prep.ui.screens.sessionIds(app)
        val own = com.appsc.prep.data.PracticeSummary.of(store.hist) { it in repo.planIds }
        val report = "restored ${r.answers} answers, ${r.read} pages; merged MCQs marked for revision $carried; " +
            "targets ${t.minimum}/${t.standard}/${t.stretch}, session ${t.session}; due revision ${due.size}; " +
            "session ${session.size} (${session.count { it in due }} revision); this app: tried ${own.tried}, to revise ${own.revise}, " +
            "mastered ${own.mastered}, only viewed ${own.viewedOnly}"
        println(report)
        java.io.File("build/backup-check.txt").writeText(report)
        assertTrue(r.answers > 10000)
        assertTrue(carried > 200)
        assertEquals(t.session, session.size)
        assertTrue("revision first, at most a third", session.take(t.session / 3).all { it in due })
        assertTrue(session.distinct().size == session.size && session.all { it in repo.planIds })
    }

        /** From the notes: first only this MCQ's key points (a line for each statement), then the whole page on request. */
    @Test fun fromTheNotesShowsTheKeyPointsOfTheMcq() {
        val app = shot("15_key_points", 4) { com.appsc.prep.ui.screens.QuizScreen(com.appsc.prep.ui.screens.QuizSource("sub", 4, 30, 0), "all", "Subsection MCQs", nav) }
        val q = runBlocking { app.repo.mcq(4).rows[30]!!.first { "Seasonal plantation" in it.stem } }
        val row = runBlocking { app.repo.book(4).rows[30] }
        val keys = com.appsc.prep.data.NotesFinder.keyPoints(q, row, 0)
        val text = keys.map { (si, bi) -> com.appsc.prep.data.NotesFinder.text(listOf(row.secs[si].blocks[bi])) }
        for (fact in listOf("hydrogen", "Seasonal plantation")) assertTrue("$fact in $text", text.any { it.contains(fact, ignoreCase = true) })
        rule.onNode(androidx.compose.ui.test.hasContentDescription("Read from the notes")).performClick()
        rule.waitForIdle()
        // the notes page is found in the background: wait for it (slow on a loaded machine)
        repeat(20) {
            if (rule.onAllNodes(hasText("Key points for this MCQ")).fetchSemanticsNodes().isEmpty()) {
                rule.mainClock.advanceTimeBy(1500); rule.waitForIdle(); Thread.sleep(300)
            }
        }
        rule.onNodeWithText("Key points for this MCQ").assertExists()
        rule.onRoot().captureRoboImage("screenshots/complete/15_key_points.png")
        rule.onNodeWithText("Show the whole page ›").performClick()
        rule.waitForIdle()
        rule.onNodeWithText("‹ Key points").assertExists()
    }

        /** A current-affairs one-liner names its page; that page of the MCQ notes holds its facts (not "No MCQs yet"). */
    @Test fun aCurrentAffairsMcqFindsItsFactsInTheMcqNotes() = runBlocking {
        val repo = Repository { ctx.assets.open(it) }
        repo.mcqNotes = true
        val m = repo.mcq(6)
        val q = m.rows.values.flatten().first { "EFTA Prosperity" in it.stem }
        val book = repo.book(6)
        val at = com.appsc.prep.data.NotesFinder.best(q, book, m.placeOf(q.id)!!.first)!!
        val page = com.appsc.prep.data.NotesFinder.text(book.rows[at.row].secs[at.sec].blocks)
        assertTrue(page, "No MCQs on this subsection" !in page && "1960" in page && "Geneva" in page)
        val keys = com.appsc.prep.data.NotesFinder.keyPoints(q, book.rows[at.row], at.sec)
        assertTrue("key points found", keys.isNotEmpty())
    }

        /** The blueprint notes have one page per numbered section: none is empty, so none is hidden. */
    @Test fun noPageIsEmptyOrHidden() = runBlocking {
        val repo = Repository { ctx.assets.open(it) }
        for (mode in listOf(true, false)) {
            repo.mcqNotes = mode
            assertTrue(repo.emptyPages(mode).isEmpty())
            for (b in 1..6) assertTrue(repo.book(b).rows.all { r -> r.secs.isNotEmpty() && r.secs.none { it.empty } })
        }
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

    /** Every topic is its one-pager (tools/onepager_app.py): a subsection per box, then its full notes, one list. */
    @Test fun aSubsectionPerBox() {
        val repo = Repository { ctx.assets.open(it) }
        for (b in 1..6) {
            val book = runBlocking { repo.book(b) }
            val mcq = runBlocking { repo.mcq(b) }
            for (row in book.rows) {
                // the boxes, then the topic's full-notes pages, as one list (none marked apart)
                assertTrue("book $b row ${row.index}: a subsection per box, then the full notes", row.secs.size >= 6)
                assertTrue("book $b row ${row.index}: one list", row.secs.none { it.full || "Full notes" in it.badges })
                assertTrue("book $b row ${row.index}: counted in full", row.secs.size <= repo.index[b - 1].rows[row.index].subsectionCount)
                assertTrue("book $b row ${row.index}: MCQs under its boxes", mcq.subs[row.index].orEmpty().all { it in -1 until row.secs.size })
            }
        }
        show("4_preamble_first_subsection") { ReaderScreen(2, 4, 0, nav) }
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
    @Test fun caUpiPage() = caPage("9_ca_upi_page", 33, 0, null)

    private class MemStorage : com.appsc.prep.data.Storage {
        private val sets = HashMap<String, Set<String>>()
        private val strings = HashMap<String, String>()
        override fun getStringSet(key: String) = sets[key].orEmpty()
        override fun getString(key: String) = strings[key]
        override fun getFloat(key: String, default: Float) = default
        override fun putStringSet(key: String, value: Set<String>) { sets[key] = value }
        override fun putString(key: String, value: String) { strings[key] = value }
        override fun putFloat(key: String, value: Float) {}
    }

    /** A past plan day's MCQs not attempted are due, each MCQ once; today's plan day's are counted apart. */
    @Test fun dueIsUnattemptedFromDay1() {
        val days = Repository { ctx.assets.open(it) }.plan.days
        val plan = com.appsc.prep.data.DueMcqs.PlanMcqs(
            listOf(days[0] to listOf("a", "b"), days[1] to listOf("c"), days[2] to listOf("d", "e")),
        )
        val tried = setOf("a", "d")
        val s = com.appsc.prep.data.DueMcqs.status(plan, days[2].date) { it in tried }
        assertEquals(listOf(1, 1), s.days.map { it.left })
        assertEquals(listOf(1, 0), s.days.map { it.attempted })
        assertEquals(2, s.due)
        assertEquals(1, s.todayLeft)
        assertEquals(2, s.today!!.total)
        assertEquals(3, s.left) // today's 1 not attempted + 2 due
    }

    /** A backup of APPSC One-liners restores here: its pages as they are; its one-liners' results on the MCQ they came from. */
    @Test fun onelinerBackupRestoresHere() {
        val r = Repository { ctx.assets.open(it) }
        val k = runBlocking { r.book(1).rows[0].secs.count { !it.full } }
        val one = ProgressStore(MemStorage().apply { putString("ids_version", "oneliner-full-1") })
        one.migrateNotes(r.noteMoves)
        one.setDone("1:0:1", true)
        one.setDone("1:0:${k + 1}", true)
        one.setAdded("1:0:${k + 1}#-1", "from one-liners")
        // two one-liners of one MCQ: one right, one wrong -> the MCQ is to revise; another MCQ's only one right
        val byMcq = r.mcqLinks.entries.groupBy({ it.value[0] }, { it.key })
        val (mcq, lines) = byMcq.entries.first { it.value.size >= 2 }
        one.recordAnswer(lines[0], true)
        one.recordAnswer(lines[1], false)
        val (mcq2, lines2) = byMcq.entries.first { it.value.size == 1 && it.key != mcq }
        one.recordAnswer(lines2[0], true)
        val complete = ProgressStore(MemStorage())
        complete.migrate(r.idMoves)
        complete.migrateNotes(r.noteMoves)
        complete.restore(one.backup(), r.idMoves, r.noteMoves, r.mcqLinks)
        val mv = { id: String -> r.idMoves.map[id] ?: id }
        assertEquals(setOf(mv("1:0:1"), mv("1:0:${k + 1}")), complete.done)
        assertEquals("from one-liners", complete.added["1:0:${k + 1}#-1"])
        assertEquals(false, complete.answers[mcq])
        assertEquals(true, complete.answers[mcq2])
        assertTrue(complete.answers.keys.none { it.startsWith("o") })
    }

    /** planmcq.json matches the plan and the MCQs shipped (tools/build_plan_mcq.py). */
    /** The magnifier's Google search works for every MCQ: a real query, no exam set phrases left in it. */
    @Test fun everyMcqHasAGoodSearch() {
        val repo = Repository { ctx.assets.open(it) }
        val all = runBlocking { (1..6).flatMap { b -> repo.mcq(b).rows.values.flatten() } }.distinctBy { it.id }
        val bad = mutableListOf<String>()
        val left = Regex("(?i)which of the following|is/are correct|select the correct|using the code|consider the following")
        val out = StringBuilder()
        all.forEachIndexed { i, q ->
            val s = com.appsc.prep.ui.components.mcqQuery(q)
            val words = s.split(' ').filter { it.isNotBlank() }
            if (words.size < 3 || words.size > 32 || left.containsMatchIn(s)) bad += "${q.id}\t$s"
            if (i % 400 == 0) out.append(q.id).append('\t').append(s).append('\n')
            assertTrue(com.appsc.prep.ui.components.googleUrl(s).length < 2000)
        }
        java.io.File("build/mcq-search-sample.txt").writeText(out.toString() + "\nBAD ${bad.size}\n" + bad.take(200).joinToString("\n"))
        assertTrue("${bad.size} of ${all.size} MCQs search badly, e.g. ${bad.take(5)}", bad.size * 1000 < all.size) // under 0.1%
    }

    @Test fun planMcqFileIsCurrent() {
        val repo = Repository { ctx.assets.open(it) }
        val books = runBlocking { (1..6).associateWith { repo.mcq(it) } }
        val fresh = com.appsc.prep.data.DueMcqs.planMcqs(repo.plan) { b, r -> books[b]!!.rows[r]?.map { it.id } ?: emptyList() }
        assertEquals(fresh.days.map { it.second }, repo.planMcqs.days.map { it.second })
        // the one-pager plan has every topic: every MCQ is on some day
        assertEquals(books.values.flatMap { b -> b.rows.values.flatten().map { it.id } }.toSet().size, repo.planMcqs.days.sumOf { it.second.size })
    }

    /** The MCQs tab: due MCQs from Day 1, Day 1 partly attempted. */
    @Test fun mcqsTab() {
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(MemStorage()), AndroidPlatform(ctx))
        val day1 = app.repo.planMcqs.days.first()
        day1.second.take(150).forEachIndexed { i, id -> app.store.recordAnswer(id, i % 4 != 0) }
        val pool = runBlocking { com.appsc.prep.ui.screens.duePool(app, day1.first.n) }
        if (java.time.LocalDate.now().isAfter(day1.first.date)) {
            assertEquals(day1.second.size - 150, pool.size)
            assertTrue(pool.none { app.store.attempted(it.id) })
        }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { com.appsc.prep.ui.screens.McqsScreen(nav) } } }
        rule.waitForIdle()
        rule.onNodeWithText("Due MCQs").assertExists()
        rule.onRoot().captureRoboImage("screenshots/complete/10_mcqs_tab.png")
    }

    /** The Today tab shows what is due from earlier plan days under today's practice, so due MCQs done count there. */
    @Test fun todayTabShowsDue() {
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(MemStorage()), AndroidPlatform(ctx))
        val today = java.time.LocalDate.now()
        val past = app.repo.planMcqs.days.filter { it.first.date.isBefore(today) }
        past.firstOrNull()?.second?.take(30)?.forEach { app.store.recordAnswer(it, true) }
        val status = com.appsc.prep.data.DueMcqs.status(app.repo.planMcqs, today, app.store::attempted)
        assertEquals(past.sumOf { it.second.size } - (if (past.isEmpty()) 0 else 30), status.due)
        runBlocking { app.repo.plan.days.forEach { d -> d.rows.forEach { app.repo.mcq(it.book) } } }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { com.appsc.prep.ui.screens.TodayScreen(nav) } } }
        rule.waitForIdle()
        if (app.repo.plan.days.any { it.date == today } && past.isNotEmpty()) {
            rule.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("Due MCQs"))
            rule.waitForIdle()
        }
        rule.onRoot().captureRoboImage("screenshots/complete/11_today_tab_due.png")
    }
}
