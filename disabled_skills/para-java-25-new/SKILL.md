---
name: para-java-25-new
description: Use when starting a new Java 25 + Maven project in 2026, picking a scaffolder (Spring Initializr, Quarkus CLI, Micronaut CLI, Helidon CLI, Maven Archetype, JBang), wiring Maven 4 with mvnd/mvnsh, choosing packaging (Spring Boot repackage vs Maven Shade vs jlink/jpackage vs GraalVM native image), or adding the JSpecify + NullAway + Error Prone + Spotless quality stack. Triggers on questions about Java 25 LTS features (JEP 506 ScopedValue, JEP 505 structured concurrency, JEP 511 module imports, JEP 512 compact source files), Maven 4 model 4.1.0, fast builds, uber jars, native images, Spring Boot 4, Quarkus 3.31, or Micronaut 4.10.
---

# Modern Java 25 + Maven Project Starter (2026)

## Overview

Java 25 became LTS on **2025-09-16**. The 2026 toolchain stack: SDKMAN → Java 25 → Maven 4.0.x → mvnd → framework CLI → JSpecify quality gates → uber-jar + GraalVM native profile → Develocity build cache → JReleaser. Every layer is independently swappable; pick the scaffolder by app shape, not habit.

Source report: `docs/java25-maven-modern-starter.md` in this project (5,150 words, 42 cited sources).

## When to Use

- Greenfield Java service, library, CLI, or script in 2026
- Migrating an old Maven project to Java 25 / Maven 4
- Choosing between Spring Boot, Quarkus, Micronaut for a new build
- Deciding how to package: nested-JAR vs uber-jar vs jlink vs native image
- Adding null-safety / static analysis / formatting gates from day one
- Speeding up a slow Maven build

**Don't use for:** Gradle projects, Android, retrofitting an existing pre-Java-17 codebase (use a migration guide instead).

## Decision: which scaffolder?

```
What are you building?
├── Web service / typical app          → Spring Initializr (Recipe A)
├── Cloud-native, cold-start sensitive → Quarkus CLI       (Recipe B)
├── Smallest memory footprint          → Micronaut CLI
├── MicroProfile shop                  → Helidon CLI
├── Plain library (no framework)       → mvn archetype:generate (Recipe C)
├── Single-file script that may grow   → JBang → jbang export maven
└── "I want zero magic"                → Hand-rolled pom.xml
```

## Quick Reference: scaffolding commands

| Tool | Command | Notes |
|------|---------|-------|
| Spring Initializr | `curl https://start.spring.io/starter.zip -d bootVersion=4.0.0 -d javaVersion=25 -d type=maven-project -d dependencies=web,actuator -o app.zip` | Default for most apps |
| Quarkus CLI | `quarkus create app com.example:app --java=25 --maven` | `quarkus dev` = live coding + dev services |
| Micronaut CLI | `mn create-app com.example.app --build=maven --lang=java --jdk=25` | Fastest JVM startup (~656ms) |
| Helidon CLI | `helidon init` | MicroProfile / SE |
| Maven Archetype | `mvn archetype:generate -DarchetypeArtifactId=maven-archetype-quickstart -DarchetypeVersion=1.5 -DgroupId=com.example -DartifactId=app -DinteractiveMode=false` | Plain pom + JUnit |
| JBang | `jbang init hello.java` then `jbang export maven --group com.example --artifact app --version 0.1.0 hello.java` | Script → project bridge |

## Toolchain setup (do once per machine)

```bash
curl -s "https://get.sdkman.io" | bash
sdk install java 25-tem      # Eclipse Temurin LTS
sdk install maven 4.0.0
sdk install mvnd             # Maven Daemon
sdk install quarkus          # if using Quarkus
sdk install jbang
```

Pin per-project versions with `.sdkmanrc` in repo root. Use `25-graal` distribution when you need GraalVM native image.

Always commit the Maven Wrapper (`mvnw`, `mvnw.cmd`, `.mvn/wrapper/`). All framework CLIs generate it; for hand-rolled projects: `mvn wrapper:wrapper -Dmaven=4.0.0`.

## Java 25 features that change project setup

| JEP | Status in 25 | Use in new code? |
|-----|--------------|------------------|
| **512** Compact Source Files + Instance Main Methods | Final | Scripts/teaching only. Don't ship app `main` as compact file. |
| **511** Module Import Declarations | Final | Yes — `import module java.base;` over star-imports |
| **506** Scoped Values | **Final** | Yes — replace `ThreadLocal` for request-scoped context |
| **505** Structured Concurrency (5th preview) | **Preview** | Behind `--enable-preview` profile only; API still shifting |
| **519** Compact Object Headers | Product | Enable `-XX:+UseCompactObjectHeaders` for heap savings |
| **521** Generational Shenandoah | Final | GC choice now: ZGC-gen / Shenandoah-gen / G1 |
| **515** AOT Method Profiling | Final | Record once, reuse to inform AOT compilation |

