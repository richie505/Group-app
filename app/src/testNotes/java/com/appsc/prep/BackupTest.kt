package com.appsc.prep

import com.appsc.prep.data.DayLog
import com.appsc.prep.data.IdMoves
import com.appsc.prep.data.NoteMoves
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Saved
import com.appsc.prep.data.SpeechText
import com.appsc.prep.data.Storage
import com.appsc.prep.data.edited
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/** Backup file and restore (Progress screen), and the read-aloud safety net. */
class BackupTest {
    private class MemStorage : Storage {
        val sets = HashMap<String, Set<String>>()
        val strings = HashMap<String, String>()
        override fun getStringSet(key: String) = sets[key].orEmpty()
        override fun getString(key: String) = strings[key]
        override fun getFloat(key: String, default: Float) = default
        override fun putStringSet(key: String, value: Set<String>) { sets[key] = value }
        override fun putString(key: String, value: String) { strings[key] = value }
        override fun putFloat(key: String, value: Float) {}
    }

    private val moves = IdMoves("2.18", mapOf("2:5:9" to "2:5:3"), setOf("2:4:1"))

    @Test fun viewedAnswersAreNotSolvedAndHistorySurvivesRestore() {
        val phone = ProgressStore(MemStorage())
        phone.recordAnswer("n1", true) // right on its own
        phone.recordAnswer("n2", false) // wrong
        phone.markSeen("n3", viewed = true) // answer viewed first, then picked: not scored
        phone.markSeen("n4", viewed = false) // an MCQ without a key: practised, not "viewed"
        phone.recordAnswer("n2", true) // right on a retry
        assertEquals(com.appsc.prep.data.Mastery.MASTERED, phone.mastery("n1"))
        assertEquals(com.appsc.prep.data.Mastery.IMPROVING, phone.mastery("n2"))
        assertEquals(com.appsc.prep.data.Mastery.LEARNING, phone.mastery("n3"))
        assertEquals(com.appsc.prep.data.Mastery.NEW, phone.mastery("n4"))
        val sum = com.appsc.prep.data.PracticeSummary.of(phone.hist)
        assertEquals(2, sum.tried) // n3 viewed is not counted as solved
        assertEquals(1, sum.viewedOnly)
        val log = phone.dayLog()
        assertEquals(5, log.mcqs)
        assertEquals(1, log.viewed)
        assertEquals(4, log.own)
        // a new phone gets every history back from the backup
        val other = ProgressStore(MemStorage())
        other.restore(phone.backup(), IdMoves("", emptyMap(), emptySet()))
        assertEquals(phone.hist, other.hist)
        assertEquals(com.appsc.prep.data.Mastery.LEARNING, other.mastery("n3"))
    }

    @Test fun anOlderBackupGetsAHistoryOnRestore() {
        val older = """{"app":"APPSC Prep backup","format":1,"answers":["a1:1","a2:0","a3:1"],"seen":["a3","a4"],"missed":["a2","a3"]}"""
        val s = ProgressStore(MemStorage())
        s.restore(older, IdMoves("", emptyMap(), emptySet()))
        assertEquals("R", s.hist["a1"]?.outcomes)
        assertEquals("W", s.hist["a2"]?.outcomes)
        assertEquals("VWR", s.hist["a3"]?.outcomes)
        assertEquals("V", s.hist["a4"]?.outcomes)
        assertEquals(com.appsc.prep.data.Mastery.IMPROVING, s.mastery("a3"))
    }

    @Test fun dailyTargetsComeFromRecentDaysWithoutDebt() {
        // the reader's real log up to 4 Nov 2026 (both devices added up per day)
        val days = mapOf(
            "2026-10-22" to 754, "2026-10-24" to 420, "2026-10-26" to 327, "2026-10-27" to 1074, "2026-10-28" to 1029,
            "2026-10-29" to 1072, "2026-10-30" to 970, "2026-10-31" to 551, "2026-11-01" to 634, "2026-11-02" to 964,
            "2026-11-03" to 1111, "2026-11-04" to 922,
        ).mapValues { DayLog(mcqs = it.value) }
        val t = com.appsc.prep.data.DailyTarget.of(days, java.time.LocalDate.parse("2026-11-05"))
        assertEquals(600, t.standard)
        assertEquals(300, t.minimum)
        assertEquals(950, t.stretch)
        assertEquals(200, t.session)
        assertEquals(3, t.sessions)
        // three light days in a row bring it down; nothing is added for what was missed
        val light = days + mapOf("2026-11-05" to 200, "2026-11-06" to 150, "2026-11-07" to 300).mapValues { DayLog(mcqs = it.value) }
        val after = com.appsc.prep.data.DailyTarget.of(light, java.time.LocalDate.parse("2026-11-08"))
        assertTrue("${after.standard}", after.standard < t.standard)
        // a session: due revision first (at most a third), then new ones in order
        val ids = com.appsc.prep.data.DailyTarget.session(9, listOf("r1", "r2", "r3", "r4"), listOf("n1", "n2", "r1", "n3", "n4", "n5", "n6", "n7")) { false }
        assertEquals(listOf("r1", "r2", "r3", "n1", "n2", "n3", "n4", "n5", "n6"), ids)
    }

