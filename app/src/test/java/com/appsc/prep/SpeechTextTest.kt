package com.appsc.prep

import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.Repository
import com.appsc.prep.data.SpeechText
import com.appsc.prep.data.TableBlock
import com.appsc.prep.data.TextBlock
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class SpeechTextTest {
    private val repo = Repository { ApplicationProvider.getApplicationContext<android.content.Context>().assets.open(it) }

    @Before fun loadNotesAbbreviations() {
        repo.abbreviations
    }

    private fun say(text: String, book: Int = 2) = SpeechText.speakable(text, book)

    @Test fun citationsAreNotRead() {
        assertEquals("Residuary powers lay with the Governor-General.", say("Residuary powers lay with the Governor-General [GK]."))
        assertEquals("The federation never came into being.", say("The federation never came into being (CDI; APP)."))
        assertEquals("Grants rose by 40%.", say("Grants rose by 40% (IYB 2026, LENS Apr 2026)."))
        assertEquals("Work rather than real job creation.", say("Work rather than real job creation (TH, 7 Sep 2026)."))
        assertEquals("The answer is Chennai.", say("The answer is Chennai (APPSC-G2 2025 key)."))
        // a bracket with real content keeps the content
        assertEquals("Franchise rose to 14% (some texts say about 10%).", say("Franchise rose to 14% (UPSC notes; some texts say about 10%)."))
    }

    @Test fun shortFormsAreSaidInFull() {
        assertEquals("Section 6 of the Act", say("Sec 6 of the Act"))
        assertEquals("Article 21 and Article 14", say("Art. 21 & Art. 14"))
        assertEquals("India joined the World Trade Organization in 1995", say("India joined the WTO in 1995"))
        assertEquals("Group 2 and Schedule 7", say("Group-II and Schedule VII"))
        assertEquals("5,000 crore rupees", say("₹5,000 cr"))
        assertEquals("Urbanisation or migration", say("Urbanisation/migration"))
        // a short form right after its full form is not read twice
        assertEquals("Fiscal Deficit is 4.4%", say("Fiscal Deficit (FD) is 4.4%"))
        // defined in the notes (abbr.json)
        assertTrue(say("the VCIC nodes", 3).contains("Visakhapatnam-Chennai Industrial Corridor"))
    }

    @Test fun scDependsOnTheWordsAround() {
        assertTrue(say("The SC bench upheld the verdict").contains("Supreme Court"))
        assertTrue(say("reservation of seats for SC communities", 3).contains("Scheduled Caste"))
        assertTrue(say("SC/ST women").contains("Scheduled Caste and Scheduled Tribe"))
        assertTrue(say("SCs and STs").contains("Scheduled Castes and Scheduled Tribes"))
    }

    /** The page in the user's screenshot: title first, then each table row as "Header: cell". */
    @Test fun tableIsReadRowByRow() {
        val sec = runBlocking { repo.book(2) }.rows[106].secs[0]
        val parts = SpeechText.parts(sec.title, sec.blocks, 2)
        assertTrue(parts.first().second.startsWith("Changing structure and urban families"))
        val table = sec.blocks.indexOfFirst { it is TableBlock }
        val first = parts.first { it.first == table }.second
        assertTrue(first, first.startsWith("Factor: Industrialisation. How it changes the family"))
    }

    /** Across all six books, almost no citation code is left in what is spoken. */
    @Test fun wholeNotesHaveNoCitations() {
        val codes = Regex("""\b(CDI|CDX|APP|APHQ|IYB|APPCA|LENS|LENSD|CDCA|VIS|PT365)\b|\[GK""")
        var spoken = 0; var left = 0; var before = 0
        for (b in 1..6) {
            for (row in runBlocking { repo.book(b) }.rows) for (s in row.secs) {
                val raw = s.blocks.filterIsInstance<TextBlock>().joinToString(" ") { t -> t.runs.joinToString("") { it.text } }
                before += codes.findAll(raw).count()
                SpeechText.parts(s.title, s.blocks, b).forEach { (_, t) -> spoken++; left += codes.findAll(t).count() }
            }
        }
        println("read-aloud: $spoken parts; citation codes in the notes $before, left when spoken $left")
        assertTrue("left $left of $before", left * 50 < before)
    }

}
