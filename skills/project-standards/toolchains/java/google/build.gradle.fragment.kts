import net.ltgt.gradle.errorprone.errorprone

plugins {
    id("com.diffplug.spotless") version "{{LATEST_STABLE_VERSION}}"
    id("net.ltgt.errorprone") version "{{LATEST_STABLE_VERSION}}"
}

dependencies {
    errorprone("com.google.errorprone:error_prone_core:{{LATEST_STABLE_VERSION}}")
}

spotless {
    java {
        googleJavaFormat()
        forbidWildcardImports()
        forbidModuleImports()
    }
}

tasks.withType<JavaCompile>().configureEach {
    options.compilerArgs.addAll(listOf("-Xlint:all", "-Werror"))
    options.errorprone.error(
        "MissingOverride",
        "EmptyCatch",
        "Finalize",
        "FallThrough",
        "MissingDefault",
        "StaticQualifiedUsingExpression",
        "MultipleTopLevelClasses",
        "UngroupedOverloads",
        "UnnecessaryStaticImport",
        "MultiVariableDeclaration",
        "MixedArrayDimensions",
        "LongLiteralLowerCaseSuffix",
        "MissingBraces",
    )
}
