import * as ts from 'typescript';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { NextResponse } from 'next/server'; // Import NextResponse for Next.js responses

export async function POST(req: Request) { // Next.js Route Handler - POST method
  try {
    const requestBody = await req.json(); // Parse JSON request body in Next.js
    const tsxCode = requestBody?.tsxCode;

    if (!tsxCode || typeof tsxCode !== 'string') {
      return NextResponse.json({ error: 'Bad Request', message: 'Missing or invalid TSX code in request body.' }, { status: 400 });
    }

    // 1. Find or create tsconfig.json (or use programmatic options)
    // const getTsConfigPath = () => {
    //     const currentDir = path.dirname(fileURLToPath(import.meta.url));
    //     const tsConfigPath = ts.findConfigFile(
    //         currentDir,
    //         ts.sys.fileExists,
    //         "tsconfig.json"
    //     );
    //     return tsConfigPath;
    // };

    // const tsConfigPath = getTsConfigPath();

    // if (!tsConfigPath) {
    //     return NextResponse.json({ error: 'Server Error', message: "tsconfig.json not found in the current directory or any parent directory." }, { status: 500 });
    // }

    // // 2. Load tsconfig.json
    // const configFileResult = ts.readConfigFile(tsConfigPath, ts.sys.readFile);
    // if (configFileResult.error) {
    //     return NextResponse.json({ error: 'Server Error', message: "Error reading tsconfig.json.", details: configFileResult.error }, { status: 500 });
    // }

    const compilerOptions = {
      target: ts.ScriptTarget.ES5,
      lib: ["esnext"],
      allowJs: true,
      skipLibCheck: true,
      strict: true,
      noEmit: true,
      esModuleInterop: true,
      module: ts.ModuleKind.ESNext,
      moduleResolution: ts.ModuleResolutionKind.Bundler,
      resolveJsonModule: true,
      isolatedModules: true,
      jsx: ts.JsxEmit.ReactJSX, // or ts.JsxEmit.ReactJSX, ts.JsxEmit.ReactJSXDev, depending on your needs
  };
    // Ensure JSX is enabled (if not already in tsconfig.json)
    // if (!compilerOptions.jsx) {
    //     compilerOptions.jsx = ts.JsxEmit.ReactJSX; // Or ts.JsxEmit.ReactJSXDev for development
    // }
    // compilerOptions.noEmit = true; // We only want validation, not output files

    // 3. Create a virtual file system
    const fileName = "in-memory-tsx.tsx"; // A virtual filename
    const sourceFile = ts.createSourceFile(
        fileName,
        tsxCode,
        ts.ScriptTarget.Latest,
        true, // set to `true` to create a full AST
        ts.ScriptKind.TSX
    );

    const host = ts.createCompilerHost(compilerOptions);

    // Override `readFile` and `fileExists` to use our in-memory content
    const originalReadFile = host.readFile;
    host.readFile = (filePath) => {
        if (filePath === fileName) {
            return sourceFile.text;
        }
        return originalReadFile(filePath); // Fallback to default file reading for other files
    };

    const originalFileExists = host.fileExists;
    host.fileExists = (filePath) => {
        if (filePath === fileName) {
            return true;
        }
        return originalFileExists(filePath);
    };

    // 4. Create a TypeScript program and get diagnostics
    const program = ts.createProgram([fileName], compilerOptions, host);
    const diagnostics = ts.getPreEmitDiagnostics(program);

    // 5. Format and process diagnostics
    const formatHost: ts.FormatDiagnosticsHost = {
        getCanonicalFileName: path => path,
        getCurrentDirectory: ts.sys.getCurrentDirectory,
        getNewLine: () => ts.sys.newLine
    };

    const formattedDiagnostics = ts.formatDiagnosticsWithColorAndContext(diagnostics, formatHost);

    if (diagnostics.length > 0) {
        const errorMessages = diagnostics.map(diagnostic => {
            return ts.formatDiagnostic(diagnostic, formatHost); // Get individual error messages
        });
        return NextResponse.json({
            isValid: false,
            errors: errorMessages,
            formattedDiagnostics: formattedDiagnostics // Optionally include full formatted string
        }, { status: 400 });
    } else {
        return NextResponse.json({ isValid: true, message: "TSX validation successful!" }, { status: 200 });
    }

  } catch (error) {
    console.error("Error during TSX validation:", error);
    return NextResponse.json({ error: 'Server Error', message: 'Failed to validate TSX code.' }, { status: 500 });
  }
}