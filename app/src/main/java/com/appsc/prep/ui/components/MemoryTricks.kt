package com.appsc.prep.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.outlined.Image
import androidx.compose.material.icons.outlined.Link
import androidx.compose.material.icons.outlined.Pin
import androidx.compose.material.icons.outlined.Place
import androidx.compose.material.icons.outlined.Psychology
import androidx.compose.material.icons.outlined.QuestionAnswer
import androidx.compose.material.icons.outlined.ReportProblem
import androidx.compose.material.icons.outlined.SwapHoriz
import androidx.compose.material.icons.outlined.TextFields
import androidx.compose.material.icons.outlined.Timeline
import androidx.compose.material.icons.outlined.ViewModule
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Popup
import androidx.compose.ui.window.PopupProperties
import com.appsc.prep.data.PageTricks
import com.appsc.prep.data.Trick
import com.appsc.prep.ui.theme.C

/** What each kind of trick is called on screen, and its icon. */
private fun kind(type: String): Pair<String, ImageVector> = when (type) {
    "mnemonic" -> "Mnemonic" to Icons.Outlined.TextFields
    "chunk" -> "Group it" to Icons.Outlined.ViewModule
    "number" -> "Number hook" to Icons.Outlined.Pin
    "story" -> "Picture it" to Icons.Outlined.Image
    "contrast" -> "Don't confuse" to Icons.Outlined.SwapHoriz
    "chain" -> "Cause → effect" to Icons.Outlined.Link
    "timeline" -> "Timeline" to Icons.Outlined.Timeline
    "place" -> "Map it" to Icons.Outlined.Place
    "trap" -> "Exam trap" to Icons.Outlined.ReportProblem
    else -> "Trick" to Icons.Outlined.Psychology
}

/**
 * "Remember it": the memory tricks of one notes page ([secs] = one index) or of a whole section (all its
 * pages, each under its title), with questions to ask yourself and the strategies behind the tricks.
 * Full screen; back or ✕ closes it.
 */
@Composable
fun MemoryTricks(book: Int, row: Int, secs: List<Pair<Int, String>>, title: String, onClose: () -> Unit) {
    val repo = LocalApp.current.repo
    val all by produceState<Map<String, PageTricks>?>(null, book) { value = repo.tricks(book) }
    var strategies by remember { mutableStateOf(false) }
    Popup(onDismissRequest = { if (strategies) strategies = false else onClose() }, properties = PopupProperties(focusable = true)) {
        Column(Modifier.fillMaxWidth().fillMaxHeight().background(Color.White)) {
            Row(Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 2.dp), verticalAlignment = Alignment.CenterVertically) {
                IconButton(onClick = { if (strategies) strategies = false else onClose() }) { Icon(Icons.Filled.Close, "Close", tint = C.Ink) }
                Text(
                    if (strategies) "How to remember" else "Remember it",
                    style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.SemiBold, color = C.Ink),
                    modifier = Modifier.weight(1f),
                )
            }
            HorizontalDivider(color = C.Line)
            if (strategies) {
                Strategies()
                return@Column
            }
            val pages = all?.let { m -> secs.mapNotNull { (i, t) -> m["$row:$i"]?.let { t to it } } }
            LazyColumn(Modifier.fillMaxWidth().weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                item {
                    Column(Modifier.widthIn(max = 880.dp).fillMaxWidth().padding(start = 20.dp, end = 20.dp, top = 14.dp)) {
                        Text(title, style = TextStyle(fontSize = 13.sp, lineHeight = 18.sp, color = C.Accent, fontWeight = FontWeight.SemiBold))
                        Text(
                            "How to use: read a trick, close your eyes and say the facts it holds, then answer the questions without looking.",
                            style = TextStyle(fontSize = 13.sp, lineHeight = 19.sp, color = C.Muted),
                            modifier = Modifier.padding(top = 4.dp),
                        )
                        Text(
                            "All memory strategies →",
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = C.Accent),
                            modifier = Modifier.padding(vertical = 8.dp).clickable { strategies = true },
                        )
                    }
                }
                when {
                    pages == null -> item { Text("Loading…", style = TextStyle(fontSize = 14.sp, color = C.Muted), modifier = Modifier.padding(20.dp)) }
                    pages.isEmpty() -> item {
                        Text("No memory tricks for this page yet.", style = TextStyle(fontSize = 14.sp, color = C.Muted), modifier = Modifier.padding(20.dp))
                    }
                    else -> pages.forEachIndexed { n, (pageTitle, p) ->
                        item(key = "p$n") {
                            Column(Modifier.widthIn(max = 880.dp).fillMaxWidth().padding(horizontal = 20.dp, vertical = 6.dp)) {
                                if (secs.size > 1) {
                                    Text(
                                        "${n + 1}. $pageTitle",
                                        style = TextStyle(fontSize = 16.sp, lineHeight = 22.sp, fontWeight = FontWeight.SemiBold, color = C.Ink),
                                        modifier = Modifier.padding(top = 10.dp, bottom = 4.dp),
                                    )
                                }
                                p.tricks.forEach { TrickCard(it) }
                                Recall(p.recall)
                            }
                        }
                    }
                }
                item { Spacer(Modifier.height(32.dp)) }
            }
        }
    }
}