**Key shift**: virtual threads are default for I/O-bound work (`Executors.newVirtualThreadPerTaskExecutor()`); reserve platform threads for CPU-bound code; replace `ThreadLocal` with `ScopedValue` for immutable per-request context.

`pom.xml` compiler config:
```xml
<plugin>
  <artifactId>maven-compiler-plugin</artifactId>
  <version>3.13.0</version>
  <configuration><release>25</release></configuration>
</plugin>
```

## Maven 4 highlights

- **Model 4.1.0**: `<parent/>` empty body inherits from `../pom.xml`; `groupId`/`version` auto-inherited.
- **`<modules>` → `<subprojects>`** (avoids JPMS clash).
- **CI-friendly versions**: `${revision}` works without Flatten plugin.
- **`--resume` / `-r`**: restart multi-project build from last failed subproject.
- **Consumer POM** auto-generated and deployed (build-only config doesn't leak to consumers).
- **`mvnenc`**: real password encryption, replaces Maven 3 obfuscation.
- **`mvnsh`**: interactive shell, keeps Maven booted across commands.
- **Maven 4 itself runs on Java 17+**, but compiles any target.

## Fast builds

| Tool | Speedup | When to use |
|------|---------|-------------|
| `mvnd` | ~40% to 2.9× | Default daily driver. `mvnd verify` |
| `mvnsh` | Eliminates JVM startup per command | Interactive iteration |
| `-T 1C` reactor parallelism | varies | Multi-module builds |
| Maven 4 incremental cache (target/ project-local repo) | re-runs skip work | Free with Maven 4 |
| Develocity Build Cache | up to 90% | Team CI (note: Build Cache Node deprecated 2026-12-31, use Develocity Edge) |

Wire Develocity into `.mvn/extensions.xml` with `com.gradle:develocity-maven-extension:2.4.0+`.

`mvnd` caveat: long-standing report (mvnd issue #867) of slowdowns on certain large monolithic projects — benchmark on your codebase before mandating.

## Packaging: pick by deployment target

| Option | Tool | Best for |
|--------|------|----------|
| **A. Nested-JAR executable** | `spring-boot-maven-plugin` repackage | Spring Boot apps; layered Docker |
| **B. True uber-jar with relocation** | `maven-shade-plugin` | Libraries with bundled deps; CLIs; classloader-finicky envs |
| **C. Custom JRE + native installer** | `jlink` + `jpackage` | Desktop apps, self-contained server runtimes |
| **D. Static native binary** | `org.graalvm.buildtools:native-maven-plugin` | Serverless, scale-to-zero, CLIs (~50ms startup, 70MB RSS) |

**Shade example (CLI):**
```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-shade-plugin</artifactId>
  <version>3.6.0</version>
  <executions><execution>
    <phase>package</phase>
    <goals><goal>shade</goal></goals>
    <configuration>
      <createDependencyReducedPom>true</createDependencyReducedPom>
      <transformers>
        <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
          <mainClass>com.example.Main</mainClass>
        </transformer>
        <transformer implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer"/>
      </transformers>
    </configuration>
  </execution></executions>
</plugin>
```

**GraalVM native profile:**
```xml
<profile><id>native</id><build><plugins>
  <plugin>
    <groupId>org.graalvm.buildtools</groupId>
    <artifactId>native-maven-plugin</artifactId>
    <version>0.10.4</version>
    <extensions>true</extensions>
    <executions><execution>
      <id>build-native</id><phase>package</phase>
      <goals><goal>compile-no-fork</goal></goals>
    </execution></executions>
  </plugin>
</plugins></build></profile>
```
Then: `sdk use java 25-graal && mvn -Pnative -DskipTests package`. Plugin auto-consults the GraalVM Reachability Metadata Repository for known libraries.

## Quality stack (day-one PR gates)

JSpecify is the **standard** annotation set in 2026 — adopted by Spring Framework 7 / Spring Boot 4, Google, JetBrains, Microsoft, Oracle, Sonar, Uber. Replace JSR-305 / Lombok / FindBugs nullability annotations with `org.jspecify.annotations.@Nullable` / `@NonNull`.

Wire NullAway + Error Prone into compiler:
```xml
<plugin>
  <artifactId>maven-compiler-plugin</artifactId>
  <version>3.13.0</version>
  <configuration>
    <release>25</release>
    <compilerArgs>
      <arg>-XDcompilePolicy=simple</arg>
      <arg>-Xplugin:ErrorProne -XepOpt:NullAway:AnnotatedPackages=com.example</arg>
    </compilerArgs>
    <annotationProcessorPaths>
      <path><groupId>com.google.errorprone</groupId><artifactId>error_prone_core</artifactId><version>2.36.0</version></path>
      <path><groupId>com.uber.nullaway</groupId><artifactId>nullaway</artifactId><version>0.12.3</version></path>
    </annotationProcessorPaths>
  </configuration>
</plugin>
```

Add **Spotless** (`com.diffplug.spotless:spotless-maven-plugin`) for Google Java Format + import order; `mvn spotless:apply` auto-fixes. Add **maven-enforcer-plugin** for banned deps and required Java/Maven versions.

## Three starter recipes

### Recipe A — Spring Boot 4 web service (default for most teams)

```bash
sdk install java 25-tem && sdk install maven 4.0.0 && sdk install mvnd
curl https://start.spring.io/starter.zip \
  -d type=maven-project -d language=java \
  -d bootVersion=4.0.0 -d javaVersion=25 \
  -d groupId=com.example -d artifactId=app \
  -d dependencies=web,actuator,validation,data-jpa,postgresql,testcontainers \
  -o app.zip && unzip app.zip -d app && cd app
mvnd verify
./mvnw spring-boot:run
```

Then add: NullAway+Error Prone, Spotless, GraalVM native profile, Develocity extension.

### Recipe B — Quarkus + GraalVM (sub-second cold start)

```bash
sdk install quarkus
quarkus create app com.example:app --java=25 --maven \
  --extension='resteasy-reactive-jackson,hibernate-orm-panache,jdbc-postgresql,smallrye-openapi'
cd app
quarkus dev    # live coding + dev services for Postgres/Keycloak
mvn -Pnative -DskipTests package   # ~50MB native binary, ~50ms startup
```

### Recipe C — Library or CLI

```bash
mvn archetype:generate -DarchetypeArtifactId=maven-archetype-quickstart \
  -DarchetypeVersion=1.5 -DgroupId=com.example -DartifactId=mytool \
  -DinteractiveMode=false
cd mytool
```

Then in `pom.xml`: `<release>25</release>`, Shade plugin (uber-jar above), JSpecify+NullAway+Error Prone, Spotless, JReleaser for Maven Central publishing.

## Releasing to Maven Central

Use **JReleaser** + GitHub Actions, not `nexus-staging-maven-plugin`. JReleaser handles GPG signing, Central staging, GitHub Release notes, and Homebrew/Scoop/Chocolatey artifacts in one config. Foojay 2025 walkthrough is canonical: https://foojay.io/today/how-to-publish-a-java-maven-project-to-maven-central-using-jreleaser-and-github-actions-2025-guide/

Typical flow: tag push → `mvn -Prelease deploy` stages → `jreleaser full-release` signs, releases on Central, drafts GitHub release.

## Benchmark numbers worth remembering

| Metric | Spring Boot | Quarkus | Micronaut |
|--------|-------------|---------|-----------|
| JVM startup | 1.909s | 1.154s | **0.656s** |
| Native startup | 0.104s | **0.049s** | 0.050s |
| Native RSS | 149.4 MB | **70.5 MB** | similar |
| Native heap | 11.0 MB | **3.2 MB** | similar |

Source: ITNEXT 2026-04 benchmark (Spring Boot 4.0.2 vs Quarkus 3.31.1 vs Micronaut 4.10.7 on Java 25).

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Using `mvn archetype:generate` for an app | Use Spring Initializr / Quarkus / Micronaut CLI; archetype is for libraries |
| Shipping JEP 512 compact source as production `main` | Use proper class for testability; compact source is for scripts/learning |
| `--enable-preview` in production for structured concurrency | JEP 505 still preview; gate behind a profile, don't ship on hot paths |
| `ThreadLocal` for new request-scoped context | Use `ScopedValue` (JEP 506 final) — works with virtual threads + `StructuredTaskScope` |
| Spring Boot repackage clashing with custom classloaders | Switch to Maven Shade with relocations |
| Mandating `mvnd` without measuring | Issue #867: known slowdowns on some monolithic projects; benchmark first |
| Using JSR-305 / FindBugs `@Nullable` | Migrate to `org.jspecify.annotations` — now the cross-vendor standard |
| Skipping Maven Wrapper | Always commit `mvnw` + `.mvn/wrapper/` so contributors don't need a specific Maven on PATH |
| Spring Boot 4 minimum Java | Still **Java 17**, not 25 — Spring hasn't dropped 17 support |
| Develocity Build Cache Node for new install | Deprecated after 2026-12-31; use Develocity Edge |

## Red flags — stop and rethink

- Adding a fat-jar plugin to a published library (consumers should depend normally)
- Picking Quarkus/Micronaut purely for "modernity" when you need Spring's ecosystem
- Wiring NullAway across third-party code (scope to your own packages with `AnnotatedPackages`)
- Running `mvn` directly when `mvnd` is installed (defeats the daemon)
- Java 25 preview flags on a production deployment artifact

## Source report

Full sourced detail with 42 citations and methodology appendix:
`/Users/wongdingfeng/scratch/test/java_project/docs/java25-maven-modern-starter.md`
