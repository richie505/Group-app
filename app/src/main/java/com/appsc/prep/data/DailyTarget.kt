package com.appsc.prep.data

import java.time.LocalDate

/**
 * The daily MCQ target (APPSC Complete's MCQs tab). Each day asks for [target] MCQs; what a day falls short is
 * carried forward as due, and MCQs done beyond a day's target clear the due first. Nothing is banked ahead:
 * extra MCQs with nothing due don't lower later days' targets.
 */
object DailyTarget {
    /** One past day: its target, MCQs done, and the due carried out of it. */
    data class Day(val date: LocalDate, val target: Int, val done: Int, val due: Int) {
        val short get() = (target - done).coerceAtLeast(0)
    }

    /** Where things stand today. [due]: carried from earlier days, after today's extra MCQs cleared some. */
    data class Status(val target: Int, val doneToday: Int, val due: Int, val days: List<Day>) {
        val leftToday get() = (target - doneToday).coerceAtLeast(0)
        val left get() = leftToday + due
    }

    /**
     * The days from [start] to the day before [today] (each with the target then in force, [targetOn]) and today.
     * [done] gives the MCQs practised on a date.
     */
    fun status(start: LocalDate, today: LocalDate, targetOn: (LocalDate) -> Int, done: (LocalDate) -> Int): Status {
        val days = ArrayList<Day>()
        var due = 0
        var d = start
        while (d.isBefore(today)) {
            val t = targetOn(d)
            due = (due + t - done(d)).coerceAtLeast(0)
            days += Day(d, t, done(d), due)
            d = d.plusDays(1)
        }
        val t = targetOn(today)
        val n = done(today)
        return Status(t, n, (due - (n - t).coerceAtLeast(0)).coerceAtLeast(0), days)
    }

    /** Target choices offered on the tab. */
    val choices = listOf(50, 100, 200, 300, 500)
    const val DEFAULT = 100
}
