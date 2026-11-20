package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.hasScrollToNodeAction
import androidx.compose.ui.test.performScrollToNode
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.platform.PrefsStorage
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.Nav
import com.appsc.prep.ui.theme.PrepTheme
import com.github.takahirom.roborazzi.captureRoboImage
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** APPSC Group 2 Slides: Group 2 with each page's notes as its lecture slides; the page keeps its MCQs. */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class Group2SlidesTest {
    @get:Rule val rule = createComposeRule()
    private val ctx get() = ApplicationProvider.getApplicationContext<android.content.Context>()
    private val repo by lazy { Repository { ctx.assets.open(it) } }
    private val nav = object : Nav {
        override fun quiz(kind: String, book: Int, index: Int, mode: String, sub: Int) {}
        override fun day(n: Int) {}
        override fun row(book: Int, row: Int) {}
        override fun read(book: Int, row: Int, sec: Int) {}
        override fun book(id: Int) {}
        override fun back() {}
    }

    @Test fun itIsTheSlidesEdition() {
        assertEquals("g2", repo.slides)
        // every listed topic has its slides
        repo.index.forEach { b -> b.rows.filter { !it.hidden }.forEach { r -> ctx.assets.open("lec/g2/${b.id}/${r.index}.html").close() } }
    }

    @Test fun aPageShowsWatchSlidesAndItsMcqs() {
        runBlocking { repo.book(1); repo.mcq(1) }
        val app = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { com.appsc.prep.ui.screens.ReaderScreen(1, 189, 2, nav) } } }
        rule.waitForIdle()
        rule.onNodeWithText("Watch slides", substring = true).assertExists()
        rule.onRoot().captureRoboImage("screenshots/group2slides/page_top.png")
        rule.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("This subsection's", substring = true))
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/group2slides/page_mcqs.png")
    }
}
