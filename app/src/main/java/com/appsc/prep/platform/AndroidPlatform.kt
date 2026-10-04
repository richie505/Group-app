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

    /**
     * Google inside the app: an Android WebView that keeps every link in the app. The page's copy menu does not
     * show inside the app's pop-up, so the last text selected is kept here and handed to [selected].
     */
    @android.annotation.SuppressLint("SetJavaScriptEnabled", "JavascriptInterface")
    @Composable
    override fun WebPage(
        url: String,
        modifier: Modifier,
        back: MutableState<(() -> Boolean)?>,
        selected: MutableState<(((String) -> Unit) -> Unit)?>?,
    ) {
        androidx.compose.ui.viewinterop.AndroidView(
            factory = { ctx ->
                android.webkit.WebView(ctx).apply {
                    settings.javaScriptEnabled = true // Google's pages need it
                    settings.domStorageEnabled = true
                    var last = ""
                    if (selected != null) {
                        addJavascriptInterface(object {
                            @android.webkit.JavascriptInterface
                            fun selected(text: String) { if (text.isNotBlank()) last = text }
                        }, "PrepApp")
                    }
                    webViewClient = object : android.webkit.WebViewClient() { // links open here, not in Chrome
                        override fun onPageFinished(view: android.webkit.WebView, url: String?) {
                            if (selected != null) view.evaluateJavascript(WATCH_SELECTION, null)
                        }
                    }
                    loadUrl(url)
                    back.value = { if (canGoBack()) { goBack(); true } else false }
                    selected?.value = { done ->
                        evaluateJavascript("String(window.getSelection())") { r ->
                            val now = if (r == null || r == "null") "" else runCatching { org.json.JSONArray("[$r]").getString(0) }.getOrDefault("")
                            done(now.ifBlank { last }.trim())
                        }
                    }
                }
            },
            modifier = modifier,
            onRelease = { it.destroy() },
        )
    }

    private companion object {
        const val WATCH_SELECTION = "if(!window.__prepSel){window.__prepSel=1;document.addEventListener('selectionchange'," +
            "function(){var s=String(window.getSelection());if(s.trim())PrepApp.selected(s);});}"
    }
}
