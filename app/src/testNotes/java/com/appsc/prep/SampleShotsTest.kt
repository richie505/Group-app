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

    private fun shot(name: String, book: Int = 2, content: @androidx.compose.runtime.Composable () -> Unit) {
        val tag = System.getProperty("sample.tag") ?: return
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        runBlocking { app.repo.book(book); app.repo.mcq(book) }
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { content() } } }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/sample/${tag}_$name.png")
    }

    @Test fun section() = shot("0_topic") { SectionScreen(2, 106, nav) }
    @Test fun page1() = shot("1_page") { ReaderScreen(2, 106, 1, nav) }
    @Test fun page2() = shot("2_page") { ReaderScreen(2, 106, 2, nav) }
    @Test fun page5() = shot("3_page") { ReaderScreen(2, 106, 5, nav) }
    @Test fun marriage() = shot("4_marriage_topic") { SectionScreen(2, 107, nav) }
    @Test fun marriage1() = shot("5_marriage_page") { ReaderScreen(2, 107, 0, nav) }
    @Test fun regionAp() = shot("6_regionalism_ap_topic") { SectionScreen(2, 120, nav) }
    @Test fun regionAp2() = shot("7_regionalism_ap_page") { ReaderScreen(2, 120, 2, nav) }

    // 2.56: one topic per other book
    @Test fun history() = shot("b1_topic", 1) { SectionScreen(1, 10, nav) }
    @Test fun history1() = shot("b1_page", 1) { ReaderScreen(1, 10, 1, nav) }
    @Test fun economy() = shot("b3_topic", 3) { SectionScreen(3, 80, nav) }
    @Test fun economy1() = shot("b3_page", 3) { ReaderScreen(3, 80, 1, nav) }
    @Test fun geography() = shot("b4_topic", 4) { SectionScreen(4, 36, nav) }
    @Test fun geography1() = shot("b4_page", 4) { ReaderScreen(4, 36, 1, nav) }
    @Test fun science() = shot("b5_topic", 5) { SectionScreen(5, 42, nav) }
    @Test fun science1() = shot("b5_page", 5) { ReaderScreen(5, 42, 1, nav) }
    @Test fun current() = shot("b6_topic", 6) { SectionScreen(6, 14, nav) }
    @Test fun current1() = shot("b6_page", 6) { ReaderScreen(6, 14, 1, nav) }
}
