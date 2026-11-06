package com.appsc.prep.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appsc.prep.R
import com.appsc.prep.data.Block
import com.appsc.prep.data.Run
import com.appsc.prep.data.TableBlock
import com.appsc.prep.data.TextBlock

/**
 * A page of the notes as a hand-written notebook page: lined paper, a handwriting font (Kalam, SIL OFL), the title and
 * section headings under a yellow highlighter, each section in its own coloured box, tables drawn by hand, and a
 * doodle for the topic. The text is the notes' own, unchanged.
 */
private val Hand = FontFamily(Font(R.font.kalam_regular, FontWeight.Normal), Font(R.font.kalam_bold, FontWeight.Bold))
private val Paper = Color(0xFFFCFCF8)
private val Rule = Color(0xFFD6E2F0)
private val Margin = Color(0xFFF2B8B8)
private val Ink = Color(0xFF1F2A5A)
private val Strong = Color(0xFF0D1440)
private val Highlight = Color(0xB3FFE45C)
private val Boxes = listOf(Color(0xFF2F5BD3), Color(0xFF2E8B57), Color(0xFF7B4FC9), Color(0xFFE07B1F), Color(0xFFD1477A), Color(0xFF1F9AA3))

private fun hand(runs: List<Run>): AnnotatedString = buildAnnotatedString {
    for (r in runs) {
        if (r.fullForm || (r.muted && r.text.trim().startsWith("["))) continue // tags and added full forms: not on paper
        withStyle(if (r.bold) SpanStyle(fontWeight = FontWeight.Bold, color = Strong) else SpanStyle()) { append(r.text) }
    }
}

private fun Modifier.highlighter() = drawBehind {
    drawRoundRect(Highlight, Offset(-4f, size.height * 0.35f), Size(size.width + 8f, size.height * 0.62f), CornerRadius(8f, 8f))
}

