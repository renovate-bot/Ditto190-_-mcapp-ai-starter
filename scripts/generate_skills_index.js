const fs = require('fs');
const path = require('path');
const cwd = process.cwd();
const ignoredFragments = ['node_modules','/.git','/.venv','/venv','migration/repodumps','site-packages','.venv','__pycache__'];
const results = [];
function isIgnored(p){ return ignoredFragments.some(f => p.includes(f)); }
function walk(dir){
  let entries;
  try{ entries = fs.readdirSync(dir, { withFileTypes: true }); } catch(e){ return; }
  for(const e of entries){
    const p = path.join(dir, e.name);
    if(isIgnored(p)) continue;
    if(e.isDirectory()) walk(p);
    else if(e.isFile()){
      if(e.name.toLowerCase() === 'skill.md' || e.name === 'SKILL.md'){
        try{
          const content = fs.readFileSync(p,'utf8');
          let name = null, description = null;
          const fmMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
          if(fmMatch){
            const fm = fmMatch[1];
            fm.split(/\r?\n/).forEach(line => {
              const m = line.match(/^([a-zA-Z0-9_\-]+):\s*(?:['"]?)(.*?)(?:['"]?)\s*$/);
              if(m){ const k = m[1].toLowerCase(); const v = m[2]; if(k==='name' && !name) name = v; if(k==='description' && !description) description = v; }
            });
          }
          if(!name) name = path.basename(path.dirname(p));
          if(!description){
            const after = content.slice(fmMatch ? fmMatch[0].length : 0).trim();
            const para = after.split(/\r?\n\r?\n/)[0] || '';
            description = para.replace(/\r?\n/g,' ').slice(0,300);
          }
          results.push({ path: p.replace(/^\.\/|^\//, ''), name, description });
        } catch(e){ /* ignore read errors */ }
      }
    }
  }
}
walk(cwd);
results.sort((a,b)=> a.path.localeCompare(b.path));
fs.writeFileSync('.github/skills-index.json', JSON.stringify(results, null, 2));
let md = '# Skills Index\n\n| path | name | description |\n|---|---|---|\n' + results.map(r => `| ${r.path} | ${r.name.replace(/\|/g,'\\|')} | ${r.description.replace(/\|/g,'\\|')} |`).join('\n');
fs.writeFileSync('.github/skills-index.md', md);
console.log(`Wrote ${results.length} skills to .github/skills-index.json and .github/skills-index.md`);
