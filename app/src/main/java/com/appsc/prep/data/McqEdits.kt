package com.appsc.prep.data

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.int
import kotlinx.serialization.json.jsonPrimitive

/**
 * The reader's own correction of an MCQ (the pencil on the quiz screen): its text, options, answer key and
 * explanation as they should be. [answer] -1 with [noKey]: shown unscored ("No key").
 */
data class McqEdit(
    val stem: String,
    val options: List<String>,
    val answer: Int,
    val explanation: String,
    val noKey: Boolean = false,
) {
    fun encode(id: String): String = buildJsonObject {
        put("id", JsonPrimitive(id))
        put("s", JsonPrimitive(stem))
        put("o", JsonArray(options.map { JsonPrimitive(it) }))
        put("a", JsonPrimitive(answer))
        put("x", JsonPrimitive(explanation))
        if (noKey) put("k", JsonPrimitive("u"))
    }.toString()

    companion object {
        /** (id, edit) from [encode]'s text; null if it is not one. */
        fun decode(text: String): Pair<String, McqEdit>? = runCatching {
            val o = Json.parseToJsonElement(text) as JsonObject
            val opts = (o["o"] as JsonArray).map { it.jsonPrimitive.content }
            o["id"]!!.jsonPrimitive.content to McqEdit(
                stem = o["s"]!!.jsonPrimitive.content,
                options = opts,
                answer = o["a"]!!.jsonPrimitive.int,
                explanation = o["x"]?.jsonPrimitive?.content ?: "",
                noKey = o["k"]?.jsonPrimitive?.content == "u",
            )
        }.getOrNull()
    }
}

/** This question as the reader corrected it ([McqEdit]); itself when not edited. Flashcards are never edited. */
fun Question.edited(e: McqEdit?): Question {
    if (e == null || kind == 'f') return this
    val newExpl = e.explanation.trim()
    val explChanged = newExpl != explanation.trim()
    return copy(
        stem = e.stem,
        options = e.options,
        answer = if (e.noKey) -1 else e.answer,
        kind = if (e.noKey || e.answer !in e.options.indices) 'u' else 's',
        cancelled = if (e.noKey) cancelled else false,
        explanation = newExpl,
        // an explanation the reader rewrote replaces the structured one built from the old text
        solution = if (explChanged) emptyList() else solution,
        extra = if (explChanged) emptyList() else extra,
    )
}
