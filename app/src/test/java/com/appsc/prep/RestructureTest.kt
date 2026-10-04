package com.appsc.prep

import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.Acronyms
import com.appsc.prep.data.IdMoves
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.data.Run
import com.appsc.prep.data.Saved
import com.appsc.prep.data.SpeechText
import com.appsc.prep.data.Storage
import com.appsc.prep.data.TextBlock
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

/** Repeated topics merged (tools/merge_topics.py), repeated facts cut (tools/dedup_notes.py), full forms added. */
@RunWith(RobolectricTestRunner::class)
class RestructureTest {
    private val repo = Repository { ApplicationProvider.getApplicationContext<android.content.Context>().assets.open(it) }

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

    @Test fun eachTopicOnce() = runBlocking {
        // POCSO and the JJ Act were subsections of both "Child rights" and the JJ/POCSO section
        val b2 = repo.book(2)
        val childRights = b2.rows.first { it.title.startsWith("Child rights") }
        val jj = b2.rows.first { it.title.startsWith("Juvenile Justice Act 2015, POCSO") }
        assertTrue(childRights.secs.none { it.title.startsWith("POCSO Act") || it.title.startsWith("Juvenile Justice Act") })
        assertTrue(jj.secs.any { it.title.startsWith("POCSO Act") })
        // every page link and MCQ points at a page that exists
        for (b in 1..6) {
            val bk = repo.book(b)
            for (r in bk.rows) {
                assertTrue(r.secs.isNotEmpty())
                for (s in r.secs) for (c in s.coveredIn) assertTrue("$c", c[2] < repo.book(c[0]).rows[c[1]].secs.size)
                assertEquals(r.secs.size, repo.rowInfo(b, r.index)!!.subsectionCount)
            }
            val mcq = repo.mcq(b)
            for (r in bk.rows) for (i in r.secs.indices) mcq.subCount(r.index, i)
        }
    }

    @Test fun readMarksFollowTheirPage() {
        val store = ProgressStore(MemStorage())
        store.setDone("2:137:9", true) // merged into 2:138:0
        store.setDone("2:137:11", true) // renumbered to 2:137:9
        store.setDone("1:0:0", true) // unchanged
        store.toggleSaved(Saved("2:137:11", "Adoption", "Child rights"))
        store.migrate(repo.idMoves)
        assertEquals(setOf("2:137:9", "1:0:0"), store.done)
        assertEquals("2:137:9", store.saved.single().id)
        // once per version
        store.setDone("2:137:10", true)
        store.migrate(repo.idMoves)
        assertTrue("2:137:10" in store.done)
        store.migrate(IdMoves("", emptyMap(), emptySet()))
    }

    @Test fun shortFormsGetTheirFullForm() {
        repo.abbreviations
        repo.checkedAcronyms
        val blocks = Acronyms.annotate(
            listOf(
                TextBlock('b', listOf(Run("NCPCR monitors the RTE Act; NCPCR also hears complaints.", 0))),
                TextBlock('b', listOf(Run("Fiscal Deficit (FD) and SC reservation in seats; quota for SC students.", 0))),
            ),
            book = 2,
        )
        val first = (blocks[0] as TextBlock).runs
        val shown = first.joinToString("") { it.text }
        assertTrue(shown, shown.startsWith("NCPCR (National Commission for Protection of Child Rights) monitors"))
        assertEquals(1, Regex("""\(National Commission""").findAll(shown).count()) // first time only
        val second = (blocks[1] as TextBlock).runs.joinToString("") { it.text }
        assertFalse(second, second.contains("FD (")) // defined right there
        assertTrue(second, second.contains("SC (Scheduled Caste)"))
        // a meaning from another page shows only when this page is about it
        val jj = Acronyms.annotate(listOf(TextBlock('b', listOf(Run("JJB and CWC in every district.", 0)))), 2, "Juvenile Justice Act")
        assertFalse(jj.toString(), (jj[0] as TextBlock).runs.joinToString("") { it.text }.contains("Water"))
        val dam = Acronyms.annotate(listOf(TextBlock('b', listOf(Run("CWC monitors reservoir water levels.", 0)))), 4, "Dams")
        assertTrue((dam[0] as TextBlock).runs.joinToString("") { it.text }.contains("CWC (Central Water Commission)"))
        fun shown(text: String, book: Int) = (Acronyms.annotate(listOf(TextBlock('b', listOf(Run(text, 0)))), book)[0] as TextBlock).runs.joinToString("") { it.text }
        assertTrue(shown("The 101st CAA inserted Art. 246A.", 2).contains("CAA (Constitutional Amendment Act)"))
        assertTrue(shown("Protests against the CAA in 2019.", 2).contains("CAA (Citizenship Amendment Act)"))
        assertTrue(shown("ASI excavated the site in 1921.", 1).contains("(Archaeological Survey of India)"))
        assertTrue(shown("AP's RTGS dashboard tracks grievances.", 4).contains("(Real Time Governance Society)"))
        assertTrue(shown("Two CJIs retired in 2025.", 2).contains("(Chief Justices of India)"))
        // read-aloud says each NCPCR in full already: the added full form is not read again (2, not 3)
        val spoken = SpeechText.parts("t", blocks, 2).joinToString(" ") { it.second }
        assertEquals(spoken, 2, Regex("National Commission for Protection of Child Rights").findAll(spoken).count())
    }

