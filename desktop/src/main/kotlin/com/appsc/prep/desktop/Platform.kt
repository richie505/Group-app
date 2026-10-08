package com.appsc.prep.desktop

import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.KeyEvent
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.isAltPressed
import androidx.compose.ui.input.key.isCtrlPressed
import androidx.compose.ui.input.key.isMetaPressed
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.type
import com.appsc.prep.ui.components.Platform
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import java.nio.file.Path
import java.nio.file.Paths

/** Folder for progress and logs: %APPDATA%\APPSC Prep on Windows, ~/.appsc-prep elsewhere. */
fun appDataDir(): Path {
    val base = System.getenv("APPDATA")?.let { Paths.get(it, APP_NAME) }
        ?: Paths.get(System.getProperty("user.home"), ".appsc-prep")
    return base.also { it.toFile().mkdirs() }
}

object DesktopPlatform : Platform {
    override val desktop = true

    override fun openInBrowser(url: String) {
        runCatching { java.awt.Desktop.getDesktop().browse(java.net.URI(url)) }
    }

    override fun askGemini(prompt: String): String {
        Toolkit.getDefaultToolkit().systemClipboard.setContents(StringSelection(prompt), null)
        openInBrowser("https://gemini.google.com/app")
        return "Question copied - paste it into Gemini with Ctrl + V."
    }

    /** A short message shown at the bottom of the window. */
    var toast by mutableStateOf<String?>(null)

    /** Set by the window: pop one screen. */
    var navBack: () -> Unit = {}

    // Innermost screen last; only the last one gets the key.
    private class Handler<T>(var fn: T)
    private val backs = mutableListOf<Handler<() -> Unit>>()
    private val keys = mutableListOf<Handler<(String) -> Boolean>>()

    override fun share(title: String, text: String) {
        Toolkit.getDefaultToolkit().systemClipboard.setContents(StringSelection(text), null)
        toast = "Copied to the clipboard – paste it anywhere with Ctrl + V"
    }

    // backups: a plain Windows save/open box
    @Composable
    override fun rememberSaveFile(done: (Boolean) -> Unit): ((String, String) -> Unit)? = { name, text ->
        val box = java.awt.FileDialog(null as java.awt.Frame?, "Save backup", java.awt.FileDialog.SAVE).apply { file = name; isVisible = true }
        val file = box.file?.let { java.io.File(box.directory, it) }
        done(file != null && runCatching { file.writeText(text) }.isSuccess)
    }

    @Composable
    override fun rememberOpenFile(got: (String?) -> Unit): (() -> Unit)? = {
        val box = java.awt.FileDialog(null as java.awt.Frame?, "Open backup", java.awt.FileDialog.LOAD).apply { isVisible = true }
        got(box.file?.let { f -> runCatching { java.io.File(box.directory, f).readText() }.getOrNull() })
    }

    @Composable
    override fun BackHandler(enabled: Boolean, onBack: () -> Unit) {
        val current by rememberUpdatedState(onBack)
        if (enabled) {
            DisposableEffect(Unit) {
                val h = Handler { current() }
                backs += h
                onDispose { backs -= h }
            }
        }
    }

    @Composable
    override fun Shortcuts(onKey: (String) -> Boolean) {
        val current by rememberUpdatedState(onKey)
        DisposableEffect(Unit) {
            val h = Handler<(String) -> Boolean> { current(it) }
            keys += h
            onDispose { keys -= h }
        }
    }

    fun back() {
        backs.lastOrNull()?.fn?.invoke() ?: navBack()
    }

    fun onKey(e: KeyEvent): Boolean {
        if (e.type != KeyEventType.KeyDown) return false
        if (e.key == Key.Escape || (e.isAltPressed && e.key == Key.DirectionLeft)) {
            back()
            return true
        }
        if (e.isCtrlPressed || e.isAltPressed || e.isMetaPressed) return false
        val name = when (e.key) {
            Key.DirectionLeft -> "Left"
            Key.DirectionRight -> "Right"
            Key.One, Key.NumPad1, Key.A -> "1"
            Key.Two, Key.NumPad2, Key.B -> "2"
            Key.Three, Key.NumPad3, Key.C -> "3"
            Key.Four, Key.NumPad4, Key.D -> "4"
            Key.Five, Key.NumPad5, Key.E -> "5"
            else -> return false
        }
        return keys.lastOrNull()?.fn?.invoke(name) ?: false
    }
}
