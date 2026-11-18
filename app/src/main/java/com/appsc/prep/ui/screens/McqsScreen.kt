package com.appsc.prep.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import com.appsc.prep.data.DueMcqs
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

/** Today's [DueMcqs.Status], following answers as they are given. */
@Composable
fun rememberDueStatus(): DueMcqs.Status {
    val app = LocalApp.current
    val store = app.store
    val plan = app.repo.planMcqs
    val today = LocalDate.now()
    return remember(plan, store.answers, store.seen, today) { DueMcqs.status(plan, today, store::attempted) }
}

/**
 * APPSC Complete's MCQs tab: today's plan-day MCQs not attempted yet, those of every plan day before today (due,
 * day by day from Day 1), and the ones answered wrong ([DueMcqs]).
 */
@Composable
fun McqsScreen(nav: Nav) {
    val app = LocalApp.current
    val store = app.store
    // this app's MCQs only (a backup also holds other apps' answers, and one-fact MCQs since merged)
    val wrong = remember(store.answers) { app.repo.planIds.let { ids -> store.answers.count { !it.value && (ids.isEmpty() || it.key in ids) } } }
    // note by note: the MCQs of the notes pages marked read, and how many of them are not tried yet
    val read = remember(store.done) { com.appsc.prep.ui.screens.readIds(app) }
    val readLeft = remember(read, store.answers, store.seen) { read.count { !store.attempted(it) } }

    Column(Modifier.fillMaxSize()) {
        TopBar("MCQs")
        PageList(Modifier.fillMaxSize()) {
            item {
                Column(Modifier.padding(start = 20.dp, end = 20.dp, top = 20.dp, bottom = 8.dp)) {
                    Text("From the notes you've read", style = TextStyle(fontSize = 13.sp, color = C.Muted))
                    Text(
                        if (read.isEmpty()) "Read a notes page first" else if (readLeft == 0) "All tried" else "$readLeft MCQs to try",
                        style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold, color = if (read.isNotEmpty() && readLeft == 0) C.Green else C.Ink),
                    )
                    if (read.isNotEmpty()) {
                        Spacer(Modifier.height(10.dp))
                        ProgressLine((read.size - readLeft) / read.size.coerceAtLeast(1).toFloat())
                        Spacer(Modifier.height(4.dp))
                        Text("${read.size - readLeft} of ${read.size} tried", style = TextStyle(fontSize = 12.sp, color = C.Muted))
                    }
                }
            }
            item {
                CountCard(
                    icon = Icons.Outlined.Today,
                    title = "From the notes you've read",
                    count = readLeft,
                    subtitle = if (read.isEmpty()) "Mark a notes page read and its MCQs show here." else
                        "MCQs of the pages you marked read, not tried yet, in book order.",
                    ink = C.Accent,
                    bg = C.AccentSoft,
                    onClick = if (read.isNotEmpty()) ({ nav.quiz("read", 0, 0, "new") }) else null,
                )
                if (wrong > 0) {
                    CountCard(
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
            item { Spacer(Modifier.height(24.dp)) }
        }
    }
}

/** A count card on the MCQs tab (also under the Today tab's practice in APPSC Complete). */
@Composable
fun CountCard(
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
private fun DayLine(d: DueMcqs.DayDue, onClick: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().clickable(enabled = d.left > 0, onClick = onClick).padding(horizontal = 20.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text("Day ${d.day.n} · ${d.day.date.format(dayFmt)}", style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium, color = C.Ink))
            Text(
                "${d.attempted} of ${d.total} attempted",
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
