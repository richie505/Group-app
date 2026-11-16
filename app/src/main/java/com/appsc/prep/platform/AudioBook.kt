package com.appsc.prep.platform

import android.content.ContentValues
import android.content.Context
import android.media.MediaCodec
import android.media.MediaCodecInfo
import android.media.MediaFormat
import android.media.MediaMuxer
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.os.PowerManager
import android.provider.MediaStore
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import com.appsc.prep.ui.components.DownloadState
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.Locale
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/**
 * "Download today's audiobook": the day's topics spoken by the phone's text-to-speech (the reader's chosen voice
 * and speed) into one compressed audio file per topic (.m4a, AAC mono 48 kbps), saved to
 * Music/APPSC Audiobooks/<app>/<day>/ so any music player can play them. Runs on its own thread with a
 * foreground notification ([AudioBookService]); its own speech engine, so read-aloud is not disturbed.
 */
object AudioBook {
    private val main = Handler(Looper.getMainLooper())
    val state = mutableStateOf(DownloadState())
    val stateRead: State<DownloadState> get() = state
    @Volatile private var cancelled = false
    @Volatile private var worker: Thread? = null

    fun start(context: Context, appName: String, folder: String, chapters: List<Pair<String, List<String>>>, voice: String, rate: Float) {
        if (worker?.isAlive == true || chapters.isEmpty()) return
        val app = context.applicationContext
        cancelled = false
        state.value = DownloadState(active = true, total = chapters.size, current = chapters[0].first, folder = folder)
        AudioBookService.start(app)
        worker = Thread {
            val pm = app.getSystemService(Context.POWER_SERVICE) as PowerManager
            val wake = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "appscprep:audiobook").apply { acquire(6 * 60 * 60 * 1000L) }
            var tts: TextToSpeech? = null
            try {
                tts = engine(app, voice, rate) ?: throw IllegalStateException("No text-to-speech engine on this phone")
                val dir = "${Environment.DIRECTORY_MUSIC}/APPSC Audiobooks/$appName/$folder"
                chapters.forEachIndexed { i, (name, parts) ->
                    if (cancelled) return@Thread
                    post { state.value = state.value.copy(done = i, current = name) }
                    val m4a = File(app.cacheDir, "chapter.m4a")
                    record(app, tts!!, parts, m4a)
                    if (cancelled) return@Thread
                    save(app, m4a, dir, "%02d - %s.m4a".format(i + 1, clean(name)))
                    m4a.delete()
                }
                post { state.value = state.value.copy(active = false, done = chapters.size, savedTo = "Music/APPSC Audiobooks/$appName/$folder") }
            } catch (e: Throwable) {
                post { state.value = state.value.copy(active = false, error = e.message ?: e.toString()) }
            } finally {
                runCatching { tts?.shutdown() }
                runCatching { wake.release() }
                if (cancelled) post { state.value = DownloadState() }
                post { AudioBookService.stop(app) }
            }
        }.apply { name = "audiobook"; start() }
    }

    fun cancel() {
        cancelled = true
    }

    private fun post(block: () -> Unit) = main.post(block)

    private fun clean(s: String) = s.replace(Regex("[\\\\/:*?\"<>|]"), " ").replace(Regex("\\s+"), " ").trim().take(80)

    /** A speech engine of its own, set like read-aloud: Indian English, the chosen voice and speed. */
    private fun engine(app: Context, voice: String, rate: Float): TextToSpeech? {
        val ready = CountDownLatch(1)
        var ok = false
        var t: TextToSpeech? = null
        main.post { t = TextToSpeech(app) { ok = it == TextToSpeech.SUCCESS; ready.countDown() } }
        if (!ready.await(30, TimeUnit.SECONDS) || !ok) return null
        val e = t ?: return null
        listOf(Locale("en", "IN"), Locale.UK, Locale.US).firstOrNull { e.isLanguageAvailable(it) >= TextToSpeech.LANG_AVAILABLE }?.let { e.language = it }
        if (voice.isNotEmpty()) runCatching { e.voices?.firstOrNull { it.name == voice }?.let { e.voice = it } }
        e.setSpeechRate(rate)
        return e
    }

    /** Speaks [parts] one by one into WAV files and encodes them, with a short pause between, into [out]. */
    private fun record(app: Context, tts: TextToSpeech, parts: List<String>, out: File) {
        var enc: Encoder? = null
        val wav = File(app.cacheDir, "part.wav")
        val max = TextToSpeech.getMaxSpeechInputLength() - 1
        try {
            for ((i, text) in parts.withIndex()) {
                if (cancelled) return
                if (text.isBlank()) continue
                val done = CountDownLatch(1)
                var failed = false
                tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                    override fun onStart(id: String?) {}
                    override fun onDone(id: String?) = done.countDown()
                    @Deprecated("Deprecated in Java")
                    override fun onError(id: String?) { failed = true; done.countDown() }
                    override fun onError(id: String?, code: Int) { failed = true; done.countDown() }
                })
                wav.delete()
                if (tts.synthesizeToFile(text.take(max), Bundle(), wav, "p$i") != TextToSpeech.SUCCESS) continue
                if (!done.await(5, TimeUnit.MINUTES) || failed || !wav.exists()) continue
                val (rateHz, channels, pcm) = readWav(wav) ?: continue
                val e = enc ?: Encoder(out, rateHz, channels).also { enc = it }
                e.feed(pcm)
                e.feed(ByteArray(rateHz * channels * 2 * 4 / 10)) // 0.4 s pause
            }
        } finally {
            wav.delete()
            enc?.finish()
        }
        if (enc == null) throw IllegalStateException("The voice did not produce any audio")
    }

    /** (sample rate, channels, 16-bit PCM) of a WAV file. */
    private fun readWav(f: File): Triple<Int, Int, ByteArray>? {
        val b = f.readBytes()
        if (b.size < 44 || String(b, 0, 4) != "RIFF") return null
        val bb = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN)
        var p = 12
        var rate = 0; var ch = 1
        while (p + 8 <= b.size) {
            val id = String(b, p, 4)
            val len = bb.getInt(p + 4)
            if (id == "fmt ") { ch = bb.getShort(p + 10).toInt(); rate = bb.getInt(p + 12) }
            if (id == "data") {
                val end = if (len <= 0 || p + 8 + len > b.size) b.size else p + 8 + len
                return if (rate > 0) Triple(rate, ch, b.copyOfRange(p + 8, end)) else null
            }
            p += 8 + len + (len and 1)
        }
        return null
    }

    /** PCM -> AAC in an .m4a file. */
    private class Encoder(out: File, private val rate: Int, private val channels: Int) {
        private val codec = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_AUDIO_AAC)
        private val muxer = MediaMuxer(out.path, MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4)
        private var track = -1
        private var muxing = false
        private var samples = 0L
        private val info = MediaCodec.BufferInfo()

        init {
            val fmt = MediaFormat.createAudioFormat(MediaFormat.MIMETYPE_AUDIO_AAC, rate, channels).apply {
                setInteger(MediaFormat.KEY_AAC_PROFILE, MediaCodecInfo.CodecProfileLevel.AACObjectLC)
                setInteger(MediaFormat.KEY_BIT_RATE, 48_000)
                setInteger(MediaFormat.KEY_MAX_INPUT_SIZE, 16_384)
            }
            codec.configure(fmt, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE)
            codec.start()
        }

        fun feed(pcm: ByteArray, end: Boolean = false) {
            var off = 0
            while (off < pcm.size || end) {
                val i = codec.dequeueInputBuffer(10_000)
                if (i >= 0) {
                    val buf = codec.getInputBuffer(i)!!
                    buf.clear()
                    val n = minOf(buf.remaining(), pcm.size - off)
                    buf.put(pcm, off, n)
                    val pts = samples * 1_000_000L / rate
                    samples += n / (2 * channels)
                    off += n
                    val last = end && off >= pcm.size
                    codec.queueInputBuffer(i, 0, n, pts, if (last) MediaCodec.BUFFER_FLAG_END_OF_STREAM else 0)
                    if (last) { drain(true); return }
                }
                drain(false)
            }
        }

        private fun drain(toEnd: Boolean) {
            while (true) {
                val o = codec.dequeueOutputBuffer(info, if (toEnd) 10_000 else 0)
                when {
                    o == MediaCodec.INFO_OUTPUT_FORMAT_CHANGED -> { track = muxer.addTrack(codec.outputFormat); muxer.start(); muxing = true }
                    o >= 0 -> {
                        val buf = codec.getOutputBuffer(o)!!
                        if (info.flags and MediaCodec.BUFFER_FLAG_CODEC_CONFIG != 0) info.size = 0
                        if (info.size > 0 && muxing) { buf.position(info.offset); buf.limit(info.offset + info.size); muxer.writeSampleData(track, buf, info) }
                        codec.releaseOutputBuffer(o, false)
                        if (info.flags and MediaCodec.BUFFER_FLAG_END_OF_STREAM != 0) return
                    }
                    o == MediaCodec.INFO_TRY_AGAIN_LATER -> if (!toEnd) return
                }
            }
        }

        fun finish() {
            runCatching { feed(ByteArray(0), end = true) }
            runCatching { codec.stop(); codec.release() }
            runCatching { if (muxing) muxer.stop(); muxer.release() }
        }
    }

    /** Copies [file] into the phone's Music folder (MediaStore on Android 10+, the app's music folder before). */
    private fun save(app: Context, file: File, dir: String, name: String) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val values = ContentValues().apply {
                put(MediaStore.Audio.Media.DISPLAY_NAME, name)
                put(MediaStore.Audio.Media.MIME_TYPE, "audio/mp4")
                put(MediaStore.Audio.Media.RELATIVE_PATH, dir)
                put(MediaStore.Audio.Media.IS_PENDING, 1)
            }
            val r = app.contentResolver
            val uri = r.insert(MediaStore.Audio.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY), values)
                ?: throw IllegalStateException("Could not save to Music")
            r.openOutputStream(uri)!!.use { out -> file.inputStream().use { it.copyTo(out) } }
            values.clear(); values.put(MediaStore.Audio.Media.IS_PENDING, 0)
            r.update(uri, values, null, null)
        } else {
            val d = File(app.getExternalFilesDir(Environment.DIRECTORY_MUSIC), dir.substringAfter("/"))
            d.mkdirs()
            file.copyTo(File(d, name), overwrite = true)
        }
    }
}
