package com.appsc.prep.data

import java.time.LocalDate

/**
 * Each MCQ's practice history, so an answer seen is never counted as solved:
 * R = answered right on its own, W = answered wrong on its own, V = answer viewed before trying ("Show the answer"),
 * kept newest last (at most [KEEP]), with the day of the latest one.
 */
data class McqHist(val outcomes: String, val last: LocalDate) {
    fun add(o: Char, day: LocalDate) = McqHist((outcomes + o).takeLast(KEEP), day)

    /** The latest answer given without seeing it first. */
    val lastOwn: Char? get() = outcomes.lastOrNull { it != 'V' }
    val tried get() = outcomes.any { it != 'V' }

    fun encode(id: String) = "$id\t$outcomes\t$last"

    companion object {
        const val KEEP = 8
        fun decode(s: String): Pair<String, McqHist>? {
            val p = s.split('\t')
            if (p.size < 3 || p[1].isEmpty()) return null
            val d = runCatching { LocalDate.parse(p[2]) }.getOrNull() ?: return null
            return p[0] to McqHist(p[1], d)
        }

        /** History rebuilt from what older versions kept (latest answer, answers seen first, ever answered wrong). */
        fun fromOld(answer: Boolean?, seen: Boolean, missed: Boolean, day: LocalDate): McqHist? {
            val s = buildString {
                if (seen) append('V')
                if (missed) append('W')
                if (answer == true) append('R') else if (answer == false && !missed) append('W')
            }
            return if (s.isEmpty()) null else McqHist(s, day)
        }
    }
}

/** How well an MCQ is known; it changes with every attempt, never with an answer only viewed. */
enum class Mastery(val label: String) {
    NEW("New"), LEARNING("Learning"), REVISE("Needs revision"), IMPROVING("Improving"), MASTERED("Mastered");

    companion object {
        fun of(h: McqHist?): Mastery {
            if (h == null) return NEW
            val o = h.outcomes
            return when {
                o.last() == 'V' -> LEARNING // seen, not yet answered on its own since
                o.last() == 'W' -> REVISE
                // right: first time, without help, or twice running since a slip
                o.none { it == 'W' || it == 'V' } -> MASTERED
                o.takeLastWhile { it == 'R' }.length >= 2 -> MASTERED
                else -> IMPROVING
            }
        }

        /**
         * When it should come back (spaced revision), or null when it need not: wrong or only viewed, the next day;
         * improving, three days after; mastered and new, not by themselves.
         */
        fun dueOn(h: McqHist?): LocalDate? = when (of(h)) {
            REVISE, LEARNING -> h!!.last.plusDays(1)
            IMPROVING -> h!!.last.plusDays(3)
            else -> null
        }
    }
}

/** What the practice adds up to, by kind of attempt (Progress and the daily card show these). */
data class PracticeSummary(
    val tried: Int, // answered on its own at least once
    val right: Int, // latest own answer right
    val wrong: Int, // latest own answer wrong
    val viewedOnly: Int, // answer viewed, never answered on its own
    val viewedThenTried: Int, // viewed once, answered on its own later
    val revise: Int, // needs revision (wrong, or viewed only)
    val mastered: Int,
) {
    companion object {
        fun of(hist: Map<String, McqHist>, keep: (String) -> Boolean = { true }): PracticeSummary {
            var tried = 0; var right = 0; var wrong = 0; var viewed = 0; var viewedTried = 0; var revise = 0; var mastered = 0
            for ((id, h) in hist) {
                if (!keep(id)) continue
                if (h.tried) {
                    tried++
                    if (h.lastOwn == 'R') right++ else wrong++
                    if ('V' in h.outcomes) viewedTried++
                } else viewed++
                when (Mastery.of(h)) {
                    Mastery.REVISE, Mastery.LEARNING -> revise++
                    Mastery.MASTERED -> mastered++
                    else -> {}
                }
            }
            return PracticeSummary(tried, right, wrong, viewed, viewedTried, revise, mastered)
        }
    }
}
