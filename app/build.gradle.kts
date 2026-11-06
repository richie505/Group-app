plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("org.jetbrains.kotlin.plugin.serialization")
    id("io.github.takahirom.roborazzi")
}

android {
    namespace = "com.appsc.prep"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.appsc.prep"
        minSdk = 26
        targetSdk = 35
        versionCode = 132
        versionName = "3.21"
    }

    signingConfigs {
        // Fixed key kept in the repo so every build can update the installed app in place.
        create("app") {
            storeFile = rootProject.file("keystore/appsc-prep.jks")
            storePassword = "appscprep"
            keyAlias = "appsc-prep"
            keyPassword = "appscprep"
        }
    }

    // Two apps from one code base: the full notes, and the exam-ready revision notes (tools/build_revision.py).
    // They install side by side, each with its own progress.
    flavorDimensions += "edition"
    productFlavors {
        create("notes") {
            dimension = "edition"
            resValue("string", "app_name", "APPSC Prep")
        }
        create("revise") {
            dimension = "edition"
            applicationIdSuffix = ".revise"
            resValue("string", "app_name", "APPSC Revision")
        }
        // the three apps' notes in one: Prep's syllabus, ROCKET sheets as the core, CA app + Prep current affairs
        create("complete") {
            dimension = "edition"
            applicationIdSuffix = ".complete"
            resValue("string", "app_name", "APPSC Complete")
        }
        // APPSC Complete with every MCQ as one-liners, one per fact, no explanations (tools/oneliner_import.py)
        create("oneliner") {
            dimension = "edition"
            applicationIdSuffix = ".oneliner"
            resValue("string", "app_name", "APPSC One-liners")
        }
        // APPSC Complete with its notes written from its own MCQs (tools/c2_build.py): same topics, pages and MCQ ids,
        // so an APPSC Complete backup restores into it; installs beside APPSC Complete
        create("complete2") {
            dimension = "edition"
            applicationIdSuffix = ".complete2"
            resValue("string", "app_name", "APPSC Complete 2.0")
        }
        // APPSC Complete cut down to the Group 2 syllabus, with its own plan (tools/group2_build.py); installs beside it
        create("group2") {
            dimension = "edition"
            applicationIdSuffix = ".group2"
            versionNameSuffix = "-g2"
            resValue("string", "app_name", "APPSC Group 2")
        }
        // APPSC Complete's full notes for reading only: no MCQs, simple meanings and markers (tools/reader_build.py)
        create("reader") {
            dimension = "edition"
            applicationIdSuffix = ".reader"
            resValue("string", "app_name", "APPSC Reader")
        }
    }
    // its assets: APPSC Complete's, with its own MCQs, topic counts and edition (src/oneliner/assets) in their place
    sourceSets["oneliner"].assets.setSrcDirs(listOf(layout.buildDirectory.dir("generated/onelinerAssets")))
    sourceSets["reader"].assets.setSrcDirs(listOf(layout.buildDirectory.dir("generated/readerAssets")))
    sourceSets["complete2"].assets.setSrcDirs(listOf(layout.buildDirectory.dir("generated/complete2Assets")))
    // APPSC Complete: its full notes, plus Complete 2.0's notes written from the MCQs as "MCQ notes" (mbook*.json)
    sourceSets["complete"].assets.srcDir(layout.buildDirectory.dir("generated/completeMcqNotes"))

    buildTypes {
        debug {
            signingConfig = signingConfigs.getByName("app")
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.getByName("app")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
    }
    lint {
        // a false alarm: every produceState here sets value (the check misses `value = ...` behind `by`)
        disable += "ProduceStateDoesNotAssignValue"
    }
    testOptions {
        unitTests.isIncludeAndroidResources = true
        // ./gradlew testNotesDebugUnitTest --tests '*SpeechAuditTest' -Pspeech.audit=/path/out.tsv dumps read-aloud text
        unitTests.all { test ->
            // the tests run on the debug builds: the same code and data, plus the test-only screen host
            // (ui-test-manifest) that release builds leave out, so the release copies cannot start a screen
            if (test.name.contains("Release")) test.enabled = false
            project.findProperty("speech.audit")?.let { test.systemProperty("speech.audit", it) }
            project.findProperty("sample.tag")?.let { test.systemProperty("sample.tag", it) }
            project.findProperty("acronym.audit")?.let { test.systemProperty("acronym.audit", it) }
            test.systemProperty("prep.strict", "true") // a failing read-aloud rule fails the tests (skipped on phones)
            test.maxHeapSize = "6g" // the tall blueprint pilot images (BlueprintPilotTest)
        }
    }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2024.12.01")
    implementation(composeBom)
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.media:media:1.7.0") // MediaStyle notification for read-aloud
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("androidx.browser:browser:1.8.0") // Google in a Chrome tab (signed in)
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("androidx.navigation:navigation-compose:2.8.5")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")

    // Screenshot tests (JVM, no device needed): ./gradlew recordRoborazziNotesDebug
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.robolectric:robolectric:4.14.1")
    testImplementation("io.github.takahirom.roborazzi:roborazzi:1.39.0")
    testImplementation("io.github.takahirom.roborazzi:roborazzi-compose:1.39.0")
    testImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}

// APPSC One-liners' assets (see sourceSets above): src/complete/assets, with src/oneliner/assets taking precedence
val onelinerAssets = tasks.register<Sync>("onelinerAssets") {
    from("src/oneliner/assets")
    from("src/complete/assets") {
        exclude { f -> file("src/oneliner/assets/${f.relativePath.pathString}").exists() }
    }
    into(layout.buildDirectory.dir("generated/onelinerAssets"))
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}
// every APPSC One-liners task (asset merge, lint, tests) reads them
tasks.matching { it.name.contains("Oneliner") }.configureEach { dependsOn(onelinerAssets) }

// APPSC Complete 2.0's assets: src/complete/assets, with src/complete2/assets (its notes, edition) taking precedence
val complete2Assets = tasks.register<Sync>("complete2Assets") {
    from("src/complete2/assets")
    from("src/complete/assets") {
        exclude { f -> file("src/complete2/assets/${f.relativePath.pathString}").exists() }
    }
    into(layout.buildDirectory.dir("generated/complete2Assets"))
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}
tasks.matching { it.name.contains("Complete2") }.configureEach { dependsOn(complete2Assets) }

// APPSC Reader's assets: APPSC Complete's notes (no MCQs, no MCQ notes), with src/reader/assets taking precedence
val readerAssets = tasks.register<Sync>("readerAssets") {
    from("src/reader/assets")
    from("src/complete/assets") {
        include("book*.json", "keyterms.json", "plan.json", "exams.json", "empty.json", "moved.json", "notemoves.json")
        exclude { f -> file("src/reader/assets/${f.relativePath.pathString}").exists() }
    }
    into(layout.buildDirectory.dir("generated/readerAssets"))
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}
tasks.matching { it.name.contains("Reader") }.configureEach { dependsOn(readerAssets) }

val completeMcqNotes = tasks.register<Sync>("completeMcqNotes") {
    // the MCQ notes in simple English (tools/simple_build.py), else Complete 2.0's as written
    from(if (file("src/complete/mcqnotes/book1.json").exists()) "src/complete/mcqnotes" else "src/complete2/assets") {
        include("book*.json")
        rename("book(\\d+)\\.json", "mbook$1.json")
    }
    into(layout.buildDirectory.dir("generated/completeMcqNotes"))
}
tasks.matching { it.name.contains("Complete") && !it.name.contains("Complete2") }.configureEach { dependsOn(completeMcqNotes) }
