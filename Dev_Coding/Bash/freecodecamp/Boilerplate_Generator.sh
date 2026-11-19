#!/bin/bash
# Made by: Hazzard
# FreeCodeCamp: Learn Bash by Building a Boilerplate
# Automates the creation of a standard frontend web project structure

echo "~~ Project Boilerplate Generator ~~"
echo ""

PROJECT_NAME=${1:-"my-project"}

echo "Creating project directory: $PROJECT_NAME"
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME" || exit 1

mkdir -p src/css src/js src/assets dist tests

echo "<!-- Boilerplate index.html -->
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>$PROJECT_NAME</title>
    <link rel=\"stylesheet\" href=\"src/css/style.css\">
</head>
<body>
    <header>
        <h1>Welcome to $PROJECT_NAME</h1>
    </header>
    <main>
        <p>Project initialized with FreeCodeCamp Bash boilerplate.</p>
    </main>
    <script src=\"src/js/index.js\"></script>
</body>
</html>" > index.html

echo "/* Project Stylesheet */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    padding: 2rem;
}" > src/css/style.css

echo "// Project Entrypoint
console.log('Project $PROJECT_NAME initialized successfully!');" > src/js/index.js

echo "# $PROJECT_NAME

Generated using FreeCodeCamp Bash boilerplate.

## Structure
- \`index.html\`: Root HTML markup
- \`src/\`: Source files (JS, CSS, Assets)
- \`dist/\`: Production build artifacts
- \`tests/\`: Automated test suites
" > README.md

echo ""
echo "Project structure generated successfully:"
ls -R