@Composable
private fun TrickCard(t: Trick) {
    val (label, icon) = kind(t.type)
    val trap = t.type == "trap" || t.type == "contrast"
    Column(
        Modifier.fillMaxWidth().padding(vertical = 5.dp).clip(RoundedCornerShape(12.dp))
            .background(if (trap) C.ExamBg else C.AccentSoft).padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, null, tint = if (trap) C.ExamInk else C.Accent, modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(6.dp))
            Text(label.uppercase(), style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.8.sp, color = if (trap) C.ExamInk else C.Accent))
        }
        Text(t.title, style = TextStyle(fontSize = 15.sp, lineHeight = 21.sp, fontWeight = FontWeight.SemiBold, color = C.Ink), modifier = Modifier.padding(top = 6.dp))
        if (t.type == "mnemonic" && t.cue.isNotBlank()) {
            Text(t.cue, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold, color = C.Accent, letterSpacing = 1.sp), modifier = Modifier.padding(top = 6.dp))
            // each letter and what it stands for
            Column(Modifier.padding(top = 4.dp)) {
                t.items.forEach { item ->
                    Text(
                        buildAnnotatedString {
                            withStyle(SpanStyle(fontWeight = FontWeight.Bold, color = C.Accent)) { append(item.take(1)) }
                            append(item.drop(1))
                        },
                        style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, color = C.Body),
                    )
                }
            }
        }
        Text(t.text, style = TextStyle(fontSize = 14.sp, lineHeight = 21.sp, color = C.Body), modifier = Modifier.padding(top = 6.dp))
    }
}

/** Questions to answer with the page closed; the answer shows on a tap. */
@Composable
private fun Recall(qs: List<Pair<String, String>>) {
    if (qs.isEmpty()) return
    Column(Modifier.fillMaxWidth().padding(vertical = 5.dp).clip(RoundedCornerShape(12.dp)).background(C.GreenSoft).padding(14.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Outlined.QuestionAnswer, null, tint = C.Green, modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(6.dp))
            Text("TEST YOURSELF", style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.8.sp, color = C.Green))
        }
        qs.forEach { (q, a) ->
            var shown by remember(q) { mutableStateOf(false) }
            Text(q, style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, fontWeight = FontWeight.SemiBold, color = C.Ink), modifier = Modifier.padding(top = 8.dp))
            if (shown) {
                Text(a, style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, color = C.Body), modifier = Modifier.padding(top = 2.dp))
            } else {
                Text(
                    "Show answer",
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = C.Green),
                    modifier = Modifier.padding(top = 2.dp).clickable { shown = true },
                )
            }
        }
    }
}

/** The ways to remember behind the tricks, for UPSC / APPSC prelims. */
private val STRATEGIES = listOf(
    "Active recall" to "Close the page and say or write what you remember, then check. Pulling a fact out of memory fixes it far better than reading it again. Use \"Test yourself\" and the MCQs right after each page.",
    "Spaced revision" to "Revise a page on day 1, day 3, day 7, day 21 and day 45. Each revision just before you would forget makes the memory last longer.",
    "Mnemonics" to "For a list or an order (sources of the Constitution, members of a body, stages of a process): make a word or phrase whose letters start each item. Funny or personal ones stick best.",
    "Chunking" to "Ten loose facts are hard; three groups of three are easy. Group items under a label (\"rights for the citizen / for everyone\", \"Centre / State / joint\").",
    "Number and date hooks" to "Tie a number to something you know (Art. 21 — 21st birthday, freedom of life) or to another number (1969 and 1973 — four years apart). Learn dates in pairs and sequences, not alone.",
    "Picture it (visualisation)" to "Turn facts into a vivid scene and place it somewhere you know (a room in your house: memory palace). The stranger the picture, the longer it stays.",
    "Contrast pairs" to "Most wrong options are a look-alike: two Acts, two committees, two rivers, two years. Make a two-column \"X vs Y\" for every pair you mix up.",
    "Cause → effect chains" to "Learn why things happened and what followed (crisis → reform → result). One link pulls the next out of memory, and statement questions test exactly this.",
    "Timelines" to "Put each period's events on one line and anchor them to a date you already know. Order questions and \"which came first\" are then easy.",
    "Map it" to "For places (parks, dams, ports, sites, events), see them on a map: direction, river, neighbouring state. Draw a rough map once from memory.",
    "Exam traps" to "Note the trap each fact sets: 'not the Planning Commission', 'Rajya Sabha, not Lok Sabha'. Past papers (PYQs) show which traps APPSC and UPSC use again and again.",
    "Explain it simply" to "Teach the page aloud to an imaginary student in two minutes (or listen to it with read-aloud on a walk). Whatever you cannot explain, you have not understood yet.",
    "Mix subjects" to "Alternate subjects and old topics in a sitting (interleaving). It feels harder but builds the recall you need in a mixed exam paper.",
    "Error log" to "Every wrong MCQ goes into a list with the right fact and why you erred. Revise this list weekly — it is your personal weak-spot book.",
    "Sleep and short blocks" to "Memory is fixed during sleep: 7 hours, and study in 60–90 minute blocks with short breaks. Revise the day's tricks just before sleeping.",
)

@Composable
private fun Strategies() {
    LazyColumn(Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(2.dp)) {
        item {
            Text(
                "Not rote learning: give each fact a hook. Every page's \"Remember it\" uses the strategy that suits its facts.",
                style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, color = C.Muted),
                modifier = Modifier.widthIn(max = 880.dp).fillMaxWidth().padding(horizontal = 20.dp, vertical = 12.dp),
            )
        }
        STRATEGIES.forEachIndexed { i, (name, how) ->
            item {
                Column(Modifier.widthIn(max = 880.dp).fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp)) {
                    Text("${i + 1}. $name", style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = C.Ink))
                    Text(how, style = TextStyle(fontSize = 14.sp, lineHeight = 21.sp, color = C.Body), modifier = Modifier.padding(top = 3.dp))
                }
            }
        }
        item { Spacer(Modifier.height(32.dp)) }
    }
}
