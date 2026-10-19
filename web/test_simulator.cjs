// Pure arithmetic tests; no browser, network, DOM interactions or user data.
const fs=require('node:fs');const vm=require('node:vm');const assert=require('node:assert/strict');
const context=vm.createContext({window:{addEventListener(){}}});
vm.runInContext(fs.readFileSync(__dirname+'/site.js','utf8'),context);
const call=args=>vm.runInContext('simulateBrowser('+JSON.stringify(args)+')',context);
const r=call([60000,1000,400,60,3,0,0,0,0]);assert.equal(r.current,18960);assert.equal(r.future,18960);assert.equal(r.requiredIncome,60000);
const g=call([60000,1000,400,60,3,10,2,3,20]);assert.ok(Math.abs(g.future-12*(1020+412+216))<1e-8);assert.ok(Math.abs(g.futureShare-g.future/66000)<1e-12);
assert.equal(call([60000,0,0,0,0,0,0,0,0]).requiredIncome,null);
for(const args of [[0,1,1,1,1,0,0,0,0],[1,-1,1,1,1,0,0,0,0],[1,1,1,1,1,-100,0,0,0]])assert.throws(()=>call(args));
console.log('Browser companion simulator: 6 arithmetic/validation cases passed.');
