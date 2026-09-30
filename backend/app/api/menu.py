from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import require_admin
from app.database.connection import get_db
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.schemas.menu import AvailabilityUpdate, MenuItemCreate, MenuItemUpdate
from app.models.user import User

router = APIRouter(prefix="/api/menu", tags=["menu"])


def serialize(item: MenuItem) -> dict:
    return {"id": item.id, "name": item.name, "description": item.description, "price": item.price, "image": item.image,
            "rating": item.rating, "available": item.available, "category_id": item.category_id,
            "category_name": item.category.name if item.category else None, "created_at": item.created_at, "updated_at": item.updated_at}


@router.get("")
def list_menu(category_id: int | None = Query(default=None, gt=0), db: Session = Depends(get_db)):
    query = select(MenuItem).options(joinedload(MenuItem.category)).where(MenuItem.available.is_(True)).order_by(MenuItem.id)
    if category_id is not None:
        query = query.where(MenuItem.category_id == category_id)
    return {"success": True, "data": [serialize(item) for item in db.scalars(query).all()]}


@router.get("/{item_id}")
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.scalar(select(MenuItem).options(joinedload(MenuItem.category)).where(MenuItem.id == item_id))
    if item is None or not item.available:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"success": True, "data": serialize(item)}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_menu_item(payload: MenuItemCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    item = MenuItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"success": True, "data": serialize(item)}


@router.put("/{item_id}")
def update_menu_item(item_id: int, payload: MenuItemUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    item = db.get(MenuItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "category_id" in changes and db.get(Category, changes["category_id"]) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in changes.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return {"success": True, "data": serialize(item)}


@router.delete("/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    item = db.get(MenuItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="This menu item is part of an order and cannot be deleted") from exc
    return {"success": True, "data": {"message": "Menu item deleted"}}


@router.patch("/{item_id}/availability")
def update_availability(item_id: int, payload: AvailabilityUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    item = db.get(MenuItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    item.available = payload.available
    db.commit()
    db.refresh(item)
    return {"success": True, "data": serialize(item)}