/** [blocks] of one page, as a notebook page titled [title] (with [topic] under it) and the [doodle] of its topic. */
@Composable
fun NotebookPage(title: String, topic: String, blocks: List<Block>, doodle: String?, modifier: Modifier = Modifier) {
    val base = TextStyle(fontFamily = Hand, color = Ink, fontSize = 17.sp, lineHeight = 26.sp)
    // sections: the lines under each heading (lines before the first heading make a section of their own)
    val sections = mutableListOf<Pair<TextBlock?, MutableList<Block>>>()
    for (b in blocks) {
        if (b is TextBlock && b.kind == 'n') continue
        if (b is TextBlock && b.kind == 'h') sections += b to mutableListOf() else {
            if (sections.isEmpty()) sections += null to mutableListOf()
            sections.last().second += b
        }
    }
    Column(
        modifier.background(Paper).drawBehind {
            var y = 34.dp.toPx()
            while (y < size.height) {
                drawLine(Rule, Offset(0f, y), Offset(size.width, y), 1.dp.toPx()); y += 28.dp.toPx()
            }
            drawLine(Margin, Offset(22.dp.toPx(), 0f), Offset(22.dp.toPx(), size.height), 1.5.dp.toPx())
        }.padding(start = 30.dp, end = 14.dp, top = 16.dp, bottom = 20.dp),
    ) {
        Row(verticalAlignment = Alignment.Top) {
            Column(Modifier.weight(1f)) {
                Text(title, style = base.copy(fontSize = 25.sp, lineHeight = 32.sp, fontWeight = FontWeight.Bold, color = Strong), modifier = Modifier.highlighter())
                Spacer(Modifier.height(6.dp))
                Text(topic, style = base.copy(fontSize = 14.sp, lineHeight = 20.sp, color = Color(0xFF3B4A8C)))
            }
            if (doodle != null) {
                Spacer(Modifier.width(8.dp))
                Doodle(doodle, Modifier.size(96.dp))
            }
        }
        Spacer(Modifier.height(12.dp))
        sections.forEachIndexed { i, (head, body) ->
            val c = Boxes[i % Boxes.size]
            Column(
                Modifier.fillMaxWidth().padding(vertical = 7.dp)
                    .border(2.dp, c, RoundedCornerShape(14.dp))
                    .background(Color.White.copy(alpha = 0.55f), RoundedCornerShape(14.dp))
                    .padding(horizontal = 12.dp, vertical = 10.dp),
            ) {
                if (head != null) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(Modifier.size(26.dp).border(2.dp, c, RoundedCornerShape(13.dp)), contentAlignment = Alignment.Center) {
                            Text("${i + 1}", style = base.copy(fontSize = 14.sp, lineHeight = 16.sp, fontWeight = FontWeight.Bold, color = c))
                        }
                        Spacer(Modifier.width(8.dp))
                        Text(hand(head.runs), style = base.copy(fontSize = 19.sp, fontWeight = FontWeight.Bold, color = Strong), modifier = Modifier.highlighter())
                    }
                    Spacer(Modifier.height(4.dp))
                }
                body.forEach { b ->
                    when (b) {
                        is TableBlock -> HandTable(b, c, base)
                        is TextBlock -> {
                            val sub = b.kind == 's'
                            val exam = b.kind == 'x'
                            Row(Modifier.padding(start = if (sub) 18.dp else 0.dp, top = 2.dp, bottom = 2.dp)) {
                                Text(if (exam) "★" else if (sub) "–" else "•", style = base.copy(fontWeight = FontWeight.Bold, color = c), modifier = Modifier.width(16.dp))
                                Text(hand(b.runs), style = if (sub) base.copy(fontSize = 16.sp) else base)
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun HandTable(t: TableBlock, c: Color, base: TextStyle) {
    val rows = listOf(t.head) + t.rows
    Column(Modifier.fillMaxWidth().padding(vertical = 6.dp).border(1.5.dp, c, RoundedCornerShape(6.dp))) {
        rows.forEachIndexed { ri, row ->
            Row(
                Modifier.fillMaxWidth().background(if (ri == 0) Highlight.copy(alpha = 0.35f) else Color.Transparent),
                horizontalArrangement = Arrangement.spacedBy(0.dp),
            ) {
                row.forEachIndexed { ci, cell ->
                    Box(Modifier.weight(if (ci == row.lastIndex && row.size > 2) 1.6f else 1f).padding(horizontal = 6.dp, vertical = 4.dp)) {
                        Text(hand(cell), style = base.copy(fontSize = 15.sp, lineHeight = 21.sp, fontWeight = if (ri == 0) FontWeight.Bold else null))
                    }
                }
            }
            if (ri < rows.lastIndex) Box(Modifier.fillMaxWidth().height(1.dp).background(c.copy(alpha = 0.5f)))
        }
    }
}

/** A topic's doodle, drawn in a 100x100 box with a felt-pen look. */
@Composable
fun Doodle(name: String, modifier: Modifier) {
    Canvas(modifier) {
        val k = size.minDimension / 100f
        when (name) {
            "solar" -> solar(k)
            "bank" -> bank(k)
            "chair" -> chair(k)
        }
    }
}

private val Pen = Color(0xFF26304F)

private fun DrawScope.pen(path: Path, k: Float, color: Color = Pen, w: Float = 2.2f) = drawPath(path, color, style = Stroke(width = w * k))

private fun DrawScope.solar(k: Float) {
    val sun = Offset(50 * k, 50 * k)
    for (r in listOf(24f, 34f, 44f)) {
        drawOval(Color(0xFF8AA4D6), Offset(sun.x - r * k, sun.y - r * 0.55f * k), Size(2 * r * k, 1.1f * r * k), style = Stroke(1.4f * k))
    }
    for (a in 0 until 12) {
        val t = Math.toRadians(a * 30.0)
        drawLine(Color(0xFFF2A516), Offset(sun.x + (13 * k * Math.cos(t)).toFloat(), sun.y + (13 * k * Math.sin(t)).toFloat()),
            Offset(sun.x + (18 * k * Math.cos(t)).toFloat(), sun.y + (18 * k * Math.sin(t)).toFloat()), 2.2f * k)
    }
    drawCircle(Color(0xFFFFC93C), 11 * k, sun); drawCircle(Color(0xFFE08A12), 11 * k, sun, style = Stroke(2 * k))
    listOf(Triple(74f, 50f, Color(0xFF4A90E2)), Triple(26f, 41f, Color(0xFFD9534F)), Triple(58f, 26f, Color(0xFFB07D48)), Triple(88f, 58f, Color(0xFF5BC0BE)))
        .forEach { (x, y, c) -> drawCircle(c, 5 * k, Offset(x * k, y * k)); drawCircle(Pen, 5 * k, Offset(x * k, y * k), style = Stroke(1.2f * k)) }
    drawOval(Pen, Offset(51 * k, 23.5f * k), Size(14 * k, 5 * k), style = Stroke(1.2f * k)) // the ringed one
}

private fun DrawScope.bank(k: Float) {
    val roof = Path().apply { moveTo(10 * k, 34 * k); lineTo(50 * k, 10 * k); lineTo(90 * k, 34 * k); close() }
    drawPath(roof, Color(0xFF6E8FD8)); pen(roof, k)
    drawRect(Color(0xFFDDE5F7), Offset(14 * k, 34 * k), Size(72 * k, 6 * k)); pen(Path().apply { addRect(androidx.compose.ui.geometry.Rect(14 * k, 34 * k, 86 * k, 40 * k)) }, k)
    for (x in listOf(20f, 38f, 56f, 74f)) {
        drawRect(Color(0xFFEFF2F8), Offset(x * k, 42 * k), Size(7 * k, 36 * k))
        pen(Path().apply { addRect(androidx.compose.ui.geometry.Rect(x * k, 42 * k, (x + 7) * k, 78 * k)) }, k, w = 1.6f)
    }
    pen(Path().apply { addRect(androidx.compose.ui.geometry.Rect(10 * k, 80 * k, 90 * k, 88 * k)) }, k)
    drawCircle(Color(0xFFFFC93C), 5 * k, Offset(50 * k, 25 * k)); drawCircle(Pen, 5 * k, Offset(50 * k, 25 * k), style = Stroke(1.2f * k))
}

private fun DrawScope.chair(k: Float) {
    // a high-backed chair (the Chairman of the Rajya Sabha) and a ballot box
    drawRoundRect(Color(0xFFC0392B), Offset(16 * k, 12 * k), Size(30 * k, 40 * k), CornerRadius(8 * k, 8 * k))
    drawRoundRect(Pen, Offset(16 * k, 12 * k), Size(30 * k, 40 * k), CornerRadius(8 * k, 8 * k), style = Stroke(2 * k))
    drawRect(Color(0xFFA0522D), Offset(12 * k, 52 * k), Size(38 * k, 8 * k)); drawRect(Pen, Offset(12 * k, 52 * k), Size(38 * k, 8 * k), style = Stroke(2 * k))
    for (x in listOf(15f, 43f)) drawLine(Pen, Offset(x * k, 60 * k), Offset(x * k, 86 * k), 2.6f * k)
    drawRect(Color(0xFF7B9BE0), Offset(58 * k, 56 * k), Size(32 * k, 30 * k)); drawRect(Pen, Offset(58 * k, 56 * k), Size(32 * k, 30 * k), style = Stroke(2 * k))
    drawLine(Pen, Offset(66 * k, 60 * k), Offset(82 * k, 60 * k), 2.4f * k)
    drawRect(Color.White, Offset(67 * k, 42 * k), Size(14 * k, 17 * k)); drawRect(Pen, Offset(67 * k, 42 * k), Size(14 * k, 17 * k), style = Stroke(1.6f * k))
    drawLine(Color(0xFF2E8B57), Offset(70 * k, 50 * k), Offset(73 * k, 54 * k), 2 * k); drawLine(Color(0xFF2E8B57), Offset(73 * k, 54 * k), Offset(79 * k, 45 * k), 2 * k)
}
