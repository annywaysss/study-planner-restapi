# study-planner-restapi
-----------------------------API DOCUMENTATION------------------------------------------------------------------------------------------------
# API Endpoint Documentation -Study Planner (API Arena 2.0)


All data is stored in-memory -
## Task Creation and Retrieval
### POST /tasks
Create a new task.
Requests JSON.
```json
{
  "title": "Read Physics",
  "subject": "Science",
  "due_date": "2025-07-15",
  "due_time": "18:00",
  "attachment_url": "...",       
  "pinned": false,                
  "priority": "medium"            
}
```
### GET /tasks
Get all tasks.

### GET /tasks/<id>
Get task by ID.

---

##  Task Update & Deletion

### PUT /tasks/<id>
Update task fields. If `is_completed` is `true`, `completed_at` is added.

Request JSON: 
Includes any of the same fields as POST (optional).

### DELETE /delete/<id> (please use curl or postman for this)
Deletes a task (redirects to homepage in UI).
### DELETE /tasks/purge
Deletes all tasks from the system.
### DELETE /tasks/delete_completed
Delete only completed tasks.
----------------------------------------------------------------------------
## Filtering & Search
### GET /tasks/search?q=keyword
Searches by title or subject.
### GET /tasks/filter
Filters tasks using any combination:
Query parameters:
- subject=Math
- is_completed=true|false
- due_date=YYYY-MM-DD
- due_time=HH:MM
---------------------------------------------------------------------------------------

## Pinning
### GET /tasks/pinned
Get all pinned tasks.
### PATCH /tasks/<id>/pin
Toggle pin status.

---

## Date-Based Filters
### GET /tasks/upcoming
Get tasks due after the current time.

----------------------------------------------------------------------------------

## Analytics

### GET /tasks/stats
Returns counts:
```json
{ "total":10, "completed":7,"pending":3 }
```

### GET /tasks/group_by_subject
Returns tasks grouped by subject:
```json
{
  "Math": [ {task1}, {task2} ],
  "CS": [ {task3} ]
}
```
--------------------------------------------------------------------------------------------------------
## Export & Suggestions

### GET /tasks/export/csv
Download tasks as `.csv`.

### GET /tasks/suggest
Suggests 3 future study slots.
Example Output:
```json
[
  {
    "date": "2025-07-12",
    "time": "15:00",
    "suggested_slot": "03:00 PM - 04:00 PM"
  }
]
```
