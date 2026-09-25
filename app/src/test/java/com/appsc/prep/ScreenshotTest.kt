package com.appsc.prep

import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.BooksScreen
import com.appsc.prep.ui.screens.DayScreen
import com.appsc.prep.ui.screens.Nav
import com.appsc.prep.ui.screens.PlanScreen
import com.appsc.prep.ui.screens.ProgressScreen
import com.appsc.prep.ui.screens.ReaderScreen
import com.appsc.prep.ui.screens.SectionScreen
import com.appsc.prep.ui.screens.TodayScreen
import com.appsc.prep.ui.theme.PrepTheme
import com.github.takahirom.roborazzi.captureRoboImage
import kotlinx.coroutines.runBlocking
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class ScreenshotTest {
    @get:Rule
    val rule = createComposeRule()

    private val nav = object : Nav {
        override fun day(n: Int) {}
        override fun row(book: Int, row: Int) {}
        override fun read(book: Int, row: Int, sec: Int) {}
        override fun book(id: Int) {}
        override fun back() {}
    }

    private fun shot(name: String, preload: Int? = null, content: @Composable () -> Unit) {
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val app = AppState(Repository(ctx), ProgressStore(ctx))
        if (preload != null) runBlocking { app.repo.book(preload) }
        rule.setContent {
            PrepTheme { CompositionLocalProvider(LocalApp provides app) { content() } }
        }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/$name.png")
    }

    @Test fun today() = shot("1_today") { TodayScreen(nav) }
    @Test fun plan() = shot("2_plan") { PlanScreen(nav) }
    @Test fun day1() = shot("3_day1") { DayScreen(1, nav) }
    @Test fun section() = shot("4_section", preload = 2) { SectionScreen(2, 0, nav) }
    @Test fun reader() = shot("5_reader", preload = 2) { ReaderScreen(2, 0, 0, nav) }
    @Test fun readerTable() = shot("6_reader_table", preload = 2) { ReaderScreen(2, 0, 1, nav) }
    @Test fun books() = shot("7_notes") { BooksScreen(nav) }
    @Test fun progress() = shot("8_progress") { ProgressScreen(nav) }
}
