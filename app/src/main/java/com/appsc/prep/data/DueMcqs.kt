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

    /** Groups the plan's MCQs by day, each on the first day whose topics hold it. [rows] gives a notes row's MCQ ids. */
    fun planMcqs(plan: Plan, rows: (book: Int, row: Int) -> List<String>): PlanMcqs {
        val seen = HashSet<String>()
        return PlanMcqs(plan.days.map { d -> d to d.rows.flatMap { rows(it.book, it.row) }.filter { seen.add(it) } })
    }

    fun status(mcqs: PlanMcqs, today: LocalDate, tried: (String) -> Boolean): Status {
        fun due(d: PlanDay, ids: List<String>) = DayDue(d, ids.size, ids.count { !tried(it) })
        return Status(
            mcqs.days.filter { it.first.date.isBefore(today) }.map { (d, ids) -> due(d, ids) },
            mcqs.days.firstOrNull { it.first.date == today }?.let { (d, ids) -> due(d, ids) },
        )
    }
}
