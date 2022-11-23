if (-not(Test-Path -Path "antlr4.jar" -PathType Leaf)){
    wget "https://www.antlr.org/download/antlr-4.10.1-complete.jar" -outfile "antlr4.jar"
}
$env:CLASSPATH = ".;$pwd\antlr4.jar;"+ $env:CLASSPATH
# Generate python Python
Write-Host "Generating Cognilang language elements for Python"
java org.antlr.v4.Tool himeko_lang_core/lang/HimekoHypergraphLang.g4 -Dlanguage=Python3 -visitor -Xexact-output-dir -o hypergraph_parser/himeko_parser/gen/hypergraphlang