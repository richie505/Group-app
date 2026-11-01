package com.appsc.prep.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.appsc.prep.data.McqEdit
import com.appsc.prep.data.Question
import com.appsc.prep.ui.theme.C

/**
 * Correct an MCQ: its answer key, question text, options and explanation. [current] is the question as shown
 * (with any earlier correction); [edited] whether it has one, so it can be taken back. [onSave] gets the new
 * correction, or null to go back to the app's own version.
 */
@Composable
fun McqEditor(current: Question, edited: Boolean, onDismiss: () -> Unit, onSave: (McqEdit?) -> Unit) {
    // a structured explanation (solution bullets) is offered as plain lines to edit
    val startExpl = remember(current.id) {
        current.explanation.ifBlank { (current.solution + current.extra).joinToString("\n") { it.replace("**", "") } }
    }
    var stem by remember(current.id) { mutableStateOf(current.stem) }
    val options = remember(current.id) { mutableStateListOf(*current.options.toTypedArray()) }
    var answer by remember(current.id) { mutableIntStateOf(current.answer) }
    var noKey by remember(current.id) { mutableStateOf(current.kind == 'u' && current.answer < 0) }
    var expl by remember(current.id) { mutableStateOf(startExpl) }
    val ok = stem.isNotBlank() && options.all { it.isNotBlank() } && (noKey || answer in options.indices)

    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(Modifier.fillMaxSize().background(Color.White).imePadding()) {
            Row(Modifier.fillMaxWidth().height(60.dp).padding(horizontal = 4.dp), verticalAlignment = Alignment.CenterVertically) {
                IconButton(onClick = onDismiss) { Icon(Icons.Filled.Close, "Close", tint = C.Ink) }
                Text(
                    "Correct this MCQ",
                    style = TextStyle(fontSize = 19.sp, fontWeight = FontWeight.SemiBold, color = C.Ink),
                    modifier = Modifier.weight(1f).padding(start = 4.dp),
                )
            }
            HorizontalDivider(color = C.Line)
            Column(
                Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 12.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Column(Modifier.widthIn(max = 860.dp).fillMaxWidth()) {
                    Label("QUESTION")
                    OutlinedTextField(stem, { stem = it }, Modifier.fillMaxWidth(), minLines = 3, textStyle = TextStyle(fontSize = 15.sp))
                    Spacer(Modifier.height(14.dp))
                    Label("OPTIONS · tap the circle of the right answer")
                    options.indices.forEach { i ->
                        Row(Modifier.fillMaxWidth().padding(vertical = 3.dp), verticalAlignment = Alignment.CenterVertically) {
                            RadioButton(selected = !noKey && answer == i, onClick = { answer = i; noKey = false })
                            OutlinedTextField(
                                options[i], { options[i] = it }, Modifier.weight(1f),
                                label = { Text("Option ${i + 1}") }, textStyle = TextStyle(fontSize = 15.sp),
                            )
                        }
                    }
                    Row(
                        Modifier.fillMaxWidth().padding(top = 6.dp).clip(RoundedCornerShape(8.dp)).clickable { noKey = !noKey },
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Checkbox(noKey, { noKey = it })
                        Text("No answer key: practice only, not scored", style = TextStyle(fontSize = 14.sp, color = C.Body))
                    }
                    Spacer(Modifier.height(14.dp))
                    Label("EXPLANATION")
                    OutlinedTextField(expl, { expl = it }, Modifier.fillMaxWidth(), minLines = 4, textStyle = TextStyle(fontSize = 14.sp))
                    Spacer(Modifier.height(10.dp))
                    Text(
                        "Your correction is kept on this phone and in your backups. To send all of them on, use " +
                            "Settings › MCQ corrections.",
                        style = TextStyle(fontSize = 13.sp, color = C.Muted),
                    )
                    if (edited) {
                        TextButton(onClick = { onSave(null) }, modifier = Modifier.padding(top = 4.dp)) {
                            Text("Undo my correction (back to the app's version)", color = C.High)
                        }
                    }
                }
            }
            HorizontalDivider(color = C.Line)
            Row(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 12.dp), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(1f).height(50.dp), shape = RoundedCornerShape(12.dp)) {
                    Text("Cancel", color = C.Ink)
                }
                Button(
                    onClick = {
                        onSave(
                            McqEdit(
                                stem = stem.trim(),
                                options = options.map { it.trim() },
                                answer = if (noKey) -1 else answer,
                                // unchanged: keep the original (and its structured form)
                                explanation = if (expl == startExpl) current.explanation else expl.trim(),
                                noKey = noKey,
                            ),
                        )
                    },
                    enabled = ok,
                    modifier = Modifier.weight(1.4f).height(50.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = C.Accent),
                ) { Text("Save", style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold)) }
            }
        }
    }
}

@Composable
private fun Label(text: String) {
    Text(
        text,
        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, color = C.Muted, letterSpacing = 0.8.sp),
        modifier = Modifier.padding(bottom = 4.dp),
    )
}
