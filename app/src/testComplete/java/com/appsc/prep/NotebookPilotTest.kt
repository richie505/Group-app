package com.appsc.prep

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.Repository
import com.appsc.prep.ui.components.NotebookPage
import com.github.takahirom.roborazzi.captureRoboImage
import kotlinx.coroutines.runBlocking
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** Notebook-style pages (the pilot): three pages of the full notes, drawn as hand-written notebook pages. */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w420dp-h1500dp-xxhdpi")
class NotebookPilotTest {
    @get:Rule val rule = createComposeRule()
    private val repo by lazy { Repository { ApplicationProvider.getApplicationContext<android.content.Context>().assets.open(it) } }

    private fun shot(name: String, book: Int, rowKey: String, secKey: String, doodle: String) {
        val bk = runBlocking { repo.book(book) }
        val row = bk.rows.first { rowKey in it.title }
        val sec = row.secs.first { secKey in it.title }
        rule.setContent { NotebookPage(sec.title, row.title, sec.blocks, doodle, Modifier.fillMaxWidth()) }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/notebook/$name.png")
    }

    @Test fun solarSystem() = shot("1_solar", 4, "universe and the solar system", "Universe and solar system", "solar")
    @Test fun basel() = shot("2_basel", 3, "Banking sector reforms", "Basel accords", "bank")
    @Test fun vicePresident() = shot("3_vice_president", 2, "Vice-President", "Vice-President: office", "chair")
}
