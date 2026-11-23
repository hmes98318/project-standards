plugins {
    id("com.diffplug.spotless") version "{{LATEST_STABLE_VERSION}}"
    id("net.ltgt.errorprone") version "{{LATEST_STABLE_VERSION}}"
}

dependencies {
    errorprone("com.google.errorprone:error_prone_core:{{LATEST_STABLE_VERSION}}")
}

spotless {
    java {
        palantirJavaFormat()
        removeUnusedImports()
        forbidWildcardImports()
        forbidModuleImports()
    }
}

tasks.withType<JavaCompile>().configureEach {
    options.compilerArgs.addAll(listOf("-Xlint:all", "-Werror"))
}