    @Test fun theReadersRealBackupRestores() {
        val path = System.getenv("APPSC_BACKUP") ?: return // run with APPSC_BACKUP=<a real backup file>
        val text = java.io.File(path).readText()
        val s = ProgressStore(MemStorage())
        val r = s.restore(text, IdMoves("", emptyMap(), emptySet()))
        val o = kotlinx.serialization.json.Json.parseToJsonElement(text).let { it as kotlinx.serialization.json.JsonObject }
        fun n(k: String) = (o[k] as kotlinx.serialization.json.JsonArray).size
        assertEquals(n("answers"), s.answers.size)
        assertEquals(n("done"), s.done.size)
        assertTrue(s.hist.size >= s.answers.size) // every answer has a history now
        // and survives its own backup again
        val again = ProgressStore(MemStorage())
        again.restore(s.backup(), IdMoves("", emptyMap(), emptySet()))
        assertEquals(s.answers, again.answers)
        assertEquals(s.hist, again.hist)
        assertEquals(s.done, again.done)
        java.io.File("build/real-backup-restore.txt").writeText(
            "answers ${s.answers.size}, done ${s.done.size}, hist ${s.hist.size}, read ${r.read}, " +
                com.appsc.prep.data.PracticeSummary.of(s.hist).toString(),
        )
    }

    @Test fun mcqCorrectionsAreShownKeptAndRestored() {
        val q = com.appsc.prep.data.Question(
            "y1", "Which led to English education?", emptyList(), listOf("and 2 only", "only", "and 3 only", "1, 2 and 3"),
            3, "UPSC 2018", false, "Old why.", emptyList(), solution = listOf("**Old** bullet"),
        )
        val phone = ProgressStore(MemStorage())
        val fix = com.appsc.prep.data.McqEdit(q.stem, listOf("1 and 2 only", "2 only", "1 and 3 only", "1, 2 and 3"), 2, "New why, with \"quotes\"\nand a line.")
        phone.setEdit("y1", fix)
        val shown = q.edited(phone.edits["y1"])
        assertEquals("1 and 3 only", shown.options[shown.answer])
        assertEquals("New why, with \"quotes\"\nand a line.", shown.explanation)
        assertTrue(shown.solution.isEmpty()) // the rewritten explanation replaces the old bullets
        // an unchanged explanation keeps the structured one
        assertEquals(listOf("**Old** bullet"), q.edited(fix.copy(explanation = "Old why.")).solution)
        // no key: unscored
        assertEquals('u', q.edited(fix.copy(answer = -1, noKey = true)).kind)

        val fresh = ProgressStore(MemStorage())
        fresh.restore(phone.backup(), moves)
        assertEquals(fix, fresh.edits["y1"])
        assertTrue(fresh.editsExport().contains("\"1 and 3 only\""))
        fresh.setEdit("y1", null)
        assertTrue(fresh.edits.isEmpty())
    }

    @Test fun pastedMarkdownExplanationIsLaidOut() {
        val md = "The correct answer is **Article 51-A**.\n### DPSP vs Duties\n| Feature | Article 48A | Article 51A(g) |\n|---|---|---|\n| Addressed To | The State | Every citizen |\n- one\n  - sub"
        assertTrue(com.appsc.prep.data.MarkdownText.looksLike(md))
        val b = com.appsc.prep.data.MarkdownText.blocks(md)
        val t = b.filterIsInstance<com.appsc.prep.data.TableBlock>().single()
        assertEquals(listOf("Feature", "Article 48A", "Article 51A(g)"), t.head.map { c -> c.joinToString("") { it.text } })
        assertEquals("Every citizen", t.rows[0][2].joinToString("") { it.text })
        val first = b[0] as com.appsc.prep.data.TextBlock
        assertTrue(first.runs.any { it.text == "Article 51-A" && it.bold })
        assertEquals(listOf('p', 'h', 'b', 's'), b.filterIsInstance<com.appsc.prep.data.TextBlock>().map { it.kind })
        assertTrue(!com.appsc.prep.data.MarkdownText.looksLike("Plain text explanation. Article 51A says so."))
    }

