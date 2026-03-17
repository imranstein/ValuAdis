"""
User Management API Endpoints

RESTful API endpoints for user management with role-based access control
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user_id, get_password_hash
from app.data.models.user import User
from app.data.models.role import Role, Permission, user_roles, role_permissions
from app.schemas.user import UserResponse, UserCreate, UserUpdate, RoleResponse, PermissionResponse
import structlog

logger = structlog.get_logger()

router = APIRouter()


def require_admin_permission(allowed_roles: List[str] = ["system_admin", "firm_admin"]):
    """FastAPI dependency to check if user has admin permissions"""
    def check_admin_permission(
        current_user_id: int = Depends(get_current_user_id),
        db: Session = Depends(get_db)
    ) -> User:
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not any(role.name in allowed_roles for role in user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return user
    
    return check_admin_permission


@router.get("/me", response_model=UserResponse, tags=["Users"])
async def get_current_user_info(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get current user information with roles and permissions"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user roles and permissions
        roles_for_user = db.query(Role).join(user_roles).filter(user_roles.c.user_id == user_id).all()
        permissions = []
        seen_permission_ids = set()
        
        for role in roles_for_user:
            role_perms = db.query(Permission).join(role_permissions).filter(role_permissions.c.role_id == role.id).distinct().all()
            for perm in role_perms:
                if perm.id not in seen_permission_ids:
                    permissions.append(perm)
                    seen_permission_ids.add(perm.id)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            municipality=user.municipality,
            license_number=user.license_number,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
            is_valuer=user.is_valuer,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=[RoleResponse(id=role.id, name=role.name, display_name=role.display_name, description=role.description) for role in roles_for_user],
            permissions=[PermissionResponse(id=p.id, name=p.name, display_name=p.display_name, resource=p.resource, action=p.action, description=p.description) for p in permissions]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching current user info", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user information"
        )


@router.get("/", response_model=List[UserResponse], tags=["Users"])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    municipality: Optional[str] = None,
    is_active: Optional[bool] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_permission())
):
    """
    Get all users with optional filtering
    Requires user management permission
    """
    try:
        
        # Query users with filters
        query = db.query(User).options(selectinload(User.roles))
        
        if municipality:
            query = query.filter(User.municipality == municipality)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if role:
            query = query.join(user_roles).join(Role).filter(Role.name == role)
        
        users = query.offset(skip).limit(limit).all()
        
        # Build response with roles
        user_responses = []
        for user in users:
            user_responses.append(UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                phone=user.phone,
                municipality=user.municipality,
                license_number=user.license_number,
                is_active=user.is_active,
                is_verified=user.is_verified,
                is_admin=user.is_admin,
                is_valuer=user.is_valuer,
                created_at=user.created_at,
                updated_at=user.updated_at,
                roles=[RoleResponse(id=role.id, name=role.name, display_name=role.display_name, description=role.description) for role in user.roles],
                permissions=[]  # Not including permissions in list view for performance
            ))
        
        return user_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching users", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_permission())
):
    """Create a new user
    Requires user management permission
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if phone already exists
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            password_hash=hashed_password,
            municipality=user_data.municipality,
            license_number=user_data.license_number,
            is_active=user_data.is_active,
            is_verified=user_data.is_verified,
            is_admin=user_data.is_admin,
            is_valuer=user_data.is_valuer
        )
        
        db.add(new_user)
        db.flush()
        
        # Assign roles if provided
        if user_data.role_ids:
            # Validate all role IDs upfront
            existing_roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
            existing_role_ids = {role.id for role in existing_roles}
            
            missing_role_ids = set(user_data.role_ids) - existing_role_ids
            if missing_role_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role IDs: {list(missing_role_ids)}"
                )
            
            for role in existing_roles:
                new_user.roles.append(role)
        
        db.commit()
        db.refresh(new_user)
        
        # Get user roles for response
        roles = db.query(Role).join(user_roles).filter(user_roles.c.user_id == new_user.id).all()
        
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            phone=new_user.phone,
            municipality=new_user.municipality,
            license_number=new_user.license_number,
            is_active=new_user.is_active,
            is_verified=new_user.is_verified,
            is_admin=new_user.is_admin,
            is_valuer=new_user.is_valuer,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
            roles=[RoleResponse(id=role.id, name=role.name, display_name=role.display_name, description=role.description) for role in roles],
            permissions=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating user", error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.put("/{user_id}", response_model=UserResponse, tags=["Users"])
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Update user information
    Requires user update permission
    """
    try:
        # Check permissions
        current_user = db.query(User).filter(User.id == current_user_id).first()
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Current user not found"
            )
        
        # Users can update their own info, or admins can update any user
        can_update = current_user_id == user_id
        if not can_update:
            for user_role in current_user.roles:
                if user_role.name in ["system_admin", "firm_admin", "municipal_admin"]:
                    can_update = True
                    break
        
        if not can_update:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update user"
            )
        
        # Get user to update
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user fields
        update_data = user_data.dict(exclude_unset=True)
        
        # Check for uniqueness conflicts on email and phone
        if "email" in update_data:
            existing_email = db.query(User).filter(
                User.email == update_data["email"],
                User.id != user_id
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        if "phone" in update_data:
            existing_phone = db.query(User).filter(
                User.phone == update_data["phone"],
                User.id != user_id
            ).first()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already exists"
                )
        
        for field, value in update_data.items():
            if field == "password" and value:
                setattr(user, "password_hash", get_password_hash(value))
            elif field != "role_ids":
                # Prevent self-updates from changing sensitive fields
                if current_user_id == user_id and field in ["is_admin", "is_active", "is_verified"]:
                    continue
                setattr(user, field, value)
        
        # Update roles if provided and user has admin permissions
        if "role_ids" in update_data and current_user_id != user_id:
            for user_role in current_user.roles:
                if user_role.name in ["system_admin", "firm_admin"]:
                    # Clear existing roles
                    user.roles.clear()
                    # Add new roles
                    for role_id in update_data["role_ids"]:
                        role = db.query(Role).filter(Role.id == role_id).first()
                        if role:
                            user.roles.append(role)
                    break
        
        db.commit()
        db.refresh(user)
        
        # Get user roles for response
        roles = db.query(Role).join(user_roles).filter(user_roles.c.user_id == user.id).all()
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            municipality=user.municipality,
            license_number=user.license_number,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
            is_valuer=user.is_valuer,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=[RoleResponse(id=role.id, name=role.name, display_name=role.display_name, description=role.description) for role in roles],
            permissions=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating user", error=str(e), user_id=user_id)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.get("/roles", response_model=List[RoleResponse], tags=["Users"])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_permission())
):
    """Get all available roles"""
    try:
        roles = db.query(Role).filter(Role.is_active.is_(True)).all()
        return [RoleResponse(id=role.id, name=role.name, display_name=role.display_name, description=role.description) for role in roles]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching roles", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch roles"
        )
