// MongoDB playground script for Zenith onboarding tracker data.
// Run in MongoDB Shell/Playground: mongosh playground-8.mongodb.js

use('zenith')

const REPLACE_EXISTING_ROWS = true

const tableMeta = {
  table: {
    msoDisplayedDecimalSeparator: '.',
    msoDisplayedThousandSeparator: ','
  },
  rowDefaults: { msoHeightSource: 'auto' },
  colDefaults: { msoWidthSource: 'auto' },
  tdDefaults: {
    paddingTop: '1px',
    paddingRight: '1px',
    paddingLeft: '1px',
    msoIgnore: 'padding',
    color: 'black',
    fontSize: '11.0pt',
    fontWeight: 400,
    fontStyle: 'normal',
    textDecoration: 'none',
    fontFamily: 'Calibri, sans-serif',
    msoFontCharset: 0,
    textAlign: 'general',
    verticalAlign: 'bottom',
    border: 'none',
    whiteSpace: 'nowrap',
    msoRotate: 0
  },
  fonts: {
    font14: {
      color: 'black',
      fontSize: '11.0pt',
      fontWeight: 400,
      fontStyle: 'normal',
      textDecoration: 'none',
      fontFamily: 'Calibri',
      msoGenericFontFamily: 'auto',
      msoFontCharset: 0
    },
    font19: {
      color: 'black',
      fontSize: '11.0pt',
      fontWeight: 700,
      fontStyle: 'normal',
      textDecoration: 'none',
      fontFamily: 'Calibri',
      msoGenericFontFamily: 'auto',
      msoFontCharset: 0
    },
    font34: {
      color: '#0563C1',
      fontSize: '11.0pt',
      fontWeight: 400,
      fontStyle: 'normal',
      textDecoration: 'underline',
      textUnderlineStyle: 'single',
      fontFamily: 'Calibri',
      msoGenericFontFamily: 'auto',
      msoFontCharset: 0
    },
    font54: {
      color: 'black',
      fontSize: '11.0pt',
      fontWeight: 700,
      fontStyle: 'normal',
      textDecoration: 'underline',
      textUnderlineStyle: 'single',
      fontFamily: 'Calibri',
      msoGenericFontFamily: 'auto',
      msoFontCharset: 0
    }
  },
  classes: {
    xl42: { textAlign: 'left', verticalAlign: 'middle', whiteSpace: 'normal' },
    xl46: { textAlign: 'left', verticalAlign: 'middle', border: '0.5pt solid black', whiteSpace: 'normal' },
    xl53: { textAlign: 'left', verticalAlign: 'middle' },
    xl64: { textAlign: 'center', verticalAlign: 'middle', border: '0.5pt solid black', background: '#1F4E78', color: 'white' },
    xl73: { fontWeight: 700, textAlign: 'center', verticalAlign: 'middle', border: '0.5pt solid black', background: '#9BC2E6' },
    xl77: { textAlign: 'left', verticalAlign: 'middle', border: '0.5pt solid black' },
    xl79: { fontWeight: 700, textAlign: 'left', verticalAlign: 'middle', border: '0.5pt solid black', background: '#DBDBDB' },
    xl121: { textAlign: 'left', verticalAlign: 'middle', border: '0.5pt solid black', background: '#FFC000' },
    xl200: { textAlign: 'left', verticalAlign: 'top', border: '0.5pt solid black' },
    xl204: { textAlign: 'left', verticalAlign: 'middle', border: '0.5pt solid black', background: '#FCE4D6' },
    xl206: { textAlign: 'left', verticalAlign: 'middle', border: '0.5pt solid black', background: 'yellow' }
  },
  columns: [
    { key: 'day', label: 'Day' },
    { key: 'activity', label: 'Activity' },
    { key: 'actions', label: 'Actions' },
    { key: 'technology', label: 'Applicable for <Technology>' },
    { key: 'projects', label: 'Applicable for <Project(s)>' }
  ],
  updatedAt: new Date()
}

db.onboarding_table_meta.updateOne(
  { key: 'default' },
  { $set: { key: 'default', ...tableMeta } },
  { upsert: true }
)

// Paste the full row dataset here in tab-separated format:
// Day<TAB>Activity<TAB>Actions<TAB>Technology<TAB>Projects
const RAW_ROWS_TSV = String.raw``

