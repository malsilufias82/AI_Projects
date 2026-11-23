const rows = [
  ["Week0", "ABLK Security Alert - Email Auto-Forwards - Compliance", "Shubhanshu/Manvi will send this email", "Applicable for all", "Applicable for all"],
  ["Week0", "Plan onboarding activities", "Manvi/Shubhanshu to walk the new joiner through this checklist and the concept of onboarding", "Applicable for all", "Applicable for all"],
  ["Week0", "Plan onboarding activities", "Walk through of onboarding checklist and identify what is not applicable. This is to be done with TL.", "Applicable for all", "Applicable for all"],
  ["Week0", "Training Sessions", "Onboarding Training (14 January 2026)", "Applicable for all", "Applicable for all"],
  ["Week0", "Training Sessions", "Phoenix onboarding guide", "Applicable for all", "Applicable for all"],
  ["Week0", "Home office setup", "Internet speed (minimum 200 mbps), power backup, mobile device readiness", "Applicable for all", "Applicable for all"],
  ["Week0", "VLink laptop", "Allotment of Vlink Laptop", "Applicable for all", "Applicable for all"],
  ["Week0", "BLK Login Credentials", "Receive BLK Login Credentials", "Applicable for all", "Applicable for all"],
  ["Week0", "Team Connect", "Meet assigned Vlink Team Lead", "Applicable for all", "Applicable for all"],
  ["Day0", "VDI Access verification", "Verify VDI as soon as BLK credentials are received and contact BLK IT in case of issues", "Applicable for all", "Applicable for all"],
  ["Day1", "Team Connect", "Meet assigned Buddy", ".Net", "Applicable for all"],
  ["Day1", "Setup", "Activate DUO account on mobile and change password", "Applicable for all", "Applicable for all"],
  ["Day1", "Status Reporting", "Share Day1 status updates with BLK team / TL / Manager", "Applicable for all", "Applicable for all"],
  ["Day2", "Status Reporting", "Share Day2 status updates with BLK team / TL / Manager", "Applicable for all", "Applicable for all"],
  ["Day3", "Status Reporting", "Share Day3 status updates with BLK team / TL / Manager", "Applicable for all", "Applicable for all"],
  ["Day4", "Status Reporting", "Share Day4 status updates with BLK team / TL / Manager", "Applicable for all", "Applicable for all"],
  ["Day5", "Status Reporting", "Share Day5 status updates with BLK team / TL / Manager", "Applicable for all", "Applicable for all"]
];

use('zenith');
const coll = db.getCollection('onboarding_tracker_rows');
const now = new Date();

coll.deleteMany({ source: 'week0_tracker' });

for (const [day, activity, actions, technology, projects] of rows) {
  coll.updateOne(
    { day: day, activity: activity, actions: actions, source: 'week0_tracker' },
    {
      $set: {
        day: day,
        activity: activity,
        actions: actions,
        action: actions,
        relevantLink: actions,
        technology: technology,
        projects: projects,
        project: projects,
        source: 'week0_tracker',
        updatedAt: now,
      },
      $setOnInsert: {
        createdAt: now,
      }
    },
    { upsert: true }
  );
}

print('Inserted ' + coll.countDocuments({ source: 'week0_tracker' }) + ' rows into onboarding_tracker_rows');
