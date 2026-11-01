package com.appsc.prep.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.OpenInNew
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.foundation.gestures.detectVerticalDragGestures
import androidx.compose.foundation.layout.size
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.tween
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.offset
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import kotlin.math.roundToInt
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.draw.clip
import androidx.compose.ui.input.pointer.pointerInput
import kotlinx.coroutines.launch
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appsc.prep.data.Question
import com.appsc.prep.ui.theme.C

/** Code options ("1 and 2 only", "Both A and B", "All of the above") say nothing to a search engine. */
private val CODE = Regex("""(?i)^\(?(?:[1-6a-d]|i{1,3}|iv)\)?(?:\s*(?:,|and|&|-|–)\s*\(?(?:[1-6a-d]|i{1,3}|iv)\)?)*\s*(?:only)?$|^only\s+\w+$|^(?:all|none) of (?:the )?(?:above|these)$|^(?:both|neither|all|none)\b.{0,25}$|of the above|more than one|^[A-D]\s*[-–]\s*\d""")

/** Exam wording that tells a search engine nothing ("Which of the following statements is/are correct?"), line by line. */
private val BOILER = listOf(
    """(?i)\bwhich (?:one )?of the (?:followings?|above|statements?(?:/s|\(s\))?|pairs?)(?: statements?(?:/s|\(s\))?| pairs?| events?)?(?: given(?: above| below)?)?(?: is| are| is/are)?(?: not)?(?: correctly matched| incorrectly matched| correct| incorrect| true| false| wrong)?\b\s*[?:]?""",
    """(?i)\b(?:statements?(?:/s|\(s\))?\s+)?(?:is|are|is/are)\s+(?:not\s+)?(?:correctly matched|incorrectly matched|correct|incorrect|true|false|wrong)\b\s*[?:.]?""",
    """(?i)\bconsider the following(?: statements?| pairs?| events?| items?)?\s*[:-]?""",
    """(?i)\b(?:select|choose|find|identify|mark)\s+the correct\s+(?:chronological |locational |geographical )?(?:answer|code|option|sequence|order|statements?|one)\b(?: of (?:the )?(?:following|above|events?|their \w+))*""",
    """(?i)\b(?:with the help of|using|from|by using) the cod(?:es?|ing scheme) given(?: below| at the end)?\s*[:.-]?|\bcodes?\s*[:-]""",
    """(?i)\bhow many of the (?:above|following)[^?]{0,60}\??""",
    """(?i)\barrange the following in (?:the )?(?:correct )?(?:chronological )?order\s*[:.-]?""",
    """(?i)\bwith (?:reference|regard) to\b|\bregarding\b|\bin (?:the context of|reference to|regards? to)\b""",
    """(?i)\bstatement[- ]?(?:I{1,2}|[12AB])\s*[:.-]|\b(?:assertion|reason)\s*\(?[AR]\)?\s*[:.-]""",
    """^\s*\(?(?:[1-6]|[a-fA-F]|i{1,3}|iv|v|vi|I{1,3}|IV|V|VI)[.)]\s""",
    """(?:^|\s)\(?(?:[1-6]|[a-f]|i{1,3}|iv|v|vi)[.)]\s""",
).map { Regex(it) }

/**
 * What to search for an MCQ: the question's topic and facts, without the exam's set phrases (Google reads about
 * 32 words, and "Which of the following statements is/are correct" swamps them), plus options that carry facts.
 */
fun mcqQuery(q: Question): String {
    val s = q.stem.lines().joinToString(" ") { line ->
        var l = line
        BOILER.forEach { l = it.replace(l, " ") }
        l
    }.replace(Regex("[\\s,;:]+"), " ").trim().trim('?', '.', '-', '–', ' ')
    val opts = q.options.map { it.trim() }.filterNot { CODE.containsMatchIn(it) }
    val words = (s.split(' ') + if (opts.isEmpty()) emptyList() else opts.joinToString(" ").split(' ')).filter { it.isNotBlank() }
    return words.take(32).joinToString(" ").ifBlank { q.stem.replace(Regex("\\s+"), " ").take(200) }
}

/** The whole MCQ as a question for an AI answer (Google AI Mode, Gemini): which option is right, and why. */
fun mcqPrompt(q: Question): String =
    q.stem.trim() + "\n" + q.options.mapIndexed { i, o -> "(${i + 1}) $o" }.joinToString("\n") +
        "\nWhich option is correct? Give the answer and a short reason with sources."

/**
 * Google for the MCQ on screen, in a sheet that slides up from the bottom. The page scrolls; drag the top bar
 * (with the handle) down, or press Back, to close. Two tabs: Google's results for the question ([results],
 * preloaded while the question shows) and Google's AI Mode answering the whole MCQ ([ai]).
 */