    @Test fun mcqSearchAsksTheQuestionNotTheCodes() {
        val q = com.appsc.prep.data.Question(
            "y2", "Which led to English education?\n1. Charter Act of 1813\n2. Orientalist Controversy\nSelect the correct answer using the code given below:",
            emptyList(), listOf("1 only", "2 only", "Both 1 and 2", "Neither 1 nor 2"), 2, "", false, "", emptyList(),
        )
        assertEquals("Which led to English education? Charter Act of 1813 Orientalist Controversy", com.appsc.prep.ui.components.mcqQuery(q))
        val s = q.copy(stem = "Which of the following statements regarding NITI Aayog is/are correct?\n1. It replaced the Planning Commission.\n2. It was set up by an Act.\nSelect the correct answer using the code given below:")
        assertEquals("NITI Aayog It replaced the Planning Commission. It was set up by an Act", com.appsc.prep.ui.components.mcqQuery(s))
        val r = q.copy(stem = "Diego Garcia is situated in:", options = listOf("Indian Ocean", "Pacific Ocean", "Arctic Ocean", "Atlantic Ocean"))
        assertEquals("Diego Garcia is situated in Indian Ocean Pacific Ocean Arctic Ocean Atlantic Ocean", com.appsc.prep.ui.components.mcqQuery(r))
        assertTrue(com.appsc.prep.ui.components.mcqPrompt(r).contains("(1) Indian Ocean"))
        assertEquals(
            "Diego Garcia is situated in:\n(a) Indian Ocean\n(b) Pacific Ocean\n(c) Arctic Ocean\n(d) Atlantic Ocean",
            com.appsc.prep.ui.components.mcqCopyText(r),
        )
    }

    @Test fun backupComesBackOnANewPhone() {
        val phone = ProgressStore(MemStorage())
        phone.migrate(moves)
        phone.setDone("1:0:0", true)
        phone.setDone("2:5:3", true)
        phone.toggleSaved(Saved("3:1:2", "GST", "Indirect taxes"))
        phone.recordAnswer("n1-5", true)
        phone.setAdded("2:7:1#4", "NCRB 2022: MP, Maharashtra and UP lead.\nSecond line.")
        val file = phone.backup()

        // a new phone that already has a little of its own
        val fresh = ProgressStore(MemStorage())
        fresh.migrate(moves)
        fresh.setDone("4:0:0", true)
        fresh.recordAnswer("n1-5", false)
        val r = fresh.restore(file, moves)

        assertEquals(setOf("1:0:0", "2:5:3", "4:0:0"), fresh.done) // nothing lost, nothing doubled
        assertEquals(listOf("3:1:2"), fresh.saved.map { it.id })
        assertEquals(true, fresh.answers["n1-5"]) // the backup's answer wins
        assertEquals("NCRB 2022: MP, Maharashtra and UP lead.\nSecond line.", fresh.added["2:7:1#4"])
        assertEquals(ProgressStore.Restored(read = 2, saved = 1, answers = 1, notes = 1), r)
        assertTrue(fresh.streak() >= 1)

        // restoring the same file again adds nothing new
        assertEquals(0, fresh.restore(file, moves).read)
    }

    /** Wrong answers and answers seen first need practice; a later right answer clears them but stays a retry. */
    @Test fun mcqsThatNeedPracticeAndRetries() {
        val phone = ProgressStore(MemStorage())
        phone.recordAnswer("n1-1", true)
        phone.recordAnswer("n1-2", false)
        phone.markSeen("n1-3")
        assertEquals(listOf(false, true, true), listOf("n1-1", "n1-2", "n1-3").map(phone::needsPractice))
        phone.recordAnswer("n1-2", true)
        phone.recordAnswer("n1-3", true)
        assertEquals(listOf(false, false, false), listOf("n1-1", "n1-2", "n1-3").map(phone::needsPractice))
        assertEquals(setOf("n1-2"), phone.missed)

        val fresh = ProgressStore(MemStorage())
        fresh.restore(phone.backup(), moves)
        assertEquals(setOf("n1-2"), fresh.missed)
    }

    @Test fun timeOnEachPageComesBackOnANewPhone() {
        val phone = ProgressStore(MemStorage())
        phone.addStudyTime(notes = true, seconds = 900, what = "n:2:77:0")
        phone.practising = "q:sub:2:77:0"
        phone.recordAnswer("n2-1", true)
        phone.recordAnswer("n2-2", false)
        phone.addStudyTime(notes = false, seconds = 300, what = "q:sub:2:77:0")
        assertEquals(com.appsc.prep.data.Spent(900, 0), phone.spentOn()["n:2:77:0"])
        assertEquals(com.appsc.prep.data.Spent(300, 2), phone.spentOn()["q:sub:2:77:0"])
        val file = phone.backup()

        val fresh = ProgressStore(MemStorage())
        fresh.addStudyTime(notes = true, seconds = 60, what = "n:2:77:0")
        fresh.restore(file, moves)
        assertEquals(com.appsc.prep.data.Spent(960, 0), fresh.spentOn()["n:2:77:0"]) // both phones' time
        fresh.restore(file, moves)
        assertEquals(com.appsc.prep.data.Spent(960, 0), fresh.spentOn()["n:2:77:0"]) // the same file twice counts once
    }

