package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.platform.PrefsStorage
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.ReaderScreen
import com.appsc.prep.ui.screens.SectionScreen
import com.appsc.prep.ui.theme.PrepTheme
import com.github.takahirom.roborazzi.captureRoboImage
import kotlinx.coroutines.runBlocking
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** Sample screenshots of one topic (-Psample.tag=before|after). Not a pass/fail test. */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class SampleShotsTest {
    @get:Rule val rule = createComposeRule()
    private val nav = object : com.appsc.prep.ui.screens.Nav {
        override fun quiz(kind: String, book: Int, index: Int, mode: String, sub: Int) {}
        override fun day(n: Int) {}
        override fun row(book: Int, row: Int) {}
        override fun read(book: Int, row: Int, sec: Int) {}
        override fun book(id: Int) {}
        override fun back() {}
    }

    private fun shot(name: String, content: @androidx.compose.runtime.Composable () -> Unit) {
        val tag = System.getProperty("sample.tag") ?: return
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(2); app.repo.mcq(2) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { content() } } }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/sample/${tag}_$name.png")
    }

    @Test fun section() = shot("0_topic") { SectionScreen(2, 106, nav) }
    @Test fun page1() = shot("1_page") { ReaderScreen(2, 106, 1, nav) }
    @Test fun page2() = shot("2_page") { ReaderScreen(2, 106, 2, nav) }
    @Test fun page5() = shot("3_page") { ReaderScreen(2, 106, 5, nav) }
}
