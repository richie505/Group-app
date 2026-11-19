package com.appsc.prep.lectures

import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onFirst
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performClick
import androidx.test.core.app.ApplicationProvider
import com.github.takahirom.roborazzi.captureRoboImage
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/** APPSC Lectures: both apps' lectures, subject-wise and topic-wise, each topic's slides in the viewer. */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h860dp-xxhdpi")
class LecturesTest {
    @get:Rule val rule = createAndroidComposeRule<LecturesActivity>()

    @Test fun everyLectureIsListedAndShipped() {
        val ctx = ApplicationProvider.getApplicationContext<android.content.Context>()
        val apps = loadIndex(ctx)
        assertEquals(listOf("APPSC Group 1 Prelims", "APPSC Group 2"), apps.map { it.name })
        assertEquals(6, apps[0].subjects.size)
        val all = apps.flatMap { a -> a.subjects.flatMap { it.topics } }
        assertTrue(all.size > 1800)
        assertTrue(all.all { it.slides > 0 })
        all.forEach { ctx.assets.open(it.file).close() }
    }

    @Test fun homeSubjectsTopics() {
        rule.onRoot().captureRoboImage("screenshots/lectures/1_home.png")
        rule.onAllNodesWithText("APPSC Group 1 Prelims").onFirst().performClick()
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/lectures/2_subjects.png")
        rule.onNode(hasText("History & Culture", substring = true)).performClick()
        rule.waitForIdle()
        rule.onRoot().captureRoboImage("screenshots/lectures/3_topics.png")
    }
}
