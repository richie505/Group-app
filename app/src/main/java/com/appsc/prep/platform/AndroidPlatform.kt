package com.appsc.prep.platform

import android.content.Context
import android.content.Intent
import androidx.compose.runtime.Composable
import androidx.compose.runtime.MutableState
import androidx.compose.ui.Modifier
import com.appsc.prep.data.Storage
import com.appsc.prep.ui.components.Platform

class PrefsStorage(context: Context) : Storage {
    private val prefs = context.getSharedPreferences("progress", Context.MODE_PRIVATE)

    override fun getStringSet(key: String): Set<String> = prefs.getStringSet(key, emptySet())!!.toSet()
    override fun getString(key: String): String? = prefs.getString(key, null)
    override fun getFloat(key: String, default: Float) = prefs.getFloat(key, default)
    override fun putStringSet(key: String, value: Set<String>) = prefs.edit().putStringSet(key, value).apply()
    override fun putString(key: String, value: String) = prefs.edit().putString(key, value).apply()
    override fun putFloat(key: String, value: Float) = prefs.edit().putFloat(key, value).apply()
}

class AndroidPlatform(private val context: Context) : Platform {
    override val desktop = false

    override val speech: ReadAloud get() = ReadAloud.init(context)

    override fun share(title: String, text: String) {
        val send = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_SUBJECT, title)
            putExtra(Intent.EXTRA_TEXT, text)
        }
        context.startActivity(Intent.createChooser(send, "Share").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    }

    @Composable
    override fun BackHandler(enabled: Boolean, onBack: () -> Unit) =
        androidx.activity.compose.BackHandler(enabled, onBack)

    @Composable
    override fun Shortcuts(onKey: (String) -> Boolean) = Unit

    /** Google inside the app: an Android WebView that keeps every link in the app. */
    @android.annotation.SuppressLint("SetJavaScriptEnabled")
    @Composable
    override fun WebPage(url: String, modifier: Modifier, back: MutableState<(() -> Boolean)?>) {
        androidx.compose.ui.viewinterop.AndroidView(
            factory = { ctx ->
                android.webkit.WebView(ctx).apply {
                    settings.javaScriptEnabled = true // Google's pages need it
                    settings.domStorageEnabled = true
                    webViewClient = android.webkit.WebViewClient() // links open here, not in Chrome
                    loadUrl(url)
                    back.value = { if (canGoBack()) { goBack(); true } else false }
                }
            },
            modifier = modifier,
            onRelease = { it.destroy() },
        )
    }
}
