package com.appsc.prep

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.hasScrollToNodeAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performScrollToNode
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.data.Storage
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.Nav
import com.appsc.prep.ui.theme.PrepTheme
import com.github.takahirom.roborazzi.captureRoboImage
import kotlinx.coroutines.runBlocking
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** The reader's case: Day 19 with 96 of its MCQs attempted, 90 due MCQs done, a daily target of 500. */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class SyncShotsTest {
    @get:Rule val rule = createComposeRule()
    private val ctx get() = ApplicationProvider.getApplicationContext<android.content.Context>()
    private val nav = object : Nav {
        override fun quiz(kind: String, book: Int, index: Int, mode: String, sub: Int) {}
        override fun day(n: Int) {}
        override fun row(book: Int, row: Int) {}
        override fun read(book: Int, row: Int, sec: Int) {}
        override fun book(id: Int) {}
        override fun back() {}
    }
    private class Mem : Storage {
        val sets = HashMap<String, Set<String>>(); val strings = HashMap<String, String>()
        override fun getStringSet(key: String) = sets[key].orEmpty()
        override fun getString(key: String) = strings[key]
        override fun getFloat(key: String, default: Float) = default
        override fun putStringSet(key: String, value: Set<String>) { sets[key] = value }
        override fun putString(key: String, value: String) { strings[key] = value }
        override fun putFloat(key: String, value: Float) {}
    }

    private fun app(): AppState {
        val app = AppState(Repository { ctx.assets.open(it) }, ProgressStore(Mem()), AndroidPlatform(ctx))
        val today = java.time.LocalDate.now()
        val days = app.repo.planMcqs.days
        days.first { it.first.date == today }.second.take(96).forEachIndexed { i, id -> app.store.recordAnswer(id, i % 6 != 0) }
        days.filter { it.first.date.isBefore(today) }.take(2).flatMap { it.second.drop(150).take(45) }
            .forEach { app.store.recordAnswer(it, true) }
        runBlocking { (1..6).forEach { app.repo.mcq(it) } }
        return app
    }

    @Test fun todayTab() {
        val app = app()
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { com.appsc.prep.ui.screens.TodayScreen(nav) } } }
        rule.waitForIdle()
        rule.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("Due MCQs"))
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/sync/today_tab.png")
    }

    @Test fun mcqsTab() {
        val app = app()
        rule.setContent { PrepTheme { CompositionLocalProvider(LocalApp provides app) { com.appsc.prep.ui.screens.McqsScreen(nav) } } }
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/sync/mcqs_tab.png")
    }
}
