package com.appsc.prep.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.layout.heightIn
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appsc.prep.data.Book
import com.appsc.prep.data.PlanDay
import com.appsc.prep.data.SpeechText
import com.appsc.prep.data.UserNotes
import com.appsc.prep.data.subsectionId
import com.appsc.prep.ui.components.Card
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.components.Playback
import com.appsc.prep.ui.components.SpeechPage
import com.appsc.prep.ui.theme.C
import kotlinx.coroutines.launch

/** The pages of a plan day's topics, in the day's order: (book, row, sub-section). */
fun dayPages(day: PlanDay, books: Map<Int, Book>): List<Triple<Int, Int, Int>> =
    day.rows.flatMap { r ->
        val secs = books[r.book]?.rows?.getOrNull(r.row)?.secs.orEmpty()
        secs.indices.filter { !secs[it].empty && secs[it].blocks.isNotEmpty() }.map { Triple(r.book, r.row, it) }
    }

/**
 * "Listen to today's notes": the day's topics read aloud one after another, like an audiobook chapter, with the
 * phone's own voice (Indian English first; the reader can pick another installed voice). Keeps reading with the
 * screen locked; the notification and this card pause or stop it.
 */
@Composable
fun ListenDayCard(day: PlanDay) {
    val app = LocalApp.current
    val speech = app.platform.speech ?: return
    if (day.rows.isEmpty()) return
    val scope = rememberCoroutineScope()
    val pb = speech.playback.value
    var chooseVoice by remember { mutableStateOf(false) }
    var loading by remember { mutableStateOf(false) }
    val listId = "day:${day.n}:"
    // this card's session: the playing page is one of today's pages
    var mine by remember { mutableStateOf(false) }
    val ours = mine && pb.active

    val dl = speech.download?.value
    val folder = "Day %02d - %s%s".format(day.n, day.date, if (day.focus.isNotBlank()) " - " + day.focus.lowercase().replaceFirstChar { it.uppercase() } else "")

    /** One audio file per topic: its name, then every page of it, read like the Listen button does. */
    fun download() {
        loading = true
        scope.launch {
            val books = day.rows.map { it.book }.distinct().associateWith { app.repo.book(it) }
            app.repo.abbreviations
            app.repo.checkedAcronyms
            val chapters = day.rows.mapNotNull { r ->
                val row = books[r.book]?.rows?.getOrNull(r.row) ?: return@mapNotNull null
                val parts = row.secs.indices.filter { !row.secs[it].empty && row.secs[it].blocks.isNotEmpty() }.flatMapIndexed { j, si ->
                    val sec = row.secs[si]
                    val pid = subsectionId(r.book, r.row, si)
                    val blocks = UserNotes.withAdded(sec.blocks, pid, app.store.added).map { it.second }
                    SpeechText.parts(if (j == 0) "${row.title}. ${sec.title}" else sec.title, blocks, r.book, row.title).map { it.second }
                }
                if (parts.isEmpty()) null else row.title to parts
            }
            loading = false
            speech.saveAudiobook(folder, chapters)
        }
    }

    fun start() {
        loading = true
        scope.launch {
            val books = day.rows.map { it.book }.distinct().associateWith { app.repo.book(it) }
            app.repo.abbreviations
            app.repo.checkedAcronyms
            val pages = dayPages(day, books)
            loading = false
            if (pages.isEmpty()) return@launch
            fun page(i: Int): SpeechPage {
                val (b, r, s) = pages[i]
                val row = books[b]!!.rows[r]
                val sec = row.secs[s]
                val pid = subsectionId(b, r, s)
                val blocks = UserNotes.withAdded(sec.blocks, pid, app.store.added).map { it.second }
                // the first page of a topic says the topic's name first
                val title = if (s == pages.firstOrNull { it.first == b && it.second == r }?.third) "${row.title}. ${sec.title}" else sec.title
                return SpeechPage(pid, sec.title, SpeechText.parts(title, blocks, b, row.title).map { it.second })
            }
            var cursor = 0
            mine = true
            speech.play(page(0), 0, app.store.speechRate) {
                cursor += 1
                if (cursor < pages.size) page(cursor) else null
            }
        }
    }

    Card {
        Column(Modifier.padding(16.dp)) {
            Text("LISTEN TO TODAY'S NOTES", style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, color = C.Accent))
            Spacer(Modifier.height(4.dp))
            Text(
                "${day.rows.size} topics read aloud one after another, like an audiobook. Keeps playing with the screen locked.",
                style = TextStyle(fontSize = 14.sp, lineHeight = 19.sp, color = C.Body),
            )
            if (ours) {
                Spacer(Modifier.height(6.dp))
                Text(
                    "Now reading: " + nowTitle(pb, day, app),
                    style = TextStyle(fontSize = 13.sp, color = C.Ink, fontWeight = FontWeight.SemiBold),
                    maxLines = 2, overflow = TextOverflow.Ellipsis,
                )
            }
            Spacer(Modifier.height(10.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                when {
                    loading -> Button(onClick = {}, enabled = false) { Text("Loading…") }
                    ours && pb.playing -> {
                        Button(onClick = { speech.pause() }) { Text("Pause") }
                        OutlinedButton(onClick = { speech.stop(); mine = false }) { Text("Stop") }
                    }
                    ours -> {
                        Button(onClick = { speech.resume() }) { Text("Resume") }
                        OutlinedButton(onClick = { speech.stop(); mine = false }) { Text("Stop") }
                    }
                    else -> Button(onClick = { start() }) { Text("▶  Listen") }
                }
                TextButton(onClick = { chooseVoice = true }) { Text("Voice") }
            }
            if (speech.download != null) {
                Spacer(Modifier.height(10.dp))
                val busy = dl?.active == true
                when {
                    busy -> {
                        Text(
                            "Saving audiobook: topic ${(dl!!.done + 1).coerceAtMost(dl.total)} of ${dl.total} · ${dl.current}",
                            style = TextStyle(fontSize = 13.sp, color = C.Body), maxLines = 2, overflow = TextOverflow.Ellipsis,
                        )
                        androidx.compose.material3.LinearProgressIndicator(
                            progress = { dl.done / dl.total.coerceAtLeast(1).toFloat() },
                            modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
                        )
                        OutlinedButton(onClick = { speech.cancelAudiobook() }) { Text("Cancel download") }
                    }
                    else -> {
                        OutlinedButton(onClick = { download() }, enabled = !loading) { Text("⬇  Download today's audiobook") }
                        val saved = dl?.savedTo.orEmpty()
                        val err = dl?.error.orEmpty()
                        when {
                            saved.isNotEmpty() && dl?.folder == folder -> Text(
                                "Saved ${dl.total} audio files (one per topic) to $saved. Play them in any music app.",
                                style = TextStyle(fontSize = 13.sp, lineHeight = 18.sp, color = C.Accent), modifier = Modifier.padding(top = 6.dp),
                            )
                            err.isNotEmpty() -> Text("Could not save: $err", style = TextStyle(fontSize = 13.sp, color = C.High), modifier = Modifier.padding(top = 6.dp))
                            else -> Text(
                                "Records each topic with the chosen voice into an audio file (about 20 MB an hour) in Music → APPSC Audiobooks. Takes a while; it carries on with the screen off.",
                                style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp, color = C.Muted), modifier = Modifier.padding(top = 6.dp),
                            )
                        }
                    }
                }
            }
        }
    }
    if (chooseVoice) VoiceDialog { chooseVoice = false }
}

