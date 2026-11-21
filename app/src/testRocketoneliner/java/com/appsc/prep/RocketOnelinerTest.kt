package com.appsc.prep

import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.Repository
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * APPSC Rocket One-liners: Group 1 and Group 2 topics, each with the one-liners made from its Rocket lecture notes
 * (tools/rocket_oneliner.py). Rerun the tool and update [MCQS] when the Rocket notes change.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class RocketOnelinerTest {
    private val repo by lazy { Repository { ApplicationProvider.getApplicationContext<android.content.Context>().assets.open(it) } }

    companion object {
        const val MCQS = 101_455 // tools/rocket_oneliner.py's total
    }

    @Test fun edition() {
        assertEquals("APPSC Rocket One-liners", repo.appName)
        assertTrue(repo.oneliner && repo.complete && !repo.revision)
        assertEquals(listOf("Group 1 Prelims", "Group 2"), repo.exams.map { it.title })
        // every syllabus line of both exams points at a topic of this app
        repo.exams.flatMap { it.subjects }.flatMap { it.groups }.flatMap { it.rows }
            .forEach { (b, r) -> assertTrue("$b:$r", repo.rowInfo(b, r) != null && repo.rowInfo(b, r)?.hidden == false) }
    }

    /** The MCQ count; every MCQ one line with 4 different options and an answer, filed under a page of its topic. */
    @Test fun everyMcqHasFourDistinctOptions() = runBlocking {
        var total = 0
        val ids = HashSet<String>()
        for (b in 1..6) {
            val book = repo.mcq(b)
            val notes = repo.book(b)
            for ((row, qs) in book.rows) {
                assertEquals("book $b row $row count", repo.rowInfo(b, row)?.questionCount, qs.size)
                val subs = book.subs[row].orEmpty()
                assertEquals("book $b row $row pages", qs.size, subs.size)
                assertTrue("book $b row $row: pages in range", subs.all { it in 0 until notes.rows[row].secs.size })
                for (q in qs) {
                    total++
                    assertTrue("${q.id}: one id", ids.add(q.id))
                    assertTrue("${q.id}: one line", '\n' !in q.stem && q.stem.isNotBlank() && q.stem.length <= 160)
                    assertEquals("${q.id}: 4 options", 4, q.options.size)
                    assertEquals("${q.id}: 4 distinct options ${q.options}", 4, q.options.map { it.trim().lowercase() }.distinct().size)
                    assertTrue("${q.id}: no blank option", q.options.none { it.isBlank() || "**" in it })
                    assertTrue("${q.id}: answer", q.answer in 0..3)
                    assertTrue("${q.id}: explanation", q.explanation.isNotBlank())
                }
            }
        }
        assertEquals(MCQS, total)
    }

    /** planmcq.json is built from these MCQs and the plan (tools/rocket_oneliner.py runs tools/build_plan_mcq.py). */
    @Test fun planMcqFileIsCurrent() = runBlocking {
        val books = (1..6).associateWith { repo.mcq(it) }
        val fresh = com.appsc.prep.data.DueMcqs.planMcqs(repo.plan) { b, row -> books[b]!!.rows[row]?.map { it.id } ?: emptyList() }
        assertEquals(fresh.days.map { it.second }, repo.planMcqs.days.map { it.second })
        assertEquals(MCQS, repo.planIds.size)
    }
}
