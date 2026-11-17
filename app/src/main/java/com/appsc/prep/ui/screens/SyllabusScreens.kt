package com.appsc.prep.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appsc.prep.data.SylLeaf
import com.appsc.prep.ui.components.Card
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.components.PageList
import com.appsc.prep.ui.components.ProgressLine
import com.appsc.prep.ui.components.SectionHeader
import com.appsc.prep.ui.components.Tag
import com.appsc.prep.ui.components.TopBar
import com.appsc.prep.ui.theme.C

/** Answered and right, per official leaf (from the MCQ -> leaf map and the answers so far). */
@Composable
private fun leafStats(): Map<String, Pair<Int, Int>>? {
    val app = LocalApp.current
    val leafOf by produceState<Map<String, String>?>(null) { value = app.repo.leafOf() }
    val answers = app.store.answers
    return remember(leafOf, answers) {
        leafOf?.let { m ->
            val out = HashMap<String, IntArray>()
            for ((id, right) in answers) {
                val l = m[id] ?: continue
                if (l.isEmpty()) continue
                val a = out.getOrPut(l) { IntArray(2) }
                a[0]++
                if (right) a[1]++
            }
            out.mapValues { it.value[0] to it.value[1] }
        }
    }
}

@Composable
private fun PriTag(pri: String) = when (pri) {
    "HIGH" -> Tag("HIGH", C.HighSoft, C.High)
    "MED" -> Tag("MED", C.MedSoft, C.Med)
    else -> Tag("LIGHT")
}

/** "2011 ×5 · 2017 ×3": the Group 2 papers that asked a leaf, by year. */
fun yearsText(years: List<Int>): String =
    years.filter { it > 0 }.groupingBy { it }.eachCount().toSortedMap().entries.joinToString(" · ") { (y, n) -> if (n > 1) "$y ×$n" else "$y" }

/** Group 2: the official APPSC syllabus (27-04-2023): Prelims and Mains subjects, the official papers, weak leaves. */
@Composable
fun SyllabusScreen(nav: Nav) {
    val app = LocalApp.current
    val syl = app.repo.syllabus ?: return
    val stats = leafStats()
    Column(Modifier.fillMaxSize()) {
        TopBar("Official syllabus", onBack = nav::back)
        PageList(Modifier.fillMaxSize(), max = 900.dp) {
            item {
                Text(
                    "APPSC Group II syllabus (${syl.source.substringAfterLast(", ")}), in APPSC's own words. Every topic, MCQ and PYQ " +
                        "of the app is tied to the exact line it is asked under.",
                    style = TextStyle(fontSize = 13.sp, lineHeight = 18.sp, color = C.Muted),
                    modifier = Modifier.padding(start = 20.dp, end = 20.dp, top = 14.dp),
                )
            }
            for (stage in listOf("Prelims", "Mains")) {
                item { SectionHeader(if (stage == "Prelims") "Prelims (Screening Test)" else "Mains (Paper I and II)") }
                syl.subjects.withIndex().filter { it.value.stage == stage }.forEach { (si, s) ->
                    item(key = "s$si") {
                        val ls = s.leaves
                        val tried = stats?.let { st -> ls.count { (st[it.code]?.first ?: 0) > 0 } }
                        Card(onClick = { nav.sylSubject(si) }) {
                            Column(Modifier.padding(14.dp)) {
                                Text(s.paper.uppercase(), style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, color = C.Accent))
                                Text("${s.title} (${s.marks} marks)", style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold, color = C.Ink))
                                Text(
                                    "${s.units.size} units · ${ls.size} syllabus lines · ${ls.sumOf { it.q }} MCQs · ${ls.sumOf { it.pyq }} PYQs (${ls.sumOf { it.g2 }} from Group 2 papers)",
                                    style = TextStyle(fontSize = 12.sp, color = C.Muted), modifier = Modifier.padding(top = 2.dp),
                                )
                                if (tried != null) {
                                    Spacer(Modifier.height(8.dp))
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        ProgressLine(tried / ls.size.coerceAtLeast(1).toFloat(), Modifier.weight(1f))
                                        Spacer(Modifier.width(10.dp))
                                        Text("$tried/${ls.size} lines practised", style = TextStyle(fontSize = 12.sp, color = C.Muted))
                                    }
                                }
                            }
                        }
                    }
                }
            }
            if (syl.papers.isNotEmpty()) {
                item { SectionHeader("Official Group 2 papers") }
                syl.papers.forEachIndexed { pi, p ->
                    item(key = "p$pi") {
                        val (a, c) = app.store.quizStats(p.ids)
                        Card(onClick = { nav.quiz("paper", 0, pi, "all") }) {
                            Column(Modifier.padding(14.dp)) {
                                Text(p.name, style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = C.Ink))
                                Text(
                                    "${p.ids.size} questions with APPSC's key · practise it like any MCQ set" +
                                        if (a > 0) " · $a done, ${c * 100 / a}% right" else "",
                                    style = TextStyle(fontSize = 12.sp, color = C.Muted), modifier = Modifier.padding(top = 2.dp),
                                )
                            }
                        }
                    }
                }
            }
            item {
                SectionHeader("Your weak lines")
                Card(onClick = { nav.weak() }) {
                    Column(Modifier.padding(14.dp)) {
                        Text("Weak syllabus lines", style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = C.Ink))
                        Text(
                            "The official lines where your MCQ accuracy is lowest, to practise first.",
                            style = TextStyle(fontSize = 12.sp, color = C.Muted), modifier = Modifier.padding(top = 2.dp),
                        )
                    }
                }
                Spacer(Modifier.height(24.dp))
            }
        }
    }
}

