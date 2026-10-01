package com.appsc.prep

import com.appsc.prep.data.Repository
import com.appsc.prep.data.TableBlock
import com.appsc.prep.ui.screens.speakable
import com.appsc.prep.ui.screens.speechParts
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import androidx.test.core.app.ApplicationProvider

@RunWith(RobolectricTestRunner::class)
class SpeechTextTest {
    @Test fun shorthandIsWrittenOut() {
        assertEquals("Urbanisation or migration", speakable("Urbanisation/migration"))
        assertEquals("Act to year", speakable("Act → year"))
        assertEquals("Article 21 and Article 14", speakable("Art. 21 & Art. 14"))
        assertEquals("Residuary powers lay with the Governor-General.", speakable("Residuary powers lay with the Governor-General [GK]."))
        assertEquals("How it changes the family", speakable("How it changes the family (CDX)"))
    }

    /** The page in the user's screenshot: title first, then each table row as "Header: cell". */
    @Test fun tableIsReadRowByRow() {
        val repo = Repository { ApplicationProvider.getApplicationContext<android.content.Context>().assets.open(it) }
        val sec = runBlocking { repo.book(2) }.rows[106].secs[0]
        val parts = speechParts(sec.title, sec.blocks)
        assertTrue(parts.first().second.startsWith("Changing structure and urban families"))
        val table = sec.blocks.indexOfFirst { it is TableBlock }
        val first = parts.first { it.first == table }.second
        assertTrue(first, first.startsWith("Factor: Industrialisation. How it changes the family"))
        assertFalse(parts.any { "[GK]" in it.second || "(CDX)" in it.second })
    }
}
