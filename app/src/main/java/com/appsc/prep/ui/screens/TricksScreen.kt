package com.appsc.prep.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appsc.prep.ui.components.Card
import com.appsc.prep.ui.components.PageList
import com.appsc.prep.ui.components.TopBar
import com.appsc.prep.ui.theme.C

/**
 * "How to crack APPSC": the tested techniques of APPSC: Cracked (docs/APPSC-Cracked.pdf) - each rule measured on
 * APPSC's own papers and on the app's ~40,000 PYQs, and a backtest on APPSC 2023-25. The same numbers drive the
 * "Stuck?" box (data/Techniques.kt).
 */
private data class TRow(val word: String, val proof: String)

private val METHOD = listOf(
    "Answer from knowledge first. A trick never overrides a fact you know.",
    "In a statement set, settle the ONE statement you are surest of, then cross out every option that disagrees with it. In a backtest on APPSC 2023–25 this alone left 2–3 options and lifted a guess from 25 to 47 in 100.",
    "Only then use the trap words below to choose among what is left.",
    "Answer whenever two or fewer options remain: with −⅓ for a wrong answer, a blind guess is worth 0, one option struck +0.11, two struck +0.33.",
)
private val FALSE_WORDS = listOf(
    TRow("… but … not …", "73% false across 40,000 PYQs · 82% in APPSC"),
    TRow("only", "68% false across all PYQs · 74% in APPSC"),
    TRow("launched / set up / implemented by …", "53–60% false: the body named is the usual error"),
    TRow("extreme words: all, never, always, every, any, entirely, must, cannot", "52–58% false"),
    TRow("a statement that itself says not / no / did not", "50–61% false"),
    TRow("main / primary / chief aim", "58% false in APPSC (weaker elsewhere)"),
    TRow("Polity: member of · Schedule · the Government · cannot be", "68–74% false"),
    TRow("Economy: a named Ministry / Department", "75% false"),
)
private val NO_EDGE = listOf(
    TRow("exact figures, percentages", "false at the base rate (38–47%): APPSC tests numbers — learn them"),
    TRow("years and dates", "base rate: APPSC asks dates straight"),
    TRow("\"the Constitution provides / Article X\"", "74% false in UPSC but only 32% in other APPSC exams: a UPSC habit that doesn't transfer"),
    TRow("named offices, international organisations, reasons (because / due to)", "base rate: use knowledge"),
)
private val TRUE_WORDS = listOf(
    TRow("Andhra Pradesh facts", "only 33% false across all PYQs, 23% in APPSC AP history"),
    TRow("Geography: \"is located in / lies in\"", "only 18% false"),
    TRow("Polity: electoral matters, Funds", "only 13–14% false"),
    TRow("\"first / largest / oldest\" (Group 2) and long multi-fact statements", "lean true in APPSC; never eliminate on them"),
)
private val OPTIONS = listOf(
    "3 statements: exactly 2 true is the most common answer (58%).",
    "4 statements: 2 or 3 true (63%); all four only 12% in Prelims.",
    "\"All of the above\": the key only 28% of the times it appears — never a default.",
    "\"None of the above / neither\": the key 39% of the time — don't dismiss it.",
    "Four numbers, no idea: one of the two middle values is the key 64% of the time.",
    "Matching: fix your surest pair, strike every code without it. The straight a-I, b-II… code is right only by chance.",
    "Chronology: place the earliest and the latest; usually one option has both.",
    "Assertion–Reason: test A, test R, then ask \"does R say WHY A happens?\" (both true + explains: 53%).",
    "Answer letters are spread evenly: there is no safe letter.",
)
private val SUBJECTS = listOf(
    "Polity" to "Harshest: ~47% of statements false; 4-statement sets often only 1–2 true. Favourite trap: a \"not\" added or removed, then a wrong category (FR vs DPSP) or a wrong Article number.",
    "Economy" to "~51% false. Favourite trap: a FLIPPED relation (raising CRR \"increases\" credit). Check the direction of every cause–effect.",
    "Indian History" to "Mostly true (31% false). Hunt for the one wrong person: a swapped ruler, author or founder. 3-statement sets: exactly 2 true.",
    "AP History & Culture" to "Gentlest: only 23% false; AP claims true 92% of the time. Traps: wrong person or wrong place. Keep ruler–capital and poet–work pairs.",
    "Geography" to "Traps: a flipped direction (east/west-flowing, higher/lower) and a wrong place. Here \"first / largest\" claims are often FALSE (67%).",
    "Science & Tech" to "Traps: a wrong agency (ISRO vs DRDO), a changed number, a flipped effect. Years and long technical statements are usually true.",
    "Current Affairs" to "The examiner swaps the venue / host country and the organiser / ministry. \"First\" claims are almost always true. Learn venue, host, edition, theme, organiser.",
    "Indian Society" to "~53% false: mostly a changed year or number on an Act (POCSO 2012, JJ Act 2015). Learn each Act's year and beneficiaries.",
)

