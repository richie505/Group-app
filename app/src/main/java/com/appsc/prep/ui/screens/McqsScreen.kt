package com.appsc.prep.ui.screens

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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.outlined.EventBusy
import androidx.compose.material.icons.outlined.Replay
import androidx.compose.material.icons.outlined.Today
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appsc.prep.data.DailyTarget
import com.appsc.prep.ui.components.Card
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.components.PageList
import com.appsc.prep.ui.components.ProgressLine
import com.appsc.prep.ui.components.SectionHeader
import com.appsc.prep.ui.components.TopBar
import com.appsc.prep.ui.theme.C
import java.time.LocalDate
import java.time.format.DateTimeFormatter

private val dayFmt = DateTimeFormatter.ofPattern("EEE, d MMM")

/** Today's [DailyTarget.Status], following answers as they are given. */
@Composable
fun rememberTargetStatus(): DailyTarget.Status {
    val app = LocalApp.current
    val store = app.store
    val plan = app.repo.planMcqs
    val today = LocalDate.now()
    val target = store.targetOn(today)
    val done = store.dayLog(today).mcqs
    return remember(plan, store.answers, store.seen, today, target, done) {
        DailyTarget.status(plan, today, target, store::attempted) { d -> store.dayLog(d).mcqs }
    }
}

/**
 * APPSC Complete's MCQs tab: the MCQs of every plan day before today not tried yet (due, day by day from Day 1),
 * today's MCQs at the daily target's pace, and the ones answered wrong ([DailyTarget]).
 */
@Composable
fun McqsScreen(nav: Nav) {
    val app = LocalApp.current
    val store = app.store
    val status = rememberTargetStatus()
    val wrong = store.answers.count { !it.value }

    Column(Modifier.fillMaxSize()) {
        TopBar("MCQs")
        val lastPast = status.days.lastOrNull()?.day
        PageList(Modifier.fillMaxSize()) {
            item {
                Column(Modifier.padding(start = 20.dp, end = 20.dp, top = 20.dp, bottom = 8.dp)) {
                    Text("Left to finish today", style = TextStyle(fontSize = 13.sp, color = C.Muted))
                    Text(
                        if (status.left == 0) "All done for today" else "${status.left} MCQs",
                        style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold, color = if (status.left == 0) C.Green else C.Ink),
                    )
                    Text("Today's ${status.leftToday} + due ${status.due}", style = TextStyle(fontSize = 13.sp, color = C.Body))
                    Spacer(Modifier.height(10.dp))
                    ProgressLine(status.doneToday / status.target.coerceAtLeast(1).toFloat())
                    Spacer(Modifier.height(4.dp))
                    Text("${status.doneToday} of ${status.target} done today", style = TextStyle(fontSize = 12.sp, color = C.Muted))
                }
            }
            item {
                TargetCard(
                    icon = Icons.Outlined.EventBusy,
                    title = "Due MCQs",
                    count = status.due,
                    subtitle = when {
                        lastPast == null -> "None yet. A plan day's MCQs you don't attempt become due the next day."
                        status.due == 0 -> "Every MCQ from Day 1 to Day ${lastPast.n} is attempted."
                        else -> "Not attempted yet, from Day 1 to Day ${lastPast.n} (yesterday's plan). Oldest first."
                    },
                    ink = C.High,
                    bg = C.HighSoft,
                    onClick = if (status.due > 0) ({ nav.quiz("due", 0, 0) }) else null,
                )
                TargetCard(
                    icon = Icons.Outlined.Today,
                    title = "Today's MCQs",
                    count = status.leftToday,
                    subtitle = (status.today?.let { "Day ${it.n}: ${status.todayLeft} of its MCQs not attempted yet. " } ?: "") +
                        if (status.leftToday == 0) "Target met; tap for ${status.target} more." else "${status.doneToday} of ${status.target} done.",
                    ink = C.Accent,
                    bg = C.AccentSoft,
                    onClick = { nav.quiz("today", if (status.leftToday > 0) status.leftToday else status.target, 0) },
                )
                if (wrong > 0) {
                    TargetCard(
                        icon = Icons.Outlined.Replay,
                        title = "Answered wrong",
                        count = wrong,
                        subtitle = "Retry the ones you got wrong on the latest try.",
                        ink = C.Med,
                        bg = C.MedSoft,
                        onClick = { nav.quiz("need", 0, 0, "wrong") },
                    )
                }
            }
            item {
                SectionHeader("Daily target")
                Row(
                    Modifier.fillMaxWidth().padding(horizontal = 20.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    DailyTarget.choices.forEach { n ->
                        val on = n == status.target
                        Box(
                            Modifier.weight(1f).clip(RoundedCornerShape(10.dp))
                                .background(if (on) C.Accent else C.Chip)
                                .clickable { store.setTarget(n) }
                                .padding(vertical = 10.dp),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(
                                "$n",
                                style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = if (on) Color.White else C.Body),
                            )
                        }
                    }
                }
                Text(
                    "MCQs a day, for today's MCQs. Due MCQs come on top until cleared.",
                    style = TextStyle(fontSize = 12.sp, color = C.Muted),
                    modifier = Modifier.padding(start = 20.dp, end = 20.dp, top = 6.dp),
                )
            }
            if (status.days.isNotEmpty()) {
                item { SectionHeader("Due by day, from Day 1") }
                items(status.days.size) { i ->
                    val d = status.days[i]
                    DayLine(d) { nav.quiz("due", 0, d.day.n) }
                    HorizontalDivider(color = C.Line, modifier = Modifier.padding(horizontal = 20.dp))
                }
            }
            item { Spacer(Modifier.height(24.dp)) }
        }
    }
}

@Composable
private fun TargetCard(
    icon: ImageVector,
    title: String,
    count: Int,
    subtitle: String,
    ink: Color,
    bg: Color,
    onClick: (() -> Unit)?,
) {
    Card(onClick = onClick) {
        Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(
                Modifier.size(40.dp).clip(RoundedCornerShape(10.dp)).background(if (count > 0) bg else C.Chip),
                contentAlignment = Alignment.Center,
            ) { Icon(icon, null, tint = if (count > 0) ink else C.Faint) }
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(title, style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold, color = C.Ink), modifier = Modifier.weight(1f))
                    Text("$count", style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold, color = if (count > 0) ink else C.Faint))
                }
                Text(subtitle, style = TextStyle(fontSize = 13.sp, color = C.Muted))
            }
            if (onClick != null) {
                Spacer(Modifier.width(4.dp))
                Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = C.Faint)
            }
        }
    }
}

@Composable
private fun DayLine(d: DailyTarget.DayDue, onClick: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().clickable(enabled = d.left > 0, onClick = onClick).padding(horizontal = 20.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text("Day ${d.day.n} · ${d.day.date.format(dayFmt)}", style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium, color = C.Ink))
            Text(
                "${d.total - d.left} of ${d.total} attempted · you did ${d.doneThatDay} MCQs that day",
                style = TextStyle(fontSize = 12.sp, color = C.Muted),
            )
        }
        Text(
            if (d.left > 0) "${d.left} due" else "Done",
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = if (d.left > 0) C.High else C.Green),
        )
        if (d.left > 0) Icon(Icons.AutoMirrored.Filled.KeyboardArrowRight, null, tint = C.Faint)
    }
}