    @Test fun activityLogAddsUpAcrossDevices() {
        val phone = ProgressStore(MemStorage())
        phone.recordAnswer("n1-1", true)
        phone.recordAnswer("n1-2", false)
        phone.markSeen("n1-3")
        phone.addStudyTime(notes = true, seconds = 600)
        phone.addStudyTime(notes = false, seconds = 300)
        assertEquals(DayLog(mcqs = 3, correct = 1, notesSec = 600, mcqSec = 300), phone.dayLog())

        val desktop = ProgressStore(MemStorage())
        desktop.recordAnswer("n2-1", true)
        desktop.addStudyTime(notes = false, seconds = 120)
        desktop.restore(phone.backup(), moves)
        val both = DayLog(mcqs = 4, correct = 2, notesSec = 600, mcqSec = 420)
        assertEquals(both, desktop.dayLog())
        desktop.restore(phone.backup(), moves) // the same backup twice counts once
        assertEquals(both, desktop.dayLog())

        // back on the phone: the desktop's file carries the phone's own log too, which is not counted twice
        phone.restore(desktop.backup(), moves)
        assertEquals(both, phone.dayLog())
    }

    @Test fun ownNotesFollowRewrittenPages() {
        val round1 = NoteMoves(listOf("b2-1" to mapOf("2:5:0#8" to "2:5:0#3")))
        val both = NoteMoves(round1.rounds + ("b2-2" to mapOf("2:5:0#3" to "2:5:0#1")))
        val phone = ProgressStore(MemStorage())
        phone.setAdded("2:5:0#8", "found it")
        val oldFile = phone.backup() // made before any rewrite
        phone.migrateNotes(round1)
        assertEquals("found it", phone.added["2:5:0#3"])
        phone.migrateNotes(round1) // once only
        assertEquals(setOf("2:5:0#3"), phone.added.keys)
        phone.migrateNotes(both)
        assertEquals(setOf("2:5:0#1"), phone.added.keys)

        // an old backup's notes are moved through every round; a new one's only through the rounds it lacks
        val desktop = ProgressStore(MemStorage())
        desktop.migrateNotes(both)
        desktop.restore(oldFile, moves, both)
        assertEquals(setOf("2:5:0#1"), desktop.added.keys)
        val laptop = ProgressStore(MemStorage())
        laptop.migrateNotes(both)
        laptop.restore(phone.backup(), moves, both)
        assertEquals(setOf("2:5:0#1"), laptop.added.keys)
    }

    @Test fun oldBackupFollowsTheRegroupedPages() {
        // a backup from before the notes were regrouped (no ids version) uses the old page ids
        val old = """{"app":"APPSC Prep backup","format":1,"ids":"","done":["2:5:9","2:4:1"],"saved":["0\t2:5:9\tPOCSO\tChild rights"]}"""
        val store = ProgressStore(MemStorage())
        store.migrate(moves)
        store.restore(old, moves)
        assertEquals(setOf("2:5:3"), store.done) // moved; the merged page's mark is dropped
        assertEquals(listOf("2:5:3"), store.saved.map { it.id })
    }

    @Test fun otherFilesAreRefused() {
        val store = ProgressStore(MemStorage())
        for (bad in listOf("hello", "{}", """{"app":"Something else"}""")) {
            val e = runCatching { store.restore(bad, moves) }.exceptionOrNull()
            assertTrue(bad, e is IllegalArgumentException && e.message!!.contains("not an APPSC Prep backup"))
        }
        assertTrue(store.done.isEmpty())
    }

    @Test fun aFailingReadAloudRuleIsSkippedOnPhones() {
        val was = SpeechText.strict
        try {
            SpeechText.strict = false // as on a phone
            assertEquals("Chandragupta II", SpeechText.safely("Chandragupta II") { Regex("(?<=[a-z]{2,} )II").replace(it, ""); throw IllegalStateException("bad rule") })
            assertEquals("deep", SpeechText.safely("deep") { throw StackOverflowError() })
            SpeechText.strict = true // tests: a broken rule must fail
            assertTrue(runCatching { SpeechText.safely("x") { throw IllegalStateException() } }.isFailure)
        } finally {
            SpeechText.strict = was
        }
    }
}
