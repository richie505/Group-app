package com.appsc.prep.lectures

import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.ActivityInfo
import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.NavigateBefore
import androidx.compose.material.icons.automirrored.filled.NavigateNext
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Fullscreen
import androidx.compose.material.icons.filled.FullscreenExit
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.int
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

/** One lecture: a topic's slides (assets lec/<app>/<book>/<row>.html, made by tools/lecture_app.py). */
data class Topic(val n: Int, val title: String, val unit: String, val slides: Int, val mcqs: Int, val file: String)
data class Subject(val id: Int, val title: String, val short: String, val topics: List<Topic>)
data class LectureApp(val key: String, val name: String, val subjects: List<Subject>)

private val Navy = Color(0xFF1E2A5A)
private val Indigo = Color(0xFF2F3F8F)
private val Amber = Color(0xFFF6A623)
private val Page = Color(0xFFF3F5FA)
private val Ink = Color(0xFF1F2430)
private val Muted = Color(0xFF6B7185)

fun loadIndex(ctx: Context): List<LectureApp> {
    val root = Json.parseToJsonElement(ctx.assets.open("lec/index.json").bufferedReader().readText()).jsonObject
    return root["apps"]!!.jsonArray.map { a ->
        val o = a.jsonObject
        LectureApp(o.s("key"), o.s("name"), o["subjects"]!!.jsonArray.map { s ->
            val so = s.jsonObject
            Subject(so["id"]!!.jsonPrimitive.int, so.s("title"), so.s("short"), so["topics"]!!.jsonArray.map { t ->
                val to = t.jsonObject
                Topic(to["n"]!!.jsonPrimitive.int, to.s("title"), to.s("unit"), to["slides"]!!.jsonPrimitive.int, to["q"]!!.jsonPrimitive.int, to.s("file"))
            })
        })
    }
}

private fun JsonObject.s(k: String) = this[k]?.jsonPrimitive?.content ?: ""

/** Where the viewer is: home, an app's subjects, a subject's topics, or a topic's slides. */
private sealed class Screen {
    data object Home : Screen()
    data class Subjects(val app: Int) : Screen()
    data class Topics(val app: Int, val subject: Int) : Screen()
    data class Slides(val app: Int, val subject: Int, val topic: Int) : Screen()
}

class LecturesActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val apps = loadIndex(this)
        val prefs = getSharedPreferences("lectures", MODE_PRIVATE)
        setContent {
            MaterialTheme(colorScheme = lightColorScheme(primary = Indigo, background = Page, surface = Color.White)) {
                var stack by remember { mutableStateOf(listOf<Screen>(Screen.Home)) }
                var seen by remember { mutableStateOf(prefs.getStringSet("seen", emptySet())!!.toSet()) }
                var last by remember { mutableStateOf(prefs.getString("last", "") ?: "") }
                val go: (Screen) -> Unit = { stack = stack + it }
                val back: () -> Unit = { if (stack.size > 1) stack = stack.dropLast(1) else finish() }
                BackHandler { back() }
                fun open(a: Int, s: Int, t: Int) {
                    val f = apps[a].subjects[s].topics[t].file
                    seen = seen + f
                    last = "$a/$s/$t"
                    prefs.edit().putStringSet("seen", seen).putString("last", last).apply()
                }
                Surface(Modifier.fillMaxSize(), color = Page) {
                    when (val sc = stack.last()) {
                        Screen.Home -> HomeScreen(apps, seen, last) { a, s, t ->
                            if (s < 0) go(Screen.Subjects(a)) else { open(a, s, t); go(Screen.Slides(a, s, t)) }
                        }
                        is Screen.Subjects -> SubjectsScreen(apps[sc.app], seen, back) { go(Screen.Topics(sc.app, it)) }
                        is Screen.Topics -> TopicsScreen(apps[sc.app], apps[sc.app].subjects[sc.subject], seen, back) {
                            open(sc.app, sc.subject, it); go(Screen.Slides(sc.app, sc.subject, it))
                        }
                        is Screen.Slides -> SlidesScreen(
                            apps[sc.app], apps[sc.app].subjects[sc.subject], sc.topic, back,
                        ) { t -> open(sc.app, sc.subject, t); stack = stack.dropLast(1) + Screen.Slides(sc.app, sc.subject, t) }
                    }
                }
            }
        }
    }
}

