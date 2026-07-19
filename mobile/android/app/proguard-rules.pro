# Flutter engine and embedding keep rules.
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }
-keep class io.flutter.embedding.** { *; }
-dontwarn io.flutter.embedding.**

# Google Play Core split-install classes referenced by Flutter's deferred
# components support; not bundled, so silence the missing-class warnings.
-dontwarn com.google.android.play.core.**
