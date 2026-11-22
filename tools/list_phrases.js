// Lists every Greek text the app can speak, with the file id the app uses to find its recording.
// Usage: node tools/list_phrases.js > phrases.json
const fs = require('fs');
const html = fs.readFileSync(__dirname + '/../index.html', 'utf8');
const data = html.slice(html.indexOf('const I={'), html.indexOf('const TABS='));
const normSrc = html.match(/const normG=[^\n]*/)[0];
const hidSrc = html.match(/function hid\([^\n]*/)[0];
const { U, normG, hid } = new Function(data + normSrc + '\n' + hidSrc + '\nreturn {U, normG, hid};')();
const clean = t => t.replace(/ \/ /g, ', ');
const texts = new Set();
for (const u of U) {
  u.items.forEach(it => texts.add(clean(it[0])));
  (u.dlg || []).forEach(d => texts.add(clean(d[1])));
  (u.alpha || []).forEach(a => texts.add(clean(a[2] + '. ' + (u.items.find(x => normG(x[0])[0] === normG(a[1])[0]) || [''])[0])));
}
const out = [...texts].map(t => ({ id: hid(t), text: t }));
const ids = new Set(out.map(o => o.id));
if (ids.size !== out.length) throw new Error('id clash');
process.stdout.write(JSON.stringify(out, null, 0).replace(/},{/g, '},\n{') + '\n');
