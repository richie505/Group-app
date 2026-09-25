package com.appsc.prep

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.MenuBook
import androidx.compose.material.icons.outlined.BarChart
import androidx.compose.material.icons.outlined.BookmarkBorder
import androidx.compose.material.icons.outlined.CalendarMonth
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.appsc.prep.data.ProgressStore
import com.appsc.prep.data.Repository
import com.appsc.prep.ui.components.AppState
import com.appsc.prep.ui.components.LocalApp
import com.appsc.prep.ui.screens.BookScreen
import com.appsc.prep.ui.screens.BooksScreen
import com.appsc.prep.ui.screens.DayScreen
import com.appsc.prep.ui.screens.Nav
import com.appsc.prep.ui.screens.PlanScreen
import com.appsc.prep.ui.screens.ProgressScreen
import com.appsc.prep.ui.screens.QuizScreen
import com.appsc.prep.ui.screens.QuizSource
import com.appsc.prep.ui.screens.ReaderScreen
import com.appsc.prep.ui.screens.SavedScreen
import com.appsc.prep.ui.screens.SectionScreen
import com.appsc.prep.ui.screens.TodayScreen
import com.appsc.prep.ui.theme.C
import com.appsc.prep.ui.theme.PrepTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val app = AppState(Repository(applicationContext), ProgressStore(applicationContext))
        setContent {
            PrepTheme {
                CompositionLocalProvider(LocalApp provides app) { AppRoot() }
            }
        }
    }
}

private data class Tab(val route: String, val label: String, val icon: ImageVector)

private val tabs = listOf(
    Tab("today", "Today", Icons.Outlined.Home),
    Tab("plan", "Plan", Icons.Outlined.CalendarMonth),
    Tab("books", "Notes", Icons.AutoMirrored.Outlined.MenuBook),
    Tab("progress", "Progress", Icons.Outlined.BarChart),
    Tab("saved", "Saved", Icons.Outlined.BookmarkBorder),
)

private class NavImpl(private val nav: NavHostController) : Nav {
    override fun quiz(kind: String, book: Int, index: Int, mode: String) = nav.navigate("quiz/$kind/$book/$index/$mode")
    override fun day(n: Int) = nav.navigate("day/$n")
    override fun row(book: Int, row: Int) = nav.navigate("row/$book/$row")
    override fun read(book: Int, row: Int, sec: Int) = nav.navigate("read/$book/$row/$sec")
    override fun book(id: Int) = nav.navigate("book/$id")
    override fun back() {
        nav.popBackStack()
    }
}

@Composable
private fun AppRoot() {
    val nav = rememberNavController()
    val actions = remember(nav) { NavImpl(nav) }
    val entry by nav.currentBackStackEntryAsState()
    val route = entry?.destination?.route
    val showBar = route in tabs.map { it.route } || route?.startsWith("day/") == true ||
        route?.startsWith("row/") == true || route?.startsWith("book/") == true

    Column(
        Modifier
            .fillMaxSize()
            .background(Color.White)
            .systemBarsPadding(),
    ) {
        Box(Modifier.weight(1f)) {
            NavHost(nav, startDestination = "today") {
                composable("today") { TodayScreen(actions) }
                composable("plan") { PlanScreen(actions) }
                composable("books") { BooksScreen(actions) }
                composable("progress") { ProgressScreen(actions) }
                composable("saved") { SavedScreen(actions) }
                composable(
                    "quiz/{k}/{b}/{i}/{m}",
                    listOf(
                        navArgument("k") { type = NavType.StringType },
                        navArgument("b") { type = NavType.IntType },
                        navArgument("i") { type = NavType.IntType },
                        navArgument("m") { type = NavType.StringType },
                    ),
                ) {
                    val a = it.arguments!!
                    val src = QuizSource(a.getString("k")!!, a.getInt("b"), a.getInt("i"))
                    val title = when (src.kind) {
                        "day" -> "Day ${src.index} PYQs"
                        else -> "PYQ Practice"
                    }
                    QuizScreen(src, a.getString("m")!!, title, actions)
                }
                composable("day/{n}", listOf(navArgument("n") { type = NavType.IntType })) {
                    DayScreen(it.arguments!!.getInt("n"), actions)
                }
                composable("book/{id}", listOf(navArgument("id") { type = NavType.IntType })) {
                    BookScreen(it.arguments!!.getInt("id"), actions)
                }
                composable(
                    "row/{b}/{r}",
                    listOf(navArgument("b") { type = NavType.IntType }, navArgument("r") { type = NavType.IntType }),
                ) {
                    SectionScreen(it.arguments!!.getInt("b"), it.arguments!!.getInt("r"), actions)
                }
                composable(
                    "read/{b}/{r}/{s}",
                    listOf(
                        navArgument("b") { type = NavType.IntType },
                        navArgument("r") { type = NavType.IntType },
                        navArgument("s") { type = NavType.IntType },
                    ),
                ) {
                    ReaderScreen(it.arguments!!.getInt("b"), it.arguments!!.getInt("r"), it.arguments!!.getInt("s"), actions)
                }
            }
        }
        if (showBar) {
            HorizontalDivider(color = C.Line)
            NavigationBar(containerColor = Color.White, tonalElevation = 0.dp, modifier = Modifier.height(68.dp)) {
                val current = tabs.firstOrNull { it.route == route }?.route ?: when {
                    route?.startsWith("day/") == true -> "plan"
                    else -> "books"
                }
                tabs.forEach { t ->
                    NavigationBarItem(
                        selected = current == t.route,
                        onClick = {
                            nav.navigate(t.route) {
                                popUpTo("today") { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Icon(t.icon, t.label) },
                        label = { Text(t.label, style = TextStyle(fontSize = 12.sp)) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = C.Accent,
                            selectedTextColor = C.Accent,
                            indicatorColor = C.AccentSoft,
                            unselectedIconColor = C.Muted,
                            unselectedTextColor = C.Muted,
                        ),
                        modifier = Modifier.padding(top = 2.dp),
                    )
                }
            }
        }
    }
}
