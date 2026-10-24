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
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
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
import java.time.format.DateTimeFormatter

private val dayFmt = DateTimeFormatter.ofPattern("EEE, d MMM")

/**
 * APPSC Complete's MCQs tab: a daily MCQ target, what earlier days fell short carried forward as due, and the
 * MCQs to clear it ([DailyTarget]).
 */
@Composable
fun McqsScreen(nav: Nav) {
    val app = LocalApp.current
    val store = app.store
    val status = store.targetStatus()
    val wrong = store.answers.count { !it.value }
    var confirmFresh by remember { mutableStateOf(false) }

    Column(Modifier.fillMaxSize()) {
        TopBar("MCQs")
        PageList(Modifier.fillMaxSize()) {
            item {
                Column(Modifier.padding(start = 20.dp, end = 20.dp, top = 20.dp, bottom = 8.dp)) {
                    Text("Left to finish today", style = TextStyle(fontSize = 13.sp, color = C.Muted))
                    Text(
                        if (status.left == 0) "All done for today" else "${status.left} MCQs",
                        style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold, color = if (status.left == 0) C.Green else C.Ink),
                    )
                    Text(
                        "Today's ${status.leftToday} + due ${status.due}",
                        style = TextStyle(fontSize = 13.sp, color = C.Body),
                    )
                    Spacer(Modifier.height(10.dp))
                    ProgressLine(status.doneToday / status.target.coerceAtLeast(1).toFloat())
                    Spacer(Modifier.height(4.dp))
                    Text(
                        "${status.doneToday} of ${status.target} done today",
                        style = TextStyle(fontSize = 12.sp, color = C.Muted),
                    )
                }
            }
            item {
                TargetCard(
                    icon = Icons.Outlined.EventBusy,
                    title = "Due MCQs",
                    count = status.due,
                    subtitle = if (status.due == 0) "Nothing due. Days you fall short of your target add here."
                    else "Carried from days you fell short. From the plan days already past, oldest first.",
                    ink = C.High,
                    bg = C.HighSoft,
                    onClick = if (status.due > 0) ({ nav.quiz("target", status.due, 0) }) else null,
                )
                TargetCard(
                    icon = Icons.Outlined.Today,
                    title = "Today's MCQs",
                    count = status.leftToday,
                    subtitle = if (status.leftToday == 0) "Today's target is met. Tap for ${status.target} more; they clear due MCQs first."
                    else "${status.doneToday} of ${status.target} done. From today's plan topics.",
                    ink = C.Accent,
                    bg = C.AccentSoft,
                    onClick = { nav.quiz("target", if (status.leftToday > 0) status.leftToday else status.target, 1) },
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
                    "MCQs a day. A new target counts from today; earlier days keep theirs.",
                    style = TextStyle(fontSize = 12.sp, color = C.Muted),
                    modifier = Modifier.padding(start = 20.dp, end = 20.dp, top = 6.dp),
                )
            }
            if (status.days.isNotEmpty()) {
                item { SectionHeader("Day by day") }
                val recent = status.days.takeLast(30).reversed()
                items(recent.size) { i ->
                    DayLine(recent[i])
                    HorizontalDivider(color = C.Line, modifier = Modifier.padding(horizontal = 20.dp))
                }
            }
            if (status.due > 0) {
                item {
                    TextButton(onClick = { confirmFresh = true }, modifier = Modifier.padding(start = 12.dp, top = 8.dp)) {
                        Text("Start fresh from today", style = TextStyle(fontSize = 14.sp, color = C.Muted))
                    }
                }
            }
            item { Spacer(Modifier.height(24.dp)) }
        }
    }
    if (confirmFresh) {
        AlertDialog(
            onDismissRequest = { confirmFresh = false },
            title = { Text("Start fresh?") },
            text = { Text("The ${status.due} due MCQs are cleared and the target counts from today. Your answers stay.") },
            confirmButton = {
                TextButton(onClick = { store.startFresh(); confirmFresh = false }) { Text("Start fresh") }
            },
            dismissButton = { TextButton(onClick = { confirmFresh = false }) { Text("Cancel") } },
        )
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
private fun DayLine(d: DailyTarget.Day) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f)) {
            Text(d.date.format(dayFmt), style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium, color = C.Ink))
            Text("${d.done} of ${d.target} done", style = TextStyle(fontSize = 12.sp, color = C.Muted))
        }
        Column(horizontalAlignment = Alignment.End) {
            Text(
                if (d.short > 0) "+${d.short} due" else "Met",
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = if (d.short > 0) C.High else C.Green),
            )
            Text("due after: ${d.due}", style = TextStyle(fontSize = 12.sp, color = C.Muted))
        }
    }
}
