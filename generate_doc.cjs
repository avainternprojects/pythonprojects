const fs = require('fs');
const path = require('path');

const projectRoot = __dirname;
const srcDir = path.join(projectRoot, 'src');
const outputFile = path.join(projectRoot, 'ProjectDocument.md');

function walkDir(dir, callback) {
    fs.readdirSync(dir).forEach(f => {
        let dirPath = path.join(dir, f);
        let isDirectory = fs.statSync(dirPath).isDirectory();
        isDirectory ? 
            walkDir(dirPath, callback) : callback(path.join(dir, f));
    });
}

let markdown = `# Project Documentation\n\n## Source Code\n\n`;

walkDir(srcDir, (filePath) => {
    if (filePath.endsWith('.js') || filePath.endsWith('.jsx') || filePath.endsWith('.css')) {
        const relativePath = path.relative(projectRoot, filePath);
        const code = fs.readFileSync(filePath, 'utf8');
        const ext = path.extname(filePath).replace('.', '');
        markdown += `### ${relativePath.replace(/\\/g, '/')}\n\n`;
        markdown += `\`\`\`${ext}\n${code}\n\`\`\`\n\n`;
    }
});

fs.writeFileSync(outputFile, markdown);
console.log('ProjectDocument.md generated successfully.');
