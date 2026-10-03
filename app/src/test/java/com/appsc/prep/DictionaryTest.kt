package com.appsc.prep

import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.Repository
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class DictionaryTest {
    private val repo = Repository { ApplicationProvider.getApplicationContext<android.content.Context>().assets.open(it) }
    private val dict get() = repo.dictionary

    @Test fun wordsFromTheNotes() {
        val e = dict.lookup("dyarchy")!!
        assertEquals("dyarchy", e.word)
        assertTrue(e.senses.first().definition.contains("two joint rulers"))
        assertTrue(dict.lookup("Federalism")!!.senses.first().definition.contains("federal"))
        assertTrue(dict.lookup(" sovereign, ")!!.senses.any { it.definition.contains("not controlled by outside forces") })
    }

    @Test fun otherFormsFindTheDictionaryWord() {
        assertEquals("government", dict.lookup("governments")!!.word)
        assertEquals("abolish", dict.lookup("abolished")!!.word)
        assertEquals("policy", dict.lookup("policies")!!.word)
        assertEquals("migrate", dict.lookup("migrating")!!.word)
        assertEquals("disintegration", dict.lookup("disintegration.")!!.word)
    }

    @Test fun shortFormsFromTheNotes() {
        assertEquals("World Trade Organization", dict.lookup("WTO")!!.shortForm)
        assertEquals("Visakhapatnam-Chennai Industrial Corridor", dict.lookup("VCIC")!!.shortForm)
        assertNull(dict.lookup("qwxzv"))
    }

    @Test fun notesHeadingsMentioningAWord() {
        val hits = runBlocking { repo.findInNotes("Dyarchy") }
        assertTrue(hits.isNotEmpty())
        assertTrue(hits.all { "dyarchy" in it.title.lowercase() })
    }
}