/** One subject of the official syllabus: its units, their phrases and lines, with what the app has for each. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun SylSubjectScreen(index: Int, nav: Nav) {
    val app = LocalApp.current
    val syl = app.repo.syllabus ?: return
    val s = syl.subjects.getOrNull(index) ?: return
    val stats = leafStats()
    Column(Modifier.fillMaxSize()) {
        TopBar(s.title, onBack = nav::back)
        PageList(Modifier.fillMaxSize(), max = 900.dp) {
            item {
                Text(
                    "${s.stage} · ${s.paper} · ${s.marks} marks",
                    style = TextStyle(fontSize = 13.sp, color = C.Muted),
                    modifier = Modifier.padding(start = 20.dp, end = 20.dp, top = 14.dp),
                )
            }
            s.units.forEach { u ->
                item(key = u.code) { SectionHeader("${u.code} · ${u.title}") }
                u.phrases.forEach { p ->
                    item(key = p.code) {
                        Text(
                            "${p.code}  ${p.text}",
                            style = TextStyle(fontSize = 14.sp, lineHeight = 19.sp, fontWeight = FontWeight.SemiBold, color = C.Ink),
                            modifier = Modifier.padding(start = 20.dp, end = 20.dp, top = 6.dp, bottom = 2.dp),
                        )
                    }
                    p.leaves.forEach { l ->
                        item(key = "l" + l.code) {
                            LeafRow(l, stats?.get(l.code), showText = p.leaves.size > 1 || l.text != p.text) { nav.leaf(syl.leaves.indexOf(l)) }
                        }
                    }
                }
            }
            item { Spacer(Modifier.height(24.dp)) }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun LeafRow(l: SylLeaf, st: Pair<Int, Int>?, showText: Boolean = true, onClick: () -> Unit) {
    Card(onClick = onClick) {
        Column(Modifier.padding(12.dp)) {
            if (showText) Text(l.text, style = TextStyle(fontSize = 14.sp, lineHeight = 19.sp, color = C.Ink))
            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier.padding(top = 6.dp)) {
                Tag(l.code, C.AccentSoft, C.Accent)
                PriTag(l.pri)
                Tag("${l.q} MCQs · ${l.pyq} PYQs")
                if (l.g2 > 0) Tag("Group 2 asked ${l.g2}", C.ExamBg, C.ExamInk)
                if (st != null && st.first > 0) {
                    val pc = st.second * 100 / st.first
                    Tag("You: ${st.first} done · $pc%", if (pc >= 70) C.GreenSoft else C.HighSoft, if (pc >= 70) C.Green else C.High)
                }
            }
            if (l.years.isNotEmpty()) {
                Text("Asked in Group 2: " + yearsText(l.years), style = TextStyle(fontSize = 12.sp, color = C.Muted), modifier = Modifier.padding(top = 4.dp))
            }
        }
    }
}

/** One line of the official syllabus: its topics (notes), its MCQs and PYQs to practise, and the years it was asked. */
@Composable
fun LeafScreen(index: Int, nav: Nav) {
    val app = LocalApp.current
    val syl = app.repo.syllabus ?: return
    val l = syl.leaves.getOrNull(index) ?: return
    val stats = leafStats()
    Column(Modifier.fillMaxSize()) {
        TopBar(l.code, onBack = nav::back)
        PageList(Modifier.fillMaxSize(), max = 900.dp) {
            item {
                Column(Modifier.padding(start = 20.dp, end = 20.dp, top = 14.dp)) {
                    Text(l.text, style = TextStyle(fontSize = 19.sp, lineHeight = 25.sp, fontWeight = FontWeight.Bold, color = C.Ink))
                    if (l.phrase != l.text) {
                        Text("Syllabus: " + l.phrase, style = TextStyle(fontSize = 13.sp, lineHeight = 18.sp, color = C.Muted), modifier = Modifier.padding(top = 4.dp))
                    }
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(top = 8.dp)) {
                        PriTag(l.pri)
                        if (l.g2 > 0) Tag("Group 2 asked ${l.g2}", C.ExamBg, C.ExamInk)
                    }
                    Text(
                        if (l.years.isEmpty()) "Not asked in a Group 2 paper in the app yet." else "Asked in Group 2 papers: " + yearsText(l.years),
                        style = TextStyle(fontSize = 13.sp, color = C.Body), modifier = Modifier.padding(top = 8.dp),
                    )
                    stats?.get(l.code)?.takeIf { it.first > 0 }?.let { (a, c) ->
                        Text("Your MCQs here: $a answered, ${c * 100 / a}% right", style = TextStyle(fontSize = 13.sp, color = C.Body), modifier = Modifier.padding(top = 2.dp))
                    }
                }
            }
            item {
                SectionHeader("Practise")
                Column(Modifier.padding(horizontal = 20.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        onClick = { nav.quiz("leaf", 0, index) }, enabled = l.q > 0,
                        modifier = Modifier.fillMaxWidth().height(48.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = C.Accent),
                    ) { Text("All ${l.q} MCQs of this line") }
                    OutlinedButton(onClick = { nav.quiz("leafpyq", 0, index) }, enabled = l.pyq > 0, modifier = Modifier.fillMaxWidth().height(48.dp)) {
                        Text("Only the ${l.pyq} PYQs")
                    }
                    if (l.g2 > 0) {
                        OutlinedButton(onClick = { nav.quiz("leafg2", 0, index) }, modifier = Modifier.fillMaxWidth().height(48.dp)) {
                            Text("Only the ${l.g2} Group 2 PYQs", color = C.ExamInk)
                        }
                    }
                }
            }
            item { SectionHeader("Notes for this line") }
            l.rows.forEach { (b, r) ->
                item(key = "r$b:$r") {
                    val info = app.repo.rowInfo(b, r)
                    Card(onClick = { nav.row(b, r) }) {
                        Column(Modifier.padding(12.dp)) {
                            Text(info?.title ?: "Topic", style = TextStyle(fontSize = 14.sp, lineHeight = 19.sp, fontWeight = FontWeight.Medium, color = C.Ink))
                            Text(app.repo.index.getOrNull(b - 1)?.short ?: "", style = TextStyle(fontSize = 12.sp, color = C.Muted))
                        }
                    }
                }
            }
            item { Spacer(Modifier.height(24.dp)) }
        }
    }
}