private fun nowTitle(pb: Playback, day: PlanDay, app: com.appsc.prep.ui.components.AppState): String {
    val (b, r) = pb.pageId.split(':').mapNotNull { it.toIntOrNull() }.let { if (it.size >= 2) it[0] to it[1] else return "" }
    val i = day.rows.indexOfFirst { it.book == b && it.row == r }
    return if (i >= 0) "topic ${i + 1} of ${day.rows.size} · ${day.rows[i].topic}" else ""
}

/** The phone's voices: Indian English first. Better or more Indian voices come from the phone's TTS settings. */
@Composable
fun VoiceDialog(onClose: () -> Unit) {
    val app = LocalApp.current
    val speech = app.platform.speech ?: return onClose()
    var list by remember { mutableStateOf<List<Pair<String, String>>?>(null) }
    var chosen by remember { mutableStateOf(speech.voice) }
    if (list == null) speech.voices { list = it }
    AlertDialog(
        onDismissRequest = onClose,
        title = { Text("Reading voice") },
        text = {
            Column {
                Text(
                    "Voices on this phone. Indian English is first. For a South Indian accent, try each Indian English voice " +
                        "(play a page after choosing) – or add voices with \"Install voices\" (Google Speech Services: English (India)).",
                    style = TextStyle(fontSize = 13.sp, lineHeight = 18.sp, color = C.Muted),
                )
                Spacer(Modifier.height(8.dp))
                val l = list
                if (l == null) Text("Loading voices…")
                else LazyColumn(Modifier.heightIn(max = 320.dp)) {
                    item {
                        Row(Modifier.fillMaxWidth().clickable { chosen = ""; speech.setVoice("") }, verticalAlignment = Alignment.CenterVertically) {
                            RadioButton(selected = chosen == "", onClick = { chosen = ""; speech.setVoice("") })
                            Text("Phone's default Indian English", style = TextStyle(fontSize = 14.sp))
                        }
                    }
                    items(l) { (id, label) ->
                        Row(Modifier.fillMaxWidth().clickable { chosen = id; speech.setVoice(id) }, verticalAlignment = Alignment.CenterVertically) {
                            RadioButton(selected = chosen == id, onClick = { chosen = id; speech.setVoice(id) })
                            Text(label, style = TextStyle(fontSize = 14.sp))
                        }
                    }
                }
            }
        },
        confirmButton = { TextButton(onClick = onClose) { Text("Done") } },
        dismissButton = { TextButton(onClick = { speech.installVoices() }) { Text("Install voices") } },
    )
}
