# =============================================================================
# MULTI-STAGE DOCKERFILE FOR DOC-INTEL BACKEND
# =============================================================================
# Stage 1: Build the application using Maven
# Stage 2: Run the application using a slim JRE image
#
# Multi-stage builds keep the final image small because we don't include
# Maven, source code, or build tools in the production image.
# =============================================================================

# ---------------------------------------------------------------------------
# STAGE 1: BUILD
# ---------------------------------------------------------------------------
# We use the official Maven image with Eclipse Temurin JDK 17 to compile
# our Spring Boot application and package it as a JAR file.
FROM maven:3.9-eclipse-temurin-17 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy just the POM file first and download dependencies.
# Docker caches this layer, so dependencies are only re-downloaded
# when pom.xml changes (not when source code changes).
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Now copy the source code and build the application
COPY src ./src
RUN mvn package -DskipTests -B

# ---------------------------------------------------------------------------
# STAGE 2: RUNTIME
# ---------------------------------------------------------------------------
# We use a slim JRE-only image (no JDK, no Maven) for the final container.
# This makes the image much smaller (~300MB vs ~800MB).
FROM eclipse-temurin:17-jre

# Set the working directory
WORKDIR /app

# Create the uploads directory where documents will be stored
RUN mkdir -p /app/uploads

# Copy the built JAR from the build stage
# The JAR file is in target/ directory after Maven build
COPY --from=build /app/target/*.jar app.jar

# Expose port 8080 so Docker knows which port the app listens on
EXPOSE 8080

# Set the entrypoint to run our Spring Boot application
# -Djava.security.egd: Speeds up random number generation in containers
ENTRYPOINT ["java", "-Djava.security.egd=file:/dev/./urandom", "-jar", "app.jar"]
