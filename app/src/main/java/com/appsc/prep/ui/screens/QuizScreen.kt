package com.appsc.prep.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appsc.prep.data.Question
import com.appsc.prep.ui.components.Loading
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.components.ProgressLine
import com.appsc.prep.ui.components.Tag
import com.appsc.prep.ui.components.TopBar
import com.appsc.prep.ui.theme.C

const val QUIZ_SET = 10

/** Where the questions come from. kind: "row" (book, index), "unit" (book, index), "day" (day number). */
data class QuizSource(val kind: String, val book: Int, val index: Int)

/** Loads the question pool for a quiz source; null while loading. */
@Composable
fun rememberPool(src: QuizSource): List<Question>? {
    val app = LocalApp.current
    val pool by produceState<List<Question>?>(null, src) {
        value = when (src.kind) {
            "row" -> app.repo.mcq(src.book).rows[src.index] ?: emptyList()
            "unit" -> app.repo.mcq(src.book).units[src.index] ?: emptyList()
            else -> {
                val day = app.repo.plan.days.first { it.n == src.index }
                val seen = HashSet<String>()
                day.rows.flatMap { r -> app.repo.mcq(r.book).rows[r.row] ?: emptyList() }.filter { seen.add(it.id) }
            }
        }
    }
    return pool
}

/** mode: "new" = unattempted first, "wrong" = answered wrong, "all" = in order from the start. */
fun pickSet(pool: List<Question>, answers: Map<String, Boolean>, mode: String): List<Question> {
    val chosen = when (mode) {
        "wrong" -> pool.filter { answers[it.id] == false }
        "new" -> pool.filter { it.id !in answers }.ifEmpty { pool }
        else -> pool
    }
    return chosen.take(QUIZ_SET)
}

@Composable
fun QuizScreen(src: QuizSource, mode: String, title: String, nav: Nav) {
    val app = LocalApp.current
    val store = app.store
    val pool = rememberPool(src)
    var currentMode by rememberSaveable { mutableStateOf(mode) }
    var round by rememberSaveable { mutableIntStateOf(0) }

    Column(Modifier.fillMaxSize()) {
        TopBar(title, onBack = nav::back)
        if (pool == null) {
            Loading()
            return@Column
        }
        if (pool.isEmpty()) {
            Box(Modifier.fillMaxSize().padding(32.dp), contentAlignment = Alignment.Center) {
                Text("No PYQs are filed under this section yet.", style = TextStyle(fontSize = 16.sp, color = C.Muted))
            }
            return@Column
        }
        // freeze the set for this round
        val set = remember(pool, round, currentMode) { pickSet(pool, store.answers, currentMode) }
        if (set.isEmpty()) {
            Box(Modifier.fillMaxSize().padding(32.dp), contentAlignment = Alignment.Center) {
                Text("Nothing left in this set — no wrong answers to retry.", style = TextStyle(fontSize = 16.sp, color = C.Muted))
            }
            return@Column
        }
        QuizRound(
            key = "$round-$currentMode",
            set = set,
            pool = pool,
            onNext = { m ->
                currentMode = m
                round++
            },
            onDone = nav::back,
        )
    }
}

@Composable
private fun QuizRound(
    key: String,
    set: List<Question>,
    pool: List<Question>,
    onNext: (String) -> Unit,
    onDone: () -> Unit,
) {
    val store = LocalApp.current.store
    var index by rememberSaveable(key) { mutableIntStateOf(0) }
    val picks = remember(key) { mutableStateListOf<Int>().apply { repeat(set.size) { add(-1) } } }
    val listState = rememberLazyListState()
    LaunchedEffect(index) { listState.scrollToItem(0) }

    if (index >= set.size) {
        Results(set, picks, pool, onNext, onDone)
        return
    }
    val q = set[index]
    val picked = picks[index]
    val answered = picked >= 0

    Column(Modifier.fillMaxSize()) {
        Column(Modifier.padding(horizontal = 20.dp, vertical = 10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "Question ${index + 1} of ${set.size}",
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = C.Accent),
                    modifier = Modifier.weight(1f),
                )
                val score = set.indices.count { picks[it] >= 0 && picks[it] == set[it].answer }
                Text("Score $score", style = TextStyle(fontSize = 13.sp, color = C.Muted))
            }
            Spacer(Modifier.height(6.dp))
            ProgressLine((index + if (answered) 1 else 0) / set.size.toFloat())
        }
        LazyColumn(Modifier.weight(1f), state = listState) {
            item(key = "q-${q.id}") {
                Column(Modifier.padding(horizontal = 20.dp)) {
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(vertical = 6.dp)) {
                        if (q.appsc) Tag("APPSC", C.ExamBg, C.ExamInk)
                        if (q.source.isNotBlank()) Tag(q.source)
                    }
                    Text(
                        q.stem,
                        style = TextStyle(fontSize = 17.sp, lineHeight = 25.sp, fontWeight = FontWeight.Medium, color = Color.Black),
                    )
                    if (q.table.isNotEmpty()) QuestionTable(q.table)
                    Spacer(Modifier.height(14.dp))
                    q.options.forEachIndexed { i, opt ->
                        OptionCard(i, opt, picked, q.answer) {
                            if (!answered) {
                                picks[index] = i
                                store.recordAnswer(q.id, i == q.answer)
                            }
                        }
                    }
                    if (answered) {
                        Spacer(Modifier.height(8.dp))
                        Explanation(q, picked == q.answer)
                    }
                    Spacer(Modifier.height(20.dp))
                }
            }
        }
        Row(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 12.dp), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            if (!answered) {
                OutlinedButton(
                    onClick = { index++ },
                    modifier = Modifier.weight(1f).height(50.dp),
                    shape = RoundedCornerShape(12.dp),
                ) { Text("Skip", color = C.Muted) }
            }
            Button(
                onClick = { index++ },
                enabled = answered,
                modifier = Modifier.weight(2f).height(50.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = C.Accent),
            ) {
                Text(
                    if (index == set.size - 1) "See results" else "Next question",
                    style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold),
                )
            }
        }
    }
}

