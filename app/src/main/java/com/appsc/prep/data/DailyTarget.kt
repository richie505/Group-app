package com.appsc.prep.data

import java.time.LocalDate

/**
 * APPSC Complete's MCQs tab. Each plan day has its own MCQs (those on its topics; an MCQ on several days counts on
 * the first). A past day's MCQs not tried yet are due; today's are worked through at the daily target's pace.
 */
object DailyTarget {
    /** A plan day's MCQ ids, in plan order. */
    class PlanMcqs(val days: List<Pair<PlanDay, List<String>>>)

    /** A past plan day: its MCQs, how many are not tried yet, and how many MCQs were done on that date. */
    data class DayDue(val day: PlanDay, val total: Int, val left: Int, val doneThatDay: Int)

    /** Where things stand on [today]. */
    data class Status(
        val target: Int,
        val doneToday: Int,
        val days: List<DayDue>,
        val today: PlanDay?,
        val todayLeft: Int,
        val todayTotal: Int = 0,
    ) {
        /** Not tried yet, over every past plan day from Day 1. */
        val due get() = days.sumOf { it.left }
        val leftToday get() = (target - doneToday).coerceAtLeast(0)
        val left get() = leftToday + due
    }

    /** Groups the plan's MCQs by day, each on the first day whose topics hold it. [rows] gives a notes row's MCQ ids. */
    fun planMcqs(plan: Plan, rows: (book: Int, row: Int) -> List<String>): PlanMcqs {
        val seen = HashSet<String>()
        return PlanMcqs(plan.days.map { d -> d to d.rows.flatMap { rows(it.book, it.row) }.filter { seen.add(it) } })
    }

    fun status(
        mcqs: PlanMcqs,
        today: LocalDate,
        target: Int,
        tried: (String) -> Boolean,
        done: (LocalDate) -> Int,
    ): Status {
        val past = mcqs.days.filter { it.first.date.isBefore(today) }
            .map { (d, ids) -> DayDue(d, ids.size, ids.count { !tried(it) }, done(d.date)) }
        val now = mcqs.days.firstOrNull { it.first.date == today }
        return Status(target, done(today), past, now?.first, now?.second?.count { !tried(it) } ?: 0, now?.second?.size ?: 0)
    }

    /** Target choices offered on the tab. */
    val choices = listOf(50, 100, 200, 300, 500)
    const val DEFAULT = 100
}
