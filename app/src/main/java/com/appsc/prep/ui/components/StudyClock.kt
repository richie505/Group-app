package com.appsc.prep.ui.components

import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.pointer.PointerEventPass
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalWindowInfo
import kotlinx.coroutines.delay

/** What the reader is doing on a route, for the study-time log: notes, MCQs, or neither (null). */
fun studyKind(route: String?): Boolean? = when {
    route == null -> null
    route.startsWith("read/") -> true
    route.startsWith("quiz/") -> false
    else -> null
}

object StudyClock {
    /** Off in screenshot tests, where a clock that never stops would keep the UI from going idle. */
    @Volatile var on = System.getProperty("prep.strict") != "true"
}

/** No touch, click, scroll or mouse move for this long and the time stops counting (the app was left open). */
const val IDLE_MS = 5 * 60_000L

/**
 * Records study time, on the notes or on MCQs ([studyKind] of the current route), while the app is in front and
 * used. Listening to read-aloud counts as notes time, even with the screen off. Only records; there is no target.
 */
fun Modifier.studyClock(route: () -> String?): Modifier = if (!StudyClock.on) this else composed {
    val app = LocalApp.current
    val window = LocalWindowInfo.current
    val currentRoute = rememberUpdatedState(route)
    val lastUse = remember { longArrayOf(System.currentTimeMillis()) }
    LaunchedEffect(Unit) {
        var notes = 0
        var mcqs = 0
        fun flush() {
            app.store.addStudyTime(notes = true, seconds = notes)
            app.store.addStudyTime(notes = false, seconds = mcqs)
            notes = 0
            mcqs = 0
        }
        try {
            while (true) {
                delay(1000)
                val kind = studyKind(currentRoute.value())
                val listening = app.platform.speech?.playback?.value?.playing == true
                val inUse = window.isWindowFocused && System.currentTimeMillis() - lastUse[0] < IDLE_MS
                when {
                    kind == false && inUse -> mcqs++
                    kind == true && inUse || listening && kind != false -> notes++
                }
                if (notes + mcqs >= 30) flush()
            }
        } finally {
            flush()
        }
    }
    onPreviewKeyEvent {
        lastUse[0] = System.currentTimeMillis()
        false
    }.pointerInput(Unit) {
        awaitPointerEventScope {
            while (true) {
                awaitPointerEvent(PointerEventPass.Initial)
                lastUse[0] = System.currentTimeMillis()
            }
        }
    }
}

/** "2h 05m", "40m", "0m". */
fun studyTime(seconds: Int): String {
    val m = seconds / 60
    return if (m < 60) "${m}m" else "${m / 60}h ${(m % 60).toString().padStart(2, '0')}m"
}
