// Zotero: Tools > Developer > Run JavaScript, tick "Run as async function", paste, Run.
// Helpers are idempotent; each change below adds one line to the returned log.
const lib = Zotero.Libraries.userLibraryID;
const log = [];

async function item(key) {
  const it = await Zotero.Items.getByLibraryAndKeyAsync(lib, key);
  if (!it) throw new Error(`item ${key} not found`);
  return it;
}

function collection(path) { // "Parent/Child"
  let col = null;
  for (const name of path.split('/')) {
    col = Zotero.Collections.getByLibrary(lib, true)
      .find(c => c.name === name && (c.parentID || null) === (col ? col.id : null));
    if (!col) throw new Error(`collection ${path} not found`);
  }
  return col;
}

const person = (firstName, lastName) => ({ firstName, lastName, creatorType: 'author' });
const org = name => ({ lastName: name, fieldMode: 1, creatorType: 'author' });

async function create(type, fields, creators, path) { // skipped if an item with this url is already filed there
  const col = collection(path);
  const dup = fields.url && col.getChildItems(false, false)
    .find(i => i.isRegularItem() && i.getField('url') === fields.url);
  if (dup) { log.push(`exists ${dup.key} ${fields.title}`); return dup; }
  const it = new Zotero.Item(type);
  it.libraryID = lib;
  for (const [k, v] of Object.entries(fields)) it.setField(k, v);
  it.setCreators(creators);
  it.addToCollection(col.id);
  await it.saveTx();
  log.push(`created ${it.key} ${fields.title}`);
  return it;
}

async function update(key, fields, creators) {
  const it = await item(key);
  for (const [k, v] of Object.entries(fields)) it.setField(k, v);
  if (creators) it.setCreators(creators);
  await it.saveTx();
  log.push(`updated ${key} ${it.getField('title')}`);
}

async function attach(childKey, parent) { // children cannot sit in collections
  const child = await item(childKey);
  if (child.parentID) { log.push(`${childKey} already has a parent`); return; }
  child.setCollections([]);
  child.parentID = parent.id;
  await child.saveTx();
  log.push(`attached ${childKey} to ${parent.key}`);
}

async function move(key, fromPath, toPath) {
  const it = await item(key);
  it.addToCollection(collection(toPath).id);
  if (fromPath) it.removeFromCollection(collection(fromPath).id);
  await it.saveTx();
  log.push(`moved ${key} ${it.getField('title')} -> ${toPath}`);
}

// --- changes ---------------------------------------------------------------

return log.join('\n') || 'nothing to do';