const curatedRows = [
  ['Week0', 'ABLK Security Alert - Email Auto-Forwards - Compliance', 'Shubhanshu/Manvi will send this email', 'Applicable for all', 'Applicable for all'],
  ['Week0', 'Plan onboarding activities', 'Manvi/Shubhanshu to walk the new joiner through this checklist and the concept of onboarding', 'Applicable for all', 'Applicable for all'],
  ['Week0', 'Plan onboarding activities', 'Walk through of onboarding checklist and identify what is not applicable. This is to be done with TL.', 'Applicable for all', 'Applicable for all'],
  ['Week0', 'Training Sessions', 'Onboarding Training (14 January 2026)', 'Applicable for all', 'Applicable for all'],
  ['Week0', 'Training Sessions', 'Phoenix onboarding guide', 'Applicable for all', 'Applicable for all'],
  ['Week0', 'Home office setup', 'Internet speed (minimum 200 mbps), power backup, mobile device readiness', 'Applicable for all', 'Applicable for all'],
  ['Week0', 'VLink laptop', 'Allotment of Vlink Laptop', 'Applicable for all', 'Applicable for all'],
  ['Week0', 'BLK Login Credentials', 'Receive BLK Login Credentials', 'Applicable for all', 'Applicable for all'],
  ['Week0', 'Team Connect', 'Meet assigned Vlink Team Lead', 'Applicable for all', 'Applicable for all'],
  ['Day0', 'VDI Access verification', 'Verify VDI as soon as BLK credentials are received and contact BLK IT in case of issues', 'Applicable for all', 'Applicable for all'],
  ['Day1', 'Team Connect', 'Meet assigned Buddy', '.Net', 'Applicable for all'],
  ['Day1', 'Setup', 'Activate DUO account on mobile and change password', 'Applicable for all', 'Applicable for all'],
  ['Day1', 'Status Reporting', 'Share Day1 status updates with BLK team / TL / Manager', 'Applicable for all', 'Applicable for all'],
  ['Day2', 'Status Reporting', 'Share Day2 status updates with BLK team / TL / Manager', 'Applicable for all', 'Applicable for all'],
  ['Day3', 'Status Reporting', 'Share Day3 status updates with BLK team / TL / Manager', 'Applicable for all', 'Applicable for all'],
  ['Day4', 'Status Reporting', 'Share Day4 status updates with BLK team / TL / Manager', 'Applicable for all', 'Applicable for all'],
  ['Day5', 'Status Reporting', 'Share Day5 status updates with BLK team / TL / Manager', 'Applicable for all', 'Applicable for all']
]

function parseRowsFromRaw(rawText) {
  const rows = []
  const lines = String(rawText || '').split(/\r?\n/)
  for (const line of lines) {
    const clean = line.trim()
    if (!clean || clean.startsWith('#')) continue
    const cols = clean.includes('\t') ? clean.split('\t') : clean.split('|')
    if (cols.length < 5) continue
    rows.push(cols.slice(0, 5).map((v) => String(v || '').trim()))
  }
  return rows
}

const parsedRows = parseRowsFromRaw(RAW_ROWS_TSV)
const sourceRows = parsedRows.length > 0 ? parsedRows : curatedRows

const rows = sourceRows.map(([day, activity, actions, technology, projects]) => ({
  day,
  activity,
  actions,
  technology,
  projects,
  source: 'week0_tracker'
}))

if (REPLACE_EXISTING_ROWS) {
  db.onboarding_tracker_rows.deleteMany({ source: 'week0_tracker' })
}

rows.forEach((row) => {
  db.onboarding_tracker_rows.updateOne(
    { day: row.day, activity: row.activity, actions: row.actions, source: row.source },
    { $set: { ...row, updatedAt: new Date() }, $setOnInsert: { createdAt: new Date() } },
    { upsert: true }
  )
})

try { db.onboarding_tracker_rows.createIndex({ day: 1 }) } catch (e) {}
try { db.onboarding_tracker_rows.createIndex({ technology: 1 }) } catch (e) {}
try { db.onboarding_tracker_rows.createIndex({ projects: 1 }) } catch (e) {}
try { db.onboarding_tracker_rows.createIndex({ source: 1 }) } catch (e) {}

print('Database: zenith')
print('Collections: onboarding_table_meta, onboarding_tracker_rows')
print(`Rows upserted: ${rows.length}`)
print(`Raw rows parsed: ${parsedRows.length}`)