@Composable
private fun Bar(title: String, sub: String = "", onBack: (() -> Unit)?, actions: @Composable () -> Unit = {}) {
    Row(
        Modifier.fillMaxWidth().background(Navy).safeDrawingPadding().padding(horizontal = 4.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (onBack != null) IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back", tint = Color.White) }
        else Spacer(Modifier.width(14.dp))
        Column(Modifier.weight(1f).padding(end = 4.dp)) {
            Text(title, color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold, maxLines = 1, overflow = TextOverflow.Ellipsis)
            if (sub.isNotEmpty()) Text(sub, color = Color.White.copy(alpha = .7f), fontSize = 12.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
        actions()
    }
}

@Composable
private fun HomeScreen(apps: List<LectureApp>, seen: Set<String>, last: String, onOpen: (Int, Int, Int) -> Unit) {
    Column(Modifier.fillMaxSize()) {
        Box(
            Modifier.fillMaxWidth().background(Brush.linearGradient(listOf(Navy, Indigo, Color(0xFF4458C4)))).safeDrawingPadding()
                .padding(horizontal = 22.dp, vertical = 26.dp),
        ) {
            Column {
                Text("APPSC LECTURES", color = Amber, fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.5.sp)
                Text("Teach every topic, slide by slide", color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.ExtraBold, modifier = Modifier.padding(top = 4.dp))
                Text("From the notes of APPSC Group 1 Prelims and APPSC Group 2", color = Color.White.copy(alpha = .75f), fontSize = 14.sp, modifier = Modifier.padding(top = 4.dp))
            }
        }
        LazyColumn(Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
            val p = last.split("/").mapNotNull { it.toIntOrNull() }
            if (p.size == 3 && p[0] < apps.size) {
                val t = apps[p[0]].subjects.getOrNull(p[1])?.topics?.getOrNull(p[2])
                if (t != null) item {
                    Card(Modifier.padding(top = 16.dp), onClick = { onOpen(p[0], p[1], p[2]) }) {
                        Text("CONTINUE", color = Amber, fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                        Text(t.title, color = Ink, fontSize = 16.sp, fontWeight = FontWeight.SemiBold, maxLines = 2, overflow = TextOverflow.Ellipsis)
                        Text("${apps[p[0]].name} · ${apps[p[0]].subjects[p[1]].short}", color = Muted, fontSize = 12.sp)
                    }
                }
            }
            items(apps.size) { a ->
                val app = apps[a]
                val all = app.subjects.flatMap { it.topics }
                Card(Modifier.padding(top = 16.dp), onClick = { onOpen(a, -1, -1) }) {
                    Text(app.name, color = Navy, fontSize = 20.sp, fontWeight = FontWeight.ExtraBold)
                    Text("${app.subjects.size} subjects · ${all.size} lectures · ${all.sumOf { it.slides }} slides", color = Muted, fontSize = 13.sp)
                    Progress(all.count { it.file in seen }, all.size)
                }
            }
            item { Spacer(Modifier.height(24.dp)) }
        }
    }
}

@Composable
private fun SubjectsScreen(app: LectureApp, seen: Set<String>, onBack: () -> Unit, onOpen: (Int) -> Unit) {
    Column(Modifier.fillMaxSize()) {
        Bar(app.name, "Subjects", onBack)
        LazyColumn(Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
            items(app.subjects.size) { i ->
                val s = app.subjects[i]
                Card(Modifier.padding(top = 12.dp), onClick = { onOpen(i) }) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(Modifier.size(36.dp).clip(CircleShape).background(Navy), contentAlignment = Alignment.Center) {
                            Text("${i + 1}", color = Color.White, fontWeight = FontWeight.Bold)
                        }
                        Column(Modifier.padding(start = 12.dp)) {
                            Text(s.title, color = Ink, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                            Text("${s.topics.size} lectures · ${s.topics.sumOf { it.slides }} slides", color = Muted, fontSize = 12.sp)
                        }
                    }
                    Progress(s.topics.count { it.file in seen }, s.topics.size)
                }
            }
            item { Spacer(Modifier.height(24.dp)) }
        }
    }
}

@Composable
private fun TopicsScreen(app: LectureApp, s: Subject, seen: Set<String>, onBack: () -> Unit, onOpen: (Int) -> Unit) {
    var q by remember { mutableStateOf("") }
    Column(Modifier.fillMaxSize()) {
        Bar(s.short, "${app.name} · ${s.topics.size} lectures", onBack)
        OutlinedTextField(
            q, { q = it }, Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
            placeholder = { Text("Search topics") }, singleLine = true,
            leadingIcon = { Icon(Icons.Filled.Search, null) },
        )
        val shown = s.topics.withIndex().filter { q.isBlank() || it.value.title.contains(q, ignoreCase = true) }
        LazyColumn(Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
            var unit = ""
            shown.forEach { (i, t) ->
                if (q.isBlank() && t.unit != unit) {
                    unit = t.unit
                    val u = t.unit
                    item(key = "u$i") {
                        Text(u.uppercase(), color = Indigo, fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp,
                            maxLines = 2, overflow = TextOverflow.Ellipsis, modifier = Modifier.padding(top = 16.dp, bottom = 2.dp))
                    }
                }
                item(key = "t$i") {
                    Row(
                        Modifier.fillMaxWidth().padding(top = 6.dp).clip(RoundedCornerShape(12.dp)).background(Color.White)
                            .clickable { onOpen(i) }.padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text("%03d".format(t.n), color = Muted, fontSize = 12.sp, fontWeight = FontWeight.Bold, modifier = Modifier.width(38.dp))
                        Column(Modifier.weight(1f)) {
                            Text(t.title, color = Ink, fontSize = 15.sp, fontWeight = FontWeight.Medium, maxLines = 3, overflow = TextOverflow.Ellipsis)
                            Text("${t.slides} slides · ${t.mcqs} MCQs in the app", color = Muted, fontSize = 12.sp)
                        }
                        if (t.file in seen) Icon(Icons.Filled.CheckCircle, "Opened", tint = Color(0xFF2E9E5B), modifier = Modifier.padding(start = 8.dp))
                    }
                }
            }
            item { Spacer(Modifier.height(24.dp)) }
        }
    }
}

@SuppressLint("SetJavaScriptEnabled")
@Composable
private fun SlidesScreen(app: LectureApp, s: Subject, i: Int, onBack: () -> Unit, onTopic: (Int) -> Unit) {
    val t = s.topics[i]
    val activity = LocalContext.current as ComponentActivity
    var present by remember { mutableStateOf(false) }
    fun setPresent(on: Boolean) {
        present = on
        activity.requestedOrientation = if (on) ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE else ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED
        val c = WindowCompat.getInsetsController(activity.window, activity.window.decorView)
        if (on) { c.hide(WindowInsetsCompat.Type.systemBars()); c.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE }
        else c.show(WindowInsetsCompat.Type.systemBars())
    }
    BackHandler { if (present) setPresent(false) else onBack() }
    Column(Modifier.fillMaxSize().background(Color(0xFFDFE3EC))) {
        if (!present) Bar(t.title, "${s.short} · lecture ${t.n} of ${s.topics.size} · ${t.slides} slides", onBack) {
            IconButton(onClick = { if (i > 0) onTopic(i - 1) }, enabled = i > 0) {
                Icon(Icons.AutoMirrored.Filled.NavigateBefore, "Previous lecture", tint = if (i > 0) Color.White else Color.White.copy(alpha = .3f))
            }
            IconButton(onClick = { if (i < s.topics.size - 1) onTopic(i + 1) }, enabled = i < s.topics.size - 1) {
                Icon(Icons.AutoMirrored.Filled.NavigateNext, "Next lecture", tint = if (i < s.topics.size - 1) Color.White else Color.White.copy(alpha = .3f))
            }
            IconButton(onClick = { setPresent(true) }) { Icon(Icons.Filled.Fullscreen, "Present", tint = Color.White) }
        }
        Box(Modifier.weight(1f)) {
            AndroidView(
                factory = { ctx ->
                    WebView(ctx).apply {
                        webViewClient = WebViewClient()
                        settings.javaScriptEnabled = true // the slides lay themselves out, measuring what fits
                        settings.useWideViewPort = true
                        settings.loadWithOverviewMode = true
                        settings.builtInZoomControls = true
                        settings.displayZoomControls = false
                        setBackgroundColor(android.graphics.Color.rgb(223, 227, 236))
                    }
                },
                update = { w -> val u = "file:///android_asset/${t.file}"; if (w.url != u) w.loadUrl(u) },
                modifier = Modifier.fillMaxSize(),
            )
            if (present) IconButton(
                onClick = { setPresent(false) },
                modifier = Modifier.align(Alignment.TopEnd).padding(8.dp).clip(CircleShape).background(Navy.copy(alpha = .55f)),
            ) { Icon(Icons.Filled.FullscreenExit, "Exit presenting", tint = Color.White) }
        }
    }
}

@Composable
private fun Card(modifier: Modifier = Modifier, onClick: () -> Unit, body: @Composable () -> Unit) {
    Column(
        modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(Color.White).clickable(onClick = onClick).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) { body() }
}

@Composable
private fun Progress(done: Int, total: Int) {
    Column(Modifier.padding(top = 8.dp)) {
        Box(Modifier.fillMaxWidth().height(6.dp).clip(RoundedCornerShape(3.dp)).background(Color(0xFFE3E6F0))) {
            Box(Modifier.fillMaxWidth(if (total == 0) 0f else done.toFloat() / total).height(6.dp).clip(RoundedCornerShape(3.dp)).background(Amber))
        }
        Text("$done of $total opened", color = Muted, fontSize = 11.sp, modifier = Modifier.padding(top = 4.dp))
    }
}
