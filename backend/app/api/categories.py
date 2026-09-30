from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.database.connection import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("")
def list_categories(db: Session = Depends(get_db)):
    return {"success": True, "data": list(db.scalars(select(Category).order_by(Category.id)).all())}


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"success": True, "data": category}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    category = Category(**payload.model_dump())
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="A category with this name already exists") from exc
    db.refresh(category)
    return {"success": True, "data": category}


@router.put("/{category_id}")
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in payload.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(category, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name is already in use") from exc
    db.refresh(category)
    return {"success": True, "data": category}


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category still contains menu items and cannot be deleted") from exc
    return {"success": True, "data": {"message": "Category deleted"}}