@Composable
private fun OptionCard(i: Int, text: String, picked: Int, answer: Int, onClick: () -> Unit) {
    val answered = picked >= 0
    val isAnswer = i == answer
    val isPicked = i == picked
    val (bg, border, ink) = when {
        answered && isAnswer -> Triple(C.GreenSoft, C.Green, C.Green)
        answered && isPicked -> Triple(C.HighSoft, C.High, C.High)
        else -> Triple(Color.White, C.Line, C.Ink)
    }
    Row(
        Modifier
            .padding(vertical = 5.dp)
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .border(1.5.dp, border, RoundedCornerShape(12.dp))
            .background(bg)
            .clickable(enabled = !answered, onClick = onClick)
            .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier.size(28.dp).clip(CircleShape).background(if (answered && (isAnswer || isPicked)) border else C.Chip),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                "${i + 1}",
                style = TextStyle(
                    fontSize = 13.sp, fontWeight = FontWeight.Bold,
                    color = if (answered && (isAnswer || isPicked)) Color.White else C.Muted,
                ),
            )
        }
        Spacer(Modifier.width(12.dp))
        Text(text, style = TextStyle(fontSize = 15.sp, lineHeight = 21.sp, color = ink), modifier = Modifier.weight(1f))
        if (answered && isAnswer) Icon(Icons.Filled.CheckCircle, null, tint = C.Green, modifier = Modifier.size(22.dp))
        if (answered && isPicked && !isAnswer) Icon(Icons.Filled.Cancel, null, tint = C.High, modifier = Modifier.size(22.dp))
    }
}

@Composable
private fun Explanation(q: Question, correct: Boolean) {
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(if (correct) C.GreenSoft else C.HighSoft)
            .padding(14.dp),
    ) {
        Text(
            if (correct) "Correct!" else "Answer: (${q.answer + 1}) ${q.options.getOrElse(q.answer) { "" }}",
            style = TextStyle(fontSize = 15.sp, lineHeight = 21.sp, fontWeight = FontWeight.Bold, color = if (correct) C.Green else C.High),
        )
        if (q.explanation.isNotBlank()) {
            Spacer(Modifier.height(8.dp))
            Text("EXPLANATION", style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, color = C.Muted, letterSpacing = 0.8.sp))
            q.explanation.split('\n').forEach {
                Text(it, style = TextStyle(fontSize = 14.sp, lineHeight = 21.sp, color = C.Body), modifier = Modifier.padding(top = 4.dp))
            }
        }
        if (q.notes.isNotEmpty()) {
            Spacer(Modifier.height(10.dp))
            Text("EXAM NOTE", style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, color = C.ExamInk, letterSpacing = 0.8.sp))
            q.notes.forEach {
                Text("• $it", style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, color = C.Body), modifier = Modifier.padding(top = 3.dp))
            }
        }
    }
}

