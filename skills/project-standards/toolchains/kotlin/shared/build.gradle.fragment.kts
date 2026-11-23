plugins {
    id("com.diffplug.spotless") version "{{LATEST_STABLE_VERSION}}"
}

spotless {
    kotlin {
        ktlint()
    }
    kotlinGradle {
        ktlint()
    }
}

kotlin {
    compilerOptions {
        allWarningsAsErrors.set(true)
    }
}
