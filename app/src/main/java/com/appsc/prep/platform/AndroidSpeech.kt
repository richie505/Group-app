package com.appsc.prep.platform

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import com.appsc.prep.ui.components.Speech
import java.util.Locale

/** Android's built-in text-to-speech (works offline with the phone's installed voices). */
class AndroidSpeech(private val context: Context) : Speech {
    private val main = Handler(Looper.getMainLooper())
    private var tts: TextToSpeech? = null
    private var ready = false
    private var pending: (() -> Unit)? = null
    // each speak() call gets a new session, so callbacks from cut-off speech are ignored
    private var session = 0

    private fun withEngine(block: () -> Unit) {
        if (ready) return block()
        pending = block
        if (tts != null) return
        tts = TextToSpeech(context.applicationContext) { status ->
            main.post {
                if (status != TextToSpeech.SUCCESS) return@post
                val engine = tts ?: return@post
                // Indian English first, then English, then the phone's default voice
                val lang = listOf(Locale("en", "IN"), Locale.UK, Locale.US)
                    .firstOrNull { engine.isLanguageAvailable(it) >= TextToSpeech.LANG_AVAILABLE }
                if (lang != null) engine.language = lang
                ready = true
                pending?.invoke()
                pending = null
            }
        }
    }

    override fun speak(parts: List<String>, from: Int, rate: Float, onPart: (Int) -> Unit, onDone: () -> Unit) {
        val id = ++session
        withEngine {
            val engine = tts ?: return@withEngine
            if (id != session) return@withEngine
            val last = parts.lastIndex
            engine.setSpeechRate(rate)
            engine.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                private fun index(u: String?): Int? =
                    u?.split(':')?.takeIf { it.size == 2 && it[0].toInt() == session }?.get(1)?.toInt()

                override fun onStart(u: String?) {
                    index(u)?.let { i -> main.post { if (id == session) onPart(i) } }
                }

                override fun onDone(u: String?) {
                    if (index(u) == last) main.post { if (id == session) onDone() }
                }

                @Deprecated("Deprecated in Java")
                override fun onError(u: String?) = Unit
            })
            val max = TextToSpeech.getMaxSpeechInputLength() - 1
            for (i in from.coerceIn(0, last.coerceAtLeast(0))..last) {
                val text = parts[i].take(max)
                engine.speak(text, if (i == from) TextToSpeech.QUEUE_FLUSH else TextToSpeech.QUEUE_ADD, null, "$id:$i")
            }
        }
    }

    override fun stop() {
        session++
        pending = null
        tts?.stop()
    }

    fun shutdown() {
        stop()
        tts?.shutdown()
        tts = null
        ready = false
    }
}
