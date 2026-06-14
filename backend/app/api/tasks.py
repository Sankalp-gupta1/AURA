from fastapi import APIRouter
from app.db.database import SessionLocal
from app.models.email_model import Email
from app.models.task_model import Task
from app.services.ai_service import extract_tasks_from_emails

router = APIRouter()


@router.post("/extract")
def extract_tasks():
    db = SessionLocal()

    emails = db.query(Email).order_by(Email.id.desc()).limit(20).all()

    extracted_tasks = extract_tasks_from_emails(emails)

    saved_tasks = []

    for t in extracted_tasks:
        new_task = Task(
            title=t.get("title"),
            description=t.get("description"),
            priority=t.get("priority"),
            deadline=t.get("deadline"),
            source="gmail"
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        saved_tasks.append({
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "priority": new_task.priority,
            "deadline": new_task.deadline,
            "source": new_task.source,
            "status": new_task.status
        })

    db.close()

    return {
        "message": "Tasks extracted and saved successfully",
        "total_tasks": len(saved_tasks),
        "tasks": saved_tasks
    }


@router.get("/")
def get_tasks():
    db = SessionLocal()

    tasks = db.query(Task).order_by(Task.id.desc()).all()

    result = []

    for t in tasks:
        result.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "deadline": t.deadline,
            "source": t.source,
            "status": t.status,
            "created_at": str(t.created_at)
        })

    db.close()

    return {
        "total": len(result),
        "tasks": result
    }

@router.patch("/{task_id}/complete")
def complete_task(task_id: int):
    db = SessionLocal()

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        db.close()
        return {
            "message": "Task not found"
        }

    task.status = "completed"
    db.commit()
    db.refresh(task)

    result = {
        "id": task.id,
        "title": task.title,
        "status": task.status
    }

    db.close()

    return {
        "message": "Task marked as completed",
        "task": result
    }


@router.patch("/{task_id}/pending")
def pending_task(task_id: int):
    db = SessionLocal()

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        db.close()
        return {
            "message": "Task not found"
        }

    task.status = "pending"
    db.commit()
    db.refresh(task)

    result = {
        "id": task.id,
        "title": task.title,
        "status": task.status
    }

    db.close()

    return {
        "message": "Task marked as pending",
        "task": result
    }


@router.delete("/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        db.close()
        return {
            "message": "Task not found"
        }

    deleted_task = {
        "id": task.id,
        "title": task.title
    }

    db.delete(task)
    db.commit()
    db.close()

    return {
        "message": "Task deleted successfully",
        "task": deleted_task
    }
