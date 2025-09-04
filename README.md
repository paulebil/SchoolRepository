# SchoolPaperRepository System

```commandline
Admin (School Owner)
│
├─ Manages School
│    ├─ Attributes: name, logo, description, location, website, email, phone, status, created_at, admin_id, optional fields
│
├─ Creates Departments
│    ├─ Attributes: name, description, logo, office_location, head_id, contact info, website, created_at
│    │
│    ├─ Generates Lecturer Signup Links → Lecturer Sign Up → Assigned to Department
│    │    ├─ Attributes: profile_picture_url, phone_number, office_location, bio, linkedin_url, research_interests, status
│    │    ├─ Upload Past Papers → Department Repo (direct)
│    │    └─ Upload Reading Materials → Department Repo (direct)
│    │
│    └─ Generates Student Signup Links → Student Sign Up → Assigned to Department
│         ├─ Attributes: profile_picture_url, phone_number, bio, linkedin_url, research_interests, status
│         └─ Upload Research Papers → Pending Approval
│              ├─ Lecturer Reviews → Approved → Added to Public School Repository
│              └─ Lecturer Reviews → Rejected → Student Edits & Resubmits
│
├─ Admin Oversight
│    ├─ Manage Departments, Lecturers, Students
│    └─ Optionally Review Content / Audit / Settings
│
└─ Public Users
     └─ Access Approved Research Papers Only

```

