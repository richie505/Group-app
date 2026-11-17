package com.appsc.prep.data

import java.time.LocalDate

/**
 * APPSC Complete's MCQs tab. Each plan day has its own MCQs (those on its topics; an MCQ on several days counts on
 * the first). Today's are today's plan day's MCQs not attempted yet; a past day's MCQs not attempted are due.
 */
object DueMcqs {
    /** A plan day's MCQ ids, in plan order. */
    class PlanMcqs(val days: List<Pair<PlanDay, List<String>>>)

    /** A plan day: its MCQs and how many are not attempted yet. */
    data class DayDue(val day: PlanDay, val total: Int, val left: Int) {
        val attempted get() = total - left
    }

    /** Where things stand on a date: the past plan days ([days]) and today's plan day ([today], if in the plan). */
    data class Status(val days: List<DayDue>, val today: DayDue?) {
        /** Not attempted, over every past plan day from Day 1. */
        val due get() = days.sumOf { it.left }
        val todayLeft get() = today?.left ?: 0
        /** Today's MCQs and what is due: what the tab's badge shows. */
        val left get() = todayLeft + due
    }

    /**
     * Groups the plan's MCQs by day, each on the first day whose topics hold it; a topic met on several days gives
     * each day its [PlanRow.share] (spread evenly over its MCQs). [rows] gives a notes row's MCQ ids.
     */
    fun planMcqs(plan: Plan, rows: (book: Int, row: Int) -> List<String>): PlanMcqs {
        val seen = HashSet<String>()
        val own = plan.days.map { d ->
            d.rows.flatMap { r -> rows(r.book, r.row).filterIndexed { i, _ -> i % 20 < r.share } }.filter { seen.add(it) }
        }
        return PlanMcqs(plan.days.zip(if (plan.spread) spread(plan.days, own) else own))
    }

    /**
     * [Plan.spread]: over each run of study days, the same number of MCQs a day. An MCQ never comes before the day of
     * its topic, so a heavy topic's extra moves on to the next days (tools/build_plan_mcq.py does the same).
     */
    private fun spread(days: List<PlanDay>, own: List<List<String>>): List<List<String>> {
        val out = own.toMutableList()
        var i = 0
        while (i < days.size) {
            if (days[i].type != "study") { i++; continue }
            var j = i
            while (j < days.size && days[j].type == "study") j++
            val flat = (i until j).flatMap { own[it] }
            val n = j - i
            var have = 0
            var prev = 0
            for (k in 0 until n) {
                have += own[i + k].size
                val cum = minOf(have, (flat.size.toLong() * (k + 1) / n).toInt())
                out[i + k] = flat.subList(prev, cum)
                prev = cum
            }
            i = j
        }
        return out
    }

    fun status(mcqs: PlanMcqs, today: LocalDate, tried: (String) -> Boolean): Status {
        fun due(d: PlanDay, ids: List<String>) = DayDue(d, ids.size, ids.count { !tried(it) })
        return Status(
            mcqs.days.filter { it.first.date.isBefore(today) }.map { (d, ids) -> due(d, ids) },
            mcqs.days.firstOrNull { it.first.date == today }?.let { (d, ids) -> due(d, ids) },
        )
    }
}
