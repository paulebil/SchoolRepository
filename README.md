# SchoolPaperRepository System
This system is a digital academic repository designed for institutions of higher learning. It allows schools to create
accounts and organize their departments, lecturers, and students in a structured way. Students can upload their research
papers, which go through an approval workflow where lecturers review and either approve, request revisions, or reject 
the work before it is published. Lecturers can also upload past exam papers and other digital reading materials such as 
notes, slides, and textbooks for students to access. Admins are responsible for managing the school account, creating 
departments, and overseeing users. Access is controlled through invitation links — schools invite lecturers, and 
lecturers invite their students — ensuring that users are correctly linked to their institution and department. The 
repository provides a central place for storing and retrieving research papers, past papers, and academic resources, 
with approved content being visible and downloadable within the school, and optionally to the public.
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

```commandline
[School] 1 ──< has ── 0..* [Department]
   |
   └─< has ── 0..* [User] (admin, lecturer, student)
                   |
                   ├─< creates ── 0..* [SignupToken]
                   |
                   ├─< has ── 0..* [UserToken]
                   |
                   ├─< has ── 0..* [PasswordResetToken]
                   |
                   ├─< supervises ── 0..* [ResearchPaper] (as supervisor/lecturer)
                   |
                   └─< uploads ── 0..* [PastPaper] / [ReadingMaterial]

[Department] 1 ──< contains ── 0..* [ResearchPaper], [PastPaper], [ReadingMaterial]
                   |
                   └─< contains ── 0..* [User] (students & lecturers)

[ResearchPaper] 1 ──< has ── 0..* [ResearchAuthors] ──> 1 [User] (student)
[ResearchPaper] 1 ──< has ── 0..* [ResearchReview] ──> 1 [User] (lecturer reviewer)

[PastPaper] 0..* ──> 1 [User] (lecturer uploader)
[ReadingMaterial] 0..* ──> 1 [User] (lecturer uploader)

```