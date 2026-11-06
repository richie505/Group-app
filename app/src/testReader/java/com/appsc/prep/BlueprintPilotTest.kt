package com.appsc.prep

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.test.core.app.ApplicationProvider
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.platform.AndroidPlatform
import com.appsc.prep.platform.PrefsStorage
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.BlockView
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.theme.C
import com.appsc.prep.ui.theme.PrepTheme
import com.github.takahirom.roborazzi.captureRoboImage
import kotlinx.coroutines.runBlocking
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode
import java.io.File

/**
 * The blueprint pilot (tools/blueprint_pilot.py) drawn with the app's own page blocks, one tall image per unit:
 * screenshots/blueprint/<n>.png. Skipped when the pilot has not been built.
 */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w400dp-h9000dp-xxhdpi")
class BlueprintPilotTest {
    @get:Rule val rule = createComposeRule()
    private val ctx get() = ApplicationProvider.getApplicationContext<android.content.Context>()
    private val pilot = File("../data/blueprint/pilot/book.json")

    private fun unit(n: Int) {
        assumeTrue(pilot.exists())
        val repo = Repository { name -> if (name == "book1.json") pilot.inputStream() else ctx.assets.open(name) }
        val book = runBlocking { repo.book(1) }
        assumeTrue(n < book.rows.size)
        val row = book.rows[n]
        val app = AppState(repo, ProgressStore(PrefsStorage(ctx)), AndroidPlatform(ctx))
        rule.setContent {
            PrepTheme {
                CompositionLocalProvider(LocalApp provides app) {
                    Column(Modifier.fillMaxWidth().wrapContentHeight().background(Color.White).testTag("unit").padding(vertical = 16.dp)) {
                        Text(
                            row.title,
                            style = TextStyle(fontSize = 22.sp, lineHeight = 28.sp, fontWeight = FontWeight.Bold, color = Color.Black),
                            modifier = Modifier.padding(horizontal = 20.dp),
                        )
                        row.secs.forEachIndexed { i, s ->
                            Spacer(Modifier.height(14.dp))
                            HorizontalDivider(color = C.Line)
                            Text(
                                "Page ${i + 1} · ${s.title}",
                                style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold, color = C.Accent),
                                modifier = Modifier.padding(start = 20.dp, end = 20.dp, top = 12.dp, bottom = 4.dp),
                            )
                            Column(Modifier.padding(horizontal = 12.dp)) { s.blocks.forEach { BlockView(it, 1f) } }
                        }
                    }
                }
            }
        }
        rule.waitForIdle()
        rule.onNodeWithTag("unit").captureRoboImage("screenshots/blueprint/${n + 1}.png")
    }

    @Test fun unit1() = unit(0)
    @Test fun unit2() = unit(1)
    @Test fun unit3() = unit(2)
}