/** The official lines with the lowest accuracy (at least 5 answered), weakest first. */
@Composable
fun WeakLeavesScreen(nav: Nav) {
    val app = LocalApp.current
    val syl = app.repo.syllabus ?: return
    val stats = leafStats()
    Column(Modifier.fillMaxSize()) {
        TopBar("Weak syllabus lines", onBack = nav::back)
        PageList(Modifier.fillMaxSize(), max = 900.dp) {
            if (stats == null) {
                item { Text("Loading…", modifier = Modifier.padding(20.dp), style = TextStyle(color = C.Muted)) }
                return@PageList
            }
            val weak = syl.leaves.mapNotNull { l -> stats[l.code]?.takeIf { it.first >= 5 }?.let { l to it } }
                .sortedBy { (_, s) -> s.second.toFloat() / s.first }.take(40)
            item {
                Text(
                    if (weak.isEmpty()) "Answer at least 5 MCQs of a syllabus line to see how you do on it."
                    else "Lowest accuracy first (lines with 5 or more MCQs answered). Tap one to practise it.",
                    style = TextStyle(fontSize = 13.sp, lineHeight = 18.sp, color = C.Muted),
                    modifier = Modifier.padding(start = 20.dp, end = 20.dp, top = 14.dp, bottom = 6.dp),
                )
            }
            weak.forEach { (l, s) ->
                item(key = l.code) { LeafRow(l, s) { nav.leaf(syl.leaves.indexOf(l)) } }
            }
            item { Spacer(Modifier.height(24.dp)) }
        }
    }
}