@Composable
fun McqSearchSheet(
    q: Question,
    results: WebHolder?,
    ai: WebHolder?,
    startAi: Boolean = false,
    onUse: ((String) -> Unit)? = null,
    onClose: () -> Unit,
) {
    val platform = LocalApp.current.platform
    val scope = rememberCoroutineScope()
    var aiTab by remember(q.id) { mutableStateOf(startAi) }
    var told by remember(q.id) { mutableStateOf<String?>(null) }
    val url = if (aiTab) googleAiUrl(mcqPrompt(q)) else googleUrl(mcqQuery(q))
    val holder = if (aiTab) ai else results
    LaunchedEffect(url) { holder?.load(url) }
    val back = remember { mutableStateOf<(() -> Boolean)?>(null) }
    // how far the sheet sits below its open place (px): slides up on open, follows the finger on the top bar
    val offset = remember { Animatable(Float.MAX_VALUE) }
    var height by remember { mutableFloatStateOf(0f) }
    fun close() {
        scope.launch { offset.animateTo(height, tween(220)); onClose() }
    }
    // Back: a page back in the results first (a site opened from them), then closes
    Dialog(onDismissRequest = { if (holder?.goBack() != true && back.value?.invoke() != true) close() }, properties = DialogProperties(usePlatformDefaultWidth = false, decorFitsSystemWindows = false)) {
        Box(Modifier.fillMaxSize()) {
            Box(Modifier.fillMaxSize().background(Color(0x66000000)).pointerInput(Unit) { detectTapGestures { close() } })
            Column(
                Modifier.align(Alignment.BottomCenter).fillMaxWidth().fillMaxHeight(0.94f)
                    .onSizeChanged {
                        if (height == 0f) {
                            height = it.height.toFloat()
                            scope.launch { offset.snapTo(height); offset.animateTo(0f, tween(260)) }
                        }
                    }
                    .offset { IntOffset(0, offset.value.coerceIn(0f, if (height > 0f) height else 0f).roundToInt()) }
                    .graphicsLayer { alpha = if (height > 0f) 1f else 0f } // not seen before it can slide up
                    .clip(RoundedCornerShape(topStart = 20.dp, topEnd = 20.dp))
                    .background(Color.White),
            ) {
                // the top bar: drag it down to close; the page below scrolls on its own
                Column(
                    Modifier.fillMaxWidth().pointerInput(Unit) {
                        detectVerticalDragGestures(
                            onDragEnd = {
                                if (offset.value > height * 0.2f) close() else scope.launch { offset.animateTo(0f, tween(180)) }
                            },
                        ) { change, dy ->
                            change.consume()
                            scope.launch { offset.snapTo((offset.value + dy).coerceAtLeast(0f)) }
                        }
                    },
                ) {
                    Box(Modifier.fillMaxWidth().padding(top = 10.dp, bottom = 6.dp), contentAlignment = Alignment.Center) {
                        Box(Modifier.size(width = 40.dp, height = 5.dp).clip(RoundedCornerShape(3.dp)).background(C.Faint))
                    }
                    Row(
                        Modifier.fillMaxWidth().padding(start = 16.dp, end = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        FilterChip(selected = !aiTab, onClick = { aiTab = false }, label = { Text("Google results") })
                        FilterChip(selected = aiTab, onClick = { aiTab = true }, label = { Text("AI answer") })
                        Box(Modifier.weight(1f))
                        IconButton(onClick = { told = platform.askGemini(mcqPrompt(q)) }) {
                            Icon(Icons.Outlined.AutoAwesome, "Ask Gemini", tint = C.Accent)
                        }
                        IconButton(onClick = { platform.openInBrowser(url) }) {
                            Icon(Icons.AutoMirrored.Outlined.OpenInNew, "Open in Chrome", tint = C.Ink)
                        }
                    }
                    Text(
                        told ?: "Drag this bar down to close. Check the answer against more than one source.",
                        style = TextStyle(fontSize = 12.sp, color = if (told != null) C.Green else C.Muted, fontWeight = FontWeight.Normal),
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
                    )
                }
                HorizontalDivider(color = C.Line)
                val page = Modifier.fillMaxWidth().weight(1f).background(Color.White)
                if (holder != null) key(aiTab) { holder.Show(page) }
                else key(url) { platform.WebPage(url, page, back, null) }
                if (onUse != null && holder != null) {
                    @Suppress("DEPRECATION")
                    val clipboard = androidx.compose.ui.platform.LocalClipboardManager.current
                    var empty by remember { mutableStateOf(false) }
                    var picking by remember { mutableStateOf<Pair<List<String>, Boolean>?>(null) } // paragraphs, first one selected
                    picking?.let { (all, first) ->
                        PickText(all, preselect = if (first) 0 else -1, verb = "Use", onAdd = { picking = null; onUse(it); close() }) { picking = null }
                    }
                    HorizontalDivider(color = C.Line)
                    if (empty) {
                        Text(
                            "Nothing to take yet - wait for the answer to load, then tap again.",
                            style = TextStyle(fontSize = 13.sp, color = C.High),
                            modifier = Modifier.padding(start = 16.dp, end = 16.dp, top = 8.dp),
                        )
                    }
                    androidx.compose.material3.Button(
                        onClick = {
                            holder.pageText { page ->
                                val chosen = page.selection.ifBlank { clipboard.getText()?.text.orEmpty() }.trim()
                                val all = (listOfNotNull(chosen.takeIf { it.isNotBlank() }) + page.paragraphs).distinct()
                                if (all.isEmpty()) empty = true else { empty = false; picking = all to chosen.isNotBlank() }
                            }
                        },
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
                        colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = C.Green),
                    ) { Text("Use as this MCQ's explanation", style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold)) }
                }
            }
        }
    }
}
