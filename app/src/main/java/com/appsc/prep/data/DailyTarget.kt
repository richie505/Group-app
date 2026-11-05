package com.appsc.prep.data

import java.time.LocalDate

/**
 * Today's practice, sized from what the reader actually does (the activity log), not from the plan's totals:
 * - standard: the lower quarter of the last two weeks' practice days (a normal day, not the best ones);
 * - minimum: half of it, for a low-energy day; stretch: about a typical good day, never required.
 * Nothing carries over: a light day lowers no one's next target into debt, and three days in a row well under the
 * standard bring it down. Practice is split into sessions; each takes the revision that is due first (at most
 * a third of it), then new MCQs in the plan's order.
 */
object DailyTarget {
    /** With too little history: the lower quarter of this reader's days up to 5 Nov 2026 (620 MCQs a day). */
    const val DEFAULT = 600

    data class Targets(val minimum: Int, val standard: Int, val stretch: Int, val session: Int) {
        val sessions get() = (standard + session - 1) / session
    }

    private fun down50(x: Int) = x / 50 * 50

    fun of(activity: Map<String, DayLog>, today: LocalDate): Targets {
        val days = (1..14).mapNotNull { activity[today.minusDays(it.toLong()).toString()]?.mcqs }.filter { it >= 100 }
        var standard = if (days.size < 4) DEFAULT else days.sorted()[days.size / 4]
        standard = down50(standard).coerceIn(200, 900)
        // struggling: the last three practice days all well under it
        val recent = (1..14).mapNotNull { activity[today.minusDays(it.toLong()).toString()]?.mcqs?.takeIf { m -> m > 0 } }.take(3)
        if (recent.size == 3 && recent.all { it < standard * 0.8 }) standard = down50((standard * 0.85).toInt()).coerceAtLeast(200)
        val median = if (days.isEmpty()) standard else days.sorted()[days.size / 2]
        val stretch = maxOf(standard + 150, down50(median)).coerceAtMost(1000)
        val session = ((standard / 3 + 5) / 10 * 10).coerceAtLeast(50)
        return Targets(down50(standard / 2).coerceAtLeast(100), standard, stretch, session)
    }

    /** Revision that is due today, most needed first (wrong, then only viewed, then improving; oldest first). */
    fun dueRevision(hist: Map<String, McqHist>, today: LocalDate, keep: (String) -> Boolean): List<String> =
        hist.entries.mapNotNull { (id, h) ->
            val due = Mastery.dueOn(h) ?: return@mapNotNull null
            if (due.isAfter(today) || !keep(id)) null else Triple(id, Mastery.of(h), h.last)
        }.sortedWith(compareBy({ it.second != Mastery.REVISE }, { it.second != Mastery.LEARNING }, { it.third })).map { it.first }

    /** One session's MCQs: due revision first (at most a third), then new ones in [order]. */
    fun session(size: Int, revision: List<String>, order: List<String>, tried: (String) -> Boolean): List<String> {
        val rev = revision.take(size / 3)
        val fresh = order.asSequence().filter { !tried(it) && it !in rev }.take(size - rev.size).toList()
        // nothing new left: more revision instead
        return rev + fresh + revision.drop(rev.size).take(size - rev.size - fresh.size)
    }
}
