package com.appsc.prep.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appsc.prep.data.MapNode
import com.appsc.prep.ui.theme.C

/** One colour per branch, as in a drawn mind map. */
private val branchColors = listOf(
    Color(0xFF3949AB), Color(0xFF00897B), Color(0xFFD84315), Color(0xFF8E24AA), Color(0xFF2E7D32), Color(0xFF6D4C41),
)

/**
 * A page's mind map drawn as a tree that fits the screen's width (no sideways panning): the page title at the top,
 * each branch in its own colour with its facts hanging from it on connector lines. Tap a branch to fold it.
 */
@Composable
fun MindMap(title: String, branches: List<MapNode>, scale: Float) {
    Column(Modifier.fillMaxWidth().padding(horizontal = 16.dp)) {
        Text(
            title,
            style = TextStyle(fontSize = (15 * scale).sp, lineHeight = (21 * scale).sp, fontWeight = FontWeight.Bold, color = Color.White),
            modifier = Modifier.clip(RoundedCornerShape(14.dp)).background(C.Navy).padding(horizontal = 14.dp, vertical = 10.dp),
        )
        branches.forEachIndexed { i, b ->
            Connected(C.Navy, last = i == branches.lastIndex, indent = 18.dp, top = 22.dp) {
                Branch(b, branchColors[i % branchColors.size], scale)
            }
        }
    }
}

@Composable
private fun Branch(node: MapNode, color: Color, scale: Float) {
    var open by rememberSaveable(node.runs.joinToString("") { it.text }) { mutableStateOf(true) }
    Column(Modifier.padding(top = 10.dp)) {
        Row(
            Modifier
                .clip(RoundedCornerShape(12.dp))
                .background(color)
                .clickable { open = !open }
                .padding(start = 12.dp, end = 6.dp, top = 7.dp, bottom = 7.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                annotated(node.runs, base = Color.White, strong = Color.White),
                style = TextStyle(fontSize = (14.5f * scale).sp, lineHeight = (20 * scale).sp, fontWeight = FontWeight.SemiBold, color = Color.White),
                modifier = Modifier.weight(1f, fill = false),
            )
            Icon(if (open) Icons.Filled.KeyboardArrowUp else Icons.Filled.KeyboardArrowDown, null, tint = Color.White.copy(alpha = 0.85f))
        }
        if (open) Children(node.children, color, scale, depth = 1)
    }
}

@Composable
private fun Children(nodes: List<MapNode>, color: Color, scale: Float, depth: Int) {
    nodes.forEachIndexed { i, n ->
        Connected(color.copy(alpha = 0.55f), last = i == nodes.lastIndex, indent = 16.dp, top = if (depth == 1) 19.dp else 15.dp) {
            Column(Modifier.padding(top = 6.dp)) {
                Node(n, color, scale, depth)
                if (n.children.isNotEmpty()) Children(n.children, color, scale, depth + 1)
            }
        }
    }
}

@Composable
private fun Node(n: MapNode, color: Color, scale: Float, depth: Int) {
    val text = remember(n) { annotated(n.runs, strong = Color.Black) }
    when {
        n.kind == 'x' -> Text(
            text,
            style = TextStyle(fontSize = (13.5f * scale).sp, lineHeight = (19 * scale).sp, color = C.ExamInk),
            modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(C.ExamBg).padding(horizontal = 10.dp, vertical = 7.dp),
        )
        depth == 1 -> Text(
            text,
            style = TextStyle(fontSize = (14 * scale).sp, lineHeight = (20 * scale).sp, color = C.Ink, fontWeight = if (n.children.isNotEmpty()) FontWeight.SemiBold else null),
            modifier = Modifier
                .clip(RoundedCornerShape(10.dp))
                .border(1.5.dp, color.copy(alpha = 0.7f), RoundedCornerShape(10.dp))
                .background(color.copy(alpha = 0.07f))
                .padding(horizontal = 10.dp, vertical = 6.dp),
        )
        else -> Text(
            text,
            style = TextStyle(fontSize = (13.5f * scale).sp, lineHeight = (19 * scale).sp, color = C.Body),
            modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp),
        )
    }
}

/** A child hanging from its parent: an elbow line on the left (the line runs on for all but the last child). */
@Composable
private fun Connected(line: Color, last: Boolean, indent: Dp, top: Dp, content: @Composable () -> Unit) {
    Row(Modifier.fillMaxWidth().height(IntrinsicSize.Min)) {
        Box(
            Modifier
                .width(indent)
                .fillMaxHeight()
                .drawBehind {
                    val x = 6.dp.toPx()
                    val y = top.toPx()
                    val w = 2.dp.toPx()
                    drawLine(line, Offset(x, 0f), Offset(x, if (last) y else size.height), strokeWidth = w)
                    drawLine(line, Offset(x, y), Offset(size.width, y), strokeWidth = w)
                },
        )
        Box(Modifier.weight(1f)) { content() }
    }
    Spacer(Modifier.height(0.dp))
}