@Composable
fun TricksScreen(nav: Nav) {
    Column(Modifier.fillMaxSize()) {
        TopBar("How to crack APPSC", onBack = { nav.back() })
        PageList(Modifier.fillMaxSize()) {
            item {
                Column(Modifier.padding(start = 20.dp, end = 20.dp, top = 18.dp, bottom = 4.dp)) {
                    Text("APPSC: CRACKED", style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, color = C.Accent, letterSpacing = 1.sp))
                    Text(
                        "Every trick here was tested on APPSC's own papers (2008–2025) and on the app's ~40,000 PYQs; base rate: 38 in 100 statements are false.",
                        style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, color = C.Body), modifier = Modifier.padding(top = 4.dp),
                    )
                }
            }
            item { Section("THE METHOD", C.Accent) { METHOD.forEachIndexed { i, t -> Line("${i + 1}. $t") } } }
            item { Section("LEAN FALSE", C.High) { FALSE_WORDS.forEach { Pair(it) } } }
            item { Section("NO EDGE — USE KNOWLEDGE", C.Muted) { NO_EDGE.forEach { Pair(it) } } }
            item { Section("LEAN TRUE", C.Green) { TRUE_WORDS.forEach { Pair(it) } } }
            item { Section("OPTIONS AND STATEMENT SETS", C.Accent) { OPTIONS.forEach { Line("• $it") } } }
            item { Section("SUBJECT BY SUBJECT", C.Accent) { SUBJECTS.forEach { (s, t) -> Pair(TRow(s, t)) } } }
            item {
                Text(
                    "In any MCQ, tap \"Stuck?\" to see the answer and its trick. For the latest papers (Group 1 Prelims 2024, Group 2 Prelims 2024, Group 2 Mains 2025) it shows the full worked method.",
                    style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp, color = C.Muted),
                    modifier = Modifier.padding(horizontal = 20.dp, vertical = 16.dp),
                )
            }
        }
    }
}

@Composable
private fun Section(title: String, ink: Color, body: @Composable () -> Unit) {
    Card {
        Column(Modifier.padding(16.dp)) {
            Text(title, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, color = ink, letterSpacing = 1.sp))
            Spacer(Modifier.height(4.dp))
            body()
        }
    }
}

@Composable
private fun Line(t: String) {
    Text(t, style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, color = C.Body), modifier = Modifier.padding(top = 5.dp))
}

@Composable
private fun Pair(r: TRow) {
    Column(Modifier.padding(top = 7.dp)) {
        Text(r.word, style = TextStyle(fontSize = 14.sp, lineHeight = 19.sp, fontWeight = FontWeight.SemiBold, color = C.Ink))
        Text(r.proof, style = TextStyle(fontSize = 13.sp, lineHeight = 18.sp, color = C.Muted))
    }
}

/** The Notes tab's way in. */
@Composable
fun TricksCard(nav: Nav) {
    Card(Modifier.padding(top = 12.dp), onClick = { nav.tricks() }) {
        Row(Modifier.padding(16.dp)) {
            Column(Modifier.weight(1f)) {
                Text("HOW TO CRACK APPSC", style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, color = C.Accent, letterSpacing = 1.sp))
                Text(
                    "The tested tricks: trap words, statement sets, options, subject by subject",
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold, color = C.Ink), modifier = Modifier.padding(top = 2.dp),
                )
                Text(
                    "Measured on APPSC's papers and ~40,000 PYQs · \"Stuck?\" in any MCQ shows the answer and its trick",
                    style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp, color = C.Muted), modifier = Modifier.padding(top = 2.dp),
                )
            }
        }
    }
}