@Composable
private fun QuestionTable(rows: List<List<String>>) {
    val cols = rows.maxOf { it.size }
    Box(
        Modifier
            .padding(top = 10.dp)
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .border(1.dp, C.Line, RoundedCornerShape(10.dp))
            .horizontalScroll(rememberScrollState()),
    ) {
        Column {
            rows.forEachIndexed { ri, r ->
                Row(Modifier.height(IntrinsicSize.Min).background(if (ri == 0) C.AccentSoft else if (ri % 2 == 0) C.Surface else Color.White)) {
                    for (c in 0 until cols) {
                        Text(
                            r.getOrElse(c) { "" },
                            style = TextStyle(
                                fontSize = 14.sp, lineHeight = 19.sp, color = if (ri == 0) C.Navy else C.Body,
                                fontWeight = if (ri == 0) FontWeight.SemiBold else FontWeight.Normal,
                            ),
                            modifier = Modifier.width(if (cols <= 2) 160.dp else 130.dp).fillMaxHeight().padding(8.dp),
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun Results(
    set: List<Question>,
    picks: List<Int>,
    pool: List<Question>,
    onNext: (String) -> Unit,
    onDone: () -> Unit,
) {
    val store = LocalApp.current.store
    val correct = set.indices.count { picks[it] == set[it].answer }
    val wrong = set.indices.count { picks[it] >= 0 && picks[it] != set[it].answer }
    val skipped = set.size - correct - wrong
    val (attempted, poolCorrect) = store.quizStats(pool.map { it.id })
    val remaining = pool.size - attempted
    val poolWrong = attempted - poolCorrect
    LazyColumn(Modifier.fillMaxSize()) {
        item {
            Column(Modifier.padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Spacer(Modifier.height(10.dp))
                Box(
                    Modifier.size(120.dp).clip(CircleShape).background(C.AccentSoft),
                    contentAlignment = Alignment.Center,
                ) {
                    Text("$correct/${set.size}", style = TextStyle(fontSize = 32.sp, fontWeight = FontWeight.Bold, color = C.Accent))
                }
                Spacer(Modifier.height(12.dp))
                // APPSC net score: +1 correct, -1/3 wrong
                val net = correct - wrong / 3f
                Text(
                    "Net score ${"%.2f".format(net)} with 1/3 negative",
                    style = TextStyle(fontSize = 15.sp, color = C.Ink, fontWeight = FontWeight.Medium),
                )
                Text(
                    "$correct correct · $wrong wrong · $skipped skipped",
                    style = TextStyle(fontSize = 13.sp, color = C.Muted),
                    modifier = Modifier.padding(top = 4.dp),
                )
                Spacer(Modifier.height(18.dp))
                Column(
                    Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).background(C.Surface).padding(14.dp),
                ) {
                    Text("This section's PYQs", style = TextStyle(fontSize = 13.sp, color = C.Muted))
                    Text(
                        "$attempted of ${pool.size} attempted · ${if (attempted == 0) 0 else poolCorrect * 100 / attempted}% accuracy",
                        style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = C.Ink),
                    )
                    Spacer(Modifier.height(8.dp))
                    ProgressLine(attempted / pool.size.toFloat())
                }
                Spacer(Modifier.height(18.dp))
                if (remaining > 0) {
                    Button(
                        onClick = { onNext("new") },
                        modifier = Modifier.fillMaxWidth().height(50.dp),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = C.Accent),
                    ) { Text("Next $QUIZ_SET questions ($remaining left)", style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold)) }
                    Spacer(Modifier.height(10.dp))
                }
                if (poolWrong > 0) {
                    OutlinedButton(
                        onClick = { onNext("wrong") },
                        modifier = Modifier.fillMaxWidth().height(50.dp),
                        shape = RoundedCornerShape(12.dp),
                    ) { Text("Retry wrong answers ($poolWrong)", color = C.High) }
                    Spacer(Modifier.height(10.dp))
                }
                OutlinedButton(
                    onClick = onDone,
                    modifier = Modifier.fillMaxWidth().height(50.dp),
                    shape = RoundedCornerShape(12.dp),
                ) { Text("Done", color = C.Ink) }
            }
        }
        item {
            Text(
                "REVIEW",
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold, color = C.Muted, letterSpacing = 1.sp),
                modifier = Modifier.padding(start = 20.dp, top = 8.dp, bottom = 4.dp),
            )
        }
        set.forEachIndexed { i, q ->
            item(key = "r-${q.id}-$i") {
                val ok = picks[i] == q.answer
                Row(Modifier.padding(horizontal = 20.dp, vertical = 10.dp)) {
                    Icon(
                        if (ok) Icons.Filled.CheckCircle else Icons.Filled.Cancel, null,
                        tint = if (ok) C.Green else if (picks[i] < 0) C.Faint else C.High,
                        modifier = Modifier.size(20.dp).padding(top = 2.dp),
                    )
                    Spacer(Modifier.width(10.dp))
                    Column {
                        Text(q.stem, style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp, color = C.Ink), maxLines = 3)
                        Text(
                            "Answer: ${q.options.getOrElse(q.answer) { "" }}",
                            style = TextStyle(fontSize = 13.sp, color = C.Green),
                            modifier = Modifier.padding(top = 2.dp),
                        )
                    }
                }
            }
        }
        item { Spacer(Modifier.height(24.dp)) }
    }
}
