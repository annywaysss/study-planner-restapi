from flask import Flask, request, jsonify, render_template, redirect,url_for
from datetime import datetime
app = Flask(__name__)

tasks = [] 
task_id = 1


@app.route('/')
def show_ui():
    #although an UI wasnt asked, i hope it doesnt get judged
    return render_template('index.html')
@app.route('/tasks', methods=['POST'])
def create_task():
    #here we are creating a  task to be added in our planner :)
    next_id = max([t["id"] for t in tasks], default=0) + 1
    #takes the max id from the data and uses the next one

    data = request.get_json()
    #parses incoming JSON data from the request body
    task = {
        "id": next_id, #mandatory field
        "title": data.get("title"), #mandatoryy field
        "subject": data.get("subject"), #mandatory field
        "due_date": data.get("due_date", ""), #optional tho
        "due_time": data.get("due_time", ""),  #optional tho
        "is_completed": False, #is false by default
        "attachment_url": data.get("attachment_url", "") #optional if user wants to keep a doc that he wants to read as todo you know
    } 

    tasks.append(task)
    #appends the task in the in-memory data
    return jsonify(task), 201
    #returns the task as JSON with created status code


#this is an endpoint which pins the tasks so that user can see which tasks has he kept pinned to complete first
@app.route('/tasks/pinned', methods=['GET'])
def get_pinned_tasks():
    #it just uses the optional pinned=true/false from the tasks and returns the pinned tasks
    return jsonify([t for t in tasks if t.get("pinned")])
#this endpoint changes the pinned status of a task by its id tho
@app.route('/tasks/<int:task_id>/pin', methods=['PATCH'])
def toggle_pin(task_id):
    for task in tasks:
        if task['id'] == task_id: #first searches the task with id
            #flips the pinned status
            task['pinned'] = not task.get('pinned', False)
            #returns the updated pin status of the task
            return jsonify({"id": task_id, "pinned": task['pinned']})
    #if no such task is there iwth the id then returns task not found and error404 staus code
    return jsonify({"error": "Task not found"}), 404
@app.route('/tasks/search', methods=['GET'])
def search_tasks():
    #it searches tasks by keyword it can ve title or subject any and it is case insensitive tho
    
    keyword = request.args.get('q', '').strip().lower()
    if not keyword: #if keyword is not anywhere to be found it returns 404 code error status
        return jsonify({"error": "Provide ?q=keyword"}), 400
    #filters tasks where keyword is found
    matched = [
        t for t in tasks
        if keyword in t.get('title', '').lower()   or
           keyword in t.get('subject', '').lower()
    ]
    #returns list of matched tasks
    return jsonify(matched)

@app.route('/tasks', methods=['GET'])
#this fetches all the tasks or JSON
def get_all_tasks():
    return jsonify(tasks)
@app.route('/tasks/upcoming', methods=['GET'])
#this endpoint helps in finding the upcoming tasks i.e. the tasks yet to do and due date is yet not achieved
def upcoming_tasks():
    from datetime import datetime
    now = datetime.now()
    upcoming = []
    for t in tasks:
        try:
            due_dt = datetime.strptime(f"{t['due_date']} {t['due_time']}", "%Y-%m-%d %H:%M")
            #checks if due date ahs passed or if it had been completed
            if due_dt>= now and not t.get('is_completed'):
                upcoming.append(t)
        except:
            continue
    #returns the list of upcoming
    return jsonify(upcoming)
@app.route('/tasks/<int:task_id>', methods=['GET'])
#tihs enpoint fetches the task by its id
def get_task(task_id):
    for task in tasks: #searches fo the matching id
        if task["id"] == task_id:
            return jsonify(task)
        #if task not found, returns status code 404
    return jsonify({"error": "Task not found"}), 404

# @app.route('/delete/<int:task_id>', methods=['GET'])
#this endpoint deletes task by its id
@app.route('/delete/<int:task_id>', methods=['GET', 'DELETE'])
def delete_task(task_id):
    #if the request method is GET or like using a browser bar, then it shows that please use postman because browser bar doesnt support DELETE method here
    if request.method == 'GET':
        return '''
            <h4>This endpoint only works via DELETE method.</h4>
            <h4>Please use Postman or curl to test it.</h4>
        ''', 405

    for task in tasks: #searches through all the tasks to find the task with mathcing id
        if task["id"] == task_id:
            tasks.remove(task) #removs the task
            return jsonify({"message": f"Task {task_id} deleted successfully"}), 200 #gives a message and 200 success status code
    return jsonify({"error": "Task not found"}), 404 #ggives a message and 404 error codee if id not found

@app.route('/tasks/filter', methods=['GET'])
def filter_tasks():
    #Query parameters supported (all optional, combine freely): subject=Math (exact match, case‑insensitive) is_completed=true|false   (boolean)due_date=YYYY-MM-DD       (return tasks with due_date <= this date)due_time=HH:MM            (works with due_date; <= comparison)
    subject  = request.args.get('subject')
    is_completed= request.args.get('is_completed')
    due_date= request.args.get('due_date')   #YYYY‑MM‑DD
    due_time = request.args.get('due_time')   #HH:MM

    #compares tasks with <=------------------------------------------
    target_dt = None
    if due_date:
        time_part = due_time or "23:59"
        try:
            target_dt = datetime.strptime(f"{due_date} {time_part}", "%Y-%m-%d %H:%M")
        except ValueError:
            return jsonify({"error": "Invalid due_date or due_time format"}), 400

