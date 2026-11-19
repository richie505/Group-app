-keepattributes *Annotation*, InnerClasses
-keepclassmembers class com.appsc.prep.data.** { *; }
-keep,includedescriptorclasses class com.appsc.prep.**$$serializer { *; }

# APPSC Lectures: the slides call the app (next / previous lecture, close)
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