    /** One checked list and the whole page decide short forms, on the page and in read-aloud alike. */
    @Test fun shortFormsByPage() {
        repo.abbreviations
        repo.checkedAcronyms
        fun spoken(text: String, book: Int, context: String = "") =
            SpeechText.parts("t", listOf(TextBlock('b', listOf(Run(text, 0)))), book, context).joinToString(" ") { it.second }
        fun says(text: String, book: Int, expect: String, context: String = "") {
            val out = spoken(text, book, context)
            assertTrue("$text -> $out", out.contains(expect))
        }
        // CWC: three meanings in the notes
        val jj = spoken("JJB and CWC in every district, each with at least one woman member.", 2, "Juvenile Justice Act 2015")
        assertTrue(jj, jj.contains("Child Welfare Committee") && !jj.contains("Water"))
        says("CWC clears dam and reservoir projects on inter-state rivers.", 4, "Central Water Commission")
        says("The CWC authorised Gandhi to launch civil disobedience.", 1, "Congress Working Committee")
        // others the old lists got wrong
        says("Lytton passed the VPA; Ripon repealed it.", 1, "Vernacular Press Act")
        says("GPS issued coins; his mother Balasri's Nasik inscription.", 1, "Gautamiputra Satakarni")
        says("The CWC and NCM were led from Wardha.", 1, "Non-Cooperation Movement")
        says("Members are elected by PR through the single transferable vote.", 2, "proportional representation")
        says("Article 51A lists the FDs.", 2, "Fundamental Duties")
        says("Fiscal targets cut the FD to 4.4% of GDP.", 3, "fiscal deficit")
        says("2.35 lakh MT rice per month.", 3, "metric tonnes")
        says("KWDT-II allotted 196 TMC to AP from the Krishna.", 4, "thousand million cubic feet")
        says("Mamata Banerjee's TMC won Bengal.", 2, "Trinamool Congress")
        says("The MPC (Art. 243ZE) prepares the draft plan.", 2, "Metropolitan Planning Committee")
        says("The MPC kept the repo rate at 5.5%.", 3, "Monetary Policy Committee")
        // names and labels stay as written
        // mixed case; spelled out elsewhere on the page is no reason to skip it here
        val mole = Acronyms.annotate(
            listOf(
                TextBlock('b', listOf(Run("Ministry of Labour and Employment, launched 2017.", 0))),
                TextBlock('b', listOf(Run("NCLP: run by MoLE since 1988; MoSJE and MeitY too; DCPUs in districts.", 0))),
            ),
            2, "PENCIL portal and National Child Labour Project",
        )
        val second2 = (mole[1] as TextBlock).runs.joinToString("") { it.text }
        assertTrue(second2, second2.contains("NCLP (National Child Labour Project)"))
        assertTrue(second2, second2.contains("MoLE (Ministry of Labour and Employment)"))
        assertTrue(second2, second2.contains("MoSJE (Ministry of Social Justice and Empowerment)"))
        assertTrue(second2, second2.contains("MeitY (Ministry of Electronics and Information Technology)"))
        assertTrue(second2, second2.contains("DCPUs (District Child Protection Units)"))
        says("Run by MoLE; NGOs and McDonald stayed.", 2, "Ministry of Labour and Employment")
        val first = Acronyms.annotate(listOf(TextBlock('b', listOf(Run("FIRST Telugu inscription", 0)))), 1)
        assertEquals("FIRST Telugu inscription", (first[0] as TextBlock).runs.joinToString("") { it.text })
    }
}