#filters the task with the subject or other parameteres ------------------------------------------
    results = []
    for t in tasks:
        # subject filter
        if subject and t.get('subject', '').lower() != subject.lower(): #as it is case insensitive so lowercases the filter tag tho
            continue

        # completed or not filter
        if is_completed is not None:
            desired = is_completed.lower() == 'true' 
            if t.get('is_completed') != desired:
                continue

        # date/time <= filter
        if target_dt:
            td = t.get('due_date')
            tt = t.get('due_time', '23:59')
            try:
                task_dt = datetime.strptime(f"{td} {tt}", "%Y-%m-%d %H:%M")
                if task_dt > target_dt:
                    continue
            except:
                continue 

        results.append(t)

    return jsonify(results)
@app.route('/tasks/stats', methods=['GET'])
#this endpoint  gives a stats of how many tasks r there total and how many copleted how many pending.
def task_stats():
    total = len(tasks) #keeps length of tasks
    completed= sum(1 for t in tasks if t.get('is_completed')) #adds 1 for each completed task
    pending = total - completed #pending is obv calc as this
    return jsonify({
        "total": total,
        "completed": completed,
        "pending": pending
    })
from collections import defaultdict
#we r using defaultdict to get a dictionary
@app.route('/tasks/group_by_subject', methods=['GET'])
def group_by_subject():
    #this endpoint groups all tasks by their subject and returns them as a JSON object
    groups = defaultdict(list)
    #iterate through all tasks and group them by the subjectfield
    for t in tasks:
        groups[t.get('subject', 'Unspecified')].append(t)
    #returns grouped tasks as a JSON dictionary
    return jsonify(groups)
@app.route('/tasks/export/csv', methods=['GET'])
def export_tasks_csv():
# this endpoint helps in donwloading al our tasks into a CSV file for help
    import csv
    import io
    from flask import Response
    #ut creares a csv file named tasks.csv and asks to download and save
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "title","subject","due_date","due_time","is_completed"]) #it gives fieldnames for the csv file as follows
    writer.writeheader()
    writer.writerows(tasks)
    return Response(output.getvalue(), mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=tasks.csv"})


@app.route('/tasks/suggest', methods=['GET'])
#this is an advanced endpint which helps in getting suggested slots, its quite simple tho, just gives 3 slots with 1 hr each 3 hrs apart
def suggest_study_slots():
    from datetime import datetime, timedelta

    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    slots = []
    for i in range(3):
        start = now + timedelta(hours=i*3)
        #creates slots
        slots.append({
            "date": start.strftime("%Y-%m-%d"),
            "time": start.strftime("%H:%M"),
            "suggested_slot": f"{start.strftime('%I:%M %p')} - {(start + timedelta(hours=1)).strftime('%I:%M %p')}"
        })
        #returns the list of suggested time blocks
    return jsonify(slots)
@app.route('/tasks/delete_completed', methods=['DELETE'])
#uses dleet method

#this endpoint deletes all the completed tasks and refreshes the planner
def delete_completed_tasks():
    global tasks
    original_len = len(tasks) #keeps data odf how many tasks were there
    tasks = [t for t in tasks if not t.get('is_completed')] #changes tasks to only if its not completed haha :)
    return jsonify({
        "message": "Deleted all completed tasks",
        "deleted":original_len -len(tasks), #shows how many aredeleted
        "remaining": len(tasks)
    })

@app.route('/tasks/<int:task_id>', methods=['PUT'])
#this endpoint updates the tasks, takes all the new values 
def update_task(task_id):
    #update any task field
    data = request.get_json()

    for task in tasks:
        if task['id'] == task_id:
            # gives a choice to  update each field -------------------
            task['title'] = data.get('title',task['title'])
            task['subject'] = data.get('subject', task['subject'])
            task['due_date'] = data.get('due_date', task['due_date'])
            task['due_time']= data.get('due_time', task['due_time'])
            task['pinned']= data.get('pinned',  task.get('pinned', False))
            if "attachment_url" in data:
                task["attachment_url"] = data["attachment_url"]
            # --- completion status -----------------------
            if 'is_completed' in data:
                task['is_completed'] = bool(data['is_completed'])
                if task['is_completed']:
                    task['completed_at'] = datetime.now().strftime("%Y-%m-%d") ##keeps a data of when is the task completed so that to show when asked 
                else:
                    task.pop('completed_at', None)   
            #returns jsonified tasks, and success codee 200
            return jsonify(task), 200

    return jsonify({"error": "Task not found"}), 404
@app.route('/tasks/purge', methods=['DELETE'])
#this endpoint deletes all the tasks and resets the planner refreshed well
def purge_all(): 
    global tasks #takes the tasks glbal
    count = len(tasks) #it gets the count of tasks
    tasks.clear() #clears all
    return jsonify({"message": f"Deleted {count} tasks. Planner reset."}) #gives a message of how many tasks dleeted and that planner is reset

if __name__ == '__main__':
    app.run(debug=True)