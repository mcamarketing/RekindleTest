const fs = require('fs');

const content = fs.readFileSync('c:\\Users\\Hello\\OneDrive\\Documents\\REKINDLE\\src\\pages\\AIAgents.tsx', 'utf8');
const lines = content.split('\n');

// Find the agent map start
let agentMapStart = -1;
let agentMapReturnStart = -1;
let agentMapEnd = -1;

for (let i = 0; i < lines.length; i++) {
  if (lines[i].includes('stage.agents.map((agent, agentIdx)')) {
    agentMapStart = i;
  }
  if (agentMapStart > -1 && agentMapReturnStart === -1 && lines[i].trim().startsWith('return (')) {
    agentMapReturnStart = i;
  }
  if (agentMapStart > -1 && lines[i].includes('})}')) {
    agentMapEnd = i;
    break;
  }
}

console.log(`Agent map starts at line: ${agentMapStart + 1}`);
console.log(`Return starts at line: ${agentMapReturnStart + 1}`);
console.log(`Agent map ends at line: ${agentMapEnd + 1}`);
console.log('');

// Count divs between return and closing
let openDivs = [];
let closeDivs = [];

for (let i = agentMapReturnStart; i <= agentMapEnd; i++) {
  const line = lines[i];
  const trimmed = line.trim();

  // Count opening divs (but not self-closing)
  if (/<div[^>]*>/.test(line) && !/<div[^>]*\/>/.test(line)) {
    openDivs.push({ line: i + 1, content: trimmed.substring(0, 80) });
  }

  // Count closing divs
  if (/<\/div>/.test(line)) {
    closeDivs.push({ line: i + 1, content: trimmed });
  }
}

console.log(`Opening divs: ${openDivs.length}`);
openDivs.forEach(d => console.log(`  Line ${d.line}: ${d.content}`));
console.log('');

console.log(`Closing divs: ${closeDivs.length}`);
closeDivs.forEach(d => console.log(`  Line ${d.line}: ${d.content}`));
console.log('');

console.log(`Difference: ${openDivs.length - closeDivs.length} (negative means too many closing divs)`);
